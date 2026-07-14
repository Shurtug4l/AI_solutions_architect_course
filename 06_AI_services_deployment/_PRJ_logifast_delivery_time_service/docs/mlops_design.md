# Disegno MLOps

Come da traccia, questi elementi sono **progettati e documentati**, non implementati come
ecosistema reale. Dove esiste già un gancio nel codice (logging, hash dell'artefatto,
endpoint `/model`, validazione con warning) lo richiamo: il disegno non parte da zero,
estende quello che il servizio espone.

Il filo conduttore è una scoperta della validazione (vedi `notebooks/`): il modello
fornito **ignora la distanza** tra origine e destinazione e predice un valore quasi
costante (R2 negativo, -4.82, contro una realtà distanza-aware). Un buon disegno MLOps
deve rendere questo degrado **visibile e azionabile**, non nasconderlo.

## 1. Versionamento

### Dataset
Ogni dataset di training è uno snapshot immutabile, identificato da `dataset_id`
(es. `delivery-2026-06`) e da un hash del contenuto. Si versionano: la finestra
temporale, lo schema, le 20 città in vocabolario, le statistiche di base (distribuzioni
di peso, tratte, servizio). In assenza di un data lake, anche un semplice manifest
versionato (CSV + `manifest.json` con hash) è sufficiente a garantire riproducibilità.

### Modello e metadati
L'artefatto è versionato con SemVer (`MODEL_VERSION`, oggi `1.0.0`) e accompagnato da una
**model card** con: tipo (`LinearRegression`), feature usate, `dataset_id` di training,
metriche di validazione, data, commit Git, e l'hash SHA-256 dell'artefatto (già calcolato
al load in `model_service.py`). L'endpoint `/model` espone questi metadati a runtime.

### Compatibilità del contratto
Il contratto API (`request_fields`) è più ampio delle feature del modello: include
`pickup_datetime`, oggi inutilizzato. Questo è deliberato e va versionato: quando il
modello verrà riaddestrato includendo la data/ora, i client esistenti non cambieranno.
Una modifica che rimuovesse o rinominasse un campo richiesto sarebbe invece breaking e
imporrebbe un bump di major.

## 2. Automazione (pipeline concettuale)

```
  commit / nuovo dataset
          |
          v
  [1] Qualità dati    -> schema, range, vocabolario città, % nulli
          |
          v
  [2] Training         -> fit Pipeline, salva artefatto + model card
          |
          v
  [3] Validazione      -> metriche su test, gate vs baseline e vs versione in prod
          |
          v
  [4] Build & deploy   -> immagine Docker, push su registry, deploy in staging
          |
          v
  [5] Promozione       -> shadow -> canary -> full (vedi rollout nel report)
```

### [1] Qualità dei dati
Controlli automatici prima del training: schema atteso, `weight > 0`, `service_type` nel
vocabolario, città note, percentuale di valori mancanti sotto soglia. Un fallimento
blocca la pipeline: meglio non addestrare che addestrare su dati sporchi.

### [2] Training
Riproducibile: seed fisso, dipendenze pinnate (`requirements.txt`, `scikit-learn==1.6.1`),
`dataset_id` registrato. L'output è l'artefatto più la model card.

### [3] Test e validazione pre-deploy
Due cancelli. Il primo, **test di regressione del modello**: le metriche sul set di test
non devono peggiorare oltre una soglia rispetto alla versione in produzione (no
regressioni silenziose). Il secondo, **test del servizio**: la suite `tests/test_api.py`
deve passare sulla nuova immagine (endpoint, validazione, batch). Solo con entrambi verdi
si procede.

### [4] Build e deploy
Immagine Docker costruita dalla pipeline, taggata con `MODEL_VERSION` e commit, spinta su
un registry. Il deploy in staging precede sempre la produzione.

## 3. Monitoraggio

### Logging di richieste e predizioni
Già attivo: `app.py` logga per ogni richiesta la tratta, il servizio, la stima e il
`reliability_score`. In produzione questi log alimentano un archivio strutturato (una
riga per predizione: input, output, versione modello, timestamp) che è la base di tutto
il resto.

### Metriche runtime
Latenza (p50/p95/p99), throughput, tasso di errori 4xx/5xx, quota di richieste con
`reliability_score` basso. Sono le metriche di servizio, indipendenti dalla qualità del
modello.

### Metriche di qualità
Richiedono il **ground truth differito**: il tempo di consegna effettivo, noto solo dopo
la consegna. Quando arriva, si accoppia alla predizione loggata e si calcola l'errore
(MAE, RMSE) **per segmento**: per tratta, fascia di peso, servizio. Il monitoraggio per
segmento non è un dettaglio: la validazione ha mostrato che l'errore di questo modello è
concentrato sui tragitti lunghi, e una media aggregata lo nasconderebbe.

### Drift detection
Due piani. **Data drift**: la distribuzione degli input cambia rispetto al training (nuove
città, pesi fuori range, mix di servizi diverso) - intercettabile già dai warning e dal
`reliability_score`, aggregati nel tempo. **Concept drift**: la relazione input-tempo
cambia (nuovi corrieri, congestione) - visibile come deriva dell'errore per segmento.

### Alerting
Soglie su: errore per segmento oltre una banda (es. RMSE > 1.5x baseline su una tratta),
quota di predizioni a bassa affidabilità in crescita, comparsa stabile di città fuori
vocabolario, p95 di latenza oltre l'SLA. L'alert è azionabile: indica il segmento, non
solo "il modello peggiora".

## 4. Governance

### Rollback
Gli artefatti sono versionati e immutabili: il rollback è ridistribuire l'immagine con la
`MODEL_VERSION` precedente. L'endpoint `/model` e l'hash SHA-256 permettono di verificare
quale versione è davvero in esecuzione. Criterio: si effettua rollback se la nuova
versione viola un gate di qualità in canary o se un alert critico scatta entro la
finestra di osservazione.

### Trigger di riaddestramento
- **Degrado**: errore per segmento oltre soglia su una finestra mobile.
- **Drift dei dati**: spostamento stabile della distribuzione degli input.
- **Nuovi dati**: disponibilità di uno storico etichettato sufficiente (es. trimestrale).
- **Gap noto**: il candidato naturale del prossimo ciclo è includere la distanza tra
  città e la `pickup_datetime`, le due informazioni che il modello attuale ignora.

### Tracciabilità e audit
Ogni predizione è ricostruibile: input loggato, `model_version`, hash dell'artefatto,
timestamp. Questo chiude il cerchio tra dato, modello e decisione, ed è il prerequisito
per qualunque analisi a posteriori di un reclamo o di un errore sistematico.
