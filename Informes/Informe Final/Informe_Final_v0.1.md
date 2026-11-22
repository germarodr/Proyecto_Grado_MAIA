<!--
Versión de lectura del artículo para ir completando en equipo, una vez finalizada se pasa al formato IEEE.
-->

# CiteScope: Clasificación de la función de citas en Computer Science con modelos de lenguaje y recuperación semántica del artículo citado

**Camilo Bejarano, Germán Rodríguez, José Arteaga, Sebastián Toro**

**Resumen—** La cita es el principal mecanismo con el que un artículo científico se conecta con el conocimiento previo, aunque en la práctica suele reducirse a un conteo que no distingue si una referencia aporta contexto, fundamenta un método, respalda una afirmación o señala una limitación. Este trabajo aborda la clasificación automática de las citas en artículos de Computer Science en inglés según nueve funciones y evalúa si la evidencia recuperada del propio artículo citado mejora esa clasificación. A partir de unarXive 2022 se construyó un corpus de contextos de cita vinculados al texto completo del artículo citado; para cada par citante–citado se recuperaron con SciBERT los tres fragmentos más similares al párrafo citante. Tres modelos de lenguaje de pesos abiertos asignaron pre-etiquetas a 38.780 instancias, y dos grupos de anotadores validaron un conjunto de prueba (Test) de 2.968 instancias (κ de Cohen = 0,854). Se ajustó SciBERT con dos entradas —título y resumen del citado, frente a fragmentos recuperados— y se comparó con dos modelos comerciales sin ajuste, GPT-6 Luna y Gemini 3.5 Flash-Lite, cada uno en cuatro condiciones que combinan el tipo de prompt y el uso de ejemplos. SciBERT obtuvo un F1 macro de 0,800 con fragmentos y de 0,797 con título y resumen, una diferencia no concluyente. Los modelos comerciales obtuvieron entre 0,582 y 0,795, con un costo medio de 0,60 y 1,63 USD por cada mil instancias según el modelo; GPT-6 Luna, con un prompt específico, quedó apenas por debajo de SciBERT base (0,795 frente a 0,797). A diferencia de trabajos previos, el estudio combina una taxonomía de nueve funciones de cita, aplicada a artículos de Computer Science, evidencia recuperada del texto del citado y una comparación de desempeño, costo y latencia entre un codificador ajustado y modelos comerciales; la solución se ofrece como aplicación web.

**Índice de Términos—** función de cita, modelos de lenguaje, recuperación semántica, SciBERT, unarXive.

## I. Introducción

El volumen de artículos científicos en Computer Science crece a un ritmo que dificulta seguir cómo se relacionan los trabajos. Los indicadores de impacto más usados se basan en el número de citas. Ese conteo trata igual una referencia que fundamenta un método y otra que solo se menciona como antecedente [1]. Distinguir la función de cada cita permitiría identificar qué trabajos se usan como base, cuáles se contrastan y cuáles se citan para señalar una limitación [2].

La función de una cita no siempre es explícita en la oración que la contiene. A menudo depende de lo que aporta el artículo citado, y esa información está dispersa en su texto completo, no solo en su título o resumen. Varias funciones tienen fronteras difusas, por ejemplo entre usar un trabajo como base y modificarlo.

El objetivo general de este trabajo es clasificar automáticamente las citas de artículos de Computer Science en inglés según nueve funciones, con evidencia recuperada del artículo citado. Los objetivos específicos son: (i) construir un corpus que vincule cada contexto de cita con los fragmentos más similares del artículo citado, recuperados con SciBERT; (ii) construir un dataset trazable, con pre-etiquetado a escala, un conjunto de prueba (Test) validado por humanos, atención a las funciones escasas y aislamiento por documento para evitar fuga de información; (iii) medir si esos fragmentos mejoran un clasificador SciBERT ajustado con datos etiquetados (*fine-tuning*), frente a una entrada con título y resumen del citado; (iv) comparar ese clasificador con modelos de lenguaje comerciales sin ajuste, en desempeño, costo y latencia, y (v) desplegar la solución como aplicación web.

La solución propuesta, CiteScope, opera en dos etapas. Primero, para cada par citante–citado, compara el párrafo citante con los fragmentos del texto completo del citado y recupera los tres más similares. Se excluyen las secciones de trabajos relacionados del citado, y cada fragmento conserva el título de su sección. Después, un clasificador basado en SciBERT asigna una de nueve funciones a partir del contexto y de esa evidencia. SciBERT es un codificador (*encoder*) preentrenado con texto científico, que aquí se ajusta con instancias etiquetadas. Para obtener instancias de Training a escala, tres modelos de lenguaje de pesos abiertos propusieron pre-etiquetas. Además, 5.935 instancias (el 17,0 % del dataset), incluidas las del Test, se validaron con anotadores humanos. El corpus, el pre-etiquetado y la validación humana se construyeron en conjunto con el Grupo 14. El modelado, la evaluación y el despliegue son trabajo de este grupo.

Las contribuciones del trabajo son:
- Un dataset de 34.988 instancias de citas en Computer Science con nueve funciones. Cada instancia se vincula al artículo citado y a sus tres fragmentos más similares, y puede reconstruirse desde unarXive mediante un identificador estable. Su Test, de 2.968 instancias, tiene etiqueta humana de dos grupos de anotadores.
- Una medición controlada del efecto de los fragmentos del citado en la clasificación. Dos versiones de SciBERT se entrenan con las mismas instancias y la misma configuración, y solo difieren en la información del citado que reciben.
- Una comparación de desempeño, costo y latencia entre SciBERT ajustado y modelos de lenguaje comerciales sin ajuste. SciBERT base y los modelos comerciales reciben el mismo texto de la cita y del citado, de modo que las diferencias no se deben a la información disponible.

## II. Estado del arte

Clasificar la función de una cita exige definir qué funciones existen, contar con datos anotados y elegir modelos capaces de distinguirlas. Este trabajo añade un cuarto elemento: la evidencia del artículo citado. Esta sección revisa taxonomías, conjuntos de datos, clasificadores y recuperación, y modelos de lenguaje grandes, y cierra con la brecha que aborda el trabajo.

**Taxonomías.** Lyu et al. [2] sintetizaron 38 estudios sobre las motivaciones para citar y las agruparon en 13. Diez son científicas, porque cumplen una función en la argumentación del texto, y tres son tácticas, porque responden a razones sociales o de beneficio del autor. Este trabajo adopta nueve de las diez funciones científicas. Se excluye Assessment, la valoración del citante sobre el citado, porque expresa una postura que puede acompañar a cualquier otra función.

**Conjuntos de datos.** SciCite [3] reúne 11.020 citas de computación y medicina anotadas en tres funciones, y ACL-ARC [4], 1.941 citas de lingüística computacional anotadas en seis. MultiCite [5] mostró que estos esquemas simplifican el fenómeno. En sus 12.653 contextos de lingüística computacional, anotados por expertos en siete funciones, el 17,1 % abarca más de una oración y el 19,3 % de las citas tiene más de una función. Ningún conjunto vincula cada cita con el contenido del artículo citado ni cubre las nueve funciones científicas de Lyu et al. en artículos de Computer Science.

**Clasificadores y recuperación.** Cohan et al. [3] obtuvieron un F1 macro de 0,840 en SciCite con tareas auxiliares sobre la estructura del artículo citante, como predecir el título de la sección. SciBERT [6] alcanzó 0,855 con ajuste fino. Este modelo fue preentrenado con el texto completo de 1,14 millones de artículos de biomedicina (82 %) y computación (18 %). La recuperación sobre artículos científicos se ha usado sobre todo para recomendar qué citar [7]. Este trabajo la usa con otro fin: dado un par citante–citado, recupera los fragmentos del citado que ayudan a explicar por qué se cita.

