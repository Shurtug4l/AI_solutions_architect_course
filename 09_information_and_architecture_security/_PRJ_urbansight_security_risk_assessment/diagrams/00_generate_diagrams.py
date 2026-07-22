"""
Diagram generator for the UrbanSight security risk assessment capstone.

Generates the five PNG figures referenced by the main DOCX report. Output
paths are anchored to this file's directory, so the script runs from any
working directory (small deviation from the module 04/05/07 generators,
which required running from inside diagrams/).

Style choices
-------------
Consistent with the module 04/05/07 capstones (portfolio continuity):
- straight horizontal / vertical arrows in flow figures;
- no background grid, light background, near-black ink, soft accents;
- one figure, one message; labels kept out of the way.

Figure inventory
----------------
    01  UrbanSight ecosystem and trust boundaries      (cap. 3)
    02  AI lifecycle attack surface                    (cap. 5)
    03  Risk heatmap 3x3 (probability x impact)        (cap. 6)
    04  Simulated incident timeline                    (cap. 9)
    05  Regulatory frame: GDPR / AI Act / NIS 2        (cap. 8)
"""

from __future__ import annotations

import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch


# === Shared style ========================================================

OUT_DIR = os.path.dirname(os.path.abspath(__file__))

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
        accent_w=0.07, radius=0.035, zorder=2):
    """Rounded rectangle with optional left accent stripe."""
    rect = FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad=0,rounding_size={radius}",
        facecolor=fill, edgecolor=border, linewidth=lw, zorder=zorder)
    ax.add_patch(rect)
    if accent:
        stripe = FancyBboxPatch(
            (x, y), accent_w, h,
            boxstyle=f"round,pad=0,rounding_size={radius}",
            facecolor=ACCENT[accent], edgecolor="none", zorder=zorder + 1)
        ax.add_patch(stripe)
    return rect


def label(ax, x, y, text, *, size=10, weight="normal", color=INK,
          ha="center", va="center", zorder=5, style="normal"):
    ax.text(x, y, text, size=size, weight=weight, color=color,
            ha=ha, va=va, zorder=zorder, style=style)


def arrow_h(ax, x0, x1, y, color=INK_SOFT, lw=1.4, zorder=3):
    ax.add_patch(FancyArrowPatch((x0, y), (x1, y), arrowstyle="-|>",
                                 mutation_scale=11, color=color, lw=lw,
                                 zorder=zorder))


def arrow_v(ax, x, y0, y1, color=INK_SOFT, lw=1.4, zorder=3):
    ax.add_patch(FancyArrowPatch((x, y0), (x, y1), arrowstyle="-|>",
                                 mutation_scale=11, color=color, lw=lw,
                                 zorder=zorder))


def save(fig, name):
    fig.savefig(os.path.join(OUT_DIR, name), dpi=DPI, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"  {name}")


# === Figure 01: ecosystem and trust boundaries ===========================


