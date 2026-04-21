"""
=============================================================================
LOGISERVER S.r.l. — Sistema di Monitoraggio Ordini e Magazzino
=============================================================================

DESCRIZIONE DEL PROGETTO
-------------------------
L'azienda LogiServe S.r.l. è una piccola realtà di e-commerce B2B specializzata
nella distribuzione di componenti elettrici per officine e rivenditori. Questo
applicativo a riga di comando gestisce il magazzino e gli ordini, permettendo di:
  - Registrare nuovi ordini con verifica disponibilità
  - Aggiornare le giacenze dopo l'evasione
  - Consultare lo stato del magazzino in tempo reale
  - Generare report giornalieri in formato CSV/TXT
  - Mantenere un log tracciato di tutte le operazioni

ARCHITETTURA LOGICA
-------------------
Il sistema è suddiviso in sei componenti principali con responsabilità distinte
(principio di separazione delle responsabilità / Single Responsibility Principle):

  - Logger          : scrive ogni operazione su file CSV con timestamp
  - DataManager     : carica e salva i dati JSON/CSV su disco
  - Warehouse       : gestisce il catalogo prodotti e le giacenze
  - OrderManager    : registra, evade e annulla gli ordini
  - ReportGenerator : costruisce i report giornalieri TXT e CSV
  - CLI             : interfaccia testuale a menu per l'utente finale

  Le dipendenze scorrono in una sola direzione:
    CLI → OrderManager/Warehouse/ReportGenerator → DataManager → Logger

FILE DATI
---------
  data/prodotti.json      : catalogo prodotti con giacenze correnti
  data/ordini.json        : lista completa degli ordini (tutti gli stati)
  data/log_operazioni.csv : storico cronologico di tutte le operazioni

ISTRUZIONI PER L'USO
--------------------
  1. Avviare lo script: python PRJ_sistema_monitoraggio_ordini_magazzino.py
  2. Alla prima esecuzione vengono creati i file dati con dati simulati
  3. Navigare il menu digitando il numero dell'opzione desiderata
  4. I report vengono salvati nella cartella reports/
  5. Lo stato persiste tra una sessione e l'altra grazie ai file JSON

SCENARI DI TEST SUGGERITI
--------------------------
  - Evadere un ordine completamente (P001 x5 con giacenza >5)
  - Tentare un ordine parziale (quantità > giacenza disponibile)
  - Verificare notifica punto di riordino dopo scarico consistente
  - Generare report giornaliero e controllare il file CSV prodotto
  - Riavviare il programma e verificare che lo stato sia preservato
"""

import csv
import json
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any, Optional

# =============================================================================
# CONFIGURAZIONE GLOBALE
# =============================================================================

# Percorsi dei file dati — tutti relativi alla directory di esecuzione
DATA_DIR = Path("data")          # cartella contenente prodotti.json, ordini.json, log CSV
REPORTS_DIR = Path("reports")   # cartella di output dei report giornalieri
PRODOTTI_FILE = DATA_DIR / "prodotti.json"
ORDINI_FILE = DATA_DIR / "ordini.json"
LOG_FILE = DATA_DIR / "log_operazioni.csv"

# Valori ammessi per il campo 'priorita' di un ordine (dal meno urgente al più urgente)
PRIORITA_VALIDE = ["bassa", "normale", "alta", "urgente"]

# Macchina a stati degli ordini:
#   nuovo → evaso        (evasione completa)
#   nuovo → parziale     (giacenza insufficiente per almeno una riga)
#   nuovo → in_attesa    (prodotto non disponibile o non trovato)
#   *     → annullato    (annullamento manuale, non applicabile a "evaso")
STATI_ORDINE = ["nuovo", "evaso", "parziale", "annullato", "in_attesa"]

# Operatore usato automaticamente dal sistema quando non è specificato dall'utente
OPERATORE_DEFAULT = "sistema"


# =============================================================================
# DATI INIZIALI SIMULATI
# =============================================================================
# Questi dati vengono scritti su file JSON solo alla prima esecuzione,
# quando i file non esistono ancora. Servono come punto di partenza realistico
# per testare il sistema senza inserimento manuale.

# Catalogo prodotti: 8 articoli distribuiti in 4 categorie merceologiche.
# Campi: codice univoco, nome descrittivo, categoria, giacenza attuale,
#        punto di riordino (soglia di allerta), unità di misura, prezzo.
PRODOTTI_INIZIALI: list[dict[str, Any]] = [
    {
        "codice": "P001",
        "nome": "Interruttore magnetotermico 16A",
        "categoria": "Protezione",
        "giacenza": 120,
        "punto_riordino": 30,   # sotto questa soglia scatta l'alert di riordino
        "unita_misura": "pz",
        "prezzo_unitario": 8.50
    },
    {
        "codice": "P002",
        "nome": "Cavo elettrico 2.5mm² (matassa 100m)",
        "categoria": "Cablaggio",
        "giacenza": 45,
        "punto_riordino": 15,
        "unita_misura": "matassa",
        "prezzo_unitario": 42.00
    },
    {
        "codice": "P003",
        "nome": "Presa industriale 32A IP44",
        "categoria": "Connettori",
        "giacenza": 60,
        "punto_riordino": 20,
        "unita_misura": "pz",
        "prezzo_unitario": 15.90
    },
    {
        "codice": "P004",
        "nome": "Quadro elettrico 24 moduli",
        "categoria": "Quadri",
        "giacenza": 18,
        "punto_riordino": 10,
        "unita_misura": "pz",
        "prezzo_unitario": 35.00
    },
    {
        "codice": "P005",
        "nome": "Interruttore differenziale 25A 30mA",
        "categoria": "Protezione",
        "giacenza": 85,
        "punto_riordino": 25,
        "unita_misura": "pz",
        "prezzo_unitario": 22.00
    },
    {
        "codice": "P006",
        "nome": "Morsetto a vite 4mm² (conf. 100pz)",
        "categoria": "Connettori",
        "giacenza": 32,
        "punto_riordino": 10,
        "unita_misura": "conf",
        "prezzo_unitario": 18.50
    },
    {
        "codice": "P007",
        "nome": "Canalina PVC 40x25mm (barra 2m)",
        "categoria": "Cablaggio",
        "giacenza": 200,
        "punto_riordino": 50,
        "unita_misura": "barra",
        "prezzo_unitario": 3.20
    },
    {
        "codice": "P008",
        "nome": "Trasformatore 230V/24V 60VA",
        "categoria": "Trasformatori",
        "giacenza": 12,
        "punto_riordino": 8,
        "unita_misura": "pz",
        "prezzo_unitario": 28.00
    }
]

# Lista ordini di esempio: tre ordini in stati diversi per testare
# tutti i flussi (evaso, parziale, nuovo/da evadere).
# Ogni riga ordine traccia sia la quantità richiesta sia quella già evasa,
# permettendo evasioni incrementali (es. ordini parziali completati in seguito).
ORDINI_INIZIALI: list[dict[str, Any]] = [
    {
        "id_ordine": "ORD-2026-001",
        "data": "2026-04-18",
        "cliente": "Officina Rossi & Figli",
        "priorita": "normale",
        "stato": "evaso",       # già completato, non modificabile
        "righe": [
            {"codice": "P001", "quantita_richiesta": 20, "quantita_evasa": 20},
            {"codice": "P003", "quantita_richiesta": 10, "quantita_evasa": 10}
        ],
        "note": ""
    },
    {
        "id_ordine": "ORD-2026-002",
        "data": "2026-04-19",
        "cliente": "Elettroforniture Bianchi",
        "priorita": "alta",
        "stato": "parziale",    # P002 non completamente disponibile al momento dell'ordine
        "righe": [
            {"codice": "P002", "quantita_richiesta": 20, "quantita_evasa": 15},
            {"codice": "P005", "quantita_richiesta": 30, "quantita_evasa": 30}
        ],
        "note": "P002 evaso parzialmente per scorta insufficiente"
    },
    {
        "id_ordine": "ORD-2026-003",
        "data": "2026-04-20",
        "cliente": "Rivendita Verdi S.n.c.",
        "priorita": "urgente",
        "stato": "nuovo",       # in attesa di evasione — ideale per testare il flusso
        "righe": [
            {"codice": "P004", "quantita_richiesta": 5, "quantita_evasa": 0},
            {"codice": "P008", "quantita_richiesta": 3, "quantita_evasa": 0}
        ],
        "note": ""
    }
]


# =============================================================================
# LOGGER
# =============================================================================

