#!/usr/bin/env python3
"""
================================================================================
PROJECT: RAG system for intelligent enterprise knowledge management
         DataPulse S.p.A.

         Module 02: Large Language Models
================================================================================

Author : Simone La Porta
Date   : 2026-05-13


OVERVIEW
--------
RAG (Retrieval-Augmented Generation) backend for DataPulse S.p.A. that lets
employees query internal corporate documentation in natural language:
policies, operational manuals, FAQs, compliance guides, and project reports.

The knowledge base is inlined as a Python list of dictionaries (KNOWLEDGE_BASE
section) rather than loaded from external .txt files. The choice is
deliberate: in a teaching context the dataset stays under version control
with the code, execution has zero filesystem dependencies, and regenerating
tests with a different corpus is trivial. Swapping in a real loader (a
data/ directory, a document repository, S3) only touches the ingestion
function: the rest of the pipeline already works on source-agnostic
`Document` objects.

ARCHITECTURE
------------

  Corporate documents (text + metadata)
           │
           ▼
   DocumentProcessor          ← chunking with overlap
     │           │
     ▼           ▼
  VectorStore  BM25Engine     ← parallel indexing
  (ChromaDB,   (rank-bm25,
   cosine)      lexical)
     │           │
     └─────┬─────┘
           ▼
   HybridRetriever            ← semantic + lexical + recency/validity fusion,
           │                    optional filters on category / minimum date
           ▼
   LLMPipeline                ← structured prompt → Ollama | OpenAI
           │
           ▼
   RAGResponse                ← text + sources + confidence + timestamp

KEY COMPONENTS
--------------
  EmbeddingEngine   : paraphrase-multilingual-MiniLM-L12-v2 (multilingual, 384d)
  VectorStore       : ChromaDB in-memory, cosine metric
  BM25Engine        : BM25Okapi with min-max score normalization
  HybridRetriever   : alpha=0.6 (text weight), gamma=0.15 (recency weight)
                      score = (1-gamma) * (alpha*sem + (1-alpha)*bm25) + gamma * recency
                      Optional filters on category and minimum document date.
  LLMPipeline       : selectable provider (ollama | openai)
  Confidence        : mean of the top-k hybrid scores (proxy for retrieval quality)

PREREQUISITES
-------------
  # LLM provider (two options: local with Ollama or cloud with OpenAI):

  # Ollama (no API key required)
  pip install langchain-ollama
  ollama serve && ollama pull llama3.2 (or any model of choice)

  # OpenAI
  pip install langchain-openai
  export OPENAI_API_KEY="sk-..."

EXECUTION
---------
  python PRJ_rag_system_for_company_knowledge.py

  The provider is set in main() through the `provider` argument.
  For retrieval-only mode (no LLM): set use_llm=False in main().
================================================================================
"""

# ── Standard library ──────────────────────────────────────────────────────────
import math
import os
import re
import textwrap
import time
import warnings
from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional

# ── Third-party libraries ─────────────────────────────────────────────────────
import chromadb
import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer

warnings.filterwarnings("ignore")


# ==============================================================================
# KNOWLEDGE BASE - DataPulse S.p.A.
# ==============================================================================
#
# In a real system this section is replaced by a loader that reads from files,
# a document database, or a corporate repository. Here I use in-memory
# dictionaries to keep the project self-contained and runnable with no
# external code dependencies.
#
# Per-document metadata:
#   doc_id         : unique identifier (used in citations)
#   title          : document title
#   category       : type: policy | manual | faq | guide | report
#   author         : responsible team or office
#   creation_date  : drafting date (YYYY-MM-DD)
#   validity_date  : expiry/review date (None = no expiry)
#
# Documents cover the most relevant areas for the primary use case
# (data access, GDPR, security) and a few adjacent areas to test the
# retriever's ability to discriminate between similar documents.
# ==============================================================================