def fig01_ecosystem():
    fig, ax = canvas((11.4, 6.4))
    ax.set_xlim(0, 11.4)
    ax.set_ylim(0, 6.4)

    # Three trust zones as vertical bands.
    zones = [
        (0.15, 3.30, "Zona campo (città)", "slate"),
        (3.65, 4.45, "Piattaforma UrbanSight (cloud)", "blue"),
        (8.30, 2.95, "Enti e integrazioni", "emerald"),
    ]
    for zx, zw, zt, zc in zones:
        box(ax, zx, 0.45, zw, 5.35, fill=TINT[zc], border=BORDER_SOFT, lw=1.0,
            radius=0.05, zorder=1)
        label(ax, zx + zw / 2, 5.55, zt, size=10.5, weight="bold",
              color=ACCENT[zc])

    # Trust boundaries between zones. zorder sotto i box e sotto la banda
    # Terze parti: le tratteggiate non devono attraversare gli elementi.
    for bx in (3.475, 8.125):
        ax.plot([bx, bx], [0.3, 6.0], ls=(0, (5, 4)), color=ACCENT["rose"],
                lw=1.4, zorder=1.5)
    label(ax, 3.475, 6.15, "trust boundary", size=8.2, color=ACCENT["rose"],
          style="italic")
    label(ax, 8.125, 6.15, "trust boundary", size=8.2, color=ACCENT["rose"],
          style="italic")

    # Field zone.
    field = [
        (0.35, 4.30, "Telecamere fisse\ne sensori di flusso", "slate"),
        (0.35, 3.10, "Unità edge\n(pre-analisi video)", "slate"),
        (0.35, 1.90, "Rete di raccolta\n(4G/5G, fibra urbana)", "slate"),
    ]
    for fx, fy, ft, fc in field:
        box(ax, fx, fy, 2.9, 0.95, accent=fc)
        label(ax, fx + 1.55, fy + 0.475, ft, size=9)

    # Platform zone, two columns.
    plat_left = [
        (3.85, 4.30, "Ingestion e storage\nfootage cifrato", "cyan"),
        (3.85, 3.10, "Dataset di training\ne pipeline di labeling", "amber"),
        (3.85, 1.90, "Training e validazione\nmodelli CV", "amber"),
    ]
    # Colonna destra rientrata a 6.20: il corridoio largo 0.40 tra le due
    # colonne da' corsa sufficiente alla punta della freccia del gomito
    # training -> registry (con 0.125 la punta collassava).
    plat_right = [
        (6.20, 4.30, "Inference real-time\n(flussi, pericoli, pedoni)", "blue"),
        (6.20, 3.10, "Model registry\n(pesi e versioni)", "violet"),
        (6.20, 1.90, "API e dashboard\noperative", "blue"),
    ]
    for px, py, pt, pc in plat_left:
        box(ax, px, py, 1.95, 0.95, accent=pc)
        label(ax, px + 1.02, py + 0.475, pt, size=8.4)
    for px, py, pt, pc in plat_right:
        box(ax, px, py, 1.80, 0.95, accent=pc)
        label(ax, px + 0.945, py + 0.475, pt, size=8.4)

    # Institutions zone.
    inst = [
        (8.50, 4.30, "Centrale semaforica\ndel comune", "emerald"),
        (8.50, 3.10, "Operatori comunali\ne di controllo", "emerald"),
        (8.50, 1.90, "Dashboard di\npianificazione urbana", "emerald"),
    ]
    for ix, iy, it, ic in inst:
        box(ax, ix, iy, 2.55, 0.95, accent=ic)
        label(ax, ix + 1.32, iy + 0.475, it, size=9)

    # Third parties band at the bottom, crossing the platform boundary.
    box(ax, 0.35, 0.60, 10.5, 0.85, fill=TINT["rose"], border=ACCENT["rose"],
        lw=1.0, zorder=2)
    label(ax, 1.15, 1.02, "Terze parti", size=9.5, weight="bold",
          color=ACCENT["rose"], ha="left")
    label(ax, 6.55, 1.02,
          "vendor di labeling  |  cloud provider  |  fornitore manutenzione "
          "(accesso VPN)  |  modelli pre-addestrati", size=8.2, color=INK_SOFT)

    # Main data flows.
    arrow_h(ax, 3.25, 3.85, 4.775)                     # field -> ingestion
    arrow_h(ax, 5.80, 6.20, 4.775)                     # storage -> inference
    arrow_v(ax, 4.825, 4.30, 4.05)                     # storage -> dataset
    arrow_v(ax, 4.825, 3.10, 2.85)                     # dataset -> training
    # training -> registry: orthogonal elbow around the column gap
    ax.plot([5.80, 5.975], [2.375, 2.375], color=INK_SOFT, lw=1.4, zorder=3)
    ax.plot([5.975, 5.975], [2.375, 3.575], color=INK_SOFT, lw=1.4, zorder=3)
    arrow_h(ax, 5.975, 6.20, 3.575)
    arrow_v(ax, 7.10, 4.05, 4.30)                      # registry -> inference
    arrow_v(ax, 7.10, 3.10, 2.85)                      # registry -> api
    arrow_h(ax, 8.00, 8.50, 4.775)                     # inference -> semafori
    arrow_h(ax, 8.00, 8.50, 2.375)                     # api -> dashboard
    arrow_v(ax, 9.775, 2.85, 3.10)                     # dashboard -> operatori

    save(fig, "01_ecosystem_trust_boundaries.png")


