#!/usr/bin/env python3
"""
================================================================================
PROGETTO: Sistema RAG per la Gestione Intelligente della Conoscenza Aziendale
          DataPulse S.p.A.

          Modulo 02: Large Language Models
================================================================================

Autore  : Simone La Porta
Data    : 2026-05-06


OVERVIEW
--------
Backend RAG (Retrieval-Augmented Generation) per DataPulse S.p.A., che
consente ai dipendenti di interrogare in linguaggio naturale la documentazione
aziendale interna: policy, manuali operativi, FAQ, guide di compliance e
report di progetto.

ARCHITETTURA
------------

  Documenti aziendali (testo + metadati)
           │
           ▼
   DocumentProcessor          ← chunking con overlap
     │           │
     ▼           ▼
  VectorStore  BM25Engine     ← indicizzazione parallela
  (ChromaDB,   (rank-bm25,
   coseno)      lessicale)
     │           │
     └─────┬─────┘
           ▼
   HybridRetriever            ← fusione lineare pesata (alpha * sem + (1-alpha) * bm25)
           │
           ▼
   LLMPipeline                ← prompt strutturato → Ollama | OpenAI
           │
           ▼
   RispostaRAG                ← testo + fonti + confidenza + timestamp

COMPONENTI CHIAVE
-----------------
  EmbeddingEngine   : paraphrase-multilingual-MiniLM-L12-v2 (multilingue, 384d)
  VectorStore       : ChromaDB in-memory, metrica coseno
  BM25Engine        : BM25Okapi con normalizzazione min-max degli score
  HybridRetriever   : alpha=0.6 (sbilanciato verso semantico)
  LLMPipeline       : provider selezionabile (ollama | openai)
  Confidenza         : media degli score ibridi top-k (proxy di qualità del retrieval)

PREREQUISITI
------------
  # Provider LLM (due opzioni: locale con Ollama o cloud con OpenAI):

  # Ollama (nessuna chiave API necessaria)
  pip install langchain-ollama
  ollama serve && ollama pull llama3.2 (o modello che si preferisce usare)

  # OpenAI
  pip install langchain-openai
  export OPENAI_API_KEY="sk-..."

ESECUZIONE
----------
  python PRJ_rag_system_for_company_knowledge.py

  Il provider si imposta nel main() tramite il parametro `provider`.
  La chiave API OpenAI non deve essere inserita nel codice: il sistema la legge
  dalla variabile d'ambiente OPENAI_API_KEY.
  Per modalità retrieval-only (senza LLM): impostare usa_llm=False nel main().
================================================================================
"""

# ── Libreria standard ──────────────────────────────────────────────────────────
import os
import re
import textwrap
import time
import warnings
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

# ── Librerie di terze parti ────────────────────────────────────────────────────
import chromadb
import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer

warnings.filterwarnings("ignore")


# ==============================================================================
# KNOWLEDGE BASE - DataPulse S.p.A.
# ==============================================================================
#
# In un sistema reale questa sezione è sostituita da un loader che legge da
# file, database documentale o repository aziendale. Qui usiamo dizionari
# in-memory per mantenere il progetto autocontenuto ed eseguibile senza
# dipendenze esterne al codice.
#
# Metadati per documento:
#   doc_id         : identificatore univoco (usato nelle citazioni)
#   titolo         : titolo del documento
#   categoria      : tipo: policy | manuale | faq | guida | report
#   autore         : team o ufficio responsabile
#   data_creazione : data di redazione (YYYY-MM-DD)
#   data_validita  : data di scadenza/revisione (None = senza scadenza)
#
# I documenti coprono le aree più rilevanti per il caso d'uso principale
# (accesso ai dati, GDPR, sicurezza) e alcune aree correlate per testare
# la capacità del retriever di discriminare tra documenti simili.
# ==============================================================================

