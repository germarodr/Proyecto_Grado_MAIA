# Notas del informe final: memoria, reglas y pendientes

Este archivo acompaña a [Informe_Final_v0.1.md](./Informe_Final_v0.1.md), que es la versión de lectura del artículo.

- **[Informe_Final_v0.1.md](./Informe_Final_v0.1.md)** contiene solo lo que va al artículo: prosa, tablas y figuras. Los huecos se marcan `[[dato · responsable]]`.
- **Este archivo** contiene todo lo demás: reglas del curso, aprendizajes, nomenclatura, fuentes verificadas, razones de cada decisión, pendientes y responsables. Las notas por sección (§7) y la columna "Sección" usan la numeración IEEE del artículo (I, III-B…); los § en arábigos se refieren a secciones de este archivo o de documentos externos.
- Cuando surja una recomendación o un aprendizaje nuevo, se registra aquí, en la §5 (Bitácora). Al artículo solo pasa el texto resultante.

**Entrega:** lunes 23-nov, 11:55 p. m.

## 1. Reglas del curso y formato

**Modelo de formato: `Formato-IEEE.doc`** (IEEE Transactions, dos columnas), armado en **Word**. `Formato_Artículo.pdf`, `Plantilla_Articulo.docx` y el `.zip` de LaTeX de la misma plantilla están en `Others/` y ya no se usan como referencia. Del curso siguen vigentes `CriteriosEvaluacionInformeFinal.rtf` (rúbrica y máximo de 12 páginas) y `RecomendacionesInformeFinal.rtf` (contenido). Los parámetros de la plantilla se extrajeron de la configuración interna del `.doc` (sección y estilos); verificado el 09-nov.

| Parámetro | Valor (plantilla IEEE salvo indicación) |
|---|---|
| Página | Carta, dos columnas (separación 0,5 cm), interlineado sencillo, justificado |
| Márgenes | 1,65 cm laterales; 1,78 cm superior e inferior |
| Extensión | Máximo **12 páginas** (rúbrica del curso) |
| Tamaños de letra | Times New Roman: título 24 pt; autores 11; cuerpo 10; resumen e índice de términos 9 en negrita; pies de figura, títulos de tabla, referencias y notas al pie 8 |
| Autores | Nombres bajo el título. En una **nota al pie sin numerar** de la primera columna de la página 1, que reemplaza el texto de ejemplo de la plantilla: fecha de recepción (23-nov-2026), apoyo de la Universidad de los Andes y del grupo FLAG–TICSw y asesoría de J. C. Sanguino, afiliación (MaIA, Departamento de Ingeniería de Sistemas y Computación, Universidad de los Andes, Bogotá, Colombia) y cada nombre con su correo. Sin autor de correspondencia ni código postal |
| Resumen | Encabezado "Resumen—"; **200–300 palabras** (Recomendaciones del curso); sin citas; definir los símbolos que aparezcan |
| Índice de Términos | Encabezado "Índice de Términos—"; ~4 términos (el curso pide 3–5) **en orden alfabético** |
| Secciones | Números romanos (I, II…), versalitas, centradas |
| Subsecciones | Letras (A, B…), cursiva; referencia cruzada como "Sección III-B" |
| Figuras | "Fig. 1.", pie debajo, también al inicio de frase. Se mantiene la fuente o "elaboración propia" por buena práctica |
| Tablas | "TABLA I" (romanos), título arriba; sin líneas verticales; notas de tabla con letras |
| Ecuaciones | Numeradas a la derecha; en el texto "(1)", salvo al inicio de frase: "La Ecuación (1)…" |
| Citas y referencias | Entre corchetes [1]; rangos [1]–[3]; lista **en orden de aparición** (la plantilla también menciona orden alfabético; se sigue el orden de aparición, propio del estilo numérico IEEE) |
| Apéndices | Antes de las referencias |
| Reconocimiento | **No se incluye la sección**; los agradecimientos (FLAG–TICSw, J. C. Sanguino) van en la frase de apoyo de la nota al pie |
| Siglas | Definir al primer uso; evitarlas en el título |
| Biografías con foto | Opcionales en la plantilla; **no se incluyen** |
| Color | Solo si es necesario |

- **Rúbrica del informe final** (`CriteriosEvaluacionInformeFinal.rtf`):

  | Criterio | Puntos |
  |---|---:|
  | Problema | 10 |
  | Estado del arte | 10 |
  | **Metodología** | **30** |
  | Resultados | 15 |
  | Discusión | 15 |
  | Conclusiones | 10 |
  | Estructura y redacción | 10 |

- **Recomendaciones del curso** (`RecomendacionesInformeFinal.rtf`):
  - resumen de 200–300 palabras con 3–5 palabras clave;
  - la Metodología sigue el ciclo de ML e incluye figura de arquitectura, herramientas y despliegue;
  - el estado del arte cierra con un análisis propio;
  - siglas explicadas al primer uso.

## 2. Flujo de edición

- **Solo GR edita el artículo.** Cada integrante deja sus insumos en `Insumos/`, con sus iniciales como prefijo (p. ej. `ST_hiperparametros.csv`, `CB_arquitectura_aws.png`). Quien no use git se los envía a GR.
- **Formato de los insumos:**
  - Las cifras para tablas llegan en CSV, Excel o texto, nunca solo como imagen.
  - Los diagramas llegan como archivo fuente o PNG en buena resolución.