# === Figure 02: AI lifecycle attack surface ==============================


def fig02_lifecycle():
    fig, ax = canvas((11.4, 5.2))
    ax.set_xlim(0, 11.4)
    ax.set_ylim(0, 5.2)

    label(ax, 0.25, 4.85, "Ciclo di vita del sistema e superficie di attacco",
          size=11, weight="bold", ha="left")

    phases = [
        ("Raccolta dati", "cyan"),
        ("Labeling", "amber"),
        ("Training", "amber"),
        ("Registry e rilascio", "violet"),
        ("Inference", "blue"),
        ("Attuazione urbana", "emerald"),
    ]
    w, gap, y, h = 1.62, 0.22, 3.55, 0.80
    x = 0.30
    centers = []
    for i, (pt, pc) in enumerate(phases):
        box(ax, x, y, w, h, accent=pc)
        label(ax, x + w / 2 + 0.03, y + h / 2, pt, size=8.6)
        centers.append(x + w / 2)
        if i < len(phases) - 1:
            arrow_h(ax, x + w, x + w + gap, y + h / 2)
        x += w + gap

    # Threats anchored to phases.
    threats = [
        (0, "Esfiltrazione footage\n(dati personali)", 2.55),
        (1, "Manipolazione label,\nvendor compromesso", 2.55),
        (2, "Data poisoning,\nbackdoor nel modello", 1.65),
        (3, "Furto / estrazione\ndel modello", 2.55),
        (4, "Evasion adversarial,\nquery di estrazione", 1.65),
        (5, "DoS su componenti\ncritici, decisioni errate", 2.55),
    ]
    for idx, tt, ty in threats:
        cx = centers[idx]
        box(ax, cx - 0.86, ty - 0.38, 1.72, 0.76, fill=TINT["rose"],
            border=ACCENT["rose"], lw=0.9)
        label(ax, cx, ty, tt, size=7.6, color="#9F1239")
        arrow_v(ax, cx, ty + 0.38, y - 0.06, color=ACCENT["rose"], lw=1.1)

    # Cross-cutting band.
    box(ax, 0.30, 0.35, 10.82, 0.72, fill=SURFACE_SOFT, border=BORDER, lw=1.0)
    label(ax, 5.71, 0.71,
          "Trasversali: insider threat  |  supply chain (dipendenze, modelli "
          "pre-addestrati)  |  assenza di auditability delle decisioni",
          size=8.6, color=INK_SOFT)

    save(fig, "02_lifecycle_attack_surface.png")


# === Figure 03: risk heatmap =============================================


