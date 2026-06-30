# Servizio di stima dei tempi di consegna - LogiFast Solutions

Capstone del Modulo 06 (AI Service Deployment). Espone via API REST Flask un
modello pre-addestrato che stima il tempo di consegna (time-to-delivery) di un
ordine a partire dai dati noti alla presa in carico.

## Avvio rapido

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt          # scikit-learn==1.6.1 pinnato all'artefatto

# sviluppo
flask --app app run --port 8080
# oppure
python app.py
# produzione (esempio)
gunicorn -w 2 -b 0.0.0.0:8080 "app:create_app()"
```

Il modello `delivery.pkl` deve trovarsi nella cartella del progetto (gia' incluso).

## Endpoint

| Metodo | Path             | Descrizione                                            |
| ------ | ---------------- | ------------------------------------------------------ |
| POST   | `/predict`       | Predizione su un singolo ordine                        |
| POST   | `/predict/batch` | Predizione su una lista di ordini                      |
| GET    | `/health`        | Stato operativo del servizio + timestamp               |
| GET    | `/model`         | Versione, feature usate, categorie note, hash artefatto |

### Esempio

```bash
curl -X POST http://localhost:8080/predict -H "Content-Type: application/json" -d '{
  "pickup_location": "Milano",
  "delivery_location": "Roma",
  "pickup_datetime": "2026-07-01T09:30:00",
  "weight": 5.0,
  "service_type": "Express"
}'
```

```json
{
  "predicted_delivery_time_hours": 43.07,
  "confidence_interval_hours": [20.57, 65.57],
  "reliability_score": 1.0,
  "unit": "ore",
  "model_version": "1.0.0",
  "warnings": [],
  "input": { "...": "record validato" }
}
```

L'intervallo e' largo (banda di ~22.5 ore, pari all'RMSE sulla validazione
sintetica) perche' il modello fornito sottostima il segnale dominante, la
distanza tra le citta': la sua incertezza reale e' grande. La banda e' onesta,
non un difetto del servizio; stringerla richiede un modello migliore (vedi
`notebooks/exploration_validation.ipynb` e il piano di riaddestramento in
`docs/mlops_design.md`).

Lo schema completo di richieste e risposte e gli altri endpoint sono in
[`docs/api_spec.md`](docs/api_spec.md); lo schema dei dati in
[`docs/data_schema.md`](docs/data_schema.md).

## Note di progettazione

Tre scelte non ovvie, motivate qui perche' incidono sull'uso del servizio.

- **`pickup_datetime` accettato ma non usato.** L'introspezione dell'artefatto
  mostra che il modello e' addestrato su quattro feature
  (`pickup_location`, `delivery_location`, `weight`, `service_type`): la
  data/ora di ritiro non entra nella predizione. L'API la richiede comunque, per
  coerenza con la specifica e per non rompere il contratto quando il modello
  verra' riaddestrato includendola. La risposta lo segnala in `unused_fields`
  (endpoint `/model`).
- **Output in ore.** Il modello restituisce un numero senza unita'. Sul range
  osservato (circa 39-55, media ~46) l'interpretazione coerente con consegne
  interurbane e' in ore (~2 giorni), non minuti. L'assunzione e' dichiarata e
  andrebbe confermata con la documentazione di training.
- **Citta' fuori vocabolario: warning, non errore.** L'`OneHotEncoder` usa
  `handle_unknown='ignore'`, quindi una citta' sconosciuta non genera errore ma
  una codifica a zeri e una stima vicina all'intercetta. Il servizio non blocca,
  ma abbassa il `reliability_score` e aggiunge un warning: una predizione
  silenziosamente degradata e' peggio di una segnalata.

Il `reliability_score` e' un'euristica di in-distribution, non una probabilita':
una `LinearRegression` non espone `predict_proba`. L'`confidence_interval_hours`
e' una banda illustrativa (~1 RMSE sulla validazione sintetica), non un
intervallo statistico rigoroso. Entrambi sono dichiarati come tali.

## Sicurezza

`delivery.pkl` e' un pickle: l'unpickle esegue codice arbitrario. L'artefatto e'
stato verificato staticamente (solo classi `sklearn`/`numpy`) e la sua integrita'
e' controllata via SHA-256 al caricamento. In produzione l'hash va verificato
contro un registro fidato prima del load.

## Struttura

```
_PRJ_logifast_delivery_time_service/
  app.py                 # API Flask (layer di trasporto)
  model_service.py       # caricamento, validazione, predizione, metadati
  delivery.pkl           # artefatto del modello (sklearn 1.6.1)
  requirements.txt
  notebooks/             # esplorazione e validazione del modello
  docs/                  # schema dati, specifica API, design MLOps
  tests/                 # test di integrazione (pytest)
  report/                # report finale
```

## Test

```bash
pip install pytest
pytest -q
```

I test coprono i quattro endpoint, la validazione (campi mancanti, `service_type`
non valido, body non-JSON), il degrado su citta' ignota e il batch misto
ok/errore.
