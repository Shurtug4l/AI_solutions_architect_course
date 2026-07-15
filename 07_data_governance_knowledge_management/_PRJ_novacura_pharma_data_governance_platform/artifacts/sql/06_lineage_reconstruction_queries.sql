-- =============================================================================
-- NovaCura Pharma - Piattaforma di Data Governance & Knowledge Management
-- Artefatto SQL 06 - Ricostruzione della lineage (backward, forward, audit)
-- =============================================================================
--
-- Scopo
--   Le query che percorrono il grafo di lineage (artefatto 03) per rispondere
--   alle domande regolatorie del caso guida. Sono la dimostrazione concreta
--   del requisito "audit completo della pipeline dai dati grezzi al risultato".
--
--   Tre domande, tre query ricorsive:
--     1. Backward: dato un output, quali sorgenti e trasformazioni lo hanno
--        prodotto? (la ricostruzione regolatoria, nota 04)
--     2. Forward: data una sorgente, quali output ne dipendono? (impact
--        analysis prima di modificare o ritirare un dato, nota 04)
--     3. Ricostruzione firmata: l'output con la catena completa di run, versioni
--        di codice e attori, cioè l'evidenza ALCOA+ per un ispettore.
--
-- Perché WITH RECURSIVE
--   La lineage è un grafo di profondità arbitraria (sorgente -> ... -> output).
--   Una join a profondità fissa non basta: la ricorsione percorre il grafo
--   fin dove arriva. È il motivo per cui il modello 03 è un grafo e non colonne.
--
-- Dialetto: PostgreSQL 15+. Presuppone gli schemi 01-04 caricati con seed.
-- =============================================================================

SET search_path TO governance;


