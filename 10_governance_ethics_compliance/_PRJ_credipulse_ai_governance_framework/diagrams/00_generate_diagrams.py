"""
Generatore dei diagrammi per il capstone del modulo 10 - Governance,
Etica e Compliance dell'AI (caso CrediPulse, framework di AI governance
per il credit scoring PMI).

Produce cinque PNG in questa directory, richiamati da generate_docx.py:

    01_operating_model.png       modello operativo: organi e tre linee di difesa
    02_model_lifecycle_gates.png ciclo di vita del modello con gate G0-G4
    03_risk_heatmap.png          heatmap probabilità x impatto (10 categorie)
    04_regulatory_frame.png      quadro normativo intorno al sistema di scoring
    05_document_architecture.png architettura documentale di accountability

Le valutazioni della heatmap replicano la tabella del capitolo 6 del
report: ogni modifica ai rating va riportata in entrambi i file (il
generatore docx resta offline per convenzione di modulo, quindi la
struttura dati non è condivisibile via import).

Esecuzione:
    uv run --with matplotlib python 00_generate_diagrams.py
"""

import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

BASE = os.path.dirname(os.path.abspath(__file__))

# Palette allineata al report (stessa famiglia del capstone 09).
INK = "#0F172A"
INK_SOFT = "#334155"
INK_MUT = "#64748B"
BLUE_DEEP = "#1E3A5F"
BLUE = "#1E40AF"
BLUE_MID = "#2563EB"
FILL_LIGHT = "#F1F5F9"
FILL_BLUE = "#DBEAFE"
FILL_AMBER = "#FEF3C7"
AMBER = "#F59E0B"
AMBER_DARK = "#92400E"
GREEN = "#DCFCE7"
ORANGE = "#FED7AA"
RED = "#FECACA"

DPI = 200


def box(ax, cx, cy, w, h, title, lines=(), fc="white", ec=BLUE_DEEP,
        title_fs=10, fs=8.2, lw=1.4, title_color=None, zorder=3,
        body_gap=0.34):
    """Riquadro arrotondato con titolo e righe di dettaglio, centrato in (cx, cy).

    Il corpo è ancorato a distanza fissa sotto il titolo (body_gap):
    l'offset proporzionale al numero di righe apriva un vuoto vistoso nei
    box alti (verificato a occhio sul primo render)."""
    patch = FancyBboxPatch((cx - w / 2, cy - h / 2), w, h,
                           boxstyle="round,pad=0.02,rounding_size=0.08",
                           fc=fc, ec=ec, lw=lw, zorder=zorder)
    ax.add_patch(patch)
    if lines:
        ty = cy + h / 2 - 0.30
        ax.text(cx, ty, title, ha="center", va="center", fontsize=title_fs,
                fontweight="bold", color=title_color or INK, zorder=zorder + 1)
        body = "\n".join(lines)
        ax.text(cx, ty - body_gap, body,
                ha="center", va="top", fontsize=fs, color=INK_SOFT,
                zorder=zorder + 1, linespacing=1.45)
    else:
        ax.text(cx, cy, title, ha="center", va="center", fontsize=title_fs,
                fontweight="bold", color=title_color or INK, zorder=zorder + 1)
    return patch


def arrow(ax, p0, p1, color=INK_MUT, lw=1.6, style="-|>", ms=13,
          connstyle="arc3,rad=0.0", ls="solid", zorder=2):
    """Freccia ancorata a coordinate esplicite (bordi dei box, non centri)."""
    a = FancyArrowPatch(p0, p1, arrowstyle=style, mutation_scale=ms,
                        color=color, lw=lw, linestyle=ls,
                        connectionstyle=connstyle, zorder=zorder,
                        shrinkA=0, shrinkB=0)
    ax.add_patch(a)
    return a


def label(ax, x, y, text, fs=8, color=INK_MUT, ha="center", style="italic",
          zorder=4, bg=True):
    kw = dict(ha=ha, va="center", fontsize=fs, color=color, zorder=zorder)
    if style:
        kw["style"] = style
    if bg:
        kw["bbox"] = dict(boxstyle="round,pad=0.15", fc="white", ec="none")
    ax.text(x, y, text, **kw)


def new_ax(w, h):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(0, w)
    ax.set_ylim(0, h)
    ax.axis("off")
    return fig, ax


def save(fig, name):
    path = os.path.join(BASE, name)
    fig.savefig(path, dpi=DPI, bbox_inches="tight", pad_inches=0.15,
                facecolor="white")
    plt.close(fig)
    print(f"Scritto: {path}")


