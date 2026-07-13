# Knowledge Management Techniques

## TL;DR

**Knowledge management (KM)** is the discipline of creating, organizing, sharing, and reusing the knowledge that data produces. The slides frame it as a cycle: **creation -> sharing -> application**, looping back on itself. The distinction that runs under everything is **tacit vs explicit** knowledge, which the course calls "documents vs experience". Explicit knowledge is formalized: written down, saved in databases, the "tablets of the law". Tacit knowledge is volatile: experience, intuition, the practical skill you pick up by watching an expert work. The two convert into each other, and this is the whole engine of KM (Nonaka's SECI model names the four conversions). Neither is enough on its own: documents without experience become rigid rules, experience without documents becomes an undocumented risk that walks out the door when the person leaves. KM is a **tool, not a panacea**. Use it where problems are complex, risks are high, questions recur, and people turn over; skip it for temporary, fast-moving, one-off decisions where documenting everything just slows you down. For AI it is load-bearing: chaotic knowledge produces chaotic AI, and a RAG system is, when you look at it honestly, a KM technique with retrieval bolted on.

## Cheatsheet

| Concept | One-line | Practical signal |
|---|---|---|
| **Knowledge management** | Create, organize, share, reuse knowledge | Same problem is not re-solved from scratch twice |
| **Explicit knowledge** | Formalized, written, stored | Lives in a doc, a wiki, a database |
| **Tacit knowledge** | Experience, intuition, practical skill | Lives in a person's head, learned by doing |
| **SECI** | The four tacit/explicit conversions | Nonaka: socialize, externalize, combine, internalize |
| **Knowledge mapping** | Map of who knows what | Points you to the holder of a competence |
| **After action review** | Structured post-event lessons | Turns one event into reusable insight |
| **Best-practice repository** | Archive of validated solutions | Explicit, reusable, searchable |
| **Community of practice** | Peers exchanging experience | Tacit knowledge moving between people |
| **Organizational storytelling** | Narrative transfer of context | Culture and edge-cases passed by story |
| **Lessons learned** | Captured outcomes, good and bad | Feeds the repository, closes the loop |

## The KM cycle

> KM serves one purpose: creating, organizing, sharing, and reusing the knowledge accumulated from data. To understand the techniques it helps to see KM as a cycle, not a one-off project.

```
   CREATION  ->  SHARING  ->  APPLICATION
      ^                             |
      +-----------------------------+
```

Knowledge is created, then shared so it stops living in one head, then applied to a real decision, and the outcome of that application feeds new creation. The cycle is the reason a repository is not KM by itself: a full archive nobody shares or applies is dead weight. The techniques below each attack one or two arcs of this loop.

## Five techniques worth knowing

The course names five techniques. They are not a menu where you pick one; they cover different arcs of the cycle and different points on the tacit/explicit axis, so a real setup usually runs several at once.

| Technique | What it captures | Mostly tacit or explicit |
|---|---|---|
| **Knowledge mapping** | Who holds which competence, where it sits | Explicit map pointing at tacit holders |
| **After action review** | What actually happened vs what was planned | Tacit -> explicit (externalization) |
| **Best-practice repository** | Solutions that have been validated in the field | Explicit, built for reuse |
| **Community of practice** | Shared experience among peers on a domain | Tacit -> tacit (socialization) |
| **Organizational storytelling** | Context, culture, edge-cases via narrative | Tacit, carried by the story |

**Opinion:** the after action review is the most undervalued of the five. It has a military origin (the US Army formalized it) and its power is that it forces the volatile "how it really went" out of people's heads and into a form the repository can hold. Skip it and your best-practice repository slowly fills with theory nobody stress-tested.

## Documents vs experience: the tacit/explicit split

> Documents and experience are not in opposition, they are complementary. Documents alone are incomplete; experience alone cannot be shared seriously. Together they work, separated they fail.

This is the central theme of the module and it is exactly the **tacit vs explicit** distinction under a friendlier name. Documents are explicit knowledge; experience is tacit knowledge. Each has a real profile of strengths and weaknesses:

| | Documents (explicit) | Experience (tacit) |
|---|---|---|
| **Says** | How the world *should* go | How the world *actually* went |
| **Pro** | Reference for governance and compliance; if well written, an excellent anchor | Lives in context; saves the day in sudden anomalies and edge-cases |
| **Con** | Verbose, slow, usually written *after* the problem occurred | Tied to a person, so volatile; not verifiable |

Separate them and you get a disaster in two flavors: documents without experience produce rigid, often useless rules; experience without documents produces untraceable risk. In a complex process both failure modes get amplified. The point of integration is not to write everything down. It is to hold both in mind at once: documents give the fixed rules, experience resolves the exceptions the rules never anticipated.

## SECI: how knowledge changes state

The slides list three transitions between explicit and tacit. Nonaka and Takeuchi's **SECI model** names four and gives the picture its missing quadrant. Worth knowing because it is the reference frame the whole industry uses.

```
                    to TACIT               to EXPLICIT
              +---------------------+---------------------+
  from        | SOCIALIZATION       | EXTERNALIZATION     |
  TACIT       | tacit -> tacit      | tacit -> explicit   |
              | learn by watching   | "I note the expert" |
              +---------------------+---------------------+
  from        | INTERNALIZATION     | COMBINATION         |
  EXPLICIT    | explicit -> tacit   | explicit -> explicit|
              | training on the job | merge the documents |
              +---------------------+---------------------+
```

Mapping the slides onto this: explicit-to-tacit is **internalization** ("training on the job"), tacit-to-explicit is **externalization** ("I write down the expert's account"), and the "hybrid" the slides mention is really **socialization + combination** working together when people collaborate and exchange. The takeaway is that knowledge is never static: it circulates through these four states, and a healthy KM setup keeps all four moving rather than betting everything on one.

## When to use it, and when not

KM techniques are fundamental but they are not free. Apply them everywhere and you slow every process down; fail to apply them where they matter and you leave the process exposed. So the where/when is a real design decision.

| Use KM when... | Skip KM when... |
|---|---|
| Risks are high | Situations are temporary |
| People turn over continuously | The environment is very dynamic |
| The same questions keep recurring | Decisions are instant and one-off |
| Problems are genuinely complex | There is no time or place to document |

**Where** it earns its keep: wherever there are relations between concepts, systems, and rules, and interactions at the nodes of a complex process. That is precisely why it is vital for AI, security, governance, and compliance. **How** to run it well: with balance, using only what is needed, once you have already established *what* you need to know, and on top of solid governance. The course's decalogue reduces to four requirements: a clear strategy, a collaborative culture, adequate tools, and a capillary definition of roles, governance, and responsibilities.

## Knowledge decays: keep it fresh

> Knowledge is also a datum, and like any datum it becomes obsolete. Documents age, and experience can expire the day the person carrying it walks out.

This is the maintenance side of KM and it is easy to skip because a captured piece of knowledge feels "done". It is not. Three practices keep the store honest:

- **Update and be updated.** Refresh the explicit record when the world moves, and refresh your own understanding against it. A best-practice repository frozen in time slowly turns into a museum of how things used to work.
- **Keep an eye on context.** A lesson that was true in one setting can quietly stop being true when the setting changes. The value of tacit knowledge is that it "lives in context", so track when the context shifts.
- **Classify the information.** Untagged, unstructured knowledge is knowledge you cannot find, and knowledge you cannot find is knowledge you do not have. Classification is what makes the cycle's *sharing* and *application* arcs actually work.

The same decay logic is why governance sits underneath all of this: without traceability and ownership, nobody notices when a documented rule or an inherited practice has gone stale.

## Why it matters for AI

> Without well-organized and well-managed knowledge, AI returns results that are incomplete, opaque, or outright wrong. If the knowledge is chaotic, so is the AI.

This is the bridge from KM theory to the rest of the module. An AI system does not invent context, it consumes whatever knowledge you feed it, and it amplifies the state of that knowledge the same way a model amplifies dirty data. Feed it well-curated explicit knowledge and it grounds its answers; feed it a chaotic pile and it produces confident nonsense. KM does not exist "to know more", it exists **to err less and know better**: it reduces the redundancy of repeated errors, contextualizes knowledge rather than just expanding it, and guarantees continuity and coherence across decisions.

Concretely, a **RAG system is a KM technique**: it turns a document corpus (explicit knowledge) into a retrievable, reusable answer surface. What it cannot capture on its own is the tacit layer, the "how it really went" that never made it into a document. That gap is the reason RAG grounded on a stale or incomplete corpus fails the same way a rigid rulebook fails. See [07_llm_rag_semantic_search.md](07_llm_rag_semantic_search.md).

So the choice of technique becomes a governance question, not a tooling preference. Integrating documents and experience well, on a foundation of clear ownership and traceability, is what lets an AI process stay accurate; integrate them badly and you get the same blunders as not integrating at all.

## Gotchas

- **Documenting everything.** Not all knowledge should be written, structured, or formalized. Applying KM uniformly slows the whole organization. Find the weak points in the process and act there, not everywhere.
- **Treating documents and experience as rivals.** They are complementary, not competing. The failure is picking one; integrating badly is as damaging as not integrating at all.
- **Forgetting knowledge decays.** Knowledge is also a datum, so it goes obsolete. Documents age, experience expires when the person carrying it leaves. Updating, re-classifying, and keeping an eye on context are non-negotiable, not chores for later.
- **Mistaking a full repository for captured knowledge.** An explicit archive misses the tacit layer by construction. A RAG index built on that archive inherits the same blind spot and hides it behind a fluent answer.
- **Selling KM as a panacea.** It is a management tool and a conscious design choice, not a cure-all. Overreach and it becomes bureaucracy that people route around.

## See also

- [05_from_data_to_knowledge.md](05_from_data_to_knowledge.md) - the DIK pyramid and how information becomes decision-usable knowledge, the input KM organizes
- [07_llm_rag_semantic_search.md](07_llm_rag_semantic_search.md) - RAG and semantic search as the concrete KM technique for AI, and its tacit-knowledge blind spot
- [09_practical_use_cases.md](09_practical_use_cases.md) - where these techniques land in real scenarios (IT support, HR, incident response)
- [01_what_is_data_governance.md](01_what_is_data_governance.md) - the governance that KM sits on top of; the collaboration principle is where knowledge is created
- [08_data_knowledge_architectures.md](08_data_knowledge_architectures.md) - the architectures that hold explicit knowledge at scale (knowledge bases, graphs, stores)
