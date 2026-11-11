# Solicitudes de insumos para el informe final

**T_B** es el conjunto de prueba del Grupo 15, validado por humanos en A3; las instancias **evaluables** son las que tienen una función de cita asignada.

## A1 — Corpus y recuperación de fragmentos

### A1-1. Razón de la elección de los subcampos del piloto

**Contexto.** El corpus piloto tomó como artículos citantes los de cs.CV, cs.SI, cs.HC, cs.CY y cs.ET, y el 97,8 % de sus contextos resultó de cs.CV. El evaluador del primer informe pidió explicar esa concentración. El artículo (Sección III-A) debe decir por qué se eligieron esos cinco subcampos.

**Qué necesitamos.** Un párrafo corto (3 a 5 líneas) con el criterio real de la elección. Por ejemplo: disponibilidad de citas resolubles, tamaño, interés del grupo, una restricción de cómputo o una decisión del experto. Si hubo un documento, reunión o mensaje donde se decidió, indica cuál.

### A1-2. Distribución por subcampo de los artículos citantes

**Contexto.** Para mostrar cuánto se redujo la concentración en cs.CV tras ampliar el corpus con cs.LG, cs.CL y cs.DS, la TABLA II del artículo necesita la distribución por subcampo.

**Requiere** A3-1.

**Qué necesitamos.** Un CSV con una fila por categoría primaria de arXiv del **artículo citante** (cs.CV, cs.LG, etc.) y estas columnas:

| Columna | Contenido |
|---|---|
| `categoria_primaria` | Categoría arXiv del artículo citante |
| `n_train`, `pct_train` | Instancias y porcentaje en entrenamiento + validación (31.265 instancias) |
| `n_test`, `pct_test` | Instancias y porcentaje en las instancias evaluables de T_B |

### A1-3. Fragmentos truncados a 512 tokens en la recuperación

**Contexto.** La recuperación codifica cada fragmento con SciBERT, que acepta hasta 512 tokens; los fragmentos más largos se recortan. El evaluador preguntó por este procedimiento, y la Sección III-B debe decir qué porcentaje de fragmentos se truncó.

**Qué necesitamos.** Para el **piloto** y la **ampliación**, en texto o CSV: total de fragmentos codificados, número de fragmentos truncados y porcentaje.

### A1-4. Evaluación humana de la recuperación (P@3)

**Contexto.** La recuperación elige, para cada cita, los 3 fragmentos del artículo citado más similares al contexto (Top-3). Las similitudes coseno son altas y muy parecidas entre sí (≈0,91), así que no prueban que los fragmentos sean útiles. La propuesta comprometió una evaluación manual (*precision@3*), y el evaluador del primer informe señaló que faltaba.

**Requiere** A3-1.

**Qué necesitamos.** Los resultados de una evaluación manual hecha así:
1. **Muestra:** entre 150 y 200 instancias evaluables de T_B, elegidas al azar con semilla fija.
2. **Línea base:** para las mismas instancias, 3 fragmentos elegidos al azar del mismo artículo citado (semilla fija).
3. **Anotación:** dos personas, de forma independiente y sin saber qué fragmentos son Top-3 y cuáles aleatorios (mezclados y en orden aleatorio). Cada una marca cada fragmento como **relevante** (aporta evidencia sobre lo que el artículo citado aporta a la cita) o **no relevante**, leyendo la oración de la cita, el párrafo citante y el fragmento.

**Entregar:**
- P@3 del Top-3 y de la línea base (proporción media de fragmentos relevantes por instancia), por anotador y en consenso, y κ de Cohen entre los dos anotadores, en un CSV.
- Tamaño final de la muestra y semillas usadas.

---

## A3 — Validación humana del conjunto de prueba (T_B)

### A3-1. Resultados finales de la validación humana

**Contexto.** Con los resultados finales de la validación humana se llenan la TABLA III (conjunto de prueba por función), la TABLA VI (indicadores de validación humana) y el resumen. Además, son la entrada obligatoria de A4-2 y A5-3.

**Qué necesitamos.** Tres archivos:
1. `test_set_gold.jsonl`: una fila por instancia de ambos conjuntos de prueba, con la etiqueta final (`gold_primary`) y si es evaluable (`in_eval`).
2. `iaa_report.md`: κ de Cohen, α de Krippendorff (nominal y MASI), tasas de corrección por función y por anotador, adjudicación.
3. `manifest_metrics.json`: hashes de entradas y salidas y commit del código.

---

## A4 — Clasificador SciBERT

