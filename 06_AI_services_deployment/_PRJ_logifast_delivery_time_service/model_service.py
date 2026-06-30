"""
================================================================================
model_service.py - Layer di servizio del modello (LogiFast Solutions)

                   Modulo 06: AI Service Deployment
================================================================================

Responsabilita': caricare l'artefatto, validare gli input, produrre le predizioni
e i metadati di versione. E' separato dal layer API (app.py) di proposito: il
contratto del modello (feature attese, categorie note, unita' di misura,
provenienza dell'artefatto) e' una preoccupazione diversa dal trasporto HTTP.
Tenere i due piani distinti rende la logica di predizione testabile senza un
server attivo e permette di sostituire Flask con un altro runtime senza toccarla.

Nota di sicurezza: il modello e' un pickle, e l'unpickle esegue codice arbitrario.
L'artefatto e' stato verificato staticamente (pickletools: solo classi
sklearn/numpy, nessun modulo sospetto) e la sua integrita' e' controllata via
SHA-256 al caricamento. In produzione l'hash andrebbe verificato contro un
registro fidato di modelli prima del load, non solo loggato.
================================================================================
"""
from __future__ import annotations

import hashlib
import logging
import pickle
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import sklearn

logger = logging.getLogger("logifast.model")

# ── Contratto del modello ─────────────────────────────────────────────────────
MODEL_DIR = Path(__file__).resolve().parent
MODEL_PATH = MODEL_DIR / "delivery.pkl"
MODEL_VERSION = "1.0.0"                 # versione semantica dell'artefatto deployato
PINNED_SKLEARN = "1.6.1"               # versione con cui il pickle e' stato serializzato
EXPECTED_SHA256 = "cb29574fa8836c9d3aa62f17760d300999c5bdbb9184b006041f95d6bbfbe260"
OUTPUT_UNIT = "ore"                    # assunzione motivata sul range osservato, vedi README

# Feature effettivamente usate dal modello: l'artefatto NON usa pickup_datetime.
MODEL_FEATURES = ["pickup_location", "delivery_location", "weight", "service_type"]
# Campi accettati dall'API: includono pickup_datetime per coerenza con la traccia,
# anche se il modello corrente lo ignora (vedi nota di progettazione nel README).
REQUEST_FIELDS = ["pickup_location", "delivery_location", "pickup_datetime", "weight", "service_type"]

# Banda per l'intervallo opzionale, pari all'RMSE sulla validazione sintetica
# (notebooks/exploration_validation.ipynb). E' ampia di proposito: il modello
# fornito sottostima il segnale distanza (R2 negativo), quindi la sua incertezza
# reale e' grande. Un intervallo piu' stretto richiede un modello migliore, non
# una banda piu' ottimistica. Dichiarata come illustrativa, non statistica.
PREDICTION_BAND_HOURS = 22.5


class ValidationError(ValueError):
    """Errore di validazione dell'input, con la lista puntuale dei problemi."""

    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__("; ".join(errors))


