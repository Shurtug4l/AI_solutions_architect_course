"""
Diagram generator for the NovaCura Pharma data governance capstone.

Generates the eight PNG figures referenced by the main DOCX report. Run this
file from inside the diagrams/ directory; each function produces a `NN_*.png`
in the working directory.

Style choices
-------------
Consistent with the module 04/05 capstones (portfolio continuity). Each figure
follows three rules:
- straight (horizontal / vertical) arrows in the flow figures; the knowledge
  graph figure is the deliberate exception, a graph cannot be drawn orthogonally
  without lying about its shape;
- no background grid, light background, near-black ink, soft accent colours;
- one figure, one message; legends and labels kept out of the way.

Palette is shared with the rest of the portfolio.

Figure inventory
----------------
    01  Platform logical architecture              (cap. 6)
    02  Data lineage end-to-end flow               (cap. 8)
    03  Knowledge graph conceptual model           (cap. 10)
    04  Governed RAG flow (7 steps + controls)     (cap. 11)
    05  Data lifecycle map (5 phases)              (cap. 7)
    06  Governance domain map                      (cap. 6)
    07  Layered storage / lakehouse (medallion)    (cap. 13)
    08  Maturity model + adoption roadmap          (cap. 14)
"""

from __future__ import annotations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, FancyArrowPatch


# === Shared style ========================================================

BG = "#FFFFFF"
SURFACE = "#FFFFFF"
SURFACE_SOFT = "#F8FAFC"
BORDER = "#CBD5E1"
BORDER_SOFT = "#E2E8F0"
INK = "#0F172A"
INK_SOFT = "#475569"
INK_MUTED = "#94A3B8"

ACCENT = {
    "blue":    "#2563EB",
    "cyan":    "#0891B2",
    "emerald": "#059669",
    "amber":   "#D97706",
    "rose":    "#E11D48",
    "violet":  "#7C3AED",
    "slate":   "#64748B",
}

TINT = {
    "blue":    "#EFF6FF",
    "cyan":    "#ECFEFF",
    "emerald": "#ECFDF5",
    "amber":   "#FFFBEB",
    "rose":    "#FFF1F2",
    "violet":  "#F5F3FF",
    "slate":   "#F1F5F9",
}

DPI = 170


# === Helpers =============================================================


def canvas(figsize):
    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(length=0, labelbottom=False, labelleft=False)
    return fig, ax


def box(ax, x, y, w, h, *, fill=SURFACE, border=BORDER, lw=1.0, accent=None,
        accent_w=0.06, radius=0.03, zorder=2):
    """Rounded rectangle with optional left accent stripe."""
    rect = FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad=0,rounding_size={radius}",
        facecolor=fill, edgecolor=border, linewidth=lw, zorder=zorder,
    )
    ax.add_patch(rect)
    if accent is not None:
        stripe = Rectangle((x, y), accent_w, h, facecolor=accent,
                           edgecolor="none", zorder=zorder + 0.1)
        ax.add_patch(stripe)
        stripe.set_clip_path(rect)
    return rect


def label(ax, x, y, text, *, size=10, weight="normal", color=INK,
          ha="center", va="center"):
    ax.text(x, y, text, fontsize=size, fontweight=weight, color=color,
            ha=ha, va=va, zorder=5)


def arrow_h(ax, x0, x1, y, color=INK_SOFT, lw=1.4):
    ax.annotate("", xy=(x1, y), xytext=(x0, y),
                arrowprops=dict(arrowstyle="-|>", color=color, lw=lw,
                                shrinkA=0, shrinkB=0), zorder=4)


def arrow_v(ax, x, y0, y1, color=INK_SOFT, lw=1.4):
    ax.annotate("", xy=(x, y1), xytext=(x, y0),
                arrowprops=dict(arrowstyle="-|>", color=color, lw=lw,
                                shrinkA=0, shrinkB=0), zorder=4)


