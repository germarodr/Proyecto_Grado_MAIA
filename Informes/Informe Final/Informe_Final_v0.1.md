<!--
Versión de lectura del artículo para ir completando en equipo, una vez finalizada se pasa al formato IEEE.
-->

# CiteScope: Clasificación de la función de citas en Computer Science con modelos de lenguaje y recuperación semántica del artículo citado

**Camilo Bejarano, Germán Rodríguez, José Arteaga y Sebastián Toro**

> *[Instrucción de maquetación, no es texto del artículo: el siguiente párrafo va como nota al pie sin numerar en la primera columna de la página 1, según la plantilla IEEE.]*
>
> Documento recibido el 23 de noviembre de 2026. Este trabajo contó con el apoyo de la Universidad de los Andes y del grupo de investigación FLAG–TICSw del Departamento de Ingeniería de Sistemas y Computación, y con la asesoría del PhD. Juan Camilo Sanguino en la definición del problema, la orientación bibliográfica y la validación de las decisiones clave. Los autores pertenecen a la Maestría en Inteligencia Artificial (MaIA), Departamento de Ingeniería de Sistemas y Computación, Universidad de los Andes, Bogotá, Colombia. Camilo Bejarano (c.bejaranoc@uniandes.edu.co), Germán Rodríguez (gm.rodriguez@uniandes.edu.co), José Arteaga (j.arteagac@uniandes.edu.co), Sebastián Toro (s.torod@uniandes.edu.co).

**Resumen—** La cita es el principal mecanismo con el que un artículo científico se conecta con el conocimiento previo, pero en la práctica suele reducirse a un conteo que no distingue si una referencia aporta contexto, fundamenta un método, respalda una afirmación o señala una limitación. Este trabajo aborda la clasificación automática de la función de una cita en nueve categorías para artículos de Computer Science en inglés y evalúa si la evidencia recuperada del propio artículo citado mejora esa clasificación. A partir de unarXive 2022 se construyó un corpus de contextos de cita vinculados al texto completo del artículo citado; para cada par citante–citado se recuperaron con SciBERT los tres fragmentos más similares al párrafo citante. Un trío de modelos de lenguaje de pesos abiertos asignó pre-etiquetas a 38.780 instancias, y dos grupos de anotadores validaron un conjunto de prueba de 2.968 citas (κ de Cohen = 0,854). Se ajustó SciBERT con dos entradas —título y resumen del citado, frente a fragmentos recuperados— y se comparó con dos modelos de lenguaje comerciales sin ajuste, cada uno en ocho condiciones que combinan la información del citado, el tipo de prompt y el uso de ejemplos. La configuración con fragmentos obtuvo un F1 macro de [[X,XX]] frente a [[X,XX]] de la configuración base, y los modelos comerciales obtuvieron entre [[X,XX]] y [[X,XX]] según el modelo y la condición, con un costo de entre [[X]] y [[X]] USD por cada mil ejemplos. [[conclusión principal en una frase]]. A diferencia de trabajos previos, el estudio combina una taxonomía de nueve funciones en Computer Science, evidencia recuperada del texto del citado y una comparación de desempeño y costo entre un codificador ajustado y modelos comerciales; la solución se ofrece como aplicación web.

**Índice de Términos—** función de cita, modelos de lenguaje, recuperación semántica, SciBERT, unarXive.

## I. Introducción

El volumen de artículos científicos en Computer Science crece a un ritmo que dificulta seguir cómo se relacionan los trabajos entre sí. Los indicadores bibliométricos más usados se basan en el número de citas, que trata por igual una referencia que fundamenta un método y otra que solo se menciona como antecedente. Distinguir estas funciones permitiría, por ejemplo, identificar qué trabajos se usan efectivamente como base, cuáles se contrastan o cuáles se citan para señalar una limitación [1].

La función de una cita no siempre es explícita en la oración que la contiene. A menudo depende de lo que el artículo citado aporta, información que está dispersa en su texto completo y no en su título o resumen. Además, varias funciones tienen fronteras difusas —por ejemplo, entre el uso de un trabajo como base y su modificación—, lo que exige criterios de anotación consistentes.

El objetivo general de este trabajo es clasificar automáticamente la función de una cita en artículos de Computer Science en inglés, incorporando evidencia recuperada del artículo citado. Los objetivos específicos son: (i) construir un corpus que vincule contextos de cita con el texto del citado; (ii) recuperar los fragmentos del citado más relevantes para cada contexto; (iii) construir un conjunto de prueba validado por humanos para nueve funciones; (iv) comparar un clasificador ajustado con y sin fragmentos recuperados, y frente a modelos de lenguaje comerciales; y (v) desplegar la solución como aplicación web. [[ajustar al alcance final]]

La solución propuesta opera en dos etapas. Primero, para cada par formado por un artículo citante y uno citado, compara el párrafo citante con los fragmentos del texto completo del artículo citado, excluidas sus secciones de trabajos relacionados, y recupera los tres más similares; cada fragmento conserva el título de la sección de la que proviene. Después, un clasificador basado en SciBERT, ajustado con ejemplos etiquetados, asigna una de nueve funciones a partir del contexto y de esa evidencia. Para obtener los ejemplos de entrenamiento a escala, tres modelos de lenguaje de pesos abiertos propusieron pre-etiquetas que luego se validaron con anotadores humanos en un conjunto de prueba. La solución se compara con modelos de lenguaje comerciales y se ofrece como aplicación web que muestra la función predicha junto con los fragmentos que la sustentan.

