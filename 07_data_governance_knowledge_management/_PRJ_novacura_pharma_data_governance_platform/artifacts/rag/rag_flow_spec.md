# Specifica funzionale del flusso RAG governato

Specifica a livello di requisiti e flussi informativi (non implementazione) del
flusso RAG che supporta la generazione di conoscenza contestuale nel programma
di drug repurposing. Segue la pipeline a sette passi della nota 07 e vi innesta
i controlli di governance a ogni passo. La meccanica del retrieval (chunking,
embedding, hybrid, reranking) è stata trattata nel modulo 02; qui la lente è la
governance, che è il topic del modulo 07.

Principio guida (nota 07): un RAG è affidabile solo quanto la data governance
dietro di esso. Il RAG è l'interfaccia; la governance è ciò che lavora dietro
le quinte per renderlo affidabile, sostenibile e spiegabile.

## Scopo e non-scopo

- **Scopo**: dato un candidato al repurposing, aggregare e sintetizzare evidenze
  verificate (clinica, assay, letteratura, PV) con provenienza esplicita, per
  supportare la decisione di un ricercatore o di un clinico.
- **Non-scopo**: il flusso non decide. Indica la via, separa ciò che è valido da
  ciò che non lo è, e cita le fonti (nota 07, esercizio ferroviario). La
  decisione resta all'umano accountable (HITL).

## Sorgenti e criteri di ammissione (passo 1: Source)

Non tutto entra nel corpus. L'ammissione è una decisione di governance fatta
prima dell'indicizzazione (nota 07: le decisioni interessanti sono tutte
decisioni di governance).

| Fonte | Ammissione | Criterio |
|-------|-----------|----------|
| Annotazioni di letteratura (Silver) | sì, con validazione | evidenza estratta e validata da uno steward |
| Misure di assay (Gold) | sì | dato strutturato governato, già DQ-passed |
| Esiti clinici (Gold, pseudonimizzati) | sì, con ACL stretta | solo aggregati/pseudonimi; PHI mai nel corpus |
| ICSR / reazioni (Gold) | sì, con ACL stretta | segnali di sicurezza, accesso ristretto |
| Documento non classificato | no | senza classificazione non entra (policy POL-CLS-01) |
| Fonte esterna non verificata | no | "non tutti i documenti sono corretti" è il default |

Regola: una fonte senza owner, senza classificazione o non fresca non è
ammessa. La selezione delle fonti è il primo controllo di qualità, applicato a
mano prima che esista un solo embedding.

## Ingestione e chunking (passo 2)

- Chunking guidato dalla domanda operativa, non da un conteggio di caratteri
  (nota 07: il chunking cattivo mette un tetto a tutto il resto). Un chunk =
  un'unità che risponde a una domanda ("qual è l'evidenza di potenza per questo
  composto su questo target").
- Ogni chunk registra i metadati di lineage e classificazione: `dataset_urn`,
  `sensitivity`, `source_ref`, `version`. Questi metadati sono ciò che
  abiliterà il filtro accessi e la citazione. Un chunk senza metadati di
  provenienza è inutilizzabile in un corpus governato.

## Indicizzazione (passo 3: Embedding)

- Vector store con i metadati accanto ai vettori: le etichette di accesso e la
  provenienza vivono qui, non in un disclaimer a valle.
- `index_version` versionato: quando cambia il modello di embedding o l'LLM,
  l'indice va rigenerato da zero (vettori di modelli diversi non sono
  confrontabili, nota 07). Il cambio di versione è un evento tracciato.

## Retrieval filtrato per accessi (passo 4)

Il controllo di governance più importante del flusso (note 07 e 09).

- Il filtro sui permessi vive **nel passo di retrieval**, prima del ranking, non
  dopo la generazione. Il vector store filtra i chunk sulle etichette di accesso
  del chiamante (lette da `sensitivity_class` e dalle ACL, artefatto SQL 01)
  prima di calcolare la similarità. Se un chunk vietato raggiunge il modello, la
  fuga di informazione è già avvenuta, qualunque cosa dica il filtro
  sull'output.
- Retrieval ibrido (semantico + lessicale/BM25) perché gli identificatori esatti
  del dominio (codice ChEMBL, PT MedDRA, id di trial) sono lessicali e la ricerca
  puramente vettoriale li perde (nota 07). Reranking a valle sulla shortlist.

## Grounding sul knowledge graph (GraphRAG)

Innesto del knowledge graph (artefatti kg_*) nel retrieval, che è ciò che
distingue questo flusso da un RAG puramente vettoriale (nota 08).

