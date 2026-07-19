"""
Diagram generator for the RetailSight video analytics capstone (module 08).

Generates the seven PNG figures referenced by the main DOCX report. Run this
file from inside the diagrams/ directory; each function produces a `NN_*.png`
in the working directory.

Style choices
-------------
Consistent with the module 04/05/07 capstones (portfolio continuity):
- straight (horizontal / vertical) arrows in flow figures;
- no background grid, light background, near-black ink, soft accent colours;
- one figure, one message; legends and labels kept out of the way.

Figure inventory
----------------
    01  High-level logical architecture (layers + cross-cutting)   (cap. 6)
    02  Edge-cloud deployment topology                             (cap. 6)
    03  Data lifecycle with retention windows                      (cap. 8)
    04  Real-time alerting path with latency budget                (cap. 8)
    05  Model lifecycle with governance gates                      (cap. 9)
    06  Risk matrix, pre and post mitigation                       (cap. 13)
    07  Adoption roadmap, three waves over twelve months           (cap. 15)
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


def title_block(ax, x, y, title, subtitle=None):
    ax.text(x, y, title, fontsize=15, fontweight="bold", color=INK,
            ha="left", va="bottom")
    if subtitle:
        ax.text(x, y - 0.25, subtitle, fontsize=9.5, color=INK_MUTED,
                ha="left", va="top")


def chip(ax, x, y, text, *, color, size=7.8):
    """Small tinted pill used for retention / access-class annotations."""
    ax.text(x, y, text, fontsize=size, color=color, ha="center", va="center",
            zorder=6, fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.28", fc=BG, ec=color, lw=0.9))


def save(fig, name):
    fig.savefig(name, dpi=DPI, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)


# === Figure 01 - High-level logical architecture =========================


def fig01_architecture():
    fig, ax = canvas((11.6, 8.2))
    ax.set_xlim(0, 11.6)
    ax.set_ylim(0, 8.2)

    title_block(ax, 0.25, 7.75, "Architettura logica RetailSight",
                "Livelli funzionali e responsabilità trasversali; la topologia di deployment è nella figura successiva")

    LX, LW = 0.25, 8.6          # layer band geometry
    CW = (LW - 0.7) / 3         # width of a 3-column component box

    def layer(y, h, name):
        box(ax, LX, y, LW, h, fill=SURFACE_SOFT, border=BORDER, lw=1.0)
        label(ax, LX + 0.18, y + h - 0.24, name, size=9, weight="bold",
              color=INK_SOFT, ha="left")
        return y

    def comp(cx, cy, w, h, name, sub, accent):
        box(ax, cx, cy, w, h, fill=SURFACE, border=BORDER, accent=ACCENT[accent])
        label(ax, cx + w / 2 + 0.04, cy + h * 0.62, name, size=8.8, weight="bold")
        label(ax, cx + w / 2 + 0.04, cy + h * 0.28, sub, size=7.6, color=INK_SOFT)

    # Layer 5 (top): presentation and integration
    y5 = layer(6.15, 1.15, "PRESENTAZIONE E INTEGRAZIONE")
    comp(LX + 0.18, y5 + 0.12, CW, 0.72, "Dashboard BI",
         "traffico, code, shrinkage", "violet")
    comp(LX + 0.36 + CW, y5 + 0.12, CW, 0.72, "Console operativa",
         "alert, revisione umana", "violet")
    comp(LX + 0.54 + 2 * CW, y5 + 0.12, CW, 0.72, "API di integrazione",
         "POS, CRM, incident mgmt", "violet")

    # Layer 4: application services
    y4 = layer(4.75, 1.15, "SERVIZI APPLICATIVI")
    comp(LX + 0.18, y4 + 0.12, CW, 0.72, "Motore regole",
         "soglie, zone di interesse", "blue")
    comp(LX + 0.36 + CW, y4 + 0.12, CW, 0.72, "Servizio alerting",
         "notifiche, escalation", "blue")
    comp(LX + 0.54 + 2 * CW, y4 + 0.12, CW, 0.72, "Reportistica",
         "aggregati, trend, export", "blue")

    # Layer 3: AI services
    y3 = layer(3.35, 1.15, "SERVIZI AI")
    comp(LX + 0.18, y3 + 0.12, CW, 0.72, "Inferenza online",
         "detection, tracking, eventi", "emerald")
    comp(LX + 0.36 + CW, y3 + 0.12, CW, 0.72, "Inferenza batch",
         "heatmap, planogram, trend", "emerald")
    comp(LX + 0.54 + 2 * CW, y3 + 0.12, CW, 0.72, "Training e registry",
         "versioning, canary, rollback", "emerald")

    # Layer 2: data platform
    y2 = layer(1.95, 1.15, "PIATTAFORMA DATI")
    comp(LX + 0.18, y2 + 0.12, CW, 0.72, "Bus eventi",
         "hot path, pub/sub", "cyan")
    comp(LX + 0.36 + CW, y2 + 0.12, CW, 0.72, "Lakehouse",
         "eventi, feature, dataset", "cyan")
    comp(LX + 0.54 + 2 * CW, y2 + 0.12, CW, 0.72, "Object storage",
         "clip selezionate, cifrate", "cyan")

    # Layer 1 (bottom): acquisition
    y1 = layer(0.55, 1.15, "ACQUISIZIONE")
    comp(LX + 0.18, y1 + 0.12, CW, 0.72, "Telecamere IP",
         "RTSP, on-premises", "amber")
    comp(LX + 0.36 + CW, y1 + 0.12, CW, 0.72, "Preproc. e anonimiz.",
         "decode, blur volti, ROI", "amber")
    comp(LX + 0.54 + 2 * CW, y1 + 0.12, CW, 0.72, "POS e sensori",
         "scontrini, conteggio ingressi", "amber")

    # Upward flow arrows between layers
    ax_x = LX + LW / 2
    for ya, yb in [(1.70, 1.95), (3.10, 3.35), (4.50, 4.75), (5.90, 6.15)]:
        arrow_v(ax, ax_x, ya, yb)

    # Cross-cutting vertical bands on the right
    CCX, CCW = 9.15, 2.2
    cc = [("Sicurezza e IAM", "cifratura, RBAC,\nsegmentazione rete", "rose"),
          ("Osservabilità", "telemetria op. e ML,\naudit log", "slate"),
          ("Governance", "lineage, policy,\ngate dei modelli", "amber")]
    for i, (name, sub, acc) in enumerate(cc):
        yy = 0.55 + i * 2.35
        box(ax, CCX, yy, CCW, 2.05, fill=TINT[acc], border=BORDER, lw=1.0)
        label(ax, CCX + CCW / 2, yy + 1.55, name, size=9.2, weight="bold")
        label(ax, CCX + CCW / 2, yy + 0.85, sub, size=7.8, color=INK_SOFT)

    label(ax, CCX + CCW / 2, 7.35, "RESPONSABILITÀ TRASVERSALI",
          size=8.2, weight="bold", color=INK_MUTED)

    save(fig, "01_highlevel_architecture.png")


# === Figure 02 - Edge-cloud deployment topology ==========================


def fig02_edge_cloud():
    fig, ax = canvas((12.2, 7.4))
    ax.set_xlim(0, 12.2)
    ax.set_ylim(0, 7.4)

    title_block(ax, 0.25, 6.95, "Topologia di deployment edge-cloud",
                "Il video resta nello store; verso il cloud viaggiano eventi e clip selezionate")

    # --- Store frame (left) ---
    box(ax, 0.25, 0.6, 5.1, 5.7, fill=TINT["amber"], border=ACCENT["amber"], lw=1.3)
    label(ax, 0.55, 6.0, "PUNTO VENDITA  (x180)", size=9.5, weight="bold",
          color=ACCENT["amber"], ha="left")

    box(ax, 0.55, 4.6, 2.1, 1.0, fill=SURFACE, border=BORDER, accent=ACCENT["amber"])
    label(ax, 1.64, 5.32, "Telecamere IP", size=8.8, weight="bold")
    label(ax, 1.64, 5.02, "30-60 per store", size=7.6, color=INK_SOFT)
    label(ax, 1.64, 4.78, "VLAN dedicata", size=7.6, color=INK_SOFT)

    box(ax, 3.05, 4.6, 2.1, 1.0, fill=SURFACE, border=BORDER, accent=ACCENT["amber"])
    label(ax, 4.14, 5.32, "POS e sensori", size=8.8, weight="bold")
    label(ax, 4.14, 5.02, "scontrini, varchi", size=7.6, color=INK_SOFT)
    label(ax, 4.14, 4.78, "conteggio ingressi", size=7.6, color=INK_SOFT)

    # Edge node
    box(ax, 0.55, 1.9, 4.6, 2.25, fill=SURFACE, border=BORDER, lw=1.1,
        accent=ACCENT["emerald"])
    label(ax, 2.9, 3.85, "Nodo edge di store (GPU)", size=9.2, weight="bold")
    inner = [("Decode e ROI", 0.75), ("Blur volti", 1.85), ("Detection\ne tracking", 2.95),
             ("Eventi e\nclip buffer", 4.05)]
    for name, cx in inner:
        box(ax, cx, 2.15, 1.0, 1.15, fill=SURFACE_SOFT, border=BORDER_SOFT)
        label(ax, cx + 0.5, 2.72, name, size=7.4, color=INK_SOFT)
    label(ax, 2.45, 1.62, "ritenzione clip locale: 72 h, cifrata", size=7.6,
          color=INK_MUTED)

    box(ax, 0.55, 0.75, 4.6, 0.62, fill=SURFACE, border=BORDER, accent=ACCENT["violet"])
    label(ax, 2.9, 1.06, "App staff di store: alert, presa in carico, esito",
          size=8.2)

    arrow_v(ax, 1.64, 4.6, 4.35, color=INK_SOFT)
    arrow_v(ax, 4.14, 4.6, 4.35, color=INK_SOFT)
    arrow_v(ax, 4.55, 1.9, 1.48, color=INK_SOFT)

    # --- Uplink ---
    arrow_h(ax, 5.35, 6.75, 3.6, color=ACCENT["blue"], lw=2.0)
    label(ax, 6.05, 4.12, "eventi + clip\nselezionate", size=7.6,
          color=ACCENT["blue"], weight="bold")
    label(ax, 6.05, 3.22, "~1-3% del girato\nTLS, mutual auth", size=7.4,
          color=INK_SOFT)
    arrow_h(ax, 6.75, 5.35, 1.35, color=ACCENT["emerald"], lw=1.6)
    label(ax, 6.05, 1.72, "rollout modelli\n(canary per coorte)", size=7.4,
          color=ACCENT["emerald"], weight="bold")

    # --- Cloud frame (right) ---
    box(ax, 6.75, 0.6, 5.2, 5.7, fill=TINT["blue"], border=ACCENT["blue"], lw=1.3)
    label(ax, 7.05, 6.0, "CLOUD  (regione UE)", size=9.5, weight="bold",
          color=ACCENT["blue"], ha="left")

    box(ax, 7.05, 4.75, 2.2, 0.95, fill=SURFACE, border=BORDER, accent=ACCENT["cyan"])
    label(ax, 8.15, 5.42, "Bus eventi", size=8.8, weight="bold")
    label(ax, 8.15, 5.08, "ingestione hot path", size=7.6, color=INK_SOFT)

    box(ax, 9.55, 4.75, 2.2, 0.95, fill=SURFACE, border=BORDER, accent=ACCENT["blue"])
    label(ax, 10.65, 5.42, "Regole e alerting", size=8.8, weight="bold")
    label(ax, 10.65, 5.08, "soglie, escalation", size=7.6, color=INK_SOFT)

    box(ax, 7.05, 3.45, 2.2, 0.95, fill=SURFACE, border=BORDER, accent=ACCENT["cyan"])
    label(ax, 8.15, 4.12, "Lakehouse", size=8.8, weight="bold")
    label(ax, 8.15, 3.78, "eventi, feature, dataset", size=7.6, color=INK_SOFT)

    box(ax, 9.55, 3.45, 2.2, 0.95, fill=SURFACE, border=BORDER, accent=ACCENT["cyan"])
    label(ax, 10.65, 4.12, "Object storage", size=8.8, weight="bold")
    label(ax, 10.65, 3.78, "clip cifrate, 30 gg", size=7.6, color=INK_SOFT)

    box(ax, 7.05, 2.15, 2.2, 0.95, fill=SURFACE, border=BORDER, accent=ACCENT["emerald"])
    label(ax, 8.15, 2.82, "Batch analytics", size=8.8, weight="bold")
    label(ax, 8.15, 2.48, "heatmap, planogram", size=7.6, color=INK_SOFT)

    box(ax, 9.55, 2.15, 2.2, 0.95, fill=SURFACE, border=BORDER, accent=ACCENT["emerald"])
    label(ax, 10.65, 2.82, "Training e registry", size=8.8, weight="bold")
    label(ax, 10.65, 2.48, "MLOps, versioning", size=7.6, color=INK_SOFT)

    box(ax, 7.05, 0.85, 4.7, 0.95, fill=SURFACE, border=BORDER, accent=ACCENT["violet"])
    label(ax, 9.4, 1.52, "Dashboard BI e API di integrazione", size=8.8, weight="bold")
    label(ax, 9.4, 1.18, "sede centrale: loss prevention, operations, merchandising",
          size=7.6, color=INK_SOFT)

    arrow_h(ax, 9.25, 9.55, 5.22)
    arrow_v(ax, 8.15, 4.75, 4.4)
    arrow_v(ax, 10.65, 4.75, 4.4)
    arrow_v(ax, 8.15, 3.45, 3.1)
    arrow_v(ax, 10.65, 3.45, 3.1)
    arrow_v(ax, 9.4, 2.15, 1.8)

    save(fig, "02_edge_cloud_topology.png")


# === Figure 03 - Data lifecycle with retention windows ===================


def fig03_data_lifecycle():
    fig, ax = canvas((12.4, 5.6))
    ax.set_xlim(0, 12.4)
    ax.set_ylim(0, 5.6)

    title_block(ax, 0.25, 5.15, "Ciclo di vita del dato",
                "Dalla ripresa alla cancellazione: a ogni passaggio il dato diventa meno identificante")

    stages = [
        ("Ripresa", "stream live,\nsolo in memoria\nsul nodo edge", "minuti", "rose",
         "dato personale"),
        ("Selezione e\nanonimizzazione", "solo segmenti con\neventi; blur volti\nprima di uscire", "on the fly", "amber",
         "dato personale"),
        ("Clip evento", "clip cifrate:\nedge 72 h,\ncloud 30 gg", "72 h / 30 gg", "blue",
         "pseudonimo"),
        ("Feature e\nderivati", "traiettorie, conteggi,\nheatmap; nessun\nframe originale", "12 mesi", "cyan",
         "non identificante"),
        ("Aggregati BI", "KPI per store,\nfascia oraria,\nreparto", "24 mesi", "emerald",
         "anonimo"),
        ("Fine vita", "cancellazione\nautomatica a fine\nritenzione + audit", "-", "slate",
         "-"),
    ]

    SW, GAP, Y, H = 1.82, 0.22, 1.55, 2.3
    x = 0.25
    for i, (name, sub, ret, acc, cls) in enumerate(stages):
        box(ax, x, Y, SW, H, fill=SURFACE, border=BORDER, accent=ACCENT[acc])
        label(ax, x + SW / 2 + 0.03, Y + H - 0.42, name, size=8.6, weight="bold")
        label(ax, x + SW / 2 + 0.03, Y + H / 2 - 0.28, sub, size=7.2, color=INK_SOFT)
        if ret != "-":
            chip(ax, x + SW / 2, Y - 0.42, ret, color=ACCENT[acc])
        if cls != "-":
            label(ax, x + SW / 2, Y + H + 0.35, cls, size=7.4, color=INK_MUTED)
        if i < len(stages) - 1:
            arrow_h(ax, x + SW, x + SW + GAP, Y + H / 2)
        x += SW + GAP

    label(ax, 0.25, 4.35, "classificazione:", size=7.4, color=INK_MUTED, ha="left")
    label(ax, 6.3, 0.52,
          "Diritti degli interessati (accesso, cancellazione) esercitabili finché il dato è riferibile a una persona: prime tre fasi.\n"
          "Eventi strutturati: 12 mesi nel lakehouse (Tabella 8.1). Ritenzione clip oltre i 30 giorni cloud solo su evento aperto (legal hold).",
          size=7.8, color=INK_SOFT)

    save(fig, "03_data_lifecycle.png")


# === Figure 04 - Real-time alerting path =================================


def fig04_realtime_path():
    fig, ax = canvas((12.4, 5.2))
    ax.set_xlim(0, 12.4)
    ax.set_ylim(0, 5.2)

    title_block(ax, 0.25, 4.75, "Percorso real-time di alerting",
                "Budget di latenza per tratta; obiettivo end-to-end sotto i 2 secondi")

    steps = [
        ("Frame", "telecamera\n10-15 fps", "amber", None),
        ("Inferenza edge", "detection, tracking,\nclassificazione evento", "emerald", "< 150 ms"),
        ("Evento sul bus", "publish + trasporto\nverso il cloud", "cyan", "< 100 ms"),
        ("Motore regole", "soglie, zona,\nde-duplica", "blue", "< 200 ms"),
        ("Notifica staff", "app di store,\nconsole centrale", "violet", "< 1 s"),
        ("Presa in carico", "revisione umana,\nesito registrato", "slate", "umano"),
    ]

    SW, GAP, Y, H = 1.78, 0.28, 2.1, 1.7
    x = 0.25
    for i, (name, sub, acc, lat) in enumerate(steps):
        box(ax, x, Y, SW, H, fill=SURFACE, border=BORDER, accent=ACCENT[acc])
        label(ax, x + SW / 2 + 0.03, Y + H - 0.38, name, size=8.7, weight="bold")
        label(ax, x + SW / 2 + 0.03, Y + H / 2 - 0.22, sub, size=7.3, color=INK_SOFT)
        if lat:
            chip(ax, x + SW / 2, Y - 0.42, lat, color=ACCENT[acc])
        if i < len(steps) - 1:
            arrow_h(ax, x + SW, x + SW + GAP, Y + H / 2)
        x += SW + GAP

    # End-to-end badge
    chip(ax, 11.15, 4.55, "end-to-end < 2 s", color=ACCENT["rose"], size=8.6)

    # Feedback loop to retraining dataset
    fb_y = 1.05
    ax.annotate("", xy=(2.55, Y - 0.72), xytext=(11.0, fb_y),
                arrowprops=dict(arrowstyle="-|>", color=ACCENT["emerald"], lw=1.4,
                                connectionstyle="arc3,rad=0.0",
                                shrinkA=0, shrinkB=0), zorder=4)
    label(ax, 6.8, fb_y - 0.28,
          "esiti verificati (vero/falso allarme)  ->  dataset di retraining e metriche di precisione sul campo",
          size=7.8, color=ACCENT["emerald"], weight="bold")

    save(fig, "04_realtime_alerting.png")


# === Figure 05 - Model lifecycle with governance gates ===================


def fig05_model_lifecycle():
    fig, ax = canvas((12.0, 7.0))
    ax.set_xlim(0, 12.0)
    ax.set_ylim(0, 7.0)

    title_block(ax, 0.25, 6.55, "Ciclo di vita dei modelli",
                "Otto fasi, quattro gate di governance; nessun avanzamento senza evidenze")

    def stage(x, y, name, sub, acc, fill=SURFACE):
        box(ax, x, y, 2.35, 1.05, fill=fill, border=BORDER, accent=ACCENT[acc])
        label(ax, x + 1.21, y + 0.72, name, size=8.8, weight="bold")
        label(ax, x + 1.21, y + 0.33, sub, size=7.3, color=INK_SOFT)

    def gate(x, y, name):
        ax.add_patch(FancyBboxPatch((x - 0.26, y - 0.26), 0.52, 0.52,
                                    boxstyle="round,pad=0,rounding_size=0.06",
                                    facecolor=TINT["amber"], edgecolor=ACCENT["amber"],
                                    linewidth=1.2, zorder=4.6,
                                    transform=ax.transData))
        label(ax, x, y, name, size=7.4, weight="bold", color=ACCENT["amber"])

    # Top row, left to right; gates sit on the connecting arrows
    TY = 4.6
    stage(0.4, TY, "1. Raccolta dati", "campionamento per\nstore e condizioni", "cyan")
    stage(3.55, TY, "2. Annotazione", "standard, doppia\netichetta, QA", "cyan")
    stage(6.7, TY, "3. Sviluppo e\nvalidazione", "metriche, bias,\nedge case", "emerald")
    stage(9.55, TY, "4. Certificazione", "review performance,\nprivacy, etica", "amber")

    arrow_h(ax, 2.75, 3.55, TY + 0.52)
    arrow_h(ax, 5.9, 6.7, TY + 0.52)
    arrow_h(ax, 9.05, 9.55, TY + 0.52)
    gate(3.15, TY + 0.52, "G1")
    gate(6.3, TY + 0.52, "G2")
    gate(9.3, TY + 0.52, "G3")

    # Down connector with G4 between certification and deployment
    BY = 1.5
    arrow_v(ax, 10.72, TY, BY + 1.05)
    gate(10.72, (TY + BY + 1.05) / 2, "G4")

    # Bottom row, right to left
    stage(9.55, BY, "5. Deployment", "canary su coorte\ndi store, rollback", "blue")
    stage(6.1, BY, "6. Monitoraggio", "drift, precisione\nsul campo, allarmi", "blue")
    stage(2.95, BY, "7. Retraining", "trigger da drift\no calo precision", "violet")
    stage(0.25, BY, "8. Ritiro", "decommissioning,\narchivio per audit", "slate",
          fill=SURFACE_SOFT)

    arrow_h(ax, 9.55, 8.45, BY + 0.52)
    arrow_h(ax, 6.1, 5.3, BY + 0.52)
    arrow_h(ax, 2.95, 2.6, BY + 0.52)

    # Retraining loop back to development
    ax.annotate("", xy=(7.4, TY - 0.02), xytext=(4.6, BY + 1.07),
                arrowprops=dict(arrowstyle="-|>", color=ACCENT["violet"], lw=1.4,
                                connectionstyle="arc3,rad=-0.22",
                                shrinkA=2, shrinkB=2), zorder=3)
    ax.text(4.55, 3.35, "nuova versione:\nrientra da G2 o G3", fontsize=7.4,
            color=ACCENT["violet"], ha="center", va="center", zorder=6,
            fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.25", fc=BG, ec="none"))

    # Gate legend at the bottom
    label(ax, 0.25, 0.62, "G1 liceità e privacy del dataset   -   "
          "G2 qualità etichette (accordo tra annotatori >= 95%)   -   "
          "G3 soglie di metriche e fairness superate   -   "
          "G4 approvazione del comitato di governance",
          size=7.8, color=INK_SOFT, ha="left")

    save(fig, "05_model_lifecycle.png")


# === Figure 06 - Risk matrix =============================================


def fig06_risk_matrix():
    fig, ax = canvas((11.6, 6.4))
    ax.set_xlim(0, 11.6)
    ax.set_ylim(0, 6.4)

    title_block(ax, 0.25, 5.95, "Matrice dei rischi",
                "Posizione inerente (pieno) e residua dopo mitigazione (vuoto)")

    # 5x5 grid
    GX, GY, CS = 0.9, 0.75, 0.88
    cell_color = {}
    shades = {1: "#ECFDF5", 2: "#FEF9C3", 3: "#FFEDD5", 4: "#FEE2E2"}
    for i in range(5):
        for j in range(5):
            score = (i + 1) * (j + 1)
            band_v = 1 if score <= 4 else 2 if score <= 9 else 3 if score <= 15 else 4
            ax.add_patch(Rectangle((GX + i * CS, GY + j * CS), CS, CS,
                                   facecolor=shades[band_v], edgecolor="#FFFFFF",
                                   linewidth=1.4, zorder=1))
    for i in range(5):
        label(ax, GX + i * CS + CS / 2, GY - 0.28, str(i + 1), size=8, color=INK_SOFT)
        label(ax, GX - 0.28, GY + i * CS + CS / 2, str(i + 1), size=8, color=INK_SOFT)
    label(ax, GX + 2.5 * CS, GY - 0.62, "Probabilità", size=9, weight="bold",
          color=INK_SOFT)
    ax.text(GX - 0.62, GY + 2.5 * CS, "Impatto", fontsize=9, fontweight="bold",
            color=INK_SOFT, ha="center", va="center", rotation=90)

    def risk(rid, p_in, i_in, p_res, i_res, col, d_in=(0, 0), d_res=(0, 0)):
        x0 = GX + (p_in - 0.5) * CS + d_in[0]
        y0 = GY + (i_in - 0.5) * CS + d_in[1]
        x1 = GX + (p_res - 0.5) * CS + d_res[0]
        y1 = GY + (i_res - 0.5) * CS + d_res[1]
        ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>",
                                     mutation_scale=10, color=col, lw=1.2,
                                     zorder=4, shrinkA=9, shrinkB=9))
        ax.scatter([x0], [y0], s=230, c=col, zorder=5)
        ax.text(x0, y0, rid, fontsize=7.2, color="#FFFFFF", ha="center",
                va="center", zorder=6, fontweight="bold")
        ax.scatter([x1], [y1], s=230, facecolors=BG, edgecolors=col,
                   linewidths=1.6, zorder=5)
        ax.text(x1, y1, rid, fontsize=7.2, color=col, ha="center", va="center",
                zorder=6, fontweight="bold")

    # rid, prob inherent, impact inherent, prob residual, impact residual.
    # R1 residual and R6 inherent share cell (2,4): honest tie, offset inside
    # the cell so both markers stay readable.
    risk("R1", 4, 5, 2, 4, ACCENT["rose"], d_res=(0.2, 0.2))
    risk("R2", 3, 4, 1, 4, ACCENT["violet"])
    risk("R3", 4, 3, 3, 2, ACCENT["blue"])
    risk("R4", 3, 5, 2, 3, ACCENT["amber"])
    risk("R5", 3, 3, 2, 2, ACCENT["emerald"])
    risk("R6", 2, 4, 1, 3, ACCENT["cyan"], d_in=(-0.2, -0.2))

    # Legend
    LX = 6.2
    entries = [
        ("R1", "Violazione privacy / non conformità GDPR e AI Act", ACCENT["rose"]),
        ("R2", "Bias e discriminazione negli alert", ACCENT["violet"]),
        ("R3", "Falsi positivi con impatto operativo", ACCENT["blue"]),
        ("R4", "Costi di scala fuori controllo", ACCENT["amber"]),
        ("R5", "Dataset non rappresentativi (drift strutturale)", ACCENT["emerald"]),
        ("R6", "Indisponibilità di componenti critici", ACCENT["cyan"]),
    ]
    for k, (rid, txt, col) in enumerate(entries):
        yy = 4.9 - k * 0.62
        ax.scatter([LX], [yy], s=190, c=col, zorder=5)
        ax.text(LX, yy, rid, fontsize=6.8, color="#FFFFFF", ha="center",
                va="center", zorder=6, fontweight="bold")
        label(ax, LX + 0.35, yy, txt, size=8.4, ha="left", color=INK_SOFT)

    label(ax, LX + 0.35, 4.9 - 6 * 0.62,
          "dettaglio dei rischi e delle mitigazioni: capitolo 13", size=7.6,
          ha="left", color=INK_MUTED)

    save(fig, "06_risk_matrix.png")


# === Figure 07 - Adoption roadmap ========================================


def fig07_roadmap():
    fig, ax = canvas((12.2, 6.7))
    ax.set_xlim(0, 12.2)
    ax.set_ylim(0, 6.7)

    title_block(ax, 0.25, 6.25, "Roadmap di adozione",
                "Tre ondate in dodici mesi; ogni ondata termina con un gate go/no-go")

    # Timeline
    TL_X0, TL_X1, TL_Y = 1.7, 11.7, 1.0
    MONTHS = 12
    ax.plot([TL_X0, TL_X1], [TL_Y, TL_Y], color=BORDER, lw=1.6, zorder=1)
    for m in range(0, MONTHS + 1, 2):
        x = TL_X0 + (TL_X1 - TL_X0) * m / MONTHS
        ax.plot([x, x], [TL_Y - 0.07, TL_Y + 0.07], color=INK_MUTED, lw=1.1)
        label(ax, x, TL_Y - 0.32, f"M{m}", size=7.8, color=INK_SOFT)

    def mx(m):
        return TL_X0 + (TL_X1 - TL_X0) * m / MONTHS

    waves = [
        ("Ondata 1 - Pilota", 0, 4, "emerald",
         "5 store pilota - pipeline ingest e blur\nmodello detection v1 - DPIA, baseline KPI"),
        ("Ondata 2 - Scala", 4, 8, "blue",
         "50 store - registry e canary - dashboard BI\ndrift monitoring - moduli code e flussi"),
        ("Ondata 3 - Industrializzazione", 8, 12, "violet",
         "180 store - planogram adherence\nFinOps a regime - audit interno"),
    ]
    for k, (name, m0, m1, acc, detail) in enumerate(waves):
        y = 4.35 - k * 1.2
        box(ax, mx(m0), y, mx(m1) - mx(m0) - 0.06, 1.0, fill=TINT[acc],
            border=ACCENT[acc], lw=1.2)
        label(ax, mx(m0) + 0.15, y + 0.74, name, size=8.8, weight="bold",
              color=ACCENT[acc], ha="left")
        label(ax, mx(m0) + 0.15, y + 0.32, detail, size=7.0, color=INK_SOFT,
              ha="left")

    # Milestones (diamonds on the timeline)
    milestones = [(4, "go/no-go pilota:\nKPI baseline raggiunti"),
                  (8, "review di scala:\ncosto/store nei limiti"),
                  (12, "audit completo:\nconformità e ROI")]
    for m, txt in milestones:
        x = mx(m)
        ax.scatter([x], [TL_Y], marker="D", s=110, c=ACCENT["amber"], zorder=5,
                   edgecolors=INK, linewidths=0.6)
        label(ax, x, TL_Y + 0.55, txt, size=7.2, color=INK_SOFT)

    label(ax, 1.7, 0.22, "Ruoli chiave: sponsor loss prevention, architetto della "
          "piattaforma, ML engineer, DPO, security officer, store operations.",
          size=7.8, color=INK_MUTED, ha="left")

    save(fig, "07_roadmap.png")


# === Driver ==============================================================


def main():
    fig01_architecture()
    fig02_edge_cloud()
    fig03_data_lifecycle()
    fig04_realtime_path()
    fig05_model_lifecycle()
    fig06_risk_matrix()
    fig07_roadmap()
    print("7 figures generated.")


if __name__ == "__main__":
    main()