Las contribuciones del trabajo son:
- Un conjunto de prueba de 2.968 citas de Computer Science con nueve funciones, validado por dos grupos de anotadores y construido con un protocolo reproducible de pre-etiquetado, calibración y adjudicación.
- Una medición controlada del aporte de los fragmentos recuperados del artículo citado a la clasificación, con las mismas instancias, partición y configuración de entrenamiento.
- Una comparación de desempeño, costo y latencia entre un codificador científico ajustado y modelos de lenguaje comerciales, y una aplicación web que muestra al usuario la función predicha junto con la evidencia del citado que la sustenta.

El resto del artículo se organiza así: la Sección II revisa el estado del arte; la Sección III describe datos, métodos y despliegue; la Sección IV presenta los resultados; la Sección V los discute, y la Sección VI concluye.

## II. Estado del arte

**Taxonomías.** Lyu et al. [1] sintetizaron 38 estudios sobre las motivaciones para citar en 13 temas: diez de motivación científica, con función retórica, y tres de motivación táctica, difíciles de detectar en el texto. Este trabajo adopta nueve de las diez científicas y excluye Assessment, la valoración positiva o negativa del citante, porque corresponde a una tarea de detección de postura.

**Conjuntos de datos.** SciCite [2] reúne 11.020 citas de computación y medicina anotadas en tres clases; su antecesor, ACL-ARC, tiene seis clases y 1.941 citas de lingüística computacional. MultiCite [3] mostró que estos esquemas simplifican el fenómeno: en 12.653 contextos de lingüística computacional, anotados por expertos con siete clases, muchas citas abarcan varias oraciones o expresan varias intenciones. Ninguno vincula cada cita con el contenido del artículo citado ni cubre las nueve funciones en Computer Science.

**Métodos.** Cohan et al. [2] alcanzaron un F1 macro de 84,0 en SciCite incorporando la estructura del artículo citante, y SciBERT [4], preentrenado con el texto completo de 1,14 millones de artículos científicos, lo elevó a 85,5 con ajuste fino. La recuperación sobre artículos científicos se ha usado sobre todo para recomendar qué citar [5]; este trabajo invierte esa dirección y, dado un par citante–citado, recupera los fragmentos del citado que ayudan a explicar por qué se cita.

**Modelos de lenguaje.** Koloveas et al. [6] adaptaron modelos de lenguaje abiertos a la intención de cita en SciCite y ACL-ARC, con aprendizaje en contexto y ajuste fino. Como anotadores, un modelo comercial superó a trabajadores de colaboración abierta con un costo unas treinta veces menor [7]. Este trabajo usa modelos abiertos como jueces para pre-etiquetar y modelos comerciales como alternativa de clasificación sin ajuste.

**TABLA I.** Comparación de trabajos relacionados con este trabajo.

| Trabajo | Clases | Dominio | Texto del citado | Modelos |
|---|---|---|---|---|
| Cohan et al. (SciCite) [2] | 3 | Computación y medicina | No | BiLSTM con ELMo |
| Lauscher et al. (MultiCite) [3] | 7, multietiqueta | Lingüística computacional | No | SciBERT, RoBERTa |
| Koloveas et al. [6] | 3 y 6 | Computación, medicina y lingüística | No | Modelos abiertos |
| Este trabajo | 9 | Computer Science (8 subcampos) | Sí | SciBERT; dos modelos comerciales |

En conjunto, los conjuntos de datos existentes tienen pocas clases o dominios acotados y clasifican la función solo con el texto citante. Ningún trabajo revisado combina las nueve funciones científicas de Lyu et al. en Computer Science, evidencia recuperada del artículo citado y una comparación de desempeño y costo entre un codificador ajustado y modelos de lenguaje comerciales (Tabla I); esa es la brecha que aborda este trabajo.

## III. Metodología

La metodología sigue el ciclo de aprendizaje automático: obtención y preparación de datos, recuperación de evidencia, construcción de etiquetas, modelado, evaluación y despliegue (Fig. 1). En cada etapa se indican las decisiones tomadas y su justificación; los resultados se presentan en la Sección IV.

**Fig. 1.** Arquitectura general de la solución: contexto de cita → recuperación Top-3 en el artículo citado → clasificador → aplicación. *Fuente: elaboración propia.* [[figura · GR]]

### A. Datos y corpus

Se utilizó unarXive 2022 [8], derivado de las fuentes LaTeX de arXiv, porque conserva el texto estructurado por secciones y párrafos y vincula las referencias bibliográficas con identificadores de arXiv, lo que permite acceder al texto completo del artículo citado. El corpus contiene 405.947 artículos con alguna categoría cs.\*; al restringir la categoría primaria a cs.\*, eess.\* o stat.ML se obtienen 358.494 artículos, y el 72,6 % de los artículos de arXiv que citan (117.194 distintos) pertenece al mismo subconjunto.

La construcción inicial tomó como artículos citantes los de cs.CV, cs.SI, cs.HC, cs.CY y cs.ET; el artículo citado podía pertenecer a cualquier subcampo disponible en el corpus. El 97,8 % de los contextos de este piloto provino de cs.CV: además de tener más artículos (59.780, frente a 7.033 o menos en los otros cuatro), el 25,8 % de sus referencias tiene identificador de arXiv, frente a entre 1,9 % y 8,2 % en los demás, y el 89,9 % de los artículos de arXiv que cita pertenece al corpus, lo que multiplica los pares citante–citado utilizables. Para aumentar el suministro de funciones escasas, el corpus se amplió con citantes de cs.LG, cs.CL y cs.DS. La Tabla II resume ambos corpus.

**TABLA II.** Corpus después de la limpieza.

| Corpus | Contextos | Artículos citantes | Artículos citados | Fragmentos |
|---|---:|---:|---:|---:|
| Piloto (cs.CV, cs.SI, cs.HC, cs.CY, cs.ET) | 1.113.513 | 50.538 | 31.532 | 1.229.408 |
| Ampliación (cs.LG, cs.CL, cs.DS) | 368.296 | 50.456 | 30.153 | 1.574.790 |