**Modelos de lenguaje grandes.** Koloveas et al. [8] evaluaron doce modelos de lenguaje de pesos abiertos en SciCite y ACL-ARC, con aprendizaje en contexto y con ajuste fino. El ajuste fino del mejor modelo mejoró su F1 un 8 % relativo en SciCite y un 4,3 % en ACL-ARC, sin preentrenamiento científico específico. En otro dominio, un modelo comercial usado como anotador superó a trabajadores de colaboración abierta en la mayoría de las tareas sobre tuits y noticias, con un costo unas treinta veces menor [9]. Este trabajo usa modelos de pesos abiertos como jueces que proponen pre-etiquetas, y modelos comerciales como alternativa de clasificación sin ajuste.

Como resume la Tabla I, ningún trabajo revisado combina tres elementos: las nueve funciones científicas de Lyu et al. en artículos de Computer Science, evidencia recuperada del artículo citado y una comparación de desempeño, costo y latencia entre un codificador ajustado y modelos de lenguaje comerciales. Esa es la brecha que aborda este trabajo.

**TABLA I.** Trabajos relacionados.

| Trabajo | Funciones | Dominio | Texto del citado | Modelos |
|---|---|---|---|---|
| SciCite [3] | 3 | Computación y medicina | No | BiLSTM con ELMo |
| MultiCite [5] | 7, multietiqueta | Lingüística computacional | No | SciBERT, RoBERTa |
| Koloveas et al. [8] | 3 y 6 | Computación, medicina y lingüística | No | Modelos de pesos abiertos |
| CiteScope | 9 | Computer Science | Sí | SciBERT; dos modelos comerciales |

## III. Metodología

La metodología sigue el ciclo de aprendizaje automático en cuatro fases (Fig. 1): construcción de los datos, modelado, evaluación y despliegue. En la figura, los recuadros oscuros señalan los controles sobre los datos: limpieza, muestreo dirigido a las funciones escasas y aislamiento por documento para evitar fuga de información. La línea discontinua indica que el Test solo se usa en la evaluación, y la caja discontinua marca los modelos sin ajuste.

![Fig. 1](Insumos/GR_Fig1_arquitectura.png)

**Fig. 1.** Arquitectura general de CiteScope.

### A. Datos y corpus

Se utilizó unarXive 2022 [10], derivado de las fuentes LaTeX de arXiv. Se eligió porque conserva el texto estructurado por secciones y párrafos, y porque vincula las referencias bibliográficas con identificadores de arXiv, lo que permite acceder al texto completo del artículo citado. unarXive contiene 405.947 artículos con alguna categoría cs.\*, principal o secundaria. Se conservaron los 358.494 cuya categoría principal es cs.\*, eess.\* o stat.ML, para excluir los artículos de otras áreas que solo tocan computación de forma secundaria. De los 117.194 artículos de arXiv distintos que estos citan, el 72,6 % pertenece al mismo subconjunto. El contexto de cita es el párrafo del citante que contiene la cita, tal como lo segmenta unarXive. Cada instancia es una cita concreta, identificada por una clave estable (citante, párrafo, posición del marcador y citado) que permite reconstruir el texto exacto. En una muestra de 300 contextos y fragmentos, todos se reconstruyeron idénticos desde unarXive.

La construcción inicial tomó como artículos citantes los de cs.CV, cs.SI, cs.HC, cs.CY y cs.ET, y el artículo citado podía pertenecer a cualquier subcampo del corpus. El 97,8 % de los contextos de este piloto provino de cs.CV, por dos razones. Primero, cs.CV tiene más artículos en el corpus (59.780, frente a 7.033 o menos en los otros cuatro). Segundo, el 25,8 % de sus referencias tiene identificador de arXiv, frente a entre 1,9 % y 8,2 % en los demás, y solo esas referencias permiten obtener el texto completo del artículo citado. Para aumentar el suministro de funciones escasas, el corpus se amplió con citantes de cs.LG, cs.CL y cs.DS.

La limpieza eliminó fragmentos duplicados, fragmentos de menos de 15 palabras y residuos de plantillas LaTeX. Los fragmentos sin sección se conservaron, porque en su mayoría son texto real de artículos cuyos encabezados no se pudieron extraer. Se descartaron los artículos citados con menos de 1.000 palabras de texto, que corresponden a extracciones incompletas sin contenido suficiente para recuperar fragmentos. También se descartaron los contextos de más de 512 tokens de SciBERT. Estos se excluyeron en lugar de truncarse porque el párrafo completo es la consulta de la recuperación (Sección III-B), y truncarlo podría dejar fuera la cita objetivo. Por último, se excluyeron los citantes en otros idiomas y las autocitas del mismo identificador. La Tabla II resume ambos corpus.

**TABLA II.** Corpus después de la limpieza.

| Corpus | Contextos | Artículos citantes | Artículos citados | Fragmentos |
|---|---:|---:|---:|---:|
| Piloto (cs.CV, cs.SI, cs.HC, cs.CY, cs.ET) | 1.113.513 | 50.538 | 31.532 | 1.229.408 |
| Ampliación (cs.LG, cs.CL, cs.DS) | 368.296 | 50.456 | 30.153 | 1.574.790 |

En los datos usados para el modelado, según la categoría principal del citante, cs.CV reúne el 77,2 % de Training y Validation (13.269 instancias) y el 88,4 % del Test (2.968 instancias).

El desbalance entre funciones responde a cómo se cita en la práctica. La mayoría de las citas cumple una función de antecedente (Background), y funciones como Further Reading o Improvement/Modification son escasas. Por eso, además de lotes aleatorios, el pre-etiquetado incluyó lotes dirigidos por señales léxicas a las funciones escasas (muestreo dirigido). En consecuencia, el conjunto pre-etiquetado, del que salen Training, Validation y Test, no refleja la distribución natural. El Test, además, se muestreó con una cuota por función (Sección III-C).

### B. Segmentación y recuperación de evidencia

El texto de cada artículo citado se segmentó respetando sus secciones, en fragmentos de hasta 300 palabras y dos párrafos. Cada contexto de cita y cada fragmento se codificó con SciBERT [6] sin ajuste (`allenai/scibert_scivocab_uncased`). La representación de un texto es el promedio de los vectores de la última capa oculta sobre sus tokens reales, sin contar el relleno (*mean pooling*). El vector se normalizó a norma unitaria, de modo que el producto punto equivale a la similitud coseno. Se prefirió el promedio al vector `[CLS]` porque, sin ajuste, este último no está entrenado como resumen del texto. A diferencia de los contextos de cita, que se excluyeron si superaban los 512 tokens (Sección III-A), los fragmentos se truncaron. La segmentación ya limitaba cada uno a ese tamaño, y solo lo superaron 138 de 1.229.408 fragmentos del piloto (0,01 %) y 252 de 1.574.790 de la ampliación (0,02 %), por ser oraciones únicas demasiado largas para dividirse.

La consulta fue el párrafo citante completo, sin marcar la cita objetivo. Para cada par citante–citado se usó un único párrafo, el primero en que aparece el par en el corpus, y se procesaron 721.335 pares. Se excluyeron los fragmentos de las secciones de trabajos relacionados del citado, porque describen trabajo ajeno a su aporte y aparecían sobrerrepresentados en las primeras posiciones. Cuando quedaban menos de tres candidatos, se conservaron los originales. Entre los fragmentos restantes del artículo citado se seleccionaron los tres más similares a la consulta (Top-3). Cada uno conservó el título de su sección tal como aparece en el artículo citado, o quedó como sección desconocida (cerca del 1,6 % de los fragmentos). Como la consulta no distingue la cita objetivo, en párrafos que citan varios trabajos el Top-3 refleja el párrafo en conjunto y no solo esa cita.

La calidad de la recuperación se verificó de dos formas. La primera fue una auditoría de las secciones de origen, que motivó excluir los trabajos relacionados. La segunda fue el efecto de los fragmentos en las decisiones de los jueces y del clasificador (H5 y H6, Tabla V). La relevancia de cada fragmento no se anotó directamente, porque el esfuerzo de anotación humana se concentró en validar las etiquetas de los dos conjuntos de prueba (11.880 anotaciones). Esa evaluación queda como trabajo futuro.

