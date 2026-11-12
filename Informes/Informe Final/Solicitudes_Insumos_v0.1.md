# Solicitudes de insumos para el informe final

## Dataset del Grupo 15 al cierre de A3 (9-nov)

**Particiones del dataset construido en A3** (versión 1, antes del aislamiento de A4; instancias por función):

| Función | Entrenamiento | Validación | Prueba T_B | Total | ≥ 2.000 |
|---|---:|---:|---:|---:|:---:|
| Background | 10.957 | 1.257 | 330 | 12.544 | ✓ |
| Gap | 2.522 | 285 | 310 | 3.117 | ✓ |
| Basis | 2.346 | 260 | 322 | 2.928 | ✓ |
| Comparison | 2.840 | 317 | 313 | 3.470 | ✓ |
| Application | 3.776 | 467 | 400 | 4.643 | ✓ |
| Improvement/Modification | 487 | 58 | 268 | 813 | ✗ |
| Evidence | 2.715 | 312 | 386 | 3.413 | ✓ |
| Identification of the Originator | 1.175 | 137 | 324 | 1.636 | ✗ |
| Further Reading | 1.221 | 133 | 315 | 1.669 | ✗ |
| **Total** | **28.039** | **3.226** | **2.968** | **34.233** | 6 de 9 |
| **Etiqueta** | pre-etiqueta | pre-etiqueta | humana | | |

**Datos que usa A4** (corrida de ST del 11-nov, verificada por GR): versión 2 de los datos (32.023), etiquetas humanas de T_A donde existen y **aislamiento estricto por documento** (ningún artículo de T_B, en ningún papel, ni de las calibraciones; entrenamiento y validación tampoco comparten documentos). Quedan **11.616 de entrenamiento y 1.653 de validación** (944 y 125 con etiqueta humana):

| Función | Entrenamiento | Validación | Prueba T_B |
|---|---:|---:|---:|
| Background | 5.004 | 717 | 330 |
| Gap | 1.217 | 179 | 310 |
| Basis | 848 | 112 | 322 |
| Comparison | 1.188 | 176 | 313 |
| Application | 871 | 144 | 400 |
| Improvement/Modification | 140 | 19 | 268 |
| Evidence | 1.318 | 166 | 386 |
| Identification of the Originator | 329 | 58 | 324 |
| Further Reading | 701 | 82 | 315 |
| **Total** | **11.616** | **1.653** | **2.968** |

**Cumplimiento** frente al documento del proyecto (PhD) y a la realimentación del primer informe (Revisor):

| Requisito | Fuente | Resultado del Grupo 15 | Estado |
|---|---|---|:---:|
| Corpus de arXiv en inglés, del área de computación | PhD | unarXive 2022, Computer Science: 38.780 contextos de cita pre-etiquetados, cada uno con los 3 fragmentos del citado recuperados con SciBERT y su sección | ✓ |
| Concentración en cs.CV: justificarla si hubo una razón de selección | Revisor | No fue una elección. cs.CV tiene más artículos (59.780), más referencias con identificador de arXiv (25,8 % frente a 1,9–8,2 %) y el 89,9 % de lo que cita está en el corpus. La ampliación a cs.LG, cs.CL y cs.DS la bajó poco: 86,2 % en entrenamiento y validación, 88,4 % en T_B. Explicado en III-A y en Limitaciones | ✓ explicado |
| Pre-etiquetado con un sistema de jueces de pesos abiertos | PhD | Qwen3.8-27B, Gemma 4 26B-A4B y Mistral Small 3.2 24B; 37.254 (96,1 %) con alta confianza (al menos 2 de 3 votos coinciden). Solo esas entran al dataset | ✓ |
| ≥ 2.000 ejemplos por función | PhD | 6 de 9. Improvement/Modification (813), Identification of the Originator (1.636) y Further Reading (1.669) no llegan | Parcial |
| Dataset balanceado (el revisor también señaló el desbalance de las funciones minoritarias) | PhD, Revisor | La prueba sí (268–400 por función); el entrenamiento no (con el aislamiento de A4: Background 43,1 %, Improvement/Modification 1,2 %). Manejo del desbalance: decisión A4-4 | Parcial |
| ≥ 15 % validado por humanos | PhD | 5.940 de los 38.780 pre-etiquetados (15,3 %): T_A + T_B, anotados por ambos grupos. El G15 evalúa con T_B (2.968, el 8,7 % de su dataset) y usa T_A (2.967) como entrenamiento con etiqueta humana | ✓ conjunto / prueba propia 8,7 % |
| Muestra aleatoria por categoría | PhD | 330 por pre-etiqueta, sorteadas entre las de alta confianza con una semilla fijada antes de muestrear (`LCR-G14G15-A3-2026`) | ✓ |
| Validación humana reservada para la prueba | PhD | T_B: 2.970 instancias; 2 *unclear* quedan fuera, así que hay **2.968 evaluables**. No se usa en entrenamiento ni en validación, y se evalúa una sola vez | ✓ |
| Entrenamiento y validación con los datos restantes | PhD | A4 usa la versión 2 (32.023) con las etiquetas humanas de T_A donde existen (autorizado por el G14) y aislamiento estricto: 11.616 de entrenamiento y 1.653 de validación, partidos 90/10 por artículo citante (hash `G15-A4-split-v1`) y sin documentos compartidos | ✓ |
| ≥ 2 anotadores independientes y métrica de acuerdo | PhD | Un miembro del G14 y uno del G15 por instancia; κ de Cohen = 0,854, α = 0,854; 386 adjudicadas (13,0 %); 9,7 % de pre-etiquetas corregidas | ✓ |
| Sin solapamiento por documento (par citante–citado) | PhD | Más estricto que lo pedido: ningún artículo de T_B aparece en entrenamiento ni en validación, ni como citante ni como citado (verificado: 0 de 4.483), y entrenamiento y validación no comparten documentos. Costo: los datos de A4 bajan de 32.023 a 13.269 | ✓ |

