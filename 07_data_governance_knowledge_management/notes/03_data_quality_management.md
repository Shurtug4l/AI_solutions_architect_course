# Data Quality Management

## TL;DR

**Data Quality Management (DQM)** is the set of processes and practices that keep data accurate, complete, consistent, timely, and reliable across its whole lifecycle. It is the **quality principle** from governance turned into something measurable and monitored, not a one-time cleanup. The engine has five moving parts: **profiling** (know the data), **dimension assessment** (measure it), **metrics and monitoring** (control it over time), **lineage** (trace where it comes from and goes), and **catalog plus metadata** (document it so it stays reusable). The core deliverable is a set of **quality dimensions** made quantitative: each dimension gets an indicator, a threshold, and a place on a scorecard. Why it bites harder for AI than for a classic report is the same amplification argument as governance in general: a model learns from data, so if the data is wrong the model does not just report the error, it generalises it. Two things to internalise: profiling tells you *whether* the data is fit for use, lineage tells you *why* it broke and *where*. A metric without lineage is an isolated number; lineage without metrics is a map with no destinations.

## Cheatsheet

| Concept | One-line | Practical signal |
|---|---|---|
| **DQM** | Processes to keep data fit for use over its life | Owned dimensions, thresholds, monitoring |
| **Fit for purpose** | The data is adequate for its intended use | A CRM campaign or a model can rely on it |
| **Quality dimension** | A measurable criterion of quality | Has an indicator and an acceptance threshold |
| **Accuracy** | Data reflects the real event or object | The value matches reality, not just the schema |
| **Completeness** | No essential value is missing | Percent of populated records for a field |
| **Consistency** | Data aligns across sources and systems | Two systems tell the same story |
| **Timeliness** | Data is current when it is needed | The change reached the next invoice |
| **Uniqueness** | No unwanted duplicates | One customer, one record |
| **Validity** | Data conforms to format and business rules | A tax code has the right pattern |
| **Data profiling** | Diagnostic analysis of structure and content | Ran before transformation, not after |
| **Data quality score** | Dimensions rolled into one number (1-100) | 82 green, 74 yellow, 61 red |
| **Data lineage** | The full path origin -> transform -> consumption | You can trace an error to its source |

## Why quality is the load-bearing principle for AI

> Business decisions and AI models rest on data. Wrong data produces misleading results, and an AI model does not report a bad datum, it amplifies it. Governance exists to guarantee trust in the data; DQM is where that guarantee becomes a number.

Quality was one of the seven governance principles (see [01_what_is_data_governance.md](01_what_is_data_governance.md)). On its own that is an aspiration. DQM is the discipline that turns the aspiration into procedure: it defines what "good" means per attribute, measures the gap, and watches the gap over time. The AI angle sharpens the stakes. A dashboard built on 90 percent-complete data is a slightly wrong dashboard; a model trained on it learns the missingness as if it were signal. Quality is a prerequisite for ethical and reliable AI, which is another way of saying an ungoverned dataset is a bias generator with a training loop attached.

DQM is not a single tool or a single stage. It spans people, processes, and technology, and it runs the length of the data lifecycle.

```
  Acquisition -> Transformation -> Use -> Storage -> Decommissioning
       |               |            |        |              |
   trace, own      standards,    metrics   retention    controlled
   profile         lineage       on trend  rules        disposal
```

Each phase has its own failure modes, which is why the lifecycle framing in [04_data_lifecycle.md](04_data_lifecycle.md) is the natural companion to this note.

## The five elements of DQM

> Profiling to know the data, dimension assessment to measure it, metrics to control it over time, lineage to understand its journey, catalog to make it reusable. Drop any one and the other four degrade.

```
  Profiling  ->  Dimension assessment  ->  Metrics + monitoring  ->  Lineage  ->  Catalog + metadata
   know it        measure it                control over time          trace it     document it
```

The order is roughly the workflow. You profile first because you cannot set sensible thresholds on data you have not looked at. You assess dimensions to convert "the data looks fine" into indicators. You monitor because quality decays: a field that is 98 percent complete today drifts as upstream systems change. Lineage and catalog are the memory layer, the part that lets a quality alert six months from now be diagnosed instead of merely observed.

## The quality dimensions

> Dimensions are the criteria that measure whether a datum is fit for purpose. They turn an abstract idea ("good data") into objective values, reduce subjectivity in the assessment, and become the base for metrics and dashboards.

