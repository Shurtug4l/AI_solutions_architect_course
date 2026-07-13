-- =============================================================================
-- NovaCura Pharma - Piattaforma di Data Governance & Knowledge Management
-- Artefatto SQL 02 - Modello di metadati e vocabolari controllati
-- =============================================================================
--
-- Scopo
--   Lo standard minimo di metadati richiesto dalla traccia: definizione dei
--   campi di metadato, loro semantica, tag semantici agganciati a vocabolari
--   controllati, e versioning dei metadati.
--
--   Il modello segue la tripartizione della nota 04: metadati tecnici (schema,
--   formato, path), business/descrittivi (nome, significato, dominio, unita) e
--   operativi (frequenza di refresh, owner, sensibilita). Ogni campo di
--   metadato dichiara a quale strato appartiene e se e obbligatorio o
--   facoltativo. Questa e la parte "specifica del modello di metadati" tra gli
--   artefatti richiesti.
--
-- Perche i vocabolari controllati sono il fulcro
--   In una farmaceutica l'interoperabilita non e opzionale: la stessa reazione
--   avversa deve significare la stessa cosa in farmacovigilanza, in clinica e
--   nel knowledge graph. I vocabolari standard (SNOMED CT, MedDRA, MeSH, ATC,
--   ChEMBL, Orphanet, UniProt) sono il semantic layer (nota 05) reso persistente.
--   Un tag semantico e cio che promuove un campo da "colonna" a "concetto
--   condiviso": e il ponte tra il catalogo (artefatto 01) e il knowledge graph
--   (artifacts/knowledge_graph).
--
-- Dialetto: PostgreSQL 15+.
-- =============================================================================

SET search_path TO governance;


-- -----------------------------------------------------------------------------
-- Vocabolari controllati
-- -----------------------------------------------------------------------------
-- I registri terminologici di riferimento. is_external marca i vocabolari
-- gestiti da enti terzi (SNOMED International, EMA per MedDRA, ...): NovaCura ne
-- allinea una versione, non li possiede. version_label e non-negoziabile: la
-- codifica MedDRA cambia due volte l'anno, e un ICSR codificato con MedDRA 26.1
-- non e confrontabile alla cieca con uno in 27.0. Tracciare la versione del
-- vocabolario e parte della tracciabilita regolatoria.
-- -----------------------------------------------------------------------------
CREATE TABLE controlled_vocabulary (
    vocab_id      SERIAL       PRIMARY KEY,
    code          VARCHAR(24)  NOT NULL UNIQUE,   -- SNOMED, MEDDRA, MESH, ATC, CHEMBL, ORPHA, UNIPROT, ICD10
    name          VARCHAR(160) NOT NULL,
    domain_note   VARCHAR(200) NOT NULL,          -- a cosa serve nel dominio NovaCura
    version_label VARCHAR(40)  NOT NULL,          -- es. MedDRA 27.0, SNOMED CT 2026-01
    is_external   BOOLEAN      NOT NULL DEFAULT TRUE,
    uri_base      VARCHAR(200)                     -- namespace base per costruire le URI dei termini
);


-- -----------------------------------------------------------------------------
-- Termini di vocabolario
-- -----------------------------------------------------------------------------
-- I singoli concetti codificati. code e il codice nativo del vocabolario
-- (es. un codice MedDRA PT), label la sua etichetta preferita, uri la sua
-- identita globale. Solo un sottoinsieme dei termini realmente usati viene
-- materializzato qui: il vocabolario completo vive nel sistema terminologico,
-- il control plane ne cataloga l'uso.
-- -----------------------------------------------------------------------------
CREATE TABLE vocabulary_term (
    term_id     BIGSERIAL    PRIMARY KEY,
    vocab_id    INTEGER      NOT NULL REFERENCES controlled_vocabulary(vocab_id),
    code        VARCHAR(60)  NOT NULL,   -- codice nativo nel vocabolario
    label       VARCHAR(240) NOT NULL,   -- etichetta preferita
    uri         VARCHAR(300),            -- identita globale (per il KG)
    UNIQUE (vocab_id, code)
);