def edge(ax, p0, p1, text=None, color=INK_SOFT, lw=1.3, curve=0.0, tsize=8,
         lpos=None):
    """Directed edge for the graph figure. Diagonal allowed by design.

    lpos, if given, places the label at an explicit (x, y) instead of the
    segment midpoint. Curved edges need this: the label offset does not follow
    an arc, so on anything but a straight edge the midpoint drifts off the line.
    """
    style = f"arc3,rad={curve}"
    ax.add_patch(FancyArrowPatch(
        p0, p1, connectionstyle=style, arrowstyle="-|>",
        mutation_scale=12, color=color, lw=lw, zorder=3,
        shrinkA=18, shrinkB=18))
    if text:
        if lpos is None:
            lpos = ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2 + 0.14)
        ax.text(lpos[0], lpos[1], text, fontsize=tsize, color=INK_SOFT,
                ha="center", va="center", zorder=6,
                bbox=dict(boxstyle="round,pad=0.18", fc=BG, ec="none"))


def title_block(ax, x, y, title, subtitle=None):
    ax.text(x, y, title, fontsize=15, fontweight="bold", color=INK,
            ha="left", va="bottom")
    if subtitle:
        ax.text(x, y - 0.25, subtitle, fontsize=9.5, color=INK_MUTED,
                ha="left", va="top")


def band(ax, x, y, w, h, head, body, *, accent):
    """Full-width tinted band: head stacked over body, both centred.

    Stacking (rather than head-left + body-centred) avoids the overlap that
    happens when a long body, centred in a narrow band, runs under the head.
    """
    box(ax, x, y, w, h, fill=TINT["slate"], border=BORDER, lw=1.0)
    label(ax, x + w / 2, y + h * 0.68, head, size=9.5, weight="bold",
          color=INK_SOFT)
    label(ax, x + w / 2, y + h * 0.30, body, size=9.5, weight="bold")


def save(fig, name):
    fig.savefig(name, dpi=DPI, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)


# === Figure 01 - Platform logical architecture ===========================