The slides develop four in depth (accuracy, completeness, consistency, timeliness). The two that the practical example implies, uniqueness and validity, round out the classic six that DAMA-style frameworks use. Treat this table as the heart of the note.

| Dimension | Question it answers | How it is measured | Failure example |
|---|---|---|---|
| **Accuracy** | Does the datum reflect the real event or object? | Percent of values validated against a trusted source | Return reason is blank in the system though the customer stated a defect |
| **Completeness** | Is any essential value missing? | Percent of populated records for a field | Only 20 percent of accounts filled in a phone number |
| **Consistency** | Do the data agree across systems? | Percent of records aligned across sources | Order status is "Cancelled" but the cancellation date is empty |
| **Timeliness** | Is the datum current when it is needed? | Average update latency vs the required window | An address change never reached the next invoice |
| **Uniqueness** | Are there unwanted duplicates? | Percent of duplicate records | 5 percent of customers exist as duplicate rows |
| **Validity** | Does the datum conform to format and rules? | Percent of values matching the expected pattern | 2 percent of tax codes have a malformed pattern |

**Opinion:** accuracy and validity get confused constantly and the distinction is worth guarding. Validity is cheap to check because it is syntactic (does the tax code match the regex). Accuracy is expensive because it is semantic (is this the *right* tax code for this person). A pipeline can be 100 percent valid and badly inaccurate, which is exactly the failure that slips past naive rule sets.

### Turning dimensions into thresholds

Every dimension needs a quantified indicator and an acceptance threshold set by the business, not by the engineer, because the tolerable level of missingness depends on how critical the field is.

```
  Completeness  >= 98%
  Accuracy      >= 97%
  Consistency   >= 95%   (across systems)
```

A worked case from the slides, a customer dataset going into a CRM campaign or a model:

- 8 percent of records have no address -> completeness is low.
- 5 percent of customers are duplicated -> uniqueness is compromised.
- 2 percent of tax codes are wrong -> accuracy is insufficient.

Conclusion: the dataset is not fit for use. Note the reasoning: no single dimension is catastrophic, but the compound effect fails the intended use. That is the argument for scoring across dimensions rather than gating on one.

## Data profiling: knowing the data before using it

> Profiling is the diagnostic analysis that examines and summarises a dataset to understand its structure, content, and relationships. It is the first step of DQM. It does not guarantee quality, it starts the process that guarantees it.

Run it at the start of any integration, BI, or AI project, before transformation, so surprises surface while they are still cheap to fix. It can be repeated (a light pass, then a detailed pass) as the work proceeds. Profiling operates at three granularities:

| Level | What it inspects | What it surfaces |
|---|---|---|
| **Table** | Record counts, sample rows | Dataset size, a first read on the content |
| **Column** | Distinct values, nulls/blanks, value ranges, data types and lengths | Domain of a column, incomplete data, outliers, type mismatches |
| **Value** | Specific values, patterns, distributions | Unknown sales regions, phone numbers missing a prefix, distribution errors |

Best practice from the slides, with the reasoning attached: profile before transforming (avoid surprises downstream), involve both technical and business teams (the technical side sees the nulls, the business side knows which nulls matter), automate on large volumes (manual profiling does not scale), and document the results (profiling output feeds the rules, metrics, and controls that follow, and without documentation there is no traceability). Tooling that automates this in code: **Great Expectations** and **Pandera** for declarative expectations and schema validation, **Deequ** for JVM/Spark-scale constraint checks, **Evidently** when the concern is drift on data feeding a model.

## Metrics, scoring, and monitoring

> Metrics translate the dimensions into numeric, comparable values. They can be static (a snapshot at one moment) or dynamic (monitored over time). The dynamic form is the one that catches decay.

Two components make up the monitoring layer:

- **Data quality score.** A number, typically on a 1-100 scale, assigned to an attribute or entity by rolling up its dimensions (completeness, validity, consistency, accuracy, uniqueness, timeliness). It makes quality quantitative and comparable across datasets.
- **Data quality thresholds.** Bands defined by the business according to how critical the data is. A common traffic-light scheme:

```
  score < 70     ->  poor      (red)     urgent: investigate a real problem
  70 <= score 80 ->  medium    (yellow)  monitor, do not ignore
  score > 80     ->  high      (green)   acceptable
```

