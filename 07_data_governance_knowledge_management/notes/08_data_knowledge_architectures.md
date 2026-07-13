# Data and Knowledge Architectures

## TL;DR

A **data architecture** defines how data is collected, stored, processed, and made available across an organisation. It is the set of components, processes, and rules that turn raw data into something usable for analytics, AI training, and knowledge management. For AI the stakes are higher than for a plain report: no solid data foundation, no reliable model. Three storage archetypes matter. **Data Warehouse** is structured data with **schema-on-write**, tuned for BI. **Data Lake** is raw data in any format with **schema-on-read**, cheap and flexible, the natural home for ML. **Lakehouse** is the convergence: one layer that keeps all data types but adds ACID transactions, governance, and warehouse-grade performance on top of lake economics. On the knowledge side, a **Knowledge Graph** models entities and the relations between them as nodes, edges, and **triples** (subject, predicate, object). It turns isolated tabular rows into a semantic network that an AI can query for facts that are certain, current, and structured. The one-line mental model from the slides is worth keeping: **the AI is the intelligence, the Knowledge Graph is the structured memory**. Put together they understand, reason, verify, and stop inventing.

## Cheatsheet

| Concept | One-line | Practical signal |
|---|---|---|
| **Data architecture** | How data is collected, stored, processed, served | Ingestion + storage + processing + catalog + governance + access |
| **Schema-on-write** | Structure enforced when data lands | You clean before you store (warehouse) |
| **Schema-on-read** | Structure applied when data is queried | You store first, interpret later (lake) |
| **Data Warehouse** | Structured, curated, BI-first | Certified sales and finance reports |
| **Data Lake** | Raw, any format, cheap, ML-first | Logs, images, text, IoT streams |
| **Lakehouse** | Lake storage + warehouse guarantees | ACID + governance + BI and ML on one layer |
| **Knowledge Graph** | Entities + relations as a graph | Nodes, edges, labels, a semantic network |
| **Triple** | (subject, predicate, object) | The atomic fact of a graph |
| **RDF** | Standard model for triples | Interoperable, machine-readable knowledge |
| **Ontology** | Schema of types, relations, properties | The rules the graph must respect |

## What a data architecture is

> A data architecture defines how data is collected, stored, processed, and made available. It is the components, processes, and rules that transform raw data into information usable for analysis and reporting, AI training, and enterprise knowledge management.

Without a solid data base, AI projects cannot produce trustworthy results. "Garbage in, garbage out" is not a slogan here, it is the failure mode: a model does not merely report bad data, it generalises it. An effective architecture buys five things: quality and consistency of sources, scalability for volume and variety, governance and traceability (lineage and metadata), controlled access for analysts and data scientists, and reusability of the same data across use cases.

A modern architecture is a pipeline of layers, not a single box:

```
  Ingestion  ->  Storage  ->  Processing  ->  Access / Consumption
   batch or       DW /         clean,           BI, analytics,
   streaming      Lake /       transform,       ML, knowledge mgmt
                  Lakehouse    integrate
       |             |             |                    |
       +------- Metadata & Catalog: documentation, lineage --------+
       +------- Governance & Security: quality, access, privacy ---+
```

Metadata/catalog and governance/security run underneath every stage rather than sitting at the end. That is the same lesson as note 04 on the data lifecycle: the catalog is what makes the architecture navigable, and governance is not a gate you bolt on at consumption time.

The point of all this plumbing is not storage for its own sake. It is to move data up the value chain, and the chain is a loop, not a one-way street:

```
     +--> DATA --analysis--> INFORMATION --models / AI--> KNOWLEDGE --+
     |                                                                |
     +------------------- feeds new decisions and new data <----------+
```

Data becomes information through analysis, information becomes knowledge through models and AI, and knowledge feeds new decisions that generate new data. The architecture is what keeps that loop turning instead of leaking value at each hop. That loop is the subject of note 05.

## The three storage archetypes

### Data Warehouse

A centralised repository of **structured** data, optimised for reporting and analysis. Schema is **defined at write time** (schema-on-write), so what lands is already clean, integrated, and consistent. Complex analytic queries are fast, and access is through BI tools. Typical use: sales analysis, cost control, business performance. The price of that discipline is rigidity and cost: everything must be modelled before it enters, and storage plus maintenance are expensive.

### Data Lake

A scalable store that keeps **raw** data in any format: structured, semi-structured, or unstructured. Schema is applied **only at read time** (schema-on-read), which is why a lake ingests logs, IoT streams, text, images, and video without a modelling ceremony up front. It handles large volumes and variety, supports advanced analytics and machine learning, and storage is cheap. The catch, and it is a real one: schema-on-read is not free flexibility, it is deferred debt. Without a catalog and governance a lake degrades into a "data swamp" where nobody knows what a field means or whether it can be trusted.

