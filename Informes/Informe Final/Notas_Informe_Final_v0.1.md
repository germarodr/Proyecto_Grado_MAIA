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
| L6 | Faltó la evaluación humana de P@3 | Ejecutarla; si no, limitación explícita | III-B, IV-A, V | **No se hace (10-nov):** se declara como limitación y trabajo futuro; H4 se responde con la auditoría de secciones |
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
| Conjunto de datos construido | "Dataset" (preferencia de GR, 11-nov); "conjunto de prueba" sigue para T_B |
| Columnas de la TABLA III | En inglés por preferencia de GR: Dataset, Excluded, Training, Validation, Test B, Correction |
| calib30, calib2 | "Primera y segunda calibración" |
| `norw` | "Exclusión de secciones de trabajos relacionados" |
| pool_v11.1, conjunto ampliado | "Conjunto pre-etiquetado" (38.780) |
| pool_cue_yield | No se menciona; "885 casos difíciles" |
| prompt v8/v11/v11.1/v12 | "Versiones sucesivas del prompt"; v11.1 = "versión final" |
| jueces | "Modelos de lenguaje de pesos abiertos usados como jueces" (definido en III-C) |
| T_A / T_B | **T_B = "Test"** (definido en III-C; primera mención en Resumen e Introducción como "conjunto de prueba (Test)"). **T_A = T_A**: en el artículo solo aparece como "el conjunto de prueba del otro grupo" |
| Particiones | **Training, Validation y Test** en inglés (preferencia de GR, 11-nov). Siguen en español "validación humana" (la anotación de A3), el proceso de "entrenamiento" (p. ej., "configuración de entrenamiento") y los verbos ("validaron") |
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
| 09-nov | **Nuevo hallazgo de A5** (commit 30d1592): el modelo comercial se evalúa en 8 condiciones (información del citado × prompt × ejemplos) con las mismas entradas recortadas de SciBERT. Ajustes: el artículo actualiza el resumen, III-E, la H7, agrega la **H8** (¿los fragmentos ayudan también al modelo comercial?), las TABLAS VII y VIII pasan a 8 filas del modelo comercial, las Figs. 3 y 4 usan la condición principal definida antes de ver el conjunto de prueba, y cambia el Apéndice A. Las solicitudes actualizan A5 y A6 y agregan **A4-6** (exportar las entradas de SciBERT para A5). El plan de trabajo se alinea | GR |
| 09-nov | **Cierre de A3** (PR #14 de `Proyecto_LCR_CF` y contrato del 9-nov): las etiquetas finales y las métricas están publicadas, así que A3-1 deja de ser solicitud y lo descarga GR. Se agregan al artículo los 2 `unclear` de T_B y el déficit de Improvement/Modification (268 < 300), en III-C y en Limitaciones. A4-3 pide la versión del entrenamiento (1 o 2, opcional según el contrato) y si se usaron las etiquetas humanas de T_A | GR |
| 09-nov | **Insumos de A3 recibidos** (ZIP de Drive en `Insumos/`). Con las cifras verificadas se llenan la TABLA III, el resumen, las contribuciones, la TABLA VI y el párrafo de acuerdo de III-C, y se agrega a Limitaciones el análisis de sensibilidad (κ 0,840 sin los dos anotadores que menos corrigieron). Los ZIP quedan fuera de git: la carpeta del equipo está en `.gitignore` | GR |
| 10-nov | Solicitudes depuradas con lo recibido: A4-3 ya no pide las filas recuperadas de la versión 2 (vienen en `manifest_training_v2_G15.json`) y A7-3 habla de las ocho condiciones. A1-2 sigue vigente porque los archivos recibidos no traen la categoría arXiv del artículo citante | GR |
| 10-nov | Se revisan A1-1 a A1-4: siguen vigentes porque no hay respuesta documentada. Se corrige III-A: la concentración en cs.CV no se debe solo al volumen, sino a que el 25,8 % de sus referencias tiene ID de arXiv (frente a 1,9–8,2 % en los demás) y el 89,9 % se resuelve en el corpus (`Proyecto_LCR_CF/docs/script_outputs/inspect_cs_subset_core_01_09_26_results.md`) | GR |
| 10-nov | **A1-1 se cierra:** el evaluador pidió la razón de selección "de existir", y la concentración en cs.CV ya está explicada con datos. Se quita la solicitud y el hueco de III-A. Se conserva la numeración A1-2 a A1-4 | GR |
| 10-nov | **Doble validación de A1.** A1-3 resuelto con los EDA oficiales de `Proyecto_LCR_CF` (138 fragmentos de 1.229.408 y 252 de 1.574.790 superan 512 tokens). A1-2 resuelto con la categoría principal de arXiv de los 24.737 citantes (100 % dentro de las 8 categorías esperadas): **la concentración en cs.CV casi no baja (86,2 % en entrenamiento, 88,4 % en T_B)**, así que III-A ya no dice que la ampliación buscaba reducirla y Limitaciones da la cifra. A1-4 (P@3) sigue pendiente: no existe y requiere anotación humana. `Proyecto_LCR_CF` local se actualizó (*fast-forward*) | GR |
| 10-nov | Readme de `Proyecto_LCR_CF` actualizado por Alejandra (commit 19715eb): confirma las cifras de A3 ya incorporadas, sin cambios en el artículo. Commit 741a15f: `a8_index.py`, índice de la demo con licencias permisivas, registrado como evidencia parcial de D-2 | GR |
| 10-nov | **Revisión de A1–A3 del artículo contra el repositorio actualizado y Drive:** de 29 afirmaciones, 26 confirmadas con fuente primaria (readme, registros de los scripts, EDA, `a1_score_stats.md`, contrato del 9-nov, `iaa_report.md`, `test_set_gold.jsonl`). Se corrigen 2 errores heredados del primer informe ("segmentos sin sección" y "el entrenamiento conserva la distribución natural") y la definición del 72,6 % y el 89,9 %. Se redacta la lectura de la validación humana en IV-A (90,3 % de coincidencia en T_B; 94,6 % con jueces unánimes frente a 82,2 % con 2 de 3; las correcciones de Improvement/Modification van sobre todo a Basis y Application, 33 y 33). Único pendiente de A1–A3: el P@3 (A1-4) | GR |
| 10-nov | **Corrección:** III-B afirmaba en pasado que el P@3 "se evaluó", y nunca se hizo (GR fue anotador y no lo hizo; no hay rastro en ningún repositorio). El párrafo pasa a ser un hueco explícito de decisión y se quita "que se valora con el P@3" de IV-A. Lo que sí existe sobre la utilidad de los fragmentos: la auditoría de secciones (filtro de trabajos relacionados), la ablación con los jueces (H5) y la regla de la guía de A3 según la cual los fragmentos solo verifican la función | GR |
| 10-nov | **P@3 descartado (opción 2):** no se hace. Para una respuesta honesta y no negativa, III-B describe las verificaciones que sí se hicieron y que la anotación humana se concentró en las etiquetas; H4 pasa a "sin filtro, las secciones de trabajos relacionados dominan las primeras posiciones", medida con la auditoría; la TABLA VI cambia la fila del P@3 por el 51,9 % de pares con trabajos relacionados en el Top-3; IV-A agrega la lectura de H4; Limitaciones y trabajo futuro mencionan el P@3. **A1 queda cerrado:** sin solicitudes pendientes | GR |
| 10-nov | **Paso a Word: GR lo hace a mano** sobre `Formato-IEEE.doc`, revisando el texto al mismo tiempo. Encabezado de página: título corto "Clasificación de la función de citas con modelos de lenguaje y recuperación semántica" más el número de página (reemplaza el marcador del identificador de manuscrito IEEE) | GR |
| 10-nov | **Precisión sobre la recuperación** (verificado en `top3_retrieval.py` y en los comandos de producción de A1, `--one-per-pair` sin `--window-words`): la consulta es el párrafo citante completo, sin marcar la cita objetivo; se hace una vez por par citante–citado con un párrafo representativo; se ordenan solo los fragmentos de ese citado, sin los de trabajos relacionados. Se corrige la Introducción (solución en dos etapas) y III-B, y se agrega la consecuencia: en párrafos con varias citas el Top-3 refleja el párrafo en conjunto. **El título y el resumen no se recuperan por similitud, se consultan en los metadatos de unarXive**; el artículo ya lo dice bien | GR |
| 10-nov | La sección **no se recupera**: es un atributo de cada fragmento heredado del párrafo de unarXive (`chunk_dataset.py`) e incluido en la salida del Top-3 (`top3_retrieval.py`). Es el encabezado tal como aparece en el artículo, no una categoría normalizada, y puede venir vacío (≈1,6 % de los fragmentos, `clean_dataset.py`). Se ajustan la Introducción y III-B | GR |
| 10-nov | **Al menos dos modelos comerciales** (indicación de GR). Artículo: resumen, Introducción, II, III-E, H7, H8, Fig. 2–4, Discusión y Apéndice A en plural. Para cuidar el espacio, las TABLAS VII y VIII muestran por cada modelo solo la condición principal de cada tipo de información (6 filas en total) y se agrega el **Apéndice C (TABLA X)** con las 8 condiciones de cada modelo. Si IV-E usa una tabla, esa sería la IX y la del apéndice la X; si usa un párrafo, la del apéndice pasa a ser la IX. La condición principal es común a todos los modelos y se fija antes de ver T_B. Solicitudes: A5-1 por modelo, A5-3 con columna `modelo`, A5-4 con dos ejemplos por modelo, A7-3 por proveedor. **El resumen quedó en 299 palabras (límite 300)** | GR |
| 10-nov | **Se fija: dos modelos comerciales** (antes "al menos dos"). Resumen revisado con los ajustes de GR (286 palabras → 289): "par citante–citado", la consulta es el párrafo citante y el costo en USD. III-E, solicitudes y plan dicen "dos" | GR |
| 10-nov | **Sección II redactada** (≈760 palabras con la TABLA I; presupuesto ≈1 página). Datos verificados en los PDF de `Papers/`: Lyu (38 estudios, 13 temas, 10 científicos + 3 tácticos; se excluye Assessment por ser detección de postura, según la guía rev3.1 l. 47); SciCite (11.020 citas, 6.627 artículos, 3 clases, computación y medicina, colaboración abierta; F1 macro 84,0 en SciCite y 67,9 en ACL-ARC); ACL-ARC (6 clases, 1.941 citas, lingüística computacional); MultiCite (12.653 contextos, 1.200 artículos, 7 clases, 17,1 % multioración, 19,3 % varias intenciones; SciBERT y RoBERTa); SciBERT (1,14 M artículos, 18 % computación y 82 % biomédicos; 85,49 de F1 macro en SciCite con ajuste fino). Por resumen oficial: Koloveas (arXiv) y Gilardi (Crossref) | GR |
| 10-nov | Sección II resumida de ≈760 a ≈445 palabras (≈1 página con la TABLA I): sin párrafo de entrada; MultiCite sin porcentajes; SciBERT sin la composición del corpus; Koloveas y Gilardi en una frase cada uno; TABLA I con celdas más cortas | GR |
| 10-nov | TABLA I: filas nombradas por autor y conjunto de datos (Cohan et al. (SciCite) [4], Lauscher et al. (MultiCite) [5]) para coincidir con el texto de la Sección II | GR |
| 10-nov | Tablas como imágenes: `Insumos/generar_tablas.py` lee las tablas del .md y genera `Insumos/tablas/TABLA_N.png` (Times New Roman 8 pt, solo líneas horizontales, 600 ppp; una columna 8,9 cm si cabe con ≤3 líneas por celda, si no doble columna; celdas con `[[…]]` resaltadas). La leyenda se escribe en Word. Regenerar tras cada cambio de tablas: `.venv/bin/python "Informes/Informe Final/Insumos/generar_tablas.py"` | GR |
| 10-nov | Solicitudes reescritas para la reunión del equipo: sección 0 con 9 decisiones (P@3, los dos modelos comerciales, condición principal, desbalance, datos de entrenamiento, app web, publicar a3/, entrega privada de A4-6, responsables y fecha del 17-nov); A4–A7 y D en tablas compactas (1.578 → 1.111 palabras). Respaldo de la versión anterior en la carpeta de la sesión | GR |
| 10-nov | Solicitudes: resumen del dataset del G15 frente a la sección 3 del documento del proyecto. Conteos recalculados de `training_v1_G15.jsonl` (ZIP de Drive) con el hash `G15-A4-split-v1` (reproduce 28.039/3.226) y de `test_set_gold.jsonl`. Totales por función (entrenamiento + validación + T_B): Bg 12.544, Gap 3.117, Basis 2.928, Comp 3.470, App 4.643, IM 813, Evid 3.413, Orig 1.636, FR 1.669. Validación humana: 5.940/38.780 = 15,3 % en conjunto; T_B = 8,7 % del dataset del G15. Fuga: 0 citantes y 0 pares compartidos; 82,9 % de T_B con citado visto | GR |
| 10-nov | Supuesto: el G14 no comparte su dataset. T_A queda en el entrenamiento del G15 con pre-etiquetas (sin la opción de usar sus etiquetas humanas); validación humana disponible para el G15 = T_B (8,7 %); `Insumos/a3/` se agrega a `.gitignore` y no se publica. Se quita esa opción del hueco A4-3 en III-D | GR |
| 10-nov | Solicitudes, A6: sin nombrar el script; se describe qué calcula A6 y sus prerrequisitos. Verificado en `A4/crear_notebook.py` (`report_predictions`) y en la corrida 1: ya existen `base/validation_predictions.csv` (columnas `predicted_label`, `p_<función>`) y `validation_classification_report.json` en Drive. A6-1 no tiene prerrequisitos; A6-2 requiere A4-2 y A5-3. **Discrepancia por resolver:** la salida de la corrida 1 muestra un F1 macro de validación de 0,8478 (precisión macro 0,8560, exhaustividad macro 0,8436, F1 micro 0,8661), mientras §8 dice 0,846; A6-1 debe confirmar cuál es el valor | GR |
| 11-nov | **Se revierte el supuesto del 10-nov:** el G14 autorizó usar sus datos (T_A con etiqueta humana) para entrenar y validar el modelo del G15. Recalculado con `G15-A4-split-v1`: 28.036/3.226 (3 *unclear* descartados), 221 de 2.967 etiquetas cambian; por función (entrenamiento/validación): Bg 10.961/1.259, Gap 2.514/284, Basis 2.349/260, Comp 2.818/317, App 3.803/475, IM 454/51, Evid 2.756/311, Orig 1.171/137, FR 1.210/132. Se restaura la opción en el hueco A4-3; `Insumos/a3/` sigue sin publicarse (autorización para usar, no para publicar) | GR |
| 11-nov | **Cruce con A4 (commit 8aec590, ST).** Corridas 1–5, todas solo en validación con pre-etiquetas, T_B cerrado, FP32: (1–3) V0 base F1 macro 0,847831 (P 0,856048, R 0,843588, micro 0,866088) y fragmentos 0,839801 (P 0,844786, R 0,837941, micro 0,858648); el 0,846065 es el F1 del Trainer en BF16 (se resuelve la discrepancia del 10-nov: se reporta FP32). (4) Top-1: F1 0,844525; recorte de evidencia de 90,92 % (Top-3) a 10,26 %; tokens medios 504 frente a 367. (5) Aislamiento V2 (11.015/1.539) sobre las mismas 1.539 citas: base 0,836→0,804 y Top-3 0,821→0,800. Mejor época 4 en todas; entrenamiento ≈859/890 s; pico 9,27 GiB; A100-SXM4-40GB; torch 2.11.0, transformers 4.57.1, scikit-learn 1.7.2, MLflow 3.17.2; CE sin pesos. Revisión manual de 20 casos Evidence/IM: sin respuestas aún. **Implicaciones:** en validación los fragmentos no superan a la base (−0,80 puntos), así que el informe debe estar listo para un H6 negativo; los modelos actuales usan T_A con pre-etiqueta, por lo que se propone reentrenar con las etiquetas humanas antes de T_B; "V2" es ambiguo (aislamiento frente a versión de los datos) | GR |
| 11-nov | Decisiones de GR: (1) las pruebas extra de A4 (Top-1, aislamiento V2) **no** se incluyen en el informe; (2) se agrega la sección sin numerar **Declaración de uso de IA** antes de las Referencias (en IEEE va en el Reconocimiento; aquí, como sección propia porque no hay Reconocimiento). Texto: código, búsqueda y organización de información, y revisión de la redacción; los autores verifican y responden; los LLM de la metodología se remiten a la Sección III. ≈70 palabras (≈5 líneas) | GR |
| 11-nov | Título nuevo de GR: "CiteScope: Clasificación de la función de citas en Computer Science con modelos de lenguaje y recuperación semántica del artículo citado" (se corrigen la tilde de "artículo" y el punto final, que IEEE no usa). CiteScope = nombre de la aplicación; los trabajos previos con ese nombre se ignoran | GR |
| 11-nov | Título con **mayúscula** tras los dos puntos ("CiteScope: Clasificación…", decisión de GR); nombres de autores con tildes (Germán Rodríguez, José Arteaga, Sebastián Toro) en el bloque de autores y en la nota al pie; índice de términos: "recuperación densa" → "recuperación semántica" (igual que en Word) | GR |
| 11-nov | **Referencias renumeradas por orden de aparición.** Se agregan las citas que faltaban donde ya se mencionaban: jueces en III-C (Qwen [9], Gemma [10], Mistral [11]); herramientas en III-H (PyTorch [14], Transformers [15], vLLM [16], scikit-learn [17], DVC [18], MLflow [19]); FastAPI [12] y Next.js [13] dentro de los huecos D-2 y D-3 (si no hay despliegue, se eliminan y se renumera). Mapa viejo→nuevo: 1→4, 2→1, 3→8, 4→2, 5→3, 6→5, 7→6, 8→7, 9–11 sin cambio, 12→14, 13→15, 14→16, 15→19, 16→18, 17→12, 18→13, 19→20, 20→17. §9 conserva la numeración anterior. TABLA I y `GR_Tablas_para_Word.txt` actualizadas | GR |
| 11-nov | "Artículo científico" en la primera mención del Resumen ("…con el que un artículo científico se conecta…") y de la Introducción ("El volumen de artículos científicos en Computer Science…"); después basta con "artículo". Resumen: +1 palabra (287) | GR |
| 11-nov | κ definido en III-C: "que descuenta el acuerdo esperado por azar; valores sobre 0,80 se consideran acuerdo casi perfecto [12]". Nueva referencia Landis y Koch (1977), verificada en Crossref. Renumeración: FastAPI–SciRepEval pasan de [12]–[20] a [13]–[21]. Lista final [1]–[21]; §9 conserva la numeración del 09-nov | GR |
| 11-nov | **Correo del experto (J. C. Sanguino, 6-nov), respuesta a la consulta de GR del 5-nov sobre cómo accede el demostrador al citado:** no hay restricciones; prefiere **fragmentos precalculados con su representación vectorial** (demo más rápido) y acepta calcularlos en ejecución si hay limitación de espacio. `a8_index.py` ya sigue la opción preferida (reutiliza los vectores de A1; Top-3 idéntico al de A1). Hueco: el catálogo tiene título pero **no resumen**, que necesita el SciBERT base. Para III-H: "siguiendo la recomendación del experto, los fragmentos de los artículos citados se precalculan con sus vectores; en ejecución solo se codifica el párrafo del usuario"; limitación: el demostrador solo cubre los citados del índice (licencia CC BY o CC0). Decisiones 13 y 14 agregadas a Solicitudes | GR |
| 11-nov | Diseño del demostrador consolidado en §7 III-H (entrada con `[[TARGET]]` + citado elegido por título; atajo de 40 ejemplos; Top-3 en ejecución sobre vectores precalculados; 4 clasificadores con entrada en texto; resultados: función, barras de puntaje y los 3 fragmentos). GR decide no graficar todos los candidatos: solo los 3 fragmentos | GR |
| 11-nov | **Demostrador: el equipo elige el atajo como única entrada.** Solo los 40 ejemplos de T_B (sin texto libre ni buscador de citados); §7 III-H, Solicitudes (D y decisión 14) actualizados | GR |
| 11-nov | Demostrador alineado con 5.3 de la guía: **tres opciones**, un SciBERT ajustado (el mejor en T_B), un modelo de pesos abiertos de **1–8B** y un modelo comercial (uno de A5). Se descarta ofrecer los dos SciBERT | GR |
| 11-nov | Demostrador, clasificador ajustado por GR: tres opciones con dos variantes cada una, Encoder fine-tuned (SciBERT Base o SciBERT Chunk), Model Open-Weight (Llama 3.1 8B o Qwen 8B) y Modelo Comercial vía API (GPT o Gemini). Diseño en §7 III-H como tabla Paso / Requisito / Proceso | GR |
| 11-nov | **Ejemplos del demostrador recibidos** (`a3-001.zip` de Drive → `Insumos/a3/demo_examples/`, en `.gitignore`): `examples_TB.jsonl`, 40 ejemplos, todos gold de T_B con `in_eval` (verificado contra `test_set_gold.jsonl`); 39 citantes y 35 citados distintos; citados CC BY 4.0 (39) y 3.0 (1). Por función: IM 10, Evid 6, FR 6, Basis 5, Gap 5, Bg 4, Comp 3, App 1, **Orig 0**. Campos: contexto con `[[TARGET]]`, títulos, enlaces, licencias, etiqueta, `a2_top3` (claves de fragmentos); **sin resumen del citado**. La guía de Alejandra (`demo_index_examples_guide.md`) recomienda mostrar `a2_top3` en los ejemplos (39/40 idénticos a la recuperación en vivo; B-015 difiere en el 3.º por 0,0001 de coseno), mostrar atribución CC BY y limpiar marcadores al mostrar. Con modelo entrenado con datos v1 se pueden sumar 8 ejemplos de reserva/colchón con pre-etiqueta (`--include-unannotated`), ninguno de Originator | GR |
| 11-nov | Demostrador: (1) **sin Identification of the Originator** (T_B no tiene ejemplos de esa función; decisión de GR, se declara en III-H); (2) **resúmenes agregados** a los 40 ejemplos: `Insumos/a3/demo_examples/examples_TB_con_resumen.jsonl` (campo `cited_abstract`, más su fuente), tomados de `cs_subset_core_paper_metadata.jsonl` (`dvc pull` de ese solo archivo en `Proyecto_LCR_CF`; es la tabla con la que A2 armó los lotes, así que son los mismos resúmenes que usa SciBERT en A4). 35/35 citados con resumen; títulos idénticos; validado contra una hoja de anotación de GR (51/51 resúmenes idénticos). Archivo en `.gitignore` | GR |
| 11-nov | **Acuerdo del equipo: los 40 ejemplos son la fuente única del demostrador y no se calcula similitud en ejecución** (se usa el Top-3 guardado, `a2_top3`). Tabla de §7 III-H actualizada. Pendiente: texto y sección de los 120 fragmentos (los ejemplos solo traen sus claves) | GR |
| 11-nov | **Ejemplos del demostrador publicados en el repositorio (decisión de GR y el equipo, pese a la regla previa de no publicar texto):** solo `examples_TB_con_resumen.jsonl`, `manifest_examples_TB.json` y un README con licencia y atribución; los 40 son CC BY (citantes 4.0; citados 39 × 4.0 y 1 × 3.0). El resto de `Insumos/a3/` (incluidas las etiquetas de T_A y los ejemplos de T_A) sigue fuera de git. `GR_Demostrador_Pasos.txt` enlaza el archivo en GitHub | GR |
| 11-nov | **Fragmentos agregados a los 40 ejemplos** (campo `top3`: rango, clave, sección y texto, en el orden de `a2_top3`). Fuente: `cited_papers_chunked_pilot_clean_v1.jsonl` y `…_ext_clean_v1.jsonl` (`dvc pull` de un archivo a la vez y borrado de la copia y de la caché después de extraer, por espacio en disco); 114 fragmentos distintos (111 del piloto y 3 de la ampliación; los repetidos son idénticos). Los 40 ejemplos quedan con los 6 componentes; 3 de 120 fragmentos tienen la sección vacía; mediana de 149 palabras por fragmento. Pendiente de III-D/§7: en el demostrador no queda nada que calcular en la recuperación | GR |
| 11-nov | Demostrador (revisión de GR): **un solo SciBERT**, el de mayor F1 macro en T_B; Open-Weight y Comercial con el prompt de la condición principal de A5 y la misma entrada del SciBERT elegido; GR decide no incluir en el .txt la línea de atribución CC BY (la exige la licencia; queda en el README de los ejemplos y debe cumplirse en la interfaz) | GR |
| 11-nov | **Entrega de ST (11-nov, `Old/11 Nov/`):** `Modelos_Entradas_Salidas.md`, `Ejemplos_Reales_Entradas_Salidas.json` y el notebook de la iteración 2. Cambios frente a lo redactado: datos **training v2 + etiquetas humanas de T_A** (944 entrenamiento / 125 validación con etiqueta humana); **aislamiento V2** (11.616 / 1.653; verificado: 0 de los 4.483 documentos de T_B aparecen en entrenamiento en ningún rol, frente al 82,9 % de citados vistos con V0); **búsqueda de hiperparámetros** (12 ensayos + 4 semillas; base LR 2e-5 y decaimiento 0,1; Top-3 LR 3e-5 y 0,01; hasta 8 épocas, paciencia 2; semillas 42/17/73). Validación (FP32, semilla 42): base 0,8306, Top-3 0,8254, Top-1 0,8311; media de 3 semillas: Top-1 0,830 ± 0,006 y Top-3 0,826 ± 0,002. Background 43,1 %; IM 140/19. Contrato de salida: `label`, `score`, `scores` (9), `score_calibrated=false`, `token_audit`. Afecta III-D, TABLA IV, Limitaciones (citados vistos), A4-2/A4-3/A6 (vistos/no vistos) y la definición de "Chunk" (Top-1 o Top-3) | GR |
| 11-nov | **Nomenclatura y alcance de A4 (GR a ST):** solo dos modelos, **SciBERT base** (contexto + título + resumen) y **SciBERT Top-3** (contexto + los 3 fragmentos con su sección); Top-1 nunca se solicitó y no se usa. "SciBERT Chunk" (término de GR del 11-nov) se reemplaza por "SciBERT Top-3" en el demostrador, las notas y las solicitudes | GR |
| 11-nov | **Informe alineado con la corrida de ST del 11-nov** (conteos reproducidos por GR: 32.023 → 16.440 tras aislar T_B y calibraciones → 2 *unclear* fuera → 13.269 → 11.616/1.653, 944/125 con etiqueta humana, 113 etiquetas de T_A corregidas; 0 documentos de T_B en entrenamiento). III-A: cs.CV 77,2 % de 13.269 (cs.LG 8,9 %, cs.DS 6,8 %, otros 7,1 %; T_B 88,4/5,8/2,4/3,4). III-D: datos, aislamiento, partición, pérdida sin pesos, búsqueda en rejilla + 3 semillas, validación mixta (92,4 % pre-etiquetas) y uso único de T_B. TABLA IV con los hiperparámetros por configuración. Fortalezas, Limitaciones (se quita el 82,9 % de citados vistos; se agrega el costo del aislamiento y el sesgo de validación), Trabajo futuro (se quita aislar citados) y huecos A4-2/IV-E (vistos/no vistos → semillas). Solicitudes: tabla de datos de A4, cumplimiento, decisión 5 y A4-1/3/4. Copia previa del artículo en la carpeta de la sesión | GR |
| 11-nov | Chat GR–ST: ST confirma que **Top-1 fue solo una prueba**; A4 queda en SciBERT base y SciBERT Top-3. GR pregunta: (1) si esos dos modelos ya quedan congelados; (2) los valores de la rejilla de los 12 ensayos (A4-3); (3) la razón de usar entropía cruzada sin pesos por clase (A4-4). En espera de respuesta | GR |
| 11-nov | **Meta de 2.000 por función aclarada en el informe.** TABLA III pasa a "Instancias por función" con columnas Conjunto (34.988 = 32.020 de la versión 2 con etiqueta humana de T_A, sin sus 3 *unclear*, + 2.968 de T_B), Entrenamiento (11.616), Validación (1.653), T_B y Corrección. III-C: 6 de 9 funciones superan 2.000 en el conjunto (IM 826, Orig 1.692, FR 1.716 no); III-D: tras el aislamiento se usan 13.269 y solo Background supera 2.000 en entrenamiento; Limitaciones ajustadas. "Dataset" → "conjunto de datos" | GR |
| 11-nov | Estilo: GR prefiere "dataset" en todo el informe; se reemplaza "conjunto de datos" (5 menciones, incluida la TABLA III) y se agrega a §4.2 | GR |
| 11-nov | TABLA III rehecha para que las cifras sumen a la vista: Dataset = Excluded + Training + Validation + Test B (p. ej., Background 12.713 = 6.662 + 5.004 + 717 + 330; total 34.988 = 18.751 + 11.616 + 1.653 + 2.968), más Correction. Excluded = aislamiento por documento + retiro por compartir artículo con Validation; recalculado desde los archivos originales | GR |
| 11-nov | Informe: T_B → "Test" (15 menciones) y particiones en inglés (Training, Validation, Test) en texto y tablas (III, IV, VI, VII, VIII, X); se mantienen en español "validación humana", el proceso de "entrenamiento" y las referencias al conjunto de prueba del otro grupo. Regla en §4.2. Copia previa en la carpeta de la sesión | GR |

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
- **CiteScope es el nombre de la aplicación de este trabajo** (11-nov, GR): solo se reutiliza el nombre. Los trabajos anteriores con ese nombre (el microproyecto citado en el primer informe con F1 macro 0,68 y la herramienta homónima de terceros) se ignoran: no son lo mismo ni son referencia de este trabajo, y no se citan.
- **Modelos de lenguaje (2023–2025):** resuelto con Koloveas et al. (2025) [7] y Gilardi et al. (2023) [8], verificadas en §9.
- **Texto base:** la sección 3 de la [propuesta](../PropuestaProyectoGrado.md) ya redacta SciCite, MultiCite, SciBERT, Gu et al. y unarXive, con la brecha "Gu et al. recuperan *qué* citar; este trabajo recupera *por qué* se cita". Sirve para la Sección II y la TABLA I.
- **Referencias de la propuesta revisadas (09-nov):** Beltagy, Cohan, Gu, Lauscher, Lyu y Saier pasan al artículo. Se completan las páginas de Gu (pp. 274–288) y el DOI de Lyu. El volumen LNCS 13185 que trae la propuesta **no se pudo confirmar** y se omitió. Se excluyen Bjerke & Renger y el Centro de Español (sirvieron para redactar objetivos) y OpenAlex (no se usó como fuente; solo se contaron sus identificadores dentro de unarXive). Se agrega scikit-learn (usado en A4). Opcional: citar a los autores originales del κ de Cohen y del α de Krippendorff, implementados en `a3_metrics.py` sin librería.

### III-A. Datos y corpus
- **Cifras tomadas del primer informe** ([Primer Informe.pdf](../Primer%20Informe.pdf) §2):
  - 405.947 artículos cs.\*;
  - 358.494 artículos y 72,6 % de cobertura con categoría primaria restringida;
  - tamaños del piloto y de la ampliación.
- ✅ **Razón de los subcampos (A1-1):** cerrada; el evaluador la pidió solo "de existir". La concentración se explica con `inspect_cs_subset_core_01_09_26_results.md`.
- ✅ **Distribución por subcampo (A1-2):** cs.CV 86,2 % (entrenamiento) y 88,4 % (T_B), según la categoría principal de arXiv (`Insumos/GR_A1-2_distribucion_subcampo.csv`).
- ✅ **Conteo del primer informe conciliado** (contrato del 9-nov, l. 128): 28.553 re-juzgadas + **900** de `pool_cue_yield` (el primer informe decía 885) − 90 de eval60 y calib30 = 29.363 − 27 de calib2 = **29.336**. El artículo solo usa el total de 38.780.
- **Corregido el 10-nov contra el código:** (1) la limpieza **no** elimina fragmentos sin sección (`clean_dataset.py`, l. 35–40: se quitó esa regla porque 20.986 fragmentos, el 1,63 %, eran texto real); (2) el conjunto pre-etiquetado **no** conserva la distribución natural: mezcla lotes aleatorios, de citas únicas y dirigidos a funciones escasas (readme, §A2); (3) el 72,6 % y el 89,9 % se refieren a artículos de arXiv citados distintos, no a referencias.

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
- ✅ **TABLA III llena (09-nov)** con `Insumos/a3/` (`iaa_report.md` §§1–3 y 8, recalculado desde `test_set_gold.jsonl`). La corrección es "etiqueta final ≠ pre-etiqueta" por celda de 330.
- **Material para la Discusión (iaa_report.md):** el κ de la ronda 2 de T_B fue más bajo (0,759) que el de la ronda 1 (0,870); el 90,6 % de las anotaciones se declaró de confianza alta (95,0 % coincide con el *gold*), frente a 62,5 % en confianza baja; las pre-etiquetas unánimes de los jueces se conservaron en el 95,4 % de los casos, frente a 83,9 % con 2 de 3 votos.
- **Cierre de A3 (contrato del 9-nov, §6.4):** 2 `unclear` en T_B. Improvement/Modification quedó en 268 en T_B (por debajo de 300) porque ambos grupos decidieron, el 8-nov, no liberar la reserva; ya está redactado en III-C y en Limitaciones. Ningún paquete de reserva ni de colchón se anotó.
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

### III-E. Modelos de lenguaje comerciales
- **Fuente:** carpeta `A5/` del repositorio (commit 30d1592, 9-nov, gaspar3107-tech): `A5_Modelo_Comercial_G15.ipynb`, `a5_runtime.py`, `Notebook_Explain.md`, `prompt_v11_1_snapshot.json` y pruebas. Por ahora solo se ejecutó en modo demostración, con datos sintéticos; **no hay modelo elegido ni corrida real**.
- **Diseño verificado en el código:**
  - 8 condiciones = información del citado (`base` o `fragmentos`) × prompt (`generic` o `specific`; este añade las reglas de v11.1) × ejemplos (`zero` o `few`); los identificadores son del tipo `base-generic-zero`;
  - *few-shot*: exactamente 9 ejemplos de desarrollo con etiqueta humana, uno por función, en orden fijo. El código impide que compartan `inst_key` o artículo citante con T_B;
  - en la prueba exige `ALIGNED_INPUTS=True`: las entradas de SciBERT ya recortadas (`a4_inputs`) → **nueva dependencia A4-6**;
  - salida: JSON con `scores` por función; la predicción es la de mayor puntaje (los empates se marcan); `unclear` no es una salida posible. Una respuesta inválida queda como predicción fallida; solo se reintentan errores transitorios (429, 5xx);
  - ya calcula métricas por condición, matrices de confusión y la comparación con SciBERT con *bootstrap* pareado por citante, y lleva un registro de costos por intento.
- **Alineación con el enunciado:** la representación `base` (título y resumen) es la que pide el enunciado; la de `fragmentos` amplía la comparación y permite la H8.
- **Pendiente (A5-1, A5-2):** modelo exacto, prompts, temperatura y la condición principal para las Figs. 3 y 4, definida antes de ver el conjunto de prueba.

### III-F. Diseño experimental
- **Fuente de H1–H5:** primer informe §3.2, §4.2 y §5, y [RESUMEN_01_A2_pool_y_jueces.md](../../../Folder_trabajo_Equipos_14_y_15/RESUMEN_01_A2_pool_y_jueces.md).
- Hay una tensión que conviene enfrentar en la Discusión: H5 (sin fragmentos 49, con fragmentos 48) va contra la hipótesis central. H6 la contrasta en el clasificador y **H8** en el modelo comercial (agregada el 09-nov por el diseño de A5).

### III-G. Métricas
- **Pendiente:** script de evaluación con bootstrap pareado por citante. GR, 12-nov.

### III-H. Despliegue
- **Pendientes de CB (19-nov):** arquitectura AWS, figura, backend y modelo de pesos abiertos elegido.
- **Pendiente de ST (19-nov):** frontend.
- Herramientas tomadas de la Propuesta §9.1.
- **Diseño acordado del demostrador (11-nov, GR; base: documento del proyecto §5 y correo del experto del 6-nov):**
  | Paso | Requisito | Proceso |
  |---|---|---|
  | **1. Elegir un ejemplo** | 5.1 Entrada de usuario | **Fuente única del demostrador (acuerdo del equipo, 11-nov): los 40 ejemplos de T_B**, sin texto libre ni buscador de citados. La lista la generó `a8_examples.py` (Alejandra) desde `test_set_gold.jsonl`: citas evaluadas, con etiqueta humana, con citante y citado bajo licencia CC BY o CC0. GR le agregó el resumen del citado (`examples_TB_con_resumen.jsonl`). Cada ejemplo trae: párrafo citante con `[[TARGET]]`; título, **resumen**, enlace y licencia del citado (y del citante); claves del Top-3 de A2 (`a2_top3`); etiqueta humana. Ningún modelo del G15 los vio en entrenamiento. Por función: IM 10, Evid 6, FR 6, Basis 5, Gap 5, Bg 4, Comp 3, App 1; **sin Identification of the Originator**. Se habilita después de la evaluación única en T_B y se muestra completa (aciertos y errores) |
  | **2. Mostrar el Top-3** | 5.2 Recuperación de chunks | **Sin cálculo en ejecución.** Se leen los 3 fragmentos guardados en el ejemplo (campo `top3`: rango, sección y texto, en el orden de `a2_top3`): los que recuperó A1 con SciBERT y que vieron anotadores y modelos. Frente al enunciado ("calcular… mediante SciBERT"), el cálculo se hizo con SciBERT en A1 y el demostrador lo presenta; se justifica en III-H con la recomendación del experto de precalcular |
  | **3. Clasificar** | 5.3 Selección del modelo | El usuario elige **una de tres opciones**: **(a) Encoder fine-tuned:** un solo SciBERT, el de mayor F1 macro en T_B (regla fijada antes de abrir T_B); entrada en texto de hasta 512 tokens, `[CLS]` contexto `[SEP]` título y resumen (SciBERT base) o 3 fragmentos con su sección (SciBERT Top-3) `[SEP]`. **(b) Model Open-Weight (Llama 3.1 8B o Qwen 8B)** y **(c) Modelo Comercial vía API (GPT o Gemini):** prompt de la condición principal de A5 + la misma entrada del SciBERT elegido, ya recortada. Todos devuelven una probabilidad o puntaje por función |
  | **4. Mostrar resultados** | 5.4 Visualización | Función predicha, con su definición de la guía; barras con el puntaje de las 9 funciones (SciBERT: probabilidad del modelo, sin calibrar; Open-Weight y Comercial: puntaje declarado por el modelo); los 3 fragmentos con rango y sección; etiqueta humana del ejemplo con ✓ o ✗; atribución CC BY (título, licencia y enlace de arXiv) junto a cada texto |
  - **Pendientes:** confirmar la versión exacta de "Qwen 8B" (en H1 se probó Qwen 2.5 7B; Qwen3-8B también está en el rango 1–8B). Los modelos Open-Weight del demostrador no se evalúan en T_B (la guía no lo pide en A6); en el informe se presentan solo como opción del demostrador. Opcional: precalcular las predicciones de los 40 ejemplos para cada opción (el demostrador quedaría sin cómputo en ejecución, salvo que se quiera mostrar la latencia).
  - **Para III-H (texto propuesto):** "El demostrador trabaja sobre 40 citas del conjunto de prueba cuyos artículos citante y citado tienen licencia abierta. Cada ejemplo incluye su artículo citado, como en unarXive, donde cada marca de cita se vincula al citado mediante la bibliografía del citante: un párrafo puede contener varias citas y el texto por sí solo no permite identificarlo. Los tres fragmentos se recuperaron previamente con SciBERT, siguiendo la recomendación del experto de precalcular la recuperación, y son los mismos que vieron anotadores y modelos. No hay ejemplos de Identification of the Originator, porque ninguna cita de esa función en el conjunto de prueba cumple el criterio de licencia." Trabajo futuro: entrada libre con selección del citado y recuperación en ejecución.

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

**Las solicitudes para enviar a cada compañero están en [Solicitudes_Insumos_v0.1.md](./Solicitudes_Insumos_v0.1.md)** (mismos códigos; cubre A4 a A7 y el despliegue D-1 a D-5; A1–A3 están cerrados). Desde el 10-nov empieza con la agenda de decisiones del equipo (sección 0). Revisado el 09-nov contra los repositorios (`Proyecto_LCR_CF`, `Folder_trabajo_Equipos_14_y_15`, `A4/`). "Evidencia" indica qué existe hoy; "Responsable" se asigna a quien pueda validar y entregar el insumo. Cada insumo se deja en `Insumos/` con las iniciales como prefijo.

### A1 — Corpus y recuperación

| # | Insumo | Alimenta | Evidencia hoy | Responsable |
|---|---|---|---|---|
| A1-1 | ~~Razón de la elección de los subcampos del piloto~~ | III-A | ✅ **Cerrada (10-nov):** el evaluador pidió la razón solo "de existir"; la concentración en cs.CV ya se explica con datos verificados. El artículo describe la elección sin atribuirle un motivo | — |
| A1-2 | Distribución por subcampo del citante en entrenamiento y T_B | III-A, Limitaciones | ✅ **Resuelto (10-nov):** categoría principal consultada en la API pública de arXiv para los 24.737 citantes de entrenamiento v1/v2 y T_B (solo se enviaron IDs). Validación: el 100 % cae en las 8 categorías del filtro del corpus. Resultado: cs.CV 86,2 % (entrenamiento v1) y 88,4 % (T_B); cs.LG 6,2 / 5,8; cs.DS 3,7 / 2,4; los otros cinco suman 3,9 / 3,5. CSV en `Insumos/GR_A1-2_distribucion_subcampo.csv`; script y caché en los archivos de la sesión | — |
| A1-3 | Fragmentos truncados a 512 tokens | III-B | ✅ **Resuelto (10-nov):** 138 de 1.229.408 (0,01 %) en el piloto y 252 de 1.574.790 (0,02 %) en la ampliación; 0 contextos. Fuente: `Proyecto_LCR_CF/src/analysis/eda_self_ref_dataset.ipynb` (EDA oficial del piloto `_clean_v1`, según el readme) y `eda_self_ref_dataset_ext.ipynb`; los totales coinciden con la TABLA II. La segmentación (`chunk_dataset.py`) ya divide cada fragmento a ≤512 tokens; el registro de la ampliación (`docs/script_outputs/corpusExtensionPipeOutput.md`) lo confirma | — |
| A1-4 | Evaluación humana P@3 | III-B, TABLA V (H4), TABLA VI, IV-A, V, VI | ✅ **Cerrada (10-nov): no se hace** (opción 2, decisión de GR). Nunca se realizó: la propuesta lo comprometió, el informe de avance lo dejó "previsto" y el plan de trabajo lo bajó a "si sobra tiempo". El artículo lo trata con honestidad y sin tono negativo: III-B describe las verificaciones que sí se hicieron y que la anotación humana se concentró en las etiquetas (11.880 anotaciones); H4 se reformula a lo medible (auditoría de secciones: 31,6 % frente a 8,55 %; 51,9 % de pares; introducción 46,8 % en el Top-1 con filtro); Limitaciones y trabajo futuro lo mencionan | — |

### A2 — Pre-etiquetado

Sin insumos pendientes: las cifras de la TABLA VI y de III-C están documentadas (primer informe, `RESUMEN_01`, notebooks de A2).

### A3 — Validación humana (T_B)

| # | Insumo | Alimenta | Evidencia hoy | Responsable |
|---|---|---|---|---|
| A3-1 | `test_set_gold.jsonl`, `iaa_report.md`, `manifest_metrics.json` y readme | Resumen, III-C, TABLA III, TABLA VI | ✅ **Recibido el 9-nov** en `Insumos/a3/`. Las cifras de T_B se recalcularon desde el archivo y coinciden con el reporte | GR ✅ |
| A3-2 | n por función, % de corrección, κ y α de T_B | TABLA III, TABLA VI, resumen | ✅ **Incorporado:** 2.968 evaluables (2 `unclear`), κ de Cohen 0,854, α nominal 0,854, α MASI 0,850, acuerdo observado 87,0 %, 386 adjudicadas, corrección 9,7 % (Improvement/Modification 25,2 %) | GR ✅ |

### A4 — SciBERT

| # | Insumo | Alimenta | Evidencia hoy | Responsable |
|---|---|---|---|---|
| A4-1 | Corrida de la configuración **con fragmentos** | III-D, IV-B, IV-C | **No existe.** La corrida 1 (2-nov, `A4/pruebascolab/…_corrida1.ipynb`) entrenó solo la base | Por asignar |
| A4-2 | Evaluación de ambas configuraciones sobre T_B (`RUN_TEST=True` con el *gold* de A3-1): métricas, F1 por función, matrices de confusión, IC *bootstrap* pareado por citante, citados vistos y no vistos | TABLA VII, Fig. 3, Fig. 4, IV-B | No ejecutada; esperaba el *gold* | Por asignar |
| A4-3 | Confirmar la TABLA IV con las corridas reales: épocas efectivas y versiones | III-D, TABLA IV | Corrida 1 (base): A100 40 GB, 4 épocas, ≈14 min de sesión, pico de 9,3 GiB, torch 2.11, transformers 4.57.1, scikit-learn 1.7.2, MLflow 3.17.2; hiperparámetros = planeados | Por asignar |
| A4-4 | Decisión sobre el desbalance de clases y su justificación | III-D | La corrida usa **entropía cruzada sin pesos** (`unweighted_cross_entropy`) | Por asignar |
| A4-5 | 2 ejemplos de errores representativos | IV-D | Depende de A4-2 | Por asignar |
| A4-6 | Entradas de SciBERT ya recortadas (base y fragmentos) para T_B y los 9 ejemplos *few-shot*, para que el modelo comercial reciba el mismo texto. Se entregan directamente a A5 (contienen texto de los artículos) | III-E, TABLA VII | El notebook de A4 construye estas entradas; falta exportarlas | Por asignar |

**Versión del entrenamiento (contrato del 9-nov, §10; `manifest_training_v2_G15.json`):** la v1 tiene 31.265 filas y la v2 32.023 (+758 recuperadas: Background 163, Basis 91, Application 88, Comparison 82, Evidence 81, Gap 81, Identification of the Originator 60, Further Reading 59, Improvement/Modification 53). la versión 2, opcional, devuelve las filas (con pre-etiqueta) de los artículos citantes de la reserva y del colchón propios, que nunca se anotaron. También se pueden usar las etiquetas humanas de T_A en lugar de sus pre-etiquetas. Si A4 usa la versión 2, el informe debe decirlo y dar las filas recuperadas por función. Lo pide A4-3.

**Advertencia para la redacción:** el F1 macro de validación de la corrida 1 (**0,846** con la base; línea de clase mayoritaria 0,062) se mide contra las **pre-etiquetas de los jueces**, no contra etiquetas humanas. Solo puede reportarse como concordancia con los jueces, nunca como desempeño final.

### A5 — Modelo de lenguaje comercial

| # | Insumo | Alimenta | Evidencia hoy | Responsable |
|---|---|---|---|---|
| A5-1 | **Los dos modelos exactos**: proveedor, nombre, versión, precio y fecha de consulta de cada uno | III-E, referencias | El notebook de A5 existe; `MODEL_ID` sin definir. El adaptador es compatible con Chat Completions: un proveedor con API distinta requiere adaptar el código | Por asignar |
| A5-2 | Prompts genérico y específico, los 9 ejemplos *few-shot*, temperatura y condición principal | III-E, Apéndice A, Figs. 3–4 | Prompts en `prompt_v11_1_snapshot.json`; ejemplos y condición principal sin definir | Por asignar |
| A5-3 | Predicciones sobre T_B por modelo y condición (2 × 8) en el formato común (A6), con columna `modelo`, tokens, costo, latencia y validez | TABLA VII, TABLA VIII, TABLA X, Figs. 3–4 | Solo corrida de demostración | Por asignar |
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
| D-2 | Backend FastAPI: endpoints, carga de modelos y modelo de pesos abiertos elegido (con sus datos exactos para la referencia) | III-H, referencia | **Parcial (10-nov):** `Proyecto_LCR_CF/src/demo/a8_index.py` (commit 741a15f, Alejandra) construye el índice de la demo. Reutiliza los vectores de A1 (el Top-3 de la demo es idéntico al de A1), se limita a artículos citados con licencia CC BY o CC0 y con título, aplica el filtro de trabajos relacionados y queda en Drive (`a1_demo_index/`), nunca en git. Faltan los endpoints y el modelo de pesos abiertos | Por asignar |
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
| ~~Renumerar las referencias por orden de aparición~~ Hecho el 11-nov; repetir solo si se agregan o quitan citas | Referencias | 21-nov |
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
| Landis y Koch (agregada el 11-nov; [12] en la numeración del 11-nov) | Crossref (DOI 10.2307/2529310) | ✅ Biometrics, vol. 33, n.º 1, p. 159 (Crossref; fin en 174 según la paginación publicada), 1977 |

**Eliminadas por no poder validarse (09-nov):** la referencia del modelo de lenguaje comercial y la del modelo de pesos abiertos de la aplicación. Ningún repositorio contiene código o configuración de ninguno de los dos; la propuesta solo menciona "GPT-4o/5, Gemini" como opciones. Entrarán cuando JA y CB entreguen el modelo exacto (proveedor, nombre, versión y fecha) y la referencia pase este protocolo.

**Corregido frente al borrador anterior:** Gemma pasa de "Google" a "Google DeepMind", según su ficha. DVC deja de atribuirse a "Iterative". Se quitan las páginas no oficiales de PyTorch y el volumen LNCS no confirmado de Gu. Se agregan DOI, sedes y años verificados.