def fig03_heatmap():
    fig, ax = canvas((8.6, 6.2))
    ax.set_xlim(0, 8.6)
    ax.set_ylim(0, 6.2)

    # Cell fill by criticality (impact col 0..2, probability row 0..2).
    cell_fill = [
        ["#ECFDF5", "#FEF9C3", "#FFEDD5"],   # P bassa
        ["#FEF9C3", "#FFEDD5", "#FEE2E2"],   # P media
        ["#FFEDD5", "#FEE2E2", "#FECACA"],   # P alta
    ]
    # Risk IDs placed in cells (impact index, probability index).
    placed = {
        (2, 0): ["R06"],
        (1, 1): ["R03", "R05", "R08", "R09"],
        (2, 1): ["R01", "R02", "R07"],
        (1, 2): ["R10"],
        (2, 2): ["R04"],
    }

    x0, y0, cw, ch = 1.55, 1.15, 2.15, 1.45
    imp = ["Basso", "Medio", "Alto"]
    prob = ["Bassa", "Media", "Alta"]
    for pi in range(3):
        for ii in range(3):
            cx, cy = x0 + ii * cw, y0 + pi * ch
            box(ax, cx + 0.05, cy + 0.05, cw - 0.10, ch - 0.10,
                fill=cell_fill[pi][ii], border=BORDER_SOFT, lw=0.9)
            ids = placed.get((ii, pi), [])
            if ids:
                label(ax, cx + cw / 2, cy + ch / 2, "  ".join(ids),
                      size=10.5, weight="bold", color=INK)
    for ii, name in enumerate(imp):
        label(ax, x0 + ii * cw + cw / 2, y0 - 0.32, name, size=9.5,
              color=INK_SOFT)
    for pi, name in enumerate(prob):
        label(ax, x0 - 0.42, y0 + pi * ch + ch / 2, name, size=9.5,
              color=INK_SOFT, ha="right")
    label(ax, x0 + 1.5 * cw, y0 - 0.75, "Impatto", size=10.5, weight="bold")
    ax.text(0.42, y0 + 1.5 * ch, "Probabilità", size=10.5, weight="bold",
            color=INK, ha="center", va="center", rotation=90, zorder=5)

    # Legend.
    leg = [("Priorità critica", "#FECACA"), ("Alta", "#FEE2E2"),
           ("Media", "#FFEDD5"), ("Bassa", "#FEF9C3"),
           ("Accettabile", "#ECFDF5")]
    lx = x0 + 3 * cw + 0.35
    label(ax, lx, y0 + 3 * ch - 0.15, "Lettura", size=9.5, weight="bold",
          ha="left")
    for i, (lt, lc) in enumerate(leg):
        ly = y0 + 3 * ch - 0.65 - i * 0.5
        box(ax, lx, ly - 0.14, 0.34, 0.28, fill=lc, border=BORDER_SOFT, lw=0.8)
        label(ax, lx + 0.48, ly, lt, size=8.6, ha="left", color=INK_SOFT)

    save(fig, "03_risk_heatmap.png")


# === Figure 04: incident timeline ========================================


def fig04_timeline():
    fig, ax = canvas((11.4, 5.6))
    ax.set_xlim(0, 11.4)
    ax.set_ylim(0, 5.6)

    label(ax, 0.25, 5.30, "Incidente INC-2026-004: linea temporale",
          size=11, weight="bold", ha="left")

    # Time axis.
    ax.plot([0.5, 11.0], [2.85, 2.85], color=INK_SOFT, lw=1.6, zorder=2)
    events = [
        (0.85, "2026-05-12\n09:41", "Phishing al tecnico\ndel fornitore", "rose", "up"),
        (2.15, "2026-05-12\n14:26", "Login VPN anomalo,\nnon rilevato", "rose", "down"),
        (3.45, "2026-05-13/14", "Accesso a footage\ne model registry", "rose", "up"),
        (4.75, "2026-05-14\n23:52", "Alert egress\nanomalo", "amber", "down"),
        (6.05, "2026-05-15\n11:30", "Incidente confermato,\ncontainment avviato", "blue", "up"),
        (7.35, "2026-05-15\n18:40", "Early warning CSIRT,\ninformativa al titolare", "violet", "down"),
        (8.65, "2026-05-16", "Notifica del comune\nal Garante (72 h)", "violet", "up"),
        (9.75, "2026-05-18", "Notifica NIS 2\ncompleta (72 h)", "violet", "down"),
        (10.65, "2026-06-14", "Relazione finale\n(1 mese)", "emerald", "up"),
    ]
    for ex, edate, etext, ecol, side in events:
        ax.plot([ex], [2.85], marker="o", ms=7, color=ACCENT[ecol], zorder=4)
        if side == "up":
            ty_box, ty_date = 3.95, 2.42
        else:
            ty_box, ty_date = 1.55, 3.24
        ax.plot([ex, ex], [2.85, ty_box - 0.42 if side == "up" else ty_box + 0.42],
                color=BORDER, lw=1.0, zorder=1)
        label(ax, ex, ty_date, edate, size=7.2, color=INK_MUTED)
        # 1.50 di larghezza: i testi piu' lunghi arrivano a ~1.25" e con i
        # box da 1.24 sbordavano; i vicini sullo stesso lato distano 2.6.
        box(ax, ex - 0.75, ty_box - 0.40, 1.50, 0.80, fill=TINT[ecol],
            border=ACCENT[ecol], lw=0.9)
        label(ax, ex, ty_box, etext, size=6.8, color=INK)

    # Detection gap annotation, anchored to the first login (not the
    # phishing mail: dwell time starts when the attacker is inside).
    ax.plot([2.15, 4.75], [0.62, 0.62], color=ACCENT["rose"], lw=1.2)
    ax.plot([2.15, 2.15], [0.55, 0.69], color=ACCENT["rose"], lw=1.2)
    ax.plot([4.75, 4.75], [0.55, 0.69], color=ACCENT["rose"], lw=1.2)
    label(ax, 3.45, 0.38, "finestra di permanenza non rilevata: ~57 ore",
          size=8.4, color=ACCENT["rose"], style="italic")

    save(fig, "04_incident_timeline.png")


