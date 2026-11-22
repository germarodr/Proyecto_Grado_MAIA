# Métricas de A4 y entrega para las siguientes fases

**Proyecto de grado · Grupo 15 · Corte: 13 de noviembre de 2026.**

Este documento reúne lo que entrenamos, cómo seleccionamos los dos modelos y qué encontramos al evaluarlos con referencias humanas. Sirve para que los responsables de A5, A6, A7 y del demostrador puedan reutilizar los resultados sin repetir el entrenamiento. Las cifras se expresan entre 0 y 1; las diferencias indicadas como puntos porcentuales multiplican la diferencia de F1 por 100.

**Resultado principal:** en 2.968 citas humanas, base alcanzó F1 macro **0,796728** y Top-3 **0,799951**. La diferencia de **+0,32 puntos porcentuales** tiene IC del 95 % **[−0,75; +1,39]**. No establece una ventaja clara de Top-3, ni demuestra equivalencia.

Fuentes del resultado: [test_comparison.csv](https://drive.google.com/file/d/1EZKtyGUeo9rgI3A7fBH1q_TkbfCXl6wO/view?usp=drivesdk), [paired_test_comparison.json](https://drive.google.com/file/d/1pQVIRBFNSN0x0xJJDuRg13Q45GFayahB/view?usp=drivesdk) y [notebook ejecutado del test](../Evaluacion_Final/Historico/Evaluacion_2026-11-13_01/SciBERT_Evaluacion_Final.ipynb), secciones 7–9.

## 1. Qué exige la universidad y qué entrega A4

| Actividad o requisito | Referencia de la universidad | Evidencia entregada y alcance |
|---|---|---|
| A4: comparar las dos entradas y producir nueve puntajes mediante clasificación supervisada | pp. 7–8 | Dos SciBERT ajustados por separado; contexto + título/abstract y contexto + Top-3/secciones. Exportaciones con tokenizador e inferencia. |
| A6: evaluar todos los modelos sobre el mismo test humano; precisión, recall y F1 macro/micro; confusiones | p. 8 | A4 entrega sus dos modelos ya evaluados, métricas, nueve probabilidades y matrices. La incorporación de los modelos de los compañeros corresponde a la comparación conjunta. |
| A7: tiempos, costos y consistencia/formato | p. 8 | Latencia del clasificador por lotes y entorno reproducible. Se deben complementar costos reales y mediciones comparables de las otras alternativas; no se asigna un costo financiero inventado. |
| Dataset: ≥2.000 ejemplos por clase, ≥15 % humano y aislamiento por documento | pp. 6–7 | Se acreditan conteos y separación. No se alcanzan 2.000 por clase salvo Background; el porcentaje global del test no acredita el muestreo humano del 15 % por categoría. |
| Test humano con dos anotadores y Kappa/Alpha | pp. 6–7 | Las referencias proceden del cierre A3. Sus métricas de acuerdo deben citarse desde A3; F1 del clasificador no mide acuerdo interanotador. |
| Demostrador: recuperar Top-3, mostrar secciones y permitir seleccionar clasificador | pp. 8–9 | A4 entrega el clasificador. La recuperación y la aplicación integrada son componentes adicionales; el exportado no recupera fragmentos por sí solo. |

**Fuente de la tabla 1:** [guía universitaria, pp. 6–9](https://github.com/germarodr/Proyecto_Grado_MAIA/blob/58f0bb8/Papers/Propuesta_Proyecto%20PLN.pdf), contrastada con [nuestra propuesta](../../Informes/PropuestaProyectoGrado.md), objetivo 4 y fase F4; evidencia técnica: [protocolo del test](https://drive.google.com/file/d/1Vclg6zlOQ82m1twDdVt2dtI4bGtYO80Q/view?usp=drivesdk) y [contrato de entradas/salidas](Modelos_Entradas_Salidas.md). Las diferencias de alcance y el uso cruzado de etiquetas requieren acuerdo con el asesor; este documento no declara su aprobación.

## 2. Qué datos utilizamos

Partimos de la entrega training v2. Los textos se reconstruyen desde los lotes originales de A2, unidos por identificador; las etiquetas humanas elegibles corrigen las preetiquetas. “Datos sintéticos” en la conversación se refiere aquí a **preetiquetas automáticas**: no afirmamos que los textos de los artículos hayan sido generados artificialmente.

| Etapa de preparación | Ejemplos |
|---|---:|
| Entrega training v2 | 32.023 |
| Después de exclusiones para proteger el test propio | 16.440 |
| Después de retirar dos citas ambiguas del conjunto humano elegible del otro grupo | 16.438 |
| Filas retiradas adicionalmente para separar documentos de train y validación | 3.169 |
| Entrenamiento final | 11.616 |
| Validación interna final | 1.653 |
| Total de aprendizaje y validación | 13.269 |
| Test propio reservado | 2.970 |
| Test propio evaluable; dos ambiguas excluidas del puntaje | 2.968 |

**Fuente de la tabla 2:** [preparación training v2](../README_TRAINING_V2_GOLD.md), [implementación de la preparación](../final_runtime.py), función `prepare_final_data`, y [data_audit.json](https://drive.google.com/file/d/1tjFmQp_xqV7TjHvduwtxzDjVAVFZcYgu/view?usp=drivesdk). Los dos casos ambiguos retirados del aprendizaje y los dos casos excluidos del puntaje del test pertenecen a conjuntos diferentes.

| Clase — orden fijo de salida | Train | Validación | Test humano | Total |
|---|---:|---:|---:|---:|
| Background | 5.004 | 717 | 330 | 6.051 |
| Gap | 1.217 | 179 | 310 | 1.706 |
| Basis | 848 | 112 | 322 | 1.282 |
| Comparison | 1.188 | 176 | 313 | 1.677 |
| Application | 871 | 144 | 400 | 1.415 |
| Improvement/Modification | 140 | 19 | 268 | 427 |
| Evidence | 1.318 | 166 | 386 | 1.870 |
| Identification of the Originator | 329 | 58 | 324 | 711 |
| Further Reading | 701 | 82 | 315 | 1.098 |
| **Total** | **11.616** | **1.653** | **2.968** | **16.237** |

**Fuente de la tabla 3:** [notebook ejecutado](../Evaluacion_Final/Historico/Evaluacion_2026-11-13_01/SciBERT_Evaluacion_Final.ipynb), sección 1, y [class_distribution.csv](https://drive.google.com/file/d/1EoWiYpQG_5QIrwLQR11vxfUcjhDp5eZZ/view?usp=drivesdk). Para los detalles de train/val, consultar `split_class_counts.csv` en el [estudio de reparto](https://drive.google.com/drive/folders/1UvtcwLFYgN48_atCVkB5XECjW24dvXu6). Totales calculados sumando las tres particiones.

Train contiene **944 etiquetas humanas y 10.672 automáticas**; validación, **125 humanas y 1.528 automáticas**. Las humanas utilizadas para aprender proceden del otro grupo conforme al contrato. Nuestro conjunto B se reservó para test, incluyendo los documentos de las citas ambiguas. El aislamiento compara la unión de documentos citantes y citados en cualquier rol y confirmó que no se comparten entre train, validación y test. Fuente: [trazabilidad de la preparación](../README_TRAINING_V2_GOLD.md), [data_audit.json](https://drive.google.com/file/d/1tjFmQp_xqV7TjHvduwtxzDjVAVFZcYgu/view?usp=drivesdk) y [contrato compartido](https://docs.google.com/document/d/1X7JXN5ZvoYJodhRxdT5Y-8wOaDlXwRXi/edit).

## 3. Recorrido experimental: qué cifras se pueden comparar

| Etapa | Referencia y población | F1 macro base | F1 macro Top-3 | Lectura |
|---|---|---:|---:|---|
| Validación inicial V0 | 3.226 citas con preetiquetas; una semilla | 0,847831 | 0,839801 | Antecedente exploratorio, con partición y aislamiento anteriores. |
| Control final de los experimentos | 1.653 citas de validación interna; media de tres semillas | 0,832861 | 0,826120 | Se usa para comparar condiciones dentro de los experimentos. |
| Modelos congelados seleccionados | Misma validación interna; semilla 42 | 0,830298 | 0,830071 | Son las exportaciones concretas llevadas al test. |
| Test humano final | 2.968 citas humanas propias; modelos congelados | **0,796728** | **0,799951** | Comparación final de A4 para A6. |

**Fuentes de la tabla 4:** primera fila: [resultados iniciales](../README_TOP1.md), apartado “Lectura del resultado”, excluyendo su variante Top-1; segunda: [comparación de experimentos](Experimentos/Comparacion_Reparto_vs_Pesos.md); tercera y cuarta: [validation_vs_test.csv](https://drive.google.com/file/d/1Tk05o-bTzYLhpwppDSooen1_je5D42Gd/view?usp=drivesdk) y [test_comparison.csv](https://drive.google.com/file/d/1EZKtyGUeo9rgI3A7fBH1q_TkbfCXl6wO/view?usp=drivesdk). Notebook inicial: [corrida 3](../pruebascolab/A4_SciBERT_G15_Colab_A100_corrida3_VSCode.ipynb); cierre experimental: [reparto recuperado](Experimentos/SciBERT_Reparto_Tokens_Recuperacion.ipynb).

**No se deben restar las filas como si midieran una evolución sobre el mismo test.** Cambian las citas, las referencias o el número de semillas. No usamos Top-1 como resultado principal ni lo incluimos en las tablas de entrega para A6.

Probamos búsqueda de hiperparámetros, hasta 12 épocas con paciencia 3 y repeticiones con semillas 42, 17 y 73. Cada estudio registró 28 entrenamientos: 12 de búsqueda y 16 adicionales; dos controles se reutilizaron dentro de cada estudio.

| Condición de validación | F1 macro medio base | F1 macro medio Top-3 |
|---|---:|---:|
| Control: contexto 192, sin pesos | **0,832861** | **0,826120** |
| Contexto 128 | 0,832815 | 0,820338 |
| Contexto 256 | 0,825601 | 0,824624 |
| Pesos de raíz inversa | 0,828316 | 0,824820 |
| Pesos de inversa limitada | 0,827102 | 0,815310 |

**Fuente de la tabla 5:** [comparación auditada](Experimentos/Comparacion_Reparto_vs_Pesos.md), `condition_summary.csv` en [Drive reparto](https://drive.google.com/drive/folders/1UvtcwLFYgN48_atCVkB5XECjW24dvXu6) y [Drive pesos](https://drive.google.com/drive/folders/1hZcQX7bbX5QcggydmSmR4d-tOH7ySdnu). Ejecuciones: [reparto](Experimentos/SciBERT_Reparto_Tokens_Recuperacion.ipynb) y [pesos](Experimentos/SciBERT_Pesos_Clases.ipynb).

Ninguna alternativa superó el promedio del control de su entrada. Los estudios seleccionaron los mismos archivos de pesos, verificados mediante SHA-256; los controles coincidentes no son evidencia independiente de una segunda mejora. La media de semillas describe estabilidad, no un intervalo de confianza. El Top-3 seleccionado presentó algún recorte de evidencia en el **91,59 % de la validación**, conservando en promedio **59,32 % de sus tokens**; son medidas distintas. Fuente: [conclusiones del reparto](Experimentos/Conclusiones_Reparto_Tokens.md).

## 4. Modelos que entregamos

| Modelo | Entrada en texto plano | Salida | Configuración seleccionada |
|---|---|---|---|
| Base | `context`, `title`, `abstract` del citado | Una etiqueta, nueve probabilidades y auditoría del texto | Contexto hasta 192; LR 3e-5; weight decay 0,1; sin pesos; semilla 42; mejor época 5 |
| Top-3 | `context`, tres `chunks` con `text` y `section` | Mismo contrato de salida | Mismos ajustes; mejor época 7 |

**Fuente de la tabla 6:** [selección congelada](../Evaluacion_Final/seleccion_congelada.json), [evaluation_protocol.json](https://drive.google.com/file/d/1Vclg6zlOQ82m1twDdVt2dtI4bGtYO80Q/view?usp=drivesdk) y [notebook de evaluación](../Evaluacion_Final/SciBERT_Evaluacion_Final.ipynb), secciones 2–4. [Ejemplos reales de ambas entradas](https://drive.google.com/file/d/1bXQSZM5LWi2aMkY5wYnLsxrC3_fJueBI/view?usp=drivesdk).

Las dos variantes parten de `allenai/scibert_scivocab_uncased`, revisión `24f92d32b1bfb0bcaf9ab193ff3ad01e87732fc1`. El máximo es **512 tokens totales**, incluidos separadores y encabezados. La entrada se tokeniza dentro del paquete; no se envían embeddings ya calculados al clasificador. Para la interfaz deben conservarse la política del exportado y el orden de etiquetas: no reconstruir una concatenación diferente.

Paquetes en `MAIA_TESIS/a4/g15_scibert_reparto_v2_01/` dentro del [estudio fuente en Drive](https://drive.google.com/drive/folders/1UvtcwLFYgN48_atCVkB5XECjW24dvXu6):

- `scibert_base_final.zip`: modelo base.
- `scibert_fragmentos_final.zip`: modelo Top-3.
- Versiones sin comprimir: `trials/grid_base_contexto_192_lr3em05_wd0p1_s42/model/` y `trials/grid_fragmentos_contexto_192_lr3em05_wd0p1_s42/model/`.
- Conservar juntos pesos, tokenizador, `inference.py`, `input_policy.json`, `label_mapping.json` y contratos. `inference.py` proporciona la clase para cargar y predecir; no es una API web desplegada ni un recuperador de fragmentos.

Identificación inequívoca: SHA-256 de `model.safetensors` base `985b9ee61228618e37d2883fdfa004c2f47d5d5628c8668c9187771d8a98ade4`; Top-3 `19c8ddb575e24aa043c934c6206639362f3605041a7f5806ec851e0da1f637d7`. Fuente: [selección congelada](../Evaluacion_Final/seleccion_congelada.json).

## 5. Resultado final para A6

| Modelo | n | P macro | R macro | F1 macro | P micro | R micro | F1 micro | Accuracy |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Base | 2968 | 0,8181 | 0,7930 | 0,7967 | 0,7921 | 0,7921 | 0,7921 | 0,7921 |
| Top-3 | 2968 | 0,8220 | 0,7981 | 0,8000 | 0,7948 | 0,7948 | 0,7948 | 0,7948 |

**Fuente de la tabla 7:** [test_comparison.csv](https://drive.google.com/file/d/1EZKtyGUeo9rgI3A7fBH1q_TkbfCXl6wO/view?usp=drivesdk), cálculo en sección 7 del [notebook ejecutado](../Evaluacion_Final/Historico/Evaluacion_2026-11-13_01/SciBERT_Evaluacion_Final.ipynb). Redondeo a cuatro decimales; conservar el CSV para cálculos. En esta clasificación de una etiqueta por ejemplo, micro P/R/F1 coinciden con accuracy.

| Clase | Soporte test | P base | R base | F1 base | P Top-3 | R Top-3 | F1 Top-3 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Background | 330 | 0,5312 | 0,8000 | 0,6385 | 0,5312 | 0,8515 | 0,6542 |
| Gap | 310 | 0,7749 | 0,7774 | 0,7762 | 0,7752 | 0,7677 | 0,7715 |
| Basis | 322 | 0,7459 | 0,8571 | 0,7977 | 0,7634 | 0,8820 | 0,8184 |
| Comparison | 313 | 0,7716 | 0,8850 | 0,8244 | 0,7550 | 0,8371 | 0,7939 |
| Application | 400 | 0,8262 | 0,7725 | 0,7984 | 0,8646 | 0,7500 | 0,8032 |
| Improvement/Modification | 268 | 0,8995 | 0,6343 | 0,7440 | 0,8750 | 0,6791 | 0,7647 |
| Evidence | 386 | 0,8824 | 0,6606 | 0,7556 | 0,9038 | 0,6088 | 0,7276 |
| Identification of the Originator | 324 | 0,9658 | 0,8704 | 0,9156 | 0,9600 | 0,8889 | 0,9231 |
| Further Reading | 315 | 0,9652 | 0,8794 | 0,9203 | 0,9698 | 0,9175 | 0,9429 |

**Fuente de la tabla 8:** [test_per_class.csv](https://drive.google.com/file/d/1Ka5CmG6_0Wie63v9NY28AOcFwc8Nr4gZ/view?usp=drivesdk); misma población para las dos entradas. Los reportes completos están en [base](https://drive.google.com/drive/folders/1lJ5_0eYwX6yHaV2BY9FbBLzeWFC5XFdO) y [Top-3](https://drive.google.com/drive/folders/1kS1Hado7p99rGx1lC5OaBPz4LKEKczXz).

Top-3 aumenta F1 en seis clases y disminuye en tres, sin que estas diferencias descriptivas sean pruebas individuales de significancia. Improvement/Modification pasa de **0,7440 a 0,7647**, con 268 citas humanas; Evidence baja de **0,7556 a 0,7276**. Background presenta el F1 más bajo en ambos modelos. Las causas de esas confusiones requieren lectura manual; los resultados no demuestran por sí solos problemas de claridad del texto.

| Comparación pareada | Valor |
|---|---|
| Diferencia F1 macro Top-3 − base | +0,0032234 = +0,32 puntos porcentuales |
| IC percentil del 95 % | [−0,0075356; +0,0138951], o [−0,75; +1,39] puntos |
| Unidad de remuestreo | Artículo citante; 2.764 grupos, 2.968 citas |
| Repeticiones y semilla | 2.000; 20261113 |
| Interpretación | El intervalo incluye cero; no establece superioridad ni equivalencia |

**Fuente de la tabla 9:** [paired_test_comparison.json](https://drive.google.com/file/d/1pQVIRBFNSN0x0xJJDuRg13Q45GFayahB/view?usp=drivesdk) y sección 8 del notebook. [Distribución del bootstrap](https://drive.google.com/file/d/1Rau7YLx-N39LVjeFbKeuEXG6XqBomMsE/view?usp=drivesdk).

Para las figuras del informe: [matrices de confusión](https://drive.google.com/file/d/1O8chPfUHbANaghlBC-1HAEEdUzg3vCwT/view?usp=drivesdk), [comparación por categoría](https://drive.google.com/file/d/13IivBYBslMbXYU9emgdma7K2TKWUJR3J/view?usp=drivesdk) y [validación frente a test](https://drive.google.com/file/d/1YalVTWGbh2vSfsduMDTt4c6CdN5p-6PI/view?usp=drivesdk). También hay [copias locales de las cinco figuras](../Evaluacion_Final/Historico/Evaluacion_2026-11-13_01/Figuras/). En las matrices las filas son referencias y las columnas predicciones; las normalizadas permiten comparar clases con soportes distintos. No presentar validación frente a test como una mejora o caída causal.

## 6. Eficiencia: evidencia disponible para A7

| Modelo | Media ms/ejemplo | Mediana ms/ejemplo | p95 ms/ejemplo | Media s/ejemplo |
|---|---:|---:|---:|---:|
| Base | 8,8109 | 8,8299 | 9,0462 | 0.008810937743598608 |
| Top-3 | 10,5772 | 10,5561 | 10,8550 | 0.010577212279987027 |

**Fuente de la tabla 10:** [latency_summary.csv](https://drive.google.com/file/d/137QGrlFk5QmFJUAwtemCc9Cqd-RLrYh9/view?usp=drivesdk); entorno [environment.json](https://drive.google.com/file/d/16sbsabrdXkFqbRiMZxFBPpqwT6s4n--W/view?usp=drivesdk). Evaluación en NVIDIA A100 de 40 GB, PyTorch 2.11.0, FP32, atención eager, TF32 desactivado y lotes de 32.

**Interpretación de la medición:** son promedios del tiempo de cada lote por ejemplo, incluyendo tokenización, transferencias y forward. Excluyen carga del modelo, calentamiento y E/S de resultados. La mediana y el p95 describen esos promedios, no solicitudes individuales cronometradas. No incluyen recuperación del Top-3, red ni interfaz: no compararlos directamente con latencia de una llamada API sin declarar o igualar el alcance.

A7 puede reutilizar estas cifras como eficiencia por lotes del clasificador. Para comparar experiencia interactiva, medir adicionalmente lote 1 y el flujo completo con iguales condiciones de entrada. Para costos, documentar tiempo computacional y tarifa/unidades realmente consumidas; no asumir costo cero por créditos ni convertirlo a dinero sin evidencia. Para APIs, registrar proveedor, modelo/versión, fecha, tokens de entrada/salida, reintentos y precio aplicado. No se reporta una tasa cero de errores de formato por deducción: deben definirse denominador y criterio, y distinguir ejecución terminada de validez de cada respuesta.

## 7. Archivos para que los compañeros continúen

Todo el cierre está en [Drive: evaluación final](https://drive.google.com/drive/folders/1eXx0tR2C8813sXzNvt8n39fQNMwbDg2E), ruta `MAIA_TESIS/a4/g15_scibert_test_B_final_01/`.

| Uso | Archivo o enlace | Cómo utilizarlo |
|---|---|---|
| Población común | [test_instances.csv](https://drive.google.com/file/d/1rocRYM00e745z3tbb3Wff2QhdwVNglJS/view?usp=drivesdk) | Mismos 2.968 `inst_key`; leer identificadores como texto para conservar ceros. |
| Predicciones base | [base/test_predictions.csv](https://drive.google.com/file/d/1LFtcomqM3AH5yNXIPjGxEG53QRZZgT7i/view?usp=drivesdk) | Unir por `inst_key`, nunca por posición de fila. |
| Predicciones Top-3 | [fragmentos/test_predictions.csv](https://drive.google.com/file/d/1KTNvUfz7aGuxVB5vXm7em0t8Hnp8mABK/view?usp=drivesdk) | Misma población y etiquetas de referencia que base. |
| Métricas agregadas | [test_comparison.csv](https://drive.google.com/file/d/1EZKtyGUeo9rgI3A7fBH1q_TkbfCXl6wO/view?usp=drivesdk) | Incorporar los dos encoders a la tabla conjunta de A6. |
| Métricas por clase | [test_per_class.csv](https://drive.google.com/file/d/1Ka5CmG6_0Wie63v9NY28AOcFwc8Nr4gZ/view?usp=drivesdk) | P/R/F1 y soporte de las nueve clases. |
| Confusiones y errores | [base](https://drive.google.com/drive/folders/1lJ5_0eYwX6yHaV2BY9FbBLzeWFC5XFdO), [Top-3](https://drive.google.com/drive/folders/1kS1Hado7p99rGx1lC5OaBPz4LKEKczXz), [error_examples.csv](https://drive.google.com/file/d/17FesoOTvOqZyg9H7DrAyiVfxGbNLFeBN/view?usp=drivesdk) | CSV de matrices absolutas/normalizadas, errores y ejemplos reales. |
| Latencia | [latency_summary.csv](https://drive.google.com/file/d/137QGrlFk5QmFJUAwtemCc9Cqd-RLrYh9/view?usp=drivesdk) | Reutilizar únicamente con la definición de la sección 6. |
| Entradas de ejemplo | [two_real_examples.json](https://drive.google.com/file/d/1bXQSZM5LWi2aMkY5wYnLsxrC3_fJueBI/view?usp=drivesdk) | Ver forma de los payloads; las referencias se muestran aparte y no se envían al modelo. |
| Auditorías | [data_audit.json](https://drive.google.com/file/d/1tjFmQp_xqV7TjHvduwtxzDjVAVFZcYgu/view?usp=drivesdk), [reconstruction_audit.json](https://drive.google.com/file/d/1e-bwpYfx9h2O-RR-kKQ6RYiHkHmE03zp/view?usp=drivesdk) | Comprobar fuentes, separación, reconstrucción y orden. |
| Cierre y huellas | [FINAL_COMPLETE.json](https://drive.google.com/file/d/1hLQOiczrQYwoA4YH2a_v6Xw3HyJqhptT/view?usp=drivesdk) | Verificar SHA-256 de los reportes antes de consumirlos. |
| Historial | [carpeta _tracking](https://drive.google.com/drive/folders/1jIUFzAIGCTVwu1l2tJdFpNEx5jIG9a-8) | Snapshot final: `20261113T211318096884Z_0ff99e6a`; experimento `G15_SciBERT_Test_Final`. |

**Fuente de la tabla 11:** inventario del cierre de Drive consultado el 13 de noviembre de 2026, [FINAL_COMPLETE.json](https://drive.google.com/file/d/1hLQOiczrQYwoA4YH2a_v6Xw3HyJqhptT/view?usp=drivesdk) y [guía de evaluación](../Evaluacion_Final/README.md). El historial del test es independiente de los historiales de entrenamiento; respetar `canonical_root` del snapshot al restaurarlo en el visor.

Los CSV de predicciones incluyen `inst_key`, documentos, referencia, predicción, nueve columnas `score_<clase>`, tiempos y procedencia de la medición. Las probabilidades son softmax del clasificador; no acreditan calibración de confianza. El orden de clases es el de la tabla 3 y `label_mapping.json`.

### Reglas para una comparación conjunta válida

1. Usar las mismas citas humanas y el mismo esquema de nueve etiquetas. Verificar unicidad, cobertura completa y coincidencia de referencias después de unir por `inst_key`.
2. Mantener separadas las dos condiciones de entrada. Para A5, la guía p. 8 define como base contexto + título y resumen; cualquier variante de evidencia debe quedar identificada para interpretar la comparación.
3. Fijar prompts y parámetros con datos de desarrollo. No usar el test propio ni sus documentos como ejemplos few-shot o para corregir modelos/prompts tras ver el resultado.
4. Registrar las variantes zero-shot/few-shot y genérico/específico por categoría requeridas por A5. Las probabilidades softmax del encoder y los puntajes solicitados a una API no son automáticamente confidencias calibradas comparables.
5. Tratar explícitamente respuestas inválidas, reintentos y faltantes; no quitar silenciosamente casos difíciles ni cambiar el denominador de un modelo.
6. Si otra fase necesita datos que chocan con este protocolo, acordarlo y documentarlo antes de comparar; un test de otro grupo no es automáticamente la misma población de esta entrega.

Estas reglas trasladan los requisitos de [la guía, pp. 6–8](https://github.com/germarodr/Proyecto_Grado_MAIA/blob/58f0bb8/Papers/Propuesta_Proyecto%20PLN.pdf) al intercambio entre fases; no implementan el trabajo de los compañeros.

## 8. Cómo citar los resultados en el informe

Texto sugerido, conservando fuentes y alcance:

> Grupo 15 (2026). Evaluación final de A4, ejecución `g15_scibert_test_B_final_01`, 13 de noviembre de 2026. Sobre 2.968 citas con referencias humanas y aislamiento documental, SciBERT base obtuvo F1 macro 0,7967 y SciBERT Top-3 0,8000. La diferencia de +0,32 puntos porcentuales presentó IC del 95 % [−0,75; +1,39], mediante bootstrap pareado por artículo citante, sin establecer una ventaja clara de Top-3. Fuentes: notebook ejecutado, `test_comparison.csv`, `paired_test_comparison.json` y cierre `FINAL_COMPLETE.json`.

En cada tabla del informe citar su CSV específico, el ID de ejecución y la fecha; añadir el enlace y la fecha real de consulta. Para metodología citar además la guía o la propuesta; para cifras propias citar los archivos de resultados. Las fuentes internas no sustituyen la referencia bibliográfica del artículo original de SciBERT que utilice la tesis. Cuando compartan este Markdown, mantenerlo dentro del repositorio para conservar los enlaces relativos; los enlaces de Drive permiten consultar los resultados por separado con los permisos existentes.

## 9. Conclusiones para el reporte

Completamos la comparación de las dos entradas de A4, con selección sobre validación interna y evaluación posterior sobre referencias humanas. La búsqueda de hiperparámetros, las repeticiones y las pruebas de pesos y reparto de tokens no aportaron una alternativa que superara el control medio correspondiente. El test final produjo F1 macro 0,7967 para base y 0,8000 para Top-3; su diferencia no establece superioridad. Fuentes: tablas 4, 5, 7 y 9.

Las mejoras y pérdidas dependen de la categoría: Top-3 sube en Improvement/Modification y baja en Evidence y Comparison. Persisten representación desigual y recorte de evidencia. El estudio no permite atribuir causalmente los errores a falta de datos, al recorte o a textos poco claros. La validez se limita al conjunto y a los criterios de selección utilizados. Fuentes: tablas 3 y 8, y [auditoría de recorte](Experimentos/Conclusiones_Reparto_Tokens.md).

A4 entrega modelos identificados, predicciones, métricas, figuras y trazabilidad para continuar A6 y A7. La aceptación de los mínimos por categoría y la interpretación de la reserva humana frente al uso cruzado del contrato se deben acordar con el asesor. Disponer de métricas finales no acredita por sí solo el cumplimiento completo de la guía ni la finalización de las otras fases. Fuentes: tabla 1, [FINAL_COMPLETE.json](https://drive.google.com/file/d/1hLQOiczrQYwoA4YH2a_v6Xw3HyJqhptT/view?usp=drivesdk) y [verificación local de ejecución](../Evaluacion_Final/Verificacion_Ejecucion.json).