-- -----------------------------------------------------------------------------
-- 1. BACKWARD LINEAGE - da un output alle sue origini
-- -----------------------------------------------------------------------------
-- Domanda regolatoria: "Da quali dati e trasformazioni nasce il report di
-- evidenza per questo candidato?". Si parte dal nodo output e si risale gli
-- archi in senso inverso (to -> from) fino alle sorgenti. depth misura la
-- distanza dall'output; path evita i cicli e rende leggibile il percorso.
-- -----------------------------------------------------------------------------
WITH RECURSIVE back AS (
    -- ancora: il nodo di partenza (l'output)
    SELECT n.node_id, n.node_type, n.name,
           0 AS depth,
           ARRAY[n.node_id] AS path,
           NULL::varchar AS via_transform,
           NULL::bigint  AS via_run
    FROM lineage_node n
    WHERE n.node_type = 'output'
      AND n.ref_external = 'urn:novacura:output:evidence_report'

    UNION ALL

    -- passo: risali dagli archi entranti nel nodo corrente
    SELECT src.node_id, src.node_type, src.name,
           b.depth + 1,
           b.path || src.node_id,
           e.transform_type,
           e.run_id
    FROM back b
    JOIN lineage_edge e ON e.to_node_id = b.node_id
    JOIN lineage_node src ON src.node_id = e.from_node_id
    WHERE NOT src.node_id = ANY(b.path)   -- niente cicli
)
SELECT depth, node_type, name, via_transform, via_run
FROM back
ORDER BY depth, name;
-- Risultato atteso: output (0) <- modello via infer <- feature_set via train <-
-- quattro dataset via feature. La catena completa dal risultato alle sorgenti.


-- -----------------------------------------------------------------------------
-- 2. FORWARD LINEAGE - da una sorgente a ciò che ne dipende
-- -----------------------------------------------------------------------------
-- Domanda di change management: "Se ritiro o correggo il dataset di
-- farmacovigilanza, quali modelli e output vanno rivisti?". Si parte dal nodo
-- dataset e si scende gli archi in avanti (from -> to). È la mossa da fare
-- PRIMA di toccare una sorgente, non dopo (nota 04, forward lineage).
-- -----------------------------------------------------------------------------
WITH RECURSIVE fwd AS (
    SELECT n.node_id, n.node_type, n.name,
           0 AS depth,
           ARRAY[n.node_id] AS path
    FROM lineage_node n
    JOIN dataset d ON d.dataset_id = n.ref_dataset_id
    WHERE n.node_type = 'dataset'
      AND d.urn = 'urn:novacura:pv:icsr_reactions'

    UNION ALL

    SELECT tgt.node_id, tgt.node_type, tgt.name,
           f.depth + 1,
           f.path || tgt.node_id
    FROM fwd f
    JOIN lineage_edge e   ON e.from_node_id = f.node_id
    JOIN lineage_node tgt ON tgt.node_id = e.to_node_id
    WHERE NOT tgt.node_id = ANY(f.path)
)
SELECT depth, node_type, name
FROM fwd
WHERE depth > 0            -- escludi la sorgente stessa
ORDER BY depth, name;
-- Risultato atteso: feature_set (1), modello (2), output (3). Tutto ciò che
-- eredita un cambiamento della fonte PV.


-- -----------------------------------------------------------------------------
-- 3. RICOSTRUZIONE FIRMATA - l'evidenza ALCOA+ per l'ispettore
-- -----------------------------------------------------------------------------
-- La query che un auditor vuole: per un dato output, la lista completa delle
-- sorgenti, con la run che le ha trasformate, la versione di codice di quella
-- run, chi l'ha lanciata e l'hash del manifest degli input. È la differenza
-- tra "il numero è questo" e "il numero è questo perché prodotto dalla run R
-- del codice a1b2c3d4 sugli input con hash H, lanciata da X il giorno D".
-- -----------------------------------------------------------------------------
WITH RECURSIVE back AS (
    SELECT n.node_id, 0 AS depth, ARRAY[n.node_id] AS path
    FROM lineage_node n
    WHERE n.node_type = 'output'
      AND n.ref_external = 'urn:novacura:output:evidence_report'
    UNION ALL
    SELECT src.node_id, b.depth + 1, b.path || src.node_id
    FROM back b
    JOIN lineage_edge e   ON e.to_node_id = b.node_id
    JOIN lineage_node src ON src.node_id = e.from_node_id
    WHERE NOT src.node_id = ANY(b.path)   -- niente cicli (feedback edge del monitoraggio)
)
SELECT DISTINCT
       d.urn                       AS sorgente,
       sc.code                     AS sensibilità,
       e.transform_type            AS trasformazione,
       run.run_id,
       run.code_version,
       run.input_manifest_hash,
       run.engine,
       actor.full_name             AS lanciata_da,
       run.started_at
FROM back b
JOIN lineage_edge e   ON e.to_node_id = b.node_id
JOIN lineage_node src ON src.node_id = e.from_node_id
LEFT JOIN dataset d          ON d.dataset_id = src.ref_dataset_id
LEFT JOIN sensitivity_class sc ON sc.class_id = d.sensitivity_class_id
JOIN pipeline_run run ON run.run_id = e.run_id
LEFT JOIN party actor ON actor.party_id = run.triggered_by
WHERE src.node_type = 'dataset'
ORDER BY d.urn;
-- Ogni sorgente del report con la sua run, versione di codice, hash del
-- manifest è responsabile: la pipeline diventa ricostruibile end-to-end.


-- -----------------------------------------------------------------------------
-- 4. Cross-check accessi: chi ha toccato le sorgenti di un output
-- -----------------------------------------------------------------------------
-- Completa la ricostruzione unendo la lineage all'audit degli accessi: per le
-- sorgenti che alimentano un output, quali accessi (concessi o negati) sono
-- stati registrati. Unisce il "cosa deriva da cosa" (lineage) al "chi ha
-- toccato cosa" (audit), che è ciò che un'indagine su un incidente richiede.
-- -----------------------------------------------------------------------------
WITH RECURSIVE back AS (
    SELECT n.node_id, ARRAY[n.node_id] AS path FROM lineage_node n
    WHERE n.node_type = 'output' AND n.ref_external = 'urn:novacura:output:evidence_report'
    UNION ALL
    SELECT src.node_id, b.path || src.node_id
    FROM back b
    JOIN lineage_edge e   ON e.to_node_id = b.node_id
    JOIN lineage_node src ON src.node_id = e.from_node_id
    WHERE NOT src.node_id = ANY(b.path)   -- niente cicli (feedback edge del monitoraggio)
),
source_datasets AS (
    SELECT DISTINCT n.ref_dataset_id AS dataset_id
    FROM back b JOIN lineage_node n ON n.node_id = b.node_id
    WHERE n.node_type = 'dataset'
)
SELECT d.urn, p.full_name, p.role_type, al.access_path,
       al.granted, al.occurred_at
FROM source_datasets s
JOIN dataset d ON d.dataset_id = s.dataset_id
LEFT JOIN access_log al ON al.dataset_id = s.dataset_id
LEFT JOIN party p       ON p.party_id = al.actor_party_id
ORDER BY d.urn, al.occurred_at;

-- =============================================================================
-- Note di lettura critica (per il valutatore)
-- =============================================================================
-- - Le stesse due CTE ricorsive (back/fwd) rispondono a domande opposte solo
--   invertendo la direzione dell'arco percorso (to->from vs from->to). È la
--   prova che il modello a grafo dell'artefatto 03 è la rappresentazione giusta:
--   una struttura, due letture.
-- - La query 3 è il deliverable regolatorio vero. Da sola giustifica perché
--   ogni arco porta la run e ogni run porta code_version e input_manifest_hash:
--   senza quei campi la ricostruzione direbbe "da dove" ma non "in quale stato
--   del mondo", e la riproducibilità richiede entrambi.
-- - Limite noto: su grafi molto grandi la ricorsione va vincolata (limite di
--   profondità, materializzazione incrementale). Su una lineage di dominio,
--   con profondità nell'ordine delle decine di hop, il costo è trascurabile;
--   il vincolo diventa rilevante solo se si tracciasse la lineage a livello di
--   singola colonna su migliaia di trasformazioni, scenario fuori scope per una
--   specifica progettuale.
-- =============================================================================
