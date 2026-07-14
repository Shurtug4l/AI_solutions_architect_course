# Modello concettuale del knowledge graph di dominio

Modello concettuale (nota 05: l'ontologia è la T-box, il grafo popolato è la
A-box) del knowledge graph biomedico che collega le entità del programma di
drug repurposing NovaCura. Rappresenta il livello di conoscenza strutturata su
cui poggiano il RAG governato (GraphRAG) e la spiegabilità degli output.

Perché un grafo e non tabelle (nota 08): la domanda centrale del repurposing
è multi-hop, "quali composti che agiscono su un target coinvolto in una malattia
rara hanno già evidenza clinica o di assay, senza segnali di sicurezza
ostativi?". Sulle tabelle è una pila di join; sul grafo è una passeggiata lungo
gli archi. La conoscenza densa di relazioni si modella come grafo.

## Tipi di nodo (entità)

Ogni tipo di nodo si aggancia a un vocabolario controllato (artefatto SQL 02),
così l'identità dei nodi è interoperabile e non locale.

| Nodo | Descrizione | Vocabolario di identità |
|------|-------------|-------------------------|
| `Compound` | Composto / principio attivo candidato | ChEMBL, ATC |
| `Target` | Bersaglio molecolare (proteina/gene) | UniProt |
| `Disease` | Malattia o indicazione (focus: malattie rare) | Orphanet, SNOMED CT, ICD-10 |
| `Trial` | Studio clinico | identificatore di registro (NCT-like) |
| `Subject` | Coorte / soggetto arruolato (pseudonimizzato) | pseudonimo interno |
| `Endpoint` | Endpoint o esito misurato | interno + SNOMED CT |
| `Assay` | Saggio di laboratorio su composto-target | interno (LIMS) |
| `AdverseEvent` | Reazione o evento avverso | MedDRA |
| `Publication` | Fonte bibliografica | PMID / DOI |
| `Evidence` | Nodo di evidenza reificato (vedi sotto) | interno |

## Tipi di arco (relazioni)

Le relazioni portano il significato (nota 05: relazioni logiche = meno
ambiguità). Le principali:

```
  (Compound) --targets--------> (Target)
  (Target)   --associated_with-> (Disease)
  (Compound) --indicated_for---> (Disease)        # indicazione approvata
  (Compound) --repurposing_candidate_for-> (Disease)   # ipotesi da valutare
  (Trial)    --studies---------> (Compound)
  (Trial)    --investigates----> (Disease)
  (Trial)    --enrolls---------> (Subject)
  (Trial)    --measures--------> (Endpoint)
  (Assay)    --tests-----------> (Compound)
  (Assay)    --against---------> (Target)
  (AdverseEvent) --reported_for-> (Compound)
  (Publication)  --reports-----> (Evidence)
  (Evidence)     --supports-----> (edge Compound-Disease)   # evidenza a favore
  (Evidence)     --refutes------> (edge Compound-Disease)   # evidenza contraria
```

## Evidenza reificata e provenienza sui fatti

Decisione di modellazione centrale: l'evidenza a favore o contro un'ipotesi di
repurposing è **reificata** in un nodo `Evidence`, non appesa come proprietà di
un arco. Motivazione, con il costo:

- Un'affermazione come "sirolimus è candidato per la LAM" non è un fatto atomico:
  è sostenuta da più fonti (un assay, una pubblicazione, un braccio di trial),
  ciascuna con forza e direzione diverse, alcune a favore, alcune contrarie. Un
  arco semplice non può portare più provenienze eterogenee.
- Reificare l'evidenza permette a ogni nodo `Evidence` di dichiarare la propria
  fonte (`derived_from` verso un `Publication`, un `Assay` o un `Trial`), la
  direzione (`supports` / `refutes`) e la forza. È ciò che rende la spiegazione
  dell'output tracciabile fino al dato originale (requisito del caso guida:
  "spiegazioni contestuali delle decisioni: provenienza dati, estratti,
  relazioni tra entità").
- Costo accettato: la reificazione aggiunge un nodo per ogni affermazione
  sostenuta, appesantendo il grafo. Il beneficio, provenienza per fatto invece
  che per grafo, è esattamente ciò che distingue un KG governato da uno
  decorativo.