Como la ampliación se usó sobre todo para muestrear funciones escasas, la concentración se redujo poco: según la categoría principal de arXiv del artículo citante, cs.CV representa el 77,2 % de las 13.269 instancias de entrenamiento y validación y el 88,4 % de las 2.968 del conjunto de prueba, seguido de cs.LG (8,9 % y 5,8 %) y cs.DS (6,8 % y 2,4 %); los otros cinco subcampos suman 7,1 % y 3,4 %.

La limpieza eliminó fragmentos duplicados, fragmentos de menos de 15 palabras y residuos de plantillas LaTeX; los fragmentos sin sección se conservaron, porque en su mayoría son texto real de artículos cuyos encabezados no se pudieron extraer. Se exigió que el cuerpo del citado tuviera al menos 1.000 palabras, se excluyeron contextos de más de 512 tokens sin truncarlos, así como citantes en otros idiomas y autocitas del mismo identificador. Cada instancia conserva una clave estable (citante, párrafo, posición del marcador y citado) que permite reconstruir el texto exacto; esa reconstrucción se verificó en 300 de 300 casos.

El desbalance entre funciones es propio del fenómeno: la mayoría de las citas cumple una función de contexto (Background), mientras que funciones como Further Reading o Improvement/Modification son escasas. Por eso, además de lotes aleatorios, el pre-etiquetado incluyó lotes dirigidos por señales léxicas a las funciones escasas, de modo que el conjunto pre-etiquetado, del que salen el entrenamiento y la prueba, no refleja la distribución natural; la prueba, además, se muestreó con una cuota por función (Sección III-C).

### B. Segmentación y recuperación de evidencia

El texto de cada artículo citado se segmentó respetando sus secciones, en fragmentos de hasta 300 palabras y dos párrafos. Cada contexto de cita y cada fragmento se codifica con SciBERT [4] sin ajuste (`allenai/scibert_scivocab_uncased`). La representación de un texto es el promedio de los vectores de la última capa oculta sobre sus tokens reales; la máscara de atención $m_t \in \{0,1\}$ excluye el relleno:

$$\mathbf{e} = \frac{\sum_t m_t\,\mathbf{h}_t}{\sum_t m_t} \qquad (1)$$

El vector se normaliza a norma unitaria, de modo que el producto punto equivale a la similitud coseno. La segmentación ya limita cada fragmento a 512 tokens de SciBERT, por lo que solo superan ese límite, y se truncan, 138 de 1.229.408 fragmentos del piloto (0,01 %) y 252 de 1.574.790 de la ampliación (0,02 %): oraciones únicas demasiado largas para dividirse. Se prefirió el promedio al vector `[CLS]` porque, sin ajuste, este último no está entrenado como resumen del texto.

La consulta es el párrafo citante completo, sin marcar la cita objetivo. Para cada par citante–citado se toma un párrafo representativo y se seleccionan, entre los fragmentos de ese artículo citado, los tres más similares a la consulta (Top-3); cada uno conserva el título de su sección tal como aparece en el artículo citado, o queda como sección desconocida si no se pudo extraer (cerca del 1,6 % de los fragmentos). Se procesaron 721.335 pares. Como la consulta no distingue la cita objetivo, en párrafos que citan varios trabajos el Top-3 refleja el párrafo en conjunto y no solo esa cita. Se excluyeron los fragmentos de las secciones de trabajos relacionados del citado, porque describen trabajo ajeno a su aporte y aparecían sobrerrepresentados en las primeras posiciones; cuando quedaban menos de tres candidatos se conservaron los originales.

La calidad de la recuperación se verificó de dos formas. Primero, una auditoría de las secciones de origen mostró que, sin filtro, las secciones de trabajos relacionados aparecían en las primeras posiciones muy por encima de su peso en el corpus, lo que motivó excluirlas. Segundo, el aporte de los fragmentos se midió por su efecto en las decisiones: en los modelos jueces (H5) y en los clasificadores (H6 y H8). El esfuerzo de anotación humana del proyecto se concentró en validar las etiquetas del conjunto de prueba (11.880 anotaciones), por lo que la relevancia de cada fragmento no se anotó directamente; esa evaluación queda como trabajo futuro.

### C. Pre-etiquetado y validación humana

Anotar desde cero decenas de miles de citas no era viable, por lo que se usaron tres modelos de lenguaje de pesos abiertos como jueces que proponen una pre-etiqueta: Qwen3.8-27B [9], Gemma 4 26B [10] y Mistral Small 3.2 24B [11]. Cada juez recibe las definiciones y reglas de la guía, el título y resumen del citado, sus tres fragmentos con sección, el párrafo citante y la oración de la cita objetivo, y devuelve en JSON la evidencia textual, una etiqueta principal y posibles secundarias. La decodificación es determinista. Una función con al menos dos votos genera una pre-etiqueta de alta confianza; los empates quedan sin pre-etiqueta, y no votan las respuestas con JSON inválido ni las que citan evidencia ajena al párrafo citante.

La selección de jueces y del prompt se hizo sobre una muestra de desarrollo de 60 instancias, sesgada a propósito hacia casos difíciles: 20 en que los jueces confundían Further Reading con Background e Improvement/Modification con Application; 5 por cada estrato de funciones escasas identificadas por señales léxicas (Identification of the Originator, Further Reading, Evidence, Gap y Comparison), y 15 al azar de una verificación previa. El tamaño quedó limitado por la capacidad de que ambos grupos la anotaran a ciegas en una sesión, por lo que diferencias de uno o dos aciertos se consideran empates. Sus artículos citantes se excluyeron de entrenamiento y prueba.

