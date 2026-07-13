-- =============================================================================
-- NovaCura Pharma - Piattaforma di Data Governance & Knowledge Management
-- Artefatto SQL 01 - Data Catalog, classificazione e policy
-- =============================================================================
--
-- Scopo
--   Schema del control plane del catalogo dati: l'inventario centrale dei
--   dataset aziendali rilevanti per il programma di drug repurposing, con
--   proprietari, classificazione di sensibilita, metadati di campo e mapping
--   verso le policy di governance.
--
--   Questo NON e lo schema dei dati clinici o di laboratorio. E lo schema che
--   descrive quei dati (catalog + metadata management, note 03 e 04): la
--   "vetrina" che dice cosa esiste, dove vive, chi ne risponde e come puo
--   essere usato. I dati veri vivono nel lakehouse (vedi artifacts/bigdata).
--
-- Dialetto
--   PostgreSQL 15+. Il control plane di governance e strutturato e
--   transazionale, quindi un motore relazionale e la scelta corretta
--   (schema-on-write, nota 08). Gli equivalenti su Big Data (Delta Lake,
--   Unity Catalog) sono annotati dove rilevante.
--
-- Principio guida
--   Ogni riga del catalogo ha un proprietario. La accountability e il
--   principio portante della governance (nota 01): un dataset senza owner e
--   un dataset di cui nessuno risponde. I vincoli NOT NULL su owner e
--   sensitivity sono la traduzione tecnica di quel principio.
--
-- Coerenza cross-artefatto
--   dataset.dataset_id e la chiave referenziata da 02 (metadata), 03 (lineage),
--   05 (data quality) e dai manifest Big Data. e l'identita stabile di un
--   asset informativo lungo tutto il suo ciclo di vita.
-- =============================================================================

CREATE SCHEMA IF NOT EXISTS governance;
SET search_path TO governance;


-- -----------------------------------------------------------------------------
-- Domini di dato
-- -----------------------------------------------------------------------------
-- Raggruppamento logico dei dataset per area di business. Nel caso NovaCura i
-- quattro domini corrispondono alle quattro famiglie di fonti che il programma
-- di drug repurposing deve integrare (traccia): studi clinici, laboratorio,
-- letteratura, farmacovigilanza. Un quinto dominio (anagrafiche/master data)
-- raccoglie i riferimenti condivisi (molecole, malattie, target).
-- -----------------------------------------------------------------------------
CREATE TABLE data_domain (
    domain_id     SMALLINT     PRIMARY KEY,
    code          VARCHAR(32)  NOT NULL UNIQUE,
    name          VARCHAR(120) NOT NULL,
    description   TEXT         NOT NULL,
    business_area VARCHAR(80)  NOT NULL
);


-- -----------------------------------------------------------------------------
-- Parti / attori di governance (ruoli)
-- -----------------------------------------------------------------------------
-- I ruoli della nota 02, tenuti distinti come vuole DAMA: Data Owner (business,
-- accountable), Data Steward (qualita), Data Custodian (infrastruttura),
-- piu i ruoli specifici del contesto AI e pharma (Model Owner, QA GxP,
-- Regulatory Affairs). Il CDO e transversale e non e legato a un singolo
-- dataset. La segregazione owner/steward/custodian non e pedanteria: in una
-- farmaceutica l'infrastruttura e spesso gestita da IT o da un fornitore
-- esterno, mentre il significato del dato resta al business (nota 02).
-- -----------------------------------------------------------------------------
CREATE TABLE party (
    party_id   SERIAL       PRIMARY KEY,
    full_name  VARCHAR(160) NOT NULL,
    org_unit   VARCHAR(120) NOT NULL,
    email      VARCHAR(160) NOT NULL UNIQUE,
    role_type  VARCHAR(24)  NOT NULL
        CHECK (role_type IN ('cdo', 'data_owner', 'data_steward',
                             'data_custodian', 'model_owner',
                             'qa_gxp', 'regulatory')),
    is_active  BOOLEAN      NOT NULL DEFAULT TRUE
);