# === Figura 1: modello operativo =========================================


def fig_operating_model():
    fig, ax = new_ax(12.4, 7.6)

    # Consiglio di amministrazione.
    box(ax, 6.2, 6.95, 7.4, 0.95, "Consiglio di amministrazione",
        ["Approva il framework e il risk appetite AI; riceve il reporting periodico e gli esiti degli audit"],
        fc=FILL_LIGHT, title_fs=11, fs=8.6)

    # Comitato AI Governance.
    box(ax, 6.2, 5.42, 8.6, 1.42, "Comitato AI Governance",
        ["Autorità di gate sul ciclo di vita (G0-G4) con potere di veto reale e decisioni verbalizzate",
         "Composizione: CRO (presidenza), Responsabile AI, DPO, Compliance, Business credito"],
        fc=FILL_BLUE, title_fs=11, fs=8.6)

    arrow(ax, (6.2, 6.13), (6.2, 6.47), color=INK_SOFT)
    label(ax, 7.6, 6.30, "reporting trimestrale", fs=8)

    # Tre linee di difesa.
    y_col, h_col = 2.55, 3.6
    box(ax, 2.25, y_col, 3.7, h_col, "Prima linea",
        ["Business credito e sviluppo",
         "",
         "Model Owner (rischio del modello)",
         "Model Steward (esercizio, doc)",
         "Data Owner (dati e qualità)",
         "Ingegneria ML / MLOps",
         "",
         "Possiede modelli e rischi;",
         "produce le evidenze"],
        fc="white", title_fs=10.5, fs=8.4)
    box(ax, 6.2, y_col, 3.7, h_col, "Seconda linea",
        ["Controllo rischi e conformità",
         "",
         "Funzione risk (CRO)",
         "Compliance",
         "DPO",
         "",
         "Scrive policy e standard,",
         "sfida le scelte della prima linea;",
         "non possiede modelli"],
        fc="white", title_fs=10.5, fs=8.4)
    box(ax, 10.15, y_col, 3.7, h_col, "Terza linea",
        ["Assurance indipendente",
         "",
         "Internal audit",
         "",
         "Verifica framework ed evidenze",
         "con audit periodici;",
         "non scrive policy,",
         "riporta al CdA"],
        fc="white", title_fs=10.5, fs=8.4)

    for x in (2.25, 6.2, 10.15):
        arrow(ax, (x, y_col + h_col / 2), (x, 4.69), color=INK_MUT, lw=1.3)
    # L'etichetta sta nella banda vuota tra colonne e comitato, non dentro
    # il box (primo render: collisione con la riga di composizione).
    label(ax, 4.22, 4.53, "gate, escalation e pareri", fs=8)

    # Inventario: spina dorsale comune.
    box(ax, 6.2, 0.42, 11.6, 0.62,
        "Inventario dei modelli: perimetro condiviso dalle tre linee, nessun modello fuori registro",
        fc=FILL_AMBER, ec=AMBER, title_fs=9.3, title_color=AMBER_DARK)
    save(fig, "01_operating_model.png")


# === Figura 2: ciclo di vita con gate ====================================