- Si un insumo no llega en su fecha, el hueco se queda y GR avisa al grupo.
- **Revisión:** las sugerencias se hacen como comentarios sobre el PDF en dos ventanas: **borrador v1 (19-nov)** y **versión final (22-nov)**. GR decide qué integrar.

## 3. Lecciones del primer informe (81/100)

Fuente: [Feedback Primer Informe.txt](../Feedback%20Primer%20Informe.txt). El primer informe perdió 15 de 35 puntos en "construcción de los modelos", que equivale a la Metodología, la sección que más pesa aquí (30 puntos).

| # | Observación del evaluador | Acción | Sección | Estado en el artículo |
|---|---|---|---|---|
| L1 | Sintetizar el aporte diferenciador y sus beneficios | Contribuciones con "qué es nuevo" y "para quién sirve"; una frase en el resumen | Resumen, I | Redactado |
| L2 | ¿Qué es el "promedio con máscara de atención"? | *Mean pooling* explicado con la ecuación (1); truncamiento a 512 | III-B | Redactado; falta % truncado |
| L3 | Desbalance y concentración en cs.CV sin justificar | Origen (volumen de arXiv), ampliación, distribución por subcampo, limitación | III-A, V | Redactado; faltan razón de subcampos y distribución |
| L4 | ¿Por qué 60 en eval60 y cómo se eligieron? | Composición, propósito y límite de tamaño | III-C | Redactado |
| L5 | No se describe el *fine-tuning* | Arquitectura, entradas, 512 tokens, hiperparámetros, selección; nombrar el LLM | III-D, III-E | Redactado con valores planeados; faltan confirmación de ST, desbalance y LLM |
| L6 | Faltó la evaluación humana de P@3 | Ejecutarla; si no, limitación explícita | III-B, IV-A, V | Protocolo redactado; **sin responsable** |
| L7 | Consolidar indicadores de recuperación, pre-etiquetado y validación | TABLA VI | IV-A | Redactado |
| L8 | Experimentos como hipótesis → resultado | TABLA V (H1–H7); la Sección IV responde cada H | III-F, IV | Redactado |
| L9 | Términos usados sin definir | Ningún identificador interno (ver §4.2 de este archivo) | Todo | Pasada final pendiente |
| L10 | No se distingue decisión de resultado | Metodología = decisiones; Resultados = cifras; Discusión = interpretación | Todo | Aplicado en la estructura |

## 4. Reglas de redacción

### 4.1 Hilo conductor (L10)

- Cada decisión de la Metodología se escribe como *decisión + por qué + alternativa descartada*.
- Las cifras de desempeño van solo en la Sección IV. La Metodología puede adelantar solo tamaños de datos.
- Las cifras sobre la muestra de 60 se rotulan siempre como "desarrollo".
- Cada sección abre con una frase que dice qué contiene.

### 4.2 Nomenclatura (L9): identificador interno → nombre en el artículo

| Identificador interno | En el artículo |
|---|---|
| A1–A7 / F1–F4 | No se usan; se nombran las etapas |
| eval60 | "Muestra de desarrollo de 60 instancias" |
| calib30, calib2 | "Primera y segunda calibración" |
| `norw` | "Exclusión de secciones de trabajos relacionados" |
| pool_v11.1, conjunto ampliado | "Conjunto pre-etiquetado" (38.780) |
| pool_cue_yield | No se menciona; "885 casos difíciles" |
| prompt v8/v11/v11.1/v12 | "Versiones sucesivas del prompt"; v11.1 = "versión final" |
| jueces | "Modelos de lenguaje de pesos abiertos usados como jueces" (definido en III-C) |
| T_A / T_B | Solo T_B, definido en III-C como "el conjunto propio" |
| V0 / V1 / V2 | No se nombran; se describe la exclusión usada (III-D) |
| paquete, ola, lote, colchón, reserva | "Instancia"; la logística no se menciona |
| `unclear` | "Instancias sin función identificable" |
| MASI | Solo si se reporta, con referencia |

## 5. Bitácora de decisiones y aprendizajes

Agregar una fila cada vez que se tome una decisión sobre el artículo.