def fig01_architecture():
    """Five horizontal layers top-down: sources, ingestion/lakehouse,
    governance services (cross-cutting), knowledge, consumption. Governance and
    security run underneath as a full-width band."""
    fig, ax = canvas((13, 9))
    ax.set_xlim(0, 13); ax.set_ylim(0, 9)
    title_block(ax, 0.3, 8.6, "Architettura logica della piattaforma",
                "Sorgenti - Lakehouse - Servizi di governance - Conoscenza - Consumo")

    # Layer 1: sources (4 families)
    srcs = [("Studi clinici", "CTMS - esiti, endpoint", ACCENT["blue"]),
            ("Laboratorio", "LIMS - assay, potenza", ACCENT["emerald"]),
            ("Letteratura", "annotazioni, evidenze", ACCENT["violet"]),
            ("Farmacovigilanza", "ICSR, MedDRA", ACCENT["rose"])]
    w = 2.85; x0 = 0.5; y = 7.05
    for i, (h1, h2, ac) in enumerate(srcs):
        x = x0 + i * (w + 0.2)
        box(ax, x, y, w, 0.95, accent=ac)
        label(ax, x + w / 2, y + 0.62, h1, size=10.5, weight="bold")
        label(ax, x + w / 2, y + 0.26, h2, size=8.5, color=INK_SOFT)
    for i in range(4):
        arrow_v(ax, x0 + i * (w + 0.2) + w / 2, y, y - 0.45)

    # Layer 2: lakehouse medallion
    box(ax, 0.5, 5.35, 12.1, 1.25, fill=TINT["cyan"], border=BORDER)
    label(ax, 0.85, 6.35, "LAKEHOUSE", size=9.5, weight="bold", color=INK_SOFT, ha="left")
    for i, (lab, ac) in enumerate([("Bronze  (raw)", ACCENT["amber"]),
                                    ("Silver  (conforme, pseudonimizzato)", ACCENT["cyan"]),
                                    ("Gold  (feature / KG-ready)", ACCENT["emerald"])]):
        x = 1.0 + i * 3.9
        box(ax, x, 5.55, 3.6, 0.62, accent=ac)
        label(ax, x + 1.8, 5.86, lab, size=9.5, weight="bold")
        if i < 2:
            arrow_h(ax, x + 3.6, x + 3.9, 5.86)
    arrow_v(ax, 6.55, 5.35, 4.95)

    # Layer 3: knowledge layer
    box(ax, 0.5, 3.55, 12.1, 1.25, fill=TINT["violet"], border=BORDER)
    label(ax, 0.85, 4.55, "CONOSCENZA", size=9.5, weight="bold", color=INK_SOFT, ha="left")
    for i, (h1, h2, ac) in enumerate([
            ("Knowledge graph", "entita biomediche, evidenza reificata", ACCENT["violet"]),
            ("Semantic layer", "vocabolari: SNOMED, MedDRA, ChEMBL", ACCENT["blue"])]):
        x = 1.6 + i * 5.6
        box(ax, x, 3.75, 5.0, 0.62, accent=ac)
        label(ax, x + 2.5, 4.20, h1, size=10, weight="bold")
        label(ax, x + 2.5, 3.90, h2, size=8, color=INK_SOFT)
    arrow_v(ax, 6.55, 3.55, 3.15)

    # Layer 4: consumption
    cons = [("Assistente RAG governato", "evidenza citata", ACCENT["blue"]),
            ("Scoring candidati", "modello + lineage", ACCENT["emerald"]),
            ("Reportistica regolatoria", "audit-ready", ACCENT["amber"])]
    w2 = 3.9
    for i, (h1, h2, ac) in enumerate(cons):
        x = 0.6 + i * (w2 + 0.15)
        box(ax, x, 2.05, w2, 0.9, accent=ac)
        label(ax, x + w2 / 2, 2.65, h1, size=10, weight="bold")
        label(ax, x + w2 / 2, 2.32, h2, size=8.5, color=INK_SOFT)

    # Cross-cutting governance/security band (bottom)
    box(ax, 0.5, 0.5, 12.1, 1.15, fill=TINT["slate"], border=BORDER)
    label(ax, 0.85, 1.32, "GOVERNANCE & SICUREZZA (trasversale a ogni layer)",
          size=9.5, weight="bold", color=INK_SOFT, ha="left")
    label(ax, 6.55, 0.82,
          "Catalogo - Metadati - Lineage - Policy & classificazione - Controllo accessi - Audit trail",
          size=10, weight="bold", ha="center")

    ax.set_axis_off()
    save(fig, "01_platform_logical_architecture.png")


# === Figure 02 - Data lineage end-to-end ================================


