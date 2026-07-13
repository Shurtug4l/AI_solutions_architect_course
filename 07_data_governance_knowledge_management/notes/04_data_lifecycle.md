# The Data Lifecycle

## TL;DR

A datum behaves like a product: it is born, it gets used, it is eventually retired. The **data lifecycle** is the ordered set of stages it passes through, from creation or collection all the way to deletion or permanent archival. Mapping that lifecycle means one concrete thing: at any moment you can say where a given datum lives and what state it is in. That is the precondition for everything governance promises. The lifecycle is also the connective tissue between three disciplines that otherwise drift apart: **data governance** (the rules), **data quality** (are the rules met), and **data lineage** (the documented path the datum travelled). The stages the course works with are **acquisition, cataloging and storage, use, archiving, decommissioning**, with **sharing** happening throughout the active middle. Two supporting mechanisms make the map usable rather than decorative: the **Data Catalog** (the inventory that says what exists and where) and **metadata management** (the engine that fills that inventory). Without them the lifecycle is a theory; with them it is queryable.

## Cheatsheet

| Concept | One-line | Practical signal |
|---|---|---|
| **Data lifecycle** | All stages a datum crosses, birth to disposal | You can name the current stage of any dataset |
| **Acquisition** | Collect or generate from sources, validate at origin | Source, accuracy, and consent checked before ingest |
| **Cataloging / storage** | Persist the datum and give it an identity | Structured to relational, unstructured to NoSQL |
| **Use** | Consumed by people, processes, or AI | Access is secure, versioned, policy-consistent |
| **Archiving** | Cold retention of inactive but still useful data | Retention policy states how long and where |
| **Decommissioning** | Delete or anonymise what is no longer needed | Catalog entry flipped to "dismissed" |
| **Data Catalog** | Central inventory of enterprise datasets | Answers what, where, who owns, how to use |
| **Metadata management** | Creating and curating data about data | Feeds the catalog, enables semantic search |
| **Technical metadata** | Schema, format, physical path | The machine's view of the datum |
| **Business metadata** | Name, meaning, domain, unit | The human's view of the datum |
| **Operational metadata** | Refresh frequency, owner, sensitivity | The runtime view of the datum |
| **Data lineage** | Documented path across systems and transforms | You can trace an output back to its source |

## Why map the lifecycle

> Every datum has a lifecycle, like a product: it is born, it is used, and in the end it is dismissed. Mapping that lifecycle means always knowing where the datum sits and in what state.

The payoff is not abstract. Four things depend directly on having the map: **process improvement** (you cannot fix a flow you cannot see), **cost control** (storage you forgot about is pure cost with no value), **data usability** (a datum nobody can locate is a datum you do not have), and **compliance and governance** (regulators ask where personal data is and how long you keep it, and "we are not sure" is not an answer).

The lifecycle is where governance stops being a policy document and becomes evidence. Each stage has to be monitored and documented, which is exactly what turns the traceability principle from note 01 into something auditable. It is the junction point between three things that are often treated separately: governance sets the rules, quality measures whether the rules hold, and lineage records the road the datum took. Continuous, evidence-based control lives here or nowhere.

```
   +-------------+     +--------------+     +-----------+
   | Acquisition | --> |  Cataloging  | --> |    Use    |
   | collect,    |     |  + storage   |     |  consume, |
   | validate,   |     |  give an     |     |  analyse, |
   | authorise   |     |  identity    |     |  feed AI  |
   +-------------+     +--------------+     +-----------+
                                                  |
                       sharing / distribution across teams
                                                  v
   +-----------------+   +---------------+   +-----------+
   | Decommissioning | <-|   Archiving   | <-|  no longer|
   | delete /        |   |  retention,   |   |  active   |
   | anonymise       |   |  cold storage |   +-----------+
   +-----------------+   +---------------+
          |
          v
   catalog entry updated to "dismissed"
```

## The phases

The course uses a five-phase model. Sharing is not a separate box: it happens continuously while the datum is active, which is why it sits on the arrow rather than in a node.