**Notas de diseño:** la pre-etiqueta estaba visible para los anotadores, y T_B solo contiene pre-etiquetas de alta confianza. Ambas cosas van en Limitaciones.

**Archivos:** `Insumos/a3/test_set_gold.jsonl`, `iaa_report.md`. Fecha límite propuesta para los insumos: **17-nov** (borrador el 19-nov).

## 0. Para decidir en la reunión

| # | Tema | Propuesta | Decisión |
|---|---|---|---|
| 1 | **P@3 de la recuperación.** El evaluador lo pidió; nunca se calculó (no hay juicios de relevancia de los fragmentos). | No calcularlo. Declararlo como limitación y trabajo futuro. Como evidencia de la recuperación se usan la auditoría de secciones (H4) y los cosenos. | |
| 2 | **Los dos modelos comerciales** (A5-1). | Elegir hoy proveedor y versión exacta de cada uno, y quién paga las API. | |
| 3 | **Condición principal** de los modelos comerciales (A5-2). Debe fijarse **antes** de ver T_B. | Fijarla hoy: una con título y resumen y otra con fragmentos, la misma para los dos modelos. | |
| 4 | **Desbalance de clases** (A4-4): 10.957 Background frente a 487 Improvement/Modification; hoy se entrena sin pesos. | (a) Mantenerlo sin pesos y justificarlo, salvo que haya tiempo para (b): probar pesos por clase solo en validación. | |
| 5 | **Modelos que se evalúan en T_B** (A4-3). | **Resuelto (11-nov):** SciBERT base y SciBERT Top-3 de la iteración 1 de ST (versión 2 de los datos, etiquetas humanas de T_A, aislamiento estricto, 3 semillas). Falta que ST confirme que se congelan antes de abrir T_B. | Resuelto |
| 6 | **Aplicación web** (D-1 a D-5). Está en el resumen y en los objetivos; hoy solo existe el índice de la demo (`a8_index.py`). | Confirmar si habrá URL pública para el 17-nov. Si no, se quita del resumen y de los objetivos. | |
| 7 | **`Insumos/a3/`** incluye las etiquetas de T_A. El G14 autorizó usarlas para entrenar, no publicarlas. | Usarlas en entrenamiento; no publicar la carpeta (ya está en `.gitignore`). | |
| 8 | **Entrega de A4-6.** Las entradas de SciBERT contienen texto de los artículos. | ST las entrega directamente a JA, fuera del repositorio. | |
| 9 | **Pruebas extra de Sebastián** (solo validación): Top-1 (un fragmento, F1 0,845) y aislamiento estricto V2 (−3,2 puntos). | Incluirlas en el informe como pruebas de desarrollo: Top-1 responde al recorte del 91 %, y V2 mide lo que se habría perdido con un aislamiento más estricto. | Top-1: no se incluye; A4 se mantiene en SciBERT base y SciBERT Top-3 (GR, 11-nov). Aislamiento V2: Sebastián lo adoptó como configuración principal el 11-nov (ver bitácora). |
| 10 | **Nombre "V2" duplicado:** el aislamiento V2 de A4 no es la versión 2 de los datos de A3. | En el informe, "variante de aislamiento" frente a "versión de los datos". | |
| 11 | **Declaración de uso de IA** (recomendación de los profesores). | Un párrafo breve al final del informe; ver la propuesta de GR. | Incluida antes de las Referencias (GR, 11-nov). |
| 13 | **Clasificadores del demostrador** (guía 5.3: tres opciones). | **Encoder fine-tuned:** un solo SciBERT, el de mayor F1 macro en T_B (fijar la regla antes de abrir T_B). **Model Open-Weight** (Llama 3.1 8B o Qwen 8B) y **Modelo Comercial vía API** (GPT o Gemini): prompt de la condición principal de A5 + la misma entrada del SciBERT elegido. Confirmar la versión exacta de Qwen. | Definido por GR (11-nov) |
| 14 | **Fuente del demostrador.** | **Acordado (11-nov):** los 40 ejemplos de T_B son la única fuente; no se calcula similitud en ejecución, se muestra el Top-3 guardado de cada ejemplo (`a2_top3`). Resúmenes ya agregados; sin Originator. Falta agregar el texto y la sección de los 3 fragmentos de cada ejemplo. | Acordado |
| 12 | **Responsables y fechas.** | A4: ST · A5: JA · despliegue: CB/ST · A6 y A7: GR, con los insumos de ST y JA · borrador del informe final: GR. Insumos listos el 17-nov. | |

