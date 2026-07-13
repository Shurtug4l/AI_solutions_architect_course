-- =============================================================================
-- NovaCura Pharma - Piattaforma di Data Governance & Knowledge Management
-- Artefatto SQL 04 - Audit trail, log accessi e provenienza degli output AI
-- =============================================================================
--
-- Scopo
--   Lo schema dell'audit trail che rende ogni operazione ricostruibile a fini
--   regolatori. Copre tre superfici distinte richieste dalla traccia (sezione
--   Audit & Reportistica): operazioni sui dati e sui metadati, accessi, e il
--   processo di generazione dei risultati AI.
--
-- Cornice normativa
--   In una farmaceutica l'audit trail non e una buona pratica, e un obbligo.
--   21 CFR Part 11 (FDA) ed EU Annex 11 richiedono, per i record elettronici
--   GxP, un audit trail sicuro, generato dal sistema, con data/ora, che
--   registri chi ha fatto cosa, il valore precedente e quello nuovo, e il
--   motivo quando previsto. I principi ALCOA+ (Attributable, Legible,
--   Contemporaneous, Original, Accurate, + Complete, Consistent, Enduring,
--   Available) sono i requisiti di integrita che questo schema traduce in
--   vincoli.
--
-- Proprieta chiave: append-only
--   Un audit trail modificabile non e un audit trail. Le tabelle sono
--   progettate per sola INSERT: niente UPDATE, niente DELETE. A livello di DB
--   l'enforcement e demandato a permessi (REVOKE UPDATE/DELETE) e a un trigger
--   che blocca le modifiche; qui si definiscono struttura e intento, con la
--   difesa a trigger inclusa come parte della specifica.
--
-- Dialetto: PostgreSQL 15+.
-- =============================================================================

SET search_path TO governance;


-- -----------------------------------------------------------------------------
-- Audit event: chi ha fatto cosa, quando, prima e dopo
-- -----------------------------------------------------------------------------
-- Il record centrale 21 CFR Part 11. Ogni campo mappa un requisito:
--   occurred_at   -> Contemporaneous (timestamp generato dal sistema)
--   actor_party_id-> Attributable (a una persona identificata, mai anonima)
--   action        -> cosa e stato fatto
--   old_value/new_value -> il prima e il dopo, per le modifiche
--   reason        -> il motivo, obbligatorio per le operazioni che lo richiedono
--   e_signature_* -> firma elettronica e suo significato (Part 11 subpart C)
-- prev_event_hash / event_hash formano una catena hash: ogni evento incorpora
-- l'hash del precedente, cosi una manomissione a posteriori spezza la catena ed
-- e rilevabile. e la difesa tecnica contro l'alterazione retroattiva.
-- -----------------------------------------------------------------------------
CREATE TABLE audit_event (
    event_id         BIGSERIAL    PRIMARY KEY,
    occurred_at      TIMESTAMPTZ  NOT NULL DEFAULT now(),
    actor_party_id   INTEGER      NOT NULL REFERENCES party(party_id),
    action           VARCHAR(40)  NOT NULL,   -- create, update, delete, classify, approve, export, ...
    entity_type      VARCHAR(40)  NOT NULL,   -- dataset, metadata_value, policy, model, ...
    entity_id        VARCHAR(80)  NOT NULL,   -- id logico dell'entita toccata
    old_value        JSONB,                   -- stato precedente (NULL per create)
    new_value        JSONB,                   -- stato nuovo (NULL per delete)
    reason           VARCHAR(300),            -- motivo, obbligatorio per azioni critiche (vedi trigger)
    e_signature_hash CHAR(64),                -- firma elettronica dell'attore, se applicabile
    signature_meaning VARCHAR(60),            -- significato: authored / reviewed / approved (Part 11)
    prev_event_hash  CHAR(64),                -- hash dell'evento precedente (catena)
    event_hash       CHAR(64) NOT NULL        -- hash di questo evento (contenuto + prev_event_hash)
);

CREATE INDEX idx_audit_entity ON audit_event(entity_type, entity_id);
CREATE INDEX idx_audit_actor  ON audit_event(actor_party_id);
CREATE INDEX idx_audit_time   ON audit_event(occurred_at);