KNOWLEDGE_BASE: list[dict] = [
    {
        "doc_id": "POL-001",
        "title": "Customer Data Access Policy",
        "category": "policy",
        "author": "Compliance Office",
        "creation_date": "2025-09-01",
        "validity_date": "2026-09-01",
        "text": """
                CUSTOMER DATA ACCESS POLICY - DataPulse S.p.A.
                Version 2.1 - Issued by the Compliance Office

                SCOPE
                This policy applies to all employees, contractors, and vendors
                who access personal customer data as part of DataPulse S.p.A.
                operations.

                ACCESS REQUEST PROCEDURE
                1. The requester fills in form RDA-01 available on the internal portal.
                2. The form is submitted to the requester's line manager for approval.
                3. The manager approves or rejects within 3 business days.
                4. The approval is forwarded to the Data Governance team for registration.
                5. The Data Governance team grants permissions in the IAM system within 24 hours.
                6. The requester receives an email notification with the access credentials.

                ACCESS LEVELS
                - Level 1 (Read-only): analytics, reporting, customer success.
                - Level 2 (Read and write): product team, backend engineering.
                - Level 3 (Full): DBAs, system architects, CISO.

                APPLICABLE REGULATIONS
                - GDPR (EU Regulation 2016/679): legal basis for processing, explicit
                  consent, right to be forgotten, data portability.
                - Legislative Decree 196/2003 (Italian Privacy Code): aligned with the
                  GDPR via Legislative Decree 101/2018.
                - ISO/IEC 27001: information security standard adopted by DataPulse.
                - DORA (Digital Operational Resilience Act): applicable to financial
                  services provided to banking customers.

                REQUESTER OBLIGATIONS
                - Access data only for the purposes declared in form RDA-01.
                - Do not share access credentials with third parties.
                - Immediately report any abnormal access to the Security team.
                - Respect the data minimization principle: access only the data
                  strictly necessary for the declared purpose.

                VIOLATIONS
                Violations lead to disciplinary action up to termination, plus
                possible legal consequences under the GDPR (fines up to 4% of
                annual global revenue or 20 million euro, whichever is higher).
                """,
    },
    {
        "doc_id": "POL-002",
        "title": "Data Classification and Protection Policy",
        "category": "policy",
        "author": "Compliance Office",
        "creation_date": "2025-01-15",
        "validity_date": "2026-01-15",
        "text": """
                DATA CLASSIFICATION AND PROTECTION POLICY - DataPulse S.p.A.
                Version 1.3

                DATA CLASSIFICATION
                DataPulse adopts the following classification scheme:

                PUBLIC: information freely shareable (press releases, website).
                INTERNAL: information for internal use only (operational guides, release notes).
                CONFIDENTIAL: sensitive business data (contracts, product roadmap, financial data).
                RESTRICTED: personal customer data, system credentials, cryptographic keys.

                HANDLING OF RESTRICTED DATA
                Data classified as RESTRICTED must be:
                - Encrypted at rest with AES-256 and in transit with TLS 1.3.
                - Accessible only via two-factor authentication (MFA).
                - Subject to access logging with 24-month retention.
                - Covered by Data Loss Prevention (DLP) on corporate systems.

                RECORD OF PROCESSING ACTIVITIES (GDPR Art. 30)
                DataPulse maintains an up-to-date register of all personal data
                processing activities, available to the Compliance Office. The
                register includes: processing purpose, data categories, legal
                basis, recipients, transfers to third countries, security measures.

                CONSENT AND LEGAL BASIS
                Before starting any new processing of personal data, the product
                team must obtain validation from the Compliance Office identifying
                the correct legal basis (consent, contract, legal obligation,
                legitimate interest).
                """,
    },
    {
        "doc_id": "MAN-001",
        "title": "Operations Manual - New Employee Onboarding",
        "category": "manual",
        "author": "HR & Operations",
        "creation_date": "2025-06-01",
        "validity_date": None,
        "text": """
                OPERATIONS MANUAL - NEW EMPLOYEE ONBOARDING
                DataPulse S.p.A. - HR & Operations

                WEEK 1: SYSTEM ACCESS
                Day 1: the IT manager sets up the workstation and AD credentials.
                Day 2: request access to corporate email, Jira, Confluence, GitHub.
                Day 3: IT security training (mandatory eLearning course,
                       duration 2 hours, platform: DataPulse Academy).
                Days 4-5: shadowing with the buddy assigned by the team.

                MAIN CORPORATE SYSTEMS
                - Project management : Jira (https://jira.datapulse.internal)
                - Documentation      : Confluence (https://wiki.datapulse.internal)
                - Source code        : GitHub Enterprise (https://github.datapulse.internal)
                - Communication      : Slack + Teams (for external customers)
                - IT ticketing       : ServiceNow

                MANDATORY POLICIES TO SIGN WITHIN 7 DAYS
                1. Corporate Code of Conduct
                2. Confidentiality Policy and NDA
                3. Customer Data Access Policy (POL-001)
                4. IT Systems Acceptable Use Policy

                VPN ACCESS
                Working remotely requires the corporate VPN (Cisco AnyConnect).
                VPN credentials are issued by IT together with the AD credentials.
                Connections from unprotected public networks are forbidden without
                an active VPN.
                """,
    },
    {
        "doc_id": "FAQ-001",
        "title": "FAQ - Product Team: Common Questions on GDPR and Compliance",
        "category": "faq",
        "author": "Product Team",
        "creation_date": "2025-04-10",
        "validity_date": "2026-04-10",
        "text": """
                FAQ - GDPR AND COMPLIANCE FOR THE PRODUCT TEAM

                Q: Can I use customer data to test a new feature in development?
                A: No. Real customer data must never be used in development or
                   testing environments. Use the synthetic datasets generated by
                   the Data Engineering team or the anonymization function
                   available in the internal DevDataGen tool.

                Q: Do I need to inform customers if I add a new field to the user profile?
                A: It depends on the nature of the data. If the field collects new
                   personal data or changes the processing purpose, the privacy
                   notice must be updated and, in some cases, fresh consent must be
                   obtained. Consult the Compliance Office before release.

                Q: What happens in case of a data breach?
                A: DataPulse is required to notify the Italian Data Protection
                   Authority (Garante Privacy) within 72 hours of detection
                   (GDPR Art. 33). Immediately activate the incident response
                   protocol (IRP-003) and notify the CISO. The Legal team handles
                   notifications to data subjects when the risk to their rights
                   is high.

                Q: Can I export customer data to an Excel file for an ad-hoc analysis?
                A: Only with Level 2 or Level 3 authorization (see POL-001) and only
                   on corporate devices with encryption enabled. The export must be
                   logged in the access register and the file deleted after use.

                Q: How do I handle a deletion request ("right to be forgotten") from a customer?
                A: Within 30 days of the request, the data must be removed from all
                   systems, including backup copies older than 30 days. An automated
                   workflow is available on ServiceNow (ticket type: GDPR-DELETE).

                Q: Is data transferred outside the EU?
                A: Only to countries with an adequate level of protection or under
                   signed Standard Contractual Clauses (SCC). All cloud providers
                   used by DataPulse have SCC in place. Always check with Compliance
                   before integrating a new provider.
                """,
    },
    {
        "doc_id": "FAQ-002",
        "title": "FAQ - IT Security: Access, VPN, and Incidents",
        "category": "faq",
        "author": "IT Security Team",
        "creation_date": "2025-05-20",
        "validity_date": "2026-05-20",
        "text": """
                FAQ - IT SECURITY

                Q: How do I request access to a system not on my list?
                A: Open a ticket on ServiceNow (category: Access > New Access Request)
                   specifying the system, the access level requested, and the
                   motivation. Approval follows the standard POL-001 flow.

                Q: I forgot my VPN password. How do I recover it?
                A: Self-service recovery is disabled for security. Contact the IT
                   Help Desk (internal extension 5500 or helpdesk@datapulse.it).
                   Identity verification is done via OTP code sent to the phone
                   number registered with HR.

                Q: I received a suspicious email. What should I do?
                A: Do not click links or attachments. Report the email as phishing
                   via the "Report Phishing" button in Outlook, or forward it to
                   security@datapulse.it. The SOC responds within 4 hours on
                   business days.

                Q: Can I use a personal USB on corporate computers?
                A: No. Non-corporate removable storage devices are blocked at the
                   DLP policy level. To transfer files, use the approved corporate
                   repositories (SharePoint, GitHub, Confluence).

                Q: What is the password policy?
                A: Minimum length 12 characters, at least one uppercase letter, one
                   number, and one special character. Changed every 90 days.
                   Reuse of the last 12 passwords is forbidden. MFA is mandatory
                   for all critical systems (IAM, GitHub, cloud console).

                Q: How do I report a vulnerability in software we are developing?
                A: Open a GitHub issue with label "security" and "private" visibility.
                   At the same time, notify the Security Champion in your team. For
                   critical vulnerabilities, contact the CISO directly
                   (ciso@datapulse.it).
                """,
    },
    {
        "doc_id": "GUIDE-001",
        "title": "Operations Guide - Handling Customer Requests",
        "category": "guide",
        "author": "Customer Success Team",
        "creation_date": "2026-02-28",
        "validity_date": None,
        "text": """
                OPERATIONS GUIDE - HANDLING CUSTOMER REQUESTS
                Customer Success Team - DataPulse S.p.A.

                INTAKE CHANNELS
                - Email: support@datapulse.it (SLA: reply within 4 business hours)
                - In-app chat: Intercom widget (SLA: reply within 30 minutes during business hours)
                - Phone: dedicated number for Premium customers (09:00-18:00, Mon-Fri)
                - Self-service portal: https://support.datapulse.it

                CLASSIFICATION AND PRIORITY
                P1 (Critical): system unusable, customer production affected.
                               Resolution SLA: 4 hours. Immediate escalation to Tech Lead.
                P2 (High):     main feature degraded, workaround available.
                               Resolution SLA: 8 business hours.
                P3 (Medium):   non-critical issue, no operational blocker.
                               Resolution SLA: 3 business days.
                P4 (Low):      clarification request, feedback, suggestion.
                               Reply SLA: 5 business days.

                ESCALATION REQUIRING ACCESS TO CUSTOMER DATA
                If resolving a ticket requires access to customer data:
                1. Verify the contract includes the "support access" clause.
                2. Request temporary Level 1 access via ServiceNow (type: SUPP-ACCESS).
                3. Document the access performed and the data consulted in the ticket.
                4. Revoke the access within 48 hours of ticket closure.

                FORMAL COMPLAINTS
                Formal complaints (certified email PEC or registered mail) must be
                forwarded within 24 hours to the Legal Office (legal@datapulse.it),
                which handles the official response within the statutory deadlines.
                """,
    },
    {
        "doc_id": "GUIDE-002",
        "title": "Consent Register Guide - GDPR Compliance",
        "category": "guide",
        "author": "Compliance Office",
        "creation_date": "2025-07-01",
        "validity_date": "2026-07-01",
        "text": """
                CONSENT REGISTER GUIDE - GDPR COMPLIANCE
                Compliance Office - DataPulse S.p.A.

                PURPOSE
                This guide describes how DataPulse collects, records, and manages
                user consent under the GDPR, with reference to Art. 7 (Conditions
                for consent) and Art. 4(11) (Definition of consent).

                REGISTER STRUCTURE
                For every consent-based processing, the register includes:
                - Data subject identity (anonymized for the internal register)
                - Date and time of consent collection
                - Version of the privacy notice at the time of consent
                - Collection channel (web form, email, in-app)
                - Specific purpose for which consent was given
                - Status: active / withdrawn / expired

                CONSENT COLLECTION
                Consent must be freely given, specific, informed, and unambiguous.
                The following are not valid:
                - Pre-ticked consents (checkboxes already selected).
                - Bundled consents (a single click for multiple purposes).
                - Consent as a condition of service (except where allowed by law).

                CONSENT WITHDRAWAL
                Withdrawal must be possible at any time, with the same ease as it
                was given. DataPulse provides:
                - Privacy panel in the user profile (immediate withdrawal via UI).
                - Email to privacy@datapulse.it (processed within 72 hours).
                - Paper form for enterprise customers (processed within 5 business days).
                After withdrawal, processing must stop immediately. If it cannot
                stop due to legal obligations, the data subject must be informed.

                REGISTER RETENTION
                The consent register must be retained for 10 years from the date
                of collection or for the full duration of the contract + 5 years
                (the longer period applies), as required by the corporate data
                retention policy.
                """,
    },
    {
        "doc_id": "REP-001",
        "title": "Project Report - Cloud Infrastructure Migration (Q1 2025)",
        "category": "report",
        "author": "Architecture Team",
        "creation_date": "2025-03-31",
        "validity_date": None,
        "text": """
                PROJECT REPORT - CLOUD INFRASTRUCTURE MIGRATION
                Architecture Team - Q1 2025 - DataPulse S.p.A.

                EXECUTIVE SUMMARY
                The migration of the on-premise infrastructure to AWS was completed
                in Q1 2025 on time and on budget. Uptime of critical services
                during the migration was 99.7%.

                TARGET ARCHITECTURE
                - Compute: EKS (managed Kubernetes) with auto-scaling on EC2 Spot + On-demand.
                - Database: RDS PostgreSQL Multi-AZ for transactional data; DynamoDB for
                  sessions and high-throughput caching.
                - Storage: S3 with lifecycle policies for automatic tiering (Standard → IA → Glacier).
                - Networking: VPC with private/public subnets, Transit Gateway for
                  multi-account connectivity, Direct Connect linking to the legacy data center.
                - Security: AWS IAM with least-privilege, KMS for data-at-rest encryption,
                  GuardDuty for threat detection, CloudTrail for audit logs.

                POST-MIGRATION PERFORMANCE DATA
                - Average API latency: reduced from 210ms to 85ms (-60%).
                - Infrastructure costs: 35% reduction vs. the previous on-premise.
                - Scalability: capacity to handle 10x traffic spikes with no manual intervention.

                LESSONS LEARNED
                - The data migration phase required 2 extra weeks for schema alignment
                  between the legacy DB and RDS. Recommendation: budget more time
                  for schema mapping at the planning stage.
                - Using Spot Instances cut compute costs by 40%, but requires
                  preemption handling with retry logic in application code.
                - CloudTrail was essential for the post-migration compliance audit
                  requested by the Compliance Office.

                NEXT STEPS
                - Q2 2025: roll out multi-region disaster recovery.
                - Q3 2025: integrate AWS Security Hub for centralized alerting.
                - Q4 2025: cost optimization with Savings Plans and Reserved Instances.
                """,
    },
]