def fig02_lineage():
    """Left-to-right lineage: four sources fan into a feature set, then model,
    then evidence report. Governance annotation under each transition."""
    fig, ax = canvas((13, 8))
    ax.set_xlim(0, 13); ax.set_ylim(0, 8)
    title_block(ax, 0.3, 7.6, "Lineage end-to-end del programma di repurposing",
                "Ingest - trasformazione - feature - modello - output, con i controlli di governance")

    # four sources (left, stacked, raised to clear the bottom band)
    srcs = [("Esiti clinici", ACCENT["blue"]), ("Assay", ACCENT["emerald"]),
            ("Letteratura", ACCENT["violet"]), ("ICSR / PV", ACCENT["rose"])]
    y_src = [6.35, 5.55, 4.75, 3.95]
    for (name, ac), y in zip(srcs, y_src):
        box(ax, 0.5, y, 2.4, 0.68, accent=ac)
        label(ax, 1.7, y + 0.34, name, size=10, weight="bold")

    fy = 5.15  # flow centreline
    # feature set (center)
    box(ax, 4.6, fy - 0.7, 2.7, 1.4, accent=ACCENT["emerald"], fill=TINT["emerald"])
    label(ax, 5.95, fy + 0.28, "Feature set", size=11, weight="bold")
    label(ax, 5.95, fy - 0.12, "candidato-malattia", size=8.5, color=INK_SOFT)
    label(ax, 5.95, fy - 0.42, "(Gold)", size=8.5, color=INK_SOFT)

    # fan-in arrows into feature set left edge
    for y in y_src:
        ax.add_patch(FancyArrowPatch((2.9, y + 0.34), (4.55, fy),
                     connectionstyle="arc3,rad=0.0", arrowstyle="-|>",
                     mutation_scale=11, color=INK_SOFT, lw=1.2, shrinkA=2, shrinkB=2))

    # model + output
    box(ax, 8.4, fy - 0.5, 2.2, 1.0, accent=ACCENT["amber"], fill=TINT["amber"])
    label(ax, 9.5, fy + 0.18, "Modello", size=11, weight="bold")
    label(ax, 9.5, fy - 0.18, "scoring 3.1", size=8.5, color=INK_SOFT)
    arrow_h(ax, 7.3, 8.4, fy); label(ax, 7.85, fy + 0.24, "train", size=8, color=INK_SOFT)

    box(ax, 11.0, fy - 0.5, 1.8, 1.0, accent=ACCENT["blue"], fill=TINT["blue"])
    label(ax, 11.9, fy + 0.18, "Report", size=10.5, weight="bold")
    label(ax, 11.9, fy - 0.18, "evidenza", size=8.5, color=INK_SOFT)
    arrow_h(ax, 10.6, 11.0, fy); label(ax, 10.8, fy + 0.24, "infer", size=8, color=INK_SOFT)

    # governance annotations (bottom band, pre-wrapped so text stays inside cards)
    box(ax, 0.5, 0.4, 12.3, 2.55, fill=SURFACE_SOFT, border=BORDER_SOFT)
    label(ax, 0.8, 2.72, "Su ogni transizione:", size=9.5, weight="bold",
          color=INK_SOFT, ha="left")
    ann = [("Ingest", "lineage + audit\n(create); Bronze\nimmutabile", ACCENT["slate"]),
           ("Silver", "DQ gate: se un\ncritico fallisce\n-> STOP", ACCENT["rose"]),
           ("Pseudonim.", "chiave nel vault\nesterno; il PHI\nresta nel Bronze", ACCENT["amber"]),
           ("Feature", "run_id +\ninput_manifest_hash\nsu ogni arco", ACCENT["emerald"]),
           ("Output", "ai_generation_log:\nprovenienza\nobbligatoria", ACCENT["blue"])]
    cw = 2.36
    for i, (h, b, ac) in enumerate(ann):
        x = 0.68 + i * (cw + 0.06)
        box(ax, x, 0.6, cw, 1.75, accent=ac)
        label(ax, x + cw / 2, 2.05, h, size=9, weight="bold")
        ax.text(x + cw / 2, 1.28, b, fontsize=6.8, color=INK_SOFT,
                ha="center", va="center", linespacing=1.35)

    ax.set_axis_off()
    save(fig, "02_data_lineage_flow.png")


# === Figure 03 - Knowledge graph conceptual model =======================