class DeliveryModelService:
    """
    Wrapper attorno alla Pipeline sklearn (ColumnTransformer + LinearRegression).

    Incapsulare il modello in una classe, invece di chiamarlo direttamente nelle
    route, isola tre responsabilita' che altrimenti finirebbero nel layer HTTP:
    introspezione dell'artefatto (categorie note, feature attese), validazione di
    dominio e calcolo di uno score di affidabilita'. L'artefatto e' caricato una
    sola volta alla creazione del servizio.
    """

    def __init__(self, model_path: Path | str = MODEL_PATH):
        self.model_path = Path(model_path)
        self.loaded_at = datetime.now(timezone.utc)
        self.artifact_sha256 = self._sha256(self.model_path)
        if self.artifact_sha256 != EXPECTED_SHA256:
            logger.warning("SHA-256 dell'artefatto inatteso: provenienza non verificata")
        if sklearn.__version__ != PINNED_SKLEARN:
            logger.warning("scikit-learn runtime %s diverso dal pin %s: unpickle non garantito",
                           sklearn.__version__, PINNED_SKLEARN)

        with open(self.model_path, "rb") as fh:
            self.model = pickle.load(fh)

        # Introspezione del ColumnTransformer per esporre le categorie note.
        pre = self.model.named_steps["preprocess"]
        self.feature_names = list(pre.feature_names_in_)
        self._known: dict[str, set[str]] = {}
        for _name, encoder, cols in pre.transformers_:
            if hasattr(encoder, "categories_"):
                for col, cats in zip(cols, encoder.categories_):
                    self._known[col] = set(map(str, cats))

    # ── Helper ────────────────────────────────────────────────────────────────
    @staticmethod
    def _sha256(path: Path) -> str:
        return hashlib.sha256(Path(path).read_bytes()).hexdigest()

    @staticmethod
    def _parse_dt(value) -> datetime | None:
        try:
            return datetime.fromisoformat(str(value))
        except (TypeError, ValueError):
            return None

    @property
    def known_locations(self) -> list[str]:
        return sorted(self._known.get("pickup_location", set()))

    @property
    def known_service_types(self) -> list[str]:
        return sorted(self._known.get("service_type", set()))

    # ── Validazione ─────────────────────────────────────────────────────────────
    def validate(self, record: dict) -> tuple[dict, list[str]]:
        """
        Valida un singolo record. Gli errori bloccanti alzano ValidationError (400).
        Le anomalie non bloccanti (citta' fuori vocabolario, datetime non parsabile)
        diventano warning: con handle_unknown='ignore' il modello produce comunque
        un output, solo meno affidabile, quindi rifiutare sarebbe troppo rigido.
        """
        if not isinstance(record, dict):
            raise ValidationError(["il record deve essere un oggetto JSON"])

        missing = [f for f in REQUEST_FIELDS if f not in record]
        if missing:
            raise ValidationError([f"campi mancanti: {', '.join(missing)}"])

        errors: list[str] = []
        warnings: list[str] = []

        weight = None
        try:
            weight = float(record["weight"])
            if weight <= 0:
                errors.append("weight deve essere > 0")
        except (TypeError, ValueError):
            errors.append("weight deve essere numerico")

        service = str(record["service_type"])
        if self.known_service_types and service not in self.known_service_types:
            errors.append(f"service_type non valido: atteso uno tra {self.known_service_types}")

        # pickup_datetime: richiesto dal contratto, non usato dal modello.
        # Validazione lasca, si avvisa senza bloccare.
        if self._parse_dt(record["pickup_datetime"]) is None:
            warnings.append("pickup_datetime non in formato ISO 8601 riconoscibile "
                            "(campo non usato dal modello corrente)")

        # Citta' fuori vocabolario -> warning, l'OHE le ignora e la stima degrada.
        for field in ("pickup_location", "delivery_location"):
            known = self._known.get(field, set())
            if known and str(record[field]) not in known:
                warnings.append(f"{field} '{record[field]}' fuori dal vocabolario del modello: "
                                "predizione meno affidabile")

        if errors:
            raise ValidationError(errors)

        clean = {
            "pickup_location": str(record["pickup_location"]),
            "delivery_location": str(record["delivery_location"]),
            "pickup_datetime": str(record["pickup_datetime"]),
            "weight": weight,
            "service_type": service,
        }
        return clean, warnings

    def _reliability(self, clean: dict) -> float:
        """
        Score di affidabilita' euristico in [0, 1]. NON e' una probabilita': una
        LinearRegression non espone predict_proba. Penalizza gli input fuori
        distribuzione (citta' ignote, peso implausibile), cioe' i casi in cui
        l'output del modello e' meno credibile. Dichiarato come proxy, non come
        intervallo statistico.
        """
        score = 1.0
        for field in ("pickup_location", "delivery_location"):
            known = self._known.get(field, set())
            if known and clean[field] not in known:
                score *= 0.6
        if clean["weight"] > 100:
            score *= 0.9
        return round(score, 2)

    # ── Predizione ──────────────────────────────────────────────────────────────
    def _format(self, value: float, clean: dict, warnings: list[str]) -> dict:
        return {
            "predicted_delivery_time_hours": round(value, 2),
            "confidence_interval_hours": [round(value - PREDICTION_BAND_HOURS, 2),
                                          round(value + PREDICTION_BAND_HOURS, 2)],
            "reliability_score": self._reliability(clean),
            "unit": OUTPUT_UNIT,
            "model_version": MODEL_VERSION,
            "warnings": warnings,
        }

    def predict_one(self, record: dict) -> dict:
        clean, warnings = self.validate(record)
        frame = pd.DataFrame([{f: clean[f] for f in MODEL_FEATURES}])
        value = float(self.model.predict(frame)[0])
        result = self._format(value, clean, warnings)
        result["input"] = clean
        return result

    def predict_batch(self, records: list[dict]) -> list[dict]:
        """
        Un record malformato non deve far cadere l'intero batch: si valida tutto,
        si raccolgono gli errori per indice, e si fa una sola chiamata vettoriale
        a predict sui record validi.
        """
        cleaned: list[dict | None] = []
        metas: list[dict] = []
        for i, rec in enumerate(records):
            try:
                clean, warnings = self.validate(rec)
                metas.append({"index": i, "clean": clean, "warnings": warnings})
                cleaned.append(clean)
            except ValidationError as exc:
                metas.append({"index": i, "errors": exc.errors})
                cleaned.append(None)

        valid = [c for c in cleaned if c is not None]
        preds: list[float] = []
        if valid:
            frame = pd.DataFrame([{f: c[f] for f in MODEL_FEATURES} for c in valid])
            preds = [float(p) for p in self.model.predict(frame)]

        results, cursor = [], 0
        for meta in metas:
            if "errors" in meta:
                results.append({"index": meta["index"], "status": "error", "errors": meta["errors"]})
                continue
            value = preds[cursor]
            cursor += 1
            record_result = {"index": meta["index"], "status": "ok"}
            record_result.update(self._format(value, meta["clean"], meta["warnings"]))
            results.append(record_result)
        return results

    # ── Metadati e versioning ────────────────────────────────────────────────────
    def metadata(self) -> dict:
        return {
            "model_version": MODEL_VERSION,
            "model_type": type(self.model.named_steps["regressor"]).__name__,
            "framework": f"scikit-learn {sklearn.__version__}",
            "pinned_sklearn": PINNED_SKLEARN,
            "features_used": MODEL_FEATURES,
            "request_fields": REQUEST_FIELDS,
            "unused_fields": ["pickup_datetime"],
            "output_unit": OUTPUT_UNIT,
            "known_locations": self.known_locations,
            "known_service_types": self.known_service_types,
            "artifact_sha256": self.artifact_sha256,
            "loaded_at": self.loaded_at.isoformat(),
        }
