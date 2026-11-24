# Evaluación final de SciBERT

El [notebook](SciBERT_Evaluacion_Final.ipynb) evalúa **base y Top-3** sobre las
**2.968 citas evaluables del test humano de G15**. No entrena, selecciona otros
parámetros ni recupera nuevos fragmentos. Los dos casos `unclear` siguen reservados
y quedan fuera de las métricas.

## Qué se congeló antes de evaluar

| Aspecto | Valor |
|---|---|
| Estudio de origen | `g15_scibert_reparto_v2_01` |
| Modelos principales | Semilla 42, LR 3e-5, regularización 0,1, sin pesos por clase |
| Base | `grid_base_contexto_192_lr3em05_wd0p1_s42`, mejor época 5 |
| Top-3 | `grid_fragmentos_contexto_192_lr3em05_wd0p1_s42`, mejor época 7 |
| Entrada | Máximo 512 tokens; contexto hasta 192; el mismo codificador de la exportación |
| Evaluación | A100, FP32, atención eager, TF32 desactivado, lote 32 |
| Referencias | Gold A3, conjunto B, `in_eval=true`; orden por `inst_key` |
| Comparación pareada | 2.000 remuestreos por artículo citante, semilla 20261113, IC percentil 95 % |

Los pesos y los archivos de cada exportación están identificados por SHA-256 en
[seleccion_congelada.json](seleccion_congelada.json), también incrustado en el
notebook. Los dos modelos seleccionados coinciden con los elegidos en el estudio
de pesos por clase. No se utiliza Top-1.

## Cómo ejecutarlo

1. Abre `SciBERT_Evaluacion_Final.ipynb` en VS Code y conecta la A100 disponible
   desde **Select Kernel → Colab**. Usa una sola sesión para esta evaluación final.
2. El notebook es autónomo: basta subir el `.ipynb` si se utiliza desde otra
   interfaz. El código funcional de esta carpeta se conserva como referencia
   metodológica; los generadores y verificadores auxiliares se excluyen de Git.
3. Ejecuta las celdas en orden y autoriza Google Drive. La primera celda comprueba
   la GPU y PyTorch 2.11.0, y prepara las versiones de las otras bibliotecas. Si
   solicita reiniciar por una biblioteca ya cargada, reinicia solo ese intérprete
   y vuelve a comenzar desde la primera celda.
4. Revisa la distribución del test y los dos ejemplos reales de la sección 2.
   Las etiquetas esperadas se muestran aparte y nunca forman parte del payload.
5. Las secciones 5 y 6 ejecutan la inferencia de un modelo a la vez. Las siguientes
   calculan las métricas, gráficas, comparación pareada, errores y conclusiones.
6. El cierre correcto muestra **«Evaluación final cerrada y respaldada»** y crea
   `FINAL_COMPLETE.json`. Guarda el notebook con sus salidas y conserva una copia
   histórica junto al manifiesto de resultados. Esa copia del editor se guarda
   después de terminar; el kernel remoto no puede guardar por sí solo el archivo
   abierto en el equipo local.

Mantén una sola ejecución activa para este estudio y evita iniciar la misma
secuencia de celdas en paralelo.
La GPU local no se utiliza en esta evaluación: se mantiene el entorno acordado.

## Entradas que ya están en Drive

```text
MAIA_PROYECTO/
  a3/{test_set_gold.jsonl,manifest_metrics.json}
  a2/batches_norw/<lotes originales>.jsonl
MAIA_TESIS/
  TrainingData_Grupo15/test_set_ids_G15.jsonl
  a4/g15_scibert_reparto_v2_01/
    STUDY_COMPLETE.json
    selected_models.json
    split_train_ids.jsonl
    split_validation_ids.jsonl
    trials/<ensayo>/model/<exportación completa>
    trials/<ensayo>/evaluation/<reportes previos>
```

No hace falta volver a descargar los modelos al equipo local. El notebook verifica
las exportaciones en Drive y las copia a una caché temporal del servidor para
cargarlas. Los datos fuente y las carpetas de entrenamiento no se modifican.

La auditoría compara documentos citantes y citados entre entrenamiento, validación
y las 2.970 citas reservadas, incluidas las dos excluidas de las métricas. Las
fuentes, localizadores, particiones y lotes de texto se comprueban contra hashes
del estudio anterior. Una discrepancia detiene la ejecución.

## Resultados y recuperación

