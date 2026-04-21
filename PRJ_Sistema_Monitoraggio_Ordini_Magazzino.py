"""
================================================================================
PROGETTO: Sistema di monitoraggio ordini e magazzino — LogiServe S.r.l.
================================================================================

Simone La Porta - 2026-04-21

TESTO DEL PROBLEMA
------------------
LogiServe S.r.l. è una piccola azienda B2B che distribuisce componenti elettrici
a officine e rivenditori. Il gestionale attuale è un foglio Excel condiviso che
crea problemi di sincronizzazione e nessuna traccia delle operazioni.
Si chiede di realizzare un'applicazione a riga di comando in Python che permetta di:
  - registrare nuovi ordini verificando la disponibilità dei prodotti
  - evadere gli ordini aggiornando automaticamente le giacenze
  - visualizzare lo stato del magazzino con filtri
  - generare un report giornaliero (TXT + CSV)
  - mantenere un log di tutte le operazioni con timestamp
  - salvare i dati su file in modo che sopravvivano al riavvio del programma

ANALISI PRELIMINARE
-------------------
Il primo passo è stato capire quali dati gestire e come collegarli tra loro.
Servono due entità principali: i Prodotti (con codice, nome, giacenza, ecc.)
e gli Ordini (con cliente, priorità, righe prodotto, stato).
Un ordine può essere in vari stati: nuovo, evaso, parziale, in_attesa, annullato.
Il passaggio di stato dipende dalla disponibilità in magazzino al momento dell'evasione.
Ho scelto di separare la fase di registrazione (che non tocca le giacenze) da quella
di evasione (che le scarica), in modo da poter registrare ordini anche se il magazzino
non ha ancora tutto il necessario.
Ho anche identificato il bisogno di un sistema di log separato dai dati principali,
così da poter ricostruire la cronologia delle operazioni indipendentemente dagli ordini.

SCELTE TECNICHE E ALGORITMICHE
-------------------------------
- Struttura a classi: ho diviso il codice in 6 classi con responsabilità separate
  (Logger, DataManager, Warehouse, OrderManager, ReportGenerator, CLI) perché così
  è più facile identificare bug e modificare una parte senza influenzare le altre.
- JSON per la persistenza: è leggibile anche con un editor di testo, facile da
  caricare in Python con json.load(), e funziona bene con liste di dizionari.
- CSV per il log: ogni riga è un evento, è semplice da aprire in Excel e si possono
  aggiungere dati in fondo senza rileggere tutto (modalità append).
- Dizionari Python per i dati in memoria: ho usato list[dict] per prodotti e ordini,
  così ogni campo ha un nome descrittivo invece di un indice numerico.
- Per l'evasione ho usato min(quantita_da_evadere, giacenza_disponibile) per evitare
  di portare la giacenza sotto zero in caso di scorta insufficiente.
- Lo stato dell'ordine viene determinato "al peggio": se anche una sola riga è parziale,
  tutto l'ordine diventa parziale; se una riga è indisponibile, diventa in_attesa.

CONCLUSIONI
-----------
Il sistema funziona correttamente per tutti i casi d'uso previsti. Il punto più
delicato è stato la gestione degli stati dell'ordine durante l'evasione parziale,
risolto aggiornando le quantità riga per riga e decidendo lo stato finale solo alla fine.
Un limite attuale è che non c'è autenticazione: chiunque avvii il programma può fare
tutto. Inoltre i file JSON non sono protetti da scritture concorrenti, quindi il sistema
regge per un singolo utente alla volta, non per un team. Come miglioramento futuro
si potrebbe usare un database SQLite invece di JSON, che gestisce meglio questi casi.
================================================================================
"""

import csv
import json
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any, Optional

# Cartelle e file usati per salvare i dati
DATA_DIR = Path("data")
REPORTS_DIR = Path("reports")
PRODOTTI_FILE = DATA_DIR / "prodotti.json"
ORDINI_FILE = DATA_DIR / "ordini.json"
LOG_FILE = DATA_DIR / "log_operazioni.csv"

# Valori ammessi per la priorità di un ordine
PRIORITA_VALIDE = ["bassa", "normale", "alta", "urgente"]

# Tutti i possibili stati di un ordine
STATI_ORDINE = ["nuovo", "evaso", "parziale", "annullato", "in_attesa"]

# Operatore di default quando l'azione viene fatta dal sistema automaticamente
OPERATORE_DEFAULT = "sistema"


# Dati di esempio per popolare il sistema alla prima esecuzione.
# Senza questi dati, il programma partirebbe completamente vuoto e sarebbe
# difficile testarlo. Ho scelto 8 prodotti reali del settore elettrico.
PRODOTTI_INIZIALI: list[dict[str, Any]] = [
    {
        "codice": "P001",
        "nome": "Interruttore magnetotermico 16A",
        "categoria": "Protezione",
        "giacenza": 120,
        "punto_riordino": 30,   # sotto questa soglia il sistema avvisa di riordinare
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
    },
]