# ==============================================================================
# DATA STRUCTURES
# ==============================================================================


@dataclass
class Document:
    """Represents a single document chunk after ingestion."""

    chunk_id: str  # e.g. "POL-001_chunk000" - unique chunk identifier
    doc_id: str  # source document ID (used for citations and dedup)
    title: str
    category: str
    author: str
    creation_date: str
    validity_date: Optional[str]
    text: str  # chunk text (used for indexing and retrieval)
    original_text: str  # full document text (used to assemble the LLM context)


@dataclass
class RetrievalResult:
    """Single retrieval result with aggregate score and signal breakdown."""

    document: Document
    hybrid_score: float  # final normalized score in [0, 1]
    semantic_score: float  # contribution from vector similarity
    bm25_score: float  # contribution from BM25 search
    recency_score: float  # contribution from the structured signal (date + validity)
    rank: int  # position in the ordered list (1-indexed)


@dataclass
class RAGResponse:
    """Full RAG system response ready to be returned to the user."""

    query: str
    answer: str
    sources: list[RetrievalResult]
    confidence: float  # mean of top-k hybrid scores: proxy for retrieval quality
    response_timestamp: str
    retrieval_latency_ms: float
    llm_latency_ms: float


# ==============================================================================
# COMPONENT 1: DOCUMENT PROCESSOR
# ==============================================================================


class DocumentProcessor:
    """
    Responsible for document ingestion and chunking.

    Why chunking is necessary:
    - Embedding models (and LLMs) have a limited context window
      (~512 tokens for sentence-transformers). Long documents must be split
      so each chunk fits into a single coherent vector.
    - Smaller chunks raise retrieval granularity: the relevant section is
      isolated without dragging irrelevant text into the LLM context.
    - The `overlap` parameter ensures that information straddling the boundary
      between two consecutive chunks is not lost.

    Chosen chunking strategy: split by paragraphs (double newline) with
    aggregation up to the target size. This approach respects natural semantic
    units of the text better than a plain character-based split.

    Default parameters:
    - chunk_size=500 characters ≈ 3-5 sentences in English. Enough for a
      coherent semantic unit; small enough for the encoding window.
    - overlap=100 characters: about 20% of the chunk size, a commonly used
      value.
    """

    def __init__(self, chunk_size: int = 500, overlap: int = 100):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def process_knowledge_base(self, kb: list[dict]) -> list[Document]:
        """Process the entire knowledge base and return the flat list of chunks."""
        documents = []
        for entry in kb:
            clean_text = entry["text"].strip()
            chunks = self._chunking(clean_text)
            for i, chunk in enumerate(chunks):
                documents.append(
                    Document(
                        chunk_id=f"{entry['doc_id']}_chunk{i:03d}",
                        doc_id=entry["doc_id"],
                        title=entry["title"],
                        category=entry["category"],
                        author=entry["author"],
                        creation_date=entry["creation_date"],
                        validity_date=entry["validity_date"],
                        text=chunk,
                        original_text=clean_text,
                    )
                )
        return documents

    def _chunking(self, text: str) -> list[str]:
        """
        Split the text into chunks with overlap based on paragraph boundaries.
        When a single paragraph exceeds the target size, it is emitted as a
        standalone chunk to preserve semantic coherence.
        """
        paragraphs = [p.strip() for p in re.split(r"\n\n+", text) if p.strip()]
        chunks: list[str] = []
        current_chunk = ""

        for paragraph in paragraphs:
            if len(current_chunk) + len(paragraph) + 2 <= self.chunk_size:
                current_chunk = (current_chunk + "\n\n" + paragraph).strip()
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                # Overlap: carry the tail of the previous chunk to maintain
                # semantic continuity between adjacent chunks.
                tail = current_chunk[-self.overlap :] if self.overlap < len(current_chunk) else current_chunk
                current_chunk = (tail + "\n\n" + paragraph).strip()

        if current_chunk:
            chunks.append(current_chunk)

        return chunks if chunks else [text]


