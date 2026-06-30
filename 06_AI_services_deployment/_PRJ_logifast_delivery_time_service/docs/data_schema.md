# Schema dei dati

## Input (record di ordine)

Campi accettati in `POST /predict` e in ogni elemento di `POST /predict/batch`.

| Campo | Tipo | Obbligatorio | Vincoli | Usato dal modello |
| --- | --- | --- | --- | --- |
| `pickup_location` | stringa | si | citta' di origine | si (one-hot) |
| `delivery_location` | stringa | si | citta' di destinazione | si (one-hot) |
| `pickup_datetime` | stringa | si | ISO 8601 consigliato | **no** (vedi nota) |
| `weight` | numero | si | > 0, in kg | si (passthrough) |
| `service_type` | stringa | si | `Express` o `Premium` | si (one-hot) |

**Nota su `pickup_datetime`.** Il modello fornito e' addestrato su quattro feature e non
usa la data/ora di ritiro. Il campo resta nel contratto per coerenza con la specifica e
per non rompere i client quando il modello verra' riaddestrato includendolo. La
validazione e' lasca: si tenta il parse ISO 8601 e si avvisa, senza bloccare. L'endpoint
`/model` lo elenca in `unused_fields`.

### Vocabolari chiusi

- **`service_type`**: `Express`, `Premium`. Un valore fuori da questo insieme produce un
  errore 400: e' un insieme di business chiuso, non ha senso degradare silenziosamente.
- **`pickup_location` / `delivery_location`**: 20 citta' note, apprese dall'artefatto e
  esposte da `/model`:
  Ancona, Bari, Bologna, Cagliari, Catania, Firenze, Genova, Lecce, Milano, Napoli,
  Palermo, Perugia, Pescara, Reggio Calabria, Roma, Salerno, Sassari, Torino, Trapani,
  Verona.
  Una citta' fuori vocabolario **non** genera errore (l'`OneHotEncoder` usa
  `handle_unknown='ignore'`, la codifica a zeri) ma abbassa il `reliability_score` e
  aggiunge un warning. La scelta e' deliberata: una stima silenziosamente degradata e'
  peggio di una segnalata.

## Output (predizione)

| Campo | Tipo | Descrizione |
| --- | --- | --- |
| `predicted_delivery_time_hours` | numero | stima del tempo di consegna, in ore |
| `confidence_interval_hours` | [numero, numero] | banda indicativa (~RMSE sintetico, ~22.5 h), non statistica |
| `reliability_score` | numero in [0, 1] | euristica di in-distribution, non una probabilita' |
| `unit` | stringa | `ore` |
| `model_version` | stringa | versione dell'artefatto deployato |
| `warnings` | lista di stringhe | anomalie non bloccanti |
| `input` | oggetto | record validato (solo in `/predict`) |

**Unita' di misura.** Il modello restituisce un numero senza unita'. Sul range osservato
(circa 39-55, media ~46) l'interpretazione coerente con consegne interurbane e' in ore
(~2 giorni medi), non minuti. Assunzione dichiarata, da confermare con la documentazione
di training del modello.

**`reliability_score`.** Parte da 1.0 e viene moltiplicato per 0.6 per ogni citta' fuori
vocabolario e per 0.9 se il peso supera i 100 kg. Non e' una probabilita': una
`LinearRegression` non espone `predict_proba`. E' un proxy di quanto l'input cade nella
distribuzione su cui il modello e' affidabile.
