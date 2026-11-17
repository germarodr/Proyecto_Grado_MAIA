"""Genera las Figs. 3 y 4 del informe final (estilo IEEE, doble columna).

Fig. 3: F1 por función de SciBERT base, SciBERT con fragmentos y la condición
principal (prompt específico con ejemplos) de cada modelo comercial.
Fig. 4: matrices de confusión normalizadas por fila de SciBERT base y de la
condición principal de cada modelo comercial.

Fuentes (sin inferencia ni llamadas a API):
- A5/Comparacion_SciBERT/resultados/: comparacion_por_categoria.csv,
  comparacion_metricas.csv, scibert_base_compatible.csv y desacuerdos_por_caso.csv.
  Las predicciones comerciales se reconstruyen así: en los casos de
  desacuerdos_por_caso.csv se toma la predicción comercial; en el resto coincide
  con la de SciBERT base.
- A4/Final/Métricas.md, tabla por clase: F1 de SciBERT con fragmentos (Top-3).

Uso (desde la raíz del repositorio):
    .venv/bin/python "Informes/Informe Final/Insumos/generar_figuras.py"
"""

import csv
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[2]
A5 = RAIZ / "A5" / "Comparacion_SciBERT" / "resultados"
METRICAS_A4 = RAIZ / "A4" / "Final" / "Métricas.md"
SALIDA = AQUI / "figuras"

CONDICION = "base-specific-few"
FUNCIONES = [
    "Background", "Gap", "Basis", "Comparison", "Application",
    "Improvement/Modification", "Evidence", "Identification of the Originator", "Further Reading",
]
CORTAS = ["Bg", "Gap", "Bas", "Comp", "App", "I/M", "Evid", "IO", "FR"]
INVALIDA = "__invalid__"
MODELOS = [
    ("SciBERT base", "#1f3b73"),
    ("SciBERT con fragmentos", "#6b8fd6"),
    ("GPT-6 Luna", "#b5502a"),
    ("Gemini 3.5 Flash-Lite", "#3f8f5a"),
]
ID_COMERCIAL = {"GPT-6 Luna": "gpt-6-luna", "Gemini 3.5 Flash-Lite": "gemini-3.5-flash-lite"}

PULGADAS_DOBLE = 7.16
DPI = 600
plt.rcParams.update({
    "font.family": "Times New Roman",
    "font.size": 8,
    "axes.linewidth": 0.6,
    "xtick.major.width": 0.6,
    "ytick.major.width": 0.6,
})