# ==============================================================================
# COMPONENT 2: EMBEDDING ENGINE
# ==============================================================================


class EmbeddingEngine:
    """
    Wrapper around SentenceTransformers for embedding generation.

    Chosen model: paraphrase-multilingual-MiniLM-L12-v2
    - Native support for English (and 50+ languages): keeps the door open to
      multilingual corpora without swapping the encoder.
    - Optimized for paraphrase similarity: captures rephrasing relationships
      better than generic English-only models.
    """

    DEFAULT_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"

    def __init__(self, model_name: str = DEFAULT_MODEL):
        print(f"[EmbeddingEngine] Loading model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.model_name = model_name

    def encode(self, texts: list[str]) -> np.ndarray:
        """Return an (N, D) matrix with the embeddings of the text batch."""
        return self.model.encode(texts, convert_to_numpy=True, show_progress_bar=False)

    def encode_query(self, query: str) -> np.ndarray:
        """Encode a single query; return a 1D vector of shape (D,)."""
        return self.model.encode([query], convert_to_numpy=True)[0]


# ==============================================================================
# COMPONENT 3: VECTOR STORE (ChromaDB)
# ==============================================================================


class VectorStore:
    """
    Vector index based on ChromaDB for semantic retrieval.

    Why ChromaDB:
    - Simpler API than FAISS (no C++ build step).
    - Native support for metadata filters on category, date, author.
    - In-memory storage for the demo; switching to
      chromadb.PersistentClient() makes the index persistent across runs.

    Cosine metric:
    Measures directional similarity between vectors, invariant to magnitude.
    The standard choice for text embeddings because the vector norm carries
    no meaningful semantic information.

    With the cosine metric, ChromaDB returns distances in the [0, 2] range
    (0 = identical vectors, 2 = diametrically opposite vectors).
    They are converted into similarity scores: score = max(0, 1 - distance).

    Note on embeddings: embeddings are precomputed with EmbeddingEngine and
    passed explicitly to ChromaDB. This avoids loading the model twice and
    gives full control over the encoding process.
    """

    _COLLECTION_NAME = "datapulse_kb"

    def __init__(self, embedding_engine: EmbeddingEngine):
        self.embedding_engine = embedding_engine
        # EphemeralClient (ChromaDB >= 0.4) creates an in-memory client that
        # does not require a separate server. Fallback to chromadb.Client() for
        # older versions.
        try:
            self.client = chromadb.EphemeralClient()
        except AttributeError:
            self.client = chromadb.Client()

        self.collection = self.client.create_collection(
            name=self._COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )

    def index(self, documents: list[Document]) -> None:
        """Insert the chunks into the vector store with their embeddings and metadata."""
        ids = [doc.chunk_id for doc in documents]
        texts = [doc.text for doc in documents]
        # Batched precomputation: more efficient than per-chunk encoding
        embeddings = self.embedding_engine.encode(texts).tolist()
        metadata = [
            {
                "doc_id": doc.doc_id,
                "title": doc.title,
                "category": doc.category,
                "author": doc.author,
                "creation_date": doc.creation_date,
                "validity_date": doc.validity_date or "N/A",
            }
            for doc in documents
        ]
        self.collection.add(documents=texts, embeddings=embeddings, metadatas=metadata, ids=ids)
        print(f"[VectorStore] Indexed {len(ids)} chunks.")

    def search(self, query: str, top_k: int = 5) -> list[tuple[str, float, dict]]:
        """
        Semantic search. Returns a list of (chunk_id, similarity_score, metadata).
        similarity_score is normalized to [0, 1]: 1 = maximum similarity.
        """
        n = min(top_k, self.collection.count())
        if n == 0:
            return []
        query_emb = self.embedding_engine.encode_query(query).tolist()
        results = self.collection.query(
            query_embeddings=[query_emb],
            n_results=n,
            include=["documents", "metadatas", "distances"],
        )
        output = []
        for chunk_id, distance, meta in zip(
            results["ids"][0],
            results["distances"][0],
            results["metadatas"][0],
        ):
            score = max(0.0, 1.0 - distance)
            output.append((chunk_id, score, meta))
        return output


# ==============================================================================
# COMPONENT 4: BM25 ENGINE
# ==============================================================================


class BM25Engine:
    """
    Lexical search engine based on BM25Okapi.

    Why BM25 on top of semantic embeddings:
    - Embeddings capture meaning well but are unreliable on rare technical
      terms, acronyms, and codes (e.g. "RDA-01", "DORA", "IRP-003",
      "POL-001"): these tokens are often missing from the model vocabulary
      and end up projected into poorly distinguishable regions of the
      embedding space.
    - BM25 is term-frequency based: it pinpoints documents that contain
      exactly the query terms, even without semantic context.
    - The hybrid combination (semantic + BM25) is state of the art for RAG
      systems over technical/operational knowledge bases (see the BEIR
      benchmark): it lowers the false-negative rate of either strategy
      taken in isolation.

    BM25Okapi is the standard variant:
    - k1=1.5 (default): balances the influence of term frequency.
    - b=0.75 (default): document length normalization.
    These hyperparameters are empirically validated across many technical
    corpora (Robertson et al. 1994, Robertson & Zaragoza 2009).
    """

    def __init__(self):
        self._index: Optional[BM25Okapi] = None
        self.documents: list[Document] = []

    def index(self, documents: list[Document]) -> None:
        """Build the BM25 index over the chunk corpus."""
        self.documents = documents
        tokenized_corpus = [self._tokenize(doc.text) for doc in documents]
        self._index = BM25Okapi(tokenized_corpus)
        print(f"[BM25Engine] Indexed {len(documents)} chunks.")

    def search(self, query: str, top_k: int = 5) -> list[tuple[int, float]]:
        """
        BM25 search. Returns a list of (corpus_index, normalized_score).
        The raw BM25 score is min-max normalized to [0, 1] so it is
        comparable with the semantic score in the hybrid fusion.
        """
        scores = self._index.get_scores(self._tokenize(query))
        s_max, s_min = scores.max(), scores.min()
        # Normalization: handle the degenerate case where all scores are
        # identical (typically all zeros = no query term present in the corpus).
        if s_max - s_min > 1e-10:
            scores_norm = (scores - s_min) / (s_max - s_min)
        else:
            scores_norm = np.zeros_like(scores)
        top_indices = np.argsort(scores_norm)[::-1][:top_k]
        return [(int(i), float(scores_norm[i])) for i in top_indices]

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        """
        Simple tokenization: lowercase + alphanumeric token extraction.
        Stemming and lemmatization are skipped to keep zero dependency on
        language-specific NLP libraries (spaCy, NLTK).
        """
        return re.findall(r"\b[a-zA-ZÀ-ÿ0-9]+\b", text.lower())


# ==============================================================================
# COMPONENT 5: HYBRID RETRIEVER
# ==============================================================================


class HybridRetriever:
    """
    Combines three signals into a single relevance score:
      1. Semantic similarity from the VectorStore.
      2. BM25 lexical match from BM25Engine.
      3. Recency, a structured signal based on the document's date metadata.

    "Recency" is the standard information-retrieval term for a temporal score
    that rewards more recent documents, optionally combined with a penalty
    for expired ones.

    Fusion formula:
        text_score   = alpha * semantic_score + (1 - alpha) * bm25_score
        hybrid_score = (1 - gamma) * text_score + gamma * recency_score

    Choosing alpha = 0.6 (skewed toward semantic):
    - For natural-language queries, semantic understanding is more
      informative than exact term matching.
    - alpha > 0.5 favors the semantic signal, useful for queries rephrased
      relative to the document text (e.g. "regulations to comply with" vs. "GDPR").
    - The BM25 contribution (0.4) remains enough to surface documents with
      exact technical codes when the query contains them.

    Choosing gamma = 0.15 (weight of the structured signal):
    - The project brief requires the hybrid retrieval to combine semantic
      relevance with structured signals (metadata, date).
    - A small weight prevents the recency score from drowning out the text
      match: a perfectly relevant one-year-old document must still win over
      a marginal but newly published one.
    - A non-zero weight is still enough to break ties between textually
      equivalent documents of very different ages, which matters for
      compliance policies that get periodically revised.

    Recency score computation:
    - Exponential decay exp(-Δdays / 730) on the creation date. The choice
      of tau = 730 days makes a one-year-old document worth about 0.61, a
      two-year-old about 0.37: a nudge toward newer items without zeroing
      out the older ones.
    - Multiplicative penalty 0.3 if validity_date is in the past: the
      document stays visible but is demoted relative to its still-valid
      peers.
    - Documents with no parseable creation_date receive a neutral score (0.5).

    Optional filters on metadata:
    - filters={"categories": {"policy", "guide"}} restricts retrieval to the
      listed categories (useful for targeted queries, e.g. "only official policies").
    - filters={"min_date": "2025-06-01"} excludes documents older than the
      threshold (useful for queries like "info updated in recent months").
    - Filters are applied post-retrieval on the candidate pool: no change to
      the underlying index APIs.

    Alternative considered: Reciprocal Rank Fusion (RRF).
    RRF is more robust to absolute score scales (no normalization needed) but
    is less interpretable and lends itself less naturally to integrating a
    third signal (recency).

    Deduplication: if the same chunk appears in both strategies' results, the
    respective scores are aggregated (the second pass updates the value, the
    missing one stays at 0.0). This avoids double-counting.
    """

    TAU_RECENCY_DAYS: float = 730.0  # half-life (~2 years)
    EXPIRED_VALIDITY_PENALTY: float = 0.3  # multiplicative on recency score

    def __init__(
        self,
        vector_store: VectorStore,
        bm25_engine: BM25Engine,
        documents: list[Document],
        alpha: float = 0.6,
        gamma: float = 0.15,
    ):
        self.vector_store = vector_store
        self.bm25_engine = bm25_engine
        self.documents = documents
        self.alpha = alpha
        self.gamma = gamma
        # chunk_id -> Document map for O(1) lookup during fusion
        self._id_to_doc: dict[str, Document] = {doc.chunk_id: doc for doc in documents}

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        filters: Optional[dict] = None,
    ) -> list[RetrievalResult]:
        """
        Run hybrid retrieval and return the ordered top_k results.

        The candidate pool is 2 * top_k so BM25 can surface documents that
        are semantically marginal but lexically exact, and vice versa. When
        metadata filters are active, the pool is further expanded (4 * top_k)
        to reduce the risk that the filter empties the final list.
        """
        pool_multiplier = 4 if filters else 2
        pool = top_k * pool_multiplier

        # Collect candidates from the two indices
        semantic_candidates = self.vector_store.search(query, top_k=pool)
        bm25_candidates = self.bm25_engine.search(query, top_k=pool)

        # Aggregate scores into a chunk_id-keyed dictionary
        scores: dict[str, dict] = {}

        for chunk_id, sem_score, _ in semantic_candidates:
            scores[chunk_id] = {"semantic_score": sem_score, "bm25_score": 0.0}

        for idx, bm25_score in bm25_candidates:
            chunk_id = self.documents[idx].chunk_id
            if chunk_id in scores:
                scores[chunk_id]["bm25_score"] = bm25_score
            else:
                scores[chunk_id] = {"semantic_score": 0.0, "bm25_score": bm25_score}

        allowed_categories = filters.get("categories") if filters else None
        min_date = filters.get("min_date") if filters else None

        # Compute hybrid score, apply filters, sort
        results: list[RetrievalResult] = []
        for chunk_id, data in scores.items():
            if chunk_id not in self._id_to_doc:
                continue
            doc = self._id_to_doc[chunk_id]

            if allowed_categories is not None and doc.category not in allowed_categories:
                continue
            # ISO YYYY-MM-DD dates compare lexicographically as they do
            # chronologically: no parsing needed for the filter.
            if min_date is not None and doc.creation_date < min_date:
                continue

            text_score = self.alpha * data["semantic_score"] + (1 - self.alpha) * data["bm25_score"]
            rec_score = self._recency(doc)
            hybrid_score = (1 - self.gamma) * text_score + self.gamma * rec_score

            results.append(
                RetrievalResult(
                    document=doc,
                    hybrid_score=hybrid_score,
                    semantic_score=data["semantic_score"],
                    bm25_score=data["bm25_score"],
                    recency_score=rec_score,
                    rank=0,
                )
            )

        results.sort(key=lambda r: r.hybrid_score, reverse=True)
        for i, r in enumerate(results[:top_k]):
            r.rank = i + 1

        return results[:top_k]

    @classmethod
    def _recency(cls, doc: Document) -> float:
        """
        Return a recency score in (0, 1] based on the document's date metadata.
        Documents without a valid creation_date receive a neutral value (0.5)
        so they are not arbitrarily penalized.
        """
        try:
            d_created = date.fromisoformat(doc.creation_date)
        except (ValueError, TypeError):
            return 0.5

        delta_days = max(0, (date.today() - d_created).days)
        recency = math.exp(-delta_days / cls.TAU_RECENCY_DAYS)

        if doc.validity_date:
            try:
                d_validity = date.fromisoformat(doc.validity_date)
                if d_validity < date.today():
                    recency *= cls.EXPIRED_VALIDITY_PENALTY
            except ValueError:
                pass

        return recency