Para la validación, los dos grupos participantes construyeron conjuntos de prueba disjuntos por instancia y artículo citante; en este trabajo se usa el propio, denominado T_B. El muestreo fue estratificado por pre-etiqueta, con semilla fija, a lo sumo dos instancias por citante y una por grupo de citas contiguas, con una meta de 300 instancias válidas por función. Cada instancia fue anotada de forma independiente por una persona de cada grupo, con la pre-etiqueta visible y sin conocer la respuesta del otro, siguiendo una guía con reglas para las fronteras más confusas. Antes de iniciar se realizaron dos calibraciones; la segunda exigió κ ≥ 0,6 en cada pareja de anotadores. Los desacuerdos se adjudicaron por una pareja que no había anotado la instancia, y las instancias sin función identificable se excluyeron (2 en T_B). La meta de 300 se cumplió en todas las funciones excepto Improvement/Modification, que quedó con 268 instancias en T_B: ambos grupos decidieron no liberar la reserva prevista para cubrir ese déficit, por la carga de anotación y el calendario. La Tabla III describe el conjunto resultante.

**TABLA III.** Conjunto de prueba T_B. Instancias: etiqueta final por función. Corrección: porcentaje de las 330 instancias muestreadas con esa pre-etiqueta cuya etiqueta final es otra.

| Función | Instancias | Corrección de la pre-etiqueta |
|---|---:|---:|
| Background | 330 | 13,9 % |
| Gap | 310 | 12,7 % |
| Basis | 322 | 13,6 % |
| Comparison | 313 | 8,2 % |
| Application | 400 | 3,3 % |
| Improvement/Modification | 268 | 25,2 % |
| Evidence | 386 | 1,5 % |
| Identification of the Originator | 324 | 3,6 % |
| Further Reading | 315 | 4,8 % |
| **Total** | **2.968** | **9,7 %** |

El acuerdo entre los dos grupos antes de adjudicar fue de 87,0 % (κ de Cohen = 0,854, que descuenta el acuerdo esperado por azar; valores sobre 0,80 se consideran acuerdo casi perfecto [12]; α de Krippendorff nominal = 0,854). Por función, el κ (una contra el resto) varió entre 0,756 en Background y 0,967 en Identification of the Originator; 386 instancias (13,0 %) requirieron adjudicación.

### D. Clasificador supervisado

Se usó la versión 2 del conjunto de entrenamiento: 32.023 instancias con pre-etiqueta de alta confianza, en las que las instancias del conjunto de prueba del otro grupo llevan su etiqueta humana en lugar de la pre-etiqueta, con autorización del Grupo 14. Para evitar fuga de información se aplicó el aislamiento más estricto por documento: se excluyeron las instancias cuyo artículo citante o citado aparece, en cualquiera de los dos papeles, en el conjunto de prueba, y las de los artículos citantes de las calibraciones, de modo que ningún documento de T_B se ve durante el entrenamiento. La partición entre entrenamiento y validación (90/10) se hizo por artículo citante con un hash fijo y, para que tampoco compartan documentos, se retiraron del entrenamiento las instancias con algún artículo presente en validación. Quedaron 11.616 instancias de entrenamiento y 1.653 de validación; 944 y 125 de ellas, respectivamente, tienen etiqueta humana y el resto conserva la pre-etiqueta. El aislamiento tiene un costo en suministro: Background pasa a ser el 43,1 % de los datos y Improvement/Modification queda con 140 instancias de entrenamiento y 19 de validación.

Se ajustó SciBERT con una capa lineal de clasificación sobre el token `[CLS]` y nueve salidas, con entropía cruzada y todos los parámetros entrenables. Se entrenaron dos modelos independientes desde el mismo punto de partida y sobre las mismas instancias, que solo difieren en la información del citado:

- **Base:** `[CLS]` contexto `[SEP]` título y resumen del citado `[SEP]`.
- **Con fragmentos:** `[CLS]` contexto `[SEP]` tres fragmentos Top-3, cada uno precedido por su sección `[SEP]`.

Como SciBERT admite 512 tokens, el contexto se limita a 192 tokens centrados en la cita objetivo y el resto se asigna al citado: hasta 64 tokens para el título en la configuración base y hasta 24 para cada encabezado de sección en la de fragmentos, recortando cada segmento desde el final y redistribuyendo el espacio no usado. La pérdida es la entropía cruzada sin pesos por clase. [[A4-4: justificación en una frase]] Los hiperparámetros de cada configuración se eligieron por separado mediante una búsqueda en rejilla sobre la tasa de aprendizaje y el decaimiento de pesos (12 ensayos en total) [[A4-3: valores de la rejilla]], y la configuración elegida se repitió con tres semillas (42, 17 y 73) para medir su estabilidad; el modelo principal es el de semilla 42 y el mejor punto de control de cada ensayo se eligió por F1 macro en validación (Tabla IV). Como la validación combina pre-etiquetas (92,4 %) y etiquetas humanas (7,6 %) y se usó para tomar estas decisiones, sus métricas son optimistas; la evaluación sin sesgo es la de T_B, que se usa una sola vez con los modelos ya congelados.

**TABLA IV.** Configuración de entrenamiento.

| Parámetro | Valor |
|---|---|
| Modelo | `allenai/scibert_scivocab_uncased` |
| Longitud máxima | 512 tokens (contexto ≤ 192) |
| Tasa de aprendizaje | 2e-5 (base) · 3e-5 (fragmentos), elegidas en validación |
| Decaimiento de pesos | 0,1 (base) · 0,01 (fragmentos), elegidos en validación |
| Épocas | Hasta 8, parada temprana con paciencia 2 |
| Lote efectivo | 32 (16 × acumulación 2) |
| Optimizador | AdamW, calentamiento 10 %, decaimiento lineal de la tasa |
| Pérdida | Entropía cruzada sin pesos por clase |
| Precisión y hardware | BF16, GPU A100 (Colab) |
| Semillas | 42 (modelo principal), 17 y 73 |