### C. Pre-etiquetado y validación humana

Anotar desde cero decenas de miles de citas no era viable. Por eso, tres modelos de lenguaje de pesos abiertos actuaron como jueces que propusieron una pre-etiqueta: Qwen3.8-27B [11], Gemma 4 26B [12] y Mistral Small 3.2 24B [13]. Cada juez recibió las definiciones y reglas de la guía, el título y resumen del citado, sus tres fragmentos con sección, el párrafo citante y la oración de la cita objetivo. Cada uno devolvió el pasaje del párrafo citante que sustenta su decisión, una etiqueta principal y posibles secundarias. La decodificación fue determinista. La etiqueta principal de cada juez contó como un voto. Una función con al menos dos votos generó una pre-etiqueta de alta confianza, y los empates quedaron sin pre-etiqueta. La Fig. 2 muestra la hoja con la que los anotadores revisaron cada pre-etiqueta: en (a), el párrafo citante con la cita objetivo marcada, la pre-etiqueta y la etiqueta asignada con su confianza; en (b), el título, el resumen y los tres fragmentos del citado.

La selección de jueces y del prompt se hizo sobre una muestra de desarrollo de 60 instancias, sesgada a propósito hacia casos difíciles. Incluyó 20 casos en que los jueces confundían Further Reading con Background e Improvement/Modification con Application, y 5 de cada una de cinco funciones escasas, buscadas por señales léxicas (Identification of the Originator, Further Reading, Evidence, Gap y Comparison). Las 15 restantes se eligieron al azar. Su tamaño se limitó a lo que ambos grupos podían anotar a ciegas en una sesión, por lo que diferencias de uno o dos aciertos se consideran empates. Sus artículos citantes se excluyeron de Training, Validation y Test.

![Fig. 2](Insumos/figuras/GR_Fig2_hoja_anotacion.png)

**Fig. 2.** Hoja de anotación del Test: (a) cita y etiquetas; (b) artículo citado.

Para la validación, cada uno de los dos grupos del proyecto (Grupos 14 y 15) construyó su propio conjunto de prueba, disjunto del otro por instancia y artículo citante. En este trabajo se usa el propio, denominado Test. El muestreo fue estratificado por pre-etiqueta, con semilla fija, a lo sumo dos instancias por citante y una por grupo de citas contiguas. La meta era de 300 instancias válidas por función. Cada instancia fue anotada de forma independiente por una persona de cada grupo, con la pre-etiqueta visible y sin conocer la respuesta del otro. La anotación siguió una guía con reglas para las fronteras más confusas. Antes de iniciar se realizaron dos calibraciones, y la segunda exigió un κ de Cohen ≥ 0,6 en cada pareja de anotadores. Los desacuerdos los adjudicó una pareja que no había anotado la instancia, y las instancias sin función identificable se excluyeron (2 en el Test). La meta de 300 se cumplió en todas las funciones excepto Improvement/Modification, que quedó con 268 instancias en el Test.

Para evitar fuga de información, se excluyeron del dataset las demás instancias de los artículos citantes del Test y de las calibraciones (2.261). El dataset resultante suma 34.988 instancias: las 2.968 del Test y 32.020 con pre-etiqueta de alta confianza. La excepción son las instancias del conjunto de prueba del otro grupo, que llevan su etiqueta humana (sin las 3 de ese conjunto sin función identificable). Seis de las nueve funciones superan la meta de 2.000 instancias del proyecto. No la alcanzan Improvement/Modification (826), Identification of the Originator (1.692) y Further Reading (1.716). Estas cifras describen el conjunto construido. El clasificador se entrenó con menos instancias, por el aislamiento descrito en la Sección III-D. En la Tabla III, Excluded reúne las instancias que no se usan por compartir un artículo, como citante o citado, con el Test o con Validation. Correction es el porcentaje de las 330 instancias del Test muestreadas con cada pre-etiqueta cuya etiqueta final fue otra.

**TABLA III.** Instancias por función.

| Función | Dataset | Excluded | Training | Validation | Test | Correction |
|---|---:|---:|---:|---:|---:|---:|
| Background | 12.713 | 6.662 | 5.004 | 717 | 330 | 13,9 % |
| Gap | 3.189 | 1.483 | 1.217 | 179 | 310 | 12,7 % |
| Basis | 3.022 | 1.740 | 848 | 112 | 322 | 13,6 % |
| Comparison | 3.530 | 1.853 | 1.188 | 176 | 313 | 8,2 % |
| Application | 4.766 | 3.351 | 871 | 144 | 400 | 3,3 % |
| Improvement/ Modification | 826 | 399 | 140 | 19 | 268 | 25,2 % |
| Evidence | 3.534 | 1.664 | 1.318 | 166 | 386 | 1,5 % |
| Identification of the Originator | 1.692 | 981 | 329 | 58 | 324 | 3,6 % |
| Further Reading | 1.716 | 618 | 701 | 82 | 315 | 4,8 % |
| **Total** | **34.988** | **18.751** | **11.616** | **1.653** | **2.968** | **9,7 %** |

Antes de adjudicar, los anotadores de los dos grupos coincidieron en el 87,0 % de las instancias del Test, y el 13,0 % restante (386 instancias) se adjudicó. Descontando las coincidencias esperables por azar, el κ de Cohen fue de 0,854. Este valor se considera casi perfecto (por encima de 0,80) [14] y respalda la confiabilidad de las etiquetas del Test. Por función, el κ fue menor en Background (0,756) y mayor en Identification of the Originator (0,967).

### D. Clasificador supervisado

Se partió de las 32.020 instancias del dataset que no pertenecen al Test (Sección III-C), con autorización del Grupo 14 para usar las etiquetas humanas de su conjunto de prueba. Para evitar fuga de información se aplicó un aislamiento estricto por documento. Se excluyeron las instancias cuyo artículo citante o citado aparece, en cualquiera de los dos papeles, en el Test, de modo que ningún documento del Test se vio durante el entrenamiento. La partición entre Training y Validation (90/10) se hizo por artículo citante con un hash fijo. Para que tampoco compartan documentos, se retiraron de Training las instancias con algún artículo presente en Validation. Quedaron 11.616 instancias en Training y 1.653 en Validation. De ellas, 944 y 125, respectivamente, tienen etiqueta humana, y el resto conserva la pre-etiqueta. El aislamiento redujo el suministro: de las 34.988 instancias del dataset se usaron 13.269 para entrenar y validar. Solo Background superó las 2.000 instancias en Training, donde pasó a ser el 43,1 %, e Improvement/Modification quedó con 140 instancias en Training y 19 en Validation (Tabla III).

Se ajustó SciBERT con una capa lineal de clasificación sobre el token `[CLS]` y nueve salidas, con todos los parámetros entrenables. Se entrenaron dos modelos independientes desde el mismo punto de partida y sobre las mismas instancias, que solo difieren en la información del citado:

- **Base:** `[CLS]` contexto `[SEP]` título y resumen del citado `[SEP]`.
- **Con fragmentos (Top-3):** `[CLS]` contexto `[SEP]` tres fragmentos Top-3, cada uno precedido por su sección `[SEP]`.

