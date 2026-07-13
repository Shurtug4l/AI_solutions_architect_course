# From Data to Knowledge

## TL;DR

Note 01 climbed the **data -> information -> knowledge** ladder to make the point that governance needs definitions. This note finishes the climb and then crosses the fence into **knowledge representation**. Two moves. First, the ladder gets a fourth rung: **experience** (the classic pyramid calls it **wisdom**), the layer where knowledge is applied to prevent risk and make decisions, and it feeds back into the data cycle. Second, the operator that lifts a datum from one rung to the next is **context**, and context has three references: temporal (when), spatial (where), semantic (in what sense it counts). Once you take representing that context seriously you get the three structures this note is really about: a **taxonomy** (a tree of categories), an **ontology** (a formal, shared description of a domain's concepts and the typed relations between them, the schema), and a **knowledge graph** (that ontology populated with real instances, a graph of subject-predicate-object triples). A **semantic layer** sits on top so every team reads the same definitions. This is the hinge of the whole module: it is where **data management** (quality, lifecycle, metadata) becomes **knowledge management**, and it is the substrate that RAG and graph architectures later stand on.

## Cheatsheet

| Concept | One-line | Practical signal |
|---|---|---|
| **DIKW pyramid** | data, information, knowledge, wisdom | each rung answers a different question |
| **Context** | the three references: when, where, in what sense | without it a datum cannot even become information |
| **Knowledge Management** | preserve, share, make knowledge accessible | data stops being isolated and starts having value |
| **Taxonomy** | hierarchical classification, an is-a tree | one backbone, categories nested under categories |
| **Ontology** | formal shared schema: concepts + typed relations + rules | a "conceptual map of context" for a domain |
| **RDF triple** | subject - predicate - object | the atomic fact of a knowledge graph |
| **Knowledge Graph** | the ontology populated with instances | nodes are entities, edges are relations |
| **Semantic layer** | logical layer that unifies definitions | everyone speaks the same language over the data |

## Completing the pyramid: from DIK to DIKW

> Knowing something is not the same as understanding it. Knowing it will rain one day is one thing; knowing that on that day I will need an umbrella is another. That gap is exactly where knowledge management lives.

Note 01 stopped at knowledge because governance only needs the first three rungs to justify definitions and ownership. The slides push one rung higher, and the standard version of this model is the **DIKW pyramid**, with **wisdom** on top. Each rung is a checkpoint, and each checkpoint answers a different question.

```
        WISDOM        knowledge applied to act: "if I skip proper shoes I might slip"
      -----------      question: how do I decide, and prevent the next risk?
      KNOWLEDGE       internalised, tied to experience: "I need an umbrella"
    ---------------    question: can I now predict more?
    INFORMATION       the datum read in context: "it is raining outside"
  -------------------  question: what could I do about it?
        DATA          the raw fact, no context: "humidity at 100%"
                       question: what does this even entail?
```

The top rung is not decoration. Wisdom (the slides call it experience) is where knowledge turns into decisions, and it loops back: the decisions you make change which data you collect next. So the pyramid is really a cycle with a pyramid drawn inside it. For the DIK portion, do not re-derive it here, note 01 already has the ASCII and the metadata twist.

## Context is the operator

The thing that promotes a datum up a rung is **context**, nothing else. A raw datum on its own is an eternal incomplete. To give it context you attach three references:

- **Temporal**: when did it happen.
- **Spatial**: where did it happen.
- **Semantic**: in what sense it counts.

Take the word "Roma". On its own the information is empty: what are we even talking about, the city, the football club, a person's name, a film? The next step after collecting a datum is therefore to make the datum itself carry what it is about. That is the whole motivation for the machinery in the second half of this note.

## Knowledge = information + experience

The formula the slides give is blunt: **information + experience = knowledge**. You turn a datum into a habit through **interpretation, feedback, and organizational memory**. **Knowledge Management (KM)** is the set of practices that preserve, share, and make that knowledge accessible. Strip KM away and data stays a pile of isolated information: in an enterprise that is cost without value.

There is a caveat that matters for an AI course:

> AI models process data and emit information, but they do not carry the critical sense a decision needs. Judgment, causality, and intention are things a model can simulate, not things it possesses.

That is the reason a human and a governance layer stay in the loop precisely where data becomes decision. Seen end to end, the AI pipeline reads as a single flow with four stages, each with its own tooling:

```
DATA         ->  Collection         ->  Data Quality
INFORMATION  ->  Contextualization  ->  Metadata
KNOWLEDGE    ->  Internalisation    ->  Knowledge Base
DECISION     ->  Application        ->  Decision Management
```

Read against the eCommerce domain the rest of this note uses, the four stages are concrete:

- **Data**: a raw purchase row, customer 42 bought SKU 991 at 14:07.
- **Information**: contextualised with metadata, that row is "a repeat customer buying running shoes".
- **Knowledge**: internalised into a knowledge base, "repeat customers who buy running shoes churn less".
- **Decision**: applied, "offer this segment the loyalty tier now".

Data Governance and Knowledge Management meet at the last arrow: **where data becomes decision**. Without order and explicit rules the data never changes a decision, and data that changes no decision is inert.

## Representing knowledge: taxonomy vs ontology vs knowledge graph

Three structures get used interchangeably in conversation and they are not the same thing. Keeping them apart is the single most useful distinction in this note.

| Structure | What it is | Shape | eCommerce example |
|---|---|---|---|
| **Taxonomy** | a classification, one hierarchy | a tree (is-a, part-of) | Footwear -> Shoes -> Running shoes |
| **Ontology** | formal, shared description of concepts and the typed relations among them, plus constraints | a schema (the "T-box") | Product, Order, Customer + how they relate |
| **Knowledge Graph** | the ontology filled with real instances | a graph of facts (the "A-box") | Anna placed order 1234 containing these shoes |

A **taxonomy** only knows one kind of relation, "belongs under". An **ontology** adds relations that are not hierarchical at all and can add rules (an Order must have at least one Product). The slides define it well: a formal and shared description of the concepts in a domain and the relations between them, a conceptual map of context. Both adjectives carry weight. **Formal** means machine-checkable, not prose in a document, so a tool can reason over it. **Shared** means agreed across the teams that use it; an ontology only one person believes in is just a private model, and the whole reason to build one is to kill disagreement. The relations come in several flavors, and naming them is half the value because logical relations mean less ambiguity:

- **Hierarchical**: membership in a category (a running shoe is footwear).
- **Composition**: a logical whole-part link (an order is composed of products).
- **Causal**: a chain of consequential events (stockout causes backorder).
- **Synonymy**: two labels for one thing (a "customer" may be a "user").

## Triples: the atom of a knowledge graph

A **Knowledge Graph** is the graph-shaped representation of a domain's knowledge: every node is a concept or entity, every edge a relation. The atomic unit is the **triple**, written **subject - predicate - object**. This is the RDF data model, and a whole graph is just a large set of triples.

```
(Customer: Anna)  --places-->    (Order: 1234)
(Order: 1234)     --contains-->  (Product: Shoes)
(Product: Shoes)  --isA-->       (Footwear)
```

Read top to bottom: Anna places order 1234, which contains a pair of shoes, which is a kind of footwear. Each arrow is one fact. In the standard stack the vocabulary and the axioms live in **RDFS/OWL** (that is the ontology), the facts live as **RDF** triples (that is the graph), and you query them with **SPARQL**. This note stays at study depth on the tooling; the point to keep is that ontology and graph are schema and data, not synonyms.

The payoff of the graph shape is **multi-hop** questions. In tables, "which customers bought a product in the same category as something Anna returned" is a pile of joins; over triples it is a short walk along edges. That is why knowledge that is dense in relations gets modelled as a graph and not as one more wide table.

You already use a knowledge graph every day: a **social network** is one. "People you may know" is the graph noticing friends in common, films you both watched, an event you both attended in the same city. Same triples, different domain.

## The semantic layer

> The semantic layer is a logical stratum on top of the stores that makes concepts and relations coherent and usable. Literally a layer that gives sense to the flood of data, so that everyone speaks the same language.

Its job is to unify definitions. When "active customer" or "revenue" means one thing in finance and another in marketing, every dashboard disagrees and no one trusts any of them. The semantic layer is the single place those definitions live, so a metric resolves the same way no matter who asks. In a business context this is not a nice-to-have, it is what makes shared knowledge queryable at all. The modern framing is the headless "metrics layer" sitting between raw storage and every consumer (BI, notebooks, apps), but the slides' point is older and simpler: it is the contract that keeps definitions from drifting.

## Why this note is the bridge

This is the hinge of module 07. On one side sits **data management**: quality, lifecycle, metadata, the machinery of notes 03 and 04. On the other sits **knowledge management**: ontologies, graphs, retrieval. Governance is what keeps the graph trustworthy (an ungoverned triple is a confident lie), and representation is what makes governed data reusable as knowledge instead of a fact you looked up once. Everything downstream leans on this: retrieval-augmented generation reads over this knowledge, and graph-backed architectures operationalise it.

## Gotchas

- **Taxonomy mistaken for ontology.** A tree of categories is not an ontology. The ontology earns the name only when it adds typed, non-hierarchical relations (and ideally constraints). A category tree is the "is-a" backbone, not the whole map.
- **Ontology mistaken for knowledge graph.** The ontology is the schema (T-box), the graph is the populated instances (A-box). One is the legend, the other is the filled-in map. Confusing them makes people think they "have a knowledge graph" when all they have is a class diagram.
- **Expecting the model to supply meaning.** AI emits information; judgment, causality, and intention come from the semantic layer and from an accountable human. Do not outsource the decision rung to the model.
- **Semantic layer as a glossary.** Definitions parked in a wiki nobody queries will drift apart from the numbers. The layer only works when it is the enforced contract the queries actually run through, not documentation on the side.
- **Treating context as optional metadata.** Without the temporal, spatial, and semantic references a datum cannot even become information. "Roma" with no context is not a weak datum, it is a non-datum.

## See also

- [01_what_is_data_governance.md](01_what_is_data_governance.md) - the DIK pyramid and the metadata twist this note extends to DIKW and to knowledge representation
- [06_knowledge_management_techniques.md](06_knowledge_management_techniques.md) - the concrete KM practices (capture, share, reuse) that operate on the knowledge modelled here
- [07_llm_rag_semantic_search.md](07_llm_rag_semantic_search.md) - RAG retrieves over exactly this knowledge; the ontology and semantic layer are what make retrieval precise
- [08_data_knowledge_architectures.md](08_data_knowledge_architectures.md) - where the knowledge graph and semantic layer become architectural components