### E. Modelos de lenguaje comerciales

Se evalúan dos modelos de lenguaje comerciales: [[A5-1: nombre, proveedor y versión de cada uno, y por qué se eligieron]]. Cada modelo se evalúa sin ajuste en las mismas ocho condiciones, que combinan tres factores: la información del citado (título y resumen, como la configuración base de SciBERT, o los tres fragmentos con su sección, como la configuración con fragmentos); el prompt (genérico, con definiciones breves de las nueve funciones, o específico, que añade las reglas del prompt final de los jueces), y el uso de ejemplos (*zero-shot*, o *few-shot* con nueve ejemplos de desarrollo con etiqueta humana, uno por función). Los ejemplos no comparten instancias ni artículos citantes con el conjunto de prueba. Para que la comparación con SciBERT sea justa, en la prueba cada modelo recibe exactamente el mismo texto, ya recortado, que SciBERT en la configuración correspondiente. Cada modelo devuelve en JSON un puntaje entre 0 y 1 por función, y la predicción es la función con mayor puntaje. Una respuesta inválida se conserva como predicción fallida; solo se reintentan los errores transitorios del servicio. [[A5-2: temperatura y demás parámetros de decodificación; condición principal por tipo de información del citado, común a todos los modelos y definida antes de ver el conjunto de prueba]] Los prompts completos están en el Apéndice A.

### F. Diseño experimental

Los experimentos se formularon como hipótesis con una métrica de decisión (Tabla V). H1–H5 corresponden al desarrollo de la recuperación y del pre-etiquetado; H6 a H8 son la evaluación final sobre el conjunto de prueba.

**TABLA V.** Hipótesis y experimentos.

| | Hipótesis | Experimento | Métrica |
|---|---|---|---|
| H1 | Jueces de 24–27B superan a jueces de 7–8B | Trío Llama 3.1 8B, Qwen 2.5 7B y Mistral 7B frente al trío final | Aciertos en los 41 casos de desarrollo con acuerdo humano |
| H2 | El tercer juez afecta la calidad del trío, sobre todo en Gap | Mistral Small 3.2 24B frente a Ministral 3 14B | Aciertos en la muestra de desarrollo; precisión en 20 Gap nuevos |
| H3 | Incorporar reglas de adjudicación al prompt mejora el pre-etiquetado | Cuatro versiones sucesivas del prompt | Aciertos en la muestra de desarrollo |
| H4 | Sin filtro, las secciones de trabajos relacionados dominan las primeras posiciones de la recuperación | Auditoría de las secciones del Top-1 con y sin filtro | Peso de esas secciones entre los candidatos frente al Top-1 |
| H5 | Los fragmentos mejoran las decisiones de los jueces | Ablación con y sin fragmentos | Aciertos en la muestra de desarrollo; cambios en 885 casos difíciles |
| H6 | El clasificador con fragmentos supera al clasificador base | Dos ajustes de SciBERT con las mismas instancias | Diferencia de F1 macro con intervalo bootstrap pareado por citante |
| H7 | Los modelos comerciales sin ajuste no superan a SciBERT ajustado y cuestan más | Ocho condiciones de cada modelo comercial frente a SciBERT con la misma información del citado | F1 macro con IC *bootstrap* pareado; costo por mil ejemplos; latencia |
| H8 | Los fragmentos también mejoran a los modelos comerciales | Condiciones con fragmentos frente a las mismas condiciones con título y resumen | Diferencia de F1 macro |

### G. Métricas

Se reportan precisión, exhaustividad y F1 por función, sus promedios macro y micro, y matrices de confusión. El F1 macro es la métrica principal porque pondera igual a todas las funciones, incluidas las escasas:

$$F1_{macro} = \frac{1}{K}\sum_{k=1}^{K}\frac{2P_kR_k}{P_k+R_k} \qquad (2)$$

La diferencia entre las dos configuraciones de SciBERT se acompaña de un intervalo de confianza del 95 % obtenido por *bootstrap* pareado por artículo citante. La eficiencia se mide con el costo (horas de GPU o tokens facturados), la latencia por ejemplo y la tasa de respuestas con formato inválido.

### H. Despliegue

[[D-1: arquitectura en AWS, servicios, dónde corre cada modelo y cómo se invocan los modelos comerciales]]

**Fig. 2.** Arquitectura de despliegue. *Fuente: elaboración propia.* [[D-1]]

[[D-2: backend FastAPI [13], endpoints, carga de modelos, modelo de pesos abiertos elegido]] [[D-3: frontend Next.js [14]; el usuario ingresa un contexto de cita, ve los fragmentos recuperados, elige un clasificador y obtiene la función predicha]]

El desarrollo usó Python, PyTorch [15], Transformers [16], vLLM [17] y scikit-learn [18]; los datos se versionaron con DVC [19] y los experimentos se registraron en MLflow [20]. El entrenamiento se ejecutó en Colab con GPU A100.

## IV. Resultados

### A. Recuperación, pre-etiquetado y validación humana (H1–H5)

La Tabla VI consolida los indicadores de las etapas de construcción. Las cifras sobre la muestra de 60 instancias son de desarrollo y no constituyen una evaluación final.

**TABLA VI.** Indicadores por etapa.