def fig03_kg():
    """The domain graph. Diagonal edges are intentional: a graph drawn with only
    orthogonal arrows would misrepresent its topology."""
    fig, ax = canvas((13, 9))
    ax.set_xlim(0, 13); ax.set_ylim(0, 9)
    title_block(ax, 0.3, 8.7, "Modello concettuale del knowledge graph",
                "Entita biomediche, relazioni tipizzate ed evidenza reificata con provenienza")

    # Layout chosen to minimise edge crossings: the Compound-Target-Disease
    # triangle sits at the top, sources feed inward from the periphery.
    nodes = {
        "Target":       (6.5, 7.3, ACCENT["cyan"]),
        "Compound":     (2.7, 5.3, ACCENT["blue"]),
        "Disease":      (10.3, 5.3, ACCENT["rose"]),
        "Evidence":     (6.5, 4.5, ACCENT["slate"]),
        "AdverseEvent": (2.7, 7.5, ACCENT["rose"]),
        "Assay":        (2.5, 2.5, ACCENT["emerald"]),
        "Trial":        (6.5, 1.5, ACCENT["amber"]),
        "Publication":  (10.5, 2.5, ACCENT["violet"]),
    }
    rw, rh = 1.95, 0.82
    for name, (x, y, ac) in nodes.items():
        box(ax, x - rw / 2, y - rh / 2, rw, rh, accent=ac, fill=SURFACE)
        label(ax, x, y, name, size=10, weight="bold")

    def c(n):
        x, y, _ = nodes[n]; return (x, y)

    # top triangle
    edge(ax, c("Compound"), c("Target"), "targets", lpos=(4.0, 6.7))
    edge(ax, c("Target"), c("Disease"), "associated_with", lpos=(9.0, 6.7))
    edge(ax, c("Compound"), c("Disease"), "repurposing_candidate_for",
         color=ACCENT["rose"], lw=2.0, lpos=(6.5, 5.55))
    # adverse event straight down onto compound
    edge(ax, c("AdverseEvent"), c("Compound"), "reported_for", lpos=(3.35, 6.4))
    # evidence supports/refutes the hypothesis, publication reports evidence
    edge(ax, c("Evidence"), c("Compound"), "supports / refutes",
         color=ACCENT["emerald"], lw=1.7, lpos=(4.6, 4.65))
    edge(ax, c("Publication"), c("Evidence"), "reports", lpos=(8.7, 3.35))
    # assay tests compound (against target)
    edge(ax, c("Assay"), c("Compound"), "tests", lpos=(2.05, 3.9))
    edge(ax, c("Assay"), c("Target"), "against", color=INK_MUTED,
         lpos=(4.5, 3.4), tsize=7.5)
    # trial studies compound / investigates disease
    edge(ax, c("Trial"), c("Compound"), "studies", lpos=(4.2, 2.7))
    edge(ax, c("Trial"), c("Disease"), "investigates", lpos=(8.8, 2.7))

    # note on reified evidence
    box(ax, 0.4, 0.4, 5.6, 0.85, fill=TINT["slate"], border=BORDER_SOFT)
    ax.text(0.7, 0.82,
            "Evidence e reificata: porta direzione, forza,\nconfidenza e provenienza (prov:wasDerivedFrom)",
            fontsize=8.3, color=INK_SOFT, ha="left", va="center")

    ax.set_axis_off()
    save(fig, "03_knowledge_graph_conceptual_model.png")


# === Figure 04 - Governed RAG flow ======================================


