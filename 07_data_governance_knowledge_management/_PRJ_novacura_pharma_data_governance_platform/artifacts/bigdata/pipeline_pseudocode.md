# Pseudocodice di pipeline: aggregazione evidenze per drug repurposing

Descrizione astratta e **non eseguibile** del job `PIPE-REPURPOSE-01`
(artefatto SQL 03). Copre il flusso tipico della traccia: ingest ->
trasformazione -> analisi -> modello -> output, con i checkpoint di governance
resi espliciti a ogni stadio. Lo scopo e mostrare *dove* la governance entra
nella pipeline (nota 01: prima, durante e dopo), non fornire codice pronto.

Convenzione: `governance.*` sono i punti in cui la pipeline scrive sul control
plane (catalogo, lineage, audit, DQ) o legge una policy. Non sono commenti
decorativi: sono il motivo per cui la pipeline e auditabile.

## Diagramma di flusso

```
  [1] INGEST            quattro fonti -> Bronze (append-only, immutabile)
        |                 governance: lineage(ingest) + audit(create)
        v
  [2] CONFORM+CLEAN     Bronze -> Silver (pulizia, dedup, vocabolari)
        |                 governance: DQ gate; se fail -> STOP, no promozione
        v
  [3] PSEUDONYMIZE      Silver (chiave -> vault esterno; da qui gira lo pseudonimo)
        |                 governance: audit(pseudonymize); PHI resta nel Bronze
        v
  [4] FEATURE           Silver x4 -> Gold feature_set (join candidato-malattia)
        |                 governance: lineage(feature) fan-in; policy check
        v
  [5] SCORE (MODEL)     feature_set -> punteggi candidati
        |                 governance: lineage(train/infer) + model_version
        v
  [6] EVIDENCE REPORT   punteggi + KG + citazioni -> report per candidato
        |                 governance: ai_generation_log (provenienza obbligatoria)
        v
  [7] MONITOR           drift, freshness, bias -> feedback
                          governance: DQ dinamica + alert; chiude il ciclo
```

## Pseudocodice annotato

