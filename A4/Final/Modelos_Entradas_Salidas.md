# A4 · Modelos, entradas y salidas

**Revisado: 11 de noviembre de 2026.** Las variantes del clasificador parten de
`allenai/scibert_scivocab_uncased` y se ajustan por separado para nueve clases.
La diferencia principal es la información del artículo citado que reciben.

La primera corrida comparó **base y Top-3**. El notebook actual ya ejecutó la
comparación **Top-1 y Top-3**, reutilizando los Top-3 guardados. Por tanto, los dos
modelos de la comparación actual reciben el contexto de la cita y fragmentos;
la entrada con título y resumen corresponde a la variante base de la primera corrida.

## 1. Qué recibe y devuelve cada variante

| Modelo y estado | Entradas y descripción | ¿Texto o vectores? | Salida por cita | Justificación y documento que lo define |
|---|---|---|---|---|
| **SciBERT base** · entrenado | `context`: contexto de la cita en el artículo **citante**, con `[[TARGET]]`.<br>`title` y `abstract`: título y resumen del artículo **citado**. Son tres campos que se combinan en una sola secuencia. | Recibe **texto plano**. El tokenizador lo convierte a IDs y máscaras; los embeddings se calculan dentro de SciBERT. | Una clase entre nueve, sus nueve probabilidades, el puntaje elegido y los conteos del texto procesado. | La **guía de la universidad, A4, pp. 7–8** [U], y la **propuesta, objetivo 4 y §4.2/F4** [P], definen esta entrada para clasificar con la descripción general del citado. Implementación: [I1], §§2–5. |
| **SciBERT Top-3** · entrenado y reutilizado como referencia | El mismo `context`, más `chunks`: **tres fragmentos del citado**, cada uno con `text` y `section`. La sección indica su origen, por ejemplo Introduction o Methods. Esta variante usa esos fragmentos y secciones como información del citado. | Recibe **los textos y los nombres de sección**. Los embeddings usados antes para recuperar los fragmentos no se entregan como entrada al clasificador A4. | El mismo contrato de salida que base. | Segunda configuración de la **guía A4** [U] y la **propuesta, §§4.1 y 4.2/F4** [P], para medir el aporte de los fragmentos. El **contrato, §5** [C], describe su procedencia. Implementación: [I1], §§2–5. |
| **SciBERT Top-1** · entrenado en la segunda iteración | El mismo `context` y **el primer fragmento del orden publicado en A2**, con su sección. El notebook conserva los otros dos para medir lo omitido, pero codifica solo el primero. | Recibe **texto plano**. La interfaz acepta un fragmento o la lista de tres y selecciona el primero. | El mismo contrato; los conteos añaden fragmentos y tokens omitidos. | **Prueba adicional de A4** para estudiar el recorte observado; las dos configuraciones principales de la propuesta siguen siendo base y Top-3. Definición experimental: [I2], §§2–4, y `encode_top1` [T]. |

**Correspondencia con los archivos:** el adaptador convierte `cited_title` en
`title`, `cited_abstract` en `abstract` y `top3` en `chunks`; `context` conserva su
nombre. Esto está definido en `BATCH_FIELDS`, `CHUNK_FIELDS` y `normalize_batch`
([I1], §2). El contrato [C], §§3 y 5, define el par citante–citado y el marcador objetivo.

Training v2 aporta identificadores y etiquetas; el notebook une esos registros
con los textos de A2. Los IDs sirven para unir datos y verificar las particiones.
El entrenamiento y la validación añaden la etiqueta de referencia en `labels`,
codificada de 0 a 8. Para pedir una predicción se envían los textos.

## 2. Cómo se transforma el texto para entrar a la red

La interfaz recibe texto; el tokenizador prepara tres tensores numéricos:

- `input_ids`: IDs enteros de los tokens, no embeddings densos precalculados.
- `attention_mask`: distingue texto de relleno.
- `token_type_ids`: distingue el contexto de la información del citado.

```text
[CLS] contexto de la cita [SEP] información del artículo citado [SEP]
```

El máximo es **512 tokens totales**, incluidos los separadores. El notebook
reserva hasta **192 para el contexto**, conservando un único `[[TARGET]]`.
En base, el título ocupa hasta 64 tokens y el resumen usa el espacio restante.
En Top-3, ese espacio se reparte entre tres fragmentos y sus encabezados; en
Top-1 se destina al fragmento elegido. SciBERT obtiene las representaciones
internamente: el entrenamiento ajusta los pesos y `predict` usa los pesos guardados.

La concatenación y el separador se especifican en la guía [U] y la propuesta
[P], §4.2/F4. El presupuesto de 192 y el reparto del espacio son decisiones de
implementación: `encode_example` ([I1], §3) y `encode_top1` [T]. El contrato [C],
§4, filtra contextos de hasta 512 tokens al construir el pool; el límite de 192
corresponde a la entrada conjunta que construimos en A4.