KNOWLEDGE_BASE: list[dict] = [
    {
        "doc_id": "POL-001",
        "titolo": "Policy di Accesso ai Dati dei Clienti",
        "categoria": "policy",
        "autore": "Ufficio Compliance",
        "data_creazione": "2025-03-01",
        "data_validita": "2026-03-01",
        "testo": """
                POLICY DI ACCESSO AI DATI DEI CLIENTI - DataPulse S.p.A.
                Versione 2.1 - Emessa dall'Ufficio Compliance

                AMBITO
                Questa policy si applica a tutti i dipendenti, collaboratori e fornitori
                che accedono ai dati personali dei clienti nell'ambito delle attività di
                DataPulse S.p.A.

                PROCEDURA DI RICHIESTA ACCESSO
                1. Il richiedente compila il modulo RDA-01 disponibile nel portale interno.
                2. Il modulo viene inviato al proprio responsabile di linea per approvazione.
                3. Il responsabile approva o rifiuta entro 3 giorni lavorativi.
                4. L'approvazione viene inoltrata al team Data Governance per registrazione.
                5. Il team Data Governance assegna i permessi nel sistema IAM entro 24 ore.
                6. Il richiedente riceve notifica via email con le credenziali di accesso.

                LIVELLI DI ACCESSO
                - Livello 1 (Sola lettura): analisi, reporting, customer success.
                - Livello 2 (Lettura e modifica): team prodotto, sviluppo backend.
                - Livello 3 (Completo): DBA, architetti di sistema, CISO.

                NORMATIVE APPLICABILI
                - GDPR (Regolamento UE 2016/679): base giuridica per il trattamento, consenso
                  esplicito, diritto all'oblio, portabilità dei dati.
                - D.Lgs. 196/2003 (Codice Privacy italiano): adeguato al GDPR tramite D.Lgs. 101/2018.
                - ISO/IEC 27001: standard di sicurezza delle informazioni adottato da DataPulse.
                - DORA (Digital Operational Resilience Act): applicabile per i servizi finanziari
                  erogati ai clienti bancari.

                OBBLIGHI DEL RICHIEDENTE
                - Accedere ai dati solo per le finalità dichiarate nel modulo RDA-01.
                - Non condividere credenziali di accesso con terzi.
                - Segnalare immediatamente qualsiasi accesso anomalo al team Security.
                - Rispettare il principio di minimizzazione dei dati: accedere solo ai dati
                  strettamente necessari allo scopo dichiarato.

                VIOLAZIONI
                Le violazioni comportano azioni disciplinari fino al licenziamento, oltre a
                possibili conseguenze legali ai sensi del GDPR (sanzioni fino al 4% del
                fatturato mondiale annuo o 20 milioni di euro, si applica il maggiore).
                """,
    },
    {
        "doc_id": "POL-002",
        "titolo": "Policy sulla Classificazione e Protezione dei Dati",
        "categoria": "policy",
        "autore": "Ufficio Compliance",
        "data_creazione": "2025-01-15",
        "data_validita": "2026-01-15",
        "testo": """
                POLICY SULLA CLASSIFICAZIONE E PROTEZIONE DEI DATI - DataPulse S.p.A.
                Versione 1.3

                CLASSIFICAZIONE DEI DATI
                DataPulse adotta il seguente schema di classificazione:

                PUBLIC: informazioni liberamente condivisibili (comunicati stampa, sito web).
                INTERNAL: informazioni ad uso esclusivamente interno (guide operative, note di rilascio).
                CONFIDENTIAL: dati sensibili di business (contratti, roadmap prodotto, dati finanziari).
                RESTRICTED: dati personali dei clienti, credenziali di sistema, chiavi crittografiche.

                GESTIONE DEI DATI RESTRICTED
                I dati classificati RESTRICTED devono essere:
                - Cifrati a riposo con AES-256 e in transito con TLS 1.3.
                - Accessibili solo tramite autenticazione a due fattori (MFA).
                - Sottoposti a log di accesso con retention di 24 mesi.
                - Soggetti a Data Loss Prevention (DLP) sui sistemi aziendali.

                REGISTRO DEI TRATTAMENTI (Art. 30 GDPR)
                DataPulse mantiene un registro aggiornato di tutti i trattamenti di dati
                personali, consultabile dall'Ufficio Compliance. Il registro include:
                finalità del trattamento, categorie di dati, base giuridica, destinatari,
                trasferimenti verso paesi terzi, misure di sicurezza adottate.

                CONSENSO E BASE GIURIDICA
                Prima di avviare un nuovo trattamento di dati personali, il team prodotto
                deve ottenere validazione dall'Ufficio Compliance che identifichi la base
                giuridica corretta (consenso, contratto, legge, interesse legittimo).
                """,
    },
    {
        "doc_id": "MAN-001",
        "titolo": "Manuale Operativo - Onboarding Nuovi Dipendenti",
        "categoria": "manuale",
        "autore": "HR & Operations",
        "data_creazione": "2025-06-01",
        "data_validita": None,
        "testo": """
                MANUALE OPERATIVO - ONBOARDING NUOVI DIPENDENTI
                DataPulse S.p.A. - HR & Operations

                SETTIMANA 1: ACCESSO AI SISTEMI
                Giorno 1: il responsabile IT configura workstation e credenziali AD.
                Giorno 2: richiesta accesso email aziendale, Jira, Confluence, GitHub.
                Giorno 3: formazione su sicurezza informatica (corso obbligatorio eLearning,
                          durata 2 ore, piattaforma: DataPulse Academy).
                Giorni 4-5: affiancamento con buddy assegnato dal team.

                SISTEMI AZIENDALI PRINCIPALI
                - Gestione progetti : Jira (https://jira.datapulse.internal)
                - Documentazione    : Confluence (https://wiki.datapulse.internal)
                - Sorgenti codice   : GitHub Enterprise (https://github.datapulse.internal)
                - Comunicazione     : Slack + Teams (per clienti esterni)
                - Ticketing IT      : ServiceNow

                POLICY OBBLIGATORIE DA FIRMARE ENTRO 7 GIORNI
                1. Codice di Condotta Aziendale
                2. Policy sulla Riservatezza e NDA
                3. Policy di Accesso ai Dati dei Clienti (POL-001)
                4. Acceptable Use Policy dei sistemi IT

                ACCESSO ALLA VPN
                Per lavorare da remoto è obbligatorio usare la VPN aziendale (Cisco AnyConnect).
                Le credenziali VPN vengono fornite dall'IT insieme alle credenziali AD.
                Connessioni da reti pubbliche non protette sono vietate senza VPN attiva.
                """,
    },
    {
        "doc_id": "FAQ-001",
        "titolo": "FAQ - Team Prodotto: Domande Frequenti su GDPR e Compliance",
        "categoria": "faq",
        "autore": "Team Prodotto",
        "data_creazione": "2025-04-10",
        "data_validita": "2026-04-10",
        "testo": """
                FAQ - GDPR E COMPLIANCE PER IL TEAM PRODOTTO

                D: Posso usare i dati dei clienti per testare una nuova feature in sviluppo?
                R: No. I dati reali dei clienti non devono mai essere usati in ambienti di
                   sviluppo o testing. Usa i dataset sintetici generati dal team Data Engineering
                   o la funzione di anonimizzazione disponibile nel tool interno DevDataGen.

                D: Devo informare i clienti se aggiungo un nuovo campo al profilo utente?
                R: Dipende dalla natura del dato. Se il campo raccoglie un nuovo dato personale
                   o cambia la finalità del trattamento, è necessario aggiornare l'informativa
                   privacy e, in alcuni casi, richiedere nuovo consenso. Consulta l'Ufficio
                   Compliance prima del rilascio.

                D: Cosa succede in caso di data breach?
                R: DataPulse è obbligata a notificare il Garante Privacy entro 72 ore dalla
                   rilevazione (Art. 33 GDPR). Attiva immediatamente il protocollo di incident
                   response (IRP-003) e notifica il CISO. Il team Legal gestisce la comunicazione
                   agli interessati se il rischio per i diritti è elevato.

                D: Posso esportare i dati dei clienti in un file Excel per un'analisi ad hoc?
                R: Solo con autorizzazione di Livello 2 o 3 (vedi POL-001) e solo su device
                   aziendali con cifratura abilitata. L'export deve essere documentato nel
                   registro degli accessi e il file eliminato dopo l'uso.

                D: Come gestire una richiesta di cancellazione ("diritto all'oblio") da un cliente?
                R: Entro 30 giorni dalla richiesta, il dato deve essere rimosso da tutti i
                   sistemi, incluse le copie di backup più vecchie di 30 giorni. Workflow
                   automatico disponibile su ServiceNow (ticket tipo: GDPR-DELETE).

                D: I dati vengono trasferiti fuori dall'UE?
                R: Solo verso paesi con adeguato livello di protezione o con Standard Contractual
                   Clauses (SCC) firmate. Tutti i provider cloud usati da DataPulse hanno SCC in
                   essere. Verificare sempre con Compliance prima di integrare un nuovo provider.
                """,
    },
    {
        "doc_id": "FAQ-002",
        "titolo": "FAQ - IT Security: Accessi, VPN e Incidenti",
        "categoria": "faq",
        "autore": "Team IT Security",
        "data_creazione": "2025-05-20",
        "data_validita": "2026-05-20",
        "testo": """
                FAQ - IT SECURITY

                D: Come richiedo l'accesso a un sistema che non è nella mia lista?
                R: Apri un ticket su ServiceNow (categoria: Accessi > Richiesta Nuovo Accesso)
                   specificando il sistema, il livello di accesso richiesto e la motivazione.
                   L'approvazione segue il flusso standard della POL-001.

                D: Ho dimenticato la password della VPN. Come la recupero?
                R: Il recupero autonomo non è disponibile per sicurezza. Contatta l'IT Help Desk
                   (interno 5500 o helpdesk@datapulse.it). La verifica dell'identità avviene
                   tramite codice OTP inviato al numero di telefono registrato in HR.

                D: Ho ricevuto un'email sospetta. Cosa faccio?
                R: Non cliccare link o allegati. Segnala la mail come phishing tramite il pulsante
                   "Segnala Phishing" in Outlook, oppure inoltra a security@datapulse.it.
                   Il SOC risponde entro 4 ore nei giorni lavorativi.

                D: Posso usare un USB personale sui computer aziendali?
                R: No. I dispositivi di storage rimovibili non aziendali sono bloccati a livello
                   di policy DLP. Per trasferire file usa i repository aziendali approvati
                   (SharePoint, GitHub, Confluence).

                D: Qual è la policy sulle password?
                R: Lunghezza minima 12 caratteri, almeno una maiuscola, un numero e un carattere
                   speciale. Cambio ogni 90 giorni. Vietato il riutilizzo delle ultime 12 password.
                   Obbligatorio MFA per tutti i sistemi critici (IAM, GitHub, cloud console).

                D: Come segnalo una vulnerabilità nel software che stiamo sviluppando?
                R: Crea un issue su GitHub con label "security" e visibilità "private". Notifica
                   contestualmente il Security Champion del tuo team. Per vulnerabilità critiche,
                   contatta direttamente il CISO (ciso@datapulse.it).
                """,
    },
    {
        "doc_id": "GUIDA-001",
        "titolo": "Guida Operativa - Gestione delle Richieste dei Clienti",
        "categoria": "guida",
        "autore": "Customer Success Team",
        "data_creazione": "2025-02-28",
        "data_validita": None,
        "testo": """
                GUIDA OPERATIVA - GESTIONE DELLE RICHIESTE DEI CLIENTI
                Customer Success Team - DataPulse S.p.A.

                CANALI DI RICEZIONE RICHIESTE
                - Email: support@datapulse.it (SLA: risposta entro 4 ore lavorative)
                - Chat in-app: widget Intercom (SLA: risposta entro 30 minuti in orario business)
                - Telefono: numero dedicato ai clienti Premium (09:00-18:00, lun-ven)
                - Portale self-service: https://support.datapulse.it

                CLASSIFICAZIONE E PRIORITÀ
                P1 (Critico): sistema non utilizzabile, impatto su produzione del cliente.
                              SLA risoluzione: 4 ore. Escalation immediata a Tech Lead.
                P2 (Alto):    feature principale degradata, workaround disponibile.
                              SLA risoluzione: 8 ore lavorative.
                P3 (Medio):   problema non critico, nessun blocco operativo.
                              SLA risoluzione: 3 giorni lavorativi.
                P4 (Basso):   richiesta di chiarimento, feedback, suggerimento.
                              SLA risposta: 5 giorni lavorativi.

                ESCALATION CHE RICHIEDE ACCESSO AI DATI DEL CLIENTE
                Se la risoluzione di un ticket richiede accesso ai dati del cliente:
                1. Verificare che il contratto preveda la clausola di "accesso per supporto".
                2. Richiedere accesso temporaneo Livello 1 tramite ServiceNow (tipo: SUPP-ACCESS).
                3. Documentare nel ticket l'accesso effettuato e i dati consultati.
                4. Revocare l'accesso entro 48 ore dalla chiusura del ticket.

                GESTIONE RECLAMI FORMALI
                I reclami formali (comunicazioni via PEC o raccomandata) devono essere
                inoltrati entro 24 ore all'Ufficio Legale (legal@datapulse.it) che gestisce
                la risposta ufficiale entro i termini di legge.
                """,
    },
    {
        "doc_id": "GUIDA-002",
        "titolo": "Guida al Registro dei Consensi - GDPR Compliance",
        "categoria": "guida",
        "autore": "Ufficio Compliance",
        "data_creazione": "2025-07-01",
        "data_validita": "2026-07-01",
        "testo": """
                GUIDA AL REGISTRO DEI CONSENSI - GDPR COMPLIANCE
                Ufficio Compliance - DataPulse S.p.A.

                SCOPO
                Questa guida descrive come DataPulse raccoglie, registra e gestisce il
                consenso degli utenti ai sensi del GDPR, con riferimento all'Art. 7
                (Condizioni per il consenso) e all'Art. 4 n.11 (Definizione di consenso).

                STRUTTURA DEL REGISTRO
                Per ogni trattamento basato sul consenso il registro include:
                - Identità dell'interessato (anonimizzata per il registro interno)
                - Data e ora di raccolta del consenso
                - Versione dell'informativa privacy al momento del consenso
                - Canale di raccolta (web form, email, in-app)
                - Finalità specifica per cui il consenso è stato dato
                - Stato: attivo / revocato / scaduto

                RACCOLTA DEL CONSENSO
                Il consenso deve essere libero, specifico, informato e inequivocabile.
                Non sono validi:
                - Consensi preselezionati (checkbox già spuntate).
                - Consensi bundled (un solo click per finalità multiple).
                - Consensi come condizione per usare il servizio (salvo eccezioni di legge).

                REVOCA DEL CONSENSO
                La revoca deve essere possibile in qualsiasi momento, con la stessa facilità
                con cui è stato dato. DataPulse mette a disposizione:
                - Pannello privacy nel profilo utente (revoca immediata via UI).
                - Email a privacy@datapulse.it (processata entro 72 ore).
                - Modulo cartaceo per clienti enterprise (processato entro 5 giorni lavorativi).
                Dopo la revoca, il trattamento deve cessare immediatamente. Se non può cessare
                per obblighi di legge, l'interessato deve essere informato.

                RETENTION DEL REGISTRO
                Il registro dei consensi deve essere conservato per 10 anni dalla data di
                raccolta o per tutta la durata del contratto + 5 anni (si applica il termine
                più lungo), come previsto dalla policy di data retention aziendale.
                """,
    },
    {
        "doc_id": "REP-001",
        "titolo": "Report di Progetto - Migrazione Infrastruttura Cloud (Q1 2025)",
        "categoria": "report",
        "autore": "Team Architettura",
        "data_creazione": "2025-03-31",
        "data_validita": None,
        "testo": """
                REPORT DI PROGETTO - MIGRAZIONE INFRASTRUTTURA CLOUD
                Team Architettura - Q1 2025 - DataPulse S.p.A.

                SOMMARIO ESECUTIVO
                La migrazione dell'infrastruttura on-premise verso AWS è stata completata
                in Q1 2025 nei tempi e nel budget previsti. L'uptime dei servizi critici
                durante la migrazione è stato del 99.7%.

                ARCHITETTURA TARGET
                - Compute: EKS (Kubernetes gestito) con auto-scaling su EC2 Spot + On-demand.
                - Database: RDS PostgreSQL Multi-AZ per dati transazionali; DynamoDB per
                  sessioni e cache ad alta velocità.
                - Storage: S3 con lifecycle policies per tier automatico (Standard → IA → Glacier).
                - Networking: VPC con subnet private/public, Transit Gateway per connettività
                  multi-account, Direct Connect per collegamento con data center legacy.
                - Sicurezza: AWS IAM con least-privilege, KMS per cifratura dati a riposo,
                  GuardDuty per threat detection, CloudTrail per audit log.

                DATI DI PERFORMANCE POST-MIGRAZIONE
                - Latenza media API: ridotta da 210ms a 85ms (-60%).
                - Costi infrastruttura: riduzione del 35% rispetto al precedente on-premise.
                - Scalabilità: capacità di gestire picchi 10x senza intervento manuale.

                LESSONS LEARNED
                - La fase di data migration ha richiesto 2 settimane extra per allineamento
                  degli schemi tra il legacy DB e RDS. Raccomandazione: dedicare più tempo
                  al mapping schema in fase di pianificazione.
                - L'uso di Spot Instances ha ridotto i costi del 40% sul compute, ma richiede
                  gestione dei preemption con retry logic nel codice applicativo.
                - CloudTrail è stato fondamentale per l'audit di conformità post-migrazione
                  richiesto dall'Ufficio Compliance.

                PROSSIMI STEP
                - Q2 2025: implementazione del disaster recovery multi-regione.
                - Q3 2025: integrazione di AWS Security Hub per centralizzazione degli alert.
                - Q4 2025: ottimizzazione dei costi con Savings Plans e Reserved Instances.
                """,
    },
]


