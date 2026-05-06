# CLAUDE.md

## Context

This repository contains coursework, exercises, and projects for a Master's program in AI Solutions Architecture. The program covers the full stack of skills needed to design and deploy enterprise AI systems: Python, classical ML, LLMs, agentic AI, cloud infrastructure, deployment, data governance, security, and ethics.

The student has a technical background and is building expertise across all of these areas. Treat them as a capable practitioner who values precision and depth, not simplified explanations.

## Language and Output Style

Always write in English unless the user explicitly asks otherwise. This applies to:
- Notebook markdown cells
- Code comments
- Print statements and plot labels
- Any prose or analysis

Do not use AI-sounding artifacts in generated text. Specifically avoid:
- Em dashes (--) as a stylistic separator
- Phrases like "Let's dive into...", "In summary...", "It's worth noting that...", "This allows us to..."
- Passive hedging: "it can be seen that", "it is important to note"
- Filler transitions: "Furthermore,", "Moreover,", "In conclusion,"
- Excessive qualifiers and disclaimers

Write like a technically sharp student: direct sentences, precise word choice, no padding.

## Technical Standards

### Code

- Write idiomatic Python. Prefer readability over cleverness, but do not over-abstract.
- Do not add error handling or validation beyond what the task actually needs.
- Comments should explain non-obvious design choices or constraints, not restate what the code does.
- No multi-line docstrings unless the function has genuinely complex behavior that cannot be inferred from its signature.

### Notebooks

- Each notebook section should include a brief technical rationale for the choices made (model selection, preprocessing steps, hyperparameters, architecture decisions).
- After running experiments or getting results, include a short critical analysis: what worked, what did not, and why. Interpret metrics in context rather than just reporting them.
- Do not write conclusions that only restate what the output already shows.

### Analysis and Critical Thinking

When producing analysis, always address:
- Why a specific technique or model was chosen over alternatives
- The tradeoffs involved (accuracy vs. speed, complexity vs. interpretability, etc.)
- What the results actually mean in the context of the problem, not just whether a metric is high or low

## Repository Structure

```
AI_solutions_architect_course/
├── 000_certs/                          # Module completion certificates
├── 00_python_programming/              # Python fundamentals + warehouse/order monitoring project
├── 01_machine_learning/                # ML pipelines + defective parts classification project
│   ├── exercises/
│   └── PRJ_classification_defective_parts/
├── 02_large_language_models/           # Transformers, prompt engineering, RAG
│   └── exercises/
└── README.md
```

Upcoming modules (not yet in repo): Agentic AI, Business Case & AI PM, Cloud for AI, Deployment, Data Governance, Solution Design, Security, Governance & Ethics.

## Module Topics (for context)

| # | Module | Core Focus |
|---|--------|------------|
| 00 | Python Programming | Data engineering, automation |
| 01 | Machine Learning | Pipelines, classification, evaluation |
| 02 | Large Language Models | Transformers, prompt engineering, fine-tuning, RAG |
| 03 | Agentic AI | Multi-agent systems, orchestration, tool use |
| 04 | Business Case & AI PM | Feasibility, roadmaps, cost estimation |
| 05 | Cloud for AI | AWS/GCP/Azure infrastructure for AI workloads |
| 06 | AI Service Deployment | Containers, CI/CD, monitoring, scalability |
| 07 | Data Governance | Data quality, lineage, enterprise data management |
| 08 | Solution Design | Architectural patterns for scalable AI systems |
| 09 | AI Security | Threat modeling, vulnerability analysis |
| 10 | Governance & Ethics | AI Act, GDPR, bias, explainability |
