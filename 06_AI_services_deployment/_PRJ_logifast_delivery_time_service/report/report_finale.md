# Report finale - Servizio di stima dei tempi di consegna

**Cliente**: LogiFast Solutions (fornitore logistico urbano e interurbano).
**Modulo 06 - AI Service Deployment.** Autore: Simone La Porta.

## 1. Contesto e valore

LogiFast vuole stimare il tempo di consegna (time-to-delivery) di ogni ordine al momento
della presa in carico, per informare clienti e operatori, pianificare le rotte e ridurre
reclami e reinvii. La soluzione espone un modello predittivo via API REST in Flask,
consumabile dal gestionale e dal front-end e-commerce.

Il valore non sta solo nella stima puntuale ma nell'**affidabilita' del servizio nel
tempo**: versionamento e monitoraggio permettono di accorgersi quando il modello smette di
essere accurato e di intervenire, invece di scoprirlo dai reclami.

## 2. Dati

Input noti alla presa in carico: origine, destinazione, data/ora di ritiro, peso, tipo di
servizio. Output: stima in ore, con score di affidabilita' e banda indicativa. Lo schema
completo e i vocabolari (20 citta', servizi `Express`/`Premium`) sono in
[`docs/data_schema.md`](../docs/data_schema.md).

Un primo risultato dell'esplorazione e' una **discrepanza tra traccia e artefatto**: la
traccia elenca cinque campi di input, ma il modello fornito ne usa quattro - `pickup_datetime`
non entra nella predizione. L'API lo accetta comunque (contratto stabile in vista del
riaddestramento) e lo dichiara come non usato.

## 3. Analisi esplorativa e validazione

Il dettaglio e in [`notebooks/exploration_validation.ipynb`](../notebooks/exploration_validation.ipynb).
L'artefatto e' una `Pipeline` scikit-learn: `OneHotEncoder` sulle categoriche
(citta', servizio) + passthrough sul peso, seguito da una `LinearRegression`.

Due letture, una intrinseca e una su dati.

- **Intrinseca** (solo coefficienti e risposte del modello): il modello e' poco sensibile
  agli input. Il peso da 1 a 50 kg sposta la stima di ~2 ore, Express e Premium di mezz'ora,
  le destinazioni restano in una banda stretta attorno alle 47 ore. Una regressione lineare
  su one-hot di citta' cattura un effetto additivo per citta', **non la distanza** tra
  origine e destinazione.
- **Su dati sintetici** (in assenza di uno storico etichettato, dataset generato da un
  processo documentato che incorpora la distanza geografica reale tra le citta'): MAE 20.2
  ore, RMSE 22.5 ore, **R2 = -4.82**. Un R2 negativo significa che il modello fa peggio di
  una semplice media: predice ~costante mentre il tempo reale varia molto con la distanza.

La conclusione non e' "il modello e' inutile": la traccia chiede di deployarlo, ed e' quello
che facciamo. La conclusione e' che il suo limite e' noto, misurato e sistematico (errore
sui tragitti lunghi), quindi **gestibile** dal monitoraggio invece che subito.

## 4. Scelta delle metriche

MAE e RMSE perche' il problema e' una regressione e l'errore va letto nell'unita' di
business (ore): MAE per l'errore tipico, RMSE perche' penalizza di piu' gli errori grossi,
che qui sono concentrati sui tragitti lunghi. R2 per posizionare il modello rispetto a una
baseline (la media): e' la metrica che ha reso evidente il problema. In produzione la
metrica chiave diventa l'**errore per segmento** (tratta, peso, servizio): la media
aggregata nasconderebbe proprio il punto debole.

## 5. Architettura della soluzione

```
  Client (e-commerce / operatori)
          |  JSON
          v
  Flask app (app.py)              <- routing, validazione payload, logging
          |
          v
  DeliveryModelService            <- validazione di dominio, affidabilita', metadati
          |
          v
  Pipeline sklearn (delivery.pkl) <- OHE(citta', servizio) + peso -> LinearRegression
          |
          v
  Risposta JSON                   <- stima (ore) + intervallo + reliability + warning
```

Due piani separati di proposito: trasporto HTTP (`app.py`) e contratto del modello
(`model_service.py`). La logica di predizione e' testabile senza server e il modello non
dipende da Flask. Endpoint: `POST /predict`, `POST /predict/batch`, `GET /health`,
`GET /model`. Dettaglio in [`docs/api_spec.md`](../docs/api_spec.md).

Scelte difese altrove e qui sintetizzate: `pickup_datetime` accettato ma segnalato come
non usato; citta' fuori vocabolario gestite con warning e affidabilita' ridotta invece che
con un errore; banda dell'intervallo pari all'RMSE sintetico (~22.5 ore), ampia perche'
onesta sul modello debole; sicurezza del pickle (verifica statica + hash SHA-256).

## 6. Elementi MLOps

Versionamento (dataset, modello, model card), pipeline concettuale di automazione,
monitoraggio (logging gia' attivo, metriche runtime e di qualita' per segmento, drift,
alerting) e governance (rollback su artefatti versionati, trigger di riaddestramento) sono
progettati in [`docs/mlops_design.md`](../docs/mlops_design.md). Il prossimo ciclo di
training ha un candidato ovvio: aggiungere distanza e `pickup_datetime`, le informazioni
che il modello attuale ignora.

## 7. Piano di rollout

Promozione a stadi, ciascuno con criterio di avanzamento e di rollback.

1. **Staging**: la suite `tests/test_api.py` passa, l'immagine Docker si avvia, `/health` e
   `/model` rispondono.
2. **Shadow**: il servizio gira in parallelo alla procedura attuale, le predizioni sono
   loggate ma non mostrate. Si raccoglie ground truth e si misura l'errore per segmento.
3. **Canary**: una quota ridotta di traffico reale (es. 5-10%). Avanzamento se latenza e
   errore restano nei limiti; rollback se un alert critico scatta.
4. **Full**: rollout completo, con monitoraggio e trigger di riaddestramento attivi.

## 8. Limiti e sviluppi

- Il modello ignora distanza e data/ora: e' il limite dominante, gia' misurato. Sviluppo
  prioritario: riaddestrare includendole.
- L'unita' (ore) e' un'assunzione sul range osservato, da confermare con la documentazione
  di training.
- `reliability_score` e intervallo sono proxy dichiarati, non statistiche rigorose: con
  dati reali si possono sostituire con intervalli di predizione veri.
- La validazione e' su dati sintetici: serve uno storico etichettato per metriche di
  produzione affidabili.