# ==============================================================================
# STRUTTURE DATI
# ==============================================================================


@dataclass
class Documento:
    """Rappresenta un singolo chunk di documento dopo l'ingestion."""

    chunk_id: str  # es. "POL-001_chunk000" - identificatore univoco del chunk
    doc_id: str  # ID del documento sorgente (per citazioni e de-dup)
    titolo: str
    categoria: str
    autore: str
    data_creazione: str
    data_validita: Optional[str]
    testo: str  # testo del chunk (usato per indicizzazione e retrieval)
    testo_originale: (
        str  # testo completo del documento (per assemblare il contesto LLM)
    )


@dataclass
class RisultatoRetrieval:
    """Singolo risultato di retrieval con score aggregato e breakdown dei segnali."""

    documento: Documento
    score_ibrido: float  # score finale normalizzato [0, 1]
    score_semantico: float  # contributo dalla similarità vettoriale
    score_bm25: float  # contributo dalla ricerca BM25
    rank: int  # posizione nella lista ordinata (1-indexed)


@dataclass
class RispostaRAG:
    """Risposta completa del sistema RAG pronta per essere restituita all'utente."""

    query: str
    risposta: str
    fonti: list[RisultatoRetrieval]
    confidenza: float  # media score ibridi top-k: proxy della qualità del retrieval
    timestamp_risposta: str
    latenza_retrieval_ms: float
    latenza_llm_ms: float