**Contexto común.** Se comparan dos SciBERT ajustados con las mismas instancias, partición y semilla, que solo difieren en la información del artículo citado:
- **base:** contexto + título y resumen del citado;
- **fragmentos:** contexto + los 3 fragmentos recuperados, con su sección.

### A4-1. Entrenamiento de SciBERT con fragmentos

**Qué necesitamos.** Los resultados del entrenamiento de SciBERT con fragmentos:
1. Métricas de validación de **ambas** configuraciones, base y fragmentos (precisión, exhaustividad y F1 macro y micro), en un CSV.
2. F1 por función en validación de la configuración con fragmentos.
3. Confirmación de que se entrenó con los mismos datos, partición (`G15-A4-split-v1`), semilla (42) e hiperparámetros que la base.

### A4-2. Evaluación de ambos SciBERT sobre T_B

**Requiere** A3-1 y A4-1.

**Qué necesitamos.** Evaluar ambas configuraciones, una sola vez, sobre el conjunto de prueba final de A3-1, y entregar estos resultados:

| Archivo (base y fragmentos) | Uso en el artículo |
|---|---|
| `test_comparison.csv` | TABLA VII: precisión, exhaustividad y F1 macro y micro |
| `paired_test_comparison.json` | Diferencia de F1 macro fragmentos − base con IC 95 % *bootstrap* pareado por artículo citante |
| `test_classification_report.json` | Fig. 3: F1 por función |
| `test_confusion.csv` y `test_confusion.png` | Fig. 4: matrices de confusión |
| `test_cited_seen_unseen.json` | F1 para artículos citados vistos y no vistos en entrenamiento |
| `test_predictions.csv` | Ejemplos de error (A4-5) y cálculo común de métricas (A6) |

### A4-3. Configuración real de entrenamiento

**Qué necesitamos**, para cada configuración: épocas efectivas (con parada temprana), época del mejor checkpoint, versiones de torch, transformers, scikit-learn y MLflow, y cualquier diferencia frente a la TABLA IV del artículo:

| Parámetro | Valor planeado |
|---|---|
| Modelo | `allenai/scibert_scivocab_uncased` |
| LR / épocas | 2e-5 / hasta 4, paciencia 2 |
| Batch efectivo | 32 (16 × acumulación 2) |
| Optimizador | AdamW, *weight decay* 0,01, *warmup* 10 %, lineal |
| Precisión | BF16, A100 |
| Semilla | 42 |

### A4-4. Decisión sobre el desbalance de clases

**Contexto.** Las funciones están muy desbalanceadas: en entrenamiento hay 10.957 Background frente a 487 Improvement/Modification. La corrida usa entropía cruzada **sin pesos por clase**. El evaluador del primer informe pidió describir la configuración del ajuste.

**Qué necesitamos.** Una de dos:
- **(a)** Mantener la entropía sin pesos: entregar la justificación en 2 o 3 líneas y el F1 por función en validación que la respalda.
- **(b)** Probar pesos por clase (inversos a la frecuencia) solo en validación y entregar la comparación de F1 macro. Si se adopta, debe aplicarse a ambas configuraciones antes de A4-2.

### A4-5. Ejemplos de errores de SciBERT

**Requiere** A4-2.

**Qué necesitamos.** Dos instancias de T_B mal clasificadas que representen los errores más frecuentes según la matriz de confusión: `inst_key`, función de referencia, predicción de cada configuración y 2 o 3 líneas sobre por qué falla. El artículo citará como mucho una frase del contexto.

---

## A5 — Modelo de lenguaje comercial

**Contexto común.** El artículo compara el mejor SciBERT con un modelo de lenguaje comercial, sin ajuste, en modalidades *zero-shot* y *few-shot*. La entrada es la misma de la configuración base: contexto de la cita, título y resumen del artículo citado.

### A5-1. Identificación del modelo

**Qué necesitamos.** Proveedor, nombre comercial y **versión exacta** del modelo (el identificador de la API, por ejemplo con fecha de versión), fecha de las consultas, precio por millón de tokens de entrada y de salida en esa fecha, y por qué se eligió. Incluye el enlace oficial a la página del modelo o a su documentación.

### A5-2. Protocolo y prompts