| Fecha | Decisión / aprendizaje | Origen |
|---|---|---|
| 09-nov | Esqueleto del artículo con huecos y tabla de responsables | Borrador v0 |
| 09-nov | Incorporar lecciones L1–L10 del primer informe | Feedback primer informe |
| 09-nov | Separar en `Informe_Final.md` (lectura) y este archivo (memoria) | GR |
| 09-nov | **v0.1**: la versión va en el nombre de ambos archivos (`Informe_Final_vX.Y.md`, `Notas_Informe_Final_vX.Y.md`); se sube en los dos a la vez y se actualizan los enlaces cruzados | GR |
| 09-nov | Las TABLAS IV, V y VI nuevas (~0,75 pág.) salen de la holgura entre 10 y 12 páginas; si falta espacio, la TABLA IV pasa a texto y la TABLA I se reduce | Presupuesto de páginas |
| 09-nov | ~~Contradicciones IEEE vs. curso resueltas a favor del curso~~ (reemplazada por la fila siguiente) | Revisión de `Formato_Artículo.pdf` |
| 09-nov | `Formato_Artículo.pdf` y `Plantilla_Articulo.docx` pasan a `Others/` como opciones alternas: **la plantilla IEEE es el único modelo de formato** y se arma en Word. El artículo pasa a numeración IEEE (I, A; TABLA I; Fig. 1), los apéndices van antes de las referencias, la afiliación y los correos van en nota al pie, y el resumen vuelve a 200–300 palabras | GR |
| 09-nov | Revisión contra `RecomendacionesInformeFinal.rtf`: se aprueban y aplican D1–D6. D1: párrafo de descripción de la solución en la Introducción. D2: nueva IV-E con la comparación con trabajos previos (sale de la Discusión) y un análisis crítico de cierre. D3: la tabla de F1 por función se reemplaza por una gráfica de barras (Fig. 3); las figuras pasan a ser Fig. 1–5 y las tablas I–VIII (IX opcional en IV-E). D4: párrafo de fortalezas en la Discusión. D5: aplicaciones prácticas y lecciones aprendidas pasan a las Conclusiones. D6: referencias de datasets, modelos y frameworks. **D7 (pasada de siglas) no se aprobó.** Suma ~0,5 pág. | GR |
| 09-nov | **Título:** "Clasificación de la función de citas en Computer Science con SciBERT y recuperación semántica del artículo citado" (16 palabras). Se descartó agregar "de fragmentos", aunque "recuperación del artículo citado" puede leerse como recomendación de citas; el resumen y III-B aclaran que se recuperan fragmentos dentro del citado. La comparación con el modelo comercial no va en el título, sino en el resumen | GR |
| 09-nov | **Título actualizado:** "Clasificación de la función de citas en Computer Science con modelos de lenguaje y recuperación semántica del artículo citado". Se cambia "SciBERT" por "modelos de lenguaje" para no atar el título a que SciBERT gane la comparación (H7), cubrir también a los jueces y al modelo comercial, y evitar un nombre de modelo en el título | GR |
| 09-nov | **CiteScope se elimina** del artículo (Sección II, TABLA I, IV-E y referencias): era un microproyecto anterior del equipo, ajeno a este trabajo, citado por error en el primer informe. Las fuentes del proyecto son `Proyecto_LCR_CF`, `Folder_trabajo_Equipos_14_y_15` y este repositorio; la bibliografía disponible está en `Papers/` (SciBERT, SciCite, MultiCite y Lyu et al.) | GR |
| 09-nov | **Nota al pie de autores:** se revisó contra el texto de ejemplo de la plantilla. Se incluye fecha de recepción, apoyo genérico de la Universidad de los Andes (sin otras organizaciones) y afiliación con departamento, confirmado en https://sistemas.uniandes.edu.co/maia/ (la sigla oficial es **MaIA**). Cada correo va junto al nombre de su autor para que no sea ambiguo. No se marca autor de correspondencia ni se incluye código postal | GR |
| 09-nov | **FLAG y experto** (fuente: definición del proyecto, `Local_Citation_Recommendation.pdf`): el grupo FLAG–TICSw se añade a la frase de apoyo de la nota al pie. ~~J. C. Sanguino va en una sección Reconocimiento~~ → GR prefiere no tener sección de Reconocimiento: la asesoría de J. C. Sanguino se menciona en la misma frase de apoyo de la nota al pie | GR |
| 09-nov | Referencias de la propuesta revisadas: se completan Gu y Lyu, se agrega scikit-learn [21] y se excluyen las referencias sobre redacción de objetivos y OpenAlex | GR |
| 09-nov | **Verificación completa de referencias** (protocolo y resultados en §9). Se elimina del artículo la nota "Orden provisional…"; la renumeración por orden de aparición queda como pendiente en §8 | GR |
| 09-nov | **Sin huecos en referencias:** se validan y agregan Koloveas et al. [7], Gilardi et al. [8] y SciRepEval/SPECTER2 [19]. Se eliminan las del modelo comercial y del modelo de la app (no hay evidencia en los repositorios). Lista renumerada [1]–[20] | GR |
| 09-nov | §8 se reorganiza por fase (A1–A5 y despliegue) con la evidencia que existe hoy, para asignar responsables. Estado verificado: A3 cerrado en código (resultados en Drive, no locales); A4 con solo la configuración base entrenada (F1 de validación 0,846 frente a las pre-etiquetas); A5 y despliegue sin evidencia en los repositorios | GR |
| 09-nov | Se crea `Solicitudes_Insumos_v0.1.md`: una solicitud independiente por insumo (contexto, qué se necesita, dónde buscar, formato, criterio de aceptación y qué hacer si no es posible), para enviarla a cada compañero. Sigue la convención de versión en el nombre | GR |
| 09-nov | GR simplifica `Solicitudes_Insumos_v0.1.md`: quedan contexto y qué se necesita por solicitud, sin indicar dónde buscar. Sin encabezado de reglas, tabla resumen, formatos ni fechas. El despliegue se pide por otro medio | GR |
| 09-nov | Las solicitudes piden solo **qué** se necesita, sin sugerir dónde buscarlo: se quitan rutas de Drive, notebooks, scripts, commits y variables de código | GR |
| 09-nov | Se agregan A6 (evaluación comparativa) y A7 (eficiencia) a las solicitudes: GR consolida, los datos vienen de A4 y A5. Se adopta el **formato común de predicciones** del plan de trabajo (A6-2) y A5-3 se alinea a él. El costo y la latencia de SciBERT pasan de A4 a A7 (A4-5 → A7-2; los ejemplos de error pasan de A4-6 a A4-5) | GR |
| 09-nov | **Sin solicitudes opcionales:** se elimina A6-3 (citados vistos/no vistos: solo aplica a SciBERT y ya viene en A4-2) y A7-4 (costo de construir los datos: no responde ninguna hipótesis). También el P@3 por función (≈20 instancias por función serían ruido) y las unidades de Colab. Pasan a obligatorios el F1 por función que respalda A4-4 y un ejemplo donde el modelo comercial difiera de SciBERT (A5-4) | GR |
| 09-nov | Revisión completa de `Solicitudes_Insumos_v0.1.md` con los criterios acordados (simplicidad, sin dónde buscar, sin opcionales, entregable claro, sin comentarios sobrantes, T_B definido): T_B se define al inicio; se quitan jerga (V0, `unclear`, paquete), referencias a hipótesis y comentarios sobrantes; A1-4 separa protocolo y entregable; se agregan las dependencias de A1-2, A1-4 y A5-4 en A3-1 o A5-3; A6-2 deja de ser solicitud y el formato común pasa al contexto de A6 | GR |
| 09-nov | **Contraste artículo–solicitudes:** cada hueco de datos del artículo tiene solicitud. Se llenan las citas [1], [2], [3] y [19] y las 38.780 instancias pre-etiquetadas del resumen; los huecos llevan el código de su solicitud en lugar del responsable; se quitan los condicionales del P@3 (A1-4 es obligatoria). Para que la TABLA VIII compare en dólares (H7), A7-1 pide el precio por hora de la GPU. Pendiente fuera del artículo: el plan de trabajo aún trata el P@3 como "si sobra tiempo" | GR |

