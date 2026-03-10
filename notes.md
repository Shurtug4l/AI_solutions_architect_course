# Application Security – Guida Completa per Preparazione Colloquio Tecnico

Questo documento raccoglie in modo strutturato i concetti fondamentali relativi alla **Application Security**, ai **framework di sicurezza**, agli **strumenti di analisi delle vulnerabilità**, ai **processi Secure Software Development** e alle **normative rilevanti**.  
Include inoltre **esempi di domande tecniche tipiche da colloquio** con spiegazioni ragionate delle risposte.

L'obiettivo è comprendere **come integrare la sicurezza nello sviluppo software moderno**, sia dal punto di vista tecnico sia dal punto di vista di governance e compliance.

---

# 1. Application Security

La **Application Security (AppSec)** riguarda l'insieme delle pratiche, dei processi e delle tecnologie utilizzate per **proteggere le applicazioni software da vulnerabilità e attacchi informatici**.

L'approccio moderno non prevede più che la sicurezza venga verificata solo alla fine dello sviluppo tramite penetration testing, ma che venga **integrata lungo tutto il ciclo di vita del software**.

Questo approccio prende il nome di **Secure Software Development Lifecycle (SSDLC)**.

Il principio fondamentale è che:

> Individuare vulnerabilità nelle prime fasi dello sviluppo è molto meno costoso e più efficace rispetto alla loro correzione dopo il rilascio.

---

# 2. Secure Software Development Lifecycle (SSDLC)

Il Secure Software Development Lifecycle consiste nell'integrare controlli di sicurezza in ogni fase del ciclo di sviluppo software.

Le fasi principali sono:

1. Definizione dei requisiti di sicurezza
2. Progettazione sicura dell'architettura
3. Threat modeling
4. Secure coding
5. Security testing
6. Deployment sicuro
7. Monitoraggio e gestione delle vulnerabilità

L'obiettivo è costruire software **sicuro by design**.

---

# 3. Security Requirements

Durante la fase iniziale del progetto vengono definiti i **requisiti di sicurezza** dell'applicazione.

Questi requisiti stabiliscono quali controlli devono essere implementati per proteggere il sistema.

Esempi di requisiti di sicurezza:

- autenticazione degli utenti
- gestione sicura delle password
- controllo degli accessi
- cifratura dei dati sensibili
- gestione delle sessioni
- logging e monitoraggio delle attività
- protezione contro vulnerabilità comuni

Uno degli standard più utilizzati per definire requisiti di sicurezza applicativa è:

OWASP Application Security Verification Standard (ASVS)

ASVS fornisce una checklist strutturata di controlli di sicurezza organizzati in tre livelli:

Livello 1  
Applicazioni con requisiti di sicurezza base

Livello 2  
Applicazioni aziendali con dati sensibili

Livello 3  
Applicazioni critiche che gestiscono dati altamente sensibili

---

# 4. Progettazione Sicura e Threat Modeling

Uno degli aspetti più importanti della sicurezza applicativa è progettare l'architettura dell'applicazione in modo sicuro.

Il **Threat Modeling** è una metodologia utilizzata per identificare le possibili minacce che potrebbero colpire un sistema.

L'obiettivo è rispondere a tre domande fondamentali:

1. Quali asset devono essere protetti?
2. Quali minacce potrebbero colpire il sistema?
3. Quali controlli di sicurezza devono essere implementati?

Una metodologia molto diffusa è il modello **STRIDE**.

STRIDE classifica le minacce in sei categorie:

Spoofing  
Impersonificazione di un'identità (es. furto di credenziali)

Tampering  
Modifica non autorizzata dei dati

Repudiation  
Possibilità di negare un'azione perché non esistono log adeguati

Information Disclosure  
Esposizione non autorizzata di informazioni sensibili

Denial of Service  
Interruzione del servizio

Elevation of Privilege  
Un utente ottiene privilegi più elevati del consentito

Il processo di threat modeling generalmente segue questi passaggi:

1. Creazione di un diagramma architetturale del sistema
2. Identificazione dei componenti principali
3. Identificazione delle trust boundaries
4. Analisi delle possibili minacce
5. Definizione delle contromisure

Esempi di contromisure:

- autenticazione forte
- validazione degli input
- cifratura dei dati
- rate limiting
- segmentazione della rete

---

# 5. Secure Coding

Il **Secure Coding** consiste nello sviluppare software seguendo pratiche che riducono la probabilità di introdurre vulnerabilità.

Le vulnerabilità più comuni nelle applicazioni web sono raccolte nella **OWASP Top 10**.

