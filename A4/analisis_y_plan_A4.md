# A4 — Análisis de datos y plan de entrenamiento de SciBERT

Fecha de revisión: **29 de octubre de 2026**. Equipo: **Grupo 15**, prueba **T_B**.

El siguiente paso es ajustar **SciBERT** para asignar una sola de nueve funciones a cada
cita. La propuesta, el informe y el plan usan SciBERT; interpreto «SeBERT» del pedido
como una referencia a ese mismo modelo. El notebook generado es
[A4_SciBERT_G15_Colab_A100.ipynb](A4_SciBERT_G15_Colab_A100.ipynb).

## 1. Contexto revisado y estado real

Se revisaron los documentos de la raíz y `Folder_trabajo_Equipos_14_y_15/`.
**No se utilizó la carpeta `entrega1/`**, aunque algunas referencias del informe
apuntan al historial de esa carpeta en GitHub.

| Fuente | Qué establece para A4 |
|---|---|
| [Propuesta](../PropuestaProyectoGrado.md) | Clasificación de nueve funciones, SciBERT con CE y dos entradas; evaluar el aporte del Top-3 |
| [Primer informe](../Primer%20Informe%20Avance.md) | Corte al 23-oct: A1/A2 completadas, A3 parcial; aún sin fine-tuning ni resultados finales |
| Plan de trabajo (archivado, sin enlace) | G15 autónomo desde A4, T_B como test, liberación temprana del modelo base para la aplicación |
| [Contrato del 28-oct](../Folder_trabajo_Equipos_14_y_15/Contrato_Datos_A3_2026-10-28_guia_rev3.1.md) | A4 puede empezar con training v1; reglas V0/V1/V2 y gold posterior por clave |
| [Guía rev3.1](../Folder_trabajo_Equipos_14_y_15/guia_anotacion_funcion_cita_rev3.1.md) | Etiqueta principal única, marcadores y fronteras entre clases |
| Presentación «A3 Round 1 (W1+W2) Results, Adjudication and Training Set» | Ronda 1 anotada al 27-oct; adjudicación, procedencia del texto, conteos y decisiones de A4 |
| Presentaciones anteriores y hojas de calibración/acuerdo | Desarrollo de reglas y jueces; no constituyen el test de A4 |
| Archivos TrainingData de G14 y G15 | Claves, pre-etiquetas, reservas, exclusiones y manifiestos; el experimento usa los de G15 |

El estado más reciente proviene del contrato del 28-oct: **A1 y A2 terminadas; A3
continúa con adjudicación/ronda 2; A4 ya puede comenzar**. El informe del 23-oct es
un corte anterior. Sus cifras de suministro no deben confundirse con filas finales
de entrenamiento. Para cuotas, exclusiones y operación prevalece el contrato reciente.

Los cuatro papers locales aportan lo siguiente:

- **Lyu et al. (2021):** marco conceptual de motivaciones. La guía concreta las nueve
  categorías y excluye Assessment; el paper no entrega nuestro dataset de entrenamiento.
- **Cohan et al. (2019), SciCite:** antecedente de clasificación de intención y señales
  estructurales. Sus tres clases no reemplazan las nueve del proyecto.
- **Beltagy et al. (2019), SciBERT:** encoder científico y fine-tuning con cabeza de
  clasificación; respalda el punto inicial de LR 2e-5 y pocas épocas, sujeto a validación.
- **Lauscher et al. (2022), MultiCite:** importancia de contextos de varias oraciones,
  múltiples intenciones y particiones por documento. Aquí se conserva la decisión de
  etiqueta principal única de la guía; no se cambia a clasificación multietiqueta.

## 2. Auditoría de los archivos locales