## 6. Presupuesto de páginas

| Sección | Puntos | Páginas | Responsable |
|---|---:|---:|---|
| Título, autores, resumen | (estructura) | 0,5 | GR |
| I. Introducción | 10 | 1 | GR |
| II. Estado del arte | 10 | 1 | GR |
| III. Metodología | **30** | 3,5 | GR + ST + JA + CB |
| IV. Resultados | 15 | 2 | GR |
| V. Discusión | 15 | 1 | GR |
| VI. Conclusiones | 10 | 0,5 | GR |
| Referencias | (estructura) | 0,5 | GR |
| **Total** | 100 | **~10** (máx. 12) | |

Las páginas se miden con los márgenes de la plantilla IEEE. La meta de ~10 páginas deja holgura frente al máximo de 12.

## 7. Notas por sección del artículo

### Resumen
- Debe tener **200–300 palabras** (`RecomendacionesInformeFinal.rtf`). El texto actual tiene ~270 con huecos; vigilar el límite al llenarlos.
- Sin citas en el resumen; definir los símbolos que aparezcan (p. ej. κ).
- L1: la última frase ya contiene el aporte diferenciador y el beneficio para el usuario.

### I. Introducción
- **Fuente:** Propuesta §1.1–1.3 y §2 ([PropuestaProyectoGrado.md](../PropuestaProyectoGrado.md)).
- Los objetivos específicos están escritos según la propuesta; ajustarlos al alcance real (p. ej. si no se hace P@3).
- Falta una referencia que sustente la motivación del conteo de citas.
- **Fuente adicional para la justificación:** [Local_Citation_Recommendation.pdf](./Local_Citation_Recommendation.pdf), documento de proyecto del grupo FLAG–TICSW con el experto J. C. Sanguino. Plantea las dos tareas (recuperación y clasificación), la motivación (crecimiento de la literatura, revisión automática, análisis bibliométrico, verificación de afirmaciones) y metas que conviene contrastar con el alcance real: ≥2.000 ejemplos por etiqueta, 15 % validado por humanos y modelos comerciales tipo GPT-4o/5 o Gemini.
- D1: el párrafo de descripción de la solución ya está redactado.

### II. Estado del arte
- **Fuente:** Propuesta §3; papers en `Papers/` y los cuatro citados en [analisis_y_plan_A4.md](../../A4/analisis_y_plan_A4.md) §1.
- **CiteScope no se usa.** El primer informe y la propuesta lo citaban como antecedente (F1 macro 0,68), pero es un microproyecto anterior del equipo, ajeno a este trabajo y no publicado. Fue un error del primer informe.
- **Modelos de lenguaje (2023–2025):** resuelto con Koloveas et al. (2025) [7] y Gilardi et al. (2023) [8], verificadas en §9.
- **Texto base:** la sección 3 de la [propuesta](../PropuestaProyectoGrado.md) ya redacta SciCite, MultiCite, SciBERT, Gu et al. y unarXive, con la brecha "Gu et al. recuperan *qué* citar; este trabajo recupera *por qué* se cita". Sirve para la Sección II y la TABLA I.
- **Referencias de la propuesta revisadas (09-nov):** Beltagy, Cohan, Gu, Lauscher, Lyu y Saier pasan al artículo. Se completan las páginas de Gu (pp. 274–288) y el DOI de Lyu. El volumen LNCS 13185 que trae la propuesta **no se pudo confirmar** y se omitió. Se excluyen Bjerke & Renger y el Centro de Español (sirvieron para redactar objetivos) y OpenAlex (no se usó como fuente; solo se contaron sus identificadores dentro de unarXive). Se agrega scikit-learn (usado en A4). Opcional: citar a los autores originales del κ de Cohen y del α de Krippendorff, implementados en `a3_metrics.py` sin librería.

### III-A. Datos y corpus
- **Cifras tomadas del primer informe** ([Primer Informe.pdf](../Primer%20Informe.pdf) §2):
  - 405.947 artículos cs.\*;
  - 358.494 artículos y 72,6 % de cobertura con categoría primaria restringida;
  - tamaños del piloto y de la ampliación.