Como SciBERT admite 512 tokens, el contexto se limitó a 192 tokens centrados en la cita objetivo y el resto se asignó al citado. El título podía ocupar hasta 64 tokens en la configuración base, y cada encabezado de sección hasta 24 en la de fragmentos. Cada segmento se recortó desde el final, y el espacio no usado se redistribuyó. La pérdida fue la entropía cruzada sin pesos por clase. Se probaron dos esquemas de pesos para compensar el desbalance (raíz de la frecuencia inversa y frecuencia inversa limitada). Ninguno superó en Validation el F1 macro medio de tres semillas del entrenamiento sin pesos, en ninguna de las dos configuraciones. Los hiperparámetros de cada configuración se eligieron por separado mediante una búsqueda en rejilla con la semilla 42: tasa de aprendizaje de 1e-5, 2e-5 y 3e-5, y decaimiento de pesos de 0,01 y 0,1, con 12 ensayos entre las dos configuraciones. La configuración elegida y cada alternativa (límites de contexto de 128 y 256 tokens y esquemas de pesos) se repitieron con las semillas 17 y 73, para compararlas por su media de tres semillas y no por una sola corrida. En ambas configuraciones se eligieron los mismos valores (Tabla IV). El modelo final de cada una fue el de semilla 42, y su mejor punto de control se eligió por F1 macro en Validation: la época 5 en la base y la 7 con fragmentos. Validation combina pre-etiquetas (92,4 %) y etiquetas humanas (7,6 %) y se usó para tomar estas decisiones, por lo que sus métricas son optimistas. La evaluación final se hizo sobre el Test, independiente de la selección de hiperparámetros, con los modelos ya congelados. Los estudios de límites de contexto y de pesos por clase sumaron 28 entrenamientos cada uno; su código, su registro en MLflow y su documentación están en el repositorio del proyecto [15].

**TABLA IV.** Configuración de entrenamiento.

| Parámetro | Valor |
|---|---|
| Modelo | `allenai/scibert_scivocab_uncased` |
| Longitud máxima | 512 tokens (contexto ≤ 192; se probaron 128 y 256) |
| Tasa de aprendizaje | 3e-5 en ambas configuraciones, elegida en Validation |
| Decaimiento de pesos | 0,1 en ambas configuraciones, elegido en Validation |
| Épocas | Hasta 12, parada temprana con paciencia 3 (mejor época: 5 en la base, 7 con fragmentos) |
| Lote efectivo | 32 (16 × acumulación 2) |
| Optimizador | AdamW, calentamiento 10 %, decaimiento lineal de la tasa |
| Pérdida | Entropía cruzada sin pesos por clase (se probaron dos esquemas de pesos) |
| Precisión y hardware | Entrenamiento en BF16; evaluación en FP32; GPU A100 de 40 GB (Colab) |
| Semillas | 42 (modelo principal), 17 y 73 |

### E. Modelos de lenguaje comerciales

Se evaluaron dos modelos de lenguaje comerciales de gama económica y de proveedores distintos, consultados mediante sus API en noviembre de 2026. GPT-6 Luna (`gpt-6-luna`, OpenAI) [16] tiene tarifas de 0,10 y 0,50 USD por millón de tokens de entrada y de salida, y Gemini 3.5 Flash-Lite (`gemini-3.5-flash-lite`, Google) [17], de 0,30 y 2,50 USD. Se eligió la gama económica para comparar su desempeño con el de SciBERT a un costo acotado. Cada modelo se evaluó sin ajuste en las mismas cuatro condiciones, que combinan dos factores. El primero es el prompt: genérico, con definiciones breves de las nueve funciones, o específico, que añade las aclaraciones de la guía de anotación y las reglas de la versión final del prompt de los jueces. El segundo es el uso de ejemplos: *zero-shot*, o *few-shot* con nueve ejemplos con etiqueta humana del conjunto de prueba del otro grupo, uno por función. Los ejemplos no comparten artículos con el Test, ni como citante ni como citado. Cada modelo respondió 11.872 consultas: cuatro condiciones por 2.968 instancias.

Todos los modelos recibieron el contexto de cita con el título y el resumen del citado, la entrada que define el enunciado del proyecto. Para que la comparación fuera justa, en el Test cada modelo recibió exactamente el mismo texto, ya recortado, que SciBERT base. Cada modelo devolvió en JSON un puntaje entre 0 y 1 por función, y la predicción fue la función con mayor puntaje. Los empates se resolvieron con un orden fijo de las funciones. Una respuesta se consideró válida si contenía las nueve funciones con puntajes que sumaban 1 (con tolerancia de 0,001). Una respuesta inválida se conservó como predicción fallida, sin reintentos. No se fijaron la temperatura ni el esfuerzo de razonamiento de GPT-6 Luna, por lo que cada servicio usó su valor por defecto, y la salida se limitó a 2.048 tokens. GPT-6 Luna se consultó en modo JSON. A Gemini 3.5 Flash-Lite se le exigió además un esquema JSON estricto tras un piloto de desarrollo con 45 instancias del conjunto de prueba del otro grupo, cinco por función y separadas de los ejemplos. En ese piloto, la salida sin esquema produjo nueve respuestas inválidas, con nombres de función alterados o con todos los puntajes en cero.

Como condición principal de cada modelo se usa la del prompt específico con ejemplos, porque es la que recibe más información, y no la de mejor resultado. En Gemini 3.5 Flash-Lite no es la mejor condición: el prompt específico sin ejemplos obtuvo un F1 macro de 0,748, frente a 0,714. Los prompts y el código de cada modelo están en el repositorio del proyecto [18], [19].

### F. Métricas

Se reportan precisión, exhaustividad y F1 por función, sus promedios macro y micro, y matrices de confusión. El F1 macro es la métrica principal porque pondera igual a todas las funciones, incluidas las escasas:

$$F1_{macro} = \frac{1}{K}\sum_{k=1}^{K}\frac{2P_kR_k}{P_k+R_k} \qquad (1)$$

donde $K = 9$ es el número de funciones, y $P_k$ y $R_k$ son la precisión y la exhaustividad de la función $k$. La precisión indica qué fracción de las predicciones de una función es correcta, y la exhaustividad, qué fracción de las instancias de esa función se recupera.

La diferencia de F1 macro entre las dos configuraciones de SciBERT, y la de cada condición de los modelos comerciales frente a SciBERT base, se acompañan de un intervalo de confianza del 95 %. El intervalo se obtiene por *bootstrap* pareado por artículo citante, porque las citas de un mismo artículo no son independientes, con 2.000 remuestreos comunes a todos los modelos. Son comparaciones exploratorias, sin corrección por comparaciones múltiples. Las respuestas inválidas cuentan como errores, y todas las métricas se calculan sobre las 2.968 instancias del Test. En esta clasificación de etiqueta única, el F1 micro coincide con la exactitud.

La eficiencia se evalúa en cuatro dimensiones:

- **Costo:** por 1.000 instancias. En SciBERT, horas de GPU por una tarifa de referencia; en los modelos comerciales, tokens por la tarifa de cada proveedor.
- **Latencia:** segundos por instancia en SciBERT, medidos por lotes, y por consulta en los comerciales.
- **Formato:** tasa de respuestas inválidas por modelo y condición.
- **Estabilidad:** variación entre semillas en Validation para SciBERT y consistencia del formato en los modelos comerciales.

### G. Diseño experimental

Los experimentos se formularon como hipótesis con una métrica de decisión (Tabla V). H1–H5 corresponden al desarrollo de la recuperación y del pre-etiquetado, y H6 y H7, a la evaluación final sobre el Test, que se usó una sola vez. Cada hipótesis se resolvió con su métrica: en desarrollo, una diferencia de uno o dos aciertos se tomó como empate; en el Test, una diferencia con intervalo que incluye el cero, como no concluyente.

**TABLA V.** Hipótesis y experimentos.

| | Hipótesis | Experimento | Métrica |
|---|---|---|---|
| H1 | Jueces de 24–27B superan a jueces de 7–8B | Trío Llama 3.1 8B [20], Qwen 2.5 7B [21] y Mistral 7B [22] frente al trío final | Aciertos en los 41 casos de desarrollo con acuerdo humano |
| H2 | El tercer juez afecta la calidad del trío, sobre todo en Gap | Mistral Small 3.2 24B [13] frente a Ministral 3 14B [23] | Aciertos en la muestra de desarrollo; precisión en 20 instancias adicionales de Gap |
| H3 | Incorporar reglas de adjudicación al prompt mejora el pre-etiquetado | Cuatro versiones sucesivas del prompt | Aciertos en la muestra de desarrollo |
| H4 | Sin filtro, las secciones de trabajos relacionados dominan las primeras posiciones de la recuperación | Auditoría de las secciones del fragmento en primera posición, con y sin filtro | Peso de esas secciones entre los candidatos frente a la primera posición |
| H5 | Los fragmentos mejoran las decisiones de los jueces | Ablación con y sin fragmentos | Aciertos en la muestra de desarrollo; cambios en 885 casos difíciles |
| H6 | El clasificador con fragmentos supera al clasificador base | Dos ajustes de SciBERT con las mismas instancias | Diferencia de F1 macro con intervalo *bootstrap* pareado por citante |
| H7 | Los modelos comerciales sin ajuste no superan a SciBERT ajustado y cuestan más | Cuatro condiciones de cada modelo comercial frente a SciBERT base, con la misma entrada | F1 macro con IC *bootstrap* pareado; costo por mil instancias; latencia |