class Logger:
    """
    Traccia cronologicamente tutte le operazioni rilevanti del sistema
    scrivendole in append su un file CSV con timestamp e operatore.

    Ogni riga del log contiene:
      timestamp  — data e ora dell'operazione (formato YYYY-MM-DD HH:MM:SS)
      operatore  — nome dell'utente che ha eseguito l'operazione
      operazione — tipo di evento (es. NUOVO_ORDINE, EVASIONE_ORDINE, ...)
      risorsa    — identificatore dell'entità coinvolta (codice prodotto, ID ordine, ...)
      dettaglio  — testo libero con informazioni aggiuntive sull'evento

    Il file viene creato automaticamente se non esiste, comprensiva la directory padre.
    """

    def __init__(self, log_path: Path):
        """
        Inizializza il logger con il percorso del file CSV.
        Crea il file con intestazione se non esiste ancora.
        """
        self.log_path = log_path
        self._init_file()

    def _init_file(self):
        """
        Garantisce che la directory padre e il file CSV esistano.
        Se il file non esiste, lo crea con la riga di intestazione.
        Usa parents=True per creare eventuali directory intermedie mancanti.
        """
        # Crea data/ (e qualsiasi sotto-directory) se non esistono
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.log_path.exists():
            with open(self.log_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["timestamp", "operatore", "operazione", "risorsa", "dettaglio"])

    def log(self, operazione: str, risorsa: str, dettaglio: str = "", operatore: str = OPERATORE_DEFAULT):
        """
        Aggiunge una riga al file di log in modalità append.

        Args:
            operazione: identificatore del tipo di evento (es. "NUOVO_ORDINE")
            risorsa:    entità coinvolta (es. "ORD-2026-003" oppure "P001")
            dettaglio:  testo aggiuntivo descrittivo (opzionale)
            operatore:  nome dell'utente; default = OPERATORE_DEFAULT ("sistema")
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Apertura in append ("a") per preservare lo storico tra le sessioni
        with open(self.log_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, operatore, operazione, risorsa, dettaglio])

    def get_log_oggi(self) -> list[dict[str, Any]]:
        """
        Restituisce tutte le voci di log della giornata corrente.

        Il filtraggio avviene confrontando il prefisso del timestamp (YYYY-MM-DD)
        con la data odierna, evitando la conversione a oggetto datetime per semplicità.

        Returns:
            Lista di dizionari (una per riga CSV), filtrata per la data odierna.
            Lista vuota se il file non esiste o non ci sono eventi oggi.
        """
        oggi = date.today().strftime("%Y-%m-%d")
        entries = []
        try:
            with open(self.log_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)   # legge le colonne come chiavi del dizionario
                for row in reader:
                    # Confronto per prefisso: "2026-04-21 14:30:00".startswith("2026-04-21")
                    if row["timestamp"].startswith(oggi):
                        entries.append(row)
        except FileNotFoundError:
            pass   # file non ancora creato: nessun log disponibile
        return entries


# =============================================================================
# DATA MANAGER
# =============================================================================

class DataManager:
    """
    Gestisce la persistenza dei dati su disco, separando completamente
    la logica di I/O dal resto del sistema.

    Responsabilità:
      - Caricare prodotti e ordini da file JSON al momento dell'avvio
      - Salvare le modifiche su file JSON dopo ogni operazione significativa
      - Creare i file con dati iniziali simulati alla prima esecuzione

    Formato scelto: JSON con indentazione per leggibilità umana e
    compatibilità con strumenti esterni (Excel, script di analisi, ecc.).
    """

    def __init__(self, logger: Logger):
        """
        Inizializza il DataManager e crea le directory necessarie se assenti.

        Args:
            logger: istanza Logger per tracciare le operazioni di I/O
        """
        self.logger = logger
        # Crea data/ e reports/ se non esistono (exist_ok evita errori se già presenti)
        DATA_DIR.mkdir(exist_ok=True)
        REPORTS_DIR.mkdir(exist_ok=True)

    def carica_prodotti(self) -> list[dict[str, Any]]:
        """
        Carica il catalogo prodotti da file JSON.
        Se il file non esiste (prima esecuzione), lo crea con PRODOTTI_INIZIALI.

        Returns:
            Lista di dizionari, uno per prodotto.
        """
        if not PRODOTTI_FILE.exists():
            # Prima esecuzione: inizializza il catalogo con i dati simulati
            self._salva_json(PRODOTTI_FILE, PRODOTTI_INIZIALI)
            self.logger.log("INIT", "prodotti.json", f"Creati {len(PRODOTTI_INIZIALI)} prodotti iniziali")
        return self._carica_json(PRODOTTI_FILE)

    def salva_prodotti(self, prodotti: list[dict[str, Any]]):
        """
        Sovrascrive il file prodotti con la lista aggiornata.
        Chiamato da Warehouse.salva() dopo ogni modifica alle giacenze.

        Args:
            prodotti: lista completa dei prodotti nello stato corrente
        """
        self._salva_json(PRODOTTI_FILE, prodotti)
        self.logger.log("SALVATAGGIO", "prodotti.json", f"{len(prodotti)} prodotti salvati")

    def carica_ordini(self) -> list[dict[str, Any]]:
        """
        Carica la lista ordini da file JSON.
        Se il file non esiste (prima esecuzione), lo crea con ORDINI_INIZIALI.

        Returns:
            Lista di dizionari, uno per ordine.
        """
        if not ORDINI_FILE.exists():
            # Prima esecuzione: inizializza con gli ordini simulati
            self._salva_json(ORDINI_FILE, ORDINI_INIZIALI)
            self.logger.log("INIT", "ordini.json", f"Creati {len(ORDINI_INIZIALI)} ordini iniziali")
        return self._carica_json(ORDINI_FILE)

    def salva_ordini(self, ordini: list[dict[str, Any]]):
        """
        Sovrascrive il file ordini con la lista aggiornata.
        Chiamato da OrderManager.salva() dopo registrazione/evasione/annullamento.

        Args:
            ordini: lista completa degli ordini nello stato corrente
        """
        self._salva_json(ORDINI_FILE, ordini)
        self.logger.log("SALVATAGGIO", "ordini.json", f"{len(ordini)} ordini salvati")

    @staticmethod
    def _carica_json(path: Path) -> list[dict[str, Any]]:
        """
        Legge e deserializza un file JSON dal percorso indicato.

        Args:
            path: percorso assoluto o relativo del file JSON

        Returns:
            Lista di dizionari Python corrispondente al contenuto JSON.
        """
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def _salva_json(path: Path, data: Any):
        """
        Serializza e scrive un oggetto Python come JSON formattato.

        ensure_ascii=False preserva i caratteri accentati (à, è, ò, ...).
        indent=2 rende il file leggibile con un editor di testo.

        Args:
            path: percorso di destinazione
            data: oggetto Python serializzabile (lista, dizionario, ecc.)
        """
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


# =============================================================================
# WAREHOUSE
# =============================================================================

class Warehouse:
    """
    Gestisce il catalogo prodotti e le operazioni sulle giacenze di magazzino.

    Mantiene in memoria la lista dei prodotti (self.prodotti) per evitare
    letture ripetute dal disco durante la sessione. Le modifiche vengono
    propagate al file JSON tramite salva() al termine di ogni operazione.

    Struttura di un prodotto:
        {
          "codice":          str   — identificatore univoco (es. "P001")
          "nome":            str   — descrizione commerciale
          "categoria":       str   — raggruppamento merceologico
          "giacenza":        int   — unità attualmente disponibili
          "punto_riordino":  int   — soglia minima: sotto questa si attiva l'alert
          "unita_misura":    str   — es. "pz", "matassa", "barra"
          "prezzo_unitario": float — prezzo di vendita per unità
        }
    """

    def __init__(self, data_manager: DataManager, logger: Logger):
        """
        Carica il catalogo prodotti dal DataManager all'avvio.

        Args:
            data_manager: istanza DataManager per la persistenza
            logger:       istanza Logger per tracciare le modifiche
        """
        self.dm = data_manager
        self.logger = logger
        # Lista di prodotti in memoria — modificata direttamente dai metodi della classe
        self.prodotti: list[dict[str, Any]] = self.dm.carica_prodotti()

    def salva(self):
        """Persiste lo stato corrente di self.prodotti su disco tramite DataManager."""
        self.dm.salva_prodotti(self.prodotti)

    def get_prodotto(self, codice: str) -> Optional[dict[str, Any]]:
        """
        Cerca un prodotto per codice (case-insensitive).

        Il confronto è case-insensitive per tollerare input come "p001" o "P001".

        Args:
            codice: codice prodotto da cercare (es. "P001")

        Returns:
            Il dizionario del prodotto se trovato, None altrimenti.
            Nota: restituisce un riferimento diretto — le modifiche al dizionario
            ritornato aggiornano direttamente self.prodotti.
        """
        for p in self.prodotti:
            if p["codice"].upper() == codice.upper():
                return p
        return None

    def get_prodotti_filtrati(
        self,
        codice: str = "",
        categoria: str = "",
        sotto_riordino: bool = False
    ) -> list[dict[str, Any]]:
        """
        Restituisce i prodotti che soddisfano tutti i criteri di filtro attivi.
        I filtri sono combinati con AND logico: un prodotto deve soddisfarli tutti.
        I confronti testuali sono case-insensitive e per sottostringa.

        Args:
            codice:         sottostringa del codice (es. "P0" trova P001, P002, ...)
            categoria:      sottostringa della categoria (es. "prot" trova "Protezione")
            sotto_riordino: se True, restituisce solo prodotti con giacenza ≤ punto_riordino

        Returns:
            Lista filtrata di prodotti; lista vuota se nessun prodotto corrisponde.
        """
        risultati = self.prodotti

        # Filtro per codice: ricerca per sottostringa case-insensitive
        if codice:
            risultati = [p for p in risultati if codice.upper() in p["codice"].upper()]

        # Filtro per categoria: ricerca per sottostringa case-insensitive
        if categoria:
            risultati = [p for p in risultati if categoria.lower() in p["categoria"].lower()]

        # Filtro giacenza: include solo i prodotti che richiedono riordino
        if sotto_riordino:
            risultati = [p for p in risultati if p["giacenza"] <= p["punto_riordino"]]

        return risultati

    def aggiorna_giacenza(self, codice: str, delta: int, operatore: str = OPERATORE_DEFAULT) -> bool:
        """
        Applica una variazione alla giacenza di un prodotto e registra l'evento nel log.
        Dopo l'aggiornamento, controlla se la nuova giacenza è scesa sotto il punto
        di riordino e, in caso affermativo, aggiunge un secondo evento ALERT_RIORDINO.

        Nota: non impedisce giacenze negative — la verifica è responsabilità del chiamante
        (CLI._aggiorna_giacenza_manuale mostra un avviso e chiede conferma all'utente).

        Args:
            codice:    codice del prodotto da aggiornare
            delta:     variazione positiva (carico) o negativa (scarico)
            operatore: chi ha eseguito l'operazione

        Returns:
            True se il prodotto esiste ed è stato aggiornato, False altrimenti.
        """
        prodotto = self.get_prodotto(codice)
        if not prodotto:
            return False   # codice non trovato: operazione ignorata silenziosamente

        vecchia = prodotto["giacenza"]
        prodotto["giacenza"] += delta   # modifica in-place del dizionario in memoria

        # Log della variazione con il valore prima e dopo per tracciabilità
        self.logger.log(
            "AGGIORNAMENTO_GIACENZA",
            codice,
            f"{vecchia} → {prodotto['giacenza']} (delta: {delta:+d})",
            operatore
        )

        # Controllo soglia di riordino: alert separato per permettere filtri analitici sul log
        if prodotto["giacenza"] <= prodotto["punto_riordino"]:
            self.logger.log(
                "ALERT_RIORDINO",
                codice,
                f"Giacenza {prodotto['giacenza']} ≤ punto riordino {prodotto['punto_riordino']}",
                operatore
            )

        return True

    def aggiungi_prodotto(self, prodotto: dict[str, Any], operatore: str = OPERATORE_DEFAULT):
        """
        Aggiunge un nuovo prodotto al catalogo in memoria.
        Il codice viene normalizzato in maiuscolo prima dell'inserimento
        per garantire coerenza con get_prodotto() (case-insensitive).

        Args:
            prodotto:  dizionario con tutti i campi richiesti del prodotto
            operatore: chi ha eseguito l'inserimento
        """
        # Normalizzazione del codice: sempre maiuscolo nel catalogo
        codice = prodotto["codice"].upper()
        prodotto["codice"] = codice
        self.prodotti.append(prodotto)
        self.logger.log("NUOVO_PRODOTTO", codice, prodotto["nome"], operatore)

    def categorie(self) -> list[str]:
        """
        Restituisce l'elenco univoco e ordinato alfabeticamente delle categorie
        presenti nel catalogo. Usato dalla CLI per suggerire le categorie disponibili.

        Returns:
            Lista di stringhe, es. ["Cablaggio", "Connettori", "Protezione", "Quadri"]
        """
        return sorted(set(p["categoria"] for p in self.prodotti))

    def prodotti_sotto_riordino(self) -> list[dict[str, Any]]:
        """
        Restituisce tutti i prodotti la cui giacenza è al di sotto (o uguale)
        al punto di riordino. Usato per gli alert all'avvio e nel report giornaliero.

        Returns:
            Lista di prodotti che richiedono riapprovvigionamento.
        """
        return [p for p in self.prodotti if p["giacenza"] <= p["punto_riordino"]]


# =============================================================================
# ORDER MANAGER
# =============================================================================

class OrderManager:
    """
    Gestisce il ciclo di vita degli ordini: registrazione, evasione e annullamento.

    Mantiene in memoria la lista degli ordini (self.ordini) e coordina con Warehouse
    per verificare disponibilità e aggiornare le giacenze durante l'evasione.

    Struttura di un ordine:
        {
          "id_ordine":  str  — identificatore univoco generato automaticamente (es. "ORD-2026-004")
          "data":       str  — data di registrazione in formato YYYY-MM-DD
          "cliente":    str  — ragione sociale del cliente
          "priorita":   str  — uno tra PRIORITA_VALIDE
          "stato":      str  — uno tra STATI_ORDINE (macchina a stati)
          "righe":      list — lista di righe ordine (vedi struttura sotto)
          "note":       str  — testo libero per annotazioni
        }

    Struttura di una riga ordine:
        {
          "codice":             str — codice prodotto
          "quantita_richiesta": int — quantità totale richiesta dal cliente
          "quantita_evasa":     int — quantità già consegnata (0 per ordini nuovi)
          "disponibilita":      str — "disponibile" | "parziale" | "indisponibile" | "prodotto_non_trovato"
        }
    """

    def __init__(self, data_manager: DataManager, warehouse: Warehouse, logger: Logger):
        """
        Carica la lista ordini dal DataManager all'avvio.

        Args:
            data_manager: istanza DataManager per la persistenza
            warehouse:    istanza Warehouse per verificare disponibilità e aggiornare giacenze
            logger:       istanza Logger per tracciare le operazioni
        """
        self.dm = data_manager
        self.wh = warehouse
        self.logger = logger
        # Lista ordini in memoria — modificata direttamente dai metodi della classe
        self.ordini: list[dict[str, Any]] = self.dm.carica_ordini()

    def salva(self):
        """Persiste lo stato corrente di self.ordini su disco tramite DataManager."""
        self.dm.salva_ordini(self.ordini)

    def _genera_id(self) -> str:
        """
        Genera il prossimo ID ordine univoco per l'anno corrente.
        Il formato è ORD-YYYY-NNN, dove NNN è un numero sequenziale a 3 cifre.

        Funzionamento:
          1. Filtra gli ordini dell'anno corrente estraendo i numeri progressivi
          2. Prende il massimo e aggiunge 1
          3. Se non esistono ordini per l'anno corrente, parte da 001

        Returns:
            Stringa nel formato "ORD-2026-005"
        """
        anno = datetime.now().year
        # Filtra solo gli ordini dell'anno in corso (per evitare collisioni tra anni)
        esistenti = [o["id_ordine"] for o in self.ordini if str(anno) in o["id_ordine"]]
        if not esistenti:
            return f"ORD-{anno}-001"
        # Estrae la parte numerica finale di ogni ID per trovare il massimo
        numeri = [int(oid.split("-")[-1]) for oid in esistenti]
        return f"ORD-{anno}-{max(numeri) + 1:03d}"   # :03d → padding con zeri a 3 cifre

    def registra_ordine(
        self,
        cliente: str,
        righe: list[dict[str, Any]],
        priorita: str = "normale",
        operatore: str = OPERATORE_DEFAULT
    ) -> dict[str, Any]:
        """
        Registra un nuovo ordine e determina la disponibilità di ciascuna riga
        al momento della registrazione, SENZA scaricare le giacenze.
        Lo scarico avviene solo all'evasione esplicita (evadi_ordine).

        Logica di disponibilità per riga:
          - giacenza >= quantità richiesta  → "disponibile"
          - 0 < giacenza < quantità richiesta → "parziale" (ordine diventa "parziale")
          - giacenza == 0                   → "indisponibile" (ordine diventa "in_attesa")
          - prodotto non nel catalogo       → "prodotto_non_trovato" (ordine diventa "in_attesa")

        Lo stato generale dell'ordine è il peggiore tra quelli delle singole righe:
          disponibile → nuovo, parziale → parziale, indisponibile → in_attesa

        Args:
            cliente:   ragione sociale del cliente
            righe:     lista di {"codice": str, "quantita": int}
            priorita:  uno tra PRIORITA_VALIDE
            operatore: chi ha registrato l'ordine

        Returns:
            Dizionario dell'ordine appena creato, già aggiunto a self.ordini.
        """
        id_ordine = self._genera_id()
        oggi = date.today().strftime("%Y-%m-%d")

        righe_processate = []
        stato_generale = "nuovo"   # pessimismo progressivo: peggiorerà se ci sono problemi

        for riga in righe:
            codice = riga["codice"].upper()
            qtà_richiesta = riga["quantita"]
            prodotto = self.wh.get_prodotto(codice)

            # Caso: prodotto non presente nel catalogo
            if not prodotto:
                righe_processate.append({
                    "codice": codice,
                    "quantita_richiesta": qtà_richiesta,
                    "quantita_evasa": 0,
                    "disponibilita": "prodotto_non_trovato"
                })
                stato_generale = "in_attesa"   # blocca l'ordine finché il prodotto non è disponibile
                continue

            # Determina la disponibilità confrontando giacenza e quantità richiesta
            disponibile = prodotto["giacenza"]
            if disponibile >= qtà_richiesta:
                disponibilita = "disponibile"
            elif disponibile > 0:
                disponibilita = "parziale"
                stato_generale = "parziale"   # almeno una riga è solo parzialmente soddisfacibile
            else:
                disponibilita = "indisponibile"
                stato_generale = "in_attesa"  # prodotto esaurito: ordine bloccato

            righe_processate.append({
                "codice": codice,
                "quantita_richiesta": qtà_richiesta,
                "quantita_evasa": 0,          # zero: nessuna quantità scaricata in fase di registrazione
                "disponibilita": disponibilita
            })

        # Costruisce il dizionario ordine completo
        ordine: dict[str, Any] = {
            "id_ordine": id_ordine,
            "data": oggi,
            "cliente": cliente,
            "priorita": priorita,
            "stato": stato_generale,
            "righe": righe_processate,
            "note": ""
        }
        self.ordini.append(ordine)
        self.logger.log(
            "NUOVO_ORDINE",
            id_ordine,
            f"Cliente: {cliente} | Priorità: {priorita} | Stato: {stato_generale}",
            operatore
        )
        return ordine

    def evadi_ordine(self, id_ordine: str, operatore: str = OPERATORE_DEFAULT) -> tuple[bool, str]:
        """
        Tenta l'evasione (totale o parziale) di un ordine esistente.

        Per ogni riga dell'ordine non ancora evasa:
          1. Calcola la quantità ancora da evadere (richiesta - già evasa)
          2. Verifica la giacenza disponibile nel magazzino
          3. Scarica min(da_evadere, giacenza) — evita giacenze negative
          4. Aggiorna quantita_evasa nella riga e la giacenza in Warehouse
          5. Determina se la riga è stata soddisfatta completamente

        Lo stato finale dell'ordine è "evaso" solo se TUTTE le righe sono complete,
        altrimenti rimane/diventa "parziale".

        Args:
            id_ordine: identificatore dell'ordine da evadere
            operatore: chi ha eseguito l'evasione

        Returns:
            Tupla (successo: bool, messaggio: str).
            successo=False se l'ordine non esiste, è già evaso o è annullato.
        """
        ordine = self.get_ordine(id_ordine)
        if not ordine:
            return False, f"Ordine {id_ordine} non trovato."
        if ordine["stato"] == "evaso":
            return False, f"Ordine {id_ordine} già evaso."
        if ordine["stato"] == "annullato":
            return False, f"Ordine {id_ordine} annullato, non evasibile."

        evaso_tutto = True   # si porta False se anche una sola riga rimane incompleta
        messaggi = []

        for riga in ordine["righe"]:
            codice = riga["codice"]
            # Quantità ancora da spedire per questa riga (supporta evasioni incrementali)
            qtà_da_evadere = riga["quantita_richiesta"] - riga["quantita_evasa"]

            # Riga già completamente evasa in una sessione precedente: salta
            if qtà_da_evadere <= 0:
                continue

            prodotto = self.wh.get_prodotto(codice)
            if not prodotto:
                messaggi.append(f"  {codice}: prodotto non trovato in magazzino")
                evaso_tutto = False
                continue

            disponibile = prodotto["giacenza"]
            # Non si va mai in negativo: si scarica al massimo quello che c'è
            da_scaricare = min(qtà_da_evadere, disponibile)

            if da_scaricare > 0:
                # Scarica le giacenze e aggiorna la riga con le unità effettivamente evase
                self.wh.aggiorna_giacenza(codice, -da_scaricare, operatore)
                riga["quantita_evasa"] += da_scaricare
                # Aggiorna il flag di disponibilità nella riga per rispecchiare il risultato reale
                riga["disponibilita"] = "disponibile" if da_scaricare == qtà_da_evadere else "parziale"

            # Verifica se la riga è ora completamente soddisfatta
            if riga["quantita_evasa"] < riga["quantita_richiesta"]:
                evaso_tutto = False
                rimanente = riga["quantita_richiesta"] - riga["quantita_evasa"]
                messaggi.append(f"  {codice}: evasi {riga['quantita_evasa']}/{riga['quantita_richiesta']} — mancano {rimanente}")
            else:
                messaggi.append(f"  {codice}: evasi {riga['quantita_evasa']}/{riga['quantita_richiesta']} ✓")

        # Stato finale: evaso solo se ogni riga è stata completamente soddisfatta
        ordine["stato"] = "evaso" if evaso_tutto else "parziale"
        self.logger.log(
            "EVASIONE_ORDINE",
            id_ordine,
            f"Stato finale: {ordine['stato']} | Op: {operatore}",
            operatore
        )
        messaggio = f"Ordine {id_ordine} — stato: {ordine['stato'].upper()}\n" + "\n".join(messaggi)
        return True, messaggio

    def annulla_ordine(self, id_ordine: str, operatore: str = OPERATORE_DEFAULT) -> tuple[bool, str]:
        """
        Annulla un ordine che non sia già stato evaso.
        Gli ordini annullati rimangono nello storico ma non possono essere evasi.
        Non viene effettuato alcun ripristino delle giacenze (l'annullamento avviene
        prima dell'evasione, quindi nessuno scarico è stato eseguito).

        Args:
            id_ordine: identificatore dell'ordine da annullare
            operatore: chi ha eseguito l'annullamento

        Returns:
            Tupla (successo: bool, messaggio: str).
        """
        ordine = self.get_ordine(id_ordine)
        if not ordine:
            return False, f"Ordine {id_ordine} non trovato."
        if ordine["stato"] == "evaso":
            return False, "Non è possibile annullare un ordine già evaso."
        ordine["stato"] = "annullato"
        self.logger.log("ANNULLAMENTO_ORDINE", id_ordine, f"Cliente: {ordine['cliente']}", operatore)
        return True, f"Ordine {id_ordine} annullato."

    def get_ordine(self, id_ordine: str) -> Optional[dict[str, Any]]:
        """
        Cerca un ordine per ID esatto (case-sensitive).

        Returns:
            Il dizionario dell'ordine (riferimento diretto) oppure None.
        """
        for o in self.ordini:
            if o["id_ordine"] == id_ordine:
                return o
        return None

    def get_ordini_filtrati(
        self,
        stato: str = "",
        cliente: str = "",
        data_da: str = "",
        data_a: str = ""
    ) -> list[dict[str, Any]]:
        """
        Filtra gli ordini per uno o più criteri combinati con AND logico.
        Le date usano confronto lessicografico su stringhe YYYY-MM-DD, che
        coincide con il confronto cronologico per questo formato ISO.

        Args:
            stato:    filtra per stato esatto (es. "nuovo", "parziale")
            cliente:  filtra per sottostringa nel nome cliente (case-insensitive)
            data_da:  mostra solo ordini dalla data inclusa (formato YYYY-MM-DD)
            data_a:   mostra solo ordini fino alla data inclusa (formato YYYY-MM-DD)

        Returns:
            Lista di ordini che soddisfano tutti i criteri attivi.
        """
        risultati = self.ordini

        if stato:
            risultati = [o for o in risultati if o["stato"] == stato]
        if cliente:
            risultati = [o for o in risultati if cliente.lower() in o["cliente"].lower()]
        if data_da:
            # Confronto lessicografico funziona correttamente con formato YYYY-MM-DD
            risultati = [o for o in risultati if o["data"] >= data_da]
        if data_a:
            risultati = [o for o in risultati if o["data"] <= data_a]

        return risultati

    def ordini_oggi(self) -> list[dict[str, Any]]:
        """
        Restituisce tutti gli ordini con data uguale a oggi.
        Usato principalmente da ReportGenerator per il report giornaliero.

        Returns:
            Lista di ordini registrati nella giornata corrente.
        """
        oggi = date.today().strftime("%Y-%m-%d")
        return [o for o in self.ordini if o["data"] == oggi]


# =============================================================================
# REPORT GENERATOR
# =============================================================================

class ReportGenerator:
    """
    Genera report giornalieri riepilogando ordini, giacenze e alert di riordino.

    Produce due file per ogni report:
      - TXT: testo formattato per la lettura immediata da terminale o editor
      - CSV: dati strutturati (sezione, campo, valore) per analisi in Excel o script

    Entrambi i file vengono salvati in REPORTS_DIR con il nome report_YYYY-MM-DD.
    """

    def __init__(self, warehouse: Warehouse, order_manager: OrderManager, logger: Logger):
        """
        Args:
            warehouse:     istanza Warehouse per accedere alle giacenze
            order_manager: istanza OrderManager per accedere agli ordini
            logger:        istanza Logger per tracciare la generazione del report
        """
        self.wh = warehouse
        self.om = order_manager
        self.logger = logger

    def genera_report_giornaliero(self, data_report: str = "") -> tuple[str, str]:
        """
        Genera il report per la data specificata (default: oggi).

        Contenuto del report:
          1. Riepilogo ordini: ricevuti, evasi, parziali, in sospeso, annullati
          2. Top 5 prodotti per quantità evasa nella giornata
          3. Tabella completa delle giacenze con indicatori di stato
          4. Alert prodotti sotto il punto di riordino
          5. Lista ordini ancora in sospeso con priorità

        Args:
            data_report: data nel formato YYYY-MM-DD (stringa vuota = oggi)

        Returns:
            Tupla (testo_report: str, percorso_csv: str).
        """
        # Se non specificata, usa la data odierna
        if not data_report:
            data_report = date.today().strftime("%Y-%m-%d")

        # Partiziona gli ordini del giorno per stato — usati sia nel testo che nel CSV
        ordini_giorno = [o for o in self.om.ordini if o["data"] == data_report]
        ordini_evasi = [o for o in ordini_giorno if o["stato"] == "evaso"]
        ordini_parziali = [o for o in ordini_giorno if o["stato"] == "parziale"]
        ordini_sospeso = [o for o in ordini_giorno if o["stato"] in ("nuovo", "in_attesa")]
        ordini_annullati = [o for o in ordini_giorno if o["stato"] == "annullato"]

        # Calcola le vendite del giorno aggregando quantita_evasa per codice prodotto.
        # Usa un dizionario accumulatore per sommare le quantità su più ordini.
        vendite: dict[str, int] = {}
        for ordine in ordini_giorno:
            for riga in ordine["righe"]:
                codice = riga["codice"]
                vendite[codice] = vendite.get(codice, 0) + riga.get("quantita_evasa", 0)
        # Ordina per quantità decrescente e prende i primi 5
        top_prodotti = sorted(vendite.items(), key=lambda x: x[1], reverse=True)[:5]

        # Prodotti sotto soglia: calcolati una volta sola e riusati in testo e CSV
        prodotti_riordino = self.wh.prodotti_sotto_riordino()

        # -----------------------------------------------------------------
        # Costruzione del testo leggibile (formato TXT)
        # -----------------------------------------------------------------
        sep = "=" * 60    # separatore principale tra sezioni
        linea = "-" * 60  # separatore secondario (intestazioni di tabella)

        righe_testo = [
            sep,
            f"  REPORT GIORNALIERO — LogiServe S.r.l.",
            f"  Data: {data_report}",
            f"  Generato il: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            sep,
            "",
            "RIEPILOGO ORDINI",
            linea,
            f"  Ordini ricevuti oggi  : {len(ordini_giorno)}",
            f"  Ordini evasi          : {len(ordini_evasi)}",
            f"  Ordini parziali       : {len(ordini_parziali)}",
            f"  Ordini in sospeso     : {len(ordini_sospeso)}",
            f"  Ordini annullati      : {len(ordini_annullati)}",
            "",
        ]

        # Sezione top venduti: mostrata solo se ci sono state vendite nella giornata
        if top_prodotti:
            righe_testo += ["PRODOTTI PIÙ VENDUTI (OGGI)", linea]
            for codice, qty in top_prodotti:
                prodotto = self.wh.get_prodotto(codice)
                nome = prodotto["nome"] if prodotto else codice   # fallback al codice se prodotto rimosso
                righe_testo.append(f"  {codice} — {nome}: {qty} unità")
            righe_testo.append("")

        # Tabella giacenze: ordinata per codice, con indicatore visivo di stato
        righe_testo += [
            "STATO GIACENZE",
            linea,
            f"  {'Codice':<8} {'Nome':<35} {'Giacenza':>9} {'Riordino':>9} {'UM':<6} {'Stato':<12}",
            f"  {'-'*8} {'-'*35} {'-'*9} {'-'*9} {'-'*6} {'-'*12}",
        ]
        for p in sorted(self.wh.prodotti, key=lambda x: x["codice"]):
            # Determina l'indicatore di stato: ESAURITO ha priorità su RIORDINO
            stato_g = "⚠ RIORDINO" if p["giacenza"] <= p["punto_riordino"] else "OK"
            if p["giacenza"] == 0:
                stato_g = "✗ ESAURITO"
            righe_testo.append(
                f"  {p['codice']:<8} {p['nome'][:35]:<35} {p['giacenza']:>9} "
                f"{p['punto_riordino']:>9} {p['unita_misura']:<6} {stato_g:<12}"
            )
        righe_testo.append("")

        # Sezione alert: mostrata solo se almeno un prodotto è sotto soglia
        if prodotti_riordino:
            righe_testo += ["ALERT: PRODOTTI DA RIORDINARE", linea]
            for p in prodotti_riordino:
                righe_testo.append(
                    f"  {p['codice']} — {p['nome']}: giacenza {p['giacenza']} (soglia: {p['punto_riordino']})"
                )
            righe_testo.append("")

        # Sezione ordini in sospeso: visibilità immediata su cosa è ancora da evadere
        if ordini_sospeso:
            righe_testo += ["ORDINI IN SOSPESO", linea]
            for o in ordini_sospeso:
                righe_testo.append(f"  {o['id_ordine']} | {o['cliente']} | Priorità: {o['priorita']}")
            righe_testo.append("")

        righe_testo.append(sep)
        testo = "\n".join(righe_testo)

        # -----------------------------------------------------------------
        # Salvataggio TXT
        # -----------------------------------------------------------------
        txt_path = REPORTS_DIR / f"report_{data_report}.txt"
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(testo)

        # -----------------------------------------------------------------
        # Salvataggio CSV — formato a tre colonne (Sezione, Campo, Valore)
        # per facilitare l'importazione in fogli di calcolo o script di analisi
        # -----------------------------------------------------------------
        csv_path = REPORTS_DIR / f"report_{data_report}.csv"
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Sezione", "Campo", "Valore"])   # intestazione

            # Riepilogo ordini
            writer.writerow(["Riepilogo", "Data report", data_report])
            writer.writerow(["Riepilogo", "Ordini ricevuti", len(ordini_giorno)])
            writer.writerow(["Riepilogo", "Ordini evasi", len(ordini_evasi)])
            writer.writerow(["Riepilogo", "Ordini parziali", len(ordini_parziali)])
            writer.writerow(["Riepilogo", "Ordini in sospeso", len(ordini_sospeso)])
            writer.writerow(["Riepilogo", "Ordini annullati", len(ordini_annullati)])

            # Top venduti (codice prodotto → quantità evasa)
            for codice, qty in top_prodotti:
                writer.writerow(["Top venduto", codice, qty])

            # Giacenze correnti di tutti i prodotti
            for p in self.wh.prodotti:
                writer.writerow(["Giacenza", p["codice"], p["giacenza"]])

            # Prodotti che necessitano riordino
            for p in prodotti_riordino:
                writer.writerow(["Alert riordino", p["codice"], p["giacenza"]])

        self.logger.log("REPORT", f"report_{data_report}", f"Salvato in {txt_path} e {csv_path}")
        return testo, str(csv_path)


# =============================================================================
# INTERFACCIA TESTUALE (CLI)
# =============================================================================

class CLI:
    """
    Interfaccia utente a riga di comando per il sistema LogiServe.

    Struttura del menu principale:
      1. Gestione Ordini     → registra, evadi, annulla, visualizza ordini
      2. Gestione Magazzino  → visualizza, filtra, aggiorna giacenze, aggiungi prodotti
      3. Report e Log        → genera report giornalieri, visualizza log operazioni
      4. Impostazioni        → cambia nome operatore corrente
      0. Esci e salva        → salva su disco e termina

    Convenzioni interne:
      - Tutti i metodi di menu iniziano con _menu_
      - Tutti i metodi di azione iniziano con _ (underscore)
      - _input e _input_int gestiscono centralmente la lettura da stdin
      - Tutti i menu sono loop while True / break per mantenere il flusso semplice
    """

    def __init__(self):
        """
        Inizializza tutte le componenti del sistema in ordine di dipendenza:
          Logger → DataManager → Warehouse → OrderManager → ReportGenerator

        Il Logger viene creato per primo perché le componenti successive
        lo usano internamente per tracciare le proprie operazioni di avvio.
        """
        logger = Logger(LOG_FILE)
        dm = DataManager(logger)
        self.wh = Warehouse(dm, logger)
        self.om = OrderManager(dm, self.wh, logger)
        self.rg = ReportGenerator(self.wh, self.om, logger)
        self.logger = logger
        self.operatore = "operatore"   # nome predefinito, modificabile dalle impostazioni

    # -------------------------------------------------------------------------
    # Utilità di I/O
    # -------------------------------------------------------------------------

    @staticmethod
    def _stampa_intestazione(titolo: str):
        """Stampa un'intestazione visivamente separata per ogni schermata di menu."""
        print(f"\n{'=' * 60}")
        print(f"  {titolo}")
        print(f"{'=' * 60}")

    @staticmethod
    def _input(prompt: str) -> str:
        """
        Legge una stringa da stdin, gestendo EOF e interruzione da tastiera.
        Restituisce stringa vuota in caso di interruzione, così i chiamanti
        possono trattare "" come "operazione annullata dall'utente".

        Args:
            prompt: testo mostrato prima del cursore di input

        Returns:
            Stringa inserita dall'utente (senza spazi iniziali/finali) oppure "".
        """
        try:
            return input(prompt).strip()
        except (EOFError, KeyboardInterrupt):
            print("\nOperazione annullata.")
            return ""

    @staticmethod
    def _input_int(prompt: str, minimo: int = 1) -> Optional[int]:
        """
        Legge un intero da stdin con validazione e ciclo di ripetizione.
        Se l'utente preme invio senza digitare nulla, restituisce None
        (segnala al chiamante che l'operazione è stata saltata).

        Args:
            prompt: testo mostrato prima del cursore
            minimo: valore minimo accettato (default 1 per le quantità)

        Returns:
            Intero valido ≥ minimo, oppure None se input vuoto.
        """
        while True:
            val = CLI._input(prompt)
            if val == "":
                return None   # input vuoto = annullamento implicito
            try:
                n = int(val)
                if n < minimo:
                    print(f"  Inserire un valore ≥ {minimo}.")
                    continue
                return n
            except ValueError:
                print("  Valore non valido. Inserire un numero intero.")

    @staticmethod
    def _conferma(domanda: str) -> bool:
        """
        Chiede una conferma sì/no all'utente.
        Il default è NO (il maiuscolo nella stringa "[s/N]" indica il default).
        Accetta "s", "si", "sì", "y", "yes" come conferma positiva.

        Args:
            domanda: testo della domanda di conferma

        Returns:
            True se l'utente ha confermato, False altrimenti.
        """
        risposta = CLI._input(f"{domanda} [s/N]: ").lower()
        return risposta in ("s", "si", "sì", "y", "yes")

    # -------------------------------------------------------------------------
    # Menu principale
    # -------------------------------------------------------------------------

    def avvia(self):
        """
        Punto di ingresso dell'interfaccia utente.
        Mostra gli alert di riordino all'avvio (se presenti) e poi
        presenta il menu principale in un loop fino all'uscita esplicita.
        """
        print("\n  Benvenuto in LogiServe — Sistema di Monitoraggio Ordini e Magazzino")
        print(f"  Operatore: {self.operatore}")
        # Alert immediato all'avvio: l'operatore vede subito cosa necessita riordino
        self._avvisa_riordino_iniziale()
        while True:
            self._stampa_intestazione("MENU PRINCIPALE")
            print("  1. Gestione Ordini")
            print("  2. Gestione Magazzino")
            print("  3. Report e Log")
            print("  4. Impostazioni")
            print("  0. Esci e salva")
            scelta = self._input("\nScelta: ")
            if scelta == "1":
                self._menu_ordini()
            elif scelta == "2":
                self._menu_magazzino()
            elif scelta == "3":
                self._menu_report()
            elif scelta == "4":
                self._menu_impostazioni()
            elif scelta == "0":
                self._esci()
                break
            else:
                print("  Scelta non valida.")

    def _avvisa_riordino_iniziale(self):
        """
        Mostra all'avvio l'elenco dei prodotti sotto il punto di riordino.
        Fornisce visibilità immediata sullo stato critico del magazzino
        prima che l'operatore inizi a lavorare sugli ordini.
        """
        sotto = self.wh.prodotti_sotto_riordino()
        if sotto:
            print(f"\n  ⚠  ATTENZIONE: {len(sotto)} prodotto/i sotto il punto di riordino:")
            for p in sotto:
                print(f"     {p['codice']} — {p['nome']}: giacenza {p['giacenza']} (soglia {p['punto_riordino']})")

    # -------------------------------------------------------------------------
    # Menu Ordini
    # -------------------------------------------------------------------------

    def _menu_ordini(self):
        """Sottomenu per tutte le operazioni sugli ordini. Loop fino a scelta 0."""
        while True:
            self._stampa_intestazione("GESTIONE ORDINI")
            print("  1. Registra nuovo ordine")
            print("  2. Evadi ordine")
            print("  3. Annulla ordine")
            print("  4. Visualizza ordini")
            print("  5. Dettaglio ordine")
            print("  0. Torna al menu principale")
            scelta = self._input("\nScelta: ")
            if scelta == "1":
                self._registra_ordine()
            elif scelta == "2":
                self._evadi_ordine()
            elif scelta == "3":
                self._annulla_ordine()
            elif scelta == "4":
                self._visualizza_ordini()
            elif scelta == "5":
                self._dettaglio_ordine()
            elif scelta == "0":
                break
            else:
                print("  Scelta non valida.")

    def _registra_ordine(self):
        """
        Guida l'utente nella creazione di un nuovo ordine.

        Flusso:
          1. Nome cliente (obbligatorio)
          2. Priorità (con default "normale" se non specificata o non valida)
          3. Loop di inserimento prodotti: codice + quantità, finché codice vuoto
             - Se il codice non è in catalogo, chiede conferma prima di aggiungerlo
             - Mostra la giacenza corrente per aiutare l'operatore
          4. Verifica che ci sia almeno una riga prima di procedere
          5. Delega la registrazione a OrderManager e mostra il risultato

        La registrazione non scarica le giacenze: avviene solo all'evasione.
        """
        self._stampa_intestazione("REGISTRA NUOVO ORDINE")
        cliente = self._input("Cliente: ")
        if not cliente:
            print("  Cliente obbligatorio.")
            return

        print(f"  Priorità disponibili: {', '.join(PRIORITA_VALIDE)}")
        priorita = self._input("Priorità [normale]: ").lower() or "normale"
        # Fallback silenzioso su "normale" se l'utente inserisce un valore non valido
        if priorita not in PRIORITA_VALIDE:
            print(f"  Priorità non valida. Usato 'normale'.")
            priorita = "normale"

        righe: list[dict[str, Any]] = []
        print("\n  Inserire i prodotti (invio su codice vuoto per terminare):")
        while True:
            codice = self._input("  Codice prodotto: ").upper()
            if not codice:
                break   # uscita dal loop di inserimento prodotti

            prodotto = self.wh.get_prodotto(codice)
            if not prodotto:
                # Prodotto non in catalogo: avvisa l'utente e chiede conferma
                print(f"  ⚠  Prodotto {codice} non trovato nel catalogo.")
                if not self._conferma("  Aggiungere comunque all'ordine?"):
                    continue   # l'utente non conferma: richiede un nuovo codice
            else:
                # Mostra nome e giacenza per aiutare l'operatore a valutare la quantità
                print(f"  → {prodotto['nome']} | Giacenza: {prodotto['giacenza']} {prodotto['unita_misura']}")

            qtà = self._input_int("  Quantità: ", minimo=1)
            if qtà is None:
                continue   # invio vuoto: salta questo prodotto e richiede il prossimo
            righe.append({"codice": codice, "quantita": qtà})

        if not righe:
            print("  Nessun prodotto inserito. Ordine annullato.")
            return

        ordine = self.om.registra_ordine(cliente, righe, priorita, self.operatore)
        print(f"\n  Ordine registrato: {ordine['id_ordine']}")
        print(f"  Stato: {ordine['stato'].upper()}")
        # Mostra la disponibilità rilevata al momento della registrazione per ogni riga
        for r in ordine["righe"]:
            disp = r.get("disponibilita", "?")
            print(f"  {r['codice']}: richiesti {r['quantita_richiesta']} — {disp}")

        self.om.salva()   # persiste immediatamente dopo la registrazione

    def _evadi_ordine(self):
        """
        Guida l'utente nell'evasione di un ordine esistente.

        Mostra prima la lista degli ordini non ancora evasi per facilitare la scelta.
        Richiede conferma prima di procedere (operazione irreversibile sulle giacenze).
        Dopo l'evasione, mostra eventuali nuovi alert di riordino.
        """
        self._stampa_intestazione("EVADI ORDINE")
        # Mostra solo gli ordini che possono essere evasi (esclude evasi e annullati)
        self._mostra_lista_ordini_breve(filtro_stato=["nuovo", "parziale", "in_attesa"])
        id_ordine = self._input("\nID ordine da evadere: ").upper()
        if not id_ordine:
            return
        if not self._conferma(f"Confermare evasione di {id_ordine}?"):
            return
        ok, msg = self.om.evadi_ordine(id_ordine, self.operatore)
        print(f"\n{msg}")
        if ok:
            # Salva sia gli ordini (stato aggiornato) sia i prodotti (giacenze ridotte)
            self.om.salva()
            self.wh.salva()
            self._avvisa_riordino_post_evasione()   # alert se l'evasione ha abbassato qualche soglia

    def _annulla_ordine(self):
        """
        Guida l'utente nell'annullamento di un ordine.

        Mostra solo gli ordini annullabili. Richiede doppia conferma per
        evitare annullamenti accidentali. Non modifica le giacenze.
        """
        self._stampa_intestazione("ANNULLA ORDINE")
        self._mostra_lista_ordini_breve(filtro_stato=["nuovo", "parziale", "in_attesa"])
        id_ordine = self._input("\nID ordine da annullare: ").upper()
        if not id_ordine:
            return
        if not self._conferma(f"Sicuro di voler annullare {id_ordine}?"):
            return
        ok, msg = self.om.annulla_ordine(id_ordine, self.operatore)
        print(f"\n  {msg}")
        if ok:
            self.om.salva()

    def _visualizza_ordini(self):
        """
        Mostra la lista degli ordini filtrata per criteri scelti dall'utente.
        Tutti i filtri sono opzionali: premere invio li disabilita.
        La tabella mostra i campi principali (ID, data, cliente, priorità, stato).
        """
        self._stampa_intestazione("VISUALIZZA ORDINI")
        print("  Filtri (invio per nessun filtro):")
        stato = self._input(f"  Stato ({'/'.join(STATI_ORDINE)}): ").lower()
        cliente = self._input("  Cliente (parte del nome): ")
        data_da = self._input("  Data da (AAAA-MM-GG): ")
        data_a = self._input("  Data a  (AAAA-MM-GG): ")

        ordini = self.om.get_ordini_filtrati(stato, cliente, data_da, data_a)
        if not ordini:
            print("  Nessun ordine trovato.")
            return

        # Tabella con larghezze fisse per allineamento in console a larghezza standard
        print(f"\n  {'ID Ordine':<18} {'Data':<12} {'Cliente':<28} {'Priorità':<10} {'Stato':<12}")
        print(f"  {'-'*18} {'-'*12} {'-'*28} {'-'*10} {'-'*12}")
        for o in ordini:
            print(
                f"  {o['id_ordine']:<18} {o['data']:<12} {o['cliente'][:28]:<28} "
                f"{o['priorita']:<10} {o['stato']:<12}"
            )
        print(f"\n  Totale: {len(ordini)} ordini")

    def _dettaglio_ordine(self):
        """
        Mostra il dettaglio completo di un singolo ordine, incluse tutte le righe
        con quantità richieste, quantità evase e stato di disponibilità per riga.
        """
        self._stampa_intestazione("DETTAGLIO ORDINE")
        id_ordine = self._input("ID ordine: ").upper()
        if not id_ordine:
            return
        ordine = self.om.get_ordine(id_ordine)
        if not ordine:
            print(f"  Ordine {id_ordine} non trovato.")
            return

        # Intestazione ordine
        print(f"\n  ID Ordine : {ordine['id_ordine']}")
        print(f"  Data      : {ordine['data']}")
        print(f"  Cliente   : {ordine['cliente']}")
        print(f"  Priorità  : {ordine['priorita']}")
        print(f"  Stato     : {ordine['stato'].upper()}")
        if ordine["note"]:
            print(f"  Note      : {ordine['note']}")

        # Tabella righe: mostra anche il nome del prodotto se ancora in catalogo
        print(f"\n  {'Codice':<8} {'Richiesti':>10} {'Evasi':>8} {'Disponibilità':<18}")
        print(f"  {'-'*8} {'-'*10} {'-'*8} {'-'*18}")
        for r in ordine["righe"]:
            prodotto = self.wh.get_prodotto(r["codice"])
            # Il prodotto potrebbe non essere più in catalogo: fallback a stringa vuota
            nome = f"({prodotto['nome'][:20]})" if prodotto else ""
            print(
                f"  {r['codice']:<8} {r['quantita_richiesta']:>10} {r['quantita_evasa']:>8} "
                f"{r.get('disponibilita','?'):<18} {nome}"
            )

    def _mostra_lista_ordini_breve(self, filtro_stato: Optional[list[str]] = None):
        """
        Stampa un riepilogo compatto degli ordini, opzionalmente filtrato per stato.
        Mostra solo gli ultimi 15 ordini per non sovraffollare il terminale.
        Usata come aiuto contestuale prima di chiedere all'utente un ID ordine.

        Args:
            filtro_stato: lista di stati da includere (None = tutti gli ordini)
        """
        ordini = self.om.ordini
        if filtro_stato:
            ordini = [o for o in ordini if o["stato"] in filtro_stato]
        if not ordini:
            print("  Nessun ordine disponibile.")
            return
        print(f"\n  {'ID Ordine':<18} {'Cliente':<28} {'Stato':<12} {'Priorità'}")
        print(f"  {'-'*18} {'-'*28} {'-'*12} {'-'*10}")
        # Mostra gli ultimi 15 ordini ([-15:]) per limitare lo scroll in console
        for o in ordini[-15:]:
            print(f"  {o['id_ordine']:<18} {o['cliente'][:28]:<28} {o['stato']:<12} {o['priorita']}")

    # -------------------------------------------------------------------------
    # Menu Magazzino
    # -------------------------------------------------------------------------

    def _menu_magazzino(self):
        """Sottomenu per tutte le operazioni sul magazzino. Loop fino a scelta 0."""
        while True:
            self._stampa_intestazione("GESTIONE MAGAZZINO")
            print("  1. Visualizza prodotti")
            print("  2. Prodotti sotto punto di riordino")
            print("  3. Aggiorna giacenza manualmente")
            print("  4. Aggiungi nuovo prodotto")
            print("  0. Torna al menu principale")
            scelta = self._input("\nScelta: ")
            if scelta == "1":
                self._visualizza_prodotti()
            elif scelta == "2":
                self._prodotti_riordino()
            elif scelta == "3":
                self._aggiorna_giacenza_manuale()
            elif scelta == "4":
                self._aggiungi_prodotto()
            elif scelta == "0":
                break
            else:
                print("  Scelta non valida.")

    def _visualizza_prodotti(self):
        """
        Mostra il catalogo prodotti con filtri opzionali per codice, categoria e
        soglia di riordino. Ogni riga include un indicatore di stato (OK/RIORDINO/ESAURITO)
        per consentire una lettura rapida della situazione del magazzino.
        """
        self._stampa_intestazione("STATO MAGAZZINO")
        print("  Filtri (invio per nessun filtro):")
        codice = self._input("  Codice: ")
        # Mostra le categorie disponibili per aiutare l'utente a scegliere
        print(f"  Categorie: {', '.join(self.wh.categorie())}")
        categoria = self._input("  Categoria: ")
        sotto_riordino_str = self._input("  Solo sotto riordino? [s/N]: ").lower()
        sotto_riordino = sotto_riordino_str in ("s", "si", "sì", "y")

        prodotti = self.wh.get_prodotti_filtrati(codice, categoria, sotto_riordino)
        if not prodotti:
            print("  Nessun prodotto trovato.")
            return

        # Tabella con prezzi e indicatore di stato; ordinata per codice
        print(
            f"\n  {'Cod':<8} {'Nome':<35} {'Giacenza':>9} {'Riordino':>9} "
            f"{'UM':<6} {'Prezzo':>8} {'Stato'}"
        )
        print(f"  {'-'*8} {'-'*35} {'-'*9} {'-'*9} {'-'*6} {'-'*8} {'-'*10}")
        for p in sorted(prodotti, key=lambda x: x["codice"]):
            # Priorità: ESAURITO supera RIORDINO come gravità
            if p["giacenza"] == 0:
                stato = "ESAURITO"
            elif p["giacenza"] <= p["punto_riordino"]:
                stato = "RIORDINO"
            else:
                stato = "OK"
            print(
                f"  {p['codice']:<8} {p['nome'][:35]:<35} {p['giacenza']:>9} "
                f"{p['punto_riordino']:>9} {p['unita_misura']:<6} "
                f"{p['prezzo_unitario']:>7.2f}€ {stato}"
            )
        print(f"\n  Totale prodotti: {len(prodotti)}")

    def _prodotti_riordino(self):
        """
        Mostra esclusivamente i prodotti che hanno raggiunto o superato il punto
        di riordino. Utile per il responsabile acquisti per pianificare i rifornimenti.
        """
        self._stampa_intestazione("PRODOTTI SOTTO PUNTO DI RIORDINO")
        prodotti = self.wh.prodotti_sotto_riordino()
        if not prodotti:
            print("  Tutti i prodotti sono sopra il punto di riordino.")
            return
        for p in prodotti:
            print(f"  {p['codice']:<8} {p['nome']:<40} Giacenza: {p['giacenza']:>6} / Riordino: {p['punto_riordino']}")

    def _aggiorna_giacenza_manuale(self):
        """
        Permette all'operatore di registrare manualmente un carico o uno scarico.
        La variazione accetta sia valori positivi (carico da fornitore) sia negativi
        (scarico per danni, inventario, rettifiche).

        Mostra un avviso e chiede conferma se la variazione porterebbe la giacenza
        sotto zero (situazione anomala che richiede attenzione consapevole).
        """
        self._stampa_intestazione("AGGIORNAMENTO GIACENZA MANUALE")
        codice = self._input("Codice prodotto: ").upper()
        if not codice:
            return
        prodotto = self.wh.get_prodotto(codice)
        if not prodotto:
            print(f"  Prodotto {codice} non trovato.")
            return

        # Mostra la giacenza attuale come riferimento prima di chiedere la variazione
        print(f"  {prodotto['nome']} — Giacenza attuale: {prodotto['giacenza']} {prodotto['unita_misura']}")
        print("  Inserire variazione (es. +50 per carico, -10 per scarico):")
        delta_str = self._input("  Variazione: ")
        if not delta_str:
            return
        try:
            delta = int(delta_str)
        except ValueError:
            print("  Valore non valido.")
            return

        # Calcola la giacenza risultante per mostrare un avviso se diventa negativa
        nuova = prodotto["giacenza"] + delta
        if nuova < 0:
            print(f"  Attenzione: la giacenza diventerebbe negativa ({nuova}).")
            if not self._conferma("Continuare?"):
                return

        self.wh.aggiorna_giacenza(codice, delta, self.operatore)
        self.wh.salva()
        # Mostra il valore già aggiornato (aggiorna_giacenza modifica il dizionario in-place)
        print(f"  Giacenza aggiornata: {prodotto['giacenza']} {prodotto['unita_misura']}")

    def _aggiungi_prodotto(self):
        """
        Guida l'utente nell'inserimento di un nuovo prodotto nel catalogo.

        Verifica che il codice non esista già prima di procedere.
        Mostra le categorie esistenti per incoraggiare coerenza nella categorizzazione.
        Il prezzo accetta sia il punto che la virgola come separatore decimale.
        """
        self._stampa_intestazione("AGGIUNGI NUOVO PRODOTTO")
        codice = self._input("Codice (es. P009): ").upper()
        if not codice:
            return
        # Impedisce l'inserimento di duplicati prima di raccogliere gli altri dati
        if self.wh.get_prodotto(codice):
            print(f"  Prodotto {codice} già esistente.")
            return

        nome = self._input("Nome prodotto: ")
        if not nome:
            return

        # Suggerisce le categorie esistenti per uniformità del catalogo
        print(f"  Categorie esistenti: {', '.join(self.wh.categorie())}")
        categoria = self._input("Categoria: ")
        giacenza = self._input_int("Giacenza iniziale: ", minimo=0) or 0
        punto_riordino = self._input_int("Punto di riordino: ", minimo=0) or 0
        unita = self._input("Unità di misura (es. pz, mt, kg): ") or "pz"

        # Gestione del prezzo: accetta sia "18.50" sia "18,50" come separatore decimale
        prezzo_str = self._input("Prezzo unitario (€): ")
        try:
            prezzo = float(prezzo_str.replace(",", "."))
        except (ValueError, AttributeError):
            prezzo = 0.0   # default 0 se il formato non è riconoscibile

        prodotto: dict[str, Any] = {
            "codice": codice,
            "nome": nome,
            "categoria": categoria,
            "giacenza": giacenza,
            "punto_riordino": punto_riordino,
            "unita_misura": unita,
            "prezzo_unitario": prezzo
        }
        self.wh.aggiungi_prodotto(prodotto, self.operatore)
        self.wh.salva()
        print(f"  Prodotto {codice} aggiunto al catalogo.")

    def _avvisa_riordino_post_evasione(self):
        """
        Mostra i prodotti scesi sotto il punto di riordino dopo l'evasione appena
        eseguita. Chiamata subito dopo ogni evasione andata a buon fine per dare
        visibilità immediata sulla necessità di riapprovvigionamento.
        """
        sotto = self.wh.prodotti_sotto_riordino()
        if sotto:
            print(f"\n  ⚠  Prodotti scesi sotto il punto di riordino dopo l'evasione:")
            for p in sotto:
                print(f"     {p['codice']} — {p['nome']}: giacenza {p['giacenza']} (soglia {p['punto_riordino']})")

    # -------------------------------------------------------------------------
    # Menu Report e Log
    # -------------------------------------------------------------------------

    def _menu_report(self):
        """Sottomenu per generazione report e consultazione del log. Loop fino a scelta 0."""
        while True:
            self._stampa_intestazione("REPORT E LOG")
            print("  1. Genera report giornaliero (oggi)")
            print("  2. Genera report per data specifica")
            print("  3. Visualizza log operazioni (oggi)")
            print("  0. Torna al menu principale")
            scelta = self._input("\nScelta: ")
            if scelta == "1":
                self._genera_report()
            elif scelta == "2":
                data = self._input("Data (AAAA-MM-GG): ")
                if data:
                    self._genera_report(data)
            elif scelta == "3":
                self._visualizza_log()
            elif scelta == "0":
                break
            else:
                print("  Scelta non valida.")

    def _genera_report(self, data: str = ""):
        """
        Invoca ReportGenerator e stampa il testo del report a schermo,
        comunicando all'utente i percorsi dei file salvati.

        Args:
            data: data del report in formato YYYY-MM-DD (stringa vuota = oggi)
        """
        print("\n  Generazione report in corso...")
        testo, csv_path = self.rg.genera_report_giornaliero(data)
        print(testo)
        print(f"\n  Report salvato in: {csv_path}")
        print(f"  Report TXT in: {csv_path.replace('.csv', '.txt')}")

    def _visualizza_log(self):
        """
        Mostra a schermo le voci del log di oggi in formato tabellare.
        Utile per un rapido controllo delle operazioni eseguite nella sessione corrente.
        Il dettaglio viene troncato a 40 caratteri per mantenere l'allineamento della tabella.
        """
        self._stampa_intestazione("LOG OPERAZIONI — OGGI")
        entries = self.logger.get_log_oggi()
        if not entries:
            print("  Nessuna operazione registrata oggi.")
            return
        print(f"\n  {'Timestamp':<20} {'Operazione':<25} {'Risorsa':<15} {'Dettaglio'}")
        print(f"  {'-'*20} {'-'*25} {'-'*15} {'-'*30}")
        for e in entries:
            print(
                f"  {e['timestamp']:<20} {e['operazione']:<25} "
                f"{e['risorsa']:<15} {e['dettaglio'][:40]}"
            )

    # -------------------------------------------------------------------------
    # Menu Impostazioni
    # -------------------------------------------------------------------------

    def _menu_impostazioni(self):
        """
        Permette di cambiare il nome dell'operatore per la sessione corrente.
        Il nome dell'operatore viene registrato nel log di tutte le operazioni
        successive, permettendo la tracciabilità per utente.
        """
        self._stampa_intestazione("IMPOSTAZIONI")
        print(f"  Operatore attuale: {self.operatore}")
        nuovo = self._input("Nuovo nome operatore (invio per non cambiare): ")
        if nuovo:
            self.operatore = nuovo
            print(f"  Operatore impostato: {self.operatore}")

    # -------------------------------------------------------------------------
    # Uscita
    # -------------------------------------------------------------------------

    def _esci(self):
        """
        Salva lo stato completo su disco prima di terminare.
        Il salvataggio avviene anche durante le operazioni (dopo ogni modifica),
        ma questo salvataggio finale garantisce la coerenza dei dati anche in
        caso di operazioni non ancora persistite nella sessione.
        """
        print("\n  Salvataggio dati in corso...")
        self.wh.salva()   # persiste le giacenze aggiornate
        self.om.salva()   # persiste gli ordini aggiornati
        print("  Dati salvati correttamente.")
        print("  Arrivederci!\n")


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    # Intercetta Ctrl+C a livello globale come ultima risorsa, nel caso in cui
    # l'interruzione avvenga fuori da un metodo _input (che lo gestisce localmente)
    try:
        cli = CLI()
        cli.avvia()
    except KeyboardInterrupt:
        print("\n\n  Interruzione da tastiera. Arrivederci!")
        sys.exit(0)