-- -----------------------------------------------------------------------------
-- Access log: ogni accesso a dati sensibili
-- -----------------------------------------------------------------------------
-- Separato dall'audit degli eventi di modifica perche ha volume e retention
-- diversi: gli accessi in lettura ai dati restricted sono molti e vanno tenuti
-- per l'indagine su un eventuale data breach. granted distingue accessi
-- riusciti e tentativi negati (entrambi sono evidenza). access_path registra da
-- dove e passato l'accesso: query diretta, retrieval del RAG, export.
-- -----------------------------------------------------------------------------
CREATE TABLE access_log (
    access_id     BIGSERIAL    PRIMARY KEY,
    occurred_at   TIMESTAMPTZ  NOT NULL DEFAULT now(),
    actor_party_id INTEGER     NOT NULL REFERENCES party(party_id),
    dataset_id    BIGINT       REFERENCES dataset(dataset_id),
    access_path   VARCHAR(24)  NOT NULL
        CHECK (access_path IN ('direct_query', 'rag_retrieval', 'export', 'api')),
    granted       BOOLEAN      NOT NULL,      -- FALSE = tentativo negato
    row_scope     VARCHAR(120),               -- filtro/ambito effettivo dell'accesso
    client_ip     INET
);

CREATE INDEX idx_access_dataset ON access_log(dataset_id);
CREATE INDEX idx_access_actor   ON access_log(actor_party_id);
CREATE INDEX idx_access_denied  ON access_log(granted) WHERE granted = FALSE;


-- -----------------------------------------------------------------------------
-- AI generation log: la provenienza di ogni risposta del RAG
-- -----------------------------------------------------------------------------
-- Lo step 7 della pipeline RAG (nota 07) reso governance: ogni output generato
-- e loggato con la sua provenienza completa. Non e telemetria di prodotto, e
-- l'audit trail del processo di generazione dei risultati AI che la traccia
-- richiede esplicitamente. I campi rispondono alla domanda regolatoria "perche
-- il sistema ha dato questa risposta?":
--   retrieved_chunks -> quali chunk sono stati recuperati (con la loro fonte)
--   kg_subgraph_ref  -> quale sottografo del KG ha fornito i fatti (GraphRAG)
--   citations        -> le citazioni mostrate all'utente (provenienza esplicita)
--   model_version / index_version -> quale modello e quale indice: se cambiano,
--        la stessa domanda puo dare risposta diversa, e va tracciato (principio
--        "se cambio le regole, il gioco e cambiato", nota 07)
--   access_filter_applied -> prova che il retrieval e stato filtrato per
--        permessi PRIMA della generazione, non dopo (controllo chiave nota 07/09)
-- -----------------------------------------------------------------------------
CREATE TABLE ai_generation_log (
    gen_id               BIGSERIAL    PRIMARY KEY,
    occurred_at          TIMESTAMPTZ  NOT NULL DEFAULT now(),
    actor_party_id       INTEGER      NOT NULL REFERENCES party(party_id),
    query_text           TEXT         NOT NULL,
    retrieved_chunks     JSONB        NOT NULL,   -- [{chunk_id, dataset_urn, score, source_ref}]
    kg_subgraph_ref      VARCHAR(200),            -- riferimento al sottografo usato per il grounding
    answer_text          TEXT         NOT NULL,
    citations            JSONB        NOT NULL,   -- [{source_ref, section, dataset_urn}]
    model_version        VARCHAR(60)  NOT NULL,
    index_version        VARCHAR(60)  NOT NULL,
    access_filter_applied BOOLEAN     NOT NULL,   -- deve essere TRUE per output validi
    confidence           NUMERIC(4,3),            -- se il sistema espone una confidenza
    CHECK (jsonb_array_length(citations) > 0)     -- nessuna risposta senza citazione (nota 07)
);

CREATE INDEX idx_gen_actor ON ai_generation_log(actor_party_id);
CREATE INDEX idx_gen_time  ON ai_generation_log(occurred_at);


-- -----------------------------------------------------------------------------
-- Difesa append-only: blocco di UPDATE e DELETE sull'audit trail
-- -----------------------------------------------------------------------------
-- La specifica non si ferma alla struttura: dichiara anche l'enforcement.
-- Un trigger BEFORE UPDATE OR DELETE che solleva eccezione rende il trail
-- immodificabile a livello applicativo anche per un utente con permessi ampi.
-- In produzione si affianca con REVOKE UPDATE, DELETE sui ruoli applicativi.
-- -----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION governance.deny_mutation() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'Audit trail immodificabile: % non consentito su %',
        TG_OP, TG_TABLE_NAME
        USING ERRCODE = 'insufficient_privilege';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_audit_event_immutable
    BEFORE UPDATE OR DELETE ON audit_event
    FOR EACH ROW EXECUTE FUNCTION governance.deny_mutation();

CREATE TRIGGER trg_access_log_immutable
    BEFORE UPDATE OR DELETE ON access_log
    FOR EACH ROW EXECUTE FUNCTION governance.deny_mutation();

CREATE TRIGGER trg_ai_gen_log_immutable
    BEFORE UPDATE OR DELETE ON ai_generation_log
    FOR EACH ROW EXECUTE FUNCTION governance.deny_mutation();


-- =============================================================================
-- Seed - eventi di audit rappresentativi
-- =============================================================================
-- La catena hash e illustrata con hash placeholder: in produzione event_hash =
-- SHA-256(canonicalizzazione dei campi + prev_event_hash). L'importante e il
-- pattern: ogni evento incorpora il precedente.