def fig04_rag():
    """Seven steps left-to-right with governance controls annotated below the
    steps where they bite, plus the KG grounding branch."""
    fig, ax = canvas((13, 7.5))
    ax.set_xlim(0, 13); ax.set_ylim(0, 7.5)
    title_block(ax, 0.3, 7.1, "Flusso RAG governato",
                "Sette passi (nota 07) con i controlli di governance dove agiscono")

    steps = [("1 Source", "fonti ammesse", ACCENT["slate"]),
             ("2 Ingest", "chunk + metadati", ACCENT["emerald"]),
             ("3 Embed", "index versionato", ACCENT["cyan"]),
             ("4 Retrieval", "filtro accessi", ACCENT["rose"]),
             ("5 Context", "solo cio autorizzato", ACCENT["amber"]),
             ("6 Generate", "citazione obbligatoria", ACCENT["blue"]),
             ("7 Feedback", "audit + drift", ACCENT["violet"])]
    w = 1.62; y = 5.2
    for i, (h, b, ac) in enumerate(steps):
        x = 0.35 + i * (w + 0.15)
        box(ax, x, y, w, 1.15, accent=ac)
        label(ax, x + w / 2, y + 0.82, h, size=9.5, weight="bold")
        ax.text(x + w / 2, y + 0.32, b, fontsize=7.4, color=INK_SOFT,
                ha="center", va="center")
        if i < 6:
            arrow_h(ax, x + w, x + w + 0.15, y + 0.57)

    # KG grounding branch feeding step 4/5
    box(ax, 4.3, 3.1, 4.3, 1.0, fill=TINT["violet"], border=BORDER, accent=ACCENT["violet"])
    label(ax, 6.45, 3.78, "Knowledge graph (GraphRAG)", size=10, weight="bold")
    label(ax, 6.45, 3.42, "sottografo asserted, provenienziato", size=8.3, color=INK_SOFT)
    arrow_v(ax, 6.45, 4.1, 5.2)

    # governance controls callouts
    box(ax, 0.35, 0.6, 12.3, 1.9, fill=SURFACE_SOFT, border=BORDER_SOFT)
    label(ax, 0.65, 2.25, "Controlli chiave:", size=9.5, weight="bold", color=INK_SOFT, ha="left")
    ctrl = [("Ammissione", "no classificazione = no corpus", ACCENT["slate"]),
            ("Access-filter", "filtro sul retrieval, non sull'output", ACCENT["rose"]),
            ("Provenienza", "nessuna risposta senza citazione", ACCENT["blue"]),
            ("Freschezza", "cambio modello = reindex completo", ACCENT["cyan"])]
    cw = 2.95
    for i, (h, b, ac) in enumerate(ctrl):
        x = 0.7 + i * (cw + 0.05)
        box(ax, x, 0.8, cw, 1.15, accent=ac)
        label(ax, x + cw / 2, 1.6, h, size=9, weight="bold")
        ax.text(x + cw / 2, 1.1, b, fontsize=7.4, color=INK_SOFT, ha="center", va="center")

    ax.set_axis_off()
    save(fig, "04_governed_rag_flow.png")


# === Figure 05 - Data lifecycle map =====================================


def fig05_lifecycle():
    """Five phases left-to-right; sharing spans the active middle; each phase
    carries owner-risk-control triple."""
    fig, ax = canvas((13, 7)); ax.set_xlim(0, 13); ax.set_ylim(0, 7)
    title_block(ax, 0.3, 6.6, "Mappa del ciclo di vita del dato",
                "Cinque fasi (nota 04); la condivisione attraversa la vita attiva; owner - rischio - controllo")

    phases = [("1 Acquisizione", "ingest, consenso,\nvalidazione origine", ACCENT["blue"]),
              ("2 Catalogazione", "identita, metadati,\nstorage", ACCENT["cyan"]),
              ("3 Uso", "accesso controllato,\nversioning", ACCENT["emerald"]),
              ("4 Archiviazione", "cold storage,\nretention", ACCENT["amber"]),
              ("5 Dismissione", "cancella / anonimizza,\ncatalogo aggiornato", ACCENT["rose"])]
    w = 2.3; y = 3.9
    for i, (h, b, ac) in enumerate(phases):
        x = 0.35 + i * (w + 0.15)
        box(ax, x, y, w, 1.35, accent=ac)
        label(ax, x + w / 2, y + 1.0, h, size=10, weight="bold")
        ax.text(x + w / 2, y + 0.42, b, fontsize=7.2, color=INK_SOFT,
                ha="center", va="center", linespacing=1.4)
        if i < 4:
            arrow_h(ax, x + w, x + w + 0.15, y + 0.68)

    # sharing spanning the active middle (phases 2-4)
    x_a = 0.35 + 1 * (w + 0.15); x_b = 0.35 + 4 * (w + 0.15)
    box(ax, x_a, 2.75, x_b - x_a - 0.4, 0.6, fill=TINT["violet"], border=BORDER_SOFT)
    label(ax, (x_a + x_b) / 2 - 0.2, 3.05, "condivisione / distribuzione (continua nella vita attiva)",
          size=9, weight="bold", color=ACCENT["violet"])

    # bottom: catalog + lineage as the connective tissue
    band(ax, 0.35, 1.0, 12.3, 1.1,
         "SOTTO OGNI FASE", "Data catalog + metadata management + lineage (la fase e evidenza, non teoria)",
         accent=ACCENT["slate"])

    ax.set_axis_off()
    save(fig, "05_data_lifecycle_map.png")