La recuperación previa usa embeddings y similitud coseno para elegir los
fragmentos ([P], §4.1). A4 vuelve a codificar **sus textos** para clasificarlos.

## 3. Respuesta exacta de la interfaz exportada

La red produce nueve puntuaciones (`logits`). La clase Python exportada,
`CitationClassifier.predict(example)`, aplica softmax y devuelve:

| Campo | Qué contiene |
|---|---|
| `label` | La función de cita con mayor probabilidad: **una sola etiqueta**. |
| `score` | Probabilidad softmax de la clase elegida. |
| `scores` | Las nueve clases y sus probabilidades; suman aproximadamente 1. |
| `score_calibrated` | `false`: los puntajes se entregan sin calibración. |
| `token_audit` | Conteos de texto original, conservado y recortado; Top-1 añade lo omitido al seleccionar un fragmento. |

Las clases son **Background, Gap, Basis, Comparison, Application,
Improvement/Modification, Evidence, Identification of the Originator y Further Reading**.

Las nueve categorías se definen en [P], §2.1; la guía [U], A4, p. 8, exige sus
puntajes. Los campos de respuesta y softmax los define `CitationClassifier`
([I1], §5). F1, precisión, recall y matrices de confusión son reportes de evaluación
sobre un conjunto de citas; `predict` devuelve la clasificación de una cita concreta.

## 4. Parámetros de entrenamiento

Estos ajustes entrenan los pesos; son distintos de los textos que se envían al
pedir una predicción.

| Variante | Ritmo de aprendizaje | Regularización | Épocas y semillas | Fuente de los valores |
|---|---|---|---|---|
| Base seleccionada | `2e-5` | `0.1` | Máximo 8; mejor época del modelo principal: 3. Semilla principal 42, repeticiones 17 y 73. | Búsqueda terminada: [V], `selected_primary.base`. |
| Top-3 seleccionada | `3e-5` | `0.01` | Máximo 8; mejor época del modelo principal: 3. Semilla principal 42, repeticiones 17 y 73. | Búsqueda terminada: [V], `selected_primary.fragmentos`. |
| Top-1 de la segunda iteración | `3e-5` | `0.01` | Máximo 8; mejor época del modelo principal: 3. Semilla principal 42, repeticiones 17 y 73; parada tras dos épocas sin mejorar. | Se fijaron iguales a Top-3 para comparar la cantidad de fragmentos: [I2], §§4 y 6. |

Todos usan lotes de 16 y acumulación de dos pasos —lote efectivo de 32 en una
GPU—, entropía cruzada, entrenamiento BF16 y evaluación de exportación FP32.
La guía exige la cabeza de clasificación y la entropía cruzada; los valores
concretos de ritmo, regularización, lotes, semillas y parada los fijan nuestros notebooks.

## 5. Ejemplos reales de entradas y salidas

Estos dos casos pertenecen a **validación** y tienen etiqueta de referencia
**humana** (`label_source=human_gold`). Para cada uno se comparan los modelos
principales de semilla 42. Se eligió un caso donde acierta Top-1 y falla Top-3
y otro con el resultado contrario, para mostrar ambos comportamientos.

Los parámetros de la tabla son los **campos de texto**, no los ajustes de
entrenamiento de la sección 4. `predict` recibe un registro; `chunks[0]`,
`chunks[1]` y `chunks[2]` son objetos dentro de la misma lista. Los textos se
abrevian con `[…]` para facilitar la lectura. Las entradas completas, antes de
tokenizar, y los nueve puntajes por modelo están en
[Ejemplos_Reales_Entradas_Salidas.json](Ejemplos_Reales_Entradas_Salidas.json).