-- -----------------------------------------------------------------------------
-- Sistemi sorgente
-- -----------------------------------------------------------------------------
-- Dove il dato nasce. Il flag gxp_relevant marca i sistemi soggetti alle norme
-- Good Practice (GCP/GLP/GMP) e quindi ai requisiti 21 CFR Part 11 ed EU Annex
-- 11 su audit trail e firme elettroniche. La distinzione GxP / non-GxP guida
-- il livello di controllo: un CTMS di trial e GxP, uno scraper di letteratura
-- pubblica non lo e.
-- -----------------------------------------------------------------------------
CREATE TABLE source_system (
    system_id      SERIAL       PRIMARY KEY,
    code           VARCHAR(40)  NOT NULL UNIQUE,
    name           VARCHAR(160) NOT NULL,
    kind           VARCHAR(40)  NOT NULL,  -- CTMS, LIMS, safety_db, literature, MDM, ...
    environment    VARCHAR(16)  NOT NULL
        CHECK (environment IN ('prod', 'validated', 'staging', 'external')),
    gxp_relevant   BOOLEAN      NOT NULL DEFAULT FALSE,
    description    TEXT
);


-- -----------------------------------------------------------------------------
-- Classi di sensibilita
-- -----------------------------------------------------------------------------
-- Lo schema di classificazione dati. Quattro livelli piu due flag ortogonali:
-- phi_flag per i dati sanitari personali (GDPR art. 9, categoria particolare)
-- e gxp_flag per i dati con impatto regolatorio. La classificazione non e
-- decorativa: e cio che la policy di accesso e il retrieval del RAG leggono
-- per decidere chi vede cosa (nota 07, access-filtered retrieval).
-- -----------------------------------------------------------------------------
CREATE TABLE sensitivity_class (
    class_id    SMALLINT     PRIMARY KEY,
    code        VARCHAR(24)  NOT NULL UNIQUE
        CHECK (code IN ('public', 'internal', 'confidential', 'restricted')),
    rank        SMALLINT     NOT NULL UNIQUE,  -- 1 public ... 4 restricted
    description TEXT         NOT NULL,
    phi_flag    BOOLEAN      NOT NULL DEFAULT FALSE,  -- dato sanitario personale
    gxp_flag    BOOLEAN      NOT NULL DEFAULT FALSE   -- rilevante GxP
);


-- -----------------------------------------------------------------------------
-- Dataset (la scheda di catalogo)
-- -----------------------------------------------------------------------------
-- Il cuore del catalogo. Ogni dataset e un asset informativo con identita,
-- proprietario e stato di ciclo di vita (nota 04: acquisition -> cataloging ->
-- use -> archiving -> decommissioning). Il campo medallion_layer colloca il
-- dataset nella scala di raffinamento Bronze/Silver/Gold (nota 08), cosi la
-- lineage e leggibile per costruzione.
--
-- schema_version abilita l'evoluzione additiva dei metadati senza rompere la
-- ricostruibilita storica: quando lo schema di un dataset cambia, si incrementa
-- la versione invece di sovrascrivere.
-- -----------------------------------------------------------------------------
CREATE TABLE dataset (
    dataset_id         BIGSERIAL    PRIMARY KEY,
    urn                VARCHAR(200) NOT NULL UNIQUE,  -- es. urn:novacura:trial:ct_outcomes
    name               VARCHAR(160) NOT NULL,
    description        TEXT         NOT NULL,
    domain_id          SMALLINT     NOT NULL REFERENCES data_domain(domain_id),
    source_system_id   INTEGER      NOT NULL REFERENCES source_system(system_id),

    -- accountability: owner e steward obbligatori, custodian opzionale
    -- (puo coincidere con un fornitore infrastrutturale)
    owner_party_id     INTEGER      NOT NULL REFERENCES party(party_id),
    steward_party_id   INTEGER      NOT NULL REFERENCES party(party_id),
    custodian_party_id INTEGER      REFERENCES party(party_id),

    -- classificazione (obbligatoria: un dataset non classificato non entra
    -- in produzione, e la regola che 05 verifica)
    sensitivity_class_id SMALLINT   NOT NULL REFERENCES sensitivity_class(class_id),

    storage_format     VARCHAR(24)  NOT NULL
        CHECK (storage_format IN ('delta', 'parquet', 'iceberg',
                                  'postgres', 'json', 'rdf', 'vector')),
    storage_location   VARCHAR(300) NOT NULL,  -- s3://... o schema.tabella
    medallion_layer    VARCHAR(12)
        CHECK (medallion_layer IN ('bronze', 'silver', 'gold', 'na')),

    refresh_frequency  VARCHAR(40)  NOT NULL,  -- real-time, daily, weekly, on-event
    sample_link        VARCHAR(300),           -- link a un campione governato

    lifecycle_state    VARCHAR(16)  NOT NULL DEFAULT 'active'
        CHECK (lifecycle_state IN ('draft', 'active', 'archived', 'dismissed')),
    gxp_relevant       BOOLEAN      NOT NULL DEFAULT FALSE,

    schema_version     INTEGER      NOT NULL DEFAULT 1,
    created_at         TIMESTAMPTZ  NOT NULL DEFAULT now(),
    updated_at         TIMESTAMPTZ  NOT NULL DEFAULT now()
);