- **Pendiente (L3):** la razón de la elección de los subcampos del piloto. No está documentada en los repos revisados. GR, 12-nov.
- **Pendiente (L3):** distribución por subcampo del citante en entrenamiento y en T_B. GR, 12-nov.
- **Conteo que no cuadra en el primer informe:** 28.553 (re-etiquetado de producción) + 885 = 29.438, pero se reportaron 29.336 en la versión congelada; la diferencia es de 102. El artículo usa solo el total consolidado de 38.780. Conciliar si se cita el desglose. GR, 12-nov.

### III-B. Segmentación y recuperación
- **Mean pooling (L2), verificado** en `Proyecto_LCR_CF/src/retrieval/top3_retrieval.py`, clase `SciBertEncoder`:
  - usa `last_hidden_state`;
  - multiplica por `attention_mask` y divide por la suma de la máscara;
  - normaliza con `normalize(p=2)`;
  - los textos de más de 512 tokens se cortan a 511 tokens y se agrega `[SEP]`.
- **Pendiente:** % de fragmentos truncados, a partir del contador `n_truncated` del script, para piloto y ampliación. GR, 12-nov.
- **Filtro de trabajos relacionados:**
  - esa sección era el 8,55 % de los candidatos y el 31,6 % de las primeras posiciones (3,7×);
  - se usó respaldo con los fragmentos originales en 14 artículos del piloto y 13 de la ampliación.
- **P@3 (L6):** el protocolo está redactado. **Sin responsable asignado**; fecha objetivo 16-nov. Si no se realiza, ajustar III-B, la TABLA VI, V y VI.
- **Riesgo para la discusión:** el coseno es alto y está comprimido (≈0,91, brecha mediana 0,013), lo típico de BERT sin ajuste con promedio de tokens.

### III-C. Pre-etiquetado y validación humana
- **Fuente:** primer informe §3.2–3.3; `Proyecto_LCR_CF` (`a3_gold_metrics_colab.ipynb`, `a3_metrics.py`); [guía rev3.1](../../../Folder_trabajo_Equipos_14_y_15/guia_anotacion_funcion_cita_rev3.1.md).
- **Composición de eval60 (L4), verificada** en `Proyecto_LCR_CF/notebooks/a2_label_colab_batches_experiments.ipynb` §9:
  - 20 inspeccionadas: 10 con señal de Further Reading pre-etiquetadas como Background y 10 con señal de Improvement/Modification pre-etiquetadas como Application, elegidas con `random.Random(0)`;
  - 5 por cada estrato de señal (Originator, Further Reading, Evidence, Gap, Comparison);
  - 15 al azar de la verificación de 300.
- **Límite de tamaño de eval60:** según el propio notebook, "~5 instances per short category, so per-category numbers are noise"; las diferencias de 1–2 se tratan como empates.
- **Versiones de los modelos jueces:**

  | Juez | Revisión |
  |---|---|
  | Qwen/Qwen3.8-27B | 1d4bf0f2ff |
  | google/gemma-4-26B-A4B-it | 4d7ae4984b |
  | mistralai/Mistral-Small-3.2-24B-Instruct-2506 | 95a6d26c4b |

  Entorno: vLLM 0.29.0, Transformers 5.16.1 y PyTorch 2.13.0. Semilla 0, decodificación *greedy*.
- **Pendiente:** TABLA III (n por clase, % de corrección, κ de Cohen, α de Krippendorff) desde los artefactos finales de A3. GR, 12-nov.
- **Advertencia:** entre la primera y la segunda calibración cambiaron a la vez la muestra, las reglas, la modalidad y la visibilidad de la pre-etiqueta. Por eso la mejora no se atribuye a una sola causa (va en Limitaciones).

### III-D. Clasificador supervisado
- **Fuente:** [analisis_y_plan_A4.md](../../A4/analisis_y_plan_A4.md) §4–6. Los valores son **planeados**; ST los confirma contra MLflow.
- **Variante de aislamiento:** V0.

  | Variante | Train | Validación |
  |---|---:|---:|
  | V0 | 28.039 | 3.226 |
  | V1 | 12.119 | 1.662 |
  | V2 | 11.015 | 1.539 |

  Con V0, 82,93 % de los 2.970 paquetes de T_B citan artículos vistos como citados en entrenamiento; 17,07 % son no vistos. Hash de partición: `G15-A4-split-v1`.
- **Auditoría de longitud** (§5 del análisis):

  | Configuración | Tokens promedio | Evidencia del citado recortada | Contextos recortados |
  |---|---:|---:|---:|
  | Fragmentos | 504 | ~91 % | 35 % |
  | Base | ~387 | ~5 % | 35 % |

  Esto va en la Discusión.
- **Secciones vacías:** 541 filas de train/val y 52 paquetes de T_B tienen algún fragmento sin sección; se conservan como `Unknown`.
- **Pendientes de ST (13-nov):**
  - manejo del desbalance (el plan usa entropía cruzada sin pesos; justificar o cambiar);
  - revisión exacta del modelo, épocas efectivas, horas de GPU y semillas adicionales.
- El corte temporal de la propuesta **no** se aplicó, para no modificar el T_B congelado. Mencionarlo si el evaluador lo puede extrañar.

### III-E. Modelo de lenguaje comercial
- **Pendiente de JA (13-nov):**
  - nombre, proveedor, versión y fecha de consulta del modelo (L5; el primer informe nunca lo nombró);
  - selección de ejemplos *few-shot* sin fuga desde T_B;
  - temperatura, reintentos y parseo;
  - prompts para el Apéndice A.