| Phase | What happens | Objective | Signal it is done right |
|---|---|---|---|
| **1. Acquisition** | Collect or generate from internal or external sources (apps, sensors, databases, APIs). Define quality and format standards at the origin. Verify source, accuracy, and authorisations (GDPR, consent, licences). | The datum enters clean, compliant, and useful. | Input error rate, source coverage, average acquisition time |
| **2. Cataloging and storage** | Persist the datum and give it an identity: characteristics and quality that later inform encryption and transformation. Structure drives the store: structured data tends to relational databases, unstructured to NoSQL or non-relational. | The datum is described and findable, not just written somewhere. | It has a catalog entry, not only a file path |
| **3. Use** | Consumed by users, processes, or AI algorithms. Quality checks, secure access, dataset versioning. Prevent improper or policy-inconsistent use. | Extract maximum value without compromising integrity. | Access is controlled and every consumer is a known one |
| **4. Archiving** | Retain data no longer active but still useful for analysis, audit, or legal obligation. Define retention (how long, where). Use secure solutions (S3, data lake, encrypted backups). | Historical availability and security at reduced maintenance cost. | Retention policy is explicit, not implicit |
| **5. Decommissioning** | Delete or anonymise data no longer needed. Respect data-protection rules (GDPR, ISO 27001). Update the catalog to mark the "dismissed" state. | Nothing stays uncontrolled or uselessly retained. | The catalog reflects deletion, not just the storage layer |

Read the table left to right and the same obligation repeats under every phase: monitor and document. A stage that is not documented is a hole in the map, and the map is only as trustworthy as its weakest stage. The transitions matter as much as the boxes. Acquisition to storage is where a datum earns its identity; storage to use is where access control decides who touches it; use to archiving is where you separate hot value from cold obligation; archiving to decommissioning is where the retention clock finally fires. Skip the documentation at any transition and lineage breaks precisely there.

**Opinion:** decommissioning is the phase teams quietly skip, and it is the one with the sharpest legal edge. Keeping personal data past its retention window is not neutral inertia, it is a GDPR liability that grows silently. The cheap discipline is to make deletion a catalog event, so "we deleted it" is a recorded fact rather than a hopeful assumption about some storage bucket.

## Data Catalog and metadata management

> The Data Catalog is the shop window that exposes the data. Metadata management is the engine that supplies the information to fill it.

A **Data Catalog** is a centralized inventory of the organisation's datasets that lets people discover, understand, and use information assets efficiently. It collects information on every dataset (structured and unstructured), makes data searchable and shareable across teams, and states where a datum lives, who owns it, and how it may be used. It is the first move from chaos to order: without a catalog data is scattered and time is lost hunting for it; with one, data is described and reachable.

**Metadata management** is the process of creating, collecting, and curating metadata, the information that describes data: what a datum represents, where it comes from, how it should be interpreted. Three types, three points of view:

| Type | Contains | Example |
|---|---|---|
| **Technical** | Schema, format, physical path | `VARCHAR(255)`, Parquet, `s3://bucket/users/` |
| **Business (descriptive)** | Name, meaning, domain, unit of measure | "signup_source", allowed values `{app, web}` |
| **Operational** | Refresh frequency, owner, sensitivity | Near real-time, Fitness Analytics Manager, PII |

Metadata is the base layer for three things: guaranteeing quality and traceability, populating the catalog, and enabling **semantic search** over the data. The slide phrasing is worth keeping: metadata is the language with which data tells its story. Catalog and metadata are two pillars of modern governance and, less obviously, of AI explainability: if you cannot say what a training column meant and where it came from, you cannot explain the model that ate it.

Concretely, the pair earns its cost on five fronts:

- Cuts the time spent searching for and understanding data.
- Raises trust in the enterprise datasets, because provenance is visible.
- Improves collaboration between IT and business, who stop arguing about what a field means.
- Enables **lineage, audit, and quality monitoring** as first-class processes rather than afterthoughts.
- Supports integration with analytics, AI, and BI tooling that reads the catalog as a source of truth.

## Lineage: the thread through the lifecycle

Lineage is the documented path a datum travels across systems and transformations, and it is the part of traceability that makes the lifecycle auditable rather than merely described. In the retail exercise below the lineage reads: e-commerce form to transactional database via API, nightly ETL to the data warehouse, warehouse to Power BI, monthly copy to long-term storage, deletion after ten years. That chain is not decoration. It is what lets you answer "where did this sales number come from" and "which upstream field, if wrong, poisons this dashboard". Lineage is where the lifecycle map and the quality discipline of note 03 meet: a broken value is only fixable if you can walk back to the stage that introduced it.

Two directions are worth naming because they answer different questions. **Backward lineage** (impact of an error) traces a suspicious output back to its origin, which is the debugging move. **Forward lineage** (impact of a change) traces a source forward to everything that depends on it, which is the change-management move: before you alter a column you want the list of dashboards and models that will break. A lifecycle map without lineage tells you the stages exist; lineage tells you how a change in one stage ripples through the rest. The medallion pattern in the subscription exercise (Bronze to Silver to Gold) is lineage made structural: each layer is a named transformation stage, so the path from raw event to executive KPI is legible by construction rather than reconstructed after the fact.

