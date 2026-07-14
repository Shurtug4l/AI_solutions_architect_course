# Specifica Big Data: layout, partizionamento e formati

Artefatto di specifica (non eseguibile) per il data plane distribuito della
piattaforma NovaCura. Definisce come i dataset del catalogo (artefatto SQL 01)
sono materializzati fisicamente nel lakehouse. Il control plane relazionale
descrive i dati; questo documento dice dove e come vivono a scala.

## Scelta architetturale: lakehouse

Archetipo: **lakehouse** (nota 08), non data warehouse puro né data lake puro.

Motivazione, con il costo e il beneficio espliciti:

- Il programma di drug repurposing integra dati **strutturati** (esiti clinici,
  misure di assay), **semi-strutturati** (ICSR in E2B R3, annotazioni di
  letteratura) e **non strutturati** (testo di pubblicazioni). Un data warehouse
  puro (schema-on-write) rifiuterebbe il testo e le annotazioni senza una
  modellazione anticipata onerosa; un data lake puro (schema-on-read) li
  accetterebbe tutti ma degraderebbe a "data swamp" senza catalogo e governance
  (nota 08).
- Il lakehouse tiene lo storage economico e tutti i tipi di dato del lake, e ci
  aggiunge transazioni ACID, metadati centralizzati e governance uniforme. In un
  contesto regolatorio le transazioni ACID non sono un lusso: una scrittura
  parziale su un dataset GxP è un record incompleto, e un record incompleto viola
  ALCOA+ (Complete). Il formato tabellare transazionale (Delta Lake) le
  garantisce.
- Costo accettato: il lakehouse ha complessità operativa maggiore di un lake
  nudo (gestione dei metadati, compaction, vacuum). Il beneficio, un solo piano
  governato per BI e ML invece di copiare dati tra lake e warehouse, ripaga in un
  contesto dove ogni copia è una superficie di audit in più.

Dove il warehouse resta giustificato: la reportistica regolatoria certificata e
a bassa latenza (submission, PSUR) può materializzare data mart dedicati a valle
del Gold, dove la rigidità schema-on-write è una feature.

## Layout medallion

Tre stadi di raffinamento (nota 08), con obblighi di governance crescenti.

```
  Bronze  ->  Silver  ->  Gold
  raw          conforme     pronto al consumo
  as-ingested  pulito       feature / aggregati / KG-ready
```

| Stadio | Contenuto | Schema | Governance | Sensibilità tipica |
|--------|-----------|--------|------------|--------------------|
| Bronze | Copia fedele della sorgente, append-only | schema-on-read | lineage di ingest, immutabile | come la sorgente |
| Silver | Dati puliti, deduplicati, pseudonimizzati, conformati ai vocabolari | schema imposto | DQ gate, pseudonimizzazione applicata | restricted -> confidential |
| Gold   | Feature set, aggregati, viste KG-ready | schema stabile, versionato | DQ pass, policy complete | confidential |

Regola di promozione: un dato non sale di stadio se non supera i controlli dello
stadio (DQ gate tra Bronze e Silver, copertura policy tra Silver e Gold). La
promozione è un evento di lineage (artefatto 03), non una copia silenziosa.

La pseudonimizzazione avviene alla transizione **Bronze -> Silver**: i dati
grezzi identificabili restano nel solo Bronze, con accesso ristretto, e da
Silver in poi circola lo pseudonimo. La chiave di re-identificazione vive in un
vault separato, fuori dal lakehouse (separazione tra prova che la
pseudonimizzazione è avvenuta e custodia del segreto, artefatto 03).

## Formati fisici

- **Delta Lake** (Parquet + transaction log) per i dataset Silver/Gold che
  richiedono ACID, time travel e schema enforcement. Il time travel di Delta è
  di fatto un lineage a livello di riga per un dato dataset: si può leggere lo
  stato a una versione passata, che è ciò che serve per riprodurre un input.
- **Parquet** semplice per il Bronze immutabile e per gli export analitici dove
  la transazionalità non serve.