| Etapa | Indicador | Valor | H |
|---|---|---|---|
| Recuperación | Coseno medio Top-1 (piloto / ampliación) | 0,915 / 0,913 | — |
| | Brecha mediana entre Top-1 y Top-3 | 0,013 | — |
| | Trabajos relacionados: % de candidatos frente a % de Top-1 sin filtro | 8,6 % frente a 31,6 % | H4 |
| | Pares con algún fragmento de trabajos relacionados en el Top-3 sin filtro | 51,9 % | H4 |
| Pre-etiquetado (desarrollo) | Trío 7–8B frente a trío final (41 casos) | 13 frente a 30 | H1 |
| | Tercer juez: Mistral Small frente a Ministral (60 casos; 20 Gap) | 48 frente a 45; 17 frente a 12 | H2 |
| | Versiones del prompt (60 casos) | 43 → 47 → **48** → 47 | H3 |
| | Sin fragmentos frente a con fragmentos (60 casos) | 49 frente a 48 | H5 |
| Pre-etiquetado (producción) | κ de Fleiss entre jueces; unanimidad | 0,67; 63 % | — |
| | Instancias con pre-etiqueta de alta confianza | 37.254 de 38.780 (96,1 %) | — |
| | Estabilidad al repetir 300 instancias | 98 % | — |
| Validación humana | κ de Fleiss: primera frente a segunda calibración | 0,47 frente a 0,87 | — |
| | Corrección de la pre-etiqueta en T_B | 9,7 % (25,2 % en Improvement/Modification) | — |
| | κ de Cohen / α de Krippendorff en T_B | 0,854 / 0,854 | — |

Los jueces de mayor tamaño superaron con claridad a los pequeños (H1), y la versión final del prompt alcanzó 48 de 60 aciertos (H3); las diferencias entre terceros jueces y entre versiones vecinas del prompt son de pocos casos y deben leerse como empates (H2). Los fragmentos no mejoraron netamente las decisiones de los jueces: de 45 cambios en 885 casos difíciles, 16 fueron mejores con fragmentos, 18 sin ellos y 11 equivalentes (H5). Las similitudes coseno son altas y muy comprimidas, comportamiento típico de promedios de BERT sin ajuste; ordenan candidatos pero no prueban su relevancia. La auditoría de secciones respalda H4: sin filtro, los trabajos relacionados ocupaban el 31,6 % de las primeras posiciones siendo el 8,6 % de los candidatos, y aparecían en el Top-3 del 51,9 % de los pares; con el filtro, la introducción del artículo citado pasa a ser la sección más frecuente en la primera posición (46,8 %). En la validación humana, la etiqueta final coincidió con la pre-etiqueta en el 90,3 % de las instancias de T_B: en el 94,6 % cuando los tres jueces votaron igual y en el 82,2 % cuando votaron 2 de 3, de modo que la unanimidad de los jueces es una señal útil de confiabilidad. Improvement/Modification concentró las correcciones (25,2 %), sobre todo hacia Basis y Application.

### B. Desempeño de clasificación (H6–H8)

**TABLA VII.** Resultados sobre el conjunto de prueba T_B. Las ocho condiciones de cada modelo comercial están en la TABLA X (Apéndice C). [[A4-2, A5-3; consolida GR en A6]]

| Modelo | Precisión macro | Exhaustividad macro | F1 macro | F1 micro |
|---|---:|---:|---:|---:|
| SciBERT base | [[ ]] | [[ ]] | [[ ]] | [[ ]] |
| SciBERT con fragmentos | [[ ]] | [[ ]] | [[ ]] | [[ ]] |
| [[A5-1: modelo 1]] · título y resumen (condición principal) | [[ ]] | [[ ]] | [[ ]] | [[ ]] |
| [[A5-1: modelo 1]] · fragmentos (condición principal) | [[ ]] | [[ ]] | [[ ]] | [[ ]] |
| [[A5-1: modelo 2]] · título y resumen (condición principal) | [[ ]] | [[ ]] | [[ ]] | [[ ]] |
| [[A5-1: modelo 2]] · fragmentos (condición principal) | [[ ]] | [[ ]] | [[ ]] | [[ ]] |

[[A4-2: diferencia de F1 macro entre fragmentos y base con IC 95 %; media y desviación del F1 macro de las tres semillas.]]

[[Fig. 3 · gráfica de barras agrupadas: F1 por función (eje x, nueve funciones) para SciBERT base, SciBERT con fragmentos y la condición principal de cada modelo comercial con cada tipo de información del citado, con una línea horizontal en el F1 macro de cada uno; consolida GR en A6]]

**Fig. 3.** F1 por función de SciBERT y de los modelos comerciales sobre el conjunto de prueba. *Fuente: elaboración propia.*

**Fig. 4.** Matrices de confusión de SciBERT con fragmentos y de la condición principal con fragmentos de cada modelo comercial. *Fuente: elaboración propia.* [[ ]]

[[Funciones más confundidas y lectura de H6, H7 y H8.]]

### C. Eficiencia, latencia y costo (H7)

**TABLA VIII.** Costo y latencia por modelo. Las ocho condiciones de cada modelo comercial están en la TABLA X (Apéndice C). [[A7-1, A7-2, A5-3, A7-3]]

| Modelo | Entrenamiento | Costo por 1.000 ejemplos | Latencia (s/ejemplo) | Formato inválido |
|---|---:|---:|---:|---:|
| SciBERT base | [[h GPU]] | [[ ]] | [[ ]] | — |
| SciBERT con fragmentos | [[h GPU]] | [[ ]] | [[ ]] | — |
| [[A5-1: modelo 1]] · título y resumen (condición principal) | — | [[ ]] | [[ ]] | [[ ]] |
| [[A5-1: modelo 1]] · fragmentos (condición principal) | — | [[ ]] | [[ ]] | [[ ]] |
| [[A5-1: modelo 2]] · título y resumen (condición principal) | — | [[ ]] | [[ ]] | [[ ]] |
| [[A5-1: modelo 2]] · fragmentos (condición principal) | — | [[ ]] | [[ ]] | [[ ]] |

### D. Análisis cualitativo y aplicación

[[A4-5, A5-4: errores representativos; contexto, etiqueta de referencia, predicción y causa.]]

**Fig. 5.** Aplicación desplegada con un ejemplo real. *Fuente: elaboración propia.* [[D-3]]