### Lakehouse

The **hybrid** that unifies the two. It keeps the lake's cheap storage and all data types, then layers on **ACID transactions**, high performance, and centralised metadata and governance. BI and ML read from the same governed layer instead of copying data between a lake and a warehouse. Use cases are unified data platforms for AI and analytics, and modern enterprise scenarios where maintaining two parallel stacks is the thing you are trying to avoid.

**Opinion:** for a greenfield AI-first organisation the Lakehouse is the sane default, because the DW-plus-Lake split forces you to duplicate data and reconcile two governance models. The Warehouse still wins where the requirement is certified, auditable, low-latency BI on stable structured data (finance, regulatory reporting), where schema-on-write rigidity is a feature, not a tax.

### The comparison that matters

| Characteristic | Data Warehouse | Data Lake | Lakehouse |
|---|---|---|---|
| **Data type** | Structured | All types (structured, semi, unstructured) | All types |
| **Schema** | Schema-on-write (at write) | Schema-on-read (at read) | Hybrid |
| **Main users** | BI analysts, business users | Data scientists, data engineers | Both |
| **Governance** | High, centralised | Variable, more complex | High, unified |
| **Performance** | High on structured queries | Depends on volume and format | High via metadata and caching |
| **Cost** | High (storage + maintenance) | Low (cheap storage) | Medium |

Reading the table as a decision rule: **Data Warehouse** for structured business analysis, KPIs, and reports. **Data Lake** for advanced analytics, ML, and unstructured data at low storage cost. **Lakehouse** for integrated BI-plus-AI on a single governed platform. These map onto real cloud services (module 05): warehouses like Redshift, BigQuery, Synapse; lakes on S3, GCS, ADLS; lakehouses on Databricks or Snowflake. The serving side, where a model trained on this data goes live, is module 06.

## Choosing an architecture: the layered storage pattern

Each archetype has its own maturity ladder inside storage. Data does not land in its final form, it is promoted stage by stage:

```
  Data Warehouse :  Staging   ->  ODS       ->  Data Mart
  Data Lake      :  Raw       ->  Cleansed  ->  Curated
  Lakehouse      :  Bronze    ->  Silver    ->  Gold
```

The Bronze/Silver/Gold naming is the Databricks "medallion" convention, and it is the same idea in all three rows: ingest raw, refine, then expose a trusted layer for consumption. When designing an architecture for a concrete case (the TechWear exercise), the deliverable is exactly this: sources (e-commerce, CRM, app, logs, feedback, images), an ingestion layer (ETL/ELT, batch or streaming), storage laid out in the stages above, and consumption tools (BI, analytics, ML). The classification instinct to build first: transactions and customer records are **structured** (Warehouse or Lakehouse), web and app logs and text feedback are **semi-structured** (Lake or Lakehouse), product images are **unstructured** (Lake).

## Knowledge Graph: representing knowledge

> A Knowledge Graph is a graph structure that represents real-world entities (people, objects, concepts) and the relations between them. Nodes are entities, edges are relations, labels carry meaning and context.

It turns isolated data into a **semantic network**, which is exactly what tabular storage cannot do. A warehouse row tells you a customer bought a laptop; it does not tell you the laptop is Electronics, that Electronics is a category with a returns policy, that Maria is a repeat buyer in that category. A graph encodes the connections as first-class objects:

```
  [Customer: Maria] --buys--> [Product: Laptop] --category--> [Electronics]
```

The atomic unit is the **triple**: (subject, predicate, object), for example (Maria, buys, Laptop). Chain enough triples and you get a graph. Formalised, this is **RDF** (Resource Description Framework), the standard that makes triples interoperable and machine-readable, queried with **SPARQL** (the Wikidata exercise runs a SPARQL query for Italian cities and their regions, then renders the result as a navigable graph of nodes and edges). Above the raw triples sits the **ontology**: the conceptual schema that defines which types, relations, and properties are legal. Metadata, queries, and reasoning are what let you extract knowledge and infer facts that were never stated explicitly.

The building blocks, named plainly:

- **Entities (nodes)**: people, organisations, products, concepts.
- **Relations (edges)**: labelled links such as "is part of", "works for", "insures".
- **Triples (S, P, O)**: the base form every fact reduces to.
- **Ontology / semantics**: the schema of types, relations, and properties.
- **Metadata, queries, reasoning**: the tooling that extracts knowledge and infers new facts.