def fig_lifecycle():
    fig, ax = new_ax(14.5, 5.7)

    stages = [
        ("Intake e\nclassificazione", ["Proposta d'uso", "Classificazione AI Act", "Iscrizione a inventario"]),
        ("Design e\nsviluppo", ["Selezione dati e LIA", "Metrica di equità", "scelta e motivata"]),
        ("Validazione\nindipendente", ["Performance e bias", "per segmento", "Robustezza e stress"]),
        ("Approvazione\ne rilascio", ["Doc tecnica e Model Card", "FRIA e oversight design", "Sign-off del comitato"]),
        ("Esercizio e\nmonitoraggio", ["KPI e drift", "Post-market (art. 72)", "Incidenti (art. 73)"]),
        ("Dismissione", ["Piano di uscita,", "conservazione di", "log e documenti"]),
    ]
    xs = [1.30, 3.80, 6.30, 8.80, 11.30, 13.55]
    y = 3.35
    w, h = 1.85, 1.9
    w_last = 1.65

    for i, (title, lines) in enumerate(stages):
        bw = w_last if i == len(stages) - 1 else w
        box(ax, xs[i], y, bw, h, title, lines, fc="white", title_fs=9.6,
            fs=7.8, body_gap=0.50)

    gates = ["G0", "G1", "G2", "G3", "G4"]
    for i, gid in enumerate(gates):
        x0 = xs[i] + (w / 2)
        x1 = xs[i + 1] - ((w_last if i + 1 == len(stages) - 1 else w) / 2)
        xm = (x0 + x1) / 2
        arrow(ax, (x0, y), (x1, y), color=INK_SOFT, lw=1.7, ms=14, zorder=4)
        circ = plt.Circle((xm, y), 0.16, fc=BLUE, ec="white", lw=1.5, zorder=5)
        ax.add_patch(circ)
        ax.text(xm, y, gid, ha="center", va="center", fontsize=7.6,
                fontweight="bold", color="white", zorder=6)

    # Ritorno: modifica sostanziale o retraining fuori envelope. Il raggio
    # negativo fa curvare l'arco verso il basso, lontano dai box (col raggio
    # positivo la sagitta li attraversava).
    arrow(ax, (11.30, 2.36), (3.80, 2.36),
          color=AMBER_DARK, lw=1.7, connstyle="arc3,rad=-0.06", ms=14)
    label(ax, 7.55, 1.50,
          "modifica sostanziale o retraining fuori dall'envelope dichiarato: si riapre il percorso da G1 a G3",
          fs=8.4, color=AMBER_DARK)

    # Legenda dei criteri di gate.
    ax.text(7.25, 0.90,
            "G0 classificazione documentata   |   G1 dati e metriche approvati   |   "
            "G2 validazione superata   |   G3 conformità completa   |   G4 review periodica superata",
            ha="center", va="center", fontsize=8.3, color=INK_MUT)

    # Fascia superiore: chi presidia i gate.
    box(ax, 7.25, 5.18, 13.6, 0.6,
        "Ogni gate è deciso dal Comitato AI Governance su evidenze della prima linea e parere della seconda; l'esito è verbalizzato",
        fc=FILL_BLUE, ec=BLUE_DEEP, title_fs=9.2)
    save(fig, "02_model_lifecycle_gates.png")


# === Figura 3: heatmap dei rischi ========================================

# Rating replicati dalla tabella del capitolo 6 del report (unica fonte
# nel generatore docx): (probabilità, impatto) per categoria.
HEAT = {
    ("Alta", "Alto"): [("RC01", "Discriminazione e bias")],
    ("Media", "Alto"): [("RC02", "Accuratezza e affidabilità"),
                        ("RC04", "Privacy e protezione dati"),
                        ("RC10", "Normativo e compliance")],
    ("Alta", "Medio"): [("RC03", "Trasparenza e spiegabilità"),
                        ("RC07", "Governance e accountability")],
    ("Media", "Medio"): [("RC05", "Robustezza operativa"),
                         ("RC08", "Fornitori terzi")],
    ("Bassa", "Alto"): [("RC06", "Cybersecurity e integrità"),
                        ("RC09", "Sistemico e di mercato")],
}

CELL_COLOR = {
    ("Bassa", "Basso"): GREEN, ("Bassa", "Medio"): GREEN,
    ("Media", "Basso"): GREEN, ("Media", "Medio"): FILL_AMBER,
    ("Bassa", "Alto"): FILL_AMBER, ("Alta", "Basso"): FILL_AMBER,
    ("Media", "Alto"): ORANGE, ("Alta", "Medio"): ORANGE,
    ("Alta", "Alto"): RED,
}