# ==============================================================================
# COMPONENT 6: LLM PIPELINE
# ==============================================================================


class LLMPipeline:
    """
    Unified interface over two LLM providers: Ollama and OpenAI.

    The `provider` argument selects the backend at instantiation time; the
    rest of the system (RAGSystem, prompt, output) is identical in both cases.

    OLLAMA (provider="ollama")
    - Fully local execution: no data transmitted to external providers.
    - Default model: llama3.2 (3B parameters)

    OPENAI (provider="openai")
    - Higher generative quality, lower latency than local models.
    - Default model: gpt-4o-mini.
    - API key read from the OPENAI_API_KEY environment variable.
    - Caveat: document context is sent to OpenAI servers. In production,
      vet the terms of service against corporate data policies.

    temperature=0.1 on both providers:
    Near-deterministic responses. For a corporate assistant, reproducibility
    matters more than creative variety.

    Prompt structure (system/context/question/instructions pattern):
    - System role: constrains the LLM to answer only from the provided context.
    - Context: retrieved documents with identifying metadata.
    - Question: the user's original query, unrephrased.
    - Output instructions: structure, citation requirement, handling of
      "information not available".
    This schema reduces hallucinations by anchoring generation to real
    sources and requiring the LLM to explicitly flag gaps.
    """

    PROVIDER_OLLAMA = "ollama"
    PROVIDER_OPENAI = "openai"

    _DEFAULT_MODELS = {
        PROVIDER_OLLAMA: "llama3.2",
        PROVIDER_OPENAI: "gpt-4o-mini",
    }

    def __init__(self, provider: str = PROVIDER_OLLAMA, model: Optional[str] = None):
        self.provider = provider
        self.model_name = model or self._DEFAULT_MODELS.get(provider, "")

        if provider == self.PROVIDER_OLLAMA:
            self._init_ollama()
        elif provider == self.PROVIDER_OPENAI:
            self._init_openai()
        else:
            raise ValueError(f"Unsupported provider: '{provider}'. Allowed values: ollama, openai.")

    def _init_ollama(self) -> None:
        from langchain_ollama import OllamaLLM

        self.llm = OllamaLLM(model=self.model_name, temperature=0.1)

    def _init_openai(self) -> None:
        from langchain_openai import ChatOpenAI

        key = os.environ.get("OPENAI_API_KEY")
        if not key:
            raise EnvironmentError(
                "OPENAI_API_KEY environment variable is not set.\nRun: export OPENAI_API_KEY='sk-...'"
            )
        # ChatOpenAI returns an AIMessage object; generate() handles it.
        self.llm = ChatOpenAI(model=self.model_name, temperature=0.1, api_key=key)

    def generate(self, query: str, context: str, sources_meta: list[dict]) -> str:
        """Generate the synthesized answer given the retrieved context."""
        prompt = self._build_prompt(query, context, sources_meta)
        response = self.llm.invoke(prompt)
        # ChatOpenAI returns an AIMessage with a .content attribute;
        # OllamaLLM returns a plain string.
        return response.content if hasattr(response, "content") else str(response)

    def _build_prompt(self, query: str, context: str, sources_meta: list[dict]) -> str:
        """Assemble the prompt with clean separation between system, context, and question."""
        sources_list = "\n".join(
            f"  [{m['doc_id']}] {m['title']} "
            f"(category: {m['category']}, author: {m['author']}, "
            f"date: {m['creation_date']}, validity: {m.get('validity_date') or 'no expiry'})"
            for m in sources_meta
        )
        return f"""
                    You are the knowledge management assistant of DataPulse S.p.A.
                    Answer EXCLUSIVELY based on the corporate documents provided in the context.
                    If the required information is not present, reply: "The requested
                    information is not available in the current knowledge base." Do not
                    invent procedures or regulations.

                    AVAILABLE DOCUMENTS:
                    {sources_list}

                    EXTRACTED CONTEXT:
                    {context}

                    QUESTION:
                    {query}

                    INSTRUCTIONS:
                    1. Provide a concise and structured answer with the key points.
                    2. Cite the documents used (e.g. "according to POL-001...").
                    3. If the procedure has sequential steps, number them.
                    4. At the end, report the validity date of the cited sources when present.

                    ANSWER:
                """


