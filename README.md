# AI Solutions Architect Master

Repository with projects, exercises, and hands-on material developed during the **AI Solutions Architecture** Master program.

The course builds the ability to design and orchestrate end-to-end AI solutions: from translating business objectives into technical architectures, to selecting technologies, integrating AI models, and leading development teams.

---

## Progress

| # | Module | Capstone | Status |
| --- | ------ | -------- | ------ |
| 00 | [Python Programming](00_python_programming) | Warehouse order monitoring system | delivered |
| 01 | [Machine Learning](01_machine_learning) | Defective-parts classification pipeline | delivered |
| 02 | [Large Language Models](02_large_language_models) | Hybrid RAG for a company knowledge base (ChromaDB + BM25) | delivered |
| 03 | [Agentic AI](03_agentic_ai) | Two capstones: DigitServe (n8n) + GreenThumb (ReAct + RAG) | delivered |
| 04 | [Business Case & AI PM](04_business_case_AIPM) | OmniRetail AI governance platform | delivered |
| 05 | [Cloud for AI](05_AI_cloud_services) | EnergoGrid hybrid multi-cloud infrastructure | delivered |
| 06 | [AI Service Deployment](06_AI_services_deployment) | LogiFast delivery-time service (Flask) | delivered |
| 07 | [Data Governance & KM](07_data_governance_knowledge_management) | NovaCura Pharma data governance platform | delivered |
| 08 | [Solution Design & Architecture](08_solutions_architectures_design) | RetailSight video analytics platform | delivered |
| 09 | [Information & Architecture Security](09_information_and_architecture_security) | Risk and vulnerability analysis of an AI system | in progress |
| 10 | Governance, Ethics & Compliance | AI governance framework for a fintech | planned |

---

## Topic Areas

### Python Programming

Programming fundamentals applied to real-world data engineering and automation scenarios.
**Project:** Order and warehouse monitoring system.

### Machine Learning

Complete ML pipelines, from data preparation to model evaluation, with a focus on industrial use cases.
**Project:** Classification model for defective parts in manufacturing.

### Large Language Models

Transformer architectures, prompt engineering, fine-tuning, and RAG systems for enterprise applications.
**Project:** RAG system for intelligent enterprise knowledge management.

### Agentic AI

Design of multi-agent systems, orchestration, and tool use for automating complex processes.
**Projects:** DigitServe agent orchestration (n8n) and GreenThumb support agent (ReAct + RAG).

### Business Case & AI Product Management

Feasibility analysis, product roadmaps, cost estimation, and lifecycle management of AI solutions.
**Project:** OmniRetail AI governance platform.

### Cloud for AI

Design of cloud-native infrastructures for AI workloads on AWS, GCP, and Azure.
**Project:** EnergoGrid hybrid multi-cloud AI infrastructure.

### AI Service Deployment

Containerization, CI/CD, monitoring, and scalability of models in production.
**Project:** Deployment of a predictive model for delivery time estimation.

### Data Governance & Knowledge Management

Strategies for data management, quality, and lineage in enterprise AI systems.
**Project:** Data Governance architecture for a pharmaceutical company.

### Solution Design & Architecture

Architectural patterns for scalable, resilient, and maintainable AI systems.
**Project:** RetailSight video analytics platform.

### Information & Architecture Security

Threat modeling, vulnerability analysis, and hardening of AI-based systems: model attacks (adversarial examples, data poisoning, model inversion), data security, classic threats, supply chain, Zero Trust architectures, NIS 2, AI forensics.
**Project:** Risk and vulnerability analysis of an AI-based system.

### Governance, Ethics & Compliance

Regulatory frameworks (AI Act, GDPR), bias, explainability, and algorithmic accountability.
**Project:** AI governance framework for a fintech company.

---

## Repository Structure

```text
AI_solutions_architect_course/
├── 000_certs/                       # Module completion certificates (00-09, .pdf)
├── 00_python_programming/           # Notes + PRJ (warehouse monitoring, stdlib) - delivered
├── 01_machine_learning/             # Notes + exercises + PRJ (defective parts classification, sklearn) - delivered
├── 02_large_language_models/        # Notes + exercises + PRJ (hybrid RAG, ChromaDB + BM25) - delivered
├── 03_agentic_ai/                   # Notes + exercises + 2 PRJ (n8n DigitServe + GreenThumb) - both delivered
│                                   #   GreenThumb = LangChain/LiteLLM ReAct + RAG + FastAPI notebook (2nd module-03 capstone)
├── 04_business_case_AIPM/           # Notes + exercises + PRJ (OmniRetail AI governance platform) - delivered
├── 05_AI_cloud_services/            # Notes + exercises + PRJ (EnergoGrid hybrid multi-cloud) - delivered
├── 06_AI_services_deployment/       # Notes + exercises + slides (local) + PRJ (LogiFast delivery-time service, Flask) - delivered
├── 07_data_governance_knowledge_management/  # Notes (9) + slides (local) + PRJ (NovaCura DG&KM: PDF + 8 diagrams + SQL/BigData/KG/RAG artifacts) - delivered
├── 08_solutions_architectures_design/        # Notes (11) + slides (local) + exercises (ETL, FastAPI+Docker, mini-RAG, draw.io) + PRJ (RetailSight video analytics platform) - delivered
├── 09_information_and_architecture_security/ # Notes (8) + slides (local) + exercises (adversarial noise, Llama Guard paper, Zero Trust engine, NIS 2 / Belmont texts) - capstone pending
└── README.md
```

Note: slide decks (`.pptx`) and capstone Word sources (`.docx`) are kept local and gitignored, so they are not part of the published repository. Every capstone delivered from module 04 onward ships its report as `.pdf` inside the `_PRJ_*` folder; the earlier capstones (modules 00-03) are code deliverables (`.py`, `.ipynb`, n8n `.json`).