Why reach for a graph in knowledge and data management at all:

- It overcomes the limits of tabular data by adding semantics, context, and relations.
- It integrates heterogeneous data (structured, semi, unstructured) through one common model.
- It supports automatic reasoning and inference, not just direct lookups.
- It favours knowledge governance, traceability, and an integrated view of the "enterprise knowledge".

## KG + AI: the complementary pair

AI and Knowledge Graphs solve two different, complementary problems. An LLM is excellent at intuiting, generating text, and predicting. A graph is excellent at remembering things in a structured way without getting them wrong. An LLM does not always know if a fact is current, it can hallucinate, and it cannot memorise all of a company's data. The graph is the reliable memory it queries:

> The AI is the intelligence. The Knowledge Graph is the structured memory. Together they build systems that are reliable, intelligent, and explainable.

The traffic runs both ways. The graph gives the AI **grounded knowledge**: the model asks the KG "which customers bought Electronics in the last 30 days?" or "which source tables feed migration process X?", gets a certain, current, structured answer, and translates it into natural language for a human. The AI, in turn, helps **build and maintain** the graph, which does not populate itself: it reads documents, PDFs, and tables, recognises entities (people, products, systems), identifies relations ("Table A depends on Table B"), and updates the graph as the data changes. Google's search does exactly this when you ask for "the actors of Inception": it queries its Knowledge Graph rather than matching web text, then lets the model phrase the answer.

Four things happen when the two work together: AI errors drop (facts are verified against the graph first), answers get smarter (the graph supplies "who is connected to whom"), enterprise knowledge stays alive (the graph grows as the AI enriches it), and you can build **reasoning-based** systems that deduce new facts instead of only retrieving old ones.

**Opinion:** the sharpest practical payoff is on RAG (note 07). Plain vector RAG retrieves text chunks by similarity and hopes the relevant facts are in there. Graph-backed retrieval (GraphRAG is the current label) adds structure: it can follow relations, respect an ontology, and hand the model a connected subgraph instead of a bag of paragraphs. That is fewer hallucinations and traceable provenance, which is the difference between a demo and something you would let a stakeholder rely on.

## Practice, in one line each

- **Analyse enterprise architectures** (TechWear): classify each data type and pick the fitting storage archetype.
- **Explore an online KG**: run the Wikidata SPARQL query, read the table, then switch to the graph view to see nodes and edges.
- **Design a data architecture**: draw sources, ingestion, layered storage, and consumption, with a note on why that architecture and which use cases it unlocks.
- **Build a mini KG** (HR domain): five entities (Employee, Manager, Department, Skill, Training Course), five relations (works in, manages, has skill, completed, develops skill), at least two properties each, then draw it.

## Gotchas

- **Schema-on-read read as free flexibility.** It is deferred governance debt. A lake without a catalog and ownership becomes a data swamp where no field is trustworthy. The flexibility is real, the bill arrives at read time.
- **Lakehouse as a magic word.** ACID and unified governance on cheap storage is a genuine architecture, not a rebranded lake. If a "lakehouse" has no transactional layer and no enforced metadata, it is a lake with a nicer name.
- **A Knowledge Graph without an ontology.** Triples with no schema drift into an inconsistent mess: the same relation spelled three ways, entities that should be one node duplicated. The ontology is what makes reasoning sound, not decorative.
- **Treating the KG as a replacement for the LLM.** It is the memory, not the intelligence. The value is in the pairing: the graph supplies certain facts, the model supplies language and inference. Drop either and the "explainable, reliable" promise collapses.
- **Copying data between a lake and a warehouse forever.** Two stacks means two governance models and constant reconciliation. If both BI and ML need the same governed data, that is the argument for a lakehouse, not for a nightly sync job.

## See also

- [04_data_lifecycle.md](04_data_lifecycle.md) - the ingestion, storage, and catalog stages here are the lifecycle made physical; lineage and cataloguing are what keep an architecture navigable
- [05_from_data_to_knowledge.md](05_from_data_to_knowledge.md) - the data-to-information-to-knowledge loop and the ontologies that a Knowledge Graph implements
- [07_llm_rag_semantic_search.md](07_llm_rag_semantic_search.md) - RAG and semantic search; a Knowledge Graph gives retrieval structure and provenance (GraphRAG)
- [09_practical_use_cases.md](09_practical_use_cases.md) - where these architectures and graphs land in concrete business scenarios
- Module 05 (cloud) for the managed services that implement warehouse, lake, and lakehouse; module 06 (deployment) for serving a model trained on this data