Di seguito alcuni esempi.

---

## SQL Injection

La SQL injection si verifica quando un'applicazione inserisce direttamente input utente nelle query SQL.

Esempio vulnerabile:

SELECT * FROM users WHERE username = ‘input_utente’

Un attaccante potrebbe inserire: ’ OR ‘1’=’1

Modificando la query e ottenendo accesso non autorizzato.

Mitigazioni:

- prepared statements
- parameterized queries
- validazione input

---

## Cross-Site Scripting (XSS)

L'XSS si verifica quando un'applicazione restituisce input utente senza sanitizzazione.

Un attaccante può inserire codice JavaScript che verrà eseguito nel browser di altri utenti.

Conseguenze possibili:

- furto dei cookie di sessione
- impersonificazione degli utenti
- manipolazione dei contenuti della pagina

Mitigazioni:

- sanitizzazione input
- encoding output
- Content Security Policy

---

## Broken Authentication

Debolezze nei meccanismi di autenticazione possono consentire accessi non autorizzati.

Mitigazioni:

- multi-factor authentication
- password hashing sicuro
- limitazione dei tentativi di login
- gestione corretta delle sessioni

---

# 6. Security Testing

Per individuare vulnerabilità durante lo sviluppo vengono utilizzati diversi strumenti di analisi automatizzata.

Le principali categorie sono:

- Static Application Security Testing (SAST)
- Dynamic Application Security Testing (DAST)
- Software Composition Analysis (SCA)

Ogni approccio analizza aspetti diversi della sicurezza.

---

# 7. Static Application Security Testing (SAST)

Il **SAST** analizza il codice sorgente dell'applicazione senza eseguirlo.

Il funzionamento prevede:

1. parsing del codice
2. costruzione dell'Abstract Syntax Tree
3. analisi del flusso dei dati
4. individuazione di pattern vulnerabili

Ad esempio:

se input utente arriva direttamente a una query SQL senza sanitizzazione, lo strumento segnala una possibile SQL injection.

Vantaggi:

- identifica vulnerabilità nelle prime fasi dello sviluppo
- facilmente integrabile nelle pipeline CI/CD

Limiti:

- possibile presenza di falsi positivi
- non analizza il comportamento runtime

---

# 8. Dynamic Application Security Testing (DAST)

Il **DAST** analizza l'applicazione mentre è in esecuzione.

Gli strumenti simulano attacchi reali inviando richieste malevole all'applicazione.

Il processo include:

1. scansione dell'applicazione
2. identificazione degli endpoint
3. invio di payload malevoli
4. analisi delle risposte del server

Vantaggi:

- identifica vulnerabilità sfruttabili realmente
- analizza configurazioni runtime

Limiti:

- non ha visibilità sul codice interno
- potrebbe non individuare vulnerabilità logiche

---

# 9. Software Composition Analysis (SCA)

Le applicazioni moderne utilizzano molte librerie open source.

La **Software Composition Analysis** serve a identificare vulnerabilità presenti nelle dipendenze software.

Il processo prevede:

1. scansione delle dipendenze
2. identificazione delle librerie utilizzate
3. confronto con database di vulnerabilità pubbliche

Se viene rilevata una libreria vulnerabile, viene suggerito un aggiornamento.

Gli strumenti SCA generano anche uno **Software Bill of Materials (SBOM)**.

Uno SBOM è un inventario completo dei componenti software utilizzati da un'applicazione.

Questo è fondamentale per la sicurezza della **software supply chain**.

---

# 10. DevSecOps

Il paradigma **DevSecOps** consiste nell'integrare la sicurezza all'interno dei processi DevOps.

Gli strumenti di sicurezza vengono integrati nelle pipeline CI/CD.

Pipeline tipica:

commit del codice  
build dell'applicazione  
test automatici  
analisi SAST  
analisi SCA  
deploy su ambiente di staging  
test DAST  
rilascio in produzione

Questo approccio implementa il concetto di **shift-left security**, cioè anticipare i controlli di sicurezza nelle prime fasi dello sviluppo.

---

# 11. Vulnerability Management

Quando vengono identificate vulnerabilità, l'organizzazione deve gestire il processo di remediation.

Il processo tipico include:

1. raccolta dei risultati delle scansioni
2. analisi dei falsi positivi
3. valutazione del rischio
4. assegnazione delle attività di remediation
5. verifica della correzione

Le vulnerabilità vengono spesso classificate utilizzando il **CVSS (Common Vulnerability Scoring System)**.

