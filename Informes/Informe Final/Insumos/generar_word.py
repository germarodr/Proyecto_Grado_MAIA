"""Vuelca Informe_Final_v*.md en la plantilla IEEE de Word.

Parte de la plantilla (respaldo en Others/), conserva el marco del título, la nota
al pie sin numerar de los autores (si el Markdown la trae), los estilos y la numeración automática de
secciones y referencias, y reemplaza todo el contenido. Las tablas se insertan
como las imágenes de Insumos/tablas/ y las figuras desde sus rutas del Markdown.
Las tablas y figuras de más de una columna van en una sección de una columna.
Los huecos [[...]] se resaltan en amarillo. La sección temporal de supuestos no
se incluye.

Uso (desde la raíz del repositorio):
    .venv/bin/python "Informes/Informe Final/Insumos/generar_word.py"
"""

import copy
import re
from pathlib import Path

import docx
from docx.enum.text import WD_COLOR_INDEX, WD_TAB_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt

AQUI = Path(__file__).resolve().parent
BASE = AQUI.parent
INFORME = sorted(BASE.glob("Informe_Final_v*.md"))[-1]
PLANTILLA = BASE / "Others" / "Informe Final IEEE_respaldo_2026-11-17.docx"
SALIDA = BASE / "Informe Final IEEE.docx"
TABLAS = AQUI / "tablas"
ECUACIONES = AQUI / "figuras"

ANCHO_COLUMNA = 3.5  # pulgadas
ANCHO_PAGINA = 7.16
ESPACIO_FIGURA = Pt(10)  # aire antes de la figura y después de su pie
ESPACIO_TABLA_ANCHA = Pt(10)  # aire antes de toda tabla y después de las tablas a doble columna
INLINE = re.compile(r"(\[\[.+?\]\]|\*\*.+?\*\*|`[^`]+`|\$[^$]+\$|\*[^*\s][^*]*?\*)")


def estilo(doc, style_id):
    return next(s for s in doc.styles if s.style_id == style_id)


def runs_matematicos(par, texto):
    for parte in re.split(r"(_\{[^}]+\}|_[A-Za-z0-9])", texto):
        if not parte:
            continue
        if parte.startswith("_"):
            r = par.add_run(parte[1:].strip("{}"))
            r.font.subscript = True
        else:
            r = par.add_run(parte)
        r.italic = True


def agregar_texto(par, texto, negrita=False, italica=False):
    for trozo in INLINE.split(texto):
        if not trozo:
            continue
        if trozo.startswith("[["):
            r = par.add_run(trozo)
            r.font.highlight_color = WD_COLOR_INDEX.YELLOW
        elif trozo.startswith("**"):
            agregar_texto(par, trozo[2:-2], negrita=True, italica=italica)
        elif trozo.startswith("`"):
            r = par.add_run(trozo[1:-1])
            r.font.name = "Courier New"
            r.font.size = Pt(9)
            r.bold = negrita or None
        elif trozo.startswith("$"):
            runs_matematicos(par, trozo[1:-1])
        elif trozo.startswith("*"):
            agregar_texto(par, trozo[1:-1], negrita=negrita, italica=True)
        else:
            r = par.add_run(trozo.replace("\\*", "*"))
            if negrita:
                r.bold = True
            if italica:
                r.italic = True


def sect_continuo(doc, columnas):
    """Párrafo con salto de sección continuo; cierra una sección de `columnas` columnas."""
    base = doc.element.body.find(qn("w:sectPr"))
    p = doc.add_paragraph()
    sp = OxmlElement("w:sectPr")
    tipo = OxmlElement("w:type")
    tipo.set(qn("w:val"), "continuous")
    sp.append(tipo)
    for tag in ("w:pgSz", "w:pgMar"):
        sp.append(copy.deepcopy(base.find(qn(tag))))
    cols = OxmlElement("w:cols")
    cols.set(qn("w:num"), str(columnas))
    cols.set(qn("w:space"), "288")
    sp.append(cols)
    p._p.get_or_add_pPr().append(sp)