Se verificaron **los cinco hashes de archivos declarados en el manifiesto de G15**:
training v1, test IDs y listas V0/V1/V2. Coinciden. Las 31.265 claves de entrenamiento
son únicas y los identificadores concuerdan con la clave canónica. No hay pares en
los que el citante sea el mismo artículo citado. Estos archivos de identificación
carecen de texto; los lotes de A2 ya incorporados en `A4/a2/batches_norw/` contienen
las entradas completas.
Las cifras y hashes se conservan en [auditoria_datos_A4.json](auditoria_datos_A4.json).

Se reconstruyeron **34.775 instancias** desde los ocho lotes: las 31.265 filas V0 y
los 3.510 IDs de T_B. No faltan contextos, títulos, abstracts ni textos de fragmentos;
cada contexto tiene exactamente un `[[TARGET]]`. Los identificadores y grupos de los
lotes coinciden con los de las filas requeridas. Se verificó además la tokenización
de las 34.775 instancias en ambas configuraciones con el vocabulario real SciBERT:
ninguna excede 512 tokens tras aplicar la política y todas conservan la cita objetivo.
Los hashes y resultados están en [auditoria_textos_A4.json](auditoria_textos_A4.json).

Se encontraron secciones vacías: **541 filas de train/val** contienen algún fragmento
sin sección (917 fragmentos), y **52 paquetes de T_B** tienen esa condición (90
fragmentos). El notebook los conserva con sección `Unknown` y un indicador de ausencia;
no inventa una categoría retórica ni elimina filas de una sola configuración.

| Medida | Resultado |
|---|---:|
| Pool extendido, según manifiesto | 38.780 |
| Alta confianza, según manifiesto | 37.254 |
| Filas retiradas para construir training V0 de G15 | 5.989 |
| Training V0 disponible, antes de separar validación | **31.265** |
| Citantes distintos en training V0 | 21.516 |
| Citados distintos en training V0 | 10.693 |
| Filas de training asociadas al test del otro grupo, T_A | 3.510 |
| Paquetes propios T_B en test_set_ids | 3.510 |
| Activos / reserva / colchón de T_B | 2.970 / 270 / 270 |
| Archivos gold de A3 presentes en el repositorio | **0** |

Las 3.510 filas de T_A en training empiezan con pre-etiquetas y se pueden actualizar
con gold de T_A. No son 3.510 etiquetas humanas ya adjudicadas. Los 3.510 IDs de T_B
tampoco equivalen al test final: incluyen reservas y colchones. Cada pre-etiqueta
tiene 390 paquetes de T_B; la meta humana final es al menos 300 válidos por clase.

Distribución comprobada al aplicar las listas reales a training V0:

| Función | V0 | V1 | V2 |
|---|---:|---:|---:|
| Background | 12.214 | 7.246 | 6.731 |
| Gap | 2.807 | 1.735 | 1.599 |
| Basis | 2.606 | 1.186 | 1.108 |
| Comparison | 3.157 | 1.738 | 1.566 |
| Application | 4.243 | 1.389 | 1.266 |
| Improvement/Modification | 545 | 197 | 174 |
| Evidence | 3.027 | 1.756 | 1.645 |
| Identification of the Originator | 1.312 | 463 | 437 |
| Further Reading | 1.354 | 854 | 823 |
| **Total antes de train/val** | **31.265** | **16.564** | **15.349** |

Hay **22,4 veces** más Background que Improvement/Modification en V0. Empezaremos
con CE sin ponderación, como indica la propuesta, y selección por F1 macro. Se
reportará cada clase. Si la validación muestra que hace falta ponderar la pérdida,
será otro experimento documentado; no se balanceará eliminando datos sin justificación.

Hay dos detalles de procedencia que conviene aclarar con quien construyó las listas:

- El manifiesto informa `calibration_citing_papers=117`; V0 contiene 115 IDs con
  `source=calibration`.
- `test_set_ids_G15` tiene 3.222 citantes distintos, mientras V0 marca 3.224 IDs como
  `source=test_set`. Los dos adicionales son `1904.09569` y `2103.10428`.