def fig_heatmap():
    fig, ax = new_ax(11.4, 7.0)
    probs = ["Bassa", "Media", "Alta"]
    imps = ["Basso", "Medio", "Alto"]
    cw, ch = 3.15, 1.85
    x0, y0 = 1.35, 0.95

    for r, p in enumerate(probs):
        for c, i in enumerate(imps):
            cx = x0 + c * cw
            cy = y0 + r * ch
            ax.add_patch(plt.Rectangle((cx, cy), cw - 0.12, ch - 0.12,
                                       fc=CELL_COLOR[(p, i)], ec="white",
                                       lw=2, zorder=1))
            chips = HEAT.get((p, i), [])
            for k, (rid, rname) in enumerate(chips):
                ty = cy + ch - 0.45 - k * 0.52
                ax.add_patch(FancyBboxPatch((cx + 0.16, ty - 0.17),
                                            cw - 0.44, 0.40,
                                            boxstyle="round,pad=0.01,rounding_size=0.05",
                                            fc="white", ec=INK_MUT, lw=0.9,
                                            zorder=3))
                ax.text(cx + 0.30, ty + 0.03, rid, fontsize=8.2,
                        fontweight="bold", color=BLUE, va="center", zorder=4)
                ax.text(cx + 0.84, ty + 0.03, rname, fontsize=7.6,
                        color=INK_SOFT, va="center", zorder=4)

    for c, i in enumerate(imps):
        ax.text(x0 + c * cw + cw / 2 - 0.06, y0 - 0.28, i, ha="center",
                fontsize=9.5, color=INK, fontweight="bold")
    for r, p in enumerate(probs):
        ax.text(x0 - 0.25, y0 + r * ch + ch / 2 - 0.06, p, ha="right",
                va="center", fontsize=9.5, color=INK, fontweight="bold")
    ax.text(x0 + 1.5 * cw - 0.06, 0.28, "Severità (impatto atteso)",
            ha="center", fontsize=10.5, fontweight="bold", color=INK_SOFT)
    ax.text(0.32, y0 + 1.5 * ch, "Probabilità", ha="center", va="center",
            fontsize=10.5, fontweight="bold", color=INK_SOFT, rotation=90)

    # Legenda delle severità.
    leg = [("Critica", RED), ("Alta", ORANGE), ("Media", FILL_AMBER),
           ("Bassa / accettabile", GREEN)]
    lx = x0
    ly = y0 + 3 * ch + 0.30
    # "Priorità", non "severità": la traccia riserva "severità" alla scala
    # B/M/A dell'impatto; l'esito della matrice nel report si chiama priorità.
    ax.text(lx, ly + 0.34, "Priorità risultante", fontsize=9,
            fontweight="bold", color=INK)
    for k, (name, colr) in enumerate(leg):
        bx = lx + k * 2.15
        ax.add_patch(plt.Rectangle((bx, ly - 0.12), 0.34, 0.24, fc=colr,
                                   ec=INK_MUT, lw=0.6))
        ax.text(bx + 0.45, ly, name, fontsize=8.6, va="center", color=INK_SOFT)
    save(fig, "03_risk_heatmap.png")


# === Figura 4: quadro normativo ==========================================


def fig_regulatory_frame():
    fig, ax = new_ax(12.6, 7.4)

    # Sistema al centro.
    box(ax, 6.3, 3.7, 4.3, 1.25, "Sistema di scoring creditizio PMI",
        ["AI ad alto rischio (Annex III, punto 5(b))",
         "CrediPulse: provider e deployer"],
        fc=FILL_BLUE, title_fs=10.5, fs=8.6, lw=1.8)

    # AI Act in alto.
    box(ax, 6.3, 6.35, 9.6, 1.5, "AI Act (Reg. UE 2024/1689) - vincolante, la spina dorsale",
        ["Provider: artt. 8-15 (requisiti), 17 (QMS), 43 e 47-49 (conformità, marcatura CE, registrazione), 72-73 (post-market, incidenti)",
         "Deployer: artt. 26 (uso e monitoraggio), 27 (FRIA), 86 (spiegazione al richiedente) - alto rischio applicabile dal 2026-08-02"],
        fc="white", ec=BLUE, title_fs=10, fs=8.2, lw=1.8)

    # GDPR a sinistra.
    box(ax, 2.10, 3.7, 3.3, 2.15, "GDPR (Reg. UE 2016/679)",
        ["Protegge i dati trattati:",
         "art. 6 base giuridica",
         "art. 9 + AI Act art. 10(5)",
         "art. 22 decisione automatizzata",
         "art. 25 by design, art. 35 DPIA"],
        fc="white", title_fs=9.8, fs=8.2)

    # Normativa finanziaria a destra.
    box(ax, 10.50, 3.7, 3.3, 2.15, "Normativa finanziaria",
        ["Governa l'attività di credito:",
         "EBA GL 2020/06 (LOM):",
         "governance dei modelli, credito",
         "DORA (Reg. UE 2022/2554):",
         "resilienza ICT, terze parti"],
        fc="white", title_fs=9.8, fs=8.2)

    # Volontari in basso.
    box(ax, 6.3, 1.05, 9.6, 1.35, "Framework volontari - come strutturare, non se",
        ["ISO/IEC 42001: sistema di gestione AI certificabile, integrabile con ISO 9001 / 27001 nel QMS dell'art. 17",
         "NIST AI RMF: ciclo Govern / Map / Measure / Manage per l'operatività del rischio"],
        fc=FILL_LIGHT, ec=INK_MUT, title_fs=9.8, fs=8.2)

    arrow(ax, (6.3, 5.60), (6.3, 4.33), color=BLUE, lw=1.8)
    arrow(ax, (3.85, 3.7), (4.15, 3.7), color=INK_MUT, lw=1.6)
    arrow(ax, (8.75, 3.7), (8.45, 3.7), color=INK_MUT, lw=1.6)
    arrow(ax, (6.3, 1.73), (6.3, 3.07), color=INK_MUT, lw=1.6, ls=(0, (4, 3)))
    label(ax, 6.95, 4.95, "regola il sistema", fs=8.2)
    label(ax, 6.95, 2.35, "struttura il QMS", fs=8.2)
    save(fig, "04_regulatory_frame.png")