# ==============================================================================
# COMPONENTE 1: DOCUMENT PROCESSOR
# ==============================================================================


class DocumentProcessor:
    """
    Responsabile dell'ingestion e del chunking dei documenti.

    Perché il chunking è necessario:
    - I modelli di embedding (e gli LLM) hanno una finestra di contesto
      limitata (~512 token per sentence-transformers). Documenti
      lunghi devono essere divisi per poter essere codificati in singoli vettori coerenti.
    - Chunk più piccoli aumentano la granularità del retrieval: si isola la sezione rilevante senza
      trascinare testo irrilevante nel contesto dell'LLM.
    - Il parametro `overlap` garantisce che le informazioni a cavallo di due chunk consecutivi non vengano perse.

    Strategia di chunking scelta: divisione per paragrafi (doppio newline) con aggregazione fino alla dimensione target.
    Questo approccio rispetta le unità semantiche naturali del testo meglio di un semplice split su caratteri.

    Parametri di default:
    - dimensione_chunk=500 caratteri ≈ 3-5 frasi in italiano. Sufficiente per
      un'unità semantica coerente; abbastanza piccolo per la finestra di encoding.
    - overlap=100 caratteri: circa il 20% della dimensione chunk, valore
      comunemente usato.
    """

    def __init__(self, dimensione_chunk: int = 500, overlap: int = 100):
        self.dimensione_chunk = dimensione_chunk
        self.overlap = overlap

    def processa_knowledge_base(self, kb: list[dict]) -> list[Documento]:
        """Processa l'intera knowledge base e restituisce la lista flat di chunk."""
        documenti = []
        for entry in kb:
            testo_pulito = entry["testo"].strip()
            chunks = self._chunking(testo_pulito)
            for i, chunk in enumerate(chunks):
                documenti.append(
                    Documento(
                        chunk_id=f"{entry['doc_id']}_chunk{i:03d}",
                        doc_id=entry["doc_id"],
                        titolo=entry["titolo"],
                        categoria=entry["categoria"],
                        autore=entry["autore"],
                        data_creazione=entry["data_creazione"],
                        data_validita=entry["data_validita"],
                        testo=chunk,
                        testo_originale=testo_pulito,
                    )
                )
        return documenti

    def _chunking(self, testo: str) -> list[str]:
        """
        Divide il testo in chunk con overlap basandosi sui confini di paragrafo.
        Quando un paragrafo da solo supera la dimensione target, viene incluso
        come chunk autonomo per preservare la coerenza semantica.
        """
        paragrafi = [p.strip() for p in re.split(r"\n\n+", testo) if p.strip()]
        chunks: list[str] = []
        chunk_corrente = ""

        for paragrafo in paragrafi:
            if len(chunk_corrente) + len(paragrafo) + 2 <= self.dimensione_chunk:
                chunk_corrente = (chunk_corrente + "\n\n" + paragrafo).strip()
            else:
                if chunk_corrente:
                    chunks.append(chunk_corrente)
                # Overlap: si trascina la coda del chunk precedente per mantenere
                # continuità semantica tra chunk adiacenti.
                coda = (
                    chunk_corrente[-self.overlap :]
                    if self.overlap < len(chunk_corrente)
                    else chunk_corrente
                )
                chunk_corrente = (coda + "\n\n" + paragrafo).strip()

        if chunk_corrente:
            chunks.append(chunk_corrente)

        return chunks if chunks else [testo]


# ==============================================================================
# COMPONENTE 2: MOTORE DI EMBEDDING
# ==============================================================================


class EmbeddingEngine:
    """
    Wrapper attorno a SentenceTransformers per la generazione di embedding.

    Modello scelto: paraphrase-multilingual-MiniLM-L12-v2
    - Supporto nativo per l'italiano (e 50+ lingue): requisito fondamentale
      per una knowledge base redatta in italiano.
    - Setup rapido, adatto al contesto didattico/demo senza GPU dedicata.
    - Ottimizzato per paraphrase similarity: cattura le relazioni semantiche
      di riformulazione meglio dei modelli generalisti solo-inglese.
    """

    MODELLO_DEFAULT = "paraphrase-multilingual-MiniLM-L12-v2"

    def __init__(self, nome_modello: str = MODELLO_DEFAULT):
        print(f"[EmbeddingEngine] Caricamento modello: {nome_modello}")
        self.modello = SentenceTransformer(nome_modello)
        self.nome_modello = nome_modello

    def codifica(self, testi: list[str]) -> np.ndarray:
        """Restituisce matrice (N, D) con gli embedding del batch di testi."""
        return self.modello.encode(
            testi, convert_to_numpy=True, show_progress_bar=False
        )

    def codifica_query(self, query: str) -> np.ndarray:
        """Codifica una singola query; restituisce vettore 1D (D,)."""
        return self.modello.encode([query], convert_to_numpy=True)[0]


# ==============================================================================
# COMPONENTE 3: VECTOR STORE (ChromaDB)
# ==============================================================================