# Tre ordini di esempio in stati diversi per poter testare subito i vari flussi
ORDINI_INIZIALI: list[dict[str, Any]] = [
    {
        "id_ordine": "ORD-2026-001",
        "data": "2026-04-18",
        "cliente": "Officina Rossi & Figli",
        "priorita": "normale",
        "stato": "evaso",
        "righe": [
            {"codice": "P001", "quantita_richiesta": 20, "quantita_evasa": 20},
            {"codice": "P003", "quantita_richiesta": 10, "quantita_evasa": 10},
        ],
        "note": ""
    },
    {
        "id_ordine": "ORD-2026-002",
        "data": "2026-04-19",
        "cliente": "Elettroforniture Bianchi",
        "priorita": "alta",
        "stato": "parziale",   # P002 non era disponibile per intero
        "righe": [
            {"codice": "P002", "quantita_richiesta": 20, "quantita_evasa": 15},
            {"codice": "P005", "quantita_richiesta": 30, "quantita_evasa": 30},
        ],
        "note": "P002 evaso parzialmente per scorta insufficiente"
    },
    {
        "id_ordine": "ORD-2026-003",
        "data": "2026-04-20",
        "cliente": "Rivendita Verdi S.n.c.",
        "priorita": "urgente",
        "stato": "nuovo",   # ancora da evadere, utile per testare il flusso
        "righe": [
            {"codice": "P004", "quantita_richiesta": 5, "quantita_evasa": 0},
            {"codice": "P008", "quantita_richiesta": 3, "quantita_evasa": 0},
        ],
        "note": ""
    },
]


# ==============================================================================
# CLASSE Logger
# ==============================================================================
# Si occupa di scrivere ogni operazione su un file CSV con data, ora e operatore.
# Ho scelto il CSV perché è facile da aprire in Excel per fare analisi successive.

class Logger:

    def __init__(self, log_path: Path):
        self.log_path = log_path
        self._init_file()

    def _init_file(self):
        """Crea la cartella e il file CSV se non esistono ancora."""
        # mkdir con parents=True crea anche le cartelle intermedie se mancano
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.log_path.exists():
            with open(self.log_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["timestamp", "operatore", "operazione", "risorsa", "dettaglio"])

    def log(self, operazione: str, risorsa: str, dettaglio: str = "", operatore: str = OPERATORE_DEFAULT):
        """Aggiunge una riga al log. Uso la modalità 'a' (append) per non sovrascrivere le righe precedenti."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, operatore, operazione, risorsa, dettaglio])

    def get_log_oggi(self) -> list[dict[str, Any]]:
        """Restituisce solo le voci di oggi filtrando per prefisso della data nel timestamp."""
        oggi = date.today().strftime("%Y-%m-%d")
        entries = []
        try:
            with open(self.log_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # il timestamp ha formato "2026-04-21 14:30:00", quindi basta
                    # controllare se inizia con la data di oggi
                    if row["timestamp"].startswith(oggi):
                        entries.append(dict(row))
        except FileNotFoundError:
            pass  # se il file non esiste ancora restituisce lista vuota
        return entries


# ==============================================================================
# CLASSE DataManager
# ==============================================================================
# Gestisce il salvataggio e il caricamento dei file JSON.
# Ho separato questa logica dalle altre classi così se in futuro volessi usare
# un database invece di JSON, cambierei solo questa classe.

class DataManager:

    def __init__(self, logger: Logger):
        self.logger = logger
        # Creo le cartelle necessarie all'avvio se non esistono
        DATA_DIR.mkdir(exist_ok=True)
        REPORTS_DIR.mkdir(exist_ok=True)

    def carica_prodotti(self) -> list[dict[str, Any]]:
        """Se il file prodotti non esiste (prima esecuzione), lo crea con i dati iniziali."""
        if not PRODOTTI_FILE.exists():
            self._salva_json(PRODOTTI_FILE, PRODOTTI_INIZIALI)
            self.logger.log("INIT", "prodotti.json", f"Creati {len(PRODOTTI_INIZIALI)} prodotti iniziali")
        return self._carica_json(PRODOTTI_FILE)

    def salva_prodotti(self, prodotti: list[dict[str, Any]]):
        self._salva_json(PRODOTTI_FILE, prodotti)
        self.logger.log("SALVATAGGIO", "prodotti.json", f"{len(prodotti)} prodotti salvati")

    def carica_ordini(self) -> list[dict[str, Any]]:
        """Se il file ordini non esiste (prima esecuzione), lo crea con gli ordini di esempio."""
        if not ORDINI_FILE.exists():
            self._salva_json(ORDINI_FILE, ORDINI_INIZIALI)
            self.logger.log("INIT", "ordini.json", f"Creati {len(ORDINI_INIZIALI)} ordini iniziali")
        return self._carica_json(ORDINI_FILE)

    def salva_ordini(self, ordini: list[dict[str, Any]]):
        self._salva_json(ORDINI_FILE, ordini)
        self.logger.log("SALVATAGGIO", "ordini.json", f"{len(ordini)} ordini salvati")

    @staticmethod
    def _carica_json(path: Path) -> list[dict[str, Any]]:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def _salva_json(path: Path, data: Any):
        # ensure_ascii=False serve per salvare correttamente i caratteri accentati (è, à, ...)
        # indent=2 rende il file leggibile anche aprendolo con un editor di testo
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


# ==============================================================================
# CLASSE Warehouse
# ==============================================================================
# Gestisce il catalogo prodotti e le giacenze. I prodotti vengono tenuti in
# memoria durante l'esecuzione e salvati su file solo quando serve.

class Warehouse:

    def __init__(self, data_manager: DataManager, logger: Logger):
        self.dm = data_manager
        self.logger = logger
        # Carico i prodotti in memoria all'avvio: così non devo rileggere il file
        # ogni volta che cerco un prodotto
        self.prodotti: list[dict[str, Any]] = self.dm.carica_prodotti()

    def salva(self):
        """Salva lo stato attuale dei prodotti su file."""
        self.dm.salva_prodotti(self.prodotti)

    def get_prodotto(self, codice: str) -> Optional[dict[str, Any]]:
        """Cerca un prodotto per codice. Restituisce None se non esiste."""
        for p in self.prodotti:
            # upper() su entrambi per non distinguere tra "p001" e "P001"
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
        Restituisce i prodotti che corrispondono ai filtri indicati.
        Se un filtro è vuoto/False viene ignorato.
        """
        risultati = self.prodotti

        if codice:
            risultati = [p for p in risultati if codice.upper() in p["codice"].upper()]

        if categoria:
            risultati = [p for p in risultati if categoria.lower() in p["categoria"].lower()]

        # questo filtro mostra solo i prodotti che hanno bisogno di essere riordinati
        if sotto_riordino:
            risultati = [p for p in risultati if p["giacenza"] <= p["punto_riordino"]]

        return risultati

    def aggiorna_giacenza(self, codice: str, delta: int, operatore: str = OPERATORE_DEFAULT) -> bool:
        """
        Modifica la giacenza di un prodotto aggiungendo delta (positivo = carico, negativo = scarico).
        Registra anche un alert nel log se la giacenza scende sotto il punto di riordino.
        """
        prodotto = self.get_prodotto(codice)
        if not prodotto:
            return False  # prodotto non trovato

        giacenza_precedente = prodotto["giacenza"]
        prodotto["giacenza"] += delta

        self.logger.log(
            "AGGIORNAMENTO_GIACENZA",
            codice,
            f"{giacenza_precedente} → {prodotto['giacenza']} (delta: {delta:+d})",
            operatore
        )

        # Controllo soglia: se dopo l'aggiornamento siamo sotto il punto di riordino, avviso
        if prodotto["giacenza"] <= prodotto["punto_riordino"]:
            self.logger.log(
                "ALERT_RIORDINO",
                codice,
                f"Giacenza {prodotto['giacenza']} <= punto riordino {prodotto['punto_riordino']}",
                operatore
            )

        return True

    def aggiungi_prodotto(self, prodotto: dict[str, Any], operatore: str = OPERATORE_DEFAULT):
        """Aggiunge un nuovo prodotto al catalogo, normalizzando il codice in maiuscolo."""
        codice = prodotto["codice"].upper()
        prodotto["codice"] = codice
        self.prodotti.append(prodotto)
        self.logger.log("NUOVO_PRODOTTO", codice, prodotto["nome"], operatore)

    def categorie(self) -> list[str]:
        """Restituisce l'elenco delle categorie presenti, senza duplicati e in ordine alfabetico."""
        return sorted(set(p["categoria"] for p in self.prodotti))

    def prodotti_sotto_riordino(self) -> list[dict[str, Any]]:
        """Restituisce tutti i prodotti con giacenza uguale o inferiore al punto di riordino."""
        return [p for p in self.prodotti if p["giacenza"] <= p["punto_riordino"]]


