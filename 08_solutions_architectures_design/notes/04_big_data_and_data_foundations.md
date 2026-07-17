# Big Data and data foundations

## TL;DR

Data is the fuel of every AI solution, and this note lays the module's foundation layer. **Big Data** is not "a lot of data": it is an ecosystem of information whose **scale, velocity, and complexity exceed traditional tools**, a definition that is relative to its era rather than tied to a byte count. It is characterised by the **5 V**: Volume, Velocity, Variety, **Veracity**, and **Value**, with the last two being the AI-critical pair. Data comes in three shapes: **structured** (predefined data model, rows and columns, SQL), **semi-structured** (self-describing, JSON/XML/HTML, no rigid schema), and **unstructured** (text, audio, video: roughly **80% of all existing data**, and the raw material of modern generative AI). **Data mining** is the extraction of useful, possibly unexpected patterns from very large collections; **text mining** is its subfield for text, where most enterprise information actually lives. On storage, the **Data Warehouse** (schema-on-write, ETL, certified BI) and the **Data Lake** (schema-on-read, ELT, raw data for ML) feed different workloads, and running both creates the **two-tier architecture** problem: duplicated cost, fragile ETL, data drift. The **Lakehouse** dissolves that dilemma with a transactional metadata layer (Delta Lake, Iceberg, Hudi) that brings **ACID transactions, open formats, and time travel** to lake economics. The architectural takeaway: warehouse feeds BI, lake feeds ML, lakehouse feeds both from a single copy of the data.

## Cheatsheet

| Concept | One-line | Practical signal |
|---|---|---|
| **Big Data** | Information ecosystem beyond traditional tools' scale, velocity, complexity | Relative to the era's tooling, not an absolute size |
| **5 V** | Volume, Velocity, Variety, Veracity, Value | Veracity and Value are the AI-critical pair |
| **Structured data** | Predefined data model, rows and columns | SQL tables: forms, POS transactions, sensor logs |
| **Semi-structured data** | Self-describing, no rigid schema, hierarchical | JSON, XML, HTML, email, NoSQL stores |
| **Unstructured data** | No schema, no SQL query | ~80% of all data: text, audio, video, images |
| **Data mining** | Extract useful, possibly unexpected patterns at scale | "Tell me something I don't know", not record lookup |
| **Text mining** | Data mining subfield for unstructured text | Emails, reviews, support tickets, reports |
| **ETL vs ELT** | Transform before load vs load raw, transform on demand | Warehouse paradigm vs lake paradigm |
| **Data virtualization** | Query-driven warehouse, no physical copy | Middleware fans the query out to live sources |
| **Two-tier architecture** | Lake for ML plus warehouse for BI, side by side | Double cost, fragile ETL, data drift |
| **Lakehouse layer** | ACID + open formats + time travel on lake storage | Delta Lake, Apache Iceberg, Apache Hudi |

## Sixty years of data management, compressed

Each decade's technology answered the previous decade's overflow:

- **1960s**: flat files, early data collection, network DBMS.
- **1970s**: the relational model and the first relational DBMS.
- **1980s**: mature RDBMS, advanced data models, application-oriented DBMS (spatial, scientific).
- **1990s**: **data mining and data warehousing** appear, plus multimedia and web databases.
- **2000s**: streaming data management and mining, XML, data integration.
- **2010s**: **Big Data and NoSQL**.

The pattern worth keeping: data mining and the warehouse were born together in the 1990s, when volume first outran the ability to extract information by hand. Big Data and NoSQL arrived when volume and variety outran the relational model itself. Storage technology has always been a reaction to data pressure, never the other way around.

## Big Data: a moving target, not a size

> Big Data is an ecosystem of information whose scale, velocity, and complexity exceed the capacity of traditional tools.

The definition is deliberately relative. There is no fixed threshold in terabytes past which data becomes "big": every era has had datasets that overwhelmed the tools of its time. What makes data "big" is the mismatch between the information ecosystem and the processing methods available, which is why the concept has no fixed historical placement.

The five characteristics:

- **Volume**: sheer scale (terabytes, petabytes, exabytes).
- **Velocity**: speed of generation and analysis (streaming, real time).
- **Variety**: the different shapes data takes (structured, unstructured, and everything between).
- **Veracity**: reliability and quality. Dirty data produces dirty results.
- **Value**: the end goal, the strategic insight extractable from the data.

For AI work the last two dominate. Veracity is "garbage in, garbage out" made explicit: a model trained on wrong or inaccurate data does not just report the noise, it learns it. And Value is a reminder that data has no intrinsic worth; value emerges only when new information is extracted and a decision is made on it. The first three V justify the infrastructure; the last two justify the project.