### H. Despliegue

El demostrador es una aplicación web de cuatro contenedores Docker desplegados en Amazon ECS (Fig. 3): la interfaz, la API, el servidor del modelo de pesos abiertos y la base de datos. Trabaja sobre 40 ejemplos del Test con licencia CC BY y el Top-3 precalculado, un alcance acordado con el experto. En la interfaz, desarrollada con Next.js, el usuario elige un ejemplo, revisa el contexto y los tres fragmentos con su sección y elige un clasificador.

![Fig. 3](Insumos/CB_Fig2_arquitectura_demostrador.png)

**Fig. 3.** Arquitectura de software del demostrador de CiteScope.

Como resultado, el usuario obtiene la función predicha, el puntaje de las nueve funciones y la etiqueta humana. La API, en FastAPI, prepara la entrada de cada modelo con el mismo código del modelado. Ofrece tres clasificadores: SciBERT con fragmentos, el de mayor F1 macro en el Test; Gemini 3.5 Flash-Lite, con el prompt específico sin ejemplos, su mejor condición, y Llama 3.1 8B Instruct [20], servido con Ollama, cuantizado a 4 bits y con el mismo prompt. Las respuestas de los modelos de lenguaje se validan con la regla de la Sección III-E, y cada inferencia se registra en PostgreSQL con su latencia para el monitoreo.

El desarrollo usó Python, PyTorch [24], Transformers [25], vLLM [26] y scikit-learn. Los datos se versionaron con DVC, los experimentos se registraron en MLflow y el entrenamiento se ejecutó en Colab con GPU A100. El código del demostrador está en el repositorio del proyecto [27].

## IV. Resultados

Los resultados siguen el orden de la metodología: primero, las etapas que construyeron el dataset (H1–H5); después, el desempeño de los clasificadores sobre el Test (H6 y H7), su eficiencia y un análisis de sus errores.

### A. Recuperación, pre-etiquetado y validación humana (H1–H5)

La Tabla VI reúne los indicadores de la construcción del dataset: recuperación, pre-etiquetado y validación humana. Las cifras de desarrollo provienen de la muestra de 60 instancias (Sección III-C), sesgada hacia casos difíciles. Sirven para comparar alternativas, no para estimar la precisión de los jueces.

Los jueces de mayor tamaño superaron con claridad a los pequeños (H1). El tercer juez casi no cambió el total, aunque sí en Gap, lo que respalda en parte H2. La versión adoptada del prompt alcanzó 48 de 60 aciertos (H3). Las diferencias de un caso entre versiones vecinas son empates.

Las similitudes coseno son altas y comprimidas, típicas de promedios de BERT sin ajuste. Sirven para ordenar candidatos, no para probar su relevancia. La auditoría de secciones respalda H4. Sin filtro, los trabajos relacionados estaban sobrerrepresentados en las primeras posiciones y aparecían en el Top-3 de la mitad de los pares. Con el filtro, la introducción del citado pasó a ser la sección más frecuente en la primera posición. Aun así, los fragmentos no mejoraron las decisiones de los jueces: los 45 cambios en 885 casos difíciles se repartieron casi por igual a favor y en contra (H5).

En la validación humana, la etiqueta final coincidió con la pre-etiqueta en el 90,3 % de las instancias del Test. La coincidencia fue del 94,6 % cuando los tres jueces votaron igual y del 82,2 % cuando votaron 2 de 3, por lo que la unanimidad es una señal útil de confiabilidad. Improvement/Modification concentró las correcciones, sobre todo hacia Basis y Application.

**TABLA VI.** Indicadores por etapa.

| Etapa | Indicador | Valor | H |
|---|---|---|---|
| Recuperación | Coseno medio del primer fragmento (piloto / ampliación) | 0,915 / 0,913 | — |
| | Brecha mediana entre el primer y el tercer fragmento | 0,013 | — |
| | Trabajos relacionados: % de candidatos frente a % de primeras posiciones, sin filtro | 8,6 % frente a 31,6 % | H4 |
| | Pares con algún fragmento de trabajos relacionados en el Top-3 sin filtro | 51,9 % | H4 |
| Pre-etiquetado (desarrollo) | Trío 7–8B frente a trío final (41 casos) | 13 frente a 30 | H1 |
| | Tercer juez: Mistral Small frente a Ministral (60 casos; 20 Gap) | 48 frente a 45; 17 frente a 12 | H2 |
| | Versiones del prompt (60 casos) | 43 → 47 → **48** → 47 | H3 |
| | Sin fragmentos frente a con fragmentos (60 casos) | 49 frente a 48 | H5 |
| Pre-etiquetado (producción) | κ de Fleiss entre jueces; unanimidad | 0,67; 63 % | — |
| | Instancias con pre-etiqueta de alta confianza | 37.254 de 38.780 (96,1 %) | — |
| | Estabilidad al repetir 300 instancias | 98 % | — |
| Validación humana | κ de Fleiss: primera frente a segunda calibración | 0,47 frente a 0,87 | — |
| | Corrección de la pre-etiqueta en el Test | 9,7 % (25,2 % en Improvement/Modification) | — |
| | κ de Cohen / α de Krippendorff en el Test | 0,854 / 0,854 | — |

### B. Desempeño de clasificación (H6 y H7)

Sobre el Test, SciBERT base obtuvo una precisión macro de 0,818, una exhaustividad macro de 0,793, un F1 macro de 0,797 y un F1 micro de 0,792; con fragmentos, 0,822, 0,798, 0,800 y 0,795, respectivamente. En su condición principal, GPT-6 Luna obtuvo 0,815, 0,800, 0,795 y 0,801, y Gemini 3.5 Flash-Lite, 0,770, 0,709, 0,714 y 0,710. Con fragmentos, SciBERT superó a la base en apenas 0,003 de F1 macro, y el intervalo de confianza de esa diferencia incluye el cero. Por tanto, los fragmentos no mejoraron el clasificador de forma demostrable (H6). En Validation, ninguna alternativa probada superó a la configuración elegida, y la variación entre semillas fue baja (desviación estándar de 0,002 en la base y 0,004 con fragmentos).

GPT-6 Luna obtuvo prácticamente el mismo F1 macro que SciBERT base, con un intervalo que incluye el cero, y el F1 micro más alto. Gemini 3.5 Flash-Lite quedó 0,083 por debajo. Ninguna de las ocho condiciones comerciales superó a SciBERT base: su F1 macro fue de 0,582 a 0,795. El prompt específico mejoró el F1 macro en todos los casos, entre 0,07 y 0,17, mientras que los ejemplos solo ayudaron con el prompt genérico.

El error más frecuente de SciBERT, en ambas configuraciones, es predecir Background, que es la función con menor precisión (0,53) y menor F1. Le siguen las confusiones de Improvement/Modification con Basis y de Evidence con Gap. Con fragmentos, el F1 sube en seis funciones y baja en tres (Fig. 4), diferencias que son solo descriptivas.

![Fig. 4](Insumos/figuras/GR_Fig3_f1_por_funcion.png)

**Fig. 4.** F1 por función sobre el Test.

