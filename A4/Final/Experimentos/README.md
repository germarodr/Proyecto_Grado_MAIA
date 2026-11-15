# Experimentos de A4: reparto del texto e importancia de las clases

Estos dos notebooks continúan las pruebas con training v2 y el mismo aislamiento
por documento de la corrida final. Conservan únicamente las dos entradas de la
propuesta: **contexto + título + abstract**, y **contexto + Top-3 + secciones**.
El test humano propio no participa en el aprendizaje ni en la selección.

| Notebook | Pregunta | Condiciones |
|---|---|---|
| [SciBERT_Reparto_Tokens.ipynb](SciBERT_Reparto_Tokens.ipynb) | ¿Qué reparto del espacio ayuda más? | Contexto máximo de 128, 192 o 256 tokens; entropía cruzada sin pesos. |
| [SciBERT_Pesos_Clases.ipynb](SciBERT_Pesos_Clases.ipynb) | ¿Ayuda dar más importancia a las clases escasas? | Sin pesos, raíz inversa o inversa limitada; contexto máximo de 192 tokens. |

Para retomar reparto tras la desconexión se preparó
[SciBERT_Reparto_Tokens_Recuperacion.ipynb](SciBERT_Reparto_Tokens_Recuperacion.ipynb).
Conserva el mismo código y el ID `g15_scibert_reparto_v2_01`, con las mismas
particiones, parámetros y respaldos. Esta copia evita arrastrar la cola del
servidor anterior en el editor; no constituye otro experimento. Usa una sola de
las dos pestañas de reparto para ejecutar. El archivo original conserva las
salidas de la sesión interrumpida.

## Cómo se comparan

En ambos estudios usamos **12 épocas máximas y paciencia 3**, batch efectivo 32,
las mismas particiones y las semillas 42, 17 y 73. El modelo sigue admitiendo 512
tokens totales. Cada ejemplo de Top-3 conserva texto y sección de los tres
fragmentos originales, sin volver a recuperarlos ni resumirlos.

Cada notebook hace primero una búsqueda sobre el control (192 tokens de contexto,
sin pesos): ritmos `[1e-5, 2e-5, 3e-5]` y regularización `[0.01, 0.1]` para ambas
entradas, **12 entrenamientos**. El mejor control por F1 macro FP32 fija los
parámetros de cada entrada antes de las pruebas siguientes.

Después compara las tres condiciones con las tres semillas y esos parámetros
fijos. Los dos controles de la semilla 42 se verifican y reutilizan. Hay **18
resultados comparables y 16 entrenamientos nuevos**, para un total de **28
entrenamientos por notebook**. Base y Top-3 tienen búsquedas equivalentes y pueden
elegir parámetros distintos; dentro de cada entrada solo cambia la condición.

Seleccionamos la condición por F1 macro **medio de tres semillas**, con preferencia
por el control si empata, y conservamos el modelo de la semilla 42. Las diferencias
frente al control están emparejadas por semilla. La desviación entre semillas no
se presenta como un intervalo de confianza ni como prueba de significancia.

Los pesos se calculan solo con las 11.616 filas de entrenamiento, en el orden fijo
de las nueve clases. Si `b_c = N / (9 × n_c)`, las alternativas parten de
`sqrt(b_c)` y de `clip(b_c, 0.25, 4)`. Cada vector se divide por su media ponderada
según las frecuencias de entrenamiento. Las dos entradas reciben el mismo vector.
La pérdida sigue siendo entropía cruzada; no hay sobremuestreo ni ejemplos nuevos.

## Ejecución en paralelo

1. Abre los dos archivos en el editor.
2. Conecta **cada notebook a un servidor distinto**. No basta abrir dos pestañas
   del mismo servidor. La primera celda comprueba la GPU requerida y BF16.
3. Autoriza Drive en cada servidor cuando aparezca la solicitud.
4. Ejecuta las secciones en orden, con un solo responsable de iniciar las celdas.
   Si Codex las supervisa, no uses «Run All» en paralelo en esa misma pestaña.
5. Ante una desconexión, recupera ese notebook en una sola sesión y ejecuta desde
   la primera sección. Los resultados completos se verifican antes de reutilizarse;
   un entrenamiento incompleto continúa desde un checkpoint válido.

Los notebooks son autónomos: no requieren subir archivos `.py`. Leen las entradas
desde `MAIA_PROYECTO/a2/batches_norw`, `MAIA_PROYECTO/a3` y las carpetas
`MAIA_TESIS/TrainingData_Grupo15{,_v2}`. El primer bloque muestra distribución de
clases, procedencia de etiquetas y los recuentos reales: **11.616 train / 1.653
validación**. La autorización de Drive puede ser interactiva.

## Resultados e historiales separados

| Estudio | Resultados en Drive | Experimento MLflow |
|---|---|---|
| Reparto | `MAIA_TESIS/a4/g15_scibert_reparto_v2_01/` | `G15_SciBERT_Reparto` |
| Pesos | `MAIA_TESIS/a4/g15_scibert_pesos_v2_01/` | `G15_SciBERT_Pesos_Clases` |

Cada estudio escribe snapshots completos en su propia carpeta
`<estudio>/_tracking/snapshots/`. Su base local está en
`/opt/maia/a4_tracking_experiments/<ID_DEL_ESTUDIO>/mlflow.db`. El bloqueo local
protege el mismo estudio dentro de un servidor; usa una sola instancia por ID.
Los snapshots de estos experimentos **no se mezclan** con el historial principal
ni se restauran en la otra prueba. Para consultarlos en el visor, hay que respetar
la ruta `canonical_root` de su manifiesto al montar la base y los artefactos.
Los CSV y PNG de Drive se pueden consultar sin encender el visor.

Archivos útiles al terminar:

- `grid_results.csv` y `control_anchors.json`: búsqueda y controles congelados.
- `comparison_results.csv`: las métricas de los 18 resultados comparables.
- `condition_summary.csv` y `paired_condition_comparison.csv`: medias, dispersión
  y diferencias por semilla frente al control.
- `per_class_comparison.csv`: precisión, recall y F1 de cada clase y condición.
- `token_budget_audit.csv` y `class_weights.{csv,json}`: texto conservado y pesos.
- `trials/<ensayo>/evaluation/`: predicciones, errores, reportes y matrices.
- `selected_models.json` y los dos ZIP: modelos de las condiciones seleccionadas.
- `validation_review.json`: verificación de hashes, referencias y métricas
  recalculadas desde las predicciones, sin otra inferencia.
- `conclusiones.md`: tres párrafos generados únicamente con las cifras obtenidas.
- `STUDY_COMPLETE.json`: cierre del estudio y huellas de sus reportes.

Cuando termine cada ejecución, se guarda el notebook con sus salidas desde el
editor y se conserva una copia en el histórico junto con los reportes y sus hashes.
Los notebooks actuales y el histórico anterior se mantienen como evidencia de
sus respectivas corridas.