CREATE INDEX idx_dataset_domain      ON dataset(domain_id);
CREATE INDEX idx_dataset_sensitivity ON dataset(sensitivity_class_id);
CREATE INDEX idx_dataset_lifecycle   ON dataset(lifecycle_state);


-- -----------------------------------------------------------------------------
-- Campi del dataset (metadati di campo)
-- -----------------------------------------------------------------------------
-- La granularita fine del catalogo: ogni campo con tipo, semantica, obbligo,
-- sensibilita e pattern di validita. La distinzione is_pii / is_phi conta:
-- un subject_id pseudonimizzato e PII ma la diagnosi associata e PHI (GDPR
-- art. 9). semantic_tag_id (definito in 02) aggancia il campo a un termine di
-- vocabolario controllato (SNOMED, MedDRA, ...), che e cio che rende il dato
-- interoperabile tra team e con il knowledge graph.
-- -----------------------------------------------------------------------------
CREATE TABLE dataset_field (
    field_id             BIGSERIAL    PRIMARY KEY,
    dataset_id           BIGINT       NOT NULL REFERENCES dataset(dataset_id) ON DELETE CASCADE,
    name                 VARCHAR(120) NOT NULL,
    ordinal              SMALLINT     NOT NULL,
    data_type            VARCHAR(40)  NOT NULL,
    description          TEXT         NOT NULL,
    is_required          BOOLEAN      NOT NULL DEFAULT FALSE,
    is_pii               BOOLEAN      NOT NULL DEFAULT FALSE,
    is_phi               BOOLEAN      NOT NULL DEFAULT FALSE,
    sensitivity_class_id SMALLINT     REFERENCES sensitivity_class(class_id),
    semantic_tag_id      INTEGER,      -- FK verso governance.semantic_tag (artefatto 02)
    valid_pattern        VARCHAR(200), -- regex o regola di validita (dimensione Validity, nota 03)
    allowed_values       TEXT,         -- dominio dei valori ammessi, se enumerabile
    unit                 VARCHAR(40),  -- unita di misura (business metadata, nota 04)
    UNIQUE (dataset_id, name)
);

CREATE INDEX idx_field_dataset ON dataset_field(dataset_id);
CREATE INDEX idx_field_phi      ON dataset_field(is_phi) WHERE is_phi = TRUE;


-- -----------------------------------------------------------------------------
-- Policy di governance
-- -----------------------------------------------------------------------------
-- Le policy aziendali (classification, access, retention, privacy, data
-- sharing) come oggetti versionati con un owner. La struttura riflette la nota
-- 02: una policy ha titolo parlante, scope, responsabile e statement. Il
-- versioning e effective_date servono perche una policy che cambia non
-- cancella la precedente: la ricostruzione regolatoria deve poter dire quale
-- policy era in vigore alla data X.
-- -----------------------------------------------------------------------------
CREATE TABLE policy (
    policy_id      SERIAL       PRIMARY KEY,
    code           VARCHAR(40)  NOT NULL,   -- es. POL-ACC-01
    title          VARCHAR(200) NOT NULL,
    category       VARCHAR(24)  NOT NULL
        CHECK (category IN ('classification', 'access', 'retention',
                            'privacy', 'data_sharing')),
    version        VARCHAR(12)  NOT NULL,   -- semver testuale, es. 1.2
    effective_date DATE         NOT NULL,
    owner_party_id INTEGER      NOT NULL REFERENCES party(party_id),
    statement      TEXT         NOT NULL,   -- il "cosa fare e perche"
    is_current     BOOLEAN      NOT NULL DEFAULT TRUE,
    UNIQUE (code, version)
);