# === Figura 5: architettura documentale ==================================


def fig_document_architecture():
    fig, ax = new_ax(13.0, 7.2)

    # Livello 1 (basso): evidenza operativa.
    y1 = 1.0
    box(ax, 2.0, y1, 2.9, 1.2, "Risk register",
        ["Art. 9 - ciclo iterativo", "Owner: Model Owner"], title_fs=9.4, fs=8.0)
    box(ax, 5.15, y1, 2.9, 1.2, "Evidenze data governance",
        ["Art. 10 - provenienza, bias", "Owner: Data Owner"], title_fs=9.4, fs=8.0)
    box(ax, 8.30, y1, 2.9, 1.2, "Log automatici",
        ["Artt. 12, 19 - tracciabilità", "Owner: Model Steward"], title_fs=9.4, fs=8.0)
    box(ax, 11.45, y1, 2.7, 1.2, "Report validazione\ne monitoraggio",
        ["Artt. 15, 72", "Owner: MO / Validazione"], title_fs=9.4, fs=8.0)
    label(ax, 0.45, y1, "Evidenza\noperativa", fs=9, color=INK, style=None, bg=False)

    # Livello 2 (centro): fascicolo e accountability.
    y2 = 3.55
    box(ax, 2.55, y2, 3.6, 1.45, "Documentazione tecnica",
        ["Art. 11, Annex IV", "Il fascicolo che l'autorità", "legge per prima"],
        fc=FILL_BLUE, title_fs=9.6, fs=8.0)
    box(ax, 6.35, y2, 3.3, 1.45, "Model Card + istruzioni d'uso",
        ["Distillato leggibile di Annex IV", "e art. 13, per audit e clienti",
         "Owner: Model Owner"], fc=FILL_BLUE, title_fs=9.6, fs=8.0)
    box(ax, 10.35, y2, 3.9, 1.45, "FRIA + DPIA",
        ["Artt. 27 AI Act e 35 GDPR,", "complementari per art. 27(4)",
         "Owner: DPO + Compliance"], fc=FILL_BLUE, title_fs=9.6, fs=8.0)
    label(ax, 0.45, y2, "Fascicolo e\naccountability", fs=9, color=INK, style=None, bg=False)

    # Livello 3 (alto): conformità e mercato.
    y3 = 6.1
    chain = [("Valutazione di conformità", "art. 43, controllo interno"),
             ("Dichiarazione UE", "art. 47"),
             ("Marcatura CE", "art. 48"),
             ("Registrazione UE", "art. 49, banca dati")]
    xs = [2.35, 5.85, 8.55, 11.35]
    ws = [3.3, 2.1, 2.0, 2.6]
    for (title, sub), cx, w in zip(chain, xs, ws):
        box(ax, cx, y3, w, 1.05, title, [sub], fc=FILL_AMBER, ec=AMBER,
            title_fs=9.3, fs=8.0)
    for i in range(3):
        arrow(ax, (xs[i] + ws[i] / 2, y3), (xs[i + 1] - ws[i + 1] / 2, y3),
              color=AMBER_DARK, lw=1.6)
    label(ax, 0.45, y3, "Conformità\ne mercato", fs=9, color=INK, style=None, bg=False)

    # Flussi tra livelli: le evidenze alimentano il fascicolo, il fascicolo
    # sostiene la conformità. Modifica sostanziale: la catena si riapre.
    for x in (2.55, 6.35, 10.35):
        arrow(ax, (x, y1 + 0.62), (x, y2 - 0.75), color=INK_MUT, lw=1.5)
    arrow(ax, (2.35, y2 + 0.75), (2.35, y3 - 0.55), color=INK_MUT, lw=1.5)
    label(ax, 3.6, 2.28, "alimenta", fs=8)
    label(ax, 3.5, 5.28, "sostiene", fs=8)
    save(fig, "05_document_architecture.png")


if __name__ == "__main__":
    fig_operating_model()
    fig_lifecycle()
    fig_heatmap()
    fig_regulatory_frame()
    fig_document_architecture()