# ==============================================================================
# COMPONENT 7: RAG SYSTEM - ORCHESTRATOR
# ==============================================================================


class RAGSystem:
    """
    Orchestrator that coordinates all RAG system components.

    Execution flow for a query:
    1. HybridRetriever.retrieve() → top-k RetrievalResult.
    2. Deduplication by doc_id: if multiple chunks from the same document are
        retrieved, the full original text is used once.
        Rationale: feeding the LLM separated fragments of the same document
        increases redundancy and reduces the room for other relevant documents.
    3. Context assembly: original texts with identifying separators.
    4. LLMPipeline.generate() -> answer string.
    5. Building RAGResponse with metrics and source metadata.

    Confidence computation:
    The mean of the top-k hybrid scores is used as a proxy for retrieval
    quality.
    - High confidence -> the corpus contains documents very relevant to the
      query -> answer likely complete and accurate.
    - Low confidence -> retrieval is weak -> the answer may be incomplete or
      based on marginal documents.

    Known limitations of the current proxy and extension directions:
    - Confidence only measures retrieval quality, not generation. The LLM can
      still produce hallucinations or imprecise syntheses from relevant
      sources. The three standard RAG metrics are not covered:
        * faithfulness     : how well the answer adheres to cited passages
        * answer relevancy : how relevant the answer is to the question asked
        * context precision: fraction of the retrieved context actually used
      In production these metrics would be measured with RAGAS (or equivalent)
      on a golden Q&A set: needs a labeled dataset and an LLM-as-judge, out
      of scope here but the natural next step.
    - Re-ranking: after hybrid retrieval one could apply a cross-encoder
      (e.g. ms-marco-MiniLM-L-6-v2) to reorder the top-N candidates based on
      a joint query-document evaluation. It raises precision but doubles
      retrieval latency; worthwhile with corpora of hundreds of documents
      or more, not with a few dozen as in this case.
    - Query expansion: automatic question rephrasing (HyDE, multi-query) to
      generate several variants and merge the results. Improves recall on
      ambiguous queries at the cost of an extra LLM call before retrieval.
    """

    def __init__(
        self,
        top_k: int = 4,
        alpha: float = 0.6,
        gamma: float = 0.15,
        use_llm: bool = True,
        provider: str = LLMPipeline.PROVIDER_OLLAMA,
        llm_model: Optional[str] = None,
    ):
        self.top_k = top_k
        self.use_llm = use_llm

        print("\n[RAGSystem] Initializing...")

        self.processor = DocumentProcessor()
        self.embedding_engine = EmbeddingEngine()
        self.bm25_engine = BM25Engine()

        self.documents = self.processor.process_knowledge_base(KNOWLEDGE_BASE)
        n_sources = len(KNOWLEDGE_BASE)
        n_chunks = len(self.documents)
        print(f"[RAGSystem] {n_sources} documents → {n_chunks} chunks (avg {n_chunks // n_sources} chunks/doc).")

        self.vector_store = VectorStore(self.embedding_engine)
        self.vector_store.index(self.documents)
        self.bm25_engine.index(self.documents)

        self.retriever = HybridRetriever(
            self.vector_store,
            self.bm25_engine,
            self.documents,
            alpha=alpha,
            gamma=gamma,
        )

        self.llm_pipeline: Optional[LLMPipeline] = None
        if self.use_llm:
            try:
                self.llm_pipeline = LLMPipeline(provider=provider, model=llm_model)
                model_in_use = self.llm_pipeline.model_name
                print(f"[RAGSystem] LLM ready: {model_in_use} (provider: {provider})")
            except Exception as exc:
                print(f"[RAGSystem] LLM not available ({exc}). Retrieval-only mode active.")
                self.use_llm = False
        else:
            print("[RAGSystem] Retrieval-only mode (LLM disabled).")

        print("[RAGSystem] System ready.\n")

    def ask(self, query: str, filters: Optional[dict] = None) -> RAGResponse:
        """
        Run the full RAG pipeline for a natural-language query.

        `filters` is optional and forwarded to the retriever to restrict the
        candidate pool on structured signals. Accepted schema:
          {"categories": set[str], "min_date": "YYYY-MM-DD"}
        """
        t_start = time.perf_counter()

        results = self.retriever.retrieve(query, top_k=self.top_k, filters=filters)
        retrieval_latency_ms = (time.perf_counter() - t_start) * 1000

        # Confidence score: mean of top-k hybrid scores
        confidence = float(np.mean([r.hybrid_score for r in results])) if results else 0.0

        # Deduplication by doc_id: the document's original text is used to
        # give the LLM the maximum available context per cited source.
        seen_doc_ids: set[str] = set()
        context_parts: list[str] = []
        sources_meta: list[dict] = []

        for r in results:
            doc = r.document
            if doc.doc_id in seen_doc_ids:
                continue
            seen_doc_ids.add(doc.doc_id)
            context_parts.append(f"[{doc.doc_id}] {doc.title}\n{'─' * 60}\n{doc.original_text}")
            sources_meta.append(
                {
                    "doc_id": doc.doc_id,
                    "title": doc.title,
                    "category": doc.category,
                    "author": doc.author,
                    "creation_date": doc.creation_date,
                    "validity_date": doc.validity_date,
                }
            )

        context = "\n\n".join(context_parts)

        t_pre_llm = time.perf_counter()

        if self.use_llm and self.llm_pipeline and results:
            try:
                answer_text = self.llm_pipeline.generate(query, context, sources_meta)
            except Exception as exc:
                answer_text = f"[LLM error: {exc}]\n\nRelevant documents found (retrieval-only):\n" + "\n".join(
                    f"  [{r.document.doc_id}] {r.document.title} (score: {r.hybrid_score:.3f})" for r in results
                )
        elif not results:
            answer_text = "No relevant documents found in the knowledge base."
        else:
            answer_text = self._retrieval_only_answer(query, results)

        llm_latency_ms = (time.perf_counter() - t_pre_llm) * 1000

        return RAGResponse(
            query=query,
            answer=answer_text,
            sources=results,
            confidence=confidence,
            response_timestamp=datetime.now().isoformat(timespec="seconds"),
            retrieval_latency_ms=retrieval_latency_ms,
            llm_latency_ms=llm_latency_ms,
        )

    @staticmethod
    def _retrieval_only_answer(query: str, results: list[RetrievalResult]) -> str:
        """
        Textual fallback when the LLM is not available.
        Returns the most relevant excerpts without generative synthesis.
        """
        lines = [f"Query: {query}\n\nMost relevant excerpts from the knowledge base:\n"]
        for r in results:
            doc = r.document
            lines.append(f"\n[{doc.doc_id}] {doc.title} (score: {r.hybrid_score:.3f})\n")
            lines.append(textwrap.fill(doc.text[:500], width=80) + "\n[...]")
        return "\n".join(lines)