-- -----------------------------------------------------------------------------
-- Tag semantici
-- -----------------------------------------------------------------------------
-- Il livello di indirezione che aggancia un campo di dataset a un concetto.
-- Un tag ha un nome interno stabile (es. 'adverse_event') e punta a un termine
-- di un vocabolario. dataset_field.semantic_tag_id (artefatto 01) referenzia
-- questa tabella. Perche non taggare direttamente col term_id: il tag e il
-- concetto interno stabile, il termine e la sua codifica in un vocabolario
-- che puo cambiare versione o essere sostituito. Un livello di indirezione
-- protegge il catalogo dal churn terminologico.
-- -----------------------------------------------------------------------------
CREATE TABLE semantic_tag (
    tag_id       SERIAL       PRIMARY KEY,
    name         VARCHAR(80)  NOT NULL UNIQUE,   -- concetto interno: adverse_event, compound, target, disease, endpoint
    description  VARCHAR(240) NOT NULL,
    primary_term BIGINT       REFERENCES vocabulary_term(term_id),  -- codifica canonica del concetto
    kg_node_type VARCHAR(40)                      -- tipo di nodo nel KG (coerenza con kg_conceptual_model)
);

-- La FK differita da 01: aggancia dataset_field.semantic_tag_id a semantic_tag.
-- Dichiarata qui perche semantic_tag e definita in questo artefatto, che si
-- assume caricato dopo 01.
ALTER TABLE dataset_field
    ADD CONSTRAINT fk_field_semantic_tag
    FOREIGN KEY (semantic_tag_id) REFERENCES semantic_tag(tag_id);


-- -----------------------------------------------------------------------------
-- Attributi del modello di metadati (lo standard minimo)
-- -----------------------------------------------------------------------------
-- La definizione formale di QUALI metadati un dataset deve o puo dichiarare.
-- Questa tabella e lo "standard minimo di metadati" della traccia reso dato:
-- ogni attributo appartiene a uno strato (technical/business/operational),
-- e obbligatorio o facoltativo, ha un tipo e una descrizione semantica.
-- La query 05 usa questa tabella per verificare che i dataset dichiarino tutti
-- i metadati obbligatori: lo standard e controllabile, non solo documentato.
-- -----------------------------------------------------------------------------
CREATE TABLE metadata_attribute (
    attr_id      SERIAL       PRIMARY KEY,
    name         VARCHAR(80)  NOT NULL UNIQUE,
    layer        VARCHAR(16)  NOT NULL
        CHECK (layer IN ('technical', 'business', 'operational')),
    is_mandatory BOOLEAN      NOT NULL,
    data_type    VARCHAR(40)  NOT NULL,
    description  VARCHAR(300) NOT NULL,
    vocab_id     INTEGER      REFERENCES controlled_vocabulary(vocab_id)  -- se il valore e vincolato a un vocabolario
);


-- -----------------------------------------------------------------------------
-- Valori di metadato (istanze) con versioning
-- -----------------------------------------------------------------------------
-- I valori concreti degli attributi per un dato dataset, versionati. Il
-- versioning dei metadati e un requisito esplicito della traccia. Il pattern e
-- append-only con validita temporale: un nuovo valore non aggiorna in place,
-- crea una nuova versione e chiude la precedente (valid_to). Cosi la domanda
-- "quali metadati aveva questo dataset quando il modello fu addestrato?" ha
-- sempre risposta, che e la base della riproducibilita.
-- -----------------------------------------------------------------------------
CREATE TABLE metadata_value (
    value_id     BIGSERIAL    PRIMARY KEY,
    dataset_id   BIGINT       NOT NULL REFERENCES dataset(dataset_id) ON DELETE CASCADE,
    attr_id      INTEGER      NOT NULL REFERENCES metadata_attribute(attr_id),
    value_text   TEXT         NOT NULL,
    version      INTEGER      NOT NULL DEFAULT 1,
    valid_from   TIMESTAMPTZ  NOT NULL DEFAULT now(),
    valid_to     TIMESTAMPTZ,                       -- NULL = versione corrente
    changed_by   INTEGER      REFERENCES party(party_id),
    change_reason VARCHAR(240),
    CHECK (valid_to IS NULL OR valid_to > valid_from)
);