Los modelos comerciales se equivocan de forma distinta (Fig. 5). GPT-6 Luna presenta la confusión inversa a la de SciBERT: asigna Improvement/Modification a más de un tercio de las instancias de Basis, su función más débil. En cambio, supera a SciBERT en Background y Evidence. Gemini 3.5 Flash-Lite acentúa el sesgo hacia Background, al que asigna la mitad de las instancias de Gap. GPT-6 Luna y SciBERT base aciertan en instancias distintas: al menos uno de los dos acierta en el 93,0 %.

![Fig. 5](Insumos/figuras/GR_Fig4_matrices_confusion.png)

**Fig. 5.** Matrices de confusión sobre el Test.

### C. Eficiencia, latencia y costo (H7)

La Tabla VII compara el costo, la latencia y el formato de los modelos, medidos como se describe en la Sección III-F. Para los comerciales muestra la condición principal. La columna Entrenamiento muestra las horas de A100 del modelo final, sin la búsqueda de hiperparámetros.

**TABLA VII.** Costo y latencia por modelo.

| Modelo | Entrenamiento (h) | Costo por 1.000 instancias (USD) | Latencia (s/instancia) | Formato inválido |
|---|---:|---:|---:|---:|
| SciBERT base | 0,26 | 0,0013 | 0,0088 | — |
| SciBERT con fragmentos | 0,35 | 0,0016 | 0,0106 | — |
| GPT-6 Luna | — | 0,96 | 2,7 | 0,03 % |
| Gemini 3.5 Flash-Lite | — | 2,70 | 1,7 | 0 % |

Con una tarifa de referencia de 0,55 USD por hora de A100 en Colab, entrenar SciBERT costaría unos 0,14 USD en la base y 0,19 USD con fragmentos, sin la búsqueda de hiperparámetros. Su inferencia por lotes requirió unos 8,8 y 10,6 s por cada 1.000 instancias. Los modelos comerciales no requieren entrenamiento, aunque cada consulta tiene un costo. Las cuatro condiciones sobre el Test costaron 7,06 USD con GPT-6 Luna y 19,32 USD con Gemini 3.5 Flash-Lite, en promedio 0,60 y 1,63 USD por 1.000 instancias. La diferencia se debe a las tarifas de Gemini 3.5 Flash-Lite, entre tres y cinco veces mayores. Así, entrenar SciBERT costaría menos que clasificar unos pocos cientos de instancias con GPT-6 Luna. Estos importes se calcularon con los tokens y las tarifas publicadas. En GPT-6 Luna, lo facturado sería algo mayor, unos 7,6 USD, por consultas repetidas tras una desconexión.

La latencia por consulta de los modelos comerciales fue de 1,0 a 1,7 s en Gemini 3.5 Flash-Lite y de 2,0 a 2,7 s en GPT-6 Luna, que razona antes de responder, y creció con la longitud del prompt. No es directamente comparable con la de SciBERT, medida por lotes y sin red.

Todas las condiciones comerciales produjeron menos del 0,7 % de respuestas inválidas, casi todas por puntajes que no sumaban 1 y en condiciones sin ejemplos. El esquema estricto de Gemini 3.5 Flash-Lite no bastó para garantizar esa suma. La estabilidad de SciBERT se midió como la variación entre semillas (Sección IV-B). La de los comerciales se midió solo como la consistencia del formato, porque cada condición se ejecutó una vez.

### D. Análisis cualitativo

Dos errores de SciBERT ilustran sus confusiones más frecuentes, y en ambos fallan las dos configuraciones. En el primero, el citante afirma que "CNNs [...] have been shown to outperform Deformable Part Model (DPM) based methods for recognition tasks" y cita el trabajo como respaldo (Evidence). SciBERT predice Background, posiblemente porque la cita aparece en una enumeración de trabajos dentro de una frase general. En el segundo, el citante declara: "Inspired by the success of convolutional-deconvolutional network (CNN-DecNN) in semantic segmentation [...], we adapt the network to detect salient objects". La adaptación del método citado corresponde a Improvement/Modification, y SciBERT predice Basis. Esta es la confusión más frecuente de Improvement/Modification, función que también concentró las correcciones de los anotadores (Sección IV-A).

Los modelos comerciales aciertan en casos en que SciBERT base falla, como el siguiente. El citante presenta "a novel background selective whitening (BSW) loss function, inspired by" el trabajo citado, que propone una función de pérdida de blanqueo selectivo por instancia. SciBERT base predice Basis, mientras que GPT-6 Luna y Gemini 3.5 Flash-Lite asignan Improvement/Modification, la etiqueta humana, porque el citante adapta la pérdida del citado a otro problema. Este caso es uno de los 40 ejemplos del demostrador, cuya interfaz se muestra en la Fig. 6.

![Fig. 6](Insumos/CB_Fig5_demostrador.png)

**Fig. 6.** Demostrador de CiteScope.

### E. Comparación con trabajos previos y análisis crítico

Las cifras de este trabajo no son directamente comparables con las publicadas. En SciCite, con tres funciones, Cohan et al. [3] reportaron un F1 macro de 0,840 y SciBERT [6], 0,855. MultiCite [5] es multietiqueta, con siete funciones, y Koloveas et al. [8] evalúan modelos de pesos abiertos sobre SciCite y ACL-ARC. Ninguno usa el texto del artículo citado. Este trabajo distingue nueve funciones, varias con fronteras difusas, y se evalúa sobre un Test con una cuota por función. Que SciBERT alcance un F1 macro cercano (0,797–0,800) indica que la tarea con nueve funciones es abordable, aunque no que el modelo supere a los anteriores.

**Análisis crítico.** Los resultados descansan en un único Test de 2.968 instancias. Las diferencias entre las dos configuraciones de SciBERT, y entre SciBERT base y GPT-6 Luna con prompt específico, son menores que la incertidumbre del muestreo y del mismo orden que la variación entre semillas, por lo que no permiten ordenar esos modelos. Sí son robustas la ventaja de SciBERT base sobre Gemini 3.5 Flash-Lite y sobre las condiciones con prompt genérico. Los contrastes con los modelos comerciales no se corrigieron por comparaciones múltiples. Además, el prompt específico deriva del de los jueces que generaron las pre-etiquetas, lo que podría favorecerlo frente al genérico. Las demás fuentes de sesgo se discuten en las Limitaciones (Sección V).

## V. Discusión

El trabajo partió de dos preguntas: si la evidencia del artículo citado mejora la clasificación y si un codificador ajustado justifica su costo frente a modelos comerciales sin ajuste. Las hipótesis se resuelven así. H1, aceptada: los jueces grandes superaron con claridad a los pequeños. H2, aceptada en parte: el tercer juez solo marcó diferencia en Gap. H3, aceptada en desarrollo: la versión adoptada del prompt fue la mejor, aunque por pocos casos. H4, aceptada: sin filtro, los trabajos relacionados dominaban las primeras posiciones. H5, rechazada: los fragmentos no mejoraron las decisiones de los jueces. H6, no concluyente: la ventaja de los fragmentos en SciBERT no se distingue del azar. H7, aceptada: ninguna condición comercial superó a SciBERT y su costo por instancia es mayor, aunque GPT-6 Luna con prompt específico no se distingue de SciBERT en F1 macro.

**Aporte de los fragmentos.** Los fragmentos no mejoraron de forma clara ni a los jueces ni al clasificador. Una explicación compatible con los datos es el límite de 512 tokens de SciBERT. Con fragmentos, el texto del citado se recorta en el 92 % de las instancias de Validation, frente a muy pocas con título y resumen, de modo que el modelo ve solo parte de la evidencia. El efecto depende de la función: los fragmentos ayudan en Further Reading, Basis e Improvement/Modification y perjudican en Evidence y Comparison (Fig. 4). El diseño, sin embargo, no permite atribuir estas diferencias a una causa concreta.

**Sesgo hacia Background.** Background es el 43,1 % de Training y solo el 11,1 % del Test, que tiene una cuota por función (Tabla III). Esa diferencia de distribución es una explicación posible del exceso de predicciones de Background, y las ponderaciones probadas no mejoraron el F1 macro medio. Gemini 3.5 Flash-Lite, sin entrenamiento, muestra el mismo sesgo con mayor intensidad, lo que sugiere que el desbalance no es la única causa. Background puede funcionar como la función por defecto cuando el contexto no explicita el papel de la cita. GPT-6 Luna no muestra ese sesgo.