| Modelo (caso) | Parámetro 1: `context` | Parámetro 2 | Parámetro 3 | Parámetro 4 | Resultado real guardado | Referencia humana | Fuente |
|---|---|---|---|---|---|---|---|
| SciBERT base · E1 | «[…] could be a text cloud or cloudmap (see [[TARGET]]). [FIGURE][FIGURE]» | `title`<br>«Tag Clouds for Displaying Semantics: The Case of Filmscripts» | `abstract`<br>«We relate tag clouds to other forms of visualization, including planar or […]» | — | `label`: **Further Reading**<br>`score`: **0.886061**<br>Coincide con la referencia | Further Reading | [PB] |
| SciBERT Top-3 · E1 | «[…] could be a text cloud or cloudmap (see [[TARGET]]). [FIGURE][FIGURE]» | `chunks[0]`<br>Sección: «Television Transcripts»<br>Texto: «Figure REF shows the resulting tag clouds. Some remarks on […]» | `chunks[1]`<br>Sección: «Tracking of Characters»<br>Texto: «The Correspondence Analysis allows us to easily seek the principal […]» | `chunks[2]`<br>Sección: «Television Transcripts»<br>Texto: «Let us now turn our attention to tag clouds. To […]» | `label`: **Background**<br>`score`: **0.692682**<br>Difiere de la referencia | Further Reading | [PT3] |
| SciBERT Top-1 · E1 | «[…] could be a text cloud or cloudmap (see [[TARGET]]). [FIGURE][FIGURE]» | `chunks[0]`<br>Sección: «Television Transcripts»<br>Texto: «Figure REF shows the resulting tag clouds. Some remarks on […]» | — | — | `label`: **Further Reading**<br>`score`: **0.781868**<br>Coincide con la referencia | Further Reading | [PT1] |
| SciBERT base · E2 | «[…] Gaussian, distribution. Such a method is advocated in [[TARGET]].» | `title`<br>«DeLiGAN : Generative Adversarial Networks for Diverse and Limited Data» | `abstract`<br>«A class of recent approaches for generating images, called Generative Adversarial Networks […]» | — | `label`: **Evidence**<br>`score`: **0.799952**<br>Difiere de la referencia | Background | [PB] |
| SciBERT Top-3 · E2 | «[…] Gaussian, distribution. Such a method is advocated in [[TARGET]].» | `chunks[0]`<br>Sección: «Freehand Sketches»<br>Texto: «The TU-Berlin dataset [CITE], contains [FORMULA] hand-drawn sketches evenly distributed […]» | `chunks[1]`<br>Sección: «Learning {{formula:b1bddd8a-3893-4e94-bdd8-5cda8cb592e9}} and {{formula:4a84d3cf-1b3f-49c9-b44f-b7447ecb7928}}»<br>Texto: «For each Gaussian component, we first need to initialise its […]» | `chunks[2]`<br>Sección: «Discussion»<br>Texto: «In complicated multi-modal settings, the data may be disproportionally distributed […]» | `label`: **Background**<br>`score`: **0.837641**<br>Coincide con la referencia | Background | [PT3] |
| SciBERT Top-1 · E2 | «[…] Gaussian, distribution. Such a method is advocated in [[TARGET]].» | `chunks[0]`<br>Sección: «Freehand Sketches»<br>Texto: «The TU-Berlin dataset [CITE], contains [FORMULA] hand-drawn sketches evenly distributed […]» | — | — | `label`: **Evidence**<br>`score`: **0.902761**<br>Difiere de la referencia | Background | [PT1] |

**Cómo leer la salida:** la clase procede de `predicted_label` en el CSV y
`score` es su valor en la columna `p_<clase>`, redondeado a seis decimales solo
para esta tabla. Las nueve probabilidades originales se conservan en el JSON.
Son puntajes softmax sin calibración, como se explica en la sección 3.

**Identificadores para localizar los mismos registros:**

- **E1**: `inst_key=1507.01529|67|333-382|0905.3830`; batch `pool_ext_cue_rare.jsonl`, línea 183.
- **E2**: `inst_key=2009.13311|7|1953-2002|1706.02071`; batch `pool_cue_eg.jsonl`, línea 3275.

Las entradas se reconstruyeron con el mismo adaptador de A2 del notebook.
Las salidas se leyeron de `evaluation/predictions.csv` de cada modelo, en FP32;
el JSON registra el estudio, ensayo, ruta del archivo y el registro original
de predicción. Estos casos ilustran respuestas individuales; las métricas del
conjunto se consultan en los reportes de cada corrida.

[PB]: https://drive.google.com/file/d/1lVOt6Dgbpah6PwaiuQV6G1KpTY0MrvsB/view
[PT3]: https://drive.google.com/file/d/15512CRhtmWMymO3pOfH6IGaSQep1sW-o/view
[PT1]: https://drive.google.com/file/d/1bqwjqcdqb8EnXPsDLWWfOWnfHcklKarL/view

## Documentos consultados

[U]: <../../Papers/Propuesta_Proyecto PLN.pdf#page=7>
[P]: ../../Informes/PropuestaProyectoGrado.md
[C]: https://drive.google.com/file/d/1X7JXN5ZvoYJodhRxdT5Y-8wOaDlXwRXi/view
[I1]: Historico/Iteracion_01_2026-11-11/SciBERT_Entrenamiento_Final.ipynb
[I2]: Historico/Iteracion_02_2026-11-11/SciBERT_Entrenamiento_Final.ipynb
[T]: ../top1_runtime.py
[V]: Historico/Iteracion_01_2026-11-11/Verificacion_Ejecucion.json

- **[U]** Guía de la universidad, actividad A4, páginas 7–8.
- **[P]** Propuesta propia, objetivos y metodología del clasificador supervisado.
- **[C]** Contrato consultado en Drive, secciones 3–5; define los datos y su procedencia.
- **[I1] y [V]** Código ejecutado y parámetros seleccionados de la primera corrida.
- **[I2] y [T]** Código de la comparación ejecutada Top-1 frente a Top-3.