```text
MAIA_TESIS/a4/g15_scibert_test_B_final_01/
  evaluation_protocol.json
  data_audit.json
  class_distribution.{csv,png}
  two_real_examples.json
  base/
    parts/<lote>.{csv,complete.json}
    test_predictions.csv
    PREDICTIONS_COMPLETE.json
    test_classification_report.json
    test_confusion.{csv,png}
    test_cited_seen_unseen.json
    test_errors.csv
  fragmentos/<mismos archivos>
  test_comparison.csv
  test_per_class.csv
  latency_summary.csv
  validation_vs_test.{csv,png}
  test_confusion_comparison.png
  test_metrics_comparison.png
  paired_test_comparison.{json,png}
  bootstrap_deltas.csv
  error_examples.{json,csv}
  conclusiones.md
  FINAL_COMPLETE.json
  _tracking/snapshots/<id>/{snapshot.zip,snapshot.sha256,COMPLETE.json}
```

El estudio de MLflow es **`G15_SciBERT_Test_Final`**. Su base local usa
`/opt/maia/a4_tracking_final_test/mlflow.db`, con snapshots completos propios en
la carpeta del test. El bloqueo local impide dos escritores de este estudio en
el mismo servidor. No se mezclan bases activas ni snapshots de entrenamiento.

Si se interrumpe el servidor, conecta uno nuevo y ejecuta desde el principio con
las mismas rutas, versiones y `RUN_ID`. Los CSV de lotes con recibo y hash válidos
se reutilizan; un lote sin cierre se recalcula. Los identificadores de artículos
se leen como texto para conservar ceros y decimales. Si ya están todas las
predicciones, se reconstruyen reportes sin ejecutar de nuevo el modelo. El
protocolo detecta cambios y evita mezclar resultados incompatibles.

## Cómo interpretar la comparación

- La comparación principal es **base contra Top-3 sobre las mismas citas humanas**.
  El bootstrap conserva juntas las citas de cada artículo citante y mantiene las
  nueve clases en el cálculo del F1 macro.
- El «antes» utiliza la validación de los **modelos de semilla 42 seleccionados**,
  no las medias entre semillas. Esa validación tiene 125 etiquetas humanas y 1.528
  automáticas; la diferencia con test no mide por sí sola una mejora del modelo.
- La latencia incluye tokenización, transferencias y forward, después de un
  calentamiento sintético. Se registra como promedio del lote por ejemplo,
  excluyendo carga del modelo y E/S. Los percentiles describen esos promedios,
  no peticiones individuales cronometradas. Las reanudaciones conservan el ID
  de sesión de cada medición.
- Las causas de los errores se examinan mediante lectura de los casos. Las
  conclusiones distinguen los resultados medidos de sus posibles explicaciones.
- El test no se utiliza para escoger parámetros. La escasez de varias clases
  respecto al requisito de 2.000 ejemplos se declara aparte; evaluar no resuelve
  esa limitación ni acredita automáticamente el cumplimiento del requisito.

## Evaluación ejecutada · 13 de noviembre de 2026

Las nueve celdas terminaron sin errores. Los dos modelos congelados evaluaron
las mismas **2.968 citas humanas** en FP32. No se entrenó ni se ajustaron
parámetros usando el test.

| Entrada | F1 macro | F1 micro |
|---|---:|---:|
| Contexto + título y abstract | 0,796728 | 0,792116 |
| Contexto + Top-3 y secciones | 0,799951 | 0,794811 |

La diferencia Top-3 menos base fue **+0,32 puntos porcentuales**, con intervalo
del 95 % **[−0,75; +1,39]** por bootstrap pareado por artículo citante. El
intervalo incluye cero: no se establece una ventaja clara entre las entradas.

Las [conclusiones](conclusiones.md) y la [verificación de ejecución](Verificacion_Ejecucion.json)
recogen el cierre. La [copia ejecutada del histórico](Historico/Evaluacion_2026-11-13_01/SciBERT_Evaluacion_Final.ipynb)
conserva las salidas; esa carpeta incluye las cinco figuras y un manifiesto de
huellas. Los resultados completos están en
`MAIA_TESIS/a4/g15_scibert_test_B_final_01/`.
El snapshot final de MLflow es `20261113T211318096884Z_0ff99e6a`.

## Comprobaciones locales de preparación

Las comprobaciones locales verificaron el notebook, la reconstrucción de las
2.968 entradas reales, el aislamiento, el bootstrap y la inferencia/reanudación
con un BERT diminuto aleatorio en CPU. Esas pruebas no evalúan los modelos
finales. El registro queda en [Verificacion_Preparacion.json](Verificacion_Preparacion.json).

Las herramientas auxiliares de creación y prueba se mantienen localmente y se
excluyen de Git. Para ejecutar la evaluación basta el notebook autónomo. La
ejecución real y sus métricas se acreditan con
[Verificacion_Ejecucion.json](Verificacion_Ejecucion.json) y el notebook del histórico.