## Worked examples

**Catalog entry (FitLife).** The exercise designs a complete catalog entry from four datasets (`users`, `workouts`, `payments`, `app_events`). Field-level metadata for `users` classifies type, sensitivity, value domain, and mandatoriness:

```
full_name     VARCHAR  PII            valid alphanumeric   mandatory
email         VARCHAR  PII            email format         mandatory
birthdate     DATE     PII            DD/MM/YYYY           mandatory
signup_source VARCHAR  non-sensitive  {app, web}           optional
```

The dataset-level entry for `workouts` shows what a full catalog card carries: functional description ("records workouts performed by users"), owner (Fitness Analytics Manager), ETL processes (app events to transformation to `user_id` enrichment), refresh (near real-time), data-quality rules (`duration_min > 0`, `workout_type in {cardio, forza, yoga}`), relations (`FK user_id -> users`), and retention (5 years). Note how the card mixes all three metadata types in one place: that co-location is the point of a catalog.

**Lifecycle map (retail orders).** Mapping the `orders_demo` dataset onto the five phases:

| Phase | Mapped to |
|---|---|
| Acquisition | Order created via e-commerce form, saved by API |
| Cataloging / storage | Transactional database |
| Use | Nightly ETL to warehouse, viewed in Power BI by Marketing |
| Archiving | Monthly copy to long-term storage |
| Decommissioning | Deleted after 10 years (fiscal law) |

**Documenting the lifecycle (subscriptions).** The richer exercise documents `subscriptions` (a Bronze to Silver to Gold data-lake flow feeding an executive KPI dashboard) against a grid of Phase, Description, Systems, Data Owner, Main Risks, Quality Controls. The instructive part is the last two columns: naming the risk (input error, missing metadata) and the matching control (mandatory-field validation, automatic classification) per phase. That is the shape a lifecycle document should take: not a list of systems, but a stage-by-stage record of who owns it, what can go wrong, and what catches it. The retention split (archive offline after 5 years, delete personal data after 7 for GDPR) shows archiving and decommissioning as two distinct obligations, not one.

The worked solution fills only the first two rows (acquisition and cataloging) and leaves use, archiving, and decommissioning for the student. That is deliberate: the acquisition row names the input-error risk against mandatory-field validation, and the cataloging row names missing metadata against automatic classification. The pattern to carry into the empty rows is the same triple every time: for each phase, one owner, the risks that phase introduces, and the control that catches them before the next phase inherits them.

## Gotchas

- **Storage is not cataloging.** Writing a datum to S3 is phase two only if the datum also gets an identity in the catalog. A file with no entry is invisible to governance, and invisible data is where compliance gaps hide.
- **Decommissioning left implicit.** Deletion has to be a catalog event, otherwise "we deleted it" means "we think some bucket no longer has it". The retention clock (5, 7, 10 years in the exercises) is a legal deadline, not a suggestion.
- **Metadata without an owner drifts.** Operational metadata includes the owner for a reason. A catalog entry with a blank owner column rots: nobody updates the refresh frequency, nobody re-checks sensitivity after a schema change.
- **Confusing lineage with a diagram.** A pipeline drawing is not lineage until it is kept in sync with the running systems. Stale lineage is worse than none, because it is trusted.
- **Sharing treated as a phase.** Sharing is continuous across the active life of the datum, not a discrete step. Modelling it as a box hides the fact that every consumer inherits the datum's quality and sensitivity.
- **Compliance bolted on late.** Consent, licences, and source verification are cheapest to enforce at acquisition. Discovering at the use or archiving stage that a dataset never had a legal basis means the cost has already compounded through every downstream copy. Push the checks to the origin.
- **KPIs measured only at the end.** Acquisition has its own metrics (input error rate, source coverage, acquisition time) for a reason: a datum that enters dirty is cheaper to catch at the door than to scrub after it has fanned out across the warehouse and three dashboards.

## See also

- [03_data_quality_management.md](03_data_quality_management.md) - quality dimensions and lineage as the mechanism that makes a bad value traceable to the stage that produced it
- [08_data_knowledge_architectures.md](08_data_knowledge_architectures.md) - where the Data Catalog sits in a larger data and knowledge architecture, alongside warehouses, lakes, and the lakehouse
- [01_what_is_data_governance.md](01_what_is_data_governance.md) - the traceability and accessibility principles that the lifecycle map turns into evidence