def imagen(doc, ruta, ancho_max):
    from PIL import Image

    im = Image.open(ruta)
    dpi = (im.info.get("dpi") or (600, 600))[0] or 600
    ancho = min(im.size[0] / dpi, ancho_max)
    p = doc.add_paragraph()
    p.alignment = 1
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(2)
    p.add_run().add_picture(str(ruta), width=Inches(ancho))
    return im.size[0] / dpi > 4.5


def es_ancha(ruta):
    from PIL import Image

    im = Image.open(ruta)
    dpi = (im.info.get("dpi") or (600, 600))[0] or 600
    return im.size[0] / dpi > 4.5


def bloque(doc, ancha, poner):
    if ancha:
        sect_continuo(doc, 2)
    poner(ANCHO_PAGINA if ancha else ANCHO_COLUMNA)
    if ancha:
        sect_continuo(doc, 1)


def ecuacion(doc, latex, numero):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    ECUACIONES.mkdir(exist_ok=True)
    ruta = ECUACIONES / f"ecuacion_{numero}.png"
    expr = latex.replace(r"\qquad", "").strip()
    expr = re.sub(r"\(\d+\)\s*$", "", expr).strip()
    expr = expr.replace(r"F1_{macro}", r"F1_{\mathrm{macro}}")
    fig = plt.figure(figsize=(0.01, 0.01))
    fig.text(0, 0, f"${expr}$", fontsize=10, family="serif")
    plt.rcParams["mathtext.fontset"] = "stix"
    fig.savefig(ruta, dpi=600, bbox_inches="tight", pad_inches=0.02, transparent=True)
    plt.close(fig)
    p = doc.add_paragraph(style=estilo(doc, "Equation"))
    # Fórmula centrada en la columna y número alineado a la derecha.
    p.paragraph_format.alignment = 0
    ancho_col = (ANCHO_PAGINA - 0.2) / 2  # columna real: página menos 0,2 in de separación
    p.paragraph_format.tab_stops.add_tab_stop(Inches(3.5), WD_TAB_ALIGNMENT.CLEAR)
    p.paragraph_format.tab_stops.add_tab_stop(Inches(ancho_col / 2), WD_TAB_ALIGNMENT.CENTER)
    p.paragraph_format.tab_stops.add_tab_stop(Inches(ancho_col), WD_TAB_ALIGNMENT.RIGHT)
    p.add_run("\t")
    p.add_run().add_picture(str(ruta), height=Inches(0.42))
    p.add_run(f"\t({numero})")


def numeracion_vinetas(plantilla):
    """pPr con numPr de la lista de contribuciones de la plantilla."""
    for p in plantilla.element.body.iter(qn("w:p")):
        if p.find(".//" + qn("w:numPr")) is not None and p.find(".//" + qn("w:pStyle")) is not None:
            if p.find(".//" + qn("w:pStyle")).get(qn("w:val")) == "TextCarCar":
                return copy.deepcopy(p.find(".//" + qn("w:numPr")))
    return None


def poner_texto_parrafo(p_xml, texto):
    ts = list(p_xml.iter(qn("w:t")))
    ts[0].text = texto
    ts[0].set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    for t in ts[1:]:
        t.text = ""


def actualizar_nota(doc, nota):
    """Reemplaza el texto de la nota al pie de autores (la de "Documento recibido")."""
    from lxml import etree

    for parte in doc.part.package.parts:
        if not str(parte.partname).endswith("footnotes.xml"):
            continue
        xml = parte._element if hasattr(parte, "_element") else etree.fromstring(parte.blob)
        for p in xml.iter(qn("w:p")):
            ts = [t for t in p.iter(qn("w:t")) if t.text]
            if any("Documento recibido" in t.text for t in ts):
                ts[0].text = nota
                for t in ts[1:]:
                    t.text = ""
        if not hasattr(parte, "_element"):
            parte._blob = etree.tostring(xml, xml_declaration=True, encoding="UTF-8", standalone=True)