class VectorStore:
    """
    Indice vettoriale basato su ChromaDB per il retrieval semantico.

    Scelta di ChromaDB:
    - API più semplice rispetto a FAISS (nessuna compilazione C++).
    - Supporto nativo per metadati filtrabili per categoria, data, autore.
    - Storage in-memory per demo; basta passare a
      chromadb.PersistentClient()per rendere l'indice persistente tra esecuzioni.

    Metrica coseno:
    Misura la similarità direzionale tra vettori, invariante rispetto alla magnitudine.
    È la scelta standard per embedding di testo perché la norma del vettore non porta informazione semantica rilevante.

    ChromaDB con metrica coseno restituisce distanze nell'intervallo [0, 2]
    (0 = vettori identici, 2 = vettori diametralmente opposti).
    Convertiamo in score di similarità: score = max(0, 1 - distance).

    Nota sull'embedding: pre-calcoliamo gli embedding con EmbeddingEngine e li
    passiamo esplicitamente a ChromaDB. Questo evita il doppio caricamento del
    modello e offre pieno controllo sul processo di encoding.
    """

    _NOME_COLLECTION = "datapulse_kb"

    def __init__(self, embedding_engine: EmbeddingEngine):
        self.embedding_engine = embedding_engine
        # EphemeralClient (ChromaDB >= 0.4) crea un client in-memory che non
        # richiede un server separato. Fallback a chromadb.Client() per versioni
        # precedenti.
        try:
            self.client = chromadb.EphemeralClient()
        except AttributeError:
            self.client = chromadb.Client()

        self.collection = self.client.create_collection(
            name=self._NOME_COLLECTION,
            metadata={"hnsw:space": "cosine"},
        )

    def indicizza(self, documenti: list[Documento]) -> None:
        """Inserisce i chunk nel vector store con i rispettivi embedding e metadati."""
        ids = [doc.chunk_id for doc in documenti]
        testi = [doc.testo for doc in documenti]
        # Pre-calcolo in batch: più efficiente di un encoding per chunk
        embeddings = self.embedding_engine.codifica(testi).tolist()
        metadati = [
            {
                "doc_id": doc.doc_id,
                "titolo": doc.titolo,
                "categoria": doc.categoria,
                "autore": doc.autore,
                "data_creazione": doc.data_creazione,
                "data_validita": doc.data_validita or "N/A",
            }
            for doc in documenti
        ]
        self.collection.add(
            documents=testi, embeddings=embeddings, metadatas=metadati, ids=ids
        )
        print(f"[VectorStore] Indicizzati {len(ids)} chunk.")

    def cerca(self, query: str, top_k: int = 5) -> list[tuple[str, float, dict]]:
        """
        Ricerca semantica. Restituisce lista di (chunk_id, score_similarità, metadati).
        score_similarità è normalizzato in [0, 1]: 1 = massima similarità.
        """
        n = min(top_k, self.collection.count())
        if n == 0:
            return []
        query_emb = self.embedding_engine.codifica_query(query).tolist()
        risultati = self.collection.query(
            query_embeddings=[query_emb],
            n_results=n,
            include=["documents", "metadatas", "distances"],
        )
        output = []
        for chunk_id, distance, meta in zip(
            risultati["ids"][0],
            risultati["distances"][0],
            risultati["metadatas"][0],
        ):
            score = max(0.0, 1.0 - distance)
            output.append((chunk_id, score, meta))
        return output


# ==============================================================================
# COMPONENTE 4: MOTORE BM25
# ==============================================================================


class BM25Engine:
    """
    Motore di ricerca lessicale basato su BM25Okapi.

    Perché BM25 in aggiunta agli embedding semantici:
    - Gli embedding catturano bene il significato ma sono poco affidabili con
      termini tecnici rari, acronimi e codici (es. "RDA-01", "DORA", "IRP-003",
      "POL-001"): questi token mancano spesso dal vocabolario del modello e
      vengono proiettati in regioni dello spazio vettoriale poco distinguibili.
    - BM25 è term-frequency based: individua con precisione documenti che
      contengono esattamente i termini della query, anche senza contesto semantico.
    - La combinazione ibrida (semantico + BM25) è lo stato dell'arte nei
      sistemi RAG su knowledge base tecnico-operative (vedi BEIR benchmark):
      riduce i falsi negativi di entrambe le strategie in isolamento.

    BM25Okapi è la variante standard:
    - k1=1.5 (default): bilancia l'influenza della frequenza del termine.
    - b=0.75 (default): normalizzazione per la lunghezza del documento.
    Questi iperparametri sono empiricamente validati su molti corpora tecnici
    (Robertson et al. 1994, Robertson & Zaragoza 2009).
    """

    def __init__(self):
        self.indice: Optional[BM25Okapi] = None
        self.documenti: list[Documento] = []

    def indicizza(self, documenti: list[Documento]) -> None:
        """Costruisce l'indice BM25 sul corpus dei chunk."""
        self.documenti = documenti
        corpus_tokenizzato = [self._tokenizza(doc.testo) for doc in documenti]
        self.indice = BM25Okapi(corpus_tokenizzato)
        print(f"[BM25Engine] Indicizzati {len(documenti)} chunk.")

    def cerca(self, query: str, top_k: int = 5) -> list[tuple[int, float]]:
        """
        Ricerca BM25. Restituisce lista di (indice_nel_corpus, score_normalizzato).
        Lo score BM25 grezzo viene normalizzato in [0, 1] con min-max per
        renderlo comparabile con lo score semantico nella fusione ibrida.
        """
        scores = self.indice.get_scores(self._tokenizza(query))
        s_max, s_min = scores.max(), scores.min()
        # Normalizzazione: gestione del caso degenere in cui tutti gli score sono
        # identici (di solito tutti zero = nessun termine della query nel corpus).
        if s_max - s_min > 1e-10:
            scores_norm = (scores - s_min) / (s_max - s_min)
        else:
            scores_norm = np.zeros_like(scores)
        top_indici = np.argsort(scores_norm)[::-1][:top_k]
        return [(int(i), float(scores_norm[i])) for i in top_indici]

    @staticmethod
    def _tokenizza(testo: str) -> list[str]:
        """
        Tokenizzazione semplice: lowercase + estrazione di token alfanumerici.
        Non si usa stemming o lemmatization per mantenere la dipendenza zero da
        librerie NLP italiane (spaCy, NLTK).
        """
        return re.findall(r"\b[a-zA-ZÀ-ÿ0-9]+\b", testo.lower())


# ==============================================================================
# COMPONENTE 5: RETRIEVER IBRIDO
# ==============================================================================