# === Figure 05: regulatory frame =========================================


def fig05_regulatory():
    fig, ax = canvas((11.4, 6.0))
    ax.set_xlim(0, 11.4)
    ax.set_ylim(0, 6.0)

    cols = [
        (0.30, "GDPR", "Reg. UE 2016/679", "blue",
         ["Oggetto: dati personali nel footage\ne nei metadati derivati",
          "Comune: titolare del trattamento\nUrbanSight: responsabile (art. 28)",
          "Base giuridica: interesse pubblico\n(art. 6.1.e), non il consenso",
          "DPIA obbligatoria: sorveglianza\nsistematica su larga scala (art. 35)"]),
        (4.00, "AI Act", "Reg. UE 2024/1689", "violet",
         ["Oggetto: il sistema AI e il suo\nciclo di vita",
          "Sistema high-risk: componente di\nsicurezza del traffico (Annex III)",
          "UrbanSight: provider\nComune: deployer (FRIA, art. 27)",
          "Obblighi chiave: risk management,\ndata governance, logging, oversight"]),
        (7.70, "NIS 2", "Dir. UE 2022/2555\nD.lgs. 138/2024", "emerald",
         ["Oggetto: resilienza cyber\ndell'organizzazione e del servizio",
          "Comune: pubblica amministrazione\nin ambito (Annex I)",
          "UrbanSight: fornitore di ente in\nambito, obblighi via audit cliente",
          "Obblighi chiave: notifica CSIRT,\nmultirischio, formazione, continuità"]),
    ]
    for cx, ct, csub, cc, items in cols:
        box(ax, cx, 1.45, 3.40, 4.10, fill=TINT[cc], border=BORDER_SOFT,
            lw=1.0, radius=0.05, zorder=1)
        label(ax, cx + 1.70, 5.20, ct, size=12, weight="bold", color=ACCENT[cc])
        label(ax, cx + 1.70, 4.86, csub, size=7.8, color=INK_MUTED)
        for i, it in enumerate(items):
            iy = 4.28 - i * 0.72
            box(ax, cx + 0.16, iy - 0.30, 3.08, 0.62, fill=SURFACE,
                border=BORDER_SOFT, lw=0.8)
            label(ax, cx + 1.70, iy + 0.01, it, size=7.4, color=INK_SOFT)

    # Interaction band.
    box(ax, 0.30, 0.22, 10.80, 0.95, fill=SURFACE_SOFT, border=BORDER, lw=1.0)
    label(ax, 5.70, 0.94, "Punti di contatto", size=8.6, weight="bold",
          color=INK_SOFT)
    label(ax, 5.70, 0.55,
          "stesso incidente, due canali di notifica (Garante 72 h, CSIRT 24/72 h)\n"
          "il logging dell'AI Act (art. 12) copre il gap di auditability (R10) "
          "e alimenta la forensics", size=7.8, color=INK_SOFT)

    save(fig, "05_regulatory_frame.png")


# === Main ================================================================


def main():
    print("Generating UrbanSight capstone figures:")
    fig01_ecosystem()
    fig02_lifecycle()
    fig03_heatmap()
    fig04_timeline()
    fig05_regulatory()
    print("Done.")


if __name__ == "__main__":
    main()