# === Figure 06 - Governance domain map ==================================


def fig06_domains():
    """2x4 grid of governance domains + regulatory band at the bottom."""
    fig, ax = canvas((13, 8)); ax.set_xlim(0, 13); ax.set_ylim(0, 8)
    title_block(ax, 0.3, 7.6, "Mappa dei domini di governance",
                "Otto domini funzionali su una cornice regolatoria pharma-specific")

    domains = [
        ("Catalogo & Metadati", "scheda dataset, metadati, versioning", ACCENT["blue"]),
        ("Data Quality", "6 dimensioni, soglie, scoring, profiling", ACCENT["emerald"]),
        ("Lineage & Provenance", "grafo ingest->output, ricostruzione", ACCENT["cyan"]),
        ("Policy & Classificazione", "4 livelli, mapping policy-dataset", ACCENT["amber"]),
        ("Accessi & Sicurezza", "RBAC, SoD, pseudonimizzazione", ACCENT["rose"]),
        ("Knowledge Graph", "entita, ontologia, evidenza reificata", ACCENT["violet"]),
        ("RAG / Generazione", "retrieval filtrato, citazioni, GraphRAG", ACCENT["blue"]),
        ("Audit & Reporting", "21 CFR Part 11, log AI, audit-ready", ACCENT["slate"]),
    ]
    w, h = 2.92, 1.65; x0 = 0.5; y_top = 4.55; gx = 0.18; gy = 0.28
    for i, (head, body, ac) in enumerate(domains):
        col = i % 4; row = i // 4
        x = x0 + col * (w + gx); y = y_top - row * (h + gy)
        box(ax, x, y, w, h, accent=ac)
        label(ax, x + w / 2, y + h - 0.42, head, size=10, weight="bold")
        ax.text(x + w / 2, y + 0.55, body, fontsize=7.8, color=INK_SOFT,
                ha="center", va="center")

    box(ax, 0.5, 0.5, 12.02, 0.95, fill=TINT["slate"], border=BORDER)
    label(ax, 0.85, 0.97, "NORME", size=9.5, weight="bold", color=INK_SOFT, ha="left")
    label(ax, 6.7, 0.97,
          "GxP (GCP/GLP/GMP)  -  21 CFR Part 11  -  EU Annex 11  -  GAMP 5  -  ALCOA+  -  GDPR art. 9  -  EU AI Act",
          size=9.8, weight="bold", ha="center")

    ax.set_axis_off()
    save(fig, "06_governance_domain_map.png")


# === Figure 07 - Layered storage / lakehouse ============================


def fig07_lakehouse():
    """Medallion layers as horizontal bands with the four sources feeding Bronze
    and governance running underneath."""
    fig, ax = canvas((12, 8.5)); ax.set_xlim(0, 12); ax.set_ylim(0, 8.5)
    title_block(ax, 0.3, 8.2, "Storage a strati: lakehouse medallion",
                "Bronze -> Silver -> Gold; governance e catalogo sotto ogni stadio")

    # sources row
    srcs = [("Clinico", ACCENT["blue"]), ("Assay", ACCENT["emerald"]),
            ("Letteratura", ACCENT["violet"]), ("PV", ACCENT["rose"])]
    for i, (n, ac) in enumerate(srcs):
        x = 1.2 + i * 2.5
        box(ax, x, 7.1, 2.1, 0.7, accent=ac)
        label(ax, x + 1.05, 7.45, n, size=9.5, weight="bold")
        arrow_v(ax, x + 1.05, 7.1, 6.65)

    layers = [("BRONZE", "copia fedele, append-only, immutabile - schema-on-read", ACCENT["amber"], 5.35),
              ("SILVER", "pulito, deduplicato, pseudonimizzato, conformato ai vocabolari", ACCENT["cyan"], 3.95),
              ("GOLD", "feature set, aggregati, viste KG-ready - schema versionato", ACCENT["emerald"], 2.55)]
    for name, body, ac, y in layers:
        box(ax, 1.2, y, 9.6, 1.15, accent=ac, fill=TINT["slate"])
        label(ax, 2.0, y + 0.58, name, size=12, weight="bold", ha="center")
        label(ax, 6.9, y + 0.58, body, size=9, color=INK_SOFT)
    arrow_v(ax, 6.0, 5.35, 5.1); label(ax, 7.2, 5.22, "DQ gate", size=8, color=ACCENT["rose"])
    arrow_v(ax, 6.0, 3.95, 3.7); label(ax, 7.6, 3.82, "policy complete", size=8, color=ACCENT["emerald"])

    band(ax, 1.2, 1.05, 9.6, 1.0, "TRASVERSALE",
         "Catalogo + metadati + lineage + ACL (Delta Lake: ACID, time travel)",
         accent=ACCENT["slate"])

    ax.set_axis_off()
    save(fig, "07_layered_storage_lakehouse.png")


