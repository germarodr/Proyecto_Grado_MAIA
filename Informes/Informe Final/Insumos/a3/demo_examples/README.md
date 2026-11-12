# Ejemplos del demostrador CiteScope (Grupo 15)

`examples_TB_con_resumen.jsonl` contiene las 40 citas del conjunto de prueba T_B que usa el demostrador. Se publican con acuerdo del equipo (11-nov-2026).

- **Origen:** `src/demo/a8_examples.py`, repositorio compartido de los grupos 14 y 15 (`Proyecto_LCR_CF`). Son instancias evaluadas de T_B con etiqueta humana, en las que el artículo citante y el citado tienen licencia abierta. Conteos y entradas en `manifest_examples_TB.json`.
- **Agregado por el G15:** `cited_abstract`, el resumen del artículo citado, tomado de `cs_subset_core_paper_metadata.jsonl` (la misma tabla con la que A2 armó los lotes).
- **Campos:** `context` (párrafo citante; `[[TARGET]]` marca la cita clasificada y `[CITE]`, `[FORMULA]`, `[FIGURE]`, `[TABLE]` los demás marcadores), títulos, enlaces de arXiv y licencias del citante y del citado, `cited_abstract`, `a2_top3` (claves de los 3 fragmentos recuperados) y `label` (etiqueta humana).
- **Por función:** Improvement/Modification 10, Evidence 6, Further Reading 6, Basis 5, Gap 5, Background 4, Comparison 3, Application 1, Identification of the Originator 0.

## Licencia y atribución

Los textos (`context`, `cited_abstract`) provienen de artículos de arXiv con licencia Creative Commons Attribution: los 40 citantes con CC BY 4.0; de los citados, 39 con CC BY 4.0 y 1 con CC BY 3.0. Cada fila trae el título, la licencia (`citing_license`, `cited_license`) y el enlace de arXiv (`citing_url`, `cited_url`) de ambos artículos. Cualquier uso o visualización debe mostrar esa atribución. Los textos se reproducen sin modificaciones, salvo el reemplazo de las marcas de cita y de los elementos no textuales por los marcadores indicados. El texto procede de unarXive 2022 (Saier, Krause y Färber, 2023).