def leer_csv(nombre):
    with open(A5 / nombre, encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def f1_top3():
    filas = {}
    for linea in METRICAS_A4.read_text(encoding="utf-8").splitlines():
        celdas = [c.strip() for c in linea.strip().strip("|").split("|")]
        if len(celdas) == 8 and celdas[0] in FUNCIONES:
            filas[celdas[0]] = float(celdas[7].replace(",", "."))
    faltan = set(FUNCIONES) - set(filas)
    if faltan:
        raise ValueError(f"Métricas.md no trae el F1 Top-3 de: {sorted(faltan)}")
    return filas


def f1_por_funcion():
    f1 = {nombre: {} for nombre, _ in MODELOS}
    for r in leer_csv("comparacion_por_categoria.csv"):
        if r["model"] == "SciBERT base":
            f1["SciBERT base"][r["label"]] = float(r["f1"])
        for nombre, ident in ID_COMERCIAL.items():
            if r["model"] == ident and r["condition"] == CONDICION:
                f1[nombre][r["label"]] = float(r["f1"])
    f1["SciBERT con fragmentos"] = f1_top3()
    return f1


def predicciones():
    sb = {r["inst_key"]: r for r in leer_csv("scibert_base_compatible.csv")}
    desacuerdos = defaultdict(dict)
    for r in leer_csv("desacuerdos_por_caso.csv"):
        if r["condition"] == CONDICION:
            if r["reference"] != sb[r["inst_key"]]["reference"]:
                raise ValueError(f"Referencia distinta en {r['inst_key']}")
            desacuerdos[r["model"]][r["inst_key"]] = r["commercial_prediction"]
    claves = list(sb)
    y = [sb[k]["reference"] for k in claves]
    p = {"SciBERT base": [sb[k]["predicted_label"] for k in claves]}
    for nombre, ident in ID_COMERCIAL.items():
        p[nombre] = [desacuerdos[ident].get(k, sb[k]["predicted_label"]) for k in claves]
    return y, p


def macro_oficial():
    m = {}
    for r in leer_csv("comparacion_metricas.csv"):
        if r["model"] == "SciBERT base":
            m["SciBERT base"] = float(r["f1_macro"])
        for nombre, ident in ID_COMERCIAL.items():
            if r["model"] == ident and r["condition"] == CONDICION:
                m[nombre] = float(r["f1_macro"])
    return m


def verificar(f1, y, p, macro):
    for nombre, pred in p.items():
        por_clase = []
        for c in FUNCIONES:
            tp = sum(a == c and b == c for a, b in zip(y, pred))
            fp = sum(a != c and b == c for a, b in zip(y, pred))
            fn = sum(a == c and b != c for a, b in zip(y, pred))
            por_clase.append(2 * tp / (2 * tp + fp + fn) if tp else 0.0)
        if abs(np.mean(por_clase) - macro[nombre]) > 1e-9:
            raise ValueError(f"F1 macro reconstruido de {nombre} no coincide con el oficial")
        if any(abs(a - f1[nombre][c]) > 1e-9 for a, c in zip(por_clase, FUNCIONES)):
            raise ValueError(f"F1 por función reconstruido de {nombre} no coincide con el oficial")


def figura_3(f1):
    fig, ax = plt.subplots(figsize=(PULGADAS_DOBLE, 2.4))
    x = np.arange(len(FUNCIONES))
    ancho = 0.2
    for i, (nombre, color) in enumerate(MODELOS):
        valores = [f1[nombre][c] for c in FUNCIONES]
        ax.bar(x + (i - 1.5) * ancho, valores, ancho, color=color, label=nombre, zorder=2)
        ax.axhline(np.mean(valores), color=color, lw=0.8, ls="--", zorder=1)
    ax.set_xticks(x, ["Background", "Gap", "Basis", "Comparison", "Application",
                      "Improvement/\nModification", "Evidence", "Identification\nof the Originator",
                      "Further\nReading"])
    ax.set_ylabel("F1")
    ax.set_ylim(0.4, 1.0)
    ax.grid(axis="y", lw=0.3, color="#cccccc", zorder=0)
    ax.spines[["top", "right"]].set_visible(False)
    handles, labels = ax.get_legend_handles_labels()
    handles.append(Line2D([], [], color="#555555", lw=0.8, ls="--"))
    labels.append("F1 macro")
    ax.legend(handles, labels, ncol=5, frameon=False, loc="upper center", bbox_to_anchor=(0.5, 1.13))
    fig.tight_layout()
    ruta = SALIDA / "GR_Fig3_f1_por_funcion.png"
    fig.savefig(ruta, dpi=DPI)
    fig.savefig(ruta.with_suffix(".pdf"))
    plt.close(fig)
    return ruta


def figura_4(y, p):
    nombres = ["SciBERT base", "GPT-6 Luna", "Gemini 3.5 Flash-Lite"]
    fig, axes = plt.subplots(1, 3, figsize=(PULGADAS_DOBLE, 3.0))
    for ax, nombre in zip(axes, nombres):
        # Las respuestas inválidas cuentan como error, pero no tienen columna: así
        # las tres matrices tienen la misma forma (se indica en el pie de figura).
        m = np.zeros((len(FUNCIONES), len(FUNCIONES)))
        for a, b in zip(y, p[nombre]):
            if b != INVALIDA:
                m[FUNCIONES.index(a), FUNCIONES.index(b)] += 1
        pct = 100 * m / np.array([y.count(c) for c in FUNCIONES])[:, None]
        ax.imshow(pct, cmap="Blues", vmin=0, vmax=100)
        for i in range(pct.shape[0]):
            for j in range(pct.shape[1]):
                if round(pct[i, j]) >= 1:
                    ax.text(j, i, f"{pct[i, j]:.0f}", ha="center", va="center", fontsize=6,
                            color="white" if pct[i, j] > 55 else "black")
        ax.set_xticks(range(len(FUNCIONES)), CORTAS, rotation=90)
        ax.set_yticks(range(len(FUNCIONES)), CORTAS if ax is axes[0] else [])
        ax.set_title(nombre, fontsize=8)
        ax.tick_params(length=0)
    axes[0].set_ylabel("Etiqueta humana")
    fig.supxlabel("Predicción (% de cada fila)", fontsize=8, y=0.075)
    fig.text(0.5, 0.012, "Bg: Background · Bas: Basis · Comp: Comparison · App: Application · "
             "I/M: Improvement/Modification · Evid: Evidence · IO: Identification of the Originator · "
             "FR: Further Reading", ha="center", fontsize=6.5)
    fig.tight_layout(w_pad=0.6, rect=(0, 0.06, 1, 1))
    ruta = SALIDA / "GR_Fig4_matrices_confusion.png"
    fig.savefig(ruta, dpi=DPI)
    fig.savefig(ruta.with_suffix(".pdf"))
    plt.close(fig)
    return ruta


def main():
    SALIDA.mkdir(exist_ok=True)
    f1 = f1_por_funcion()
    y, p = predicciones()
    verificar(f1, y, p, macro_oficial())
    print(figura_3(f1).name)
    print(figura_4(y, p).name)


if __name__ == "__main__":
    main()