# ==============================================================================
# RESULTS PRESENTATION
# ==============================================================================


def print_response(response: RAGResponse, width: int = 80) -> None:
    """Print the RAG response in a readable on-screen format."""
    sep = "=" * width
    sep_light = "-" * width

    print(f"\n{sep}")
    print(f"QUERY: {response.query}")
    print(sep)

    level = "HIGH" if response.confidence >= 0.6 else "MEDIUM" if response.confidence >= 0.3 else "LOW"
    print(
        f"Confidence: {response.confidence:.2%} [{level}]  |  "
        f"Retrieval: {response.retrieval_latency_ms:.0f}ms  |  "
        f"LLM: {response.llm_latency_ms:.0f}ms  |  "
        f"Timestamp: {response.response_timestamp}"
    )
    print(sep_light)
    print("ANSWER:\n")
    # Preserve intentional newlines (e.g. numbered lists from the LLM) while
    # word-wrapping long lines for terminal readability.
    for line in response.answer.split("\n"):
        print(textwrap.fill(line, width=width) if len(line) > width else line)

    print(f"\n{sep_light}")
    print("SOURCES USED:")

    # Deduplication on print: show each source document once even if it
    # contributes with multiple chunks to retrieval.
    printed_doc_ids: set[str] = set()
    for r in response.sources:
        if r.document.doc_id in printed_doc_ids:
            continue
        printed_doc_ids.add(r.document.doc_id)
        validity = r.document.validity_date or "no expiry"
        print(
            f"  [{r.rank}] {r.document.doc_id} - {r.document.title}\n"
            f"       Category: {r.document.category}  |  Author: {r.document.author}\n"
            f"       Created: {r.document.creation_date}  |  Validity: {validity}\n"
            f"       Score: hybrid={r.hybrid_score:.3f}  "
            f"semantic={r.semantic_score:.3f}  BM25={r.bm25_score:.3f}  "
            f"recency={r.recency_score:.3f}"
        )
    print(sep)


# ==============================================================================
# ON-SCREEN CONCLUSIONS
# ==============================================================================