**Codificador frente a modelos comerciales.** Un modelo comercial de gama económica, sin ajuste y con un prompt específico, alcanzó el desempeño de SciBERT ajustado con 11.616 instancias, aunque con otro perfil de errores. Por eso, la ventaja del ajuste no está en el desempeño medio, sino en el costo por instancia y en la independencia de un proveedor externo. El desempeño de los modelos comerciales depende sobre todo del prompt: las reglas del prompt específico, desarrolladas para los jueces, aportaron más que los ejemplos. Además, GPT-6 Luna superó a Gemini 3.5 Flash-Lite en todas las condiciones con tarifas menores, por lo que el precio no anticipa el desempeño. Como GPT-6 Luna y SciBERT aciertan en instancias distintas, combinarlos podría mejorar a ambos.

**Aportes y fortalezas.** Los aportes son los tres señalados en la Introducción: el dataset, la medición controlada del efecto de los fragmentos y la comparación de desempeño, costo y latencia. El Test se construyó con un protocolo reproducible: muestreo estratificado con semilla fija, guía con reglas para las fronteras más confusas, calibración previa con un umbral de acuerdo por pareja y adjudicación de desacuerdos por anotadores independientes. Las dos configuraciones de SciBERT se compararon de forma controlada: mismas instancias y partición, hiperparámetros elegidos con la misma búsqueda y tres semillas. Así, la diferencia entre ellas se atribuye a la información del citado. El aislamiento por documento garantiza que ningún artículo del Test se vio durante el entrenamiento. La evaluación incluye costo y latencia, y no solo desempeño, lo que permite juzgar la viabilidad práctica de cada alternativa. Cada instancia conserva una clave que permite reconstruir su texto exacto y reproducir el pre-etiquetado y la recuperación.

**Limitaciones.** El corpus está concentrado en cs.CV (77 % de Training y Validation y 88 % del Test), por lo que los resultados no representan por igual a todo Computer Science. Tres funciones quedaron por debajo de la meta de 2.000 instancias, y tras el aislamiento por documento solo Background la supera en Training. Improvement/Modification quedó con apenas 140 instancias en Training y 268 en el Test, por debajo de la meta de 300. El Test se muestreó entre instancias con pre-etiqueta de alta confianza y se anotó con la pre-etiqueta visible, lo que puede favorecer tanto el F1 como el acuerdo. La mejora del acuerdo entre calibraciones tampoco puede atribuirse a una sola intervención, porque cambiaron a la vez la muestra, las reglas y la modalidad. La muestra de desarrollo es pequeña y sesgada a casos difíciles. La recuperación usa SciBERT sin ajuste, la entrada con fragmentos se trunca y la relevancia de los fragmentos no se evaluó con anotadores. Un diagnóstico posterior del modelo base, con nueve entrenamientos que aumentaron el *dropout* o el decaimiento de pesos, no redujo la pérdida de Validation, y en todos persistieron señales de sobreajuste después de la tercera época. Los modelos finales, elegidos por F1 en las épocas 5 y 7, no se reemplazaron. Los modelos comerciales se evaluaron una sola vez por condición, en versiones de servicio que pueden cambiar, y con un costo calculado, no facturado.

## VI. Conclusiones y trabajo futuro

Este trabajo construyó, con el Grupo 14, un dataset de 34.988 instancias de citas en Computer Science con nueve funciones, vinculadas al texto del artículo citado. Su Test, de 2.968 instancias, fue validado por dos grupos de anotadores con un κ de Cohen de 0,854.

La primera pregunta del trabajo no tiene una respuesta concluyente: no se encontró evidencia de que los fragmentos del artículo citado mejoraran la clasificación. SciBERT obtuvo un F1 macro de 0,800 con fragmentos y de 0,797 con título y resumen, y el intervalo de confianza de la diferencia incluye el cero. El recorte por el límite de 512 tokens es una limitación del diseño cuyo efecto no se aisló.

La segunda pregunta tiene una respuesta mixta. En desempeño, GPT-6 Luna, sin ajuste y con un prompt específico, no se distinguió de SciBERT, aunque se equivocó en otras instancias. Gemini 3.5 Flash-Lite quedó por debajo en todas las condiciones. En costo, SciBERT es más conveniente: entrenarlo costaría menos que clasificar unos pocos cientos de instancias con un modelo comercial. En los dos modelos comerciales, el prompt pesó más que los ejemplos, y más del 99 % de las respuestas respetó el formato pedido. La solución se ofrece como aplicación web que muestra la función predicha junto con los fragmentos del citado.

**Aplicaciones prácticas.** Clasificar la función de las citas, junto con la evidencia del citado, puede apoyar revisiones sistemáticas de literatura, al identificar qué trabajos se usan como base o se contrastan. También puede apoyar estudios bibliométricos que midan el tipo de influencia entre trabajos, y no solo el número de citas, y herramientas de escritura académica que sugieran o verifiquen cómo se cita una fuente.

**Lecciones aprendidas.**
- **Datos.** Coordinar dos grupos exige, desde el inicio, un contrato de datos con identificadores estables y reglas de exclusión explícitas. Así se separaron los dos conjuntos de prueba y se aisló el Test por documento.
- **Pre-etiquetado.** Los jueces permiten pre-etiquetar a escala, aunque su fiabilidad cambia según la función: se corrigió el 25,2 % de las pre-etiquetas de Improvement/Modification y el 1,5 % de las de Evidence. Por eso, la validación humana debe planearse por función.
- **Validación humana.** La calibración debe preceder a la anotación: entre calibraciones, con la guía ajustada, el κ de Fleiss pasó de 0,47 a 0,87, de un acuerdo moderado a uno casi perfecto [14].
- **Modelado.** Con el límite de 512 tokens totales de SciBERT, incorporar fragmentos del artículo citado no mostró una mejora concluyente de la clasificación en las configuraciones evaluadas. Redistribuir ese presupuesto entre el contexto y los fragmentos tampoco mejoró el F1 macro medio frente a la configuración elegida. La recuperación debe evaluarse junto con la forma en que la evidencia llega al clasificador.
- **Modelos comerciales.** El esquema y los ejemplos cuidan la validez de las respuestas, y el prompt decide el desempeño. Sin esquema, Gemini 3.5 Flash-Lite dio 9 respuestas inválidas de 45 en el piloto, y con él, menos del 0,7 % en el Test. Los ejemplos redujeron las inválidas y subieron el F1 macro con el prompt genérico. Con el específico, solo GPT-6 Luna mantuvo su desempeño.

**Trabajo futuro.** En la recuperación, se propone evaluar con anotadores la relevancia de los fragmentos mediante precisión en 3 (P@3), frente a una línea base aleatoria, y usar un modelo ajustado para similitud entre documentos científicos, como SPECTER2 [28]. En la clasificación, usar modelos de contexto largo, para no truncar los fragmentos, y combinar SciBERT con un modelo comercial, porque aciertan en instancias distintas. En los datos y la evaluación, ampliar las funciones escasas, extender la clasificación a múltiples etiquetas y medir la estabilidad de los modelos comerciales con ejecuciones repetidas.

## Declaración de uso de IA

Los autores usaron asistentes de inteligencia artificial generativa como apoyo en la escritura y depuración de código, en la búsqueda y organización de información y en la revisión de la redacción de este documento. Los autores revisaron y verificaron todo el contenido y asumen la responsabilidad por él. Los modelos de lenguaje que forman parte de la metodología (jueces de pre-etiquetado y modelos comerciales evaluados) se describen en la Sección III.

## Referencias

[1] L. Bornmann y H.-D. Daniel, "What do citation counts measure? A review of studies on citing behavior," *J. Documentation*, vol. 64, no. 1, pp. 45–80, 2008, doi: 10.1108/00220410810844150.