Tuttavia la prioritizzazione deve considerare anche:

- criticità del sistema
- esposizione su Internet
- sensibilità dei dati

---

# 12. Attack Surface

La **attack surface** rappresenta l'insieme di tutti i punti attraverso cui un attaccante può interagire con il sistema.

Esempi:

- API
- interfacce web
- servizi esposti
- database
- integrazioni con sistemi esterni

Ridurre la superficie di attacco è una strategia fondamentale.

Tecniche di riduzione includono:

- rimozione di endpoint non necessari
- limitazione dei servizi esposti
- controllo rigoroso degli accessi
- segmentazione della rete
- hardening delle configurazioni

---

# 13. Runtime Security e Observability

Anche applicazioni progettate correttamente possono contenere vulnerabilità sconosciute.

Per questo motivo è necessario monitorare il comportamento delle applicazioni in produzione.

Questo include:

- logging dettagliato
- monitoraggio delle richieste
- rilevamento di anomalie

Una tecnologia utilizzata è il **Runtime Application Self Protection (RASP)**.

I sistemi RASP monitorano il comportamento dell'applicazione e possono bloccare attacchi in tempo reale.

---

# 14. ISO 27001

ISO 27001 è uno standard internazionale per i sistemi di gestione della sicurezza delle informazioni.

Definisce come implementare un **Information Security Management System (ISMS)**.

Include controlli relativi a:

- gestione degli accessi
- gestione degli incidenti
- gestione dei rischi
- sicurezza delle informazioni

La sicurezza applicativa contribuisce alla conformità attraverso:

- secure development practices
- vulnerability management
- report di sicurezza utilizzabili durante gli audit

---

# 15. NIS2

La direttiva NIS2 è una normativa europea che mira a rafforzare la cybersecurity delle infrastrutture critiche.

Richiede alle organizzazioni di implementare:

- gestione del rischio informatico
- gestione delle vulnerabilità
- sicurezza della supply chain
- procedure di incident reporting

Le organizzazioni devono dimostrare di adottare misure adeguate di sicurezza.

---

# 16. DORA

Il Digital Operational Resilience Act riguarda la resilienza operativa digitale del settore finanziario.

Introduce requisiti relativi a:

- gestione del rischio ICT
- resilienza operativa
- gestione dei fornitori tecnologici
- testing della sicurezza

---

# 17. PCI DSS

PCI DSS è lo standard di sicurezza per organizzazioni che gestiscono dati di carte di pagamento.

Richiede:

- cifratura dei dati delle carte
- controlli di accesso rigorosi
- monitoraggio delle attività
- vulnerability scanning e penetration testing

---

# 18. Cultura della Sicurezza nello Sviluppo

La sicurezza applicativa non può essere gestita solo dal team security.

È necessario coinvolgere anche gli sviluppatori.

Le pratiche più efficaci includono:

- linee guida di secure coding
- formazione sulla sicurezza per gli sviluppatori
- integrazione di strumenti di sicurezza negli ambienti di sviluppo

---

# 19. Metriche di Sicurezza

Le organizzazioni monitorano la maturità della sicurezza applicativa tramite KPI come:

- numero di vulnerabilità critiche per release
- tempo medio di remediation
- percentuale di codice analizzato
- numero di incidenti di sicurezza

---

# 20. Esempi di Domande Tecniche da Colloquio

## Come integreresti la sicurezza nel ciclo di sviluppo software?

Risposta attesa:

Implementazione di Secure SDLC con security requirements, threat modeling, secure coding, testing automatico (SAST, DAST, SCA) e vulnerability management.

---

## Qual è la differenza tra SAST e DAST?

SAST analizza il codice staticamente senza eseguire l'applicazione.

DAST analizza l'applicazione mentre è in esecuzione simulando attacchi.

I due approcci sono complementari.

---

## Come gestiresti centinaia di vulnerabilità segnalate da uno scanner?

Processo:

triage  
eliminazione falsi positivi  
prioritizzazione basata su rischio  
assegnazione remediation  
verifica fix

---

## Cos'è la Software Composition Analysis?

Tecnica che identifica vulnerabilità nelle librerie open source utilizzate dall'applicazione.

---

## Come gestiresti il trade-off tra sicurezza e velocità di sviluppo?

Automazione dei controlli di sicurezza nelle pipeline CI/CD tramite approccio DevSecOps.

---

## Quali sono le principali sfide nell'implementare un programma di Application Security?

- integrazione con processi DevOps
- complessità delle architetture moderne
- cultura della sicurezza nei team di sviluppo

---