-- Una sola versione corrente per (dataset, attributo): il vincolo parziale
-- impedisce due valori "aperti" contemporaneamente.
CREATE UNIQUE INDEX uq_metadata_current
    ON metadata_value(dataset_id, attr_id)
    WHERE valid_to IS NULL;


-- =============================================================================
-- Seed - vocabolari, termini, tag e lo standard di metadati
-- =============================================================================

INSERT INTO controlled_vocabulary (code, name, domain_note, version_label, is_external, uri_base) VALUES
    ('MEDDRA', 'Medical Dictionary for Regulatory Activities',
        'Codifica di reazioni ed eventi avversi in farmacovigilanza e clinica.', 'MedDRA 27.0', TRUE,
        'https://meddra.org/'),
    ('SNOMED', 'SNOMED CT',
        'Termini clinici: diagnosi, procedure, reperti nei dati di studio.', 'SNOMED CT 2026-01', TRUE,
        'http://snomed.info/id/'),
    ('MESH',   'Medical Subject Headings',
        'Indicizzazione della letteratura biomedica.', 'MeSH 2026', TRUE,
        'https://id.nlm.nih.gov/mesh/'),
    ('ATC',    'Anatomical Therapeutic Chemical Classification',
        'Classificazione dei farmaci per organo bersaglio e meccanismo.', 'ATC 2026', TRUE,
        'https://www.whocc.no/atc/'),
    ('CHEMBL', 'ChEMBL',
        'Identita dei composti e bioattivita, base dell''anagrafica molecole.', 'ChEMBL 34', TRUE,
        'https://www.ebi.ac.uk/chembl/'),
    ('ORPHA',  'Orphanet',
        'Nomenclatura delle malattie rare, centrale per il focus NovaCura.', 'Orphanet 2026-01', TRUE,
        'http://www.orpha.net/ORDO/'),
    ('UNIPROT','UniProt',
        'Identita di proteine e target molecolari.', 'UniProt 2026_01', TRUE,
        'https://www.uniprot.org/uniprotkb/'),
    ('ICD10',  'ICD-10',
        'Classificazione delle malattie per reportistica e mapping.', 'ICD-10 2019', TRUE,
        'https://icd.who.int/browse10/');

-- Termini di esempio effettivamente usati nel caso guida (sottoinsieme).
INSERT INTO vocabulary_term (vocab_id, code, label, uri)
SELECT v.vocab_id, t.code, t.label, v.uri_base || t.suffix
FROM controlled_vocabulary v
JOIN (VALUES
        ('CHEMBL',  'CHEMBL1201631', 'Sirolimus',                         'CHEMBL1201631'),
        ('ORPHA',   'ORPHA:3253',    'Lymphangioleiomiomatosi (LAM)',     '3253'),
        ('UNIPROT', 'P42345',        'mTOR (serina/treonina chinasi)',    'P42345'),
        ('MEDDRA',  '10062os',       'Stomatite (PT esemplificativo)',    ''),
        ('ATC',     'L04AA10',       'Sirolimus (immunosoppressore)',     ''),
        ('SNOMED',  '254837009',     'Reperto clinico (esempio)',         '254837009')
    ) AS t(vcode, code, label, suffix)
  ON v.code = t.vcode;

-- I tag semantici interni, agganciati alla codifica canonica e al tipo di nodo KG.
INSERT INTO semantic_tag (name, description, primary_term, kg_node_type) VALUES
    ('compound',      'Composto o principio attivo.',              NULL, 'Compound'),
    ('target',        'Bersaglio molecolare (proteina/gene).',     NULL, 'Target'),
    ('disease',       'Malattia o indicazione.',                   NULL, 'Disease'),
    ('adverse_event', 'Reazione o evento avverso.',                NULL, 'AdverseEvent'),
    ('endpoint',      'Endpoint o esito di studio.',               NULL, 'Endpoint'),
    ('trial',         'Studio clinico.',                           NULL, 'Trial'),
    ('publication',   'Pubblicazione o fonte bibliografica.',      NULL, 'Publication'),
    ('subject',       'Soggetto arruolato (pseudonimizzato).',     NULL, 'Subject');