[2] D. Lyu, X. Ruan, J. Xie y Y. Cheng, "The classification of citing motivations: A meta-synthesis," *Scientometrics*, vol. 126, no. 4, pp. 3243–3264, 2021, doi: 10.1007/s11192-021-03908-z.

[3] A. Cohan, W. Ammar, M. van Zuylen y F. Cady, "Structural scaffolds for citation intent classification in scientific publications," en *Proc. 2019 Conf. North American Chapter of the Association for Computational Linguistics: Human Language Technologies (NAACL-HLT)*, Minneapolis, MN, EE. UU., 2019, pp. 3586–3596, doi: 10.18653/v1/N19-1361.

[4] D. Jurgens, S. Kumar, R. Hoover, D. McFarland y D. Jurafsky, "Measuring the evolution of a scientific field through citation frames," *Trans. Assoc. Comput. Linguistics*, vol. 6, pp. 391–406, 2018, doi: 10.1162/tacl_a_00028.

[5] A. Lauscher, B. Ko, B. Kuehl, S. Johnson, A. Cohan, D. Jurgens y K. Lo, "MultiCite: Modeling realistic citations requires moving beyond the single-sentence single-label setting," en *Proc. 2022 Conf. North American Chapter of the Association for Computational Linguistics: Human Language Technologies (NAACL-HLT)*, Seattle, WA, EE. UU., 2022, pp. 1875–1889, doi: 10.18653/v1/2022.naacl-main.137.

[6] I. Beltagy, K. Lo y A. Cohan, "SciBERT: A pretrained language model for scientific text," en *Proc. 2019 Conf. Empirical Methods in Natural Language Processing and 9th Int. Joint Conf. Natural Language Processing (EMNLP-IJCNLP)*, Hong Kong, China, 2019, pp. 3615–3620, doi: 10.18653/v1/D19-1371.

[7] N. Gu, Y. Gao y R. H. R. Hahnloser, "Local citation recommendation with hierarchical-attention text encoder and SciBERT-based reranking," en *Advances in Information Retrieval (ECIR 2022)*, Lecture Notes in Computer Science, Cham, Suiza: Springer International Publishing, 2022, pp. 274–288, doi: 10.1007/978-3-030-99736-6_19.

[8] P. Koloveas, S. Chatzopoulos, T. Vergoulis y C. Tryfonopoulos, "Can LLMs predict citation intent? An experimental analysis of in-context learning and fine-tuning on open LLMs," en *Linking Theory and Practice of Digital Libraries (TPDL 2025)*, Lecture Notes in Computer Science, Cham, Suiza: Springer Nature Switzerland, 2025, pp. 207–224, doi: 10.1007/978-3-032-05409-8_13.

[9] F. Gilardi, M. Alizadeh y M. Kubli, "ChatGPT outperforms crowd workers for text-annotation tasks," *Proc. Natl. Acad. Sci. U.S.A.*, vol. 120, no. 30, art. e2305016120, 2023, doi: 10.1073/pnas.2305016120.

[10] T. Saier, J. Krause y M. Färber, "unarXive 2022: All arXiv publications pre-processed for NLP, including structured full-text and citation network," en *Proc. 2023 ACM/IEEE Joint Conf. Digital Libraries (JCDL)*, 2023, pp. 66–70, doi: 10.1109/JCDL57899.2023.00020.

[11] Qwen Team, "Qwen3.8-27B," Hugging Face, 2026, rev. 1d4bf0f2ff. [En línea]. Disponible: https://huggingface.co/Qwen/Qwen3.8-27B

[12] Google DeepMind, "gemma-4-26B-A4B-it," Hugging Face, 2026, rev. 4d7ae4984b. [En línea]. Disponible: https://huggingface.co/google/gemma-4-26B-A4B-it

[13] Mistral AI, "Mistral-Small-3.2-24B-Instruct-2506," Hugging Face, 2025, rev. 95a6d26c4b. [En línea]. Disponible: https://huggingface.co/mistralai/Mistral-Small-3.2-24B-Instruct-2506

[14] J. R. Landis y G. G. Koch, "The measurement of observer agreement for categorical data," *Biometrics*, vol. 33, no. 1, pp. 159–174, 1977, doi: 10.2307/2529310.

[15] C. Bejarano, G. Rodríguez, J. Arteaga y S. Toro, "CiteScope: entrenamiento y experimentos de SciBERT," repositorio de código, GitHub, 2026, commit 58f0bb8. [En línea]. Disponible: https://github.com/germarodr/Proyecto_Grado_MAIA/tree/58f0bb8/A4/Final

[16] OpenAI, "GPT-6 Luna (gpt-6-luna)," documentación de la API de OpenAI, 2026. [En línea]. Disponible: https://developers.openai.com/api/docs/models/gpt-6-luna (consultado el 14 de noviembre de 2026).

[17] Google, "Gemini 3.5 Flash-Lite (gemini-3.5-flash-lite)," documentación de la API de Gemini, 2026. [En línea]. Disponible: https://aistudio.google.com/docs/models/gemini-3.5-flash-lite (consultado el 16 de noviembre de 2026).

[18] C. Bejarano, G. Rodríguez, J. Arteaga y S. Toro, "CiteScope: clasificación con GPT-6 Luna," notebook de Jupyter, GitHub, 2026, commit 58f0bb8. [En línea]. Disponible: https://github.com/germarodr/Proyecto_Grado_MAIA/blob/58f0bb8/A5/A5_Modelo_Comercial_G15.ipynb

[19] C. Bejarano, G. Rodríguez, J. Arteaga y S. Toro, "CiteScope: clasificación con Gemini 3.5 Flash-Lite," notebook de Jupyter, GitHub, 2026, commit 58f0bb8. [En línea]. Disponible: https://github.com/germarodr/Proyecto_Grado_MAIA/blob/58f0bb8/A5/Gemini/A5_Gemini_G15.ipynb

[20] Meta, "Llama-3.1-8B-Instruct," Hugging Face, 2024. [En línea]. Disponible: https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct

[21] Qwen Team, "Qwen2.5-7B-Instruct," Hugging Face, 2024. [En línea]. Disponible: https://huggingface.co/Qwen/Qwen2.5-7B-Instruct

[22] Mistral AI, "Mistral-7B-Instruct-v0.3," Hugging Face, 2024. [En línea]. Disponible: https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.3

[23] Mistral AI, "Ministral-3-14B-Instruct-2512," Hugging Face, 2025. [En línea]. Disponible: https://huggingface.co/mistralai/Ministral-3-14B-Instruct-2512-BF16

[24] A. Paszke *et al.*, "PyTorch: An imperative style, high-performance deep learning library," en *Advances in Neural Information Processing Systems 32 (NeurIPS 2019)*, 2019.

[25] T. Wolf *et al.*, "Transformers: State-of-the-art natural language processing," en *Proc. 2020 Conf. Empirical Methods in Natural Language Processing: System Demonstrations*, 2020, pp. 38–45, doi: 10.18653/v1/2020.emnlp-demos.6.

[26] W. Kwon *et al.*, "Efficient memory management for large language model serving with PagedAttention," en *Proc. 29th Symp. Operating Systems Principles (SOSP)*, Koblenz, Alemania, 2023, pp. 611–626, doi: 10.1145/3600006.3613165.

[27] C. Bejarano, G. Rodríguez, J. Arteaga y S. Toro, "CiteScope: demostrador y API," repositorio de código, GitHub, 2026, commit 58f0bb8. [En línea]. Disponible: https://github.com/germarodr/Proyecto_Grado_MAIA/tree/58f0bb8

[28] A. Singh, M. D'Arcy, A. Cohan, D. Downey y S. Feldman, "SciRepEval: A multi-format benchmark for scientific document representations," en *Proc. 2023 Conf. Empirical Methods in Natural Language Processing (EMNLP)*, Singapur, 2023, pp. 5548–5566, doi: 10.18653/v1/2023.emnlp-main.338.

---