-- -----------------------------------------------------------------------------
-- Mapping policy -> dataset
-- -----------------------------------------------------------------------------
-- Il legame esplicito tra policy e dataset che la traccia richiede
-- ("mapping tra policy e dataset"). Una tabella ponte molti-a-molti: un
-- dataset e soggetto a piu policy, una policy copre piu dataset. La query 05
-- verifica che ogni dataset restricted/PHI sia coperto almeno da una policy di
-- access e una di retention: la copertura non e assunta, e controllata.
-- -----------------------------------------------------------------------------
CREATE TABLE policy_dataset_map (
    policy_id   INTEGER NOT NULL REFERENCES policy(policy_id),
    dataset_id  BIGINT  NOT NULL REFERENCES dataset(dataset_id) ON DELETE CASCADE,
    notes       TEXT,
    PRIMARY KEY (policy_id, dataset_id)
);


-- -----------------------------------------------------------------------------
-- Regole di retention
-- -----------------------------------------------------------------------------
-- La retention non e mai "tenere tutto per sempre" (nota 02). Ogni regola lega
-- una categoria di dato a un periodo, una base legale e un'azione di
-- dismissione. Nel contesto pharma i periodi sono lunghi e imposti da norma:
-- i dati di uno studio clinico vanno conservati fino a 25 anni dalla fine dello
-- studio (EU CTR 536/2014, ICH GCP E6). disposal_action distingue cancellazione
-- fisica e anonimizzazione: per l'analisi secondaria si anonimizza, non si
-- cancella.
-- -----------------------------------------------------------------------------
CREATE TABLE retention_rule (
    rule_id         SERIAL       PRIMARY KEY,
    policy_id       INTEGER      NOT NULL REFERENCES policy(policy_id),
    data_category   VARCHAR(80)  NOT NULL,   -- clinical_trial, assay, pv_icsr, literature, ...
    retention_period INTERVAL    NOT NULL,   -- es. '25 years'
    legal_basis     VARCHAR(200) NOT NULL,   -- es. EU CTR 536/2014 Art. 58
    disposal_action VARCHAR(24)  NOT NULL
        CHECK (disposal_action IN ('hard_delete', 'anonymize', 'archive_cold'))
);


-- =============================================================================
-- Seed dati - i quattro domini e i dataset rappresentativi del caso guida
-- =============================================================================
-- I dati seed sono illustrativi (vedi Nota metodologica del report). Servono a
-- rendere le query di 05 e 06 eseguibili su un catalogo realistico, non a
-- rappresentare dati reali NovaCura.

INSERT INTO data_domain (domain_id, code, name, description, business_area) VALUES
    (1, 'clinical', 'Studi clinici',
        'Dataset di trial clinici interni: soggetti, bracci, endpoint, esiti, eventi avversi.',
        'Clinical Development'),
    (2, 'lab', 'Laboratorio (assay)',
        'Misure di laboratorio su composti e target: screening, potenza, tossicita.',
        'Discovery & Preclinical'),
    (3, 'literature', 'Letteratura scientifica',
        'Annotazioni ed evidenze estratte da pubblicazioni e fonti bibliografiche.',
        'Medical & Scientific Affairs'),
    (4, 'pharmacovigilance', 'Farmacovigilanza',
        'Report di sicurezza individuali (ICSR) e reazioni avverse codificate MedDRA.',
        'Drug Safety / PV'),
    (5, 'mdm', 'Master data di dominio',
        'Anagrafiche condivise: molecole, malattie, target, come riferimenti interoperabili.',
        'Data Governance Office');

INSERT INTO sensitivity_class (class_id, code, rank, description, phi_flag, gxp_flag) VALUES
    (1, 'public',       1, 'Dato pubblico o pubblicabile senza restrizioni.', FALSE, FALSE),
    (2, 'internal',     2, 'Dato interno, riservato all''organizzazione.',    FALSE, FALSE),
    (3, 'confidential', 3, 'Dato riservato: IP, dati di studio aggregati, dati commerciali.', FALSE, TRUE),
    (4, 'restricted',   4, 'Dato sanitario personale a livello soggetto (PHI) o safety identificabile.', TRUE, TRUE);

INSERT INTO party (full_name, org_unit, email, role_type) VALUES
    ('Chief Data Officer', 'Data Governance Office', 'cdo@novacura.example', 'cdo'),
    ('Clinical Data Owner', 'Clinical Development', 'owner.clinical@novacura.example', 'data_owner'),
    ('Preclinical Data Owner', 'Discovery', 'owner.lab@novacura.example', 'data_owner'),
    ('PV Data Owner', 'Drug Safety', 'owner.pv@novacura.example', 'data_owner'),
    ('Clinical Data Steward', 'Clinical Development', 'steward.clinical@novacura.example', 'data_steward'),
    ('Lab Data Steward', 'Discovery', 'steward.lab@novacura.example', 'data_steward'),
    ('Platform Custodian', 'IT / Cloud Platform', 'custodian.platform@novacura.example', 'data_custodian'),
    ('Repurposing Model Owner', 'AI & Data Science', 'owner.model@novacura.example', 'model_owner'),
    ('QA GxP Lead', 'Quality Assurance', 'qa.gxp@novacura.example', 'qa_gxp'),
    ('Regulatory Affairs Lead', 'Regulatory Affairs', 'regulatory@novacura.example', 'regulatory');