# === Figure 08 - Maturity model + roadmap ===============================


def fig08_maturity():
    """Left: five-rung maturity ladder. Right: three-wave adoption roadmap."""
    fig, ax = canvas((13, 7.5)); ax.set_xlim(0, 13); ax.set_ylim(0, 7.5)
    title_block(ax, 0.3, 7.1, "Modello di maturita e roadmap di adozione",
                "Scala di maturita (nota 09) e adozione incrementale a tre wave")

    # maturity ladder (left)
    rungs = [("1 Ad-hoc", "nessuna regola, conoscenza tribale", ACCENT["rose"]),
             ("2 Aware", "regole informali, applicate a macchia", ACCENT["amber"]),
             ("3 Defined", "policy scritte, owner nominati", ACCENT["cyan"]),
             ("4 Managed", "controlli automatici, audit trail", ACCENT["blue"]),
             ("5 Optimising", "monitoraggio continuo, alert drift/bias", ACCENT["emerald"])]
    for i, (h, b, ac) in enumerate(rungs):
        y = 1.2 + i * 1.02
        x = 0.6 + i * 0.28
        box(ax, x, y, 5.0, 0.9, accent=ac)
        label(ax, x + 0.9, y + 0.45, h, size=9.5, weight="bold")
        ax.text(x + 3.4, y + 0.45, b, fontsize=7.8, color=INK_SOFT, ha="center", va="center")
    label(ax, 1.0, 6.5, "Maturita", size=11, weight="bold", color=INK_SOFT, ha="left")

    # roadmap waves (right)
    label(ax, 7.6, 6.5, "Adozione", size=11, weight="bold", color=INK_SOFT, ha="left")
    waves = [("Wave 1", "PoC", "catalogo + classificazione + lineage su 1 dominio", ACCENT["blue"]),
             ("Wave 2", "MVP", "policy, DQ gate, RAG governato su repurposing", ACCENT["cyan"]),
             ("Wave 3", "Scala", "KG di dominio, audit AI, estensione ai domini", ACCENT["emerald"])]
    for i, (h, tag, b, ac) in enumerate(waves):
        y = 4.65 - i * 1.35
        box(ax, 7.4, y, 5.2, 1.15, accent=ac)
        label(ax, 8.15, y + 0.78, h, size=10, weight="bold")
        label(ax, 8.15, y + 0.34, tag, size=8.5, color=INK_SOFT)
        ax.text(10.6, y + 0.57, b, fontsize=7.8, color=INK_SOFT, ha="center", va="center")
        if i < 2:
            arrow_v(ax, 10.0, y, y - 0.2)

    ax.set_axis_off()
    save(fig, "08_maturity_roadmap.png")


# === Driver ==============================================================


def main():
    fig01_architecture()
    fig02_lineage()
    fig03_kg()
    fig04_rag()
    fig05_lifecycle()
    fig06_domains()
    fig07_lakehouse()
    fig08_maturity()
    print("[OK] 8 figure rigenerate.")


if __name__ == "__main__":
    main()