## A4 — Clasificador SciBERT (ST)

Dos SciBERT con las mismas instancias, partición (`G15-A4-split-v1`), semilla (42) e hiperparámetros. Solo cambia la información del citado: **base** (contexto + título y resumen) y **fragmentos** (contexto + 3 fragmentos con su sección).

| Código | Qué necesitamos | Requiere |
|---|---|---|
| A4-1 | ✓ **Entregado** (iteración 1 del 11-nov, FP32, semilla 42): F1 macro de validación base 0,8306 y Top-3 0,8254; Top-3 con 3 semillas 0,826 ± 0,002. Falta la media de base con 3 semillas y el F1 por función de ambos. | — |
| A4-2 | Evaluación **única** de ambas configuraciones sobre T_B: `test_comparison.csv`, `paired_test_comparison.json` (IC 95 % bootstrap pareado por citante), `test_classification_report.json`, `test_confusion.csv/.png`, `test_cited_seen_unseen.json`, `test_predictions.csv`. | A4-1 |
| A4-3 | *Parcial:* datos, aislamiento, partición (11.616/1.653), hiperparámetros elegidos (base 2e-5 / 0,1; Top-3 3e-5 / 0,01), hasta 8 épocas con paciencia 2 y semillas 42/17/73 ya confirmados. Faltan los **valores de la rejilla** (12 ensayos), la mejor época por modelo y las versiones de las bibliotecas de esta corrida. | — |
| A4-4 | Confirmado: entropía cruzada sin pesos por clase. Falta la justificación en una frase. | — |
| A4-5 | Dos errores típicos en T_B: `inst_key`, etiqueta real, predicción de cada configuración y 2–3 líneas de explicación. | A4-2 |
| A4-6 | Texto de entrada de SciBERT, ya recortado a 512 tokens, en base y fragmentos, por `inst_key`, para T_B y los 9 ejemplos few-shot. Entrega privada a JA. | A5-2 |

## A5 — Modelos comerciales (JA)

Dos modelos sin ajuste, cada uno en **8 condiciones**: información del citado (título y resumen o fragmentos) × prompt (genérico o específico) × zero-shot o few-shot (9 ejemplos, uno por función). Los dos reciben el mismo texto que SciBERT (A4-6) y los mismos prompts, ejemplos y parámetros.