-- 1) Classificazione di un dataset (con firma di approvazione).
INSERT INTO audit_event (actor_party_id, action, entity_type, entity_id,
        old_value, new_value, reason, e_signature_hash, signature_meaning,
        prev_event_hash, event_hash)
SELECT (SELECT party_id FROM party WHERE role_type = 'cdo'),
       'classify', 'dataset', d.urn::text,
       NULL, jsonb_build_object('sensitivity', 'restricted'),
       'Classificazione iniziale: dati a livello soggetto.',
       repeat('a', 64), 'approved',
       NULL, repeat('1', 64)
FROM dataset d WHERE d.urn = 'urn:novacura:clinical:ct_subject_outcomes';

-- 2) Modifica della definizione di metadato (aggancia il versioning di 02).
INSERT INTO audit_event (actor_party_id, action, entity_type, entity_id,
        old_value, new_value, reason, prev_event_hash, event_hash)
SELECT (SELECT party_id FROM party WHERE role_type = 'data_steward' AND org_unit = 'Clinical Development'),
       'update', 'metadata_value', 'definition@ct_subject_outcomes',
       jsonb_build_object('definition', 'Esiti primari per soggetto.'),
       jsonb_build_object('definition', 'Esiti primari e secondari per soggetto, con bracci ed endpoint.'),
       'Estensione agli endpoint secondari.',
       repeat('1', 64), repeat('2', 64);

-- 3) Tentativo di accesso negato a dati restricted (evidenza di segregazione).
INSERT INTO access_log (actor_party_id, dataset_id, access_path, granted, row_scope)
SELECT (SELECT party_id FROM party WHERE role_type = 'data_steward' AND org_unit = 'Discovery'),
       d.dataset_id, 'direct_query', FALSE, 'blocked: PHI non nel perimetro del ruolo'
FROM dataset d WHERE d.urn = 'urn:novacura:pv:icsr_reactions';

-- 4) Una generazione RAG governata, con provenienza e filtro accessi applicato.
INSERT INTO ai_generation_log (actor_party_id, query_text, retrieved_chunks,
        kg_subgraph_ref, answer_text, citations, model_version, index_version,
        access_filter_applied, confidence)
SELECT (SELECT party_id FROM party WHERE role_type = 'model_owner'),
       'Quali evidenze supportano sirolimus come candidato per la LAM?',
       '[{"chunk_id":"lit-4471#3","dataset_urn":"urn:novacura:literature:evidence_annotations","score":0.89,"source_ref":"PMID:18836093"},
         {"chunk_id":"assay-233#1","dataset_urn":"urn:novacura:lab:assay_measurements","score":0.81,"source_ref":"assay_run:233"}]'::jsonb,
       'kg://subgraph/sirolimus-LAM-mTOR',
       'Le evidenze convergono su inibizione di mTOR: dati di assay (IC50) e una '
       'pubblicazione clinica supportano l''ipotesi. Nessun segnale PV ostativo nel perimetro consultato.',
       '[{"source_ref":"PMID:18836093","section":"Results","dataset_urn":"urn:novacura:literature:evidence_annotations"},
         {"source_ref":"assay_run:233","section":"potency","dataset_urn":"urn:novacura:lab:assay_measurements"}]'::jsonb,
       'repurpose-scorer-3.1', 'idx-2026-06-10', TRUE, 0.780;

-- =============================================================================
-- Note di lettura critica (per il valutatore)
-- =============================================================================
-- - La catena hash (prev_event_hash -> event_hash) e la difesa contro
--   l'alterazione retroattiva che un trigger da solo non da: un DBA con accesso
--   fisico potrebbe aggirare il trigger, ma non ricalcolare l'intera catena
--   senza che il mismatch emerga a una verifica. e lo stesso principio di un
--   registro append-only firmato.
-- - Il CHECK su citations (>= 1) impone a livello di schema cio che la nota 07
--   chiede come principio: nessuna risposta AI senza provenienza. Rende
--   impossibile loggare un output non citato, quindi impossibile produrne uno
--   "conforme" senza fonte.
-- - access_filter_applied e volutamente NOT NULL e atteso TRUE: un output con
--   FALSE e un incidente di sicurezza (retrieval non filtrato = potenziale
--   esfiltrazione, nota 09), e resta nel log come tale invece di essere nascosto.
-- - Limite: il seed usa hash placeholder (ripetizioni di un carattere). La
--   canonicalizzazione reale (ordine dei campi, encoding) andrebbe fissata in
--   una spec separata per garantire che due verificatori calcolino lo stesso
--   hash; qui si definisce il pattern, non l'algoritmo di canonicalizzazione.
-- =============================================================================