- **Iceberg** è un'alternativa equivalente a Delta; la specifica resta agnostica
  purché il formato offra ACID, snapshot isolabili e schema evolution.

Colonnare in tutti i casi: le query di feature engineering leggono poche colonne
su molte righe, ed è il pattern che il colonnare ottimizza.

## Partizionamento logico

Principio: partizionare per le chiavi con cui si filtra e su cui si applica la
retention, non per le chiavi con cui si joina. Un partizionamento sbagliato non
rompe la correttezza ma distrugge le prestazioni (small files, scansioni piene).

| Dataset (urn) | Chiavi di partizione | Motivazione |
|---------------|----------------------|-------------|
| `clinical:ct_subject_outcomes` | `study_id`, `snapshot_date` | Si interroga per studio; la retention si applica alla chiusura dello studio |
| `lab:assay_measurements` | `assay_type`, `run_date` | Si filtra per tipo di assay; i run arrivano a lotti datati |
| `literature:evidence_annotations` | `ingest_month` | Volume incrementale mensile; retention breve per mese |
| `pv:icsr_reactions` | `receipt_year`, `seriousness` | Reporting regolatorio per anno; i casi seri hanno flussi prioritari |

Regole anti-degrado:

- **No over-partitioning.** Partizionare `ct_subject_outcomes` anche per
  `subject_id` genererebbe milioni di partizioni minuscole. Il soggetto è una
  chiave di filtro fine gestita da indici / Z-order, non da partizione.
- **Compaction** periodica sul Bronze ad alta frequenza (letteratura,
  farmacovigilanza) per evitare il problema degli small files.
- **Z-ordering** (o clustering) su `subject_id` e `compound_id` nei dataset Gold
  per accelerare i filtri fini senza esplodere le partizioni.

## Manifest di dataset

Ogni dataset distribuito espone un **manifest** (esempio in
`dataset_manifest_sample.json`) che ne dichiara schema, partizioni, metriche di
qualità, sensibilità e riferimenti di lineage. Il manifest è il punto di
aggancio tra data plane e control plane: il suo hash è registrato su
`pipeline_run.input_manifest_hash` (artefatto 03), così una run è legata
all'esatto stato degli input. Verificare l'hash è verificare che i dati non
siano cambiati sotto il modello.

Il manifest è anche ciò che rende il lakehouse **navigabile** invece che uno
swamp: senza un manifest per dataset e senza una voce di catalogo, un percorso
`s3://.../gold/...` è un file che nessuno sa interpretare (nota 08, il rischio
del data lake senza catalogo).

## Governance trasversale (sotto ogni stadio)

Coerente con lo schema a strati della nota 08: metadati/catalogo e
governance/sicurezza corrono sotto ogni stadio, non a valle.

- **Catalogo e metadati**: ogni tabella fisica ha una voce in `dataset`
  (artefatto 01) e un manifest; nessuna tabella orfana.
- **Accesso**: le ACL a livello di tabella e colonna nel catalogo del lakehouse
  (es. Unity Catalog) rispecchiano `sensitivity_class`; il mascheramento delle
  colonne PHI è applicato per i ruoli non autorizzati.
- **Lineage**: ogni job di promozione emette archi di lineage (artefatto 03) e
  un evento di audit (artefatto 04).
- **Qualità**: i DQ gate tra stadi eseguono le regole `dq_rule` (artefatto 05);
  un dataset che non supera il gate non viene promosso.

## Nota di lettura critica

Il rischio maggiore di questa architettura non è tecnico ma organizzativo: il
lakehouse concentra dati di sensibilità molto diversa (letteratura pubblica e
PHI a livello soggetto) su un solo piano. La separazione non può essere solo
logica. La difesa è a tre livelli: Bronze identificabile isolato con accesso
minimo, pseudonimizzazione obbligatoria alla promozione a Silver, e ACL +
mascheramento colonna applicati dal catalogo del lakehouse, non
dall'applicazione. Se anche uno solo di questi salta, la comodità di un piano
unico diventa una superficie di esfiltrazione unica.