Ogni nodo e ogni arco portano metadati di governance minimi: `source_dataset`
(urn del catalogo), `derived_from` (fonte), `asserted_at`, `confidence`. Un
triple senza provenienza è, nelle parole della nota 05, una bugia sicura di sé.

## Proprietà principali per nodo (estratto)

```
  Compound:     chembl_id, atc_code, preferred_name, modality
  Target:       uniprot_id, gene_symbol, protein_class
  Disease:      orpha_code, snomed_id, icd10, prevalence_class (rare)
  Trial:        registry_id, phase, status, start_date
  Assay:        assay_type, readout, value, unit, run_date
  AdverseEvent: meddra_pt, seriousness, frequency_class
  Publication:  pmid, doi, year, source_type
  Evidence:     direction (support/refute), strength, derived_from, asserted_at
```

## Vincoli ontologici (T-box)

L'ontologia impone regole, non solo tipi (nota 05: un'ontologia aggiunge
vincoli, non solo relazioni). Alcuni vincoli rilevanti:

- Un `Trial` che `studies` un `Compound` deve `investigate` almeno una `Disease`.
- Un arco `repurposing_candidate_for` deve essere sostenuto da almeno un nodo
  `Evidence` con `direction = support`; altrimenti è un'ipotesi non evidenziata
  e non entra nel Gold.
- Un `AdverseEvent` `reported_for` un `Compound` con `seriousness = serious` è un
  segnale che il modello di scoring deve poter leggere come penalità.
- `indicated_for` e `repurposing_candidate_for` sono disgiunti: un composto già
  indicato per una malattia non è "candidato al repurposing" per la stessa.

Questi vincoli rendono il reasoning sano (nota 08: un KG senza ontologia deriva
in un mess incoerente). Sono controllabili in fase di caricamento come un DQ
gate sul grafo.

## Competency questions (cosa il grafo deve saper rispondere)

Le domande che il grafo è progettato per rispondere, che sono anche il suo test
di accettazione:

1. Quali composti già in portafoglio agiscono su un target associato a una data
   malattia rara?
2. Per un candidato, qual è l'evidenza a favore e contraria, con la fonte di
   ciascun pezzo?
3. Esistono segnali di farmacovigilanza seri per il candidato che
   controindicano il repurposing?
4. Quali trial hanno misurato un endpoint rilevante per la malattia bersaglio?
5. Ricostruire il percorso entità->evidenza->fonte per giustificare uno score a
   un revisore regolatorio.

Le domande 2, 3 e 5 sono multi-hop e attraversano più tipi di nodo: sono
esattamente ciò che una rappresentazione tabellare renderebbe faticoso e il
grafo rende diretto.

## KG + AI: il ruolo nel sistema (nota 08)

Il grafo è la **memoria strutturata**, l'LLM è l'intelligenza. Nel flusso
governato (artefatto rag):

- Il grafo fornisce all'LLM fatti certi, correnti e strutturati (grounding):
  quali evidenze, quali fonti, quali segnali di sicurezza.
- L'LLM, a sua volta, aiuta a costruire e mantenere il grafo estraendo entità e
  relazioni dalla letteratura (nodo `Publication` -> `Evidence`), sotto controllo
  umano prima del commit.
- Il risultato è GraphRAG: il retrieval consegna al modello un sottografo
  connesso e provenienziato invece di un sacco di paragrafi, con meno
  allucinazioni e provenienza tracciabile (nota 08).

## Nota di lettura critica

Il rischio del modello è il popolamento automatico dalla letteratura:
l'estrazione di relazioni con un LLM introduce errori (relazioni inventate,
entità mal risolte) che, una volta nel grafo, diventano fatti autorevoli
consumati dal RAG. La difesa è la governance del grafo, non la fiducia
nell'estrazione: ogni `Evidence` di origine automatica nasce in stato
`proposed`, richiede validazione umana (uno steward) per passare a `asserted`, e
porta sempre la sua `confidence` e la sua fonte. Un grafo che accetta estrazioni
non validate eredita il problema del "looks right but is not" della nota 07, con
l'aggravante che lo cristallizza come conoscenza strutturata.