## The three shapes of data

### Structured

Structured does not just mean "fixed length": it means the data has a **predefined data model**. Rigid containers, tables with rows and columns, every field with a precise meaning, at home in relational (SQL) databases. Two source families:

- **Machine-generated**: produced automatically, high velocity, massive volume. Sensors (RFID, GPS), web server logs. Precise and continuous.
- **Human-generated**: born from human interaction with software. Form inputs, CRM records, POS transactions, in-game actions.

### Unstructured

No predefined schema, no rows, no columns, no simple SQL query to interrogate them. Human-generated examples are natural language and pixels: documents, messages, photos, video, audio. Machine-generated examples: satellite imagery, surveillance camera footage.

The number that matters: unstructured data is roughly **80% of all existing data**. Structured data tells you *who* bought *what*; unstructured data, through text analysis and computer vision, explains the *why* and the *how*: sentiment, opinion, context. This is also the bridge to the generative half of this module (note 07): LLM and RAG architectures exist precisely because the 80% became tractable.

### Semi-structured

The bridge between the two worlds, with three defining traits:

- **Self-describing**: the data carries its own structural information inside it.
- **No rigid schema**: structure can vary record to record.
- **Hierarchical**: typically organised as trees or graphs.

Canonical formats: **XML**, **JSON**, **HTML**, and email (structured headers plus an unstructured body). A JSON record shows all three traits at once: keys describe the fields, nesting carries the hierarchy, and nothing stops the next record from adding an attribute. Semi-structured data dominates the web and modern data architectures: API payloads, HTML pages, NoSQL stores like MongoDB. The operational win is evolvability, new attributes without restructuring the whole database.

## Data mining and text mining

> Data mining is the use of efficient techniques to analyse very large data collections and extract useful, possibly unexpected patterns.

The framing matters more than the definition: mining is not searching for a specific record, it is asking the data to say something you do not already know. Discovery of hidden patterns and correlations in large volumes, mostly over structured data.

**Text mining** is the subfield specialised in unstructured text: emails, reports, customer reviews, support tickets. Its leverage is the same 80% figure from above, restated for the enterprise: the large majority of company information is text. Reading this deck next to the rest of the course, classical data mining is the ancestor of today's ML pipelines, and text mining is the ancestor of the NLP and LLM workloads this module architects for.

## Where the data lives: warehouse, lake, lakehouse

The full treatment of the three archetypes (definitions, schema-on-write vs schema-on-read, comparison table, medallion layers) is in the module 07 notes (`07_data_governance_knowledge_management/notes/08_data_knowledge_architectures.md`); this section keeps the recap to one line each and focuses on what this deck adds: the internal warehouse architectures, the two-tier dilemma, the lakehouse enabling technology, and the workload mapping.

One-line recap: **warehouse** = structured, filtered, schema-on-write, single source of truth for OLAP and BI; **lake** = everything raw in native format, ELT, schema-on-read; **lakehouse** = lake storage with warehouse guarantees.

### Two ways to build a warehouse

The deck splits the warehouse world into two architectures:

```
  Warehouse-driven (ETL)                 Data virtualization (query-driven)

  ERP --+                                       query
  CRM --+--> ETL --> [ physical DW ] --> BI       |
  DBs --+    clean,     central,                [ virtual layer ]
             transform  structured              /      |      \
             (nightly batch)                  ERP     CRM     DBs
                                              (no copy: decompose the query,
                                               hit live sources, reassemble)
```

**Warehouse-driven** is the classic Inmon/Kimball centralisation: extract, transform, load into a physical repository. What it buys: certified, coherent data (when the CEO reads a report, the numbers hold) and fast SQL. What it costs: **rigidity** (adding a field from the CRM is an IT project, not a click: schema change, ETL rewrite, testing) and **latency** (batch loads, typically nightly, so the warehouse tells you what happened yesterday, not what is happening now).

**Data virtualization** keeps no physical repository at all. A middleware layer receives the query, decomposes it, sends the pieces to the source systems, and reassembles the result on the fly. Zero ETL latency and high agility, ideal for rapid prototyping and occasional reports. The two costs are structural: **performance is unpredictable** (the query is as fast as the slowest source) and there is real **operational risk**: a heavy analytical query lands directly on transactional systems. The deck's example is vivid and correct: run a complex statistical query against a supermarket's checkout database during opening hours and you are competing with the cash registers. Good for light reporting, wrong for heavy mining.

### The lake: ELT and five components

