-- =============================================================================
-- NovaCura Pharma - Piattaforma di Data Governance & Knowledge Management
-- Artefatto SQL 05 - Query di validazione della qualità e della governance
-- =============================================================================
--
-- Scopo
--   Query che trasformano i principi di governance in controlli eseguibili.
--   Due gruppi:
--     A. Controlli sul control plane: la governance verifica sé stessa
--        (dataset senza copertura policy, metadati obbligatori mancanti,
--        dati sensibili non classificati). Sono i controlli che rendono
--        la governance dimostrabile e non solo dichiarata.
--     B. Controlli di data quality sui dataset, sulle sei dimensioni della
--        nota 03 (completeness, accuracy, consistency, timeliness, uniqueness,
--        validity), con soglia e scoring.
--
--   Il principio della nota 03: una metrica senza soglia è un numero isolato,
--   e una soglia la fissa il business, non l'ingegnere. Qui le soglie sono
--   dati (tabella dq_rule), non costanti nel codice.
--
-- Dialetto: PostgreSQL 15+. Presuppone gli schemi 01-04 caricati.
-- =============================================================================

SET search_path TO governance;


-- -----------------------------------------------------------------------------
-- DDL di supporto: regole e risultati di data quality
-- -----------------------------------------------------------------------------
-- Definite qui perché sono gli oggetti che le query di questo artefatto
-- popolano e leggono. dq_rule lega una dimensione a un dataset/campo con una
-- soglia; dq_result registra le misure nel tempo (la forma dinamica della nota
-- 03, quella che coglie il decadimento).
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS dq_rule (
    rule_id     SERIAL       PRIMARY KEY,
    dataset_id  BIGINT       NOT NULL REFERENCES dataset(dataset_id) ON DELETE CASCADE,
    field_id    BIGINT       REFERENCES dataset_field(field_id),
    dimension   VARCHAR(16)  NOT NULL
        CHECK (dimension IN ('completeness', 'accuracy', 'consistency',
                            'timeliness', 'uniqueness', 'validity')),
    description VARCHAR(240) NOT NULL,
    threshold   NUMERIC(5,2) NOT NULL,          -- soglia di accettazione (percentuale)
    set_by      INTEGER      REFERENCES party(party_id),  -- chi ha fissato la soglia (il business)
    is_critical BOOLEAN      NOT NULL DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS dq_result (
    result_id     BIGSERIAL   PRIMARY KEY,
    rule_id       INTEGER     NOT NULL REFERENCES dq_rule(rule_id),
    measured_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    measured_value NUMERIC(5,2) NOT NULL,       -- valore osservato
    passed        BOOLEAN     NOT NULL
);

-- Seed minimo: regole e misure per il dataset di esiti clinici.
INSERT INTO dq_rule (dataset_id, field_id, dimension, description, threshold, set_by, is_critical)
SELECT d.dataset_id, NULL, v.dimension, v.description, v.threshold,
       (SELECT party_id FROM party WHERE role_type = 'data_owner' AND org_unit = 'Clinical Development'),
       v.is_critical
FROM dataset d, (VALUES
        ('completeness', 'Endpoint primario popolato su tutti i soggetti', 98.00, TRUE),
        ('validity',     'subject_id conforme al pattern di pseudonimo',   99.50, TRUE),
        ('uniqueness',   'Un soggetto, una riga di esito per visita',      99.00, FALSE),
        ('timeliness',   'Esito caricato entro 24h dalla visita',          95.00, FALSE)
    ) AS v(dimension, description, threshold, is_critical)
WHERE d.urn = 'urn:novacura:clinical:ct_subject_outcomes';

INSERT INTO dq_result (rule_id, measured_at, measured_value, passed)
SELECT r.rule_id, TIMESTAMPTZ '2026-06-10 04:00', m.val, m.val >= r.threshold
FROM dq_rule r
JOIN (VALUES ('completeness', 99.10), ('validity', 99.80),
             ('uniqueness', 98.40), ('timeliness', 96.20)) AS m(dim, val)
  ON r.dimension = m.dim
JOIN dataset d ON d.dataset_id = r.dataset_id
WHERE d.urn = 'urn:novacura:clinical:ct_subject_outcomes';


-- =============================================================================
-- GRUPPO A - la governance verifica sé stessa
-- =============================================================================

-- A1. Dataset sensibili senza copertura di policy completa.
--     Regola: ogni dataset restricted (PHI) deve essere coperto da almeno una
--     policy di access, una di retention e una di privacy. Un dataset PHI
--     scoperto è un rischio di compliance concreto, non teorico.
SELECT d.urn, d.name, sc.code AS sensitivity,
       array_agg(DISTINCT p.category ORDER BY p.category) AS categorie_coperte
FROM dataset d
JOIN sensitivity_class sc ON sc.class_id = d.sensitivity_class_id
LEFT JOIN policy_dataset_map m ON m.dataset_id = d.dataset_id
LEFT JOIN policy p ON p.policy_id = m.policy_id AND p.is_current
WHERE sc.code = 'restricted'
GROUP BY d.urn, d.name, sc.code
HAVING NOT (array_agg(DISTINCT p.category) @> ARRAY['access','retention','privacy']::varchar[]);
-- Atteso su questo seed: nessuna riga (i due dataset PHI sono coperti). Una
-- riga qui è un finding di audit.


-- A2. Dataset senza tutti i metadati operativi obbligatori dichiarati.
--     Confronta i metadati obbligatori dello standard (metadata_attribute) con
--     quelli effettivamente valorizzati e correnti (metadata_value). Traduce
--     "lo standard minimo di metadati" in un controllo, non in un auspicio.
WITH mandatory AS (
    SELECT attr_id, name FROM metadata_attribute
    WHERE is_mandatory AND layer = 'operational'
),
declared AS (
    SELECT dataset_id, attr_id
    FROM metadata_value
    WHERE valid_to IS NULL          -- solo la versione corrente
)
SELECT d.urn, m.name AS metadato_obbligatorio_mancante
FROM dataset d
CROSS JOIN mandatory m
LEFT JOIN declared dv ON dv.dataset_id = d.dataset_id AND dv.attr_id = m.attr_id
WHERE d.lifecycle_state = 'active'
  AND dv.attr_id IS NULL
ORDER BY d.urn, m.name;
-- Nota: il seed valorizza solo 'definition' come esempio di versioning, quindi
-- questa query evidenzia i metadati non ancora popolati. In esercizio la lista
-- vuota è l'obiettivo; qui mostra il controllo che guida il completamento.


-- A3. Campi PHI senza tag semantico o senza pattern di validità.
--     Un campo sanitario personale senza semantica esplicita e senza regola di
--     validità è un doppio rischio: non è interoperabile e non è verificabile.
SELECT d.urn, f.name AS campo, f.is_phi,
       (f.semantic_tag_id IS NULL) AS senza_tag_semantico,
       (f.valid_pattern IS NULL)   AS senza_pattern_validita
FROM dataset_field f
JOIN dataset d ON d.dataset_id = f.dataset_id
WHERE f.is_phi
  AND (f.semantic_tag_id IS NULL OR f.valid_pattern IS NULL);


-- A4. Accessi negati a dati restricted nelle ultime 24h (segnale di sicurezza).
--     Un tentativo negato non è un errore da nascondere: È evidenza che la
--     segregazione dei ruoli funziona, e un pattern di negati ripetuti è un
--     segnale da indagare.
SELECT p.full_name, p.role_type, d.urn, al.occurred_at, al.row_scope
FROM access_log al
JOIN party p   ON p.party_id = al.actor_party_id
JOIN dataset d ON d.dataset_id = al.dataset_id
JOIN sensitivity_class sc ON sc.class_id = d.sensitivity_class_id
WHERE NOT al.granted
  AND sc.code = 'restricted'
  AND al.occurred_at >= now() - INTERVAL '24 hours'
ORDER BY al.occurred_at DESC;


-- A5. Output AI non conformi: risposte senza filtro accessi o senza citazione.
--     Il CHECK di schema (artefatto 04) impedisce citazioni vuote, ma
--     access_filter_applied = FALSE resta possibile e va sorvegliato: È la spia
--     di un retrieval non filtrato prima della generazione (rischio nota 09).
SELECT g.gen_id, p.full_name, g.occurred_at, g.model_version, g.index_version
FROM ai_generation_log g
JOIN party p ON p.party_id = g.actor_party_id
WHERE g.access_filter_applied = FALSE
   OR jsonb_array_length(g.citations) = 0;
-- Atteso su questo seed: nessuna riga.


-- =============================================================================
-- GRUPPO B - data quality sulle sei dimensioni (nota 03)
-- =============================================================================

-- B1. Ultimo esito per ogni regola di qualità, con esito vs soglia.
--     La forma "scorecard": ogni dimensione con il suo valore, la sua soglia e
--     il verdetto. Tenere la scomposizione per dimensione accanto allo score
--     composito è la raccomandazione esplicita della nota 03 (uno score
--     aggregato nasconde quale dimensione ha fallito).
SELECT d.urn, r.dimension, r.description, r.threshold,
       res.measured_value, res.passed, r.is_critical
FROM dq_rule r
JOIN dataset d ON d.dataset_id = r.dataset_id
JOIN LATERAL (
    SELECT measured_value, passed
    FROM dq_result
    WHERE rule_id = r.rule_id
    ORDER BY measured_at DESC
    LIMIT 1
) res ON TRUE
ORDER BY d.urn, r.is_critical DESC, r.dimension;


-- B2. Data quality score per dataset (rollup) con banda a semaforo.
--     Lo score composito della nota 03 (1-100) con le bande < 70 rosso,
--     70-80 giallo, > 80 verde. Il rollup è la media delle ultime misure, ma
--     un fallimento su una dimensione critica forza il rosso: un dataset con
--     alta media ma endpoint primario incompleto non è "quasi buono", e
--     inutilizzabile per lo scopo (argomento della nota 03 sull'effetto
--     composto).
WITH latest AS (
    SELECT r.dataset_id, r.dimension, r.is_critical, res.measured_value, res.passed
    FROM dq_rule r
    JOIN LATERAL (
        SELECT measured_value, passed FROM dq_result
        WHERE rule_id = r.rule_id ORDER BY measured_at DESC LIMIT 1
    ) res ON TRUE
)
SELECT d.urn,
       ROUND(AVG(l.measured_value), 1) AS score,
       bool_or(l.is_critical AND NOT l.passed) AS critical_fail,
       CASE
           WHEN bool_or(l.is_critical AND NOT l.passed) THEN 'red (critical fail)'
           WHEN AVG(l.measured_value) < 70 THEN 'red'
           WHEN AVG(l.measured_value) < 80 THEN 'yellow'
           ELSE 'green'
       END AS banda
FROM latest l
JOIN dataset d ON d.dataset_id = l.dataset_id
GROUP BY d.urn;


-- B3. Freshness: dataset la cui ultima misura di qualità è più vecchia della
--     sua frequenza di refresh dichiarata. Un dataset "daily" senza misure da
--     giorni non è fresco, e la staleness è il fallimento silenzioso sia della
--     DQ sia del RAG (note 03 e 07).
SELECT d.urn, d.refresh_frequency,
       MAX(res.measured_at) AS ultima_misura,
       now() - MAX(res.measured_at) AS eta
FROM dataset d
JOIN dq_rule r    ON r.dataset_id = d.dataset_id
JOIN dq_result res ON res.rule_id = r.rule_id
WHERE d.lifecycle_state = 'active'
GROUP BY d.urn, d.refresh_frequency
HAVING (d.refresh_frequency = 'daily'  AND now() - MAX(res.measured_at) > INTERVAL '2 days')
    OR (d.refresh_frequency = 'weekly' AND now() - MAX(res.measured_at) > INTERVAL '10 days');

-- =============================================================================
-- Note di lettura critica (per il valutatore)
-- =============================================================================
-- - Il gruppo A è la parte più caratterizzante: la maggior parte dei sistemi
--   misura la qualità dei dati (gruppo B) ma non verifica la qualità della
--   propria governance. A1-A3 controllano che ownership, classificazione,
--   metadati e policy siano coerenti: È la governance che si autoispeziona.
-- - B2 codifica l'argomento dell'effetto composto della nota 03: la media da
--   sola direbbe "verde", ma un fallimento critico forza il rosso. Uno score
--   che ignora la criticità per dimensione è fuorviante per costruzione.
-- - Le soglie vivono in dq_rule.threshold con dq_rule.set_by, cioè sono dato e
--   hanno un responsabile. Cambiare una soglia è un UPDATE tracciabile, non un
--   edit del codice: È la traduzione del principio "la soglia la fissa il
--   business" (nota 03).
-- - Limite: accuracy e consistency compaiono nello schema dq_rule ma non nel
--   seed, perché misurarle richiede una fonte di verità esterna e un secondo
--   sistema con cui confrontare (nota 03: accuracy è semantica, non sintattica).
--   Sono modellabili, non popolabili su dati illustrativi.
-- =============================================================================