def conclusions(responses: list[RAGResponse], width: int = 80) -> None:
    """
    Concise on-screen summary: aggregate statistics on the three retrieval
    signals (semantic, BM25, recency), corpus coverage, and three dynamic
    observations computed on the actual run metrics.
    """
    if not responses:
        return

    confidences = [r.confidence for r in responses]
    conf_mean = float(np.mean(confidences))
    conf_min = float(np.min(confidences))
    conf_max = float(np.max(confidences))

    all_sources = [f for r in responses for f in r.sources]
    avg_sem = float(np.mean([f.semantic_score for f in all_sources]))
    avg_bm25 = float(np.mean([f.bm25_score for f in all_sources]))
    avg_rec = float(np.mean([f.recency_score for f in all_sources]))

    cited_docs = {f.document.doc_id for r in responses for f in r.sources}

    sep = "=" * width
    print(f"\n{sep}")
    print("CONCLUSIONS")
    print(sep)
    print(f"Queries run      : {len(responses)}")
    print(f"Confidence       : mean {conf_mean:.2%}  range [{conf_min:.2%}, {conf_max:.2%}]")
    print(f"Mean source scores: semantic={avg_sem:.2f}  BM25={avg_bm25:.2f}  recency={avg_rec:.2f}")
    print(f"Corpus coverage  : {len(cited_docs)}/{len(KNOWLEDGE_BASE)} documents surfaced")

    observations: list[str] = []
    if avg_bm25 > avg_sem + 0.05:
        observations.append(
            "BM25 drives the ranking: expected behavior when queries contain "
            "verbatim codes or acronyms (POL-001, GDPR). It would only be a "
            "red flag if it persisted on pure natural-language queries."
        )
    elif avg_sem > avg_bm25 + 0.05:
        observations.append(
            "Semantic drives the ranking: the multilingual embedding is "
            "working well on queries rephrased relative to the document text."
        )
    else:
        observations.append(
            "Semantic and BM25 balanced: neither signal dominates, alpha=0.6 is well calibrated on this corpus."
        )

    if avg_rec < 0.40:
        observations.append(
            "Low recency: part of the corpus is expired or aging, the "
            "structured signal is correctly demoting obsolete documents "
            "without hiding them."
        )
    elif avg_rec > 0.70:
        observations.append(
            "High recency: corpus mostly fresh, the structured signal "
            "carries little weight today but remains useful as a shield "
            "as the corpus ages."
        )
    else:
        observations.append(
            "Mid-range recency: corpus halfway between fresh and near "
            "expiry, the scenario where the structured signal brings the "
            "most value to ranking."
        )

    if conf_max - conf_min > 0.30:
        observations.append(
            "Wide confidence spread: the system discriminates well between "
            "covered and marginal queries, useful for threshold-based "
            "fallback policies."
        )
    else:
        observations.append(
            "Narrow confidence spread: small corpus, BM25 saturates and "
            "scores compress. At larger scale it would be worth evaluating "
            "Reciprocal Rank Fusion."
        )

    print("\nObservations:")
    for o in observations:
        print(textwrap.fill(o, width=width, initial_indent="  - ", subsequent_indent="    "))
    print(sep)


# ==============================================================================
# OUTPUT SAVING
# ==============================================================================


def save_to_markdown(responses: list[RAGResponse], path: str) -> None:
    """Serialize a list of RAGResponse into a Markdown file."""
    lines = [
        f"# RAG Output - DataPulse S.p.A.",
        f"",
        f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"",
    ]
    for i, r in enumerate(responses, start=1):
        level = "HIGH" if r.confidence >= 0.6 else "MEDIUM" if r.confidence >= 0.3 else "LOW"
        lines += [
            f"---",
            f"",
            f"## Query {i}",
            f"",
            f"> {r.query}",
            f"",
            f"**Confidence:** {r.confidence:.2%} [{level}] &nbsp;|&nbsp; "
            f"Retrieval: {r.retrieval_latency_ms:.0f}ms &nbsp;|&nbsp; "
            f"LLM: {r.llm_latency_ms:.0f}ms &nbsp;|&nbsp; "
            f"Timestamp: {r.response_timestamp}",
            f"",
            f"### Answer",
            f"",
            r.answer.strip(),
            f"",
            f"### Sources",
            f"",
            f"| # | Document | Category | Author | Created | Validity | Hybrid score |",
            f"|---|----------|----------|--------|---------|----------|--------------|",
        ]
        seen_doc_ids: set[str] = set()
        for res in r.sources:
            doc = res.document
            if doc.doc_id in seen_doc_ids:
                continue
            seen_doc_ids.add(doc.doc_id)
            validity = doc.validity_date or "-"
            lines.append(
                f"| {res.rank} | **{doc.doc_id}** - {doc.title} "
                f"| {doc.category} | {doc.author} "
                f"| {doc.creation_date} | {validity} "
                f"| {res.hybrid_score:.3f} |"
            )
        lines.append("")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


# ==============================================================================
# MAIN - DEMO AND TEST CASES
# ==============================================================================


def main() -> None:
    """
    Run the main test cases that cover the project requirements.

    Test queries selected to verify:
    1. Primary use case (data access, GDPR regulations):
       tests retrieval of POL-001, POL-002, FAQ-001, GUIDE-002.
    2. Data breach handling: tests cross-document retrieval (FAQ-001 + POL-002).
    3. Query with explicit document code (POL-001):
       tests the BM25 contribution that should surface the document with that exact code.
    4. Technical infrastructure info: tests retrieval of REP-001, a document
       far from the compliance domain.
    5. Multi-document onboarding: tests the ability to aggregate information
       from MAN-001, FAQ-002, and POL-001 into a single coherent answer.

    LLM provider selection:
      - "ollama"  -> local, no API key, requires Ollama running
      - "openai"  -> requires the OPENAI_API_KEY environment variable
    For retrieval-only mode (no LLM): set use_llm=False.
    """
    # ── Configuration ─────────────────────────────────────────────────────────
    # RAGSystem constructor parameters (edit the call below):
    #   provider="openai"        use GPT-4o-mini instead of Ollama; requires $OPENAI_API_KEY
    #   llm_model="gpt-4o"       overrides the provider's default model
    #   use_llm=False            retrieval-only, skips the LLM call entirely
    #   top_k=N                  number of chunks retrieved per query (default 4)
    #   alpha                    weight of the semantic signal in the text fusion (default 0.6)
    #   gamma                    weight of the recency signal (default 0.15; 0.0 = disabled)
    #
    # Metadata filters - optional second argument of ask():
    #   filters={"categories": {"policy", "guide"}}    limit to policies and guides
    #   filters={"min_date": "2025-06-01"}             drop documents older than the threshold
    #   the two keys can be combined in the same dict.
    system = RAGSystem(top_k=4, alpha=0.6, gamma=0.15, use_llm=True, provider="ollama")

    test_queries = [
        # Test 1 - primary project use case
        (
            "What is the updated procedure for requesting access to customer data "
            "and which regulations must we comply with?"
        ),
        # Test 2 - security incident handling
        ("What should I do if I discover a personal data breach?"),
        # Test 3 - query with specific document code (BM25 signal)
        ("What does POL-001 state about access levels and sanctions?"),
        # Test 4 - technical info retrieval (outside the compliance domain)
        ("What are the results of the cloud migration and what is DataPulse's current AWS architecture?"),
        # Test 5 - multi-document aggregation for onboarding
        ("I am a new employee: what should I do in my first week and which policies must I sign?"),
    ]

    responses: list[RAGResponse] = []
    for query in test_queries:
        response = system.ask(query)
        print_response(response)
        responses.append(response)
        # Small pause between queries to avoid overloading the local LLM
        time.sleep(1)

    # ── Metadata filter demo ──────────────────────────────────────────────────
    # Same query as test 1 but restricted to policies and guides. Shows how
    # the hybrid pipeline can be constrained to a subset of the corpus
    # without rewriting the natural-language query: useful when the user
    # explicitly wants "only official documents" or "only documents updated
    # in recent months".
    print("=" * 70)
    print("FILTER DEMO - retrieval restricted to categories {policy, guide}")
    print("=" * 70)
    filtered_response = system.ask(
        test_queries[0],
        filters={"categories": {"policy", "guide"}},
    )
    print_response(filtered_response)
    responses.append(filtered_response)

    conclusions(responses)

    choice = input("\nDo you want to save the output to a Markdown file? [y/N] ").strip().lower()
    if choice == "y":
        filename = f"rag_output_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.md"
        save_to_markdown(responses, filename)
        print(f"Output saved to: {filename}")
    else:
        print("Output not saved.")


if __name__ == "__main__":
    main()