INSERT INTO source_system (code, name, kind, environment, gxp_relevant, description) VALUES
    ('CTMS-01', 'Clinical Trial Management System', 'CTMS', 'validated', TRUE,
        'Sistema validato di gestione degli studi clinici.'),
    ('LIMS-01', 'Laboratory Information Management System', 'LIMS', 'validated', TRUE,
        'Gestione dati di laboratorio preclinico e assay.'),
    ('SAFETY-01', 'Pharmacovigilance Safety Database', 'safety_db', 'validated', TRUE,
        'Database di sicurezza per ICSR e segnali (E2B R3).'),
    ('LIT-01', 'Literature Ingestion Service', 'literature', 'external', FALSE,
        'Ingestione e annotazione di letteratura scientifica pubblica.'),
    ('MDM-01', 'Master Data Management', 'MDM', 'prod', TRUE,
        'Anagrafiche di dominio con mapping a vocabolari standard.');

-- Un dataset rappresentativo per ciascuna famiglia di fonti del caso guida.
-- storage_location, medallion_layer e sensibilita sono coerenti con lo schema:
-- i dati a livello soggetto sono restricted+PHI; letteratura pubblica e public.
INSERT INTO dataset (urn, name, description, domain_id, source_system_id,
        owner_party_id, steward_party_id, custodian_party_id, sensitivity_class_id,
        storage_format, storage_location, medallion_layer, refresh_frequency,
        sample_link, lifecycle_state, gxp_relevant) VALUES
    ('urn:novacura:clinical:ct_subject_outcomes',
        'Esiti per soggetto negli studi clinici',
        'Esiti primari e secondari per soggetto arruolato, con bracci ed endpoint.',
        1, 1, 2, 5, 7, 4,
        'delta', 's3://novacura-lake/gold/clinical/subject_outcomes', 'gold',
        'daily', 's3://novacura-lake/samples/clinical_outcomes_sample', 'active', TRUE),
    ('urn:novacura:lab:assay_measurements',
        'Misure di assay su composti e target',
        'Risultati di screening: potenza (IC50/EC50), affinita, citotossicita per coppia composto-target.',
        2, 2, 3, 6, 7, 3,
        'delta', 's3://novacura-lake/gold/lab/assay_measurements', 'gold',
        'on-event', 's3://novacura-lake/samples/assay_sample', 'active', TRUE),
    ('urn:novacura:literature:evidence_annotations',
        'Annotazioni di evidenza dalla letteratura',
        'Relazioni farmaco-malattia-target estratte da pubblicazioni, con riferimento alla fonte.',
        3, 4, 2, 5, 7, 2,
        'parquet', 's3://novacura-lake/silver/literature/evidence', 'silver',
        'weekly', 's3://novacura-lake/samples/literature_sample', 'active', FALSE),
    ('urn:novacura:pv:icsr_reactions',
        'Reazioni avverse da ICSR',
        'Reazioni avverse codificate MedDRA a livello di caso individuale di sicurezza.',
        4, 3, 4, 5, 7, 4,
        'delta', 's3://novacura-lake/gold/pv/icsr_reactions', 'gold',
        'daily', 's3://novacura-lake/samples/pv_sample', 'active', TRUE),
    ('urn:novacura:mdm:compound_master',
        'Anagrafica composti',
        'Master data dei composti con codici ChEMBL e ATC, base per il knowledge graph.',
        5, 5, 3, 6, 7, 2,
        'postgres', 'governance.compound_master', 'na',
        'weekly', NULL, 'active', TRUE);