- Oltre ai chunk testuali, il retrieval recupera un **sottografo connesso** dal
  KG: il candidato, il suo target, la malattia, le evidenze `asserted` a favore
  e contro, i segnali PV. Il modello riceve fatti strutturati e provenienziati,
  non solo un sacco di paragrafi.
- Il grounding sul grafo riduce le allucinazioni (i fatti sono verificati contro
  il grafo prima) e fornisce provenienza per costruzione (ogni evidenza porta la
  sua fonte). Solo il sottografo `validationStatus = asserted` è interrogabile:
  la conoscenza non validata non fa da grounding.

## Generazione con citazione obbligatoria (passi 5-6)

- Il contesto iniettato è l'unica conoscenza che il modello è autorizzato a
  usare (passo 5). Nessuna conoscenza parametrica non citata entra nella
  risposta di record.
- Filtri a valle (passo 6): validazione linguistica, cross-check di coerenza tra
  la risposta e le fonti recuperate, controlli Responsible AI (bias, tono).
- **Citazione obbligatoria**: ogni affermazione della risposta nomina la fonte
  (documento/sezione, dataset urn, o nodo di evidenza del KG). La citazione è un
  requisito di governance, non un vezzo di UI (nota 07): una risposta senza
  provenienza è una supposizione fluente. Lo schema di log (artefatto SQL 04)
  impone a livello di CHECK che nessun output sia loggabile senza citazioni.

## Audit e feedback (passo 7)

- Ogni generazione è loggata su `ai_generation_log` (artefatto SQL 04) con
  query, chunk recuperati, sottografo KG, risposta, citazioni, versioni di
  modello e indice, e il flag `access_filter_applied`. È l'audit trail del
  processo di generazione AI richiesto dalla traccia.
- Il feedback dell'utente è il segnale che coglie il drift dell'embedding prima
  che degradi silenziosamente il corpus (nota 07). Un calo di utilità è il
  trigger per rivalutare il modello o rigenerare l'indice.

## Freschezza e ciclo di vita

- Cambio di una fonte -> re-embedding dei chunk interessati. Cambio del modello
  di embedding o dell'LLM -> rigenerazione completa dell'indice ("se cambio le
  regole, il gioco è cambiato", nota 07).
- Documenti scaduti rimossi dall'indice secondo la retention (artefatto SQL 01).
  La staleness è il fallimento silenzioso del RAG che "inventa" su dati vecchi
  (note 01 e 07): l'aggiornamento ha un owner e una cadenza, non è un buon
  proposito.

## Mappatura controlli di governance -> passi (sintesi, nota 07)

| Controllo di governance | Dove agisce |
|-------------------------|-------------|
| Qualità e validazione delle fonti | passo 2 (ingest), prima dell'embedding |
| Controllo accessi e sicurezza | passo 4 (retrieval) e passo 7 (log) |
| Gestione del ciclo di vita | passo 3 (embedding) e passo 7 (feedback) |
| Bias ed etica | passo 6 (generation) e a monte al passo 1 |
| Provenienza e spiegabilità | passi 5-6 (citazione) e KG grounding |

## Requisiti non funzionali specifici

- **Tracciabilità**: ogni output ricostruibile fino ai chunk e ai nodi di
  evidenza usati, con le versioni di modello e indice.
- **Segregazione**: due utenti con permessi diversi, sulla stessa query, devono
  ricevere risposte costruite su contesti diversi (il filtro è sul retrieval).
- **Riproducibilità**: fissati query, versione di modello e versione di indice,
  la risposta è ricostruibile; il log conserva i tre elementi.

## Nota di lettura critica

Il punto più fragile del flusso è il confine tra retrieval filtrato e
generazione. Tutta la sicurezza del sistema poggia sul fatto che i permessi
siano applicati prima che il contesto raggiunga il modello: un solo percorso che
inietti un chunk non filtrato (un tool ausiliario, una cache non segregata, un
prompt che rivela contesto di sistema) trasforma l'assistente in un canale di
esfiltrazione (nota 09). Per questo il flag `access_filter_applied` è loggato e
atteso sempre TRUE, e un FALSE è trattato come incidente di sicurezza, non come
warning. Il secondo rischio, più subdolo, è la fiducia nella fluenza: una
risposta ben scritta ma costruita su un'evidenza `proposed` non validata è
esattamente il "looks right but is not" della nota 07. La difesa non è un
disclaimer, è la disciplina di interrogare solo conoscenza `asserted` e di
esporre sempre la provenienza così che un umano possa verificare.