| Código | Qué necesitamos | Requiere |
|---|---|---|
| A5-1 | Por modelo: proveedor, nombre, versión exacta de la API, fecha de las consultas, precio por millón de tokens de entrada y de salida, motivo de la elección y enlace oficial. | Tema 2 |
| A5-2 | Prompts genérico y específico completos, con el formato de los ejemplos; los 9 `inst_key` few-shot con su etiqueta y el criterio de elección; temperatura y demás parámetros; condición principal (tema 3). | — |
| A5-3 | `A5-3_predicciones.csv`: una fila por instancia × modelo × condición, con `inst_key`, `modelo`, `condicion`, `pred_label`, `score_<función>` (9), `latency_ms`, `respuesta_valida`, `tokens_entrada`, `tokens_salida`, `costo_usd` e `intentos`. | A4-6 |
| A5-4 | Dos errores por modelo; uno de ellos, un caso donde difiera de SciBERT. | A5-3 |

## A6 — Evaluación comparativa (GR)

Compara todos los modelos sobre las mismas 2.968 instancias de T_B: los dos SciBERT y las 8 condiciones de cada modelo comercial. Calcula:
- precisión, exhaustividad y F1, macro y micro;
- F1 por función y matrices de confusión;
- diferencia de F1 macro entre fragmentos y base, con IC 95 % bootstrap pareado por artículo citante;
- F1 para artículos citados vistos y no vistos en entrenamiento.

Alimenta la TABLA VII y las Figs. 3 y 4.

| Código | Qué necesitamos | Requiere |
|---|---|---|
| A6-1 | Los archivos `validation_predictions.csv` y `validation_classification_report.json` de la configuración base de la corrida del 2-nov (3.226 filas), para probar el cálculo antes de tener T_B. El notebook ya los generó en la carpeta de la corrida en Drive; solo hay que compartirlos. | — |
| A6-2 | Predicciones de cada modelo sobre T_B: un archivo por configuración o condición, con `inst_key`, la etiqueta predicha (nombre exacto de la guía) y el puntaje de cada una de las 9 funciones. Los CSV que exporta el notebook de SciBERT (`predicted_label`, `p_<función>`) sirven tal cual. | A4-2, A5-3 |

## A7 — Eficiencia y costo (GR, con insumos de ST y JA)

| Código | Qué necesitamos | Requiere |
|---|---|---|
| A7-1 | *Parcial:* A100-SXM4-40GB, ≈859 s (base) y ≈890 s (fragmentos) de sesión de entrenamiento, pico de 9,27 GiB. Falta el precio por hora con su fuente y confirmarlo para el par final. Por configuración de SciBERT: GPU, horas de entrenamiento (en total y hasta el mejor checkpoint), pico de memoria y precio por hora con su fuente (plan de Colab). | — |
| A7-2 | Por configuración de SciBERT: ms por ejemplo, hardware, tamaño de lote, número de ejemplos medidos y si incluye la tokenización. | — |
| A7-3 | Costo total facturado por cada proveedor en las 8 condiciones, para contrastarlo con `costo_usd`. | A5-3 |

## D — Despliegue (CB/ST)

Diseño acordado: el usuario elige una cita de los **40 ejemplos de T_B**, la única fuente del demostrador; la app muestra el Top-3 ya guardado para ese ejemplo (sin cálculo de similitud), clasifica con la opción elegida (Encoder fine-tuned: el mejor entre SciBERT base y SciBERT Top-3; Open-Weight: Llama 3.1 8B o Qwen 8B; Comercial: GPT o Gemini) y muestra la función, el puntaje de las 9 funciones, los 3 fragmentos con su sección y la etiqueta humana. Detalle en las notas, §7 III-H.

| Código | Qué necesitamos |
|---|---|
| D-1 | Arquitectura en AWS y su diagrama (Fig. 2). |
| D-2 | Backend FastAPI: endpoints y carga de los modelos de la decisión 13 (dos SciBERT, dos Open-Weight y llamadas a dos API comerciales). Ya existe el índice de la demo (`a8_index.py`): fragmentos precalculados con vectores SciBERT, como recomendó el experto el 6-nov. Resúmenes de los 40 ejemplos ya agregados por GR (`examples_TB_con_resumen.jsonl`, en Drive o compartido en privado). Sin Identification of the Originator (T_B no tiene ejemplos). |
| D-3 | Frontend Next.js: flujo de usuario y una captura con un ejemplo real (Fig. 5). |
| D-4 | Latencia medida de la API por clasificador. |
| D-5 | URL pública y repositorios que se pueden enlazar (sin texto de unarXive). |