class HybridRetriever:
    """
    Combina retrieval semantico (VectorStore) e lessicale (BM25Engine).

    Formula di fusione lineare pesata:
        score_ibrido = alpha * score_semantico + (1 - alpha) * score_bm25

    Scelta dell'alpha = 0.6 (sbilanciato verso il semantico):
    - Per query in linguaggio naturale, la comprensione semantica è più
      informativa della corrispondenza esatta dei termini.
    - alpha > 0.5 favorisce il semantico, utile per query riformulate rispetto
      al testo dei documenti (es. "normative da rispettare" vs. "GDPR").
    - Il contributo BM25 (0.4) rimane sufficiente per far emergere documenti
      con codici tecnici esatti quando presenti nella query.

    Alternativa considerata: Reciprocal Rank Fusion (RRF).
    RRF è più robusta alla scala assoluta degli score (non richiede
    normalizzazione), ma è meno interpretabile per un progetto didattico.
    La fusione lineare è preferita per trasparenza e controllabilità.

    De-duplicazione: se lo stesso chunk appare nei risultati di entrambe le
    strategie, si aggregano i rispettivi score (il secondo passaggio aggiorna
    il valore, quello mancante rimane a 0.0). Questo evita il double-counting.
    """

    def __init__(
        self,
        vector_store: VectorStore,
        bm25_engine: BM25Engine,
        documenti: list[Documento],
        alpha: float = 0.6,
    ):
        self.vector_store = vector_store
        self.bm25_engine = bm25_engine
        self.documenti = documenti
        self.alpha = alpha
        # Dizionario chunk_id -> Documento per lookup O(1) durante la fusione
        self._id_a_doc: dict[str, Documento] = {doc.chunk_id: doc for doc in documenti}

    def recupera(self, query: str, top_k: int = 5) -> list[RisultatoRetrieval]:
        """
        Esegue il retrieval ibrido e restituisce i top_k risultati ordinati.

        Il pool di candidati è 2 * top_k per dare al BM25 la possibilità di
        far emergere documenti poco rilevanti semanticamente ma con corrispondenza
        lessicale precisa, e viceversa.
        """
        pool = top_k * 2

        # Raccolta candidati dai due indici
        candidati_sem = self.vector_store.cerca(query, top_k=pool)
        candidati_bm25 = self.bm25_engine.cerca(query, top_k=pool)

        # Aggregazione degli score su un dizionario keyed su chunk_id
        scores: dict[str, dict] = {}

        for chunk_id, score_sem, _ in candidati_sem:
            scores[chunk_id] = {"score_semantico": score_sem, "score_bm25": 0.0}

        for idx, score_bm25 in candidati_bm25:
            chunk_id = self.documenti[idx].chunk_id
            if chunk_id in scores:
                scores[chunk_id]["score_bm25"] = score_bm25
            else:
                scores[chunk_id] = {"score_semantico": 0.0, "score_bm25": score_bm25}

        # Calcolo score ibrido, filtraggio dei chunk non mappati, ordinamento
        risultati: list[RisultatoRetrieval] = []
        for chunk_id, dati in scores.items():
            if chunk_id not in self._id_a_doc:
                continue
            score_ibrido = (
                self.alpha * dati["score_semantico"]
                + (1 - self.alpha) * dati["score_bm25"]
            )
            risultati.append(
                RisultatoRetrieval(
                    documento=self._id_a_doc[chunk_id],
                    score_ibrido=score_ibrido,
                    score_semantico=dati["score_semantico"],
                    score_bm25=dati["score_bm25"],
                    rank=0,
                )
            )

        risultati.sort(key=lambda r: r.score_ibrido, reverse=True)
        for i, r in enumerate(risultati[:top_k]):
            r.rank = i + 1

        return risultati[:top_k]


# ==============================================================================
# COMPONENTE 6: PIPELINE LLM
# ==============================================================================


class LLMPipeline:
    """
    Interfaccia unificata verso due provider LLM: Ollama e OpenAI.

    Il parametro `provider` seleziona il backend al momento dell'istanziazione;
    il resto del sistema (RAGSystem, prompt, output) rimane identico nei due casi.

    OLLAMA (provider="ollama")
    - Esecuzione completamente locale: nessun dato trasmesso a provider esterni.
      La scelta più sicura per una knowledge base soggetta a specifiche normative di protezione dei dati.
    - Modello default: llama3.2 (3B parametri) - buon equilibrio tra qualità
      e latenza su hardware consumer.
    - Dipendenza: langchain-ollama. Nessuna chiave API richiesta.

    OPENAI (provider="openai")
    - Qualità generativa superiore, latenza ridotta rispetto ai modelli locali.
    - Modello default: gpt-4o-mini - ottimo rapporto qualità/costo per RAG.
    - Dipendenza: langchain-openai.
    - Chiave API letta dalla variabile d'ambiente OPENAI_API_KEY (non inserire
      mai nel codice per rispettare le best practice di sicurezza).
    - Attenzione: il contesto dei documenti viene trasmesso ai server OpenAI.
      In produzione necessario valutare i termini di servizio rispetto ai dati aziendali.

    temperature=0.1 su entrambi i provider:
    Risposte quasi deterministiche. Per un assistente aziendale la
    riproducibilità è più importante della varietà creativa.

    Struttura del prompt (pattern system/context/question/instructions):
    - Ruolo sistema: vincola l'LLM a rispondere solo sul contesto fornito.
    - Contesto: documenti recuperati con metadati identificativi.
    - Domanda: la query originale dell'utente, non riformulata.
    - Istruzioni di output: struttura, obbligo di citazione, gestione
      del caso "informazione non disponibile".
    Questo schema riduce le allucinazioni ancorando la generazione alle fonti
    reali e richiedendo all'LLM di segnalare esplicitamente le lacune.
    """

    PROVIDER_OLLAMA = "ollama"
    PROVIDER_OPENAI = "openai"

    _MODELLI_DEFAULT = {
        PROVIDER_OLLAMA: "llama3.2",
        PROVIDER_OPENAI: "gpt-4o-mini",
    }

    def __init__(self, provider: str = PROVIDER_OLLAMA, modello: Optional[str] = None):
        self.provider = provider
        self.modello_nome = modello or self._MODELLI_DEFAULT.get(provider, "")

        if provider == self.PROVIDER_OLLAMA:
            self._init_ollama()
        elif provider == self.PROVIDER_OPENAI:
            self._init_openai()
        else:
            raise ValueError(
                f"Provider non supportato: '{provider}'. "
                f"Valori ammessi: ollama, openai."
            )

    def _init_ollama(self) -> None:
        from langchain_ollama import OllamaLLM

        self.llm = OllamaLLM(model=self.modello_nome, temperature=0.1)

    def _init_openai(self) -> None:
        from langchain_openai import ChatOpenAI

        chiave = os.environ.get("OPENAI_API_KEY")
        if not chiave:
            raise EnvironmentError(
                "Variabile d'ambiente OPENAI_API_KEY non impostata.\n"
                "Eseguire: export OPENAI_API_KEY='sk-...'"
            )
        # ChatOpenAI restituisce un oggetto AIMessage; genera() lo gestisce.
        self.llm = ChatOpenAI(model=self.modello_nome, temperature=0.1, api_key=chiave)

    def genera(self, query: str, contesto: str, fonti_meta: list[dict]) -> str:
        """Genera la risposta sintetica dato il contesto recuperato."""
        prompt = self._costruisci_prompt(query, contesto, fonti_meta)
        risposta = self.llm.invoke(prompt)
        # ChatOpenAI restituisce AIMessage con attributo .content;
        # OllamaLLM restituisce direttamente una stringa.
        return risposta.content if hasattr(risposta, "content") else str(risposta)

    def _costruisci_prompt(
        self, query: str, contesto: str, fonti_meta: list[dict]
    ) -> str:
        """Assembla il prompt con separazione netta tra sistema, contesto e domanda."""
        lista_fonti = "\n".join(
            f"  [{m['doc_id']}] {m['titolo']} "
            f"(categoria: {m['categoria']}, autore: {m['autore']}, "
            f"data: {m['data_creazione']}, validità: {m.get('data_validita') or 'senza scadenza'})"
            for m in fonti_meta
        )
        return f"""
                    Sei l'assistente di knowledge management di DataPulse S.p.A.
                    Rispondi ESCLUSIVAMENTE sulla base dei documenti aziendali forniti nel contesto.
                    Se le informazioni necessarie non sono presenti, rispondi: "Le informazioni richieste
                    non sono disponibili nella knowledge base attuale." Non inventare procedure o normative.

                    DOCUMENTI DISPONIBILI:
                    {lista_fonti}

                    CONTESTO ESTRATTO:
                    {contesto}

                    DOMANDA:
                    {query}

                    ISTRUZIONI:
                    1. Fornisci una risposta sintetica e strutturata con i punti chiave.
                    2. Cita i documenti usati (es. "secondo POL-001...").
                    3. Se la procedura ha passaggi sequenziali, numerali.
                    4. Al termine, indica la data di validità delle fonti citate se presente.

                    RISPOSTA:
                """