Estas diferencias no justifican reincorporar artículos: **se aplican las listas
completas verificadas**. No se ha determinado si ambos detalles tienen una causa
común. El notebook no reconstruye exclusiones únicamente a partir de los IDs de test.

La meta 2.700 humana nació como 15% de un dataset de referencia de 18.000 ejemplos.
Con el suministro ampliado, esa cuota no demuestra por sí sola que el 15% del nuevo
dataset completo esté validado. El cierre de A3 debe documentar el denominador y las
cuotas reales según el contrato; A4 no presenta las pre-etiquetas como gold humano.

## 3. Archivos de Drive disponibles y pendientes

**Los ocho JSONL necesarios ya están disponibles en `A4/a2/batches_norw/` y fueron
verificados. No hace falta descargarlos de nuevo.** En Colab pueden seguir en
`MAIA_PROYECTO/a2/batches_norw/` de Drive, ajustando la ruta de acceso:

| Archivo | Filas requeridas por training V0 de G15 |
|---|---:|
| `pilot_random_1500.jsonl` | 1.232 |
| `pool_single_7000.jsonl` | 5.810 |
| `pool_cue_eg.jsonl` | 9.271 |
| `pool_cue_cmp.jsonl` | 4.038 |
| `pool_cue_rare.jsonl` | 2.371 |
| `pool_cue_yield.jsonl` | 676 |
| `pool_cue_basis.jsonl` | 4.493 |
| `pool_ext_cue_rare.jsonl` | 3.374 |
| **Total** | **31.265** |

Son las filas que necesitamos de cada archivo, **no el tamaño total de cada lote**.
T_B utiliza los mismos ocho nombres de lote. El texto se recupera por `source_batch`
y `inst_key`; no se une por orden de fila.

