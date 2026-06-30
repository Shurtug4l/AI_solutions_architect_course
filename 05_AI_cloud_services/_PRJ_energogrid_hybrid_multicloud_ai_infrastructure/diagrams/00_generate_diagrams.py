"""
Diagram generator for the EnergoGrid multi-cloud AI capstone.

Generates the ten PNG figures referenced by the main DOCX report. Run this
file from inside the diagrams/ directory; each function produces a `NN_*.png`
in the working directory.

Style choices
-------------
Deliberately simple. Each figure follows three rules:
- only straight (horizontal / vertical) arrows; no diagonals, no curves;
- no overlay or background grid;
- one diagram, one message; legends moved out of the plot area.

Palette is kept consistent with the rest of the portfolio (light bg, near-black
ink, soft accent colours) but the visual budget is intentionally narrow.

Figure inventory
----------------
    01  Hybrid multi-cloud architecture                (cap. 6)
    02  Edge-to-cloud data flow                        (cap. 6 / cap. 2)
    03  Criteria x solution-clusters heatmap           (cap. 5)
    04  PaaS / IaaS / OSS decision tree                (cap. 5 / cap. 6)
    05  Hybrid ML lifecycle                            (cap. 6 / cap. 7)
    06  TCO 5-year projection (on-prem vs hybrid)      (cap. 7)
    07  Migration roadmap with three waves             (cap. 9)
    08  Risk heatmap (probability x impact)            (cap. 9)
    09  KPI tree (business -> technical -> operations) (cap. 10)
    10  Multi-cloud governance domain map              (cap. 8)
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch, Rectangle


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
    """Rounded rectangle with optional left accent stripe.

    The accent stripe is a plain rectangle clipped to the rounded card so its
    square corners never poke out past the rounded border (the artefact that
    made every card look imprecise in the first revision)."""
    rect = FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad=0,rounding_size={radius}",
        facecolor=fill, edgecolor=border, linewidth=lw, zorder=zorder,
    )
    ax.add_patch(rect)
    if accent is not None:
        stripe = Rectangle(
            (x, y), accent_w, h,
            facecolor=accent, edgecolor="none", zorder=zorder + 0.1,
        )
        ax.add_patch(stripe)
        stripe.set_clip_path(rect)
    return rect


def label(ax, x, y, text, *, size=10, weight="normal", color=INK,
          ha="center", va="center"):
    ax.text(x, y, text, fontsize=size, fontweight=weight, color=color,
            ha=ha, va=va, zorder=5)


def arrow_h(ax, x0, x1, y, color=INK_SOFT, lw=1.2):
    """Straight horizontal arrow from x0 to x1."""
    ax.annotate(
        "", xy=(x1, y), xytext=(x0, y),
        arrowprops=dict(arrowstyle="-|>", color=color, lw=lw,
                        shrinkA=0, shrinkB=0),
        zorder=4,
    )


def arrow_v(ax, x, y0, y1, color=INK_SOFT, lw=1.2):
    ax.annotate(
        "", xy=(x, y1), xytext=(x, y0),
        arrowprops=dict(arrowstyle="-|>", color=color, lw=lw,
                        shrinkA=0, shrinkB=0),
        zorder=4,
    )


def title_block(ax, x, y, title, subtitle=None):
    ax.text(x, y, title, fontsize=15, fontweight="bold", color=INK,
            ha="left", va="bottom")
    if subtitle:
        ax.text(x, y - 0.25, subtitle, fontsize=9.5, color=INK_MUTED,
                ha="left", va="top")


def save(fig, name):
    fig.savefig(name, dpi=DPI, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)


# === Figure 1 - Hybrid multi-cloud architecture ==========================


def fig1_hybrid_architecture():
    """Four swimlanes top-down: Edge, Private on-prem, Public multi-cloud,
    Consumers. Vertical arrows only between adjacent layers."""
    fig, ax = canvas((13, 8.5))
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 8.5)

    title_block(
        ax, 0.3, 8.2,
        "Architettura ibrida multi-cloud",
        "Quattro layer: Edge - Private on-prem - Public multi-cloud - Consumers",
    )

    layers = [
        # (y, height, name, accent, items)
        (6.4, 1.1, "EDGE", ACCENT["rose"], [
            ("Centrali & impianti", "SCADA - PLC - gateway IoT"),
            ("Parchi rinnovabili",  "inverter - meteo - MQTT"),
            ("Substation & meters", "AMI - PMU - time-series"),
            ("Edge inference",      "K3s - ONNX - low-latency"),
        ]),
        (4.6, 1.1, "PRIVATE", ACCENT["amber"], [
            ("Data hub",        "Kafka - MinIO - TimescaleDB"),
            ("OSS ML platform", "K8s - MLflow - FastAPI"),
            ("Sovereign vault", "secrets - KMS - audit log"),
            ("Identity & SSO",  "AD - Keycloak - MFA"),
        ]),
        (2.8, 1.1, "PUBLIC", ACCENT["blue"], [
            ("AWS landing zone",   "S3 - SageMaker - IoT Core"),
            ("Azure landing zone", "Blob - Azure ML - OpenAI"),
            ("GCP landing zone",   "BigQuery - Vertex AI"),
            ("Control plane",      "Terraform - ArgoCD"),
        ]),
        (1.0, 1.1, "CONSUMERS", ACCENT["emerald"], [
            ("Dispatcher",      "decision support UI"),
            ("Asset management", "manutenzione predittiva"),
            ("Trading & balancing", "API - CRM - ERP"),
            ("Regulator & audit",  "report - evidenze"),
        ]),
    ]

    x_start = 1.4
    x_end = 12.7
    cell_w = (x_end - x_start - 3 * 0.3) / 4
    gap = 0.3

    for (y, h, name, accent, items) in layers:
        # Lane label on the left, vertical
        label(ax, 0.7, y + h / 2, name, size=9, weight="bold",
              color=INK_SOFT)
        for i, (head, body) in enumerate(items):
            x = x_start + i * (cell_w + gap)
            box(ax, x, y, cell_w, h, accent=accent)
            label(ax, x + cell_w / 2, y + h - 0.35, head,
                  size=10.5, weight="bold")
            label(ax, x + cell_w / 2, y + 0.32, body,
                  size=8.8, color=INK_SOFT)

    # Vertical arrows between layers (centered between lanes)
    for y0, y1 in [(6.35, 5.75), (4.55, 3.95), (2.75, 2.15)]:
        for i in range(4):
            x = x_start + i * (cell_w + gap) + cell_w / 2
            arrow_v(ax, x, y0, y1, color=INK_MUTED, lw=1.0)

    label(ax, 6.5, 0.25,
          "Flusso unidirezionale top-down. Cross-cloud assente per design: ogni "
          "use case è assegnato a un solo cloud.",
          size=8.5, color=INK_SOFT)

    ax.set_axis_off()
    save(fig, "01_hybrid_multicloud_architecture.png")


# === Figure 2 - Edge-to-cloud data flow ==================================


def fig2_edge_to_cloud_data_flow():
    """Six sequential stages, straight horizontal arrows, monospace caption
    under each stage. No drift-loop curves, no parallel category lane."""
    fig, ax = canvas((14, 5.2))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 5.2)

    title_block(
        ax, 0.3, 4.9,
        "Flusso dati edge-to-cloud",
        "Dalla telemetria di campo alla decisione operativa",
    )

    stages = [
        ("Sorgenti",        "telemetria, SCADA,\nmeteo, mercato",      ACCENT["rose"]),
        ("Ingestion",       "MQTT, Kafka,\nIoT Hub, Pub/Sub",          ACCENT["amber"]),
        ("Feature pipeline","Spark / Beam,\nfeature store",            ACCENT["violet"]),
        ("Training",        "AutoML, custom,\nGPU spot",               ACCENT["blue"]),
        ("Serving",         "endpoint, edge,\nbatch, streaming",       ACCENT["cyan"]),
        ("Consumers",       "dispatcher, CRM,\naudit, reporting",      ACCENT["emerald"]),
    ]

    w, h = 2.05, 1.7
    y = 1.7
    gap = 0.2
    x_start = 0.3

    for i, (head, body, accent) in enumerate(stages):
        x = x_start + i * (w + gap)
        box(ax, x, y, w, h, accent=accent)
        label(ax, x + w / 2, y + h - 0.35, head, size=10, weight="bold")
        label(ax, x + w / 2, y + 0.55, body, size=9, color=INK_SOFT)
        if i < len(stages) - 1:
            arrow_h(ax, x + w + 0.02, x + w + gap - 0.02, y + h / 2,
                    color=INK_SOFT, lw=1.4)

    # Single caption strip for the drift loop, as text not arrow
    label(ax, 7.0, 0.8,
          "Loop di retraining attivato dal drift monitor (Sezione 7).",
          size=9, color=INK_SOFT)

    ax.set_axis_off()
    save(fig, "02_edge_to_cloud_data_flow.png")


# === Figure 3 - Criteria x solution-clusters heatmap =====================


def fig3_criteria_solutions_heatmap():
    """Qualitative 1-5 grid. Pure table, no decoration."""
    criteria = [
        "Costo (TCO 3-5y)", "Scalabilità & resilienza",
        "Sicurezza & compliance", "Portabilità & lock-in",
        "Lifecycle ML", "Ecosistema & integrazione",
        "Supporto & comunità", "Time-to-market",
    ]
    solutions = ["AWS PaaS", "Azure PaaS", "GCP PaaS", "OSS on-prem", "Hybrid mix"]
    scores = np.array([
        [3, 3, 3, 5, 4],
        [5, 5, 5, 3, 4],
        [4, 5, 4, 4, 5],
        [2, 2, 3, 5, 4],
        [5, 5, 5, 3, 4],
        [5, 5, 4, 3, 5],
        [5, 5, 4, 4, 4],
        [5, 5, 5, 2, 4],
    ])

    score_fill = {
        1: ("#FECDD3", ACCENT["rose"]),
        2: ("#FEF3C7", ACCENT["amber"]),
        3: ("#E2E8F0", INK_SOFT),
        4: ("#DBEAFE", ACCENT["blue"]),
        5: ("#D1FAE5", ACCENT["emerald"]),
    }

    fig, ax = canvas((13, 8.5))
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 8.5)

    title_block(
        ax, 0.3, 8.2,
        "Mappa di valutazione: criteri x cluster di soluzione",
        "Scala qualitativa 1-5 (1 = debole, 5 = best-in-class)",
    )

    n_rows = len(criteria)
    n_cols = len(solutions)
    cell_w, cell_h = 1.5, 0.65
    x_start = 3.5
    y_top = 7.1

    # Column headers
    for j, sol in enumerate(solutions):
        x = x_start + j * cell_w + cell_w / 2
        label(ax, x, y_top + 0.35, sol, size=10, weight="bold")

    # Rows
    for i, crit in enumerate(criteria):
        y = y_top - (i + 1) * cell_h
        label(ax, 3.3, y + cell_h / 2, crit, size=10, ha="right")
        for j in range(n_cols):
            x = x_start + j * cell_w
            fill, txt = score_fill[int(scores[i, j])]
            box(ax, x + 0.05, y + 0.05, cell_w - 0.1, cell_h - 0.1,
                fill=fill, border="none", lw=0)
            label(ax, x + cell_w / 2, y + cell_h / 2, str(scores[i, j]),
                  size=11, weight="bold", color=txt)

    # Legend at bottom
    y_leg = 0.6
    leg_items = [(1, "debole"), (2, "sotto media"), (3, "adeguato"),
                 (4, "forte"), (5, "best-in-class")]
    x = 1.0
    for k, (s, lab) in enumerate(leg_items):
        fill, txt = score_fill[s]
        box(ax, x, y_leg, 0.4, 0.4, fill=fill, border="none", lw=0)
        label(ax, x + 0.5, y_leg + 0.2, f"{s}  {lab}", size=9, ha="left", color=INK_SOFT)
        x += 2.3

    ax.set_axis_off()
    save(fig, "03_criteria_solutions_heatmap.png")


# === Figure 4 - PaaS / IaaS / OSS decision tree ==========================


def fig4_decision_tree():
    """Decision tree top-down with orthogonal connectors only.

    Layout: root (L1) -> two questions (L2) -> three leaves + one question
    at the same row (L3) -> two leaves (L4). All leaves at the deepest row
    they really need.
    """
    fig, ax = canvas((13, 7.5))
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 7.5)

    title_block(
        ax, 0.3, 7.2,
        "Decision tree: scelta del deployment per use case",
        "Quattro domande, cinque esiti possibili",
    )

    def question(x, y, w, h, text):
        box(ax, x, y, w, h, accent=ACCENT["amber"], fill=TINT["amber"])
        label(ax, x + w / 2, y + h / 2, text, size=10, weight="bold")

    def leaf(x, y, w, h, head, sub, accent):
        box(ax, x, y, w, h, accent=accent)
        label(ax, x + w / 2, y + h - 0.3, head, size=10, weight="bold")
        label(ax, x + w / 2, y + 0.3, sub, size=8.6, color=INK_SOFT)

    # === Nodes ============================================================
    # L1: root
    Q1 = (5.0, 6.2, 3.0, 0.8); question(*Q1, "Dato sensibile / sovrano?")
    # L2
    Q2 = (1.5, 4.6, 2.8, 0.8); question(*Q2, "GPU di picco?")
    Q3 = (8.7, 4.6, 2.8, 0.8); question(*Q3, "Lock-in tollerabile?")
    # L3
    L_hybrid = (0.4, 2.8, 2.1, 1.0)
    L_oss    = (2.8, 2.8, 2.1, 1.0)
    L_paas   = (5.6, 2.8, 2.1, 1.0)
    Q4 = (8.7, 2.9, 2.8, 0.8); question(*Q4, "Skill team disponibili?")
    leaf(*L_hybrid, "Hybrid burst", "on-prem + spot cloud", ACCENT["violet"])
    leaf(*L_oss,    "OSS on-prem",  "K8s + MLflow",         ACCENT["rose"])
    leaf(*L_paas,   "PaaS pieno",   "SageMaker / Vertex",   ACCENT["blue"])
    # L4
    L_curato = (7.4, 1.0, 2.1, 1.0)
    L_iaas   = (9.9, 1.0, 2.1, 1.0)
    leaf(*L_curato, "PaaS curato",  "managed services",     ACCENT["cyan"])
    leaf(*L_iaas,   "IaaS + OSS",   "VM cloud + OSS stack", ACCENT["emerald"])

    # === Orthogonal connectors ===========================================
    def cx(node):
        return node[0] + node[2] / 2

    def split(parent, left, right, label_l, label_r, label_r_offset=0.15):
        """Connect a parent node to two children below with an orthogonal
        bus. parent / left / right are (x, y, w, h) tuples."""
        x_p = cx(parent); y_p_bot = parent[1]
        x_l = cx(left); y_l_top = left[1] + left[3]
        x_r = cx(right); y_r_top = right[1] + right[3]
        y_mid = max(y_l_top, y_r_top) + 0.45
        # vertical from parent to bus
        ax.plot([x_p, x_p], [y_p_bot, y_mid], color=INK_MUTED, lw=1.0, zorder=2)
        # horizontal bus
        ax.plot([x_l, x_r], [y_mid, y_mid], color=INK_MUTED, lw=1.0, zorder=2)
        # arrows from bus down to children
        arrow_v(ax, x_l, y_mid, y_l_top, color=INK_MUTED, lw=1.0)
        arrow_v(ax, x_r, y_mid, y_r_top, color=INK_MUTED, lw=1.0)
        # labels
        label(ax, x_l + 0.15, y_mid + 0.18, label_l, size=9, color=INK_SOFT, ha="left")
        label(ax, x_r - label_r_offset, y_mid + 0.18, label_r, size=9, color=INK_SOFT, ha="right")

    # Root -> Q2 / Q3
    split(Q1, Q2, Q3, "sì", "no")
    # Q2 -> Hybrid burst / OSS on-prem
    split(Q2, L_hybrid, L_oss, "sì", "no")
    # Q3 -> PaaS pieno / Q4
    split(Q3, L_paas, Q4, "sì", "no")
    # Q4 -> PaaS curato / IaaS + OSS
    split(Q4, L_curato, L_iaas, "no", "sì")

    ax.set_axis_off()
    save(fig, "04_paas_iaas_oss_decision_tree.png")


# === Figure 5 - Hybrid ML lifecycle ======================================


def fig5_ml_lifecycle_hybrid():
    """Two parallel lanes (private and public) connected by a single registry
    handoff. Each lane is a clean horizontal sequence."""
    fig, ax = canvas((14, 6.5))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 6.5)

    title_block(
        ax, 0.3, 6.2,
        "Lifecycle ML ibrido",
        "Lane private e public si incontrano nel model registry",
    )

    # Private lane (top)
    y_priv = 4.4
    priv = [
        ("Experiment",    "Jupyter - MLflow",      ACCENT["slate"]),
        ("Training",      "GPU pool privato",      ACCENT["rose"]),
        ("Validation",    "test set sensibili",    ACCENT["amber"]),
        ("Edge serving",  "K3s - ONNX",            ACCENT["emerald"]),
    ]
    w_priv = 2.4
    gap = 0.3
    x0 = 1.4
    label(ax, 0.7, y_priv + 0.55, "PRIVATE", size=9, weight="bold",
          color=INK_SOFT)
    for i, (head, body, accent) in enumerate(priv):
        x = x0 + i * (w_priv + gap)
        box(ax, x, y_priv, w_priv, 1.1, accent=accent)
        label(ax, x + w_priv / 2, y_priv + 0.78, head, size=10.5, weight="bold")
        label(ax, x + w_priv / 2, y_priv + 0.3, body, size=8.8, color=INK_SOFT)
        if i < len(priv) - 1:
            arrow_h(ax, x + w_priv + 0.02, x + w_priv + gap - 0.02,
                    y_priv + 0.55, color=INK_SOFT, lw=1.2)

    # Public lane (bottom)
    y_pub = 1.6
    pub = [
        ("Training",       "spot GPU cloud",       ACCENT["blue"]),
        ("HPO & tuning",   "AutoML / managed",     ACCENT["violet"]),
        ("Online endpoint","REST - autoscale",     ACCENT["cyan"]),
        ("Batch & drift",  "BigQuery / S3",        ACCENT["emerald"]),
    ]
    w_pub = 2.4
    label(ax, 0.7, y_pub + 0.55, "PUBLIC", size=9, weight="bold",
          color=INK_SOFT)
    for i, (head, body, accent) in enumerate(pub):
        x = x0 + i * (w_pub + gap)
        box(ax, x, y_pub, w_pub, 1.1, accent=accent)
        label(ax, x + w_pub / 2, y_pub + 0.78, head, size=10.5, weight="bold")
        label(ax, x + w_pub / 2, y_pub + 0.3, body, size=8.8, color=INK_SOFT)
        if i < len(pub) - 1:
            arrow_h(ax, x + w_pub + 0.02, x + w_pub + gap - 0.02,
                    y_pub + 0.55, color=INK_SOFT, lw=1.2)

    # Model registry bridge in the middle
    y_reg = 3.1
    box(ax, 6.0, y_reg, 4.0, 0.7, fill=TINT["amber"], border=ACCENT["amber"], lw=1.3)
    label(ax, 8.0, y_reg + 0.42, "Model registry condiviso",
          size=10.5, weight="bold", color=ACCENT["amber"])
    label(ax, 8.0, y_reg + 0.18, "promote-on-approval - audit log",
          size=8.8, color=INK_SOFT)

    # Two vertical hand-offs, centred on x=8.0 so they line up with the
    # Validation box (top lane) and Online endpoint box (bottom lane) they connect.
    arrow_v(ax, 8.0, y_priv, y_reg + 0.7, color=ACCENT["amber"], lw=1.4)
    arrow_v(ax, 8.0, y_reg, y_pub + 1.1, color=ACCENT["amber"], lw=1.4)

    label(ax, 7.0, 0.4,
          "Un solo registry per entrambe le lane. Drift loop riportato in Sezione 7.",
          size=9, color=INK_SOFT)

    ax.set_axis_off()
    save(fig, "05_ml_lifecycle_hybrid.png")


# === Figure 6 - TCO 5-year projection ====================================


def fig6_tco_5y_projection():
    """Grouped bars + cumulative lines. Annotation as a plain text box,
    no curved arrow."""
    years = ["Anno 1", "Anno 2", "Anno 3", "Anno 4", "Anno 5"]
    on_prem = [2.20, 1.55, 1.60, 1.70, 1.85]
    hybrid  = [1.55, 1.40, 1.35, 1.35, 1.40]
    cum_on  = np.cumsum(on_prem)
    cum_hy  = np.cumsum(hybrid)

    fig, (ax, ax2) = plt.subplots(
        1, 2, figsize=(13, 5.8),
        gridspec_kw=dict(width_ratios=[1.0, 1.0], wspace=0.25),
    )
    fig.patch.set_facecolor(BG)
    for a in (ax, ax2):
        a.set_facecolor(BG)
        for spine in ["top", "right"]:
            a.spines[spine].set_visible(False)
        for spine in ["left", "bottom"]:
            a.spines[spine].set_color(BORDER)
        a.tick_params(colors=INK_SOFT, length=0)

    # Left: grouped bars (annual)
    x = np.arange(len(years))
    width = 0.36
    ax.bar(x - width / 2, on_prem, width, label="On-prem only",
           color=ACCENT["rose"], edgecolor="none")
    ax.bar(x + width / 2, hybrid, width, label="Hybrid multi-cloud",
           color=ACCENT["blue"], edgecolor="none")
    for i in range(len(years)):
        ax.text(i - width / 2, on_prem[i] + 0.05, f"{on_prem[i]:.2f}",
                ha="center", fontsize=8.5, color=INK_SOFT)
        ax.text(i + width / 2, hybrid[i] + 0.05, f"{hybrid[i]:.2f}",
                ha="center", fontsize=8.5, color=INK_SOFT)
    ax.set_xticks(x)
    ax.set_xticklabels(years, fontsize=9.5, color=INK)
    ax.set_ylabel("Spesa annua (proxy normalizzata)", fontsize=9.5, color=INK_SOFT)
    ax.set_title("Spesa annua", fontsize=11, color=INK, loc="left", pad=8)
    ax.set_ylim(0, max(on_prem) * 1.2)
    ax.grid(axis="y", color=BORDER_SOFT, lw=0.7)
    ax.set_axisbelow(True)
    ax.legend(frameon=False, loc="upper right", fontsize=9)

    # Right: cumulative lines
    ax2.plot(years, cum_on, marker="o", color=ACCENT["rose"], lw=2.0,
             label="Cumulato on-prem")
    ax2.plot(years, cum_hy, marker="o", color=ACCENT["blue"], lw=2.0,
             label="Cumulato hybrid")
    ax2.set_ylabel("Cumulato a 5 anni (proxy)", fontsize=9.5, color=INK_SOFT)
    ax2.set_title("Cumulato 5y", fontsize=11, color=INK, loc="left", pad=8)
    ax2.set_ylim(0, max(cum_on) * 1.2)
    ax2.grid(axis="y", color=BORDER_SOFT, lw=0.7)
    ax2.set_axisbelow(True)
    ax2.legend(frameon=False, loc="lower right", fontsize=9)
    # Inline saving annotation as text box, top-left
    ax2.text(
        0.02, 0.95,
        "Risparmio cumulato 5y: ~21%",
        transform=ax2.transAxes, fontsize=10, color=ACCENT["emerald"],
        weight="bold", va="top", ha="left",
        bbox=dict(boxstyle="round,pad=0.4", facecolor=TINT["emerald"],
                  edgecolor=ACCENT["emerald"], linewidth=1.0),
    )

    fig.suptitle("Proiezione TCO a 5 anni (concettuale): on-prem only vs hybrid multi-cloud",
                 fontsize=13, color=INK, weight="bold", x=0.06, ha="left", y=1.02)

    fig.savefig("06_tco_5y_projection.png", dpi=DPI, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close(fig)


# === Figure 7 - Migration roadmap ========================================


def fig7_migration_roadmap():
    """Three horizontal bars on a 36-month timeline + milestone markers
    below."""
    fig, ax = canvas((13, 6.4))
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 6.4)

    title_block(
        ax, 0.3, 6.1,
        "Roadmap di migrazione a tre wave (36 mesi)",
        "Tre workstream, sei milestone, tre gate strategici",
    )

    # Timeline area between x=2.0 and x=12.5
    t0, t1 = 2.0, 12.5
    months_total = 36

    def m_to_x(m):
        return t0 + (m / months_total) * (t1 - t0)

    # Three waves: (title, body wrapped to two lines, start_m, end_m, accent).
    # The body is split so it stays inside the bar width even for the shortest
    # wave; a single line overflowed the bar on the right.
    waves = [
        ("Wave 1 - Foundations",
         "landing zone, governance,\ndata hub, pilot forecasting",
         0, 12, ACCENT["amber"]),
        ("Wave 2 - Hybrid lifecycle",
         "MLflow, feature store,\npredictive maintenance, drift loop",
         9, 24, ACCENT["blue"]),
        ("Wave 3 - Scale & optimisation",
         "dispatch optimisation, edge\ninference, multi-region",
         21, 36, ACCENT["emerald"]),
    ]

    bar_h = 0.9
    y_waves = [4.4, 3.35, 2.3]
    for (head, body, m0, m1, accent), y in zip(waves, y_waves):
        x = m_to_x(m0)
        w = m_to_x(m1) - x
        box(ax, x, y, w, bar_h, fill=TINT["slate"], border="none", lw=0)
        # accent stripe on top of bar
        ax.add_patch(Rectangle((x, y + bar_h - 0.08), w, 0.08,
                               facecolor=accent, edgecolor="none", zorder=3))
        label(ax, x + 0.14, y + bar_h - 0.26, head, size=10, weight="bold",
              ha="left")
        label(ax, x + 0.14, y + 0.30, body, size=8.3, color=INK_SOFT,
              ha="left", va="center")

    # Lane labels on left
    for y, lane in zip(y_waves, ["Infra & governance",
                                  "ML platform & lifecycle",
                                  "Use case delivery"]):
        label(ax, 1.85, y + bar_h / 2, lane, size=9, color=INK_SOFT,
              ha="right")

    # Timeline axis
    y_axis = 1.6
    ax.plot([t0, t1], [y_axis, y_axis], color=BORDER, lw=1.2, zorder=2)
    for m in [0, 6, 12, 18, 24, 30, 36]:
        x = m_to_x(m)
        ax.plot([x, x], [y_axis - 0.07, y_axis + 0.07], color=BORDER, lw=1.0)
        label(ax, x, y_axis - 0.22, f"M{m}", size=8.5, color=INK_MUTED)

    # Milestones on axis
    milestones = [
        (3,  "M1", "landing zone"),
        (8,  "M2", "pilot live"),
        (14, "M3", "feature store"),
        (20, "M4", "pred. maint. prod."),
        (26, "M5", "dispatch opt."),
        (34, "M6", "regime"),
    ]
    for m, code, name in milestones:
        x = m_to_x(m)
        ax.plot(x, y_axis, marker="D", color=ACCENT["rose"], markersize=8,
                zorder=4)
        label(ax, x, y_axis - 0.55, code, size=9, weight="bold")
        label(ax, x, y_axis - 0.78, name, size=8.2, color=INK_SOFT)

    # Strategic gates below
    gates = [(8, "Go / No-Go pilot"), (18, "Approval scaling"), (28, "Vendor review")]
    label(ax, 0.4, 0.4, "GATE STRATEGICI", size=8.5, weight="bold",
          color=INK_SOFT, ha="left")
    for m, name in gates:
        x = m_to_x(m)
        box(ax, x - 0.7, 0.05, 1.4, 0.35, fill=TINT["amber"],
            border=ACCENT["amber"], lw=1.0)
        label(ax, x, 0.22, name, size=8.2, color=ACCENT["amber"], weight="bold")

    ax.set_axis_off()
    save(fig, "07_migration_roadmap_waves.png")


# === Figure 8 - Risk heatmap =============================================


def fig8_risk_heatmap():
    """5x5 heatmap on the left, compact ID legend on the right (3 columns)."""
    fig, ax = canvas((14.5, 7.5))
    ax.set_xlim(0, 14.5)
    ax.set_ylim(0, 7.5)

    title_block(
        ax, 0.3, 7.2,
        "Heatmap rischi: probabilità x impatto",
        "Quindici rischi censiti, scala 1-5; severità = prob x impatto",
    )

    # === Grid =============================================================
    gx0, gy0 = 1.4, 1.2
    gw, gh = 6.4, 5.4
    n = 5
    cw, ch = gw / n, gh / n

    def cell_colour(p, i):
        s = p * i
        if s >= 16: return "#FECDD3"
        if s >= 10: return "#FEF3C7"
        if s >= 5:  return TINT["slate"]
        return "#ECFDF5"

    for i in range(n):
        for p in range(n):
            ax.add_patch(Rectangle(
                (gx0 + p * cw, gy0 + i * ch), cw, ch,
                facecolor=cell_colour(p + 1, i + 1),
                edgecolor=SURFACE, lw=1.5, zorder=1,
            ))

    for k in range(n):
        label(ax, gx0 + (k + 0.5) * cw, gy0 - 0.28, str(k + 1),
              size=10, weight="bold", color=INK_SOFT)
        label(ax, gx0 - 0.28, gy0 + (k + 0.5) * ch, str(k + 1),
              size=10, weight="bold", color=INK_SOFT)
    label(ax, gx0 + gw / 2, gy0 - 0.62, "Probabilità (1-5)",
          size=10, color=INK)
    ax.text(gx0 - 0.85, gy0 + gh / 2, "Impatto (1-5)",
            fontsize=10, color=INK, rotation=90, ha="center", va="center")

    # === Risks ============================================================
    risks = [
        ("R1",  "Cloud lock-in",          3, 4),
        ("R2",  "Data sovereignty",       2, 5),
        ("R3",  "Cost overrun",           4, 3),
        ("R4",  "Skill gap MLOps",        4, 3),
        ("R5",  "Drift modelli",          4, 4),
        ("R6",  "Outage cloud",           2, 4),
        ("R7",  "Supply chain ML",        3, 3),
        ("R8",  "Cyber attack OT",        2, 5),
        ("R9",  "Bias forecasting",       3, 2),
        ("R10", "Latenza dispatch",       2, 3),
        ("R11", "Versioning artefatti",   3, 2),
        ("R12", "Audit findings",         3, 4),
        ("R13", "Vendor SLA",             2, 3),
        ("R14", "Edge OTA failure",       2, 2),
        ("R15", "Concept drift mercato",  3, 3),
    ]

    # Codes are drawn as rounded text chips sized for three characters
    # (R10-R15), so nothing gets clipped. At most two risks share a cell, laid
    # out side by side with a clear gap.
    by_cell = {}
    for code, name, p, i in risks:
        by_cell.setdefault((p, i), []).append(code)

    chip_w, chip_h = 0.52, 0.34
    for (p, i), codes in by_cell.items():
        cxc = gx0 + (p - 1) * cw + cw / 2
        cyc = gy0 + (i - 1) * ch + ch / 2
        offsets = [0.0] if len(codes) == 1 else [-0.31, 0.31]
        for code, off in zip(codes, offsets):
            cxp = cxc + off
            chip = FancyBboxPatch(
                (cxp - chip_w / 2, cyc - chip_h / 2), chip_w, chip_h,
                boxstyle="round,pad=0,rounding_size=0.08",
                facecolor=INK, edgecolor=SURFACE, linewidth=1.2, zorder=4,
            )
            ax.add_patch(chip)
            label(ax, cxp, cyc, code, size=8.5, color=SURFACE, weight="bold")

    # === Legend (3 columns on the right) ==================================
    lx0 = 8.4
    ly0 = 6.4
    line_h = 0.36
    label(ax, lx0, ly0 + 0.22, "LEGENDA", size=10, weight="bold",
          color=INK_SOFT, ha="left")
    col_x = [lx0, lx0 + 2.05, lx0 + 4.1]
    for idx, (code, name, _, _) in enumerate(risks):
        col = idx // 5
        row = idx % 5
        y = ly0 - 0.2 - row * line_h
        x = col_x[col]
        label(ax, x, y, f"{code}", size=8.8, weight="bold",
              color=INK, ha="left")
        label(ax, x + 0.42, y, name, size=8.8, color=INK_SOFT, ha="left")

    # Severity legend on the right, stacked under the ID legend so it no longer
    # collides with the x-axis title at the bottom of the grid.
    items = [
        ("#ECFDF5", "basso (<5)"),
        (TINT["slate"], "medio (5-9)"),
        ("#FEF3C7", "alto (10-15)"),
        ("#FECDD3", "critico (>=16)"),
    ]
    label(ax, lx0, 4.05, "SEVERITÀ", size=10, weight="bold",
          color=INK_SOFT, ha="left")
    y_sev = 3.6
    for fill, txt in items:
        box(ax, lx0, y_sev - 0.18, 0.35, 0.35, fill=fill, border="none", lw=0)
        label(ax, lx0 + 0.5, y_sev, txt, size=9, color=INK_SOFT, ha="left")
        y_sev -= 0.46

    ax.set_axis_off()
    save(fig, "08_risk_heatmap.png")


# === Figure 9 - KPI tree =================================================


def fig9_kpi_tree():
    """Three-level tree, orthogonal connectors only."""
    fig, ax = canvas((13, 7.5))
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 7.5)

    title_block(
        ax, 0.3, 7.2,
        "Albero dei KPI di progetto",
        "Valore di business -> macro KPI -> metriche operative",
    )

    # Level 1
    box(ax, 5.0, 5.6, 3.0, 0.9, accent=ACCENT["amber"], fill=TINT["amber"])
    label(ax, 6.5, 6.2, "Valore di business", size=11, weight="bold")
    label(ax, 6.5, 5.85, "affidabilità rete - costo - rinnovabili",
          size=8.8, color=INK_SOFT)

    # Level 2 (three branches)
    macros = [
        (1.5, "Riduzione costi",       "OpEx dispatch - MTBF assets",  ACCENT["blue"]),
        (5.0, "Qualità del modello",   "MAPE forecast - precision PM", ACCENT["emerald"]),
        (8.5, "Compliance & sicurezza","gap NIS2 - audit findings",    ACCENT["rose"]),
    ]
    for x, head, sub, accent in macros:
        box(ax, x, 3.7, 3.0, 0.9, accent=accent)
        label(ax, x + 1.5, 4.3, head, size=10.5, weight="bold")
        label(ax, x + 1.5, 3.95, sub, size=8.6, color=INK_SOFT)

    # Connectors L1 -> L2 (orthogonal)
    for x in [3.0, 6.5, 10.0]:
        ax.plot([6.5, 6.5], [5.6, 5.3], color=INK_MUTED, lw=1.0, zorder=2)
        ax.plot([3.0, 10.0], [5.3, 5.3], color=INK_MUTED, lw=1.0, zorder=2)
        arrow_v(ax, x, 5.3, 4.6, color=INK_MUTED, lw=1.0)

    # Level 3: two operative metrics per macro
    leaves = [
        (1.5, ["MTBF\n+15% in 24m", "Cost / MWh\n-8% baseline"], ACCENT["blue"]),
        (5.0, ["MAPE forecast\n<=4% T+24h", "Recall PM\n>=0.85"], ACCENT["emerald"]),
        (8.5, ["Gap NIS2\n0 critici", "Audit log\n100% coverage"], ACCENT["rose"]),
    ]
    leaf_w = 1.42
    for x, items, accent in leaves:
        # Two leaves per macro, widened so headers like "MAPE forecast" keep
        # clear of the box border.
        positions = [(x + 0.04, 1.6), (x + 1.54, 1.6)]
        for (lx, ly), txt in zip(positions, items):
            box(ax, lx, ly, leaf_w, 1.0, accent=accent)
            head, val = txt.split("\n")
            label(ax, lx + leaf_w / 2, ly + 0.7, head, size=8.8, weight="bold")
            label(ax, lx + leaf_w / 2, ly + 0.3, val, size=8.3, color=INK_SOFT)

    # Connectors L2 -> L3 (orthogonal), aligned to the new leaf centres
    for x in [1.5, 5.0, 8.5]:
        xl, xr = x + 0.04 + leaf_w / 2, x + 1.54 + leaf_w / 2
        ax.plot([x + 1.5, x + 1.5], [3.7, 3.1], color=INK_MUTED, lw=1.0, zorder=2)
        ax.plot([xl, xr], [3.1, 3.1], color=INK_MUTED, lw=1.0, zorder=2)
        arrow_v(ax, xl, 3.1, 2.6, color=INK_MUTED, lw=1.0)
        arrow_v(ax, xr, 3.1, 2.6, color=INK_MUTED, lw=1.0)

    label(ax, 6.5, 0.55,
          "Le metriche operative sono misurabili settimanalmente. Il valore di "
          "business si rivede in steering trimestrale.",
          size=8.8, color=INK_SOFT)

    ax.set_axis_off()
    save(fig, "09_kpi_tree.png")


# === Figure 10 - Governance domain map ===================================


def fig10_governance_map():
    """Grid 2x3 of governance domains, with principles band on top and
    regulations band at the bottom. No circles, no diagonal arrows."""
    fig, ax = canvas((13, 7.5))
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 7.5)

    title_block(
        ax, 0.3, 7.2,
        "Mappa dei domini di governance multi-cloud",
        "Principi (header) -> domini (corpo) -> norme applicabili (footer)",
    )

    # Principles band (top)
    box(ax, 0.5, 6.0, 12.0, 0.7, fill=TINT["blue"], border=ACCENT["blue"], lw=1.2)
    label(ax, 0.85, 6.35, "PRINCIPI", size=9.5, weight="bold",
          color=ACCENT["blue"], ha="left")
    label(ax, 7.0, 6.35, "least privilege   -   zero trust   -   data sovereignty",
          size=11, weight="bold", ha="center")

    # Domains grid 2 rows x 3 cols
    domains = [
        ("Identità & accessi", "IAM unificato, MFA, SSO federato",    ACCENT["blue"]),
        ("Dato",               "classificazione, lineage, retention", ACCENT["emerald"]),
        ("Modello",            "registry, approval, model card",      ACCENT["amber"]),
        ("Rete",               "VPC, segmentazione, peering privato", ACCENT["violet"]),
        ("Edge",               "device identity, OTA firmate",        ACCENT["rose"]),
        ("Audit",              "log centralizzato, evidence trail",   ACCENT["cyan"]),
    ]
    w, h = 3.8, 1.55
    x_start = 0.6
    y_top = 4.20   # top row starts here; spans [4.20, 5.75]
    gap_x = 0.25
    gap_y = 0.30
    for i, (head, body, accent) in enumerate(domains):
        col = i % 3
        row = i // 3
        x = x_start + col * (w + gap_x)
        y = y_top - row * (h + gap_y)
        box(ax, x, y, w, h, accent=accent)
        label(ax, x + w / 2, y + h - 0.42, head, size=11, weight="bold")
        label(ax, x + w / 2, y + 0.52, body, size=9, color=INK_SOFT)

    # Regulations band (bottom)
    box(ax, 0.5, 0.5, 12.0, 0.7, fill=TINT["slate"], border=BORDER, lw=1.0)
    label(ax, 0.85, 0.85, "NORME", size=9.5, weight="bold",
          color=INK_SOFT, ha="left")
    label(ax, 7.0, 0.85, "GDPR  -  NIS2  -  EU AI Act  -  ISO 27001 / 27019  -  IEC 62443 (OT)",
          size=10.5, weight="bold", ha="center")

    ax.set_axis_off()
    save(fig, "10_governance_domain_map.png")


# === Driver ==============================================================


def main():
    fig1_hybrid_architecture()
    fig2_edge_to_cloud_data_flow()
    fig3_criteria_solutions_heatmap()
    fig4_decision_tree()
    fig5_ml_lifecycle_hybrid()
    fig6_tco_5y_projection()
    fig7_migration_roadmap()
    fig8_risk_heatmap()
    fig9_kpi_tree()
    fig10_governance_map()
    print("[OK] 10 figure rigenerate.")


if __name__ == "__main__":
    main()
