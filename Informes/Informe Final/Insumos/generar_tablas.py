"""Genera una imagen PNG por cada tabla del informe final, con estilo IEEE.

Lee las tablas Markdown de Informe_Final_v*.md (bloques que empiezan con
"**TABLA N.**") y escribe Insumos/tablas/TABLA_N.png. La leyenda no va en la
imagen: se escribe en Word sobre la tabla.

Uso (desde la raíz del repositorio):
    .venv/bin/python "Informes/Informe Final/Insumos/generar_tablas.py"
    .venv/bin/python "Informes/Informe Final/Insumos/generar_tablas.py" --solo I III
"""

import argparse
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.font_manager import FontProperties  # noqa: E402
from matplotlib.textpath import TextToPath  # noqa: E402

AQUI = Path(__file__).resolve().parent
INFORME = sorted(AQUI.parent.glob("Informe_Final_v*.md"))[-1]
SALIDA = AQUI / "tablas"

PT_POR_PULGADA = 72
# Plantilla IEEE: columna de 3,5 in y página de 7,16 in entre márgenes.
ANCHO = {"1": 3.5 * PT_POR_PULGADA, "2": 7.16 * PT_POR_PULGADA}
# Por defecto, una tabla va en una columna si cabe partiendo cada celda en a lo
# sumo MAX_LINEAS líneas; si no, va en doble columna. Estos conjuntos fuerzan
# la elección.
DOBLE_COLUMNA = {"V"}
UNA_COLUMNA = set()
MAX_LINEAS = 3

TAM = 8
INTERLINEA = TAM * 1.15
PAD_X, PAD_Y = 4.0, 2.2
DPI = 600
FUENTE = "Times New Roman"
HUECO = "#fff2a8"

_t2p = TextToPath()
_props = {
    (b, i): FontProperties(
        family=FUENTE, size=TAM, weight="bold" if b else "normal", style="italic" if i else "normal"
    )
    for b in (False, True)
    for i in (False, True)
}


def ancho_texto(s, negrita=False, cursiva=False):
    if not s:
        return 0.0
    w, _, _ = _t2p.get_text_width_height_descent(s, _props[(negrita, cursiva)], ismath=False)
    return w


def limpiar(celda):
    """Devuelve (texto, negrita, cursiva) quitando el marcado Markdown."""
    t = celda.strip().replace("`", "")
    negrita = bool(re.fullmatch(r"\*\*.*\*\*", t))
    t = t.replace("**", "")
    cursiva = bool(re.fullmatch(r"\*[^*]+\*", t))
    t = t.replace("*", "")
    return t, negrita, cursiva


def leer_tablas(ruta):
    lineas = ruta.read_text(encoding="utf-8").splitlines()
    tablas, i = {}, 0
    while i < len(lineas):
        m = re.search(r"\*\*TABLA ([IVXL]+)\.\*\*", lineas[i])
        if not m:
            i += 1
            continue
        num, j = m.group(1), i + 1
        while j < len(lineas) and not lineas[j].startswith("|") and "**TABLA" not in lineas[j] and not lineas[j].startswith("#"):
            j += 1
        filas, alinear = [], None
        while j < len(lineas) and lineas[j].startswith("|"):
            celdas = lineas[j].strip().strip("|").split("|")
            if all(re.fullmatch(r"\s*:?-+:?\s*", c) for c in celdas):
                alinear = ["right" if c.strip().endswith(":") else "left" for c in celdas]
            else:
                filas.append([limpiar(c) for c in celdas])
            j += 1
        if filas:
            tablas[num] = (filas, alinear or ["left"] * len(filas[0]))
        i = j
    return tablas


def partir(texto, ancho, negrita, cursiva):
    palabras, lineas, actual = texto.split(), [], ""
    for p in palabras:
        prueba = f"{actual} {p}".strip()
        if actual and ancho_texto(prueba, negrita, cursiva) > ancho:
            lineas.append(actual)
            actual = p
        else:
            actual = prueba
    return lineas + [actual] if actual or not lineas else lineas


def naturales(filas):
    n = len(filas[0])
    return [max(ancho_texto(t, b or r == 0, c) for r, (t, b, c) in enumerate(f[k] for f in filas)) for k in range(n)]