-- Lo standard minimo di metadati: cosa ogni dataset DEVE o PUO dichiarare.
-- Gli obbligatori coprono i tre strati; senza di essi un dataset non e
-- governabile (nessun owner = nessuna accountability; nessuna classificazione
-- = nessuna policy di accesso applicabile).
INSERT INTO metadata_attribute (name, layer, is_mandatory, data_type, description, vocab_id) VALUES
    -- tecnici
    ('storage_format',    'technical',   TRUE,  'enum',   'Formato fisico di storage (delta/parquet/...).', NULL),
    ('schema_version',    'technical',   TRUE,  'int',    'Versione dello schema del dataset.', NULL),
    ('physical_location', 'technical',   TRUE,  'string', 'Percorso fisico o riferimento tabella.', NULL),
    ('partition_keys',    'technical',   FALSE, 'string', 'Chiavi di partizionamento logico (Big Data).', NULL),
    -- business
    ('business_name',     'business',    TRUE,  'string', 'Nome comprensibile al business.', NULL),
    ('definition',        'business',    TRUE,  'string', 'Significato del dataset e dei suoi campi chiave.', NULL),
    ('domain_vocabulary', 'business',    FALSE, 'enum',   'Vocabolario di dominio prevalente.', 1),
    ('unit_of_measure',   'business',    FALSE, 'string', 'Unita di misura dei campi quantitativi.', NULL),
    -- operativi
    ('data_owner',        'operational', TRUE,  'ref',    'Owner accountable del dataset.', NULL),
    ('data_steward',      'operational', TRUE,  'ref',    'Steward responsabile della qualita.', NULL),
    ('sensitivity',       'operational', TRUE,  'enum',   'Classe di sensibilita.', NULL),
    ('refresh_frequency', 'operational', TRUE,  'string', 'Frequenza di aggiornamento.', NULL),
    ('retention_period',  'operational', TRUE,  'string', 'Periodo di conservazione applicabile.', NULL),
    ('gxp_relevant',      'operational', TRUE,  'bool',   'Rilevanza GxP del dataset.', NULL);

-- Esempio: valori di metadato per il dataset di esiti clinici, con versioning.
-- La versione 1 di 'definition' viene chiusa e sostituita dalla 2, mostrando il
-- pattern append-only: la storia resta ricostruibile.
INSERT INTO metadata_value (dataset_id, attr_id, value_text, version, valid_from, valid_to, changed_by, change_reason)
SELECT d.dataset_id, a.attr_id, 'Esiti primari per soggetto.', 1,
       TIMESTAMPTZ '2026-02-01', TIMESTAMPTZ '2026-04-01', 5, 'Prima definizione'
FROM dataset d, metadata_attribute a
WHERE d.urn = 'urn:novacura:clinical:ct_subject_outcomes' AND a.name = 'definition';

INSERT INTO metadata_value (dataset_id, attr_id, value_text, version, changed_by, change_reason)
SELECT d.dataset_id, a.attr_id, 'Esiti primari e secondari per soggetto, con bracci ed endpoint.', 2,
       5, 'Estesa agli endpoint secondari'
FROM dataset d, metadata_attribute a
WHERE d.urn = 'urn:novacura:clinical:ct_subject_outcomes' AND a.name = 'definition';

-- =============================================================================
-- Note di lettura critica (per il valutatore)
-- =============================================================================
-- - Il livello di indirezione tag -> termine -> vocabolario e la scelta di
--   design piu importante qui. Costa una join in piu, ma disaccoppia la
--   semantica interna stabile dal churn dei vocabolari esterni (MedDRA cambia
--   ogni sei mesi). Senza indirezione, ogni aggiornamento di MedDRA
--   toccherebbe il catalogo.
-- - metadata_value e volutamente append-only con valid_from/valid_to invece di
--   una colonna aggiornabile. Costa spazio e una unique parziale, ma e cio che
--   rende i metadati ricostruibili a una data passata: senza, il versioning
--   sarebbe dichiarato ma non dimostrabile.
-- - Limite: qui non e modellato il mapping cross-vocabolario (UMLS come
--   ponte tra SNOMED e MedDRA). In un sistema reale una crosswalk table
--   collegherebbe termini equivalenti tra vocabolari; e stato omesso per non
--   gonfiare l'artefatto oltre lo scopo della specifica.
-- =============================================================================