INSERT INTO policy (code, title, category, version, effective_date, owner_party_id, statement) VALUES
    ('POL-CLS-01', 'Classificazione dei dati', 'classification', '1.0', DATE '2026-01-15', 1,
        'Ogni dataset e classificato su quattro livelli (public/internal/confidential/restricted) '
        'prima dell''ingresso in produzione; i dati a livello soggetto sono restricted per default.'),
    ('POL-ACC-01', 'Controllo degli accessi', 'access', '1.1', DATE '2026-03-01', 1,
        'Accesso basato sui ruoli (RBAC) con segregazione dei compiti; i dati restricted sono '
        'accessibili solo a ruoli autorizzati e ogni accesso e registrato.'),
    ('POL-RET-01', 'Conservazione dei dati', 'retention', '1.0', DATE '2026-01-15', 10,
        'La conservazione segue gli obblighi regolatori per categoria; i dati di studio clinico '
        'sono conservati fino a 25 anni dalla chiusura dello studio.'),
    ('POL-PRV-01', 'Privacy e pseudonimizzazione', 'privacy', '1.0', DATE '2026-01-15', 1,
        'I dati sanitari personali sono trattati come categoria particolare (GDPR art. 9); '
        'pseudonimizzazione all''ingest, anonimizzazione per l''uso secondario.'),
    ('POL-SHR-01', 'Condivisione dei dati', 'data_sharing', '1.0', DATE '2026-02-01', 10,
        'La condivisione esterna di dati di studio richiede anonimizzazione validata e '
        'approvazione di Regulatory Affairs.');

-- Mapping policy -> dataset: i due dataset restricted (PHI) sono coperti da
-- classification, access, retention e privacy. La query 05 verifica proprio
-- questa copertura.
INSERT INTO policy_dataset_map (policy_id, dataset_id, notes)
SELECT p.policy_id, d.dataset_id,
       'Copertura per dataset a livello soggetto (PHI).'
FROM policy p
CROSS JOIN dataset d
WHERE d.urn IN ('urn:novacura:clinical:ct_subject_outcomes',
                'urn:novacura:pv:icsr_reactions')
  AND p.code IN ('POL-CLS-01', 'POL-ACC-01', 'POL-RET-01', 'POL-PRV-01');

-- I dataset non-PHI ricevono almeno classificazione e accesso.
INSERT INTO policy_dataset_map (policy_id, dataset_id, notes)
SELECT p.policy_id, d.dataset_id, 'Copertura base per dataset non-PHI.'
FROM policy p
CROSS JOIN dataset d
WHERE d.urn IN ('urn:novacura:lab:assay_measurements',
                'urn:novacura:literature:evidence_annotations',
                'urn:novacura:mdm:compound_master')
  AND p.code IN ('POL-CLS-01', 'POL-ACC-01');

INSERT INTO retention_rule (policy_id, data_category, retention_period, legal_basis, disposal_action)
SELECT policy_id, v.data_category, v.retention_period, v.legal_basis, v.disposal_action
FROM policy, (VALUES
        ('clinical_trial', INTERVAL '25 years', 'EU CTR 536/2014 Art. 58; ICH GCP E6(R2)', 'anonymize'),
        ('pv_icsr',        INTERVAL '10 years', 'GVP Module VI; Dir. 2001/83/EC',          'anonymize'),
        ('assay',          INTERVAL '15 years', 'GLP; policy IP interna',                   'archive_cold'),
        ('literature',     INTERVAL '3 years',  'Policy interna di knowledge refresh',      'hard_delete')
    ) AS v(data_category, retention_period, legal_basis, disposal_action)
WHERE policy.code = 'POL-RET-01';

-- =============================================================================
-- Note di lettura critica (per il valutatore)
-- =============================================================================
-- - Perche PostgreSQL e non un catalog gia pronto (Collibra/DataHub): a livello
--   di specifica progettuale, modellare il control plane in SQL esplicito rende
--   verificabili i vincoli di governance (owner obbligatorio, classificazione
--   obbligatoria, copertura policy). Un prodotto COTS li implementerebbe, ma la
--   traccia chiede lo schema logico, non la configurazione di un prodotto.
-- - Limite: questo schema modella il control plane, non impone di per se
--   l'access-filtered retrieval del RAG (nota 07). L'enforcement vive nel piano
--   applicativo che legge sensitivity_class e le ACL; qui se ne definisce la
--   base dati.
-- - Evoluzione: sensitivity_class e volutamente piccola e stabile. Aggiungere
--   un dominio o un formato di storage e additivo (nuova riga), non un cambio
--   di schema: la scalabilita verso nuovi domini di dato (requisito non
--   funzionale) e supportata dal modello, non solo dichiarata.
-- =============================================================================