```text
JOB repurpose_evidence_aggregation(candidate_compound, target_disease):

    run = governance.open_pipeline_run(
              pipeline="PIPE-REPURPOSE-01",
              code_version=CURRENT_COMMIT,
              triggered_by=CURRENT_USER)          # ALCOA+: Attributable, Contemporaneous

    # --- [1] INGEST: sorgenti -> Bronze -------------------------------------
    FOR source IN [clinical_ctms, lab_lims, literature_svc, safety_db]:
        raw = read_source(source)                 # nessuna trasformazione: copia fedele
        write_bronze(raw, mode=APPEND)            # immutabile (Original)
        governance.emit_lineage(edge="ingest", src=source, dst=bronze(source), run=run)
        governance.audit(action="create", entity=bronze(source), actor=CURRENT_USER)

    # --- [2] CONFORM + CLEAN: Bronze -> Silver ------------------------------
    FOR ds IN bronze_datasets:
        silver = clean(ds)                        # dedup, tipi, valori fuori dominio
        silver = map_to_vocabularies(silver)      # SNOMED/MedDRA/ChEMBL/ATC (artefatto 02)
        dq = governance.run_dq_gate(silver)       # regole dq_rule (artefatto 05)
        IF NOT dq.passed_critical:
            governance.audit(action="dq_fail", entity=silver, detail=dq.report)
            governance.close_run(run, status="aborted")
            STOP                                  # un critico fallito ferma la promozione
        write_silver(silver)
        governance.emit_lineage(edge="clean", src=bronze(ds), dst=silver, run=run)

    # --- [3] PSEUDONYMIZE: dati a livello soggetto --------------------------
    FOR ds IN silver_datasets WHERE contains_phi(ds):
        pseudo = pseudonymize(ds, key_ref=EXTERNAL_VAULT)   # chiave fuori dal lakehouse
        write_silver(pseudo, overwrite_phi_columns=TRUE)
        governance.audit(action="pseudonymize", entity=ds, actor=CURRENT_USER)
        # da qui in poi circola lo pseudonimo; il grezzo identificabile resta nel Bronze

    # --- [4] FEATURE: fan-in x4 -> Gold feature_set -------------------------
    features = build_features(                     # join candidato-malattia-target-evidenza
                   clinical=silver.clinical,
                   assay=silver.assay,
                   literature=silver.literature,
                   pv=silver.pv,
                   focus=(candidate_compound, target_disease))
    governance.assert_policy_coverage(features)    # Silver->Gold: policy complete o STOP
    write_gold(features)
    FOR src IN [clinical, assay, literature, pv]:
        governance.emit_lineage(edge="feature", src=silver(src), dst=features, run=run)

    # --- [5] SCORE: modello -------------------------------------------------
    model = load_model(registry="repurpose-scorer", version=PINNED)
    scores = model.infer(features)                 # nessun training in-line: modello versionato
    governance.emit_lineage(edge="infer", src=features, dst=scores,
                            run=run, model_version=model.version)

    # --- [6] EVIDENCE REPORT: RAG governato + citazioni ---------------------
    FOR candidate IN top(scores):
        evidence = governed_rag(                    # vedi artifacts/rag/rag_flow_spec.md
                       query=explain(candidate),
                       acl=CURRENT_USER.permissions, # access-filtered retrieval (nota 07)
                       kg_grounding=TRUE)            # GraphRAG sul sottografo candidato
        assert evidence.citations != EMPTY          # nessun output senza provenienza
        report = render(candidate, scores, evidence)
        governance.log_ai_generation(               # ai_generation_log (artefatto 04)
            query=evidence.query, chunks=evidence.chunks,
            kg_subgraph=evidence.subgraph, answer=report,
            citations=evidence.citations,
            model_version=LLM_VERSION, index_version=INDEX_VERSION,
            access_filter_applied=TRUE)

    governance.close_run(run, status="succeeded",
                         input_manifest_hash=hash(features.manifest))   # lega la run agli input

    # --- [7] MONITOR (asincrono) --------------------------------------------
    schedule_monitoring(
        drift_on=features, freshness_on=silver_datasets,
        bias_checks=fairness_suite,                 # note 01, 09
        on_alert=governance.raise_dq_incident)      # chiude il ciclo, riapre la creazione
```

## Nota di lettura critica

Tre decisioni di design meritano di essere difese esplicitamente.

- **Il DQ gate ferma la pipeline, non la avverte soltanto.** In [2], un
  fallimento su una dimensione critica aborta il run. e la traduzione operativa
  del principio della nota 03 (l'effetto composto): promuovere dati che falliscono
  un controllo critico significa addestrare o inferire su input inaffidabili, e
  in un contesto GxP e un difetto tracciabile. Il costo e che un dato sporco
  blocca la produzione; il beneficio e che non produce evidenza falsa.

- **Il modello e caricato versionato, non addestrato in-line.** In [5] non c'e
  training dentro il job di produzione: si carica una versione pinnata dal
  registry. Separare training e inferenza e cio che rende l'output riproducibile
  (stesso modello, stesso input, stesso risultato) e verificabile da un
  ispettore. Un training in-line renderebbe ogni run irripetibile.

- **La pseudonimizzazione precede il feature engineering, non lo segue.** In [3],
  i dati identificabili non arrivano mai al piano Gold. Filtrare l'identita a
  valle (dopo il join) lascerebbe PHI transitare in tabelle intermedie: lo stesso
  errore del "filtrare la risposta invece del contesto" nel RAG (nota 07). La
  difesa deve stare a monte del punto in cui i dati si diffondono.

Limite: lo pseudocodice presenta il flusso come lineare per leggibilita. In
esercizio [1], [2] e [7] girano con cadenze diverse (ingest continuo,
promozione batch, monitoraggio asincrono); il diagramma coglie le dipendenze di
dato, non la schedulazione reale.