def anchos_columna(filas, ancho_total):
    n = len(filas[0])
    minimo = [max(max((ancho_texto(w, b or r == 0, c) for w in t.split()), default=0)
                  for r, (t, b, c) in enumerate(f[k] for f in filas)) for k in range(n)]
    natural = naturales(filas)
    util = ancho_total - 2 * PAD_X * n
    if sum(natural) <= util:
        return natural
    holgura = [nat - mn for nat, mn in zip(natural, minimo)]
    resto = max(util - sum(minimo), 0)
    return [mn + resto * h / (sum(holgura) or 1) for mn, h in zip(minimo, holgura)]


def cabe(filas, ancho_total):
    n = len(filas[0])
    minimo = sum(max(max((ancho_texto(w, b or r == 0, c) for w in t.split()), default=0)
                     for r, (t, b, c) in enumerate(f[k] for f in filas)) for k in range(n))
    if minimo + 2 * PAD_X * n > ancho_total:
        return False
    cols = anchos_columna(filas, ancho_total)
    return all(len(partir(t, w, b or r == 0, c)) <= MAX_LINEAS
               for r, f in enumerate(filas) for (t, b, c), w in zip(f, cols))


def dibujar(num, filas, alinear, ruta):
    if num in DOBLE_COLUMNA:
        columnas = "2"
    elif num in UNA_COLUMNA:
        columnas = "1"
    else:
        columnas = "1" if cabe(filas, ANCHO["1"]) else "2"
    cols = anchos_columna(filas, ANCHO[columnas])
    ancho_total = sum(cols) + 2 * PAD_X * len(cols)
    partidas = [[partir(t, w, b or r == 0, c) for (t, b, c), w in zip(f, cols)] for r, f in enumerate(filas)]
    altos = [max(len(l) for l in f) * INTERLINEA + 2 * PAD_Y for f in partidas]
    alto_total = sum(altos) + 2

    fig = plt.figure(figsize=(ancho_total / PT_POR_PULGADA, alto_total / PT_POR_PULGADA))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, ancho_total)
    ax.set_ylim(alto_total, 0)
    ax.axis("off")

    y = 1.0
    for r, (fila, lineas_fila) in enumerate(zip(filas, partidas)):
        x = 0.0
        for k, ((texto, negrita, cursiva), lineas) in enumerate(zip(fila, lineas_fila)):
            w = cols[k] + 2 * PAD_X
            if "[[" in texto:
                ax.add_patch(plt.Rectangle((x, y), w, altos[r], color=HUECO, lw=0, zorder=0))
            ha = alinear[k]
            tx = x + PAD_X if ha == "left" else x + w - PAD_X
            for n_linea, linea in enumerate(lineas):
                ax.text(
                    tx, y + PAD_Y + n_linea * INTERLINEA, linea, ha=ha, va="top",
                    fontproperties=_props[(negrita or r == 0, cursiva)], parse_math=False,
                )
            x += w
        y += altos[r]
        if r == 0:
            ax.plot([0, ancho_total], [y, y], color="black", lw=0.5)
    ax.plot([0, ancho_total], [1.0, 1.0], color="black", lw=0.8)
    ax.plot([0, ancho_total], [y, y], color="black", lw=0.8)

    fig.savefig(ruta, dpi=DPI)
    plt.close(fig)
    return columnas, ancho_total / PT_POR_PULGADA * 2.54


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--solo", nargs="*", help="Números romanos de las tablas a generar (por defecto, todas).")
    args = ap.parse_args()

    SALIDA.mkdir(exist_ok=True)
    tablas = leer_tablas(INFORME)
    for num, (filas, alinear) in tablas.items():
        if args.solo and num not in args.solo:
            continue
        ruta = SALIDA / f"TABLA_{num}.png"
        columnas, cm = dibujar(num, filas, alinear, ruta)
        huecos = sum("[[" in t for f in filas for t, _, _ in f)
        tipo = "una columna" if columnas == "1" else "doble columna"
        print(f"TABLA {num}: {ruta.name}  {tipo}, {cm:.1f} cm" + (f"  ({huecos} celdas con huecos)" if huecos else ""))
    if "X" not in tablas:
        print("TABLA X: sin filas en el informe todavía (se generará cuando existan).")


if __name__ == "__main__":
    main()