# ==============================================================================
# COMPONENTE 7: SISTEMA RAG - ORCHESTRATORE
# ==============================================================================


class RAGSystem:
    """
    Orchestratore che coordina tutti i componenti del sistema RAG.

    Flusso di esecuzione per una query:
    1. HybridRetriever.recupera() → top-k RisultatoRetrieval
    2. De-duplicazione per doc_id: se più chunk dello stesso documento sono
        stati recuperati, si usa il testo originale completo una sola volta.
        Motivazione: presentare all'LLM frammenti dello stesso documento
        separati aumenta la ridondanza e riduce lo spazio disponibile per
        altri documenti rilevanti.
    3. Assemblaggio del contesto: testi originali con separatori identificativi.
    4. LLMPipeline.genera() -> stringa risposta.
    5. Costruzione di RispostaRAG con metriche e metadati delle fonti.

    Calcolo della confidenza:
    Usiamo la media degli score ibridi dei top-k risultati come proxy della
    qualità del retrieval.
    - Alta confidenza -> il corpus contiene documenti molto pertinenti alla query
      -> risposta probabilmente completa e accurata.
    - Bassa confidenza -> il retrieval è debole
      -> la risposta potrebbe essere incompleta o basata su documenti marginali.
    Limitazione: è un proxy indiretto; non misura la correttezza della risposta
    generata dall'LLM. In produzione si aggiungerebbe un layer di valutazione
    separato (es. LLM-as-judge, RAGAS).
    """

    def __init__(
        self,
        top_k: int = 4,
        alpha: float = 0.6,
        usa_llm: bool = True,
        provider: str = LLMPipeline.PROVIDER_OLLAMA,
        modello_llm: Optional[str] = None,
    ):
        self.top_k = top_k
        self.usa_llm = usa_llm

        print("\n[RAGSystem] Inizializzazione in corso...")

        self.processor = DocumentProcessor()
        self.embedding_engine = EmbeddingEngine()
        self.bm25_engine = BM25Engine()

        self.documenti = self.processor.processa_knowledge_base(KNOWLEDGE_BASE)
        n_sorgenti = len(KNOWLEDGE_BASE)
        n_chunk = len(self.documenti)
        print(
            f"[RAGSystem] {n_sorgenti} documenti → {n_chunk} chunk (avg {n_chunk // n_sorgenti} chunk/doc)."
        )

        self.vector_store = VectorStore(self.embedding_engine)
        self.vector_store.indicizza(self.documenti)
        self.bm25_engine.indicizza(self.documenti)

        self.retriever = HybridRetriever(
            self.vector_store, self.bm25_engine, self.documenti, alpha=alpha
        )

        self.llm_pipeline: Optional[LLMPipeline] = None
        if self.usa_llm:
            try:
                self.llm_pipeline = LLMPipeline(provider=provider, modello=modello_llm)
                nome_mod = self.llm_pipeline.modello_nome
                print(f"[RAGSystem] LLM pronto: {nome_mod} (provider: {provider})")
            except Exception as exc:
                print(
                    f"[RAGSystem] LLM non disponibile ({exc}). Modalità retrieval-only attiva."
                )
                self.usa_llm = False
        else:
            print("[RAGSystem] Modalità retrieval-only (LLM disabilitato).")

        print("[RAGSystem] Sistema pronto.\n")

    def interroga(self, query: str) -> RispostaRAG:
        """Esegue la pipeline RAG completa per una query in linguaggio naturale."""
        ts_inizio = time.perf_counter()

        risultati = self.retriever.recupera(query, top_k=self.top_k)
        latenza_retrieval_ms = (time.perf_counter() - ts_inizio) * 1000

        # Score di confidenza: media degli score ibridi top-k
        confidenza = (
            float(np.mean([r.score_ibrido for r in risultati])) if risultati else 0.0
        )

        # De-duplicazione per doc_id: si usa il testo originale del documento
        # per dare all'LLM il massimo contesto disponibile per ogni fonte citata.
        doc_ids_visti: set[str] = set()
        parti_contesto: list[str] = []
        fonti_meta: list[dict] = []

        for r in risultati:
            doc = r.documento
            if doc.doc_id in doc_ids_visti:
                continue
            doc_ids_visti.add(doc.doc_id)
            parti_contesto.append(
                f"[{doc.doc_id}] {doc.titolo}\n{'─' * 60}\n{doc.testo_originale}"
            )
            fonti_meta.append(
                {
                    "doc_id": doc.doc_id,
                    "titolo": doc.titolo,
                    "categoria": doc.categoria,
                    "autore": doc.autore,
                    "data_creazione": doc.data_creazione,
                    "data_validita": doc.data_validita,
                }
            )

        contesto = "\n\n".join(parti_contesto)

        ts_pre_llm = time.perf_counter()

        if self.usa_llm and self.llm_pipeline and risultati:
            try:
                testo_risposta = self.llm_pipeline.genera(query, contesto, fonti_meta)
            except Exception as exc:
                testo_risposta = (
                    f"[Errore LLM: {exc}]\n\n"
                    "Documenti pertinenti trovati (retrieval-only):\n"
                    + "\n".join(
                        f"  [{r.documento.doc_id}] {r.documento.titolo} (score: {r.score_ibrido:.3f})"
                        for r in risultati
                    )
                )
        elif not risultati:
            testo_risposta = "Nessun documento pertinente trovato nella knowledge base."
        else:
            testo_risposta = self._risposta_retrieval_only(query, risultati)

        latenza_llm_ms = (time.perf_counter() - ts_pre_llm) * 1000

        return RispostaRAG(
            query=query,
            risposta=testo_risposta,
            fonti=risultati,
            confidenza=confidenza,
            timestamp_risposta=datetime.now().isoformat(timespec="seconds"),
            latenza_retrieval_ms=latenza_retrieval_ms,
            latenza_llm_ms=latenza_llm_ms,
        )

    @staticmethod
    def _risposta_retrieval_only(
        query: str, risultati: list[RisultatoRetrieval]
    ) -> str:
        """
        Fallback testuale quando l'LLM non è disponibile.
        Restituisce gli estratti più rilevanti senza sintesi generativa.
        """
        righe = [f"Query: {query}\n\nEstratti più rilevanti dalla knowledge base:\n"]
        for r in risultati:
            doc = r.documento
            righe.append(
                f"\n[{doc.doc_id}] {doc.titolo} (score: {r.score_ibrido:.3f})\n"
            )
            righe.append(textwrap.fill(doc.testo[:500], width=80) + "\n[...]")
        return "\n".join(righe)


# ==============================================================================
# PRESENTAZIONE RISULTATI
# ==============================================================================