### III-F. Diseño experimental
- **Fuente de H1–H5:** primer informe §3.2, §4.2 y §5, y [RESUMEN_01_A2_pool_y_jueces.md](../../../Folder_trabajo_Equipos_14_y_15/RESUMEN_01_A2_pool_y_jueces.md).
- Hay una tensión que conviene enfrentar en la Discusión: H5 (sin fragmentos 49, con fragmentos 48) va contra la hipótesis central. H6 la contrasta en el clasificador.

### III-G. Métricas
- **Pendiente:** script de evaluación con bootstrap pareado por citante. GR, 12-nov.

### III-H. Despliegue
- **Pendientes de CB (19-nov):** arquitectura AWS, figura, backend y modelo de pesos abiertos elegido.
- **Pendiente de ST (19-nov):** frontend.
- Herramientas tomadas de la Propuesta §9.1.

### IV. Resultados
- La TABLA VI ya está llena con las cifras del primer informe (redondeadas a 3 decimales o 1 decimal en %).
- **Pendientes de GR (16-nov):** TABLAS VII–VIII, Fig. 3 (barras de F1 por función, D3), Fig. 4 (matrices de confusión) y análisis.
- **IV-E (D2):** comparación con los resultados publicados de SciCite y MultiCite (TABLA IX opcional) y análisis crítico de cierre. GR, 16-nov.
- **Insumos que se necesitan:**
  - **ST:** CSV de predicciones (13-nov);
  - **JA:** CSV con tokens, costo y latencia (13-nov);
  - **CB:** latencia de la API (18-nov).
- **Ejemplos de error:** ST y JA proponen 2 cada uno (16-nov).

### V. Discusión y VI. Conclusiones
- **Limitaciones ya redactadas:**
  - concentración en cs.CV;
  - tres funciones por debajo de 2.000;
  - T_B solo con pre-etiquetas de alta confianza;
  - pre-etiqueta visible;
  - calibraciones con varios cambios a la vez;
  - muestra de desarrollo pequeña;
  - recuperación sin ajuste;
  - truncamiento;
  - 82,9 % de citados vistos.
- **Fortalezas (D4)** ya redactadas en V: protocolo reproducible, comparación controlada, costo y latencia, trazabilidad por clave.
- **Aplicaciones y lecciones aprendidas (D5)** pasaron a VI. Las aplicaciones están redactadas; las lecciones son candidatas a confirmar con el equipo.
- **Trabajo futuro ya redactado:** SPECTER2, contexto largo, multietiqueta, aislamiento de citados y más funciones escasas.

## 8. Insumos requeridos por fase

**Las solicitudes para enviar a cada compañero están en [Solicitudes_Insumos_v0.1.md](./Solicitudes_Insumos_v0.1.md)** (mismos códigos; cubre A1, A3, A4 y A5). **El despliegue (D-1 a D-5) se solicita por otro medio.** Revisado el 09-nov contra los repositorios (`Proyecto_LCR_CF`, `Folder_trabajo_Equipos_14_y_15`, `A4/`). "Evidencia" indica qué existe hoy; "Responsable" se asigna a quien pueda validar y entregar el insumo. Cada insumo se deja en `Insumos/` con las iniciales como prefijo.

### A1 — Corpus y recuperación

| # | Insumo | Alimenta | Evidencia hoy | Responsable |
|---|---|---|---|---|
| A1-1 | Razón de la elección de los subcampos del piloto (cs.CV, cs.SI, cs.HC, cs.CY, cs.ET) | III-A | No documentada en los repositorios | Por asignar |
| A1-2 | Distribución por subcampo del artículo citante en entrenamiento y en T_B | III-A, TABLA II | Calculable con los datos; no existe la tabla | Por asignar |
| A1-3 | % de fragmentos truncados a 512 tokens en la recuperación (piloto y ampliación) | III-B | El script `top3_retrieval.py` lleva el contador `n_truncated`; falta el valor de las corridas | Por asignar |
| A1-4 | Evaluación humana P@3: muestra de ≈150–200 contextos (según la propuesta), dos anotadores, línea base aleatoria y κ. Si no se hace, se declara como limitación | III-B, TABLA VI, IV-A, V | No existe | Por asignar |

### A2 — Pre-etiquetado

Sin insumos pendientes: las cifras de la TABLA VI y de III-C están documentadas (primer informe, `RESUMEN_01`, notebooks de A2).

### A3 — Validación humana (T_B)

| # | Insumo | Alimenta | Evidencia hoy | Responsable |
|---|---|---|---|---|
| A3-1 | `iaa_report.md` y `test_set_gold.jsonl` (Drive, `_admin/metrics/`) | Resumen, III-C, TABLA III, TABLA VI | El cierre de A3 está en el código (commits "Gold labels and Annotation metrics"). El notebook preveía para el 9-nov 2.970 paquetes en T_B, 2 `unclear` y **2.968 evaluables**. Los archivos no están en los repositorios locales | Por asignar |
| A3-2 | De A3-1: n por función y % de corrección de la pre-etiqueta en T_B; κ de Cohen y α de Krippendorff | TABLA III, TABLA VI, resumen | Depende de A3-1 | Por asignar |

### A4 — SciBERT