Example metrics behind the score: percent complete records, percent consistency errors, average update time. A score dropping below 70 is not a cosmetic dip, it signals a significant issue upstream. This is where AI-assisted DQ earns its place: automatic anomaly detection flags incoherent or drifting data faster than a scheduled rule sweep, and dashboards (Power BI, Collibra) keep the trend visible instead of buried in a query.

## Data lineage: the memory of the datum

> Lineage describes the full path of a datum: from its origin, through its transformations, to its consumption. It answers three questions: where did this come from, how was it computed or transformed, who uses it and where is it shown. It is the base for transparency and trust.

```
  Origin  ->  Transformations (ETL/ELT)  ->  Consumption (report, model, dashboard)
     |                 |                                  |
  source system   rules applied                     who reads it
```

Lineage is what makes quality diagnosable. When a metric goes red, lineage lets you trace back to the cause: a wrong source, a broken ETL rule, a mistimed load. It connects the DQ metrics to the specific lifecycle stage where the fault entered, which is the difference between "the number is wrong" and "the number is wrong because of transform X on source Y." It also carries compliance weight: GDPR, audits, and certifications all want the reconstructable history that lineage provides, and for AI it underwrites trust in the model's inputs. Tooling lives in the catalog and governance space: **Collibra**, **Alation**, **DataHub**, **Atlan**, **Purview**, backed by metadata repositories and automatic ETL-flow tracking. The catalog and metadata layer this depends on is developed in [04_data_lifecycle.md](04_data_lifecycle.md).

The slide's own line is the right summary: lineage is the historical memory of the data, and without it the metrics stay isolated numbers.

## Practice: identifying metadata (BookWave)

The exercise grounds the catalog idea. Given an e-commerce `books` table, describe each field's metadata, then assemble a catalog entry. The point is that metadata is what turns a column into a documented, findable, reusable asset.

Field metadata for `books`:

| Field | Data type | Description | Sensitivity | Required |
|---|---|---|---|---|
| `book_id` | INT | Book identifier | Not sensitive | Yes |
| `title` | VARCHAR | Book title | Not sensitive | Yes |
| `author` | VARCHAR | Author | Not sensitive | Yes |
| `price` | DECIMAL | Price | Not sensitive | Yes |
| `category` | VARCHAR | Book category | Not sensitive | Optional |
| `publish_date` | DATE | Publication date | Not sensitive | Optional |

Catalog entry for the table:

```
  Table:        books
  Description:  Books available in the e-commerce catalogue
  Source:       BookWave backend
  Refresh:      Real-time
  Owner:        Product Owner
  Key fields:   book_id, title, author, price
  Uses:         Sales reports, performance analysis, business dashboards
```

The `Owner` line is not decoration. It is the accountability principle from governance showing up at the field level: a catalog entry without a named owner is documentation nobody maintains.

## Gotchas

- **Valid is not accurate.** Rule sets catch format violations (validity) and silently pass semantically wrong values (accuracy). A green validity check on a field that is confidently wrong is a false comfort.
- **Profiling once, at the start.** Profiling is a repeated activity. Upstream schemas drift, so a clean profile at project kickoff says nothing about the data six months later. Re-profile on a cadence.
- **Thresholds set by engineers.** Acceptance thresholds encode business risk tolerance. The engineer knows the null rate; only the business knows whether that null rate is fatal for the use case. Let the owner set the band.
- **Metrics without lineage.** A red score with no lineage is an alarm with no address. You know something broke, not where. Wire lineage before you scale the metrics.
- **Score as a single gate.** A quality score is a rollup and it hides which dimension failed. Keep the per-dimension breakdown next to the composite number, otherwise remediation is guesswork.

## See also

- [01_what_is_data_governance.md](01_what_is_data_governance.md) - the quality principle and accountability that DQM operationalises
- [02_policies_standards_frameworks.md](02_policies_standards_frameworks.md) - where quality thresholds and rules become documented standards
- [04_data_lifecycle.md](04_data_lifecycle.md) - metadata, data catalog, and lineage across the lifecycle stages
- [05_from_data_to_knowledge.md](05_from_data_to_knowledge.md) - what fit-for-use data enables once it becomes knowledge
- [07_llm_rag_semantic_search.md](07_llm_rag_semantic_search.md) - retrieval quality as a downstream consumer of clean, profiled data