### E. Comparación con trabajos previos y análisis crítico

[[TABLA IX o párrafo: F1 macro de este trabajo frente a los resultados publicados de SciCite y MultiCite, indicando para cada uno número de clases, dominio y si usa texto del citado, porque las cifras no son directamente comparables.]]

[[Análisis crítico de los resultados: qué tan robustos son (intervalos, variación entre semillas, sesgo por muestreo de alta confianza y pre-etiqueta visible), qué hipótesis quedan respaldadas y cuáles no.]]

## V. Discusión

[[Respuesta a H1–H8, una frase cada una: aceptada, rechazada o no concluyente.]]

[[Aporte de los fragmentos: contrastar H5 (sin mejora neta en los jueces) con H6 en el clasificador. La entrada con fragmentos recorta evidencia del citado en cerca del 91 % de las instancias por el límite de 512 tokens, frente a un 5 % en la configuración base.]]

[[Codificador frente a modelos comerciales: desempeño y costo; diferencias entre los modelos comerciales; si los fragmentos ayudan también a esos modelos (H8).]]

**Fortalezas.** El conjunto de prueba se construyó con un protocolo reproducible: muestreo estratificado con semilla fija, guía de anotación con reglas para las fronteras más confusas, calibración previa con un umbral de acuerdo por pareja y adjudicación de desacuerdos por anotadores independientes. Las dos configuraciones de SciBERT se compararon de forma controlada, con las mismas instancias y partición, hiperparámetros elegidos con la misma búsqueda y tres semillas, de modo que la diferencia entre ellas se atribuye a la información del citado. El aislamiento por documento garantiza que ningún artículo del conjunto de prueba se vio durante el entrenamiento. La evaluación incluye costo y latencia, y no solo desempeño, lo que permite juzgar la viabilidad práctica de cada alternativa. Cada instancia conserva una clave que permite reconstruir su texto exacto y reproducir el pre-etiquetado y la recuperación.

**Limitaciones.** El corpus está concentrado en cs.CV (77 % de las instancias de entrenamiento y 88 % de las de prueba), por lo que los resultados no describen de manera uniforme todo Computer Science. Tres funciones quedaron por debajo de la meta de 2.000 ejemplos, e Improvement/Modification quedó por debajo de la meta de 300 instancias en el conjunto de prueba (268), lo que amplía la incertidumbre de su F1. El conjunto de prueba se muestreó entre instancias con pre-etiqueta de alta confianza y se anotó con la pre-etiqueta visible, lo que puede favorecer tanto el F1 como el acuerdo (sin los dos anotadores que menos corrigieron la pre-etiqueta, el κ en T_B baja de 0,854 a 0,840); la mejora del acuerdo entre calibraciones no puede atribuirse a una sola intervención, porque cambiaron a la vez la muestra, las reglas y la modalidad. La muestra de desarrollo es pequeña y sesgada a casos difíciles. La recuperación usa SciBERT sin ajuste y la entrada con fragmentos se trunca. La relevancia de los fragmentos recuperados no se evaluó con anotadores; su utilidad se infiere de la auditoría de secciones y de su efecto en las decisiones de los jueces y de los clasificadores. El aislamiento estricto por documento reduce el entrenamiento a 11.616 instancias y deja muy pocas de las funciones escasas (140 de Improvement/Modification). Las métricas de validación se calculan sobre pre-etiquetas en su mayoría y se usaron para elegir hiperparámetros, por lo que solo T_B ofrece una estimación sin sesgo.

## VI. Conclusiones y trabajo futuro

[[Hallazgos clave en tres o cuatro frases y contribuciones.]]

**Aplicaciones prácticas.** La clasificación de la función de las citas, acompañada de la evidencia del citado, puede apoyar revisiones sistemáticas de literatura, al identificar qué trabajos se usan como base o se contrastan; estudios bibliométricos que distingan el tipo de influencia entre trabajos y no solo su número de citas, y herramientas de asistencia a la escritura académica que sugieran o verifiquen cómo se cita una fuente.

**Lecciones aprendidas.** [[Tres o cuatro lecciones (GR, con aportes del equipo). Candidatas: los modelos de lenguaje como jueces permiten pre-etiquetar a escala, pero requieren validación humana por función; calibrar a los anotadores antes de anotar fue decisivo para alcanzar un acuerdo aceptable; el límite de 512 tokens condiciona cuánta evidencia del citado puede usar un codificador; coordinar dos grupos exige un contrato de datos con identificadores estables y reglas de exclusión explícitas.]]

Como trabajo futuro se plantea evaluar con anotadores la relevancia de los fragmentos recuperados mediante precisión en 3 (P@3), frente a una línea base aleatoria; reemplazar la recuperación por un modelo ajustado para similitud entre documentos científicos, como SPECTER2 [21]; usar modelos de contexto largo para no truncar los fragmentos; extender la clasificación a múltiples etiquetas, y ampliar el suministro de las funciones escasas.

## Apéndices

**Apéndice A.** Prompts genérico y específico de los modelos comerciales y formato de los ejemplos *few-shot*. [[A5-2]]

**Apéndice B.** Repositorios y aplicación desplegada: [[D-5]]

**Apéndice C.** **TABLA X.** Precisión, exhaustividad, F1 macro y micro, costo por 1.000 ejemplos, latencia y tasa de respuestas inválidas de las ocho condiciones de cada modelo comercial sobre T_B. [[A5-3, A6, A7]]

## Declaración de uso de IA

Los autores usaron asistentes de inteligencia artificial generativa como apoyo en la escritura y depuración de código, en la búsqueda y organización de información y en la revisión de la redacción de este documento. Los autores revisaron y verificaron todo el contenido y asumen la responsabilidad por él. Los modelos de lenguaje que forman parte de la metodología (jueces de pre-etiquetado y modelos comerciales evaluados) se describen en la Sección III.