| # | Insumo | Alimenta | Evidencia hoy | Responsable |
|---|---|---|---|---|
| A4-1 | Corrida de la configuración **con fragmentos** | III-D, IV-B, IV-C | **No existe.** La corrida 1 (2-nov, `A4/pruebascolab/…_corrida1.ipynb`) entrenó solo la base | Por asignar |
| A4-2 | Evaluación de ambas configuraciones sobre T_B (`RUN_TEST=True` con el *gold* de A3-1): métricas, F1 por función, matrices de confusión, IC *bootstrap* pareado por citante, citados vistos y no vistos | TABLA VII, Fig. 3, Fig. 4, IV-B | No ejecutada; esperaba el *gold* | Por asignar |
| A4-3 | Confirmar la TABLA IV con las corridas reales: épocas efectivas y versiones | III-D, TABLA IV | Corrida 1 (base): A100 40 GB, 4 épocas, ≈14 min de sesión, pico de 9,3 GiB, torch 2.11, transformers 4.57.1, scikit-learn 1.7.2, MLflow 3.17.2; hiperparámetros = planeados | Por asignar |
| A4-4 | Decisión sobre el desbalance de clases y su justificación | III-D | La corrida usa **entropía cruzada sin pesos** (`unweighted_cross_entropy`) | Por asignar |
| A4-5 | 2 ejemplos de errores representativos | IV-D | Depende de A4-2 | Por asignar |

**Advertencia para la redacción:** el F1 macro de validación de la corrida 1 (**0,846** con la base; línea de clase mayoritaria 0,062) se mide contra las **pre-etiquetas de los jueces**, no contra etiquetas humanas. Solo puede reportarse como concordancia con los jueces, nunca como desempeño final.

### A5 — Modelo de lenguaje comercial

| # | Insumo | Alimenta | Evidencia hoy | Responsable |
|---|---|---|---|---|
| A5-1 | Modelo exacto: proveedor, nombre, versión y fecha de consulta | III-E, referencia | **Sin evidencia** en los repositorios; la propuesta solo menciona "GPT-4o/5, Gemini" | Por asignar |
| A5-2 | Prompts *zero-shot* y *few-shot*; cómo se eligieron los ejemplos sin fuga desde T_B; temperatura, reintentos y manejo de respuestas inválidas | III-E, Apéndice A | Sin evidencia | Por asignar |
| A5-3 | Predicciones sobre T_B en el formato común (A6) con tokens, costo, latencia y validez por llamada | TABLA VII, TABLA VIII, Fig. 3, Fig. 4 | Sin evidencia | Por asignar |
| A5-4 | 2 ejemplos de errores representativos | IV-D | Depende de A5-3 | Por asignar |

### A6 — Evaluación comparativa (consolida GR; los datos vienen de A4 y A5)

| # | Insumo | Alimenta | Evidencia hoy | Responsable |
|---|---|---|---|---|
| A6-1 | Predicciones de validación de SciBERT base (corrida del 2-nov) y su reporte, para probar el script de métricas | III-G | Existen en la salida de la corrida 1 | Por asignar |
| — | Formato común de predicciones (`inst_key`, `pred_label`, `score_<función>`, `latency_ms`; del plan de trabajo): va en el contexto de A6 y lo cumplen A4-2 y A5-3 | TABLA VII, Figs. 3–4 | Definido en el plan de trabajo | — |

### A7 — Eficiencia, latencia y costo (consolida GR)

| # | Insumo | Alimenta | Evidencia hoy | Responsable |
|---|---|---|---|---|
| A7-1 | Costo de entrenamiento de SciBERT por configuración: GPU, horas (total y hasta el mejor checkpoint), pico de memoria y precio por hora de la GPU en USD | TABLA VIII | Corrida 1 (base): A100 40 GB, ≈14 min, pico de 9,3 GiB | Por asignar |
| A7-2 | Latencia de inferencia de SciBERT por configuración (ms/ejemplo, hardware, lote) | TABLA VIII | No existe | Por asignar |
| A7-3 | Costo total facturado por el proveedor del modelo comercial, para contrastar con el calculado en A5-3 | TABLA VIII | Sin evidencia | Por asignar |

### Despliegue

| # | Insumo | Alimenta | Evidencia hoy | Responsable |
|---|---|---|---|---|
| D-1 | Arquitectura en AWS y diagrama | III-H, Fig. 2 | Sin evidencia en los repositorios | Por asignar |
| D-2 | Backend FastAPI: endpoints, carga de modelos y modelo de pesos abiertos elegido (con sus datos exactos para la referencia) | III-H, referencia | Sin evidencia | Por asignar |
| D-3 | Frontend Next.js: flujo de usuario y captura de pantalla | III-H, Fig. 5 | Sin evidencia | Por asignar |
| D-4 | Latencia medida de la API por clasificador | TABLA VIII | Sin evidencia | Por asignar |
| D-5 | URL pública y repositorios o datos que se pueden enlazar (los textos de unarXive tienen licencias mixtas) | Apéndice B | Sin definir | Por asignar |

### Redacción (GR)

| Tarea | Sección | Fecha |
|---|---|---|
| Estado del arte (texto base: sección 3 de la propuesta), Fig. 1, TABLA I | II, III | 16-nov |
| Script de métricas con *bootstrap* pareado por citante | III-G | 12-nov |
| TABLAS VII–VIII, Figs. 3–4, comparación con trabajos previos y análisis crítico | IV | 16-nov |
| Introducción, Discusión, Conclusiones (incluidas las lecciones aprendidas), resumen | I, V, VI | 21-nov |
| Renumerar las referencias por orden de aparición cuando el texto tenga las citas [n] | Referencias | 21-nov |
| Pasada final de nomenclatura (L9) | Todo | 22-nov |
| **Todos:** revisión completa del borrador | Todo | 22-nov |