def stampa_risposta(risposta: RispostaRAG, larghezza: int = 80) -> None:
    """Stampa la risposta RAG in formato leggibile a schermo."""
    sep = "=" * larghezza
    sep_lieve = "-" * larghezza

    print(f"\n{sep}")
    print(f"QUERY: {risposta.query}")
    print(sep)

    livello = (
        "ALTA"
        if risposta.confidenza >= 0.6
        else "MEDIA" if risposta.confidenza >= 0.3 else "BASSA"
    )
    print(
        f"Confidenza: {risposta.confidenza:.2%} [{livello}]  |  "
        f"Retrieval: {risposta.latenza_retrieval_ms:.0f}ms  |  "
        f"LLM: {risposta.latenza_llm_ms:.0f}ms  |  "
        f"Timestamp: {risposta.timestamp_risposta}"
    )
    print(sep_lieve)
    print("RISPOSTA:\n")
    # Preserva i newline intenzionali (es. elenchi numerati dall'LLM),
    # ma applica word-wrap alle righe lunghe per leggibilità su terminale.
    for riga in risposta.risposta.split("\n"):
        print(textwrap.fill(riga, width=larghezza) if len(riga) > larghezza else riga)

    print(f"\n{sep_lieve}")
    print("FONTI UTILIZZATE:")

    # De-duplicazione nella stampa: mostra ogni documento sorgente una volta
    # anche se contribuisce con più chunk al retrieval.
    doc_ids_stampati: set[str] = set()
    for r in risposta.fonti:
        if r.documento.doc_id in doc_ids_stampati:
            continue
        doc_ids_stampati.add(r.documento.doc_id)
        validita = r.documento.data_validita or "senza scadenza"
        print(
            f"  [{r.rank}] {r.documento.doc_id} - {r.documento.titolo}\n"
            f"       Categoria: {r.documento.categoria}  |  Autore: {r.documento.autore}\n"
            f"       Creazione: {r.documento.data_creazione}  |  Validità: {validita}\n"
            f"       Score: ibrido={r.score_ibrido:.3f}  "
            f"semantico={r.score_semantico:.3f}  BM25={r.score_bm25:.3f}"
        )
    print(sep)


# ==============================================================================
# SALVATAGGIO OUTPUT
# ==============================================================================


def salva_in_markdown(risposte: list[RispostaRAG], percorso: str) -> None:
    """Serializza una lista di RispostaRAG in un file Markdown."""
    righe = [
        f"# Output RAG - DataPulse S.p.A.",
        f"",
        f"Generato il: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"",
    ]
    for i, r in enumerate(risposte, start=1):
        livello = (
            "ALTA"
            if r.confidenza >= 0.6
            else "MEDIA" if r.confidenza >= 0.3 else "BASSA"
        )
        righe += [
            f"---",
            f"",
            f"## Query {i}",
            f"",
            f"> {r.query}",
            f"",
            f"**Confidenza:** {r.confidenza:.2%} [{livello}] &nbsp;|&nbsp; "
            f"Retrieval: {r.latenza_retrieval_ms:.0f}ms &nbsp;|&nbsp; "
            f"LLM: {r.latenza_llm_ms:.0f}ms &nbsp;|&nbsp; "
            f"Timestamp: {r.timestamp_risposta}",
            f"",
            f"### Risposta",
            f"",
            r.risposta.strip(),
            f"",
            f"### Fonti",
            f"",
            f"| # | Documento | Categoria | Autore | Creazione | Validità | Score ibrido |",
            f"|---|-----------|-----------|--------|-----------|----------|-------------|",
        ]
        doc_ids_visti: set[str] = set()
        for res in r.fonti:
            doc = res.documento
            if doc.doc_id in doc_ids_visti:
                continue
            doc_ids_visti.add(doc.doc_id)
            validita = doc.data_validita or "-"
            righe.append(
                f"| {res.rank} | **{doc.doc_id}** - {doc.titolo} "
                f"| {doc.categoria} | {doc.autore} "
                f"| {doc.data_creazione} | {validita} "
                f"| {res.score_ibrido:.3f} |"
            )
        righe.append("")

    with open(percorso, "w", encoding="utf-8") as f:
        f.write("\n".join(righe))


# ==============================================================================
# MAIN - DEMO E CASI DI TEST
# ==============================================================================


def main() -> None:
    """
    Esegue i test case principali che coprono i requisiti del progetto.

    Query di test selezionate per verificare:
    1. Caso d'uso principale (accesso ai dati, normative GDPR):
       testa il retrieval di POL-001, POL-002, FAQ-001, GUIDA-002.
    2. Gestione data breach: testa il retrieval cross-documento (FAQ-001 + POL-002).
    3. Query con codice documento esplicito (POL-001):
       testa il contributo BM25 che deve far emergere il documento con quel codice esatto.
    4. Informazioni tecniche sull'infrastruttura: testa il retrieval di REP-001,
       documento lontano dal dominio compliance.
    5. Onboarding multi-documento: testa la capacità di aggregare informazioni
       da MAN-001, FAQ-002 e POL-001 in un'unica risposta coerente.

    Selezione del provider LLM:
      - "ollama"  -> locale, nessuna chiave API, richiede Ollama attivo
      - "openai"  -> richiede variabile d'ambiente OPENAI_API_KEY
    Per modalità retrieval-only (senza LLM): impostare usa_llm=False.
    """
    # ── Configurazione provider ────────────────────────────────────────────────
    # Modificare `provider` per scegliere il backend LLM.
    # Il modello può essere sovrascritto con `modello_llm`; se None si usa
    # il default del provider (llama3.2 per Ollama, gpt-4o-mini per OpenAI).
    #
    # Esempi:
    #   RAGSystem(provider="ollama")
    #   RAGSystem(provider="openai")
    #   RAGSystem(provider="openai", modello_llm="gpt-4o")
    #   RAGSystem(usa_llm=False)  ← retrieval-only, nessun LLM
    sistema = RAGSystem(top_k=4, alpha=0.6, usa_llm=True, provider="ollama")

    query_di_test = [
        # Test 1 - caso d'uso principale del progetto
        (
            "Qual è la procedura aggiornata per la richiesta di accesso ai dati "
            "dei clienti e quali normative dobbiamo rispettare?"
        ),
        # Test 2 - gestione incidenti di sicurezza
        ("Cosa devo fare se scopro una violazione dei dati personali (data breach)?"),
        # Test 3 - query con codice documento specifico (segnale BM25)
        ("Cosa prevede la POL-001 riguardo ai livelli di accesso e alle sanzioni?"),
        # Test 4 - recupero informazioni tecniche (fuori dal dominio compliance)
        (
            "Quali sono i risultati della migrazione cloud e qual è "
            "l'architettura AWS attuale di DataPulse?"
        ),
        # Test 5 - aggregazione multi-documento per onboarding
        (
            "Sono un nuovo dipendente: cosa devo fare nella prima settimana "
            "e quali policy devo firmare?"
        ),
    ]

    risposte: list[RispostaRAG] = []
    for query in query_di_test:
        risposta = sistema.interroga(query)
        stampa_risposta(risposta)
        risposte.append(risposta)
        # Pausa minima tra le query per non sovraccaricare l'LLM locale
        time.sleep(1)

    scelta = (
        input("\nVuoi salvare l'output in un file Markdown? [s/N] ").strip().lower()
    )
    if scelta == "s":
        nome_file = f"rag_output_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.md"
        salva_in_markdown(risposte, nome_file)
        print(f"Output salvato in: {nome_file}")
    else:
        print("Output non salvato.")


if __name__ == "__main__":
    main()