Carpetas de origen localizadas: [MAIA_PROYECTO](https://drive.google.com/drive/folders/11RYKPpKDissDfgVTvdXWLJekbZabRK1U)
y [batches_norw](https://drive.google.com/drive/folders/1QeuZs-l3h38suN4jEVUr-SkWXg7vDrKR).
Los archivos de texto se mantienen fuera de Git mediante `A4/.gitignore`.

También serán útiles:

| Artefacto | Momento y finalidad |
|---|---|
| `a2/pool_v11.1_ext/prelabels_pool.jsonl` | Recomendado para auditoría de votos, licencias y localizadores; opcional para entrenar si los lotes incluyen los textos completos |
| `gold_round1.jsonl`, `gold_round2.jsonl` o `test_set_gold.jsonl` consolidado | Cuando estén adjudicados; actualizar T_A y evaluar T_B. Evitar versiones conflictivas |
| `iaa_report.md` | Cierre de A3 y reporte metodológico; no es entrada de entrenamiento |
| Notebook/script original de A2 que construye batches | No es necesario para estos lotes: ya incluyen `inst_key`, `context` renderizado y `top3` |

**De los archivos de `inputs/` de la segunda imagen no necesitas descargar ninguno
para este camino de A4.** Los lotes contienen precisamente el contexto, título,
abstract y Top-3 que ya usaron los jueces. Los JSONL de contextos, chunks y el corpus
de 58 GB solo serían necesarios para reconstruir textos faltantes o rehacer A1.
Ni `a1`, `a1_ext` ni las variantes `norw` requieren nueva ejecución para este notebook.

## 4. Qué haremos en el entrenamiento

1. Verificar versiones, GPU, manifiesto, hashes y claves.
2. Medir el impacto de V0/V1/V2 y aplicar la variante seleccionada antes de separar datos.
3. Incorporar gold disponible de T_A por clave. Eliminar `unclear` conocido de train/val.
4. Separar train y validación por artículo citante, con hash y semilla congelados.
5. Reconstruir ambos tipos de entrada sobre exactamente las mismas filas.
6. Ajustar SciBERT base y exportarlo como v0 para la aplicación.
7. Ajustar otro SciBERT desde el checkpoint original, ahora con secciones y Top-3.
8. Elegir el mejor checkpoint de cada configuración por F1 macro en validación.
9. Cuando cierre A3, evaluar ambos sobre el mismo T_B humano y calcular diferencia de
   F1 macro, métricas por clase, matrices y un intervalo bootstrap pareado por citante.

**Punto inicial recomendado: V0**, permitido por el contrato y favorable al suministro
de minoritarias. Es una propuesta configurable, no una decisión histórica del equipo.
V0 no implica separación completa de los citados. En los 2.970 paquetes activos de T_B,
2.463 citan artículos vistos como citados en training V0 y 507 no: **82,93% / 17,07%**.
La prueba final deberá recalcular y reportar el desglose sobre el gold realmente usado.

Con el hash propuesto `G15-A4-split-v1` y 10% objetivo, sin gold adicional, se comprobó:

| Variante | Antes de split | Train final | Validación | Train retirado para separar documentos de val |
|---|---:|---:|---:|---:|
| V0 | 31.265 | 28.039 | 3.226 | 0 |
| V1 | 16.564 | 12.119 | 1.662 | 2.783 |
| V2 | 15.349 | 11.015 | 1.539 | 2.795 |

Las nueve clases están representadas en ambas particiones. El hash ofrece separación
estable por documento, pero no fuerza proporciones exactas por clase ni sección. El
notebook publica conteos y distribución de secciones, y falla si falta alguna clase.
El corte temporal contemplado en la propuesta no se aplica en esta ejecución: no
modificaremos el T_B ya congelado para simular una prueba temporal.

## 5. Formato de entrada y límite de longitud

Las dos entradas comparten el contexto citante con la cita objetivo marcada. Se usa
el formato BERT `[CLS] contexto [SEP] información_del_citado [SEP]`, con tipos de
segmento 0 y 1. Nunca se introduce la etiqueta, los votos o IDs como entrada textual.

No caben tres fragmentos de hasta 300 palabras, más contexto, en 512 tokens. La
política inicial conserva hasta **192 tokens de contexto centrados en `[[TARGET]]`**
en ambas configuraciones. El presupuesto restante —al menos 317 tokens con una
ventana llena— se asigna al citado:

- Base: título hasta 64 tokens y abstract con el resto.
- Fragmentos: reparto entre los tres, con encabezado de sección hasta 24 tokens;
  se redistribuye el presupuesto que no use un fragmento corto.

Se recorta texto del citado desde el final de cada segmento. Se registra longitud
original y conservada por instancia, incluido cuánto se recortó cada fragmento. Esta
política puede perder información relevante y es una limitación que deberá reportarse.
La A100 permite batches mayores, pero no amplía las posiciones de SciBERT.

La auditoría real confirma que este límite afecta materialmente la entrada:

| Configuración y partición V0 | Tokens totales promedio | Contextos recortados | Evidencia del citado recortada |
|---|---:|---:|---:|
| Base, train | 386,5 | 35,38% | 5,14% |
| Base, val | 386,9 | 35,71% | 5,77% |
| Fragmentos, train | 504,0 | 35,38% | 90,98% |
| Fragmentos, val | 504,0 | 35,71% | 90,92% |

Estas son medidas de longitud, no métricas de calidad. La política conserva partes
de los tres fragmentos; no puede presentar como entrada los Top-3 completos en todos
los casos. Se deberá tener en cuenta al interpretar el aporte del retrieval.

## 6. Configuración inicial para Colab Pro A100

| Parámetro | Valor propuesto |
|---|---|
| Modelo | `allenai/scibert_scivocab_uncased`, revisión exacta registrada al ejecutar |
| Objetivo | Entropía cruzada multiclase, 9 salidas, todos los parámetros ajustables |
| Semilla | 42 para ambas configuraciones |
| Longitud | 512 tokens incluidos los especiales |
| LR / épocas | 2e-5 / hasta 4 |
| Batch efectivo | 32: microbatch 16 × acumulación 2 |
| Precisión | BF16 en A100 |
| Optimización | AdamW, decay 0,01, warmup 10%, descenso lineal |
| Selección | Mayor F1 macro de validación, parada temprana paciencia 2 |
| Checkpoints | Cada época en Drive; retención limitada y opción de reanudar |
| Resultados | Pesos, tokenizador, inferencia, contratos, métricas, auditorías y claves de partición |

El notebook tiene **32 celdas: 16 descripciones alternadas con 16 celdas de código**.
Incluye seguimiento MLflow, snapshots en Drive y recuperación de checkpoints;
los pasos para ejecutarlo están en [PRIMERA_CORRIDA.md](PRIMERA_CORRIDA.md).
Es autónomo: no necesita `crear_notebook.py` para correr en Colab. Ese script permite
regenerarlo en el repositorio. Inicialmente `RUN_TEST=False` y `GOLD_FINAL=False`.

## 7. Cómo usarlo y qué queda por confirmar

Abrir el `.ipynb` en Colab y elegir A100. **Rutas actualizadas el 1 de noviembre de
2026:** `DATA_ROOT` apunta al acceso directo `Mi unidad/MAIA_PROYECTO` y `RESULTS_ROOT`
a tu carpeta `Mi unidad/MAIA_TESIS`. Los lotes se leen del primero; los resultados
quedan en `MAIA_TESIS/a4/<RUN_ID>/`. Los respaldos del historial se guardarán en
`MAIA_TESIS/a4/_tracking/snapshots/` según la guía de instalación.

Los JSONL de identificación ya están en el repositorio. Copia la carpeta
`TrainingData_Grupo15/` a `MAIA_TESIS/TrainingData_Grupo15/`, la ubicación de
`IDS_DIR` del notebook. Configura `GOLD_FILES` cuando estén disponibles los archivos
adjudicados. No hace falta copiar los textos de A2 a la carpeta de resultados.

El adaptador se verificó con los ocho archivos reales. Su esquema es:

```text
inst_key, group_key, citing_paper_id, cited_paper_id,
context, cited_title, cited_abstract,
top3: [{chunk_key, text, section}, {chunk_key, text, section}, {chunk_key, text, section}]
```

La celda de inspección muestra claves y tipos; `BATCH_FIELDS` y `CHUNK_FIELDS` permiten
ajustar nombres o rutas anidadas. Si la clave o los textos no están completos, el
notebook se detiene y explica el faltante. La reconstrucción y la política de tokens
ya se comprobaron con todos los datos requeridos; **no se ha entrenado SciBERT en
A100 desde este entorno**.

La validación local cubre formato del notebook, hashes, las tres variantes de aislamiento,
train/val con datos reales, unión de gold y rechazo de errores de texto. Además se
comprueba tokenización, un paso de gradiente y exportación/recarga con un BERT pequeño
aleatorio: esa prueba es de funcionamiento, no un resultado de SciBERT.
Pasaron las seis pruebas de `verificar_notebook.py`. El entorno local usa PyTorch
2.11.0 CPU y Transformers 5.5.4; la instalación fijada de Transformers 4.57.1 y la
ejecución GPU de Colab están pendientes de comprobar allí.

El cierre de A3 requiere el gold adjudicado de T_B, sus cuotas finales y el informe
IAA. La propuesta también contempla P@3 manual, que no se sustituye por cosenos ni
por F1 del clasificador. Para afirmar una mejora consistente de Top-3, además de la
ejecución inicial conviene repetir las dos configuraciones con varias semillas y el
mismo split, sin ajustar decisiones mirando T_B.

Referencias técnicas consultadas: [SciBERT](https://aclanthology.org/D19-1371/),
[checkpoint publicado](https://huggingface.co/allenai/scibert_scivocab_uncased),
[Trainer 4.57.1](https://huggingface.co/docs/transformers/v4.57.1/en/main_classes/trainer),
[MultiCite](https://aclanthology.org/2022.naacl-main.137/).