## 9. Verificación de referencias (09-nov)

**Protocolo.** Una referencia solo entra al artículo si su existencia y cada dato (autores, título, sede, volumen, páginas, año, DOI) se confirma en una fuente primaria: el PDF del paper, Crossref (registro oficial de DOI), ACL Anthology, la página oficial de la revista o de las actas, o DBLP. Todo DOI debe resolver en doi.org y todo enlace debe responder HTTP 200. Para los modelos de Hugging Face se confirma con la API que el repositorio existe y que la revisión registrada en el proyecto es un commit real (un modelo inexistente sirvió de control y devolvió error). El dato que no se pueda confirmar se omite; no se completa de memoria. Toda referencia nueva sigue este mismo protocolo antes de entrar.

| Ref. | Fuente de verificación | Resultado |
|---|---|---|
| [1] SciBERT | PDF `Papers/D19-1371.pdf` + DOI | ✅ pp. 3615–3620, Hong Kong; DOI resuelve |
| [2] Lyu et al. | PDF `Papers/s11192-021-03908-z.pdf` + Crossref | ✅ vol. 126, n.º 4, pp. 3243–3264; DOI resuelve |
| [3] unarXive 2022 | Crossref | ✅ JCDL 2023, pp. 66–70; DOI resuelve (IEEE Xplore) |
| [4] SciCite | PDF `Papers/N19-1361.pdf` + DOI | ✅ pp. 3586–3596, Minneapolis; DOI resuelve |
| [5] MultiCite | PDF `Papers/2022.naacl-main.137.pdf` + ACL Anthology | ✅ pp. 1875–1889, Seattle; DOI resuelve |
| [6] Gu et al. | Crossref + Springer + repositorio ETH Zürich | ✅ ECIR 2022, LNCS, Springer International Publishing (Cham), pp. 274–288; DOI resuelve. **Volumen LNCS no confirmado: omitido** |
| [7] Koloveas et al. | Crossref + resumen en arXiv (2502.14561) | ✅ TPDL 2025, LNCS, Springer Nature Switzerland (Cham), pp. 207–224; DOI resuelve. El resumen confirma que evalúan modelos de lenguaje abiertos para predecir la intención de cita (SciCite, ACL-ARC) |
| [8] Gilardi et al. | Crossref (con resumen) | ✅ PNAS, vol. 120, n.º 30, art. e2305016120, 2023; DOI resuelve. Un modelo de lenguaje supera a anotadores de *crowdsourcing* |
| [9] Qwen3.8-27B | API de Hugging Face | ✅ Existe (autor: Qwen; Apache-2.0); rev. 1d4bf0f2ff = commit del 14-ago-2026; enlace 200 |
| [10] gemma-4-26B-A4B-it | API y ficha de Hugging Face | ✅ Existe; la ficha lo atribuye a Google DeepMind; rev. 4d7ae4984b = commit del 20-jul-2026; enlace 200 |
| [11] Mistral-Small-3.2-24B-Instruct-2506 | API de Hugging Face | ✅ Existe (creado 19-jun-2025); rev. 95a6d26c4b = commit del 22-dic-2025; enlace 200 |
| [12] PyTorch | Actas oficiales de NeurIPS (página y BibTeX) | ✅ NeurIPS 2019, vol. 32. Las actas no publican páginas: **omitidas**. Ciudad no confirmada: omitida |
| [13] Transformers | BibTeX de ACL Anthology | ✅ EMNLP 2020 System Demonstrations, pp. 38–45; DOI resuelve |
| [14] vLLM | Crossref | ✅ SOSP '23, Koblenz, pp. 611–626; DOI resuelve (ACM DL) |
| [15] MLflow | PDF oficial del boletín + índice + DBLP | ✅ IEEE Data Eng. Bull., vol. 41, n.º 4 (dic. 2018), pp. 39–45 |
| [16] DVC | Sitio oficial y GitHub | ✅ Enlace 200. El proyecto pasó de Iterative a Treeverse/lakeFS: **se cita sin organización como autor** |
| [17] FastAPI | Sitio oficial y licencia en GitHub | ✅ Enlace 200; "Copyright (c) 2018 Sebastián Ramírez" |
| [18] Next.js | Sitio oficial | ✅ Enlace 200; el sitio identifica a Vercel como editor |
| [19] SciRepEval (SPECTER2) | Crossref + resumen en ACL Anthology + ficha `allenai/specter2` | ✅ EMNLP 2023, Singapur, pp. 5548–5566; DOI resuelve. El resumen dice que el paper publica la familia de modelos SPECTER2 |
| [20] scikit-learn | Página oficial de JMLR | ✅ vol. 12, pp. 2825–2830, 2011 |

**Eliminadas por no poder validarse (09-nov):** la referencia del modelo de lenguaje comercial y la del modelo de pesos abiertos de la aplicación. Ningún repositorio contiene código o configuración de ninguno de los dos; la propuesta solo menciona "GPT-4o/5, Gemini" como opciones. Entrarán cuando JA y CB entreguen el modelo exacto (proveedor, nombre, versión y fecha) y la referencia pase este protocolo.

**Corregido frente al borrador anterior:** Gemma pasa de "Google" a "Google DeepMind", según su ficha. DVC deja de atribuirse a "Iterative". Se quitan las páginas no oficiales de PyTorch y el volumen LNCS no confirmado de Gu. Se agregan DOI, sedes y años verificados.
