# Specifica API REST

Base URL (sviluppo): `http://localhost:8080`. Tutte le richieste e risposte sono in
`application/json`. Lo schema dei campi e' in [`data_schema.md`](data_schema.md).

## POST /predict

Predizione su un singolo ordine.

**Richiesta**

```json
{
  "pickup_location": "Milano",
  "delivery_location": "Roma",
  "pickup_datetime": "2026-07-01T09:30:00",
  "weight": 5.0,
  "service_type": "Express"
}
```

**Risposta 200**

```json
{
  "predicted_delivery_time_hours": 43.07,
  "confidence_interval_hours": [20.57, 65.57],
  "reliability_score": 1.0,
  "unit": "ore",
  "model_version": "1.0.0",
  "warnings": [],
  "input": { "pickup_location": "Milano", "delivery_location": "Roma",
             "pickup_datetime": "2026-07-01T09:30:00", "weight": 5.0,
             "service_type": "Express" }
}
```

Con input fuori distribuzione la risposta resta 200 ma `reliability_score` scende e
`warnings` si popola (es. citta' ignota, `pickup_datetime` non parsabile).

## POST /predict/batch

Predizione su una lista di ordini. Un record malformato non fa cadere il batch: viene
isolato come errore, gli altri vengono predetti.

**Richiesta**: lista di record con lo stesso schema di `/predict`.

**Risposta 200**

```json
{
  "count": 2,
  "results": [
    { "index": 0, "status": "ok", "predicted_delivery_time_hours": 55.19,
      "confidence_interval_hours": [32.69, 77.69], "reliability_score": 1.0,
      "unit": "ore", "model_version": "1.0.0", "warnings": [] },
    { "index": 1, "status": "error", "errors": ["weight deve essere > 0"] }
  ]
}
```

## GET /health

Stato operativo del servizio.

```json
{ "status": "OK", "timestamp": "2026-07-01T07:49:00.152448+00:00" }
```

## GET /model

Versione e contratto del modello: utile per i client e per il versionamento.

```json
{
  "model_version": "1.0.0",
  "model_type": "LinearRegression",
  "framework": "scikit-learn 1.6.1",
  "pinned_sklearn": "1.6.1",
  "features_used": ["pickup_location", "delivery_location", "weight", "service_type"],
  "request_fields": ["pickup_location", "delivery_location", "pickup_datetime", "weight", "service_type"],
  "unused_fields": ["pickup_datetime"],
  "output_unit": "ore",
  "known_locations": ["Ancona", "... 20 citta ..."],
  "known_service_types": ["Express", "Premium"],
  "artifact_sha256": "cb29574f...",
  "loaded_at": "2026-06-30T21:49:00+00:00"
}
```

## Formato degli errori

Gli errori bloccanti hanno sempre la stessa forma, con la lista puntuale dei problemi:

```json
{ "status": "error", "errors": ["campi mancanti: weight"] }
```

## Codici di stato

| Codice | Quando |
| --- | --- |
| 200 | richiesta valida (anche con warning per input degradato) |
| 400 | payload assente/non-JSON, campi mancanti, `service_type` non valido, body batch non lista |
| 404 | endpoint inesistente |
| 500 | errore interno non previsto (loggato lato server) |