**Qué necesitamos.**
1. **Prompts completos** *zero-shot* y *few-shot* (van al Apéndice A).
2. **Ejemplos *few-shot*:** cuántos, de dónde salen y cómo se garantiza que **ningún ejemplo provenga de T_B ni de sus artículos citantes**.
3. **Formato de salida pedido:** el artículo indica que es JSON con un puntaje entre 0 y 1 por función; confirma o corrige.
4. **Parámetros:** temperatura y demás parámetros de decodificación.
5. **Robustez:** reintentos, cómo se maneja una respuesta inválida y qué etiqueta se asigna si no se puede leer.

### A5-3. Predicciones sobre T_B

**Requiere** A3-1 (lista de instancias evaluables).

**Qué necesitamos.** `A5-3_predicciones.csv`, una fila por instancia evaluable de T_B y por modalidad, con el formato común de predicciones (sección A6) más las columnas propias del modelo comercial:

| Columna | Contenido |
|---|---|
| `inst_key` | Identificador de la instancia |
| `modalidad` | `zero-shot` o `few-shot` |
| `pred_label` | Función predicha (una de las 9 etiquetas exactas) |
| `score_<función>` | Puntaje de cada función, 0 a 1 (9 columnas) |
| `latency_ms` | Tiempo de la llamada, en milisegundos |
| `respuesta_valida` | 1 si la respuesta se pudo leer; 0 si no |
| `tokens_entrada`, `tokens_salida` | Conteo informado por la API |
| `costo_usd` | Costo calculado con el precio de A5-1 |
| `intentos` | Número de llamadas usadas |

### A5-4. Ejemplos de errores del modelo comercial

**Requiere** A5-3.

**Qué necesitamos.** Igual que A4-5, para el modelo comercial (dos instancias; una de ellas, un caso donde difiera de SciBERT).

---

## A6 — Evaluación comparativa

**Contexto común.** Con un mismo script se calculan, para los cuatro modelos (SciBERT base, SciBERT con fragmentos, modelo comercial *zero-shot* y *few-shot*), precisión, exhaustividad y F1 macro y micro, F1 por función, matrices de confusión y la diferencia de F1 macro entre fragmentos y base con su IC 95 % *bootstrap* pareado por artículo citante (TABLA VII, Figs. 3 y 4). Para que los cuatro sean comparables, las predicciones de A4-2 y A5-3 deben cubrir las mismas instancias evaluables de T_B y traer, como mínimo, estas columnas (formato común del plan de trabajo):

| Columna | Contenido |
|---|---|
| `inst_key` | Identificador de la instancia |
| `pred_label` | Función predicha, escrita exactamente como en la guía de anotación |
| `score_<función>` | Puntaje de cada función, 0 a 1 (9 columnas) |
| `latency_ms` | Tiempo de inferencia por ejemplo, en milisegundos |

Las predicciones de SciBERT sirven aunque usen otros nombres de columna, siempre que traigan la etiqueta predicha y la probabilidad de cada función.

### A6-1. Predicciones de validación de SciBERT base

**Contexto.** Permite probar el script de métricas antes de tener los resultados sobre T_B.

**Qué necesitamos.** Las predicciones sobre validación de la corrida del 2 de noviembre (3.226 filas, con la etiqueta predicha y la probabilidad de cada función) en un CSV, y su reporte de clasificación, para comprobar que el script reproduce las métricas que reportó la corrida.

---

## A7 — Eficiencia, latencia y costo

**Contexto común.** La TABLA VIII compara el costo de entrenar SciBERT con el costo por tokens del modelo comercial, la latencia por ejemplo de cada modelo y la tasa de respuestas inválidas del modelo comercial. Los costos se expresan por cada 1.000 ejemplos para que sean comparables.

### A7-1. Costo de entrenamiento de SciBERT

**Qué necesitamos**, para cada configuración: GPU usada, tiempo de entrenamiento en horas (total y hasta el mejor checkpoint), pico de memoria y precio por hora de esa GPU en dólares, con su fuente (por ejemplo, el plan de Colab usado). Con ese precio, el costo de SciBERT se expresa en dólares por cada 1.000 ejemplos, igual que el del modelo comercial.

### A7-2. Latencia de inferencia de SciBERT

**Qué necesitamos**, para cada configuración: tiempo medio por ejemplo en milisegundos, hardware, tamaño de lote, número de ejemplos medidos y si incluye la tokenización. Si se mide por lote, `latency_ms` puede ser el tiempo del lote dividido por su tamaño; indícalo.

### A7-3. Costo facturado del modelo comercial

**Contexto.** El costo por llamada viene en A5-3, calculado con el precio de A5-1.

**Qué necesitamos.** El costo total que reporta el proveedor para las corridas *zero-shot* y *few-shot*, para contrastarlo con el calculado.