# ==============================================================================
# CLASSE OrderManager
# ==============================================================================
# Si occupa di creare, evadere e annullare gli ordini.
# La logica più complessa è nell'evasione, dove bisogna aggiornare le giacenze
# riga per riga e determinare lo stato finale dell'ordine.

class OrderManager:

    def __init__(self, data_manager: DataManager, warehouse: Warehouse, logger: Logger):
        self.dm = data_manager
        self.wh = warehouse
        self.logger = logger
        self.ordini: list[dict[str, Any]] = self.dm.carica_ordini()

    def salva(self):
        self.dm.salva_ordini(self.ordini)

    def _genera_id(self) -> str:
        """
        Genera il prossimo ID ordine nel formato ORD-ANNO-NNN.
        Conta quanti ordini esistono già per l'anno corrente e prende il numero successivo.
        """
        anno = datetime.now().year
        # Filtro gli ordini dell'anno in corso per trovare l'ultimo numero usato
        ordini_anno = [o["id_ordine"] for o in self.ordini if str(anno) in o["id_ordine"]]
        if not ordini_anno:
            return f"ORD-{anno}-001"
        # Estraggo solo la parte numerica finale di ogni ID (es. "003") e prendo il massimo
        numeri = [int(oid.split("-")[-1]) for oid in ordini_anno]
        prossimo = max(numeri) + 1
        return f"ORD-{anno}-{prossimo:03d}"  # :03d garantisce sempre 3 cifre (es. 004, not 4)

    def registra_ordine(
        self,
        cliente: str,
        righe: list[dict[str, Any]],
        priorita: str = "normale",
        operatore: str = OPERATORE_DEFAULT
    ) -> dict[str, Any]:
        """
        Registra un nuovo ordine verificando la disponibilità per ogni prodotto.
        NON scarica le giacenze: quello avviene solo quando si evade l'ordine.
        Lo stato dell'ordine dipende dalla disponibilità peggiore tra le righe:
          - tutte disponibili  → "nuovo"
          - almeno una parziale → "parziale"
          - almeno una a zero o non trovata → "in_attesa"
        """
        id_ordine = self._genera_id()
        data_oggi = date.today().strftime("%Y-%m-%d")

        righe_processate = []
        stato_ordine = "nuovo"  # parto da nuovo e peggioro se trovo problemi

        for riga in righe:
            codice = riga["codice"].upper()
            quantita_richiesta = riga["quantita"]
            prodotto = self.wh.get_prodotto(codice)

            if not prodotto:
                # Prodotto non trovato nel catalogo
                righe_processate.append({
                    "codice": codice,
                    "quantita_richiesta": quantita_richiesta,
                    "quantita_evasa": 0,
                    "disponibilita": "prodotto_non_trovato"
                })
                stato_ordine = "in_attesa"
                continue

            # Confronto la giacenza disponibile con quanto richiesto
            giacenza = prodotto["giacenza"]
            if giacenza >= quantita_richiesta:
                disponibilita = "disponibile"
            elif giacenza > 0:
                disponibilita = "parziale"
                # peggioro lo stato solo se era ancora "nuovo"
                if stato_ordine == "nuovo":
                    stato_ordine = "parziale"
            else:
                disponibilita = "indisponibile"
                stato_ordine = "in_attesa"  # zero unità disponibili: ordine bloccato

            righe_processate.append({
                "codice": codice,
                "quantita_richiesta": quantita_richiesta,
                "quantita_evasa": 0,
                "disponibilita": disponibilita
            })

        # Costruisco il dizionario dell'ordine completo
        nuovo_ordine: dict[str, Any] = {
            "id_ordine": id_ordine,
            "data": data_oggi,
            "cliente": cliente,
            "priorita": priorita,
            "stato": stato_ordine,
            "righe": righe_processate,
            "note": ""
        }
        self.ordini.append(nuovo_ordine)
        self.logger.log(
            "NUOVO_ORDINE",
            id_ordine,
            f"Cliente: {cliente} | Priorità: {priorita} | Stato: {stato_ordine}",
            operatore
        )
        return nuovo_ordine

    def evadi_ordine(self, id_ordine: str, operatore: str = OPERATORE_DEFAULT) -> tuple[bool, str]:
        """
        Tenta di evadere un ordine: per ogni riga, scarica dal magazzino
        quanto disponibile (fino alla quantità richiesta).
        Uso min() per non rischiare di portare la giacenza sotto zero.
        """
        ordine = self.get_ordine(id_ordine)
        if not ordine:
            return False, f"Ordine {id_ordine} non trovato."
        if ordine["stato"] == "evaso":
            return False, f"Ordine {id_ordine} è già stato evaso."
        if ordine["stato"] == "annullato":
            return False, f"Ordine {id_ordine} è annullato, non si può evadere."

        tutto_evaso = True  # diventerà False se anche solo una riga rimane incompleta
        messaggi: list[str] = []

        for riga in ordine["righe"]:
            codice = riga["codice"]
            # Calcolo quanto manca ancora da evadere per questa riga
            da_evadere = riga["quantita_richiesta"] - riga["quantita_evasa"]

            if da_evadere <= 0:
                continue  # questa riga era già completa

            prodotto = self.wh.get_prodotto(codice)
            if not prodotto:
                messaggi.append(f"  {codice}: prodotto non trovato in magazzino")
                tutto_evaso = False
                continue

            # min() serve a non scaricare più di quello che c'è in magazzino
            da_scaricare = min(da_evadere, prodotto["giacenza"])

            if da_scaricare > 0:
                self.wh.aggiorna_giacenza(codice, -da_scaricare, operatore)
                riga["quantita_evasa"] += da_scaricare
                # aggiorno il flag di disponibilità per rispecchiare il risultato reale
                if da_scaricare == da_evadere:
                    riga["disponibilita"] = "disponibile"
                else:
                    riga["disponibilita"] = "parziale"

            # Controllo se la riga è ora completamente soddisfatta
            if riga["quantita_evasa"] < riga["quantita_richiesta"]:
                tutto_evaso = False
                mancanti = riga["quantita_richiesta"] - riga["quantita_evasa"]
                messaggi.append(
                    f"  {codice}: evasi {riga['quantita_evasa']}/{riga['quantita_richiesta']} — mancano {mancanti}"
                )
            else:
                messaggi.append(
                    f"  {codice}: evasi {riga['quantita_evasa']}/{riga['quantita_richiesta']} ✓"
                )

        # Lo stato finale è "evaso" solo se tutte le righe sono state completate
        if tutto_evaso:
            ordine["stato"] = "evaso"
        else:
            ordine["stato"] = "parziale"

        self.logger.log(
            "EVASIONE_ORDINE",
            id_ordine,
            f"Stato finale: {ordine['stato']} | Operatore: {operatore}",
            operatore
        )
        messaggio_finale = f"Ordine {id_ordine} — stato: {ordine['stato'].upper()}\n" + "\n".join(messaggi)
        return True, messaggio_finale

    def annulla_ordine(self, id_ordine: str, operatore: str = OPERATORE_DEFAULT) -> tuple[bool, str]:
        """Annulla un ordine che non sia già stato evaso. Non modifica le giacenze."""
        ordine = self.get_ordine(id_ordine)
        if not ordine:
            return False, f"Ordine {id_ordine} non trovato."
        if ordine["stato"] == "evaso":
            return False, "Non si può annullare un ordine già evaso."
        ordine["stato"] = "annullato"
        self.logger.log("ANNULLAMENTO_ORDINE", id_ordine, f"Cliente: {ordine['cliente']}", operatore)
        return True, f"Ordine {id_ordine} annullato."

    def get_ordine(self, id_ordine: str) -> Optional[dict[str, Any]]:
        """Cerca un ordine per ID esatto. Restituisce None se non esiste."""
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
        Filtra gli ordini per i criteri indicati (tutti opzionali).
        Per le date uso il confronto diretto tra stringhe: funziona perché
        il formato YYYY-MM-DD ha lo stesso ordine lessicografico e cronologico.
        """
        risultati = self.ordini

        if stato:
            risultati = [o for o in risultati if o["stato"] == stato]

        if cliente:
            risultati = [o for o in risultati if cliente.lower() in o["cliente"].lower()]

        if data_da:
            risultati = [o for o in risultati if o["data"] >= data_da]

        if data_a:
            risultati = [o for o in risultati if o["data"] <= data_a]

        return risultati

    def ordini_oggi(self) -> list[dict[str, Any]]:
        oggi = date.today().strftime("%Y-%m-%d")
        return [o for o in self.ordini if o["data"] == oggi]


# ==============================================================================
# CLASSE ReportGenerator
# ==============================================================================
# Genera il report giornaliero in due formati: TXT (leggibile a schermo) e
# CSV (importabile in Excel). Ho scelto questi due formati per coprire sia
# chi usa il terminale sia chi preferisce i fogli di calcolo.

class ReportGenerator:

    def __init__(self, warehouse: Warehouse, order_manager: OrderManager, logger: Logger):
        self.wh = warehouse
        self.om = order_manager
        self.logger = logger

    def genera_report_giornaliero(self, data_report: str = "") -> tuple[str, str]:
        """
        Genera il report per la data indicata (default: oggi).
        Restituisce il testo del report e il percorso del file CSV salvato.
        """
        if not data_report:
            data_report = date.today().strftime("%Y-%m-%d")

        # Separo gli ordini del giorno per stato
        ordini_giorno = [o for o in self.om.ordini if o["data"] == data_report]
        ordini_evasi    = [o for o in ordini_giorno if o["stato"] == "evaso"]
        ordini_parziali = [o for o in ordini_giorno if o["stato"] == "parziale"]
        ordini_sospeso  = [o for o in ordini_giorno if o["stato"] in ("nuovo", "in_attesa")]
        ordini_annullati = [o for o in ordini_giorno if o["stato"] == "annullato"]

        # Calcolo le vendite del giorno: sommo le quantità evase per ogni prodotto
        # usando un dizionario come accumulatore (chiave = codice prodotto)
        vendite: dict[str, int] = {}
        for ordine in ordini_giorno:
            for riga in ordine["righe"]:
                codice = riga["codice"]
                vendite[codice] = vendite.get(codice, 0) + riga.get("quantita_evasa", 0)
        # Ordino per quantità decrescente e prendo i primi 5
        top_prodotti = sorted(vendite.items(), key=lambda x: x[1], reverse=True)[:5]

        prodotti_riordino = self.wh.prodotti_sotto_riordino()

        # ---- Costruzione del testo TXT ----
        sep   = "=" * 60
        linea = "-" * 60

        righe_testo = [
            sep,
            f"  REPORT GIORNALIERO — LogiServe S.r.l.",
            f"  Data: {data_report}",
            f"  Generato il: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            sep, "",
            "RIEPILOGO ORDINI", linea,
            f"  Ordini ricevuti oggi  : {len(ordini_giorno)}",
            f"  Ordini evasi          : {len(ordini_evasi)}",
            f"  Ordini parziali       : {len(ordini_parziali)}",
            f"  Ordini in sospeso     : {len(ordini_sospeso)}",
            f"  Ordini annullati      : {len(ordini_annullati)}", "",
        ]

        if top_prodotti:
            righe_testo += ["PRODOTTI PIÙ VENDUTI (OGGI)", linea]
            for codice, qty in top_prodotti:
                prodotto = self.wh.get_prodotto(codice)
                nome = prodotto["nome"] if prodotto else codice
                righe_testo.append(f"  {codice} — {nome}: {qty} unità")
            righe_testo.append("")

        righe_testo += [
            "STATO GIACENZE", linea,
            f"  {'Codice':<8} {'Nome':<35} {'Giacenza':>9} {'Riordino':>9} {'UM':<6} {'Stato':<12}",
            f"  {'-'*8} {'-'*35} {'-'*9} {'-'*9} {'-'*6} {'-'*12}",
        ]
        for p in sorted(self.wh.prodotti, key=lambda x: x["codice"]):
            if p["giacenza"] == 0:
                stato_g = "✗ ESAURITO"
            elif p["giacenza"] <= p["punto_riordino"]:
                stato_g = "⚠ RIORDINO"
            else:
                stato_g = "OK"
            righe_testo.append(
                f"  {p['codice']:<8} {p['nome'][:35]:<35} {p['giacenza']:>9} "
                f"{p['punto_riordino']:>9} {p['unita_misura']:<6} {stato_g:<12}"
            )
        righe_testo.append("")

        if prodotti_riordino:
            righe_testo += ["ALERT: PRODOTTI DA RIORDINARE", linea]
            for p in prodotti_riordino:
                righe_testo.append(
                    f"  {p['codice']} — {p['nome']}: giacenza {p['giacenza']} (soglia: {p['punto_riordino']})"
                )
            righe_testo.append("")

        if ordini_sospeso:
            righe_testo += ["ORDINI IN SOSPESO", linea]
            for o in ordini_sospeso:
                righe_testo.append(
                    f"  {o['id_ordine']} | {o['cliente']} | Priorità: {o['priorita']}"
                )
            righe_testo.append("")

        righe_testo.append(sep)
        testo = "\n".join(righe_testo)

        # Salvo il file TXT
        txt_path = REPORTS_DIR / f"report_{data_report}.txt"
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(testo)

        # ---- Costruzione e salvataggio del CSV ----
        # Uso tre colonne (Sezione, Campo, Valore) per poterlo filtrare facilmente in Excel
        csv_path = REPORTS_DIR / f"report_{data_report}.csv"
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Sezione", "Campo", "Valore"])
            writer.writerow(["Riepilogo", "Data report", data_report])
            writer.writerow(["Riepilogo", "Ordini ricevuti", len(ordini_giorno)])
            writer.writerow(["Riepilogo", "Ordini evasi", len(ordini_evasi)])
            writer.writerow(["Riepilogo", "Ordini parziali", len(ordini_parziali)])
            writer.writerow(["Riepilogo", "Ordini in sospeso", len(ordini_sospeso)])
            writer.writerow(["Riepilogo", "Ordini annullati", len(ordini_annullati)])
            for codice, qty in top_prodotti:
                writer.writerow(["Top venduto", codice, qty])
            for p in self.wh.prodotti:
                writer.writerow(["Giacenza", p["codice"], p["giacenza"]])
            for p in prodotti_riordino:
                writer.writerow(["Alert riordino", p["codice"], p["giacenza"]])

        self.logger.log("REPORT", f"report_{data_report}", f"Salvato in {txt_path} e {csv_path}")
        return testo, str(csv_path)


# ==============================================================================
# CLASSE CLI
# ==============================================================================
# Gestisce tutta l'interfaccia a menu. Ho cercato di tenere ogni funzione
# il più corta possibile, delegando la logica alle altre classi.

class CLI:

    def __init__(self):
        # Creo le componenti nell'ordine giusto: Logger prima di tutto,
        # perché le altre classi lo usano già durante l'inizializzazione
        logger = Logger(LOG_FILE)
        dm = DataManager(logger)
        self.wh = Warehouse(dm, logger)
        self.om = OrderManager(dm, self.wh, logger)
        self.rg = ReportGenerator(self.wh, self.om, logger)
        self.logger = logger
        self.operatore = "operatore"  # modificabile dal menu impostazioni

    @staticmethod
    def _stampa_intestazione(titolo: str):
        print(f"\n{'=' * 60}")
        print(f"  {titolo}")
        print(f"{'=' * 60}")

    @staticmethod
    def _input(prompt: str) -> str:
        """Legge una stringa da tastiera. In caso di Ctrl+C o EOF restituisce stringa vuota."""
        try:
            return input(prompt).strip()
        except (EOFError, KeyboardInterrupt):
            print("\nOperazione annullata.")
            return ""

    @staticmethod
    def _input_int(prompt: str, minimo: int = 1) -> Optional[int]:
        """Chiede un numero intero ripetendo la domanda finché il valore non è valido.
        Se l'utente preme invio senza scrivere nulla, restituisce None."""
        while True:
            val = CLI._input(prompt)
            if val == "":
                return None  # l'utente vuole saltare
            try:
                n = int(val)
                if n < minimo:
                    print(f"  Inserire un valore >= {minimo}.")
                    continue
                return n
            except ValueError:
                print("  Valore non valido. Inserire un numero intero.")

    @staticmethod
    def _conferma(domanda: str) -> bool:
        """Chiede conferma sì/no. Il default è NO (la N maiuscola nel prompt lo indica)."""
        risposta = CLI._input(f"{domanda} [s/N]: ").lower()
        return risposta in ("s", "si", "sì", "y", "yes")

    def avvia(self):
        print("\n  Benvenuto in LogiServe — Sistema di Monitoraggio Ordini e Magazzino")
        print(f"  Operatore corrente: {self.operatore}")
        self._avvisa_riordino_iniziale()  # mostro subito se ci sono prodotti critici
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
        """Mostra all'avvio i prodotti che hanno bisogno di essere riordinati."""
        sotto = self.wh.prodotti_sotto_riordino()
        if sotto:
            print(f"\n  ⚠  ATTENZIONE: {len(sotto)} prodotto/i sotto il punto di riordino:")
            for p in sotto:
                print(f"     {p['codice']} — {p['nome']}: giacenza {p['giacenza']} (soglia {p['punto_riordino']})")

    # --- Menu Ordini ---

    def _menu_ordini(self):
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
        self._stampa_intestazione("REGISTRA NUOVO ORDINE")

        cliente = self._input("Cliente: ")
        if not cliente:
            print("  Il nome del cliente è obbligatorio.")
            return

        print(f"  Priorità disponibili: {', '.join(PRIORITA_VALIDE)}")
        priorita = self._input("Priorità [normale]: ").lower() or "normale"
        if priorita not in PRIORITA_VALIDE:
            print("  Priorità non riconosciuta, uso 'normale'.")
            priorita = "normale"

        # Raccolgo le righe dell'ordine in un loop: ogni iterazione chiede codice + quantità
        righe: list[dict[str, Any]] = []
        print("\n  Inserire i prodotti dell'ordine (lasciare il codice vuoto per terminare):")
        while True:
            codice = self._input("  Codice prodotto: ").upper()
            if not codice:
                break  # l'utente ha finito di inserire prodotti

            prodotto = self.wh.get_prodotto(codice)
            if not prodotto:
                print(f"  ⚠  Prodotto {codice} non trovato nel catalogo.")
                if not self._conferma("  Aggiungere comunque all'ordine?"):
                    continue
            else:
                # mostro le info del prodotto per aiutare l'operatore
                print(f"  → {prodotto['nome']} | Giacenza attuale: {prodotto['giacenza']} {prodotto['unita_misura']}")

            quantita = self._input_int("  Quantità: ", minimo=1)
            if quantita is None:
                continue  # quantità vuota = salto questo prodotto
            righe.append({"codice": codice, "quantita": quantita})

        if not righe:
            print("  Nessun prodotto inserito. Ordine non creato.")
            return

        ordine = self.om.registra_ordine(cliente, righe, priorita, self.operatore)
        print(f"\n  Ordine registrato con ID: {ordine['id_ordine']}")
        print(f"  Stato: {ordine['stato'].upper()}")
        for r in ordine["righe"]:
            print(f"  {r['codice']}: richiesti {r['quantita_richiesta']} — disponibilità: {r.get('disponibilita', '?')}")

        self.om.salva()

    def _evadi_ordine(self):
        self._stampa_intestazione("EVADI ORDINE")
        # Mostro prima la lista degli ordini in attesa di evasione per aiutare l'utente
        self._mostra_lista_ordini_breve(filtro_stato=["nuovo", "parziale", "in_attesa"])

        id_ordine = self._input("\nID ordine da evadere: ").upper()
        if not id_ordine:
            return
        if not self._conferma(f"Confermare evasione di {id_ordine}?"):
            return

        ok, msg = self.om.evadi_ordine(id_ordine, self.operatore)
        print(f"\n{msg}")

        if ok:
            self.om.salva()
            self.wh.salva()  # salvo anche le giacenze aggiornate
            self._avvisa_riordino_post_evasione()

    def _annulla_ordine(self):
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
        self._stampa_intestazione("VISUALIZZA ORDINI")
        print("  Filtri opzionali (invio per saltare):")
        stato   = self._input(f"  Stato ({'/'.join(STATI_ORDINE)}): ").lower()
        cliente = self._input("  Cliente (anche parziale): ")
        data_da = self._input("  Data da (AAAA-MM-GG): ")
        data_a  = self._input("  Data a  (AAAA-MM-GG): ")

        ordini = self.om.get_ordini_filtrati(stato, cliente, data_da, data_a)
        if not ordini:
            print("  Nessun ordine trovato con i filtri indicati.")
            return

        print(f"\n  {'ID Ordine':<18} {'Data':<12} {'Cliente':<28} {'Priorità':<10} {'Stato':<12}")
        print(f"  {'-'*18} {'-'*12} {'-'*28} {'-'*10} {'-'*12}")
        for o in ordini:
            print(
                f"  {o['id_ordine']:<18} {o['data']:<12} {o['cliente'][:28]:<28} "
                f"{o['priorita']:<10} {o['stato']:<12}"
            )
        print(f"\n  Trovati: {len(ordini)} ordini")

    def _dettaglio_ordine(self):
        self._stampa_intestazione("DETTAGLIO ORDINE")
        id_ordine = self._input("ID ordine: ").upper()
        if not id_ordine:
            return
        ordine = self.om.get_ordine(id_ordine)
        if not ordine:
            print(f"  Ordine {id_ordine} non trovato.")
            return

        print(f"\n  ID Ordine : {ordine['id_ordine']}")
        print(f"  Data      : {ordine['data']}")
        print(f"  Cliente   : {ordine['cliente']}")
        print(f"  Priorità  : {ordine['priorita']}")
        print(f"  Stato     : {ordine['stato'].upper()}")
        if ordine["note"]:
            print(f"  Note      : {ordine['note']}")

        print(f"\n  {'Codice':<8} {'Richiesti':>10} {'Evasi':>8} {'Disponibilità':<18}")
        print(f"  {'-'*8} {'-'*10} {'-'*8} {'-'*18}")
        for r in ordine["righe"]:
            prodotto = self.wh.get_prodotto(r["codice"])
            # mostro il nome del prodotto tra parentesi se esiste ancora in catalogo
            nome = f"({prodotto['nome'][:20]})" if prodotto else ""
            print(
                f"  {r['codice']:<8} {r['quantita_richiesta']:>10} {r['quantita_evasa']:>8} "
                f"{r.get('disponibilita', '?'):<18} {nome}"
            )

    def _mostra_lista_ordini_breve(self, filtro_stato: Optional[list[str]] = None):
        """Stampa un riepilogo compatto degli ordini, usato come riferimento prima di chiedere un ID."""
        ordini = self.om.ordini
        if filtro_stato:
            ordini = [o for o in ordini if o["stato"] in filtro_stato]
        if not ordini:
            print("  Nessun ordine disponibile.")
            return
        print(f"\n  {'ID Ordine':<18} {'Cliente':<28} {'Stato':<12} {'Priorità'}")
        print(f"  {'-'*18} {'-'*28} {'-'*12} {'-'*10}")
        # Mostro solo gli ultimi 15 per non riempire troppo lo schermo
        for o in ordini[-15:]:
            print(f"  {o['id_ordine']:<18} {o['cliente'][:28]:<28} {o['stato']:<12} {o['priorita']}")

    # --- Menu Magazzino ---

    def _menu_magazzino(self):
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
        self._stampa_intestazione("STATO MAGAZZINO")
        print("  Filtri opzionali (invio per saltare):")
        codice = self._input("  Codice: ")
        print(f"  Categorie presenti: {', '.join(self.wh.categorie())}")
        categoria = self._input("  Categoria: ")
        sotto_str = self._input("  Solo prodotti sotto riordino? [s/N]: ").lower()
        sotto_riordino = sotto_str in ("s", "si", "sì", "y")

        prodotti = self.wh.get_prodotti_filtrati(codice, categoria, sotto_riordino)
        if not prodotti:
            print("  Nessun prodotto trovato.")
            return

        print(
            f"\n  {'Cod':<8} {'Nome':<35} {'Giacenza':>9} {'Riordino':>9} "
            f"{'UM':<6} {'Prezzo':>8} {'Stato'}"
        )
        print(f"  {'-'*8} {'-'*35} {'-'*9} {'-'*9} {'-'*6} {'-'*8} {'-'*10}")
        for p in sorted(prodotti, key=lambda x: x["codice"]):
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
        print(f"\n  Totale: {len(prodotti)} prodotti")

    def _prodotti_riordino(self):
        self._stampa_intestazione("PRODOTTI SOTTO PUNTO DI RIORDINO")
        prodotti = self.wh.prodotti_sotto_riordino()
        if not prodotti:
            print("  Tutti i prodotti sono sopra il punto di riordino.")
            return
        for p in prodotti:
            print(
                f"  {p['codice']:<8} {p['nome']:<40} "
                f"Giacenza: {p['giacenza']:>6} / Riordino: {p['punto_riordino']}"
            )

    def _aggiorna_giacenza_manuale(self):
        """Permette di registrare un carico (+) o uno scarico (-) manuale."""
        self._stampa_intestazione("AGGIORNAMENTO GIACENZA MANUALE")
        codice = self._input("Codice prodotto: ").upper()
        if not codice:
            return

        prodotto = self.wh.get_prodotto(codice)
        if not prodotto:
            print(f"  Prodotto {codice} non trovato.")
            return

        print(f"  {prodotto['nome']} — Giacenza attuale: {prodotto['giacenza']} {prodotto['unita_misura']}")
        print("  Inserire la variazione (es. +50 per un carico, -10 per uno scarico):")
        delta_str = self._input("  Variazione: ")
        if not delta_str:
            return

        try:
            delta = int(delta_str)
        except ValueError:
            print("  Valore non valido.")
            return

        # Avviso se la variazione porterebbe la giacenza sotto zero
        nuova_giacenza = prodotto["giacenza"] + delta
        if nuova_giacenza < 0:
            print(f"  Attenzione: la giacenza diventerebbe {nuova_giacenza} (negativa).")
            if not self._conferma("Continuare comunque?"):
                return

        self.wh.aggiorna_giacenza(codice, delta, self.operatore)
        self.wh.salva()
        # prodotto["giacenza"] è già aggiornato perché aggiorna_giacenza modifica il dizionario
        print(f"  Giacenza aggiornata: {prodotto['giacenza']} {prodotto['unita_misura']}")

    def _aggiungi_prodotto(self):
        self._stampa_intestazione("AGGIUNGI NUOVO PRODOTTO")

        codice = self._input("Codice (es. P009): ").upper()
        if not codice:
            return
        if self.wh.get_prodotto(codice):
            print(f"  Esiste già un prodotto con codice {codice}.")
            return

        nome = self._input("Nome prodotto: ")
        if not nome:
            return

        print(f"  Categorie già presenti: {', '.join(self.wh.categorie())}")
        categoria      = self._input("Categoria: ")
        giacenza       = self._input_int("Giacenza iniziale: ", minimo=0) or 0
        punto_riordino = self._input_int("Punto di riordino: ", minimo=0) or 0
        unita          = self._input("Unità di misura (es. pz, mt, kg): ") or "pz"

        # Accetto sia il punto che la virgola come separatore decimale
        prezzo_str = self._input("Prezzo unitario (€): ")
        try:
            prezzo = float(prezzo_str.replace(",", "."))
        except (ValueError, AttributeError):
            prezzo = 0.0

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
        print(f"  Prodotto {codice} aggiunto correttamente al catalogo.")

    def _avvisa_riordino_post_evasione(self):
        """Mostra i prodotti scesi sotto soglia dopo l'evasione appena completata."""
        sotto = self.wh.prodotti_sotto_riordino()
        if sotto:
            print(f"\n  ⚠  Prodotti scesi sotto il punto di riordino dopo l'evasione:")
            for p in sotto:
                print(f"     {p['codice']} — {p['nome']}: giacenza {p['giacenza']} (soglia {p['punto_riordino']})")

    # --- Menu Report e Log ---

    def _menu_report(self):
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
        print("\n  Generazione report in corso...")
        testo, csv_path = self.rg.genera_report_giornaliero(data)
        print(testo)
        print(f"\n  File CSV salvato in: {csv_path}")
        print(f"  File TXT salvato in: {csv_path.replace('.csv', '.txt')}")

    def _visualizza_log(self):
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

    # --- Menu Impostazioni ---

    def _menu_impostazioni(self):
        self._stampa_intestazione("IMPOSTAZIONI")
        print(f"  Operatore attuale: {self.operatore}")
        nuovo = self._input("Nuovo nome operatore (invio per non cambiare): ")
        if nuovo:
            self.operatore = nuovo
            print(f"  Operatore impostato a: {self.operatore}")

    def _esci(self):
        """Salva tutto prima di uscire."""
        print("\n  Salvataggio dati in corso...")
        self.wh.salva()
        self.om.salva()
        print("  Dati salvati.")
        print("  Arrivederci!\n")


# Punto di ingresso del programma
if __name__ == "__main__":
    try:
        cli = CLI()
        cli.avvia()
    except KeyboardInterrupt:
        print("\n\n  Interruzione da tastiera. Arrivederci!")
        sys.exit(0)