The lake inverts the paradigm: **ELT**, load everything raw immediately, transform only when needed, with schema applied at read time. Its three strategic advantages are exactly the ones AI workloads care about: **raw-data access** (data scientists want the uncooked data, not someone else's aggregation), **cheap storage** (S3, Azure Blob), and **storage/compute decoupling** (scale each independently).

A lake is not a shared folder; it stands on five components: **ingestion** (batch or streaming), **storage**, **processing** (engines like Spark), **data catalog** (the metadata index), and **governance and security**. The same layered pipeline appears in the module 07 architecture diagram; the two critical layers are the last two. A lake without a catalog is a library with a million books and no index: a **data swamp**.

### The two-tier dilemma

Before the lakehouse, the common survival strategy was running both stacks:

```
  sources --> [ Data Lake ] ----ETL----> [ Data Warehouse ] --> BI, reporting
                    |                    (fragile, slow,
                    +--> ML, data science  duplicated)
```

Two technology silos: the warehouse for official BI (reliable but partial data), the lake for ML and data science (complete but chaotic data). Three problems make it an expensive compromise:

- **Duplicated cost**: the same data stored and maintained twice.
- **ETL fragility**: moving data from lake to warehouse is complex and error-prone.
- **Data drift**: the warehouse lags the lake. The deck's scenario: the CEO reads 1 million in sales from the warehouse, the data scientist reads 1.2 million from the lake. When the two disagree, trust in the data itself collapses, and that is the worst outcome an architecture can produce.

### Lakehouse: a metadata layer, not marketing

The lakehouse claim, warehouse reliability on lake economics, rests on one precise innovation: a **transactional metadata layer** (Delta Lake, Apache Iceberg, Apache Hudi) sitting on top of the lake's raw files. What that layer delivers:

- **ACID transactions** on lake storage: a write interrupted mid-flight no longer corrupts the table.
- **Open formats** (Apache Parquet): the data stays in standard files any engine can read, no vendor lock-in.
- **Time travel**: automatic versioning, so the data can be queried as it was at a past point in time.

The result is unification: the data scientist and the financial analyst work on the same data at the same moment, no copies, no drift. The deck's provenance point is worth keeping: these technologies were not born in universities but at Netflix, Uber, and Databricks, companies whose data volumes broke the old solutions. The summary compression from the slides is neat: warehouse is schema-on-write, lake is schema-on-read, lakehouse is **schema-on-read plus ACID**, serving everyone instead of one user class.

### Which archetype feeds which AI workload

The module 08 reading of all this: storage is a solution-architecture decision, and the downstream workload decides it.

| Workload | Natural home | Why |
|---|---|---|
| BI, KPI reporting, dashboards | Warehouse (or lakehouse gold layer) | Certified schema-on-write data, fast SQL |
| ML training, data science exploration | Lake (or lakehouse) | Raw data access, cheap scale, storage/compute decoupled |
| GenAI and RAG over documents | Lake / lakehouse | The 80% unstructured lives here (note 07) |
| Unified BI + AI platform | Lakehouse | One governed copy, ACID, no drift |
| Occasional real-time reports, no copy | Data virtualization | Zero ETL latency; keep the queries light |

How the data actually travels from sources into these stores is the pipeline question: architectural patterns for it (batch vs streaming, Lambda/Kappa) are note 02, and exercise 01 builds an ETL pipeline in Python end to end.

## Gotchas

- **Big Data read as a byte threshold.** The definition is relative to the era's tooling. The interesting question is never "how many terabytes" but "do the current tools still cope".
- **Veracity treated as a data-team detail.** For AI it is the primary failure mode: a model does not flag dirty data, it generalises it. Dirty in, confidently dirty out.
- **Data virtualization used for heavy mining.** The query lands on live transactional systems; a statistical scan competing with the checkout lanes is an outage, not an architecture.
- **ELT read as "no transformation".** Transform is deferred, not deleted. Skip the catalog and governance components and the deferred work compounds into a swamp.
- **The two-tier setup accepted as an end state.** It is a transition cost that never amortises: double storage, fragile ETL, and drift that erodes trust in every number the organisation reads.

## See also

- Note 01 for where the data layer sits among the components of an AI solution
- Note 02 for the ingestion side: batch vs streaming, Lambda and Kappa, Velocity made architectural
- Note 05 for the model lifecycle these data foundations feed
- Note 07 for LLM and RAG architectures, where the 80% unstructured data pays off
- Module 07 notes (`07_data_governance_knowledge_management/notes/08_data_knowledge_architectures.md`) for the in-depth archetype comparison, medallion layers, and knowledge graphs
- Exercise 01 (data pipeline with Python) for the ETL/ELT flow in working code