def sin_numeracion_automatica(p):
    """El número del título va como texto: la numeración heredada (legacy) de la plantilla
    se reinicia en Word tras los saltos de sección de las figuras y tablas a doble columna."""
    numPr = p._p.get_or_add_pPr().get_or_add_numPr()
    numPr.get_or_add_numId().val = 0


def quitar_marca_clasificacion(doc):
    """Quita la marca "Cisco Confidential" que Office añadió a los pies de página de la plantilla."""
    from lxml import etree

    for parte in doc.part.package.parts:
        nombre = str(parte.partname)
        if nombre.startswith("/word/footer"):
            xml = parte._element if hasattr(parte, "_element") else etree.fromstring(parte.blob)
            for r in list(xml.iter(qn("w:r"))):
                if r.getparent() is not None and "Cisco Confidential" in etree.tostring(r, encoding="unicode") \
                        and r.find(".//" + qn("w:txbxContent")) is not None:
                    r.getparent().remove(r)
            if not hasattr(parte, "_element"):
                parte._blob = etree.tostring(xml, xml_declaration=True, encoding="UTF-8", standalone=True)
        elif nombre == "/docProps/custom.xml":
            xml = etree.fromstring(parte.blob)
            for prop in list(xml):
                if prop.get("name", "").startswith("ClassificationContentMarking"):
                    xml.remove(prop)
            parte._blob = etree.tostring(xml, xml_declaration=True, encoding="UTF-8", standalone=True)