## Referencias

[1] D. Lyu, X. Ruan, J. Xie y Y. Cheng, "The classification of citing motivations: A meta-synthesis," *Scientometrics*, vol. 126, no. 4, pp. 3243–3264, 2021, doi: 10.1007/s11192-021-03908-z.

[2] A. Cohan, W. Ammar, M. van Zuylen y F. Cady, "Structural scaffolds for citation intent classification in scientific publications," en *Proc. 2019 Conf. North American Chapter of the Association for Computational Linguistics: Human Language Technologies (NAACL-HLT)*, Minneapolis, MN, EE. UU., 2019, pp. 3586–3596, doi: 10.18653/v1/N19-1361.

[3] A. Lauscher, B. Ko, B. Kuehl, S. Johnson, A. Cohan, D. Jurgens y K. Lo, "MultiCite: Modeling realistic citations requires moving beyond the single-sentence single-label setting," en *Proc. 2022 Conf. North American Chapter of the Association for Computational Linguistics: Human Language Technologies (NAACL-HLT)*, Seattle, WA, EE. UU., 2022, pp. 1875–1889, doi: 10.18653/v1/2022.naacl-main.137.

[4] I. Beltagy, K. Lo y A. Cohan, "SciBERT: A pretrained language model for scientific text," en *Proc. 2019 Conf. Empirical Methods in Natural Language Processing and 9th Int. Joint Conf. Natural Language Processing (EMNLP-IJCNLP)*, Hong Kong, China, 2019, pp. 3615–3620, doi: 10.18653/v1/D19-1371.

[5] N. Gu, Y. Gao y R. H. R. Hahnloser, "Local citation recommendation with hierarchical-attention text encoder and SciBERT-based reranking," en *Advances in Information Retrieval (ECIR 2022)*, Lecture Notes in Computer Science, Cham, Suiza: Springer International Publishing, 2022, pp. 274–288, doi: 10.1007/978-3-030-99736-6_19.

[6] P. Koloveas, S. Chatzopoulos, T. Vergoulis y C. Tryfonopoulos, "Can LLMs predict citation intent? An experimental analysis of in-context learning and fine-tuning on open LLMs," en *Linking Theory and Practice of Digital Libraries (TPDL 2025)*, Lecture Notes in Computer Science, Cham, Suiza: Springer Nature Switzerland, 2025, pp. 207–224, doi: 10.1007/978-3-032-05409-8_13.

[7] F. Gilardi, M. Alizadeh y M. Kubli, "ChatGPT outperforms crowd workers for text-annotation tasks," *Proc. Natl. Acad. Sci. U.S.A.*, vol. 120, no. 30, art. e2305016120, 2023, doi: 10.1073/pnas.2305016120.

[8] T. Saier, J. Krause y M. Färber, "unarXive 2022: All arXiv publications pre-processed for NLP, including structured full-text and citation network," en *Proc. 2023 ACM/IEEE Joint Conf. Digital Libraries (JCDL)*, 2023, pp. 66–70, doi: 10.1109/JCDL57899.2023.00020.

[9] Qwen Team, "Qwen3.8-27B," Hugging Face, 2026, rev. 1d4bf0f2ff. [En línea]. Disponible: https://huggingface.co/Qwen/Qwen3.8-27B

[10] Google DeepMind, "gemma-4-26B-A4B-it," Hugging Face, 2026, rev. 4d7ae4984b. [En línea]. Disponible: https://huggingface.co/google/gemma-4-26B-A4B-it

[11] Mistral AI, "Mistral-Small-3.2-24B-Instruct-2506," Hugging Face, 2025, rev. 95a6d26c4b. [En línea]. Disponible: https://huggingface.co/mistralai/Mistral-Small-3.2-24B-Instruct-2506

[12] J. R. Landis y G. G. Koch, "The measurement of observer agreement for categorical data," *Biometrics*, vol. 33, no. 1, pp. 159–174, 1977, doi: 10.2307/2529310.

[13] S. Ramírez, "FastAPI," software. [En línea]. Disponible: https://fastapi.tiangolo.com

[14] Vercel, "Next.js," software. [En línea]. Disponible: https://nextjs.org

[15] A. Paszke *et al.*, "PyTorch: An imperative style, high-performance deep learning library," en *Advances in Neural Information Processing Systems 32 (NeurIPS 2019)*, 2019.

[16] T. Wolf *et al.*, "Transformers: State-of-the-art natural language processing," en *Proc. 2020 Conf. Empirical Methods in Natural Language Processing: System Demonstrations*, 2020, pp. 38–45, doi: 10.18653/v1/2020.emnlp-demos.6.

[17] W. Kwon *et al.*, "Efficient memory management for large language model serving with PagedAttention," en *Proc. 29th Symp. Operating Systems Principles (SOSP)*, Koblenz, Alemania, 2023, pp. 611–626, doi: 10.1145/3600006.3613165.

[18] F. Pedregosa *et al.*, "Scikit-learn: Machine learning in Python," *J. Mach. Learn. Res.*, vol. 12, pp. 2825–2830, 2011.

[19] "DVC: Data Version Control," software. [En línea]. Disponible: https://dvc.org

[20] M. Zaharia *et al.*, "Accelerating the machine learning lifecycle with MLflow," *IEEE Data Eng. Bull.*, vol. 41, no. 4, pp. 39–45, 2018.

[21] A. Singh, M. D'Arcy, A. Cohan, D. Downey y S. Feldman, "SciRepEval: A multi-format benchmark for scientific document representations," en *Proc. 2023 Conf. Empirical Methods in Natural Language Processing (EMNLP)*, Singapur, 2023, pp. 5548–5566, doi: 10.18653/v1/2023.emnlp-main.338.
