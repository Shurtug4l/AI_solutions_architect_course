#!/usr/bin/env python3
"""
================================================================================
PROGETTO: Servizio di stima dei tempi di consegna - LogiFast Solutions

          Modulo 06: AI Service Deployment
================================================================================

Autore : Simone La Porta
Data   : 2026-06-30


PANORAMICA
----------
API REST in Flask che espone un modello pre-addestrato per la stima del tempo di
consegna (time-to-delivery) degli ordini di LogiFast Solutions, fornitore
logistico urbano e interurbano. Il servizio riceve i dati noti al momento della
presa in carico (origine, destinazione, peso, tipo di servizio, data/ora di
ritiro) e restituisce una stima in ore, con uno score di affidabilita' e un
intervallo indicativo.

Il codice e' diviso in due piani: questo file e' il layer di trasporto (HTTP,
validazione del payload, logging, gestione degli errori); model_service.py e' il
layer del modello (caricamento dell'artefatto, contratto delle feature,
predizione). La separazione e' deliberata: il contratto del modello non deve
dipendere da Flask, e la logica di predizione resta testabile senza un server.

ARCHITETTURA
------------

   Client (e-commerce / operatori)
            |  JSON
            v
   Flask app (app.py)                 <- routing, validazione payload, logging
            |
            v
   DeliveryModelService               <- validazione di dominio, affidabilita'
   (model_service.py)
            |
            v
   Pipeline sklearn (delivery.pkl)    <- OneHotEncoder(citta', servizio) +
            |                             passthrough(peso) -> LinearRegression
            v
   Risposta JSON                      <- stima (ore) + CI + reliability + warning

ENDPOINT
--------
  POST /predict         predizione singola
  POST /predict/batch   predizione su lista di record
  GET  /health          stato operativo + timestamp
  GET  /model           versione, feature, categorie note, hash dell'artefatto

PREREQUISITI
------------
  python -m venv venv && source venv/bin/activate
  pip install -r requirements.txt        # scikit-learn==1.6.1 pinnato all'artefatto

ESECUZIONE
----------
  # sviluppo
  flask --app app run --port 8080
  # oppure
  python app.py
  # produzione (esempio)
  gunicorn -w 2 -b 0.0.0.0:8080 "app:create_app()"
================================================================================
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone

from flask import Flask, jsonify, request

from model_service import DeliveryModelService, ValidationError

# ── Logging minimo di richieste e predizioni (requisito non funzionale) ─────────
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger("logifast.api")


# ── Application factory ─────────────────────────────────────────────────────────
def create_app(model_path: str | None = None) -> Flask:
    """
    Factory invece di un'app globale: permette ai test di istanziare il servizio
    con un artefatto controllato e non esegue side effect al semplice import.
    Il modello viene caricato una sola volta, alla creazione dell'app.
    """
    app = Flask(__name__)
    service = DeliveryModelService(model_path) if model_path else DeliveryModelService()

    @app.get("/health")
    def health():
        return jsonify(status="OK", timestamp=datetime.now(timezone.utc).isoformat())

    @app.get("/model")
    def model_info():
        return jsonify(service.metadata())

    @app.post("/predict")
    def predict():
        payload = request.get_json(silent=True)
        if payload is None:
            return jsonify(status="error", errors=["body JSON assente o non valido"]), 400
        result = service.predict_one(payload)
        logger.info("predict %s->%s %s -> %.2f %s (rel=%.2f)",
                    result["input"]["pickup_location"], result["input"]["delivery_location"],
                    result["input"]["service_type"], result["predicted_delivery_time_hours"],
                    result["unit"], result["reliability_score"])
        return jsonify(result)

    @app.post("/predict/batch")
    def predict_batch():
        payload = request.get_json(silent=True)
        if not isinstance(payload, list):
            return jsonify(status="error", errors=["il body deve essere una lista di record"]), 400
        if not payload:
            return jsonify(status="error", errors=["lista vuota"]), 400
        results = service.predict_batch(payload)
        ok = sum(1 for r in results if r["status"] == "ok")
        logger.info("predict/batch ricevuti=%d ok=%d errori=%d", len(payload), ok, len(payload) - ok)
        return jsonify(count=len(results), results=results)

    # ── Gestione errori centralizzata ────────────────────────────────────────────
    @app.errorhandler(ValidationError)
    def on_validation_error(exc: ValidationError):
        return jsonify(status="error", errors=exc.errors), 400

    @app.errorhandler(404)
    def on_not_found(_exc):
        return jsonify(status="error", errors=["endpoint non trovato"]), 404

    @app.errorhandler(Exception)
    def on_unexpected(exc: Exception):
        logger.exception("errore non gestito")
        return jsonify(status="error", errors=["errore interno del servizio"]), 500

    return app


if __name__ == "__main__":
    create_app().run(host="0.0.0.0", port=8080)