def main():
    doc = docx.Document(str(PLANTILLA))
    quitar_marca_clasificacion(doc)
    for nombre in ("Heading 1", "Heading 2", "Reference Head"):
        doc.styles[nombre].font.bold = True
    vineta = numeracion_vinetas(doc)
    md = INFORME.read_text(encoding="utf-8")
    md = re.sub(r"<!--.*?-->", "", md, flags=re.S)
    md = md.split("## [TEMPORAL")[0]
    lineas = md.splitlines()

    titulo = next(l[2:].strip() for l in lineas if l.startswith("# "))
    autores = next(l.strip("* ") for l in lineas if l.startswith("**") and "Bejarano" in l)
    nota = next((l[2:].strip() for l in lineas if l.startswith("> Documento recibido")), None)

    cuerpo = list(doc.element.body.iterchildren())
    poner_texto_parrafo(cuerpo[1], titulo)
    poner_texto_parrafo(cuerpo[2], autores)
    for el in cuerpo[3:]:
        if el.tag != qn("w:sectPr"):
            doc.element.body.remove(el)
    if nota:
        actualizar_nota(doc, nota)
    else:
        # Sin nota de autores en el Markdown: se quita la llamada a la nota al pie de la plantilla.
        for ref in list(cuerpo[0].iter(qn("w:footnoteReference"))):
            run = ref.getparent()
            run.getparent().remove(run)
    sp_final = doc.element.body.find(qn("w:sectPr"))
    tipo = OxmlElement("w:type")
    tipo.set(qn("w:val"), "continuous")
    sp_final.find(qn("w:pgSz")).addprevious(tipo)
    # Sin encabezado de la plantilla (título corto y número de página).
    for ref in sp_final.findall(qn("w:headerReference")):
        sp_final.remove(ref)

    sin_numero = {"Apéndices", "Declaración de uso de IA", "Referencias"}
    i = next(k for k, l in enumerate(lineas) if l.startswith("**Resumen—**"))
    pendiente_tabla = None
    en_referencias = False
    while i < len(lineas):
        l = lineas[i].rstrip()
        i += 1
        if not l or l == "---":
            continue
        if l.startswith("**Resumen—**") or l.startswith("**Índice de Términos—**"):
            etiqueta, resto = l[2:].split("**", 1)
            p = doc.add_paragraph(style=estilo(doc, "Abstract"))
            r = p.add_run(etiqueta)
            r.italic = True
            agregar_texto(p, resto.lstrip())
            continue
        if l.startswith("## "):
            nombre = l[3:].strip()
            if nombre in sin_numero:
                p = doc.add_paragraph(style=estilo(doc, "ReferenceHead"))
                p.add_run(nombre)
                en_referencias = nombre == "Referencias"
                if nombre == "Apéndices":
                    p.paragraph_format.page_break_before = True
            else:
                p = doc.add_paragraph(style=estilo(doc, "Heading1"))
                sin_numeracion_automatica(p)
                p.add_run(nombre)
            continue
        if l.startswith("### "):
            p = doc.add_paragraph(style=estilo(doc, "Heading2"))
            sin_numeracion_automatica(p)
            p.add_run(l[4:].strip())
            continue
        if l.startswith("$$"):
            m = re.search(r"\((\d+)\)\s*\$\$$", l)
            ecuacion(doc, l.strip("$"), m.group(1) if m else "1")
            continue
        m = re.match(r"\*\*TABLA ([IVXL]+)\.\*\*\s*(.*)", l)
        if m:
            pendiente_tabla = (m.group(1), m.group(2))
            continue
        if l.startswith("|"):
            if pendiente_tabla:
                num, tit = pendiente_tabla
                ruta = TABLAS / f"TABLA_{num}.png"

                def poner(ancho, num=num, tit=tit, ruta=ruta):
                    p = doc.add_paragraph(style=estilo(doc, "TableTitle"))
                    p.add_run(f"TABLA {num}")
                    p.paragraph_format.space_before = ESPACIO_TABLA_ANCHA
                    p.paragraph_format.keep_with_next = True
                    p = doc.add_paragraph(style=estilo(doc, "TableTitle"))
                    agregar_texto(p, tit.rstrip("."))
                    p.paragraph_format.keep_with_next = True
                    imagen(doc, ruta, ancho)
                    if ancho == ANCHO_PAGINA:
                        doc.paragraphs[-1].paragraph_format.space_after = ESPACIO_TABLA_ANCHA

                bloque(doc, es_ancha(ruta), poner)
                pendiente_tabla = None
            continue
        m = re.match(r"!\[(Fig\. \d+)\]\(([^)]+)\)", l)
        if m:
            ruta = BASE / m.group(2)
            j = i
            while j < len(lineas) and not lineas[j].strip():
                j += 1
            pie = lineas[j] if j < len(lineas) and lineas[j].startswith("**Fig.") else None
            if pie:
                i = j + 1

            def poner(ancho, ruta=ruta, pie=pie):
                imagen(doc, ruta, ancho)
                doc.paragraphs[-1].paragraph_format.space_before = ESPACIO_FIGURA
                if pie:
                    mm = re.match(r"\*\*(Fig\. \d+\.)\*\*\s*(.*)", pie)
                    p = doc.add_paragraph(style=estilo(doc, "FigureCaption"))
                    p.add_run(mm.group(1) + " ")
                    agregar_texto(p, mm.group(2))
                doc.paragraphs[-1].paragraph_format.space_after = ESPACIO_FIGURA

            bloque(doc, es_ancha(ruta), poner)
            continue
        if l.startswith("**Fig."):
            mm = re.match(r"\*\*(Fig\. \d+\.)\*\*\s*(.*)", l)
            p = doc.add_paragraph(style=estilo(doc, "FigureCaption"))
            p.add_run(mm.group(1) + " ")
            agregar_texto(p, mm.group(2))
            continue
        if en_referencias and re.match(r"\[\d+\]\s", l):
            p = doc.add_paragraph(style=estilo(doc, "References"))
            agregar_texto(p, re.sub(r"^\[\d+\]\s+", "", l))
            continue
        if l.startswith("- "):
            p = doc.add_paragraph(style=estilo(doc, "TextCarCar"))
            if vineta is not None:
                p._p.get_or_add_pPr().append(copy.deepcopy(vineta))
            else:
                p.add_run("•\t")
            agregar_texto(p, l[2:])
            continue
        p = doc.add_paragraph(style=estilo(doc, "TextCarCar"))
        agregar_texto(p, l)

    doc.save(str(SALIDA))
    print(f"{SALIDA.name}: {len(doc.paragraphs)} párrafos, {len(doc.inline_shapes)} imágenes")


if __name__ == "__main__":
    main()
