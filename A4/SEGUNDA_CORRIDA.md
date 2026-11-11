# Continuar A4: comparar base y fragmentos

La primera corrida de `base` terminó en A100: cuatro épocas, F1 macro de Trainer
0,846065 y F1 macro del modelo recargado 0,847831. Estas métricas provienen de
validación con preetiquetas, no del test humano T_B.
El notebook descargado se conserva en `pruebascolab/` como evidencia.
Archivo: [A4_SciBERT_G15_Colab_A100_corrida1.ipynb](pruebascolab/A4_SciBERT_G15_Colab_A100_corrida1.ipynb).

Esta versión mantiene el entrenamiento y añade evaluación FP32 con atención
`eager`, comprobación de toda la validación y evaluaciones separadas en MLflow.
Los reportes de la primera corrida no se sobrescriben.

## 1. Abrir la versión nueva

1. En Colab selecciona **Archivo → Subir notebook** y abre el archivo actualizado
   `A4_SciBERT_G15_Colab_A100.ipynb` de la carpeta `A4/` del repositorio.
2. Guarda una copia nueva en Drive, por ejemplo `A4_G15_comparacion_fragmentos.ipynb`.
   Conserva la copia anterior con sus salidas.
3. Selecciona una **A100** y usa una sola sesión escritora de este historial.
4. Ejecuta la instalación inicial; si Colab pide reiniciar, hazlo antes de continuar.

## 2. Configurar la continuación

En la celda de la sección 1 cambia estos valores antes de ejecutarla:

```python
RUN_ID = "g15_a4_v0_seed42_mlflow_01"   # el mismo de base
CONFIGS = ["base", "fragmentos"]
RESUME = True
RUN_TEST = False
GOLD_FINAL = False
```

Conserva V0, semilla 42, LR 2e-5, batch 16 con acumulación 2, cuatro épocas y las
rutas de Drive. No cambies pesos por clase ni otros hiperparámetros en esta comparación.
Se necesita la carpeta del RUN_ID en Drive, no solo el notebook descargado o su ZIP:

```text
MAIA_TESIS/a4/g15_a4_v0_seed42_mlflow_01/
  request_manifest.json
  run_manifest.json
  base/TRAINING_COMPLETE.json
  base/validation_metrics.json
  base/model/
  base/checkpoints/                 # para comprobar checkpoint contra exportación
```

El notebook comprueba que exista `base/TRAINING_COMPLETE.json` antes de continuar.
Si faltan archivos o hay diferencias de manifiesto, detente y revisa el mensaje;
no borres los controles ni crees otro RUN_ID para eludirlos.

## 3. Preparar los datos y entrenar

1. Ejecuta las secciones **1 a 10.1** en orden y autoriza Drive. Se conserva la
   revisión exacta de SciBERT de la primera corrida.
2. Comprueba 28.039 filas de entrenamiento y 3.226 de validación. En la sección 9
   ahora verás la auditoría de tokens para `base` y para `fragmentos`.
3. En 10.1 deben aparecer el historial restaurado, un respaldo nuevo y `MLflow listo`.
4. Ejecuta **11**. Para base debe indicar **«ya entrenado y verificado; se omite entrenamiento»**.
   Si intenta entrenar base o hay un error de hashes, detente y revisa la configuración.
5. Después comienza el entrenamiento de `fragmentos`, desde SciBERT preentrenado,
   con la misma partición de datos. Sus pesos no proceden del modelo base ajustado.

No se presupone que fragmentos tarde los mismos 14 minutos: sus entradas suelen
tener más tokens. Los respaldos y checkpoints siguen activos. AWS puede estar apagado.

## 4. Evaluar y cerrar

1. Ejecuta **12**. Para cada configuración:
   - Recalcula las predicciones del modelo exportado en FP32 y atención eager.
   - Las compara con el checkpoint seleccionado sobre toda la validación.
   - Repite la predicción con Trainer en BF16 y registra qué etiquetas cambian.
   - Muestra métricas por clase y guarda las claves de los errores, sin textos.
2. Si aparece `passed_full_validation`, el checkpoint y la exportación coinciden
   dentro de las tolerancias y asignan las mismas etiquetas. Si falta el checkpoint,
   queda `pending_checkpoint_missing`: puedes consultar las métricas, pero no se
   considera completada esa comprobación. Si hay discrepancias, se detiene la celda.
3. Compara los dos modelos con el F1 macro **FP32** de la tabla final. El delta
   `fragmentos - base` se muestra debajo. Es una comparación de validación; la
   conclusión final del proyecto sigue dependiendo del gold humano de T_B.
4. Ejecuta **13**: el test se omite con la configuración actual.
5. Ejecuta **14** para empaquetar fragmentos y publicar el respaldo final. El ZIP
   existente de base se conserva. Guarda el notebook con sus salidas.

## 5. Archivos y MLflow

Cada ejecución de la sección 12 crea una carpeta nueva:

```text
MAIA_TESIS/a4/g15_a4_v0_seed42_mlflow_01/evaluations/v2_fp32_<id>/
  base/
    export_precision_audit.json
    validation_scores.json
    validation_classification_report.json
    validation_per_class.csv
    validation_predictions.csv
    validation_errors.csv
    validation_confusion.csv
    validation_confusion.png
  fragmentos/
    ...los mismos reportes...
  validation_comparison.csv
```

Los hijos `attempt_*` conservan el entrenamiento. Los hijos `evaluation_v2_fp32_*`
contienen la auditoría y los reportes nuevos. Las métricas finales se llaman
`validation_fp32_f1_macro`, `validation_fp32_accuracy`, etc. El padre señala la
última evaluación; los hijos anteriores se mantienen disponibles.

Para consultar en AWS, descarga los tres archivos del último snapshot completo y
sigue la [sección 7.1 de la instalación](README_INSTALACION.md#71-actualizar-el-panel-con-un-snapshot-nuevo).
Abre `G15_A4_SciBERT` y expande los padres de ambas configuraciones. El visor sigue
siendo una copia del snapshot, sin actualización en vivo desde Colab.

Si solo quieres auditar el modelo base antes de entrenar fragmentos, usa
`CONFIGS = ["base"]` y `RESUME = True`, ejecutando igualmente hasta 14. No reentrena base.

## Validación de esta actualización

Pasaron 14 pruebas locales: seis del notebook, cuatro de MLflow y cuatro de
evaluación. Incluyen interrupción/reanudación en CPU, preservación de resultados,
auditoría sobre todo un conjunto pequeño y rechazo de una exportación alterada.
Se verificó que los argumentos de entrenamiento y la preparación de datos no
cambiaron respecto del commit de la primera corrida. La evaluación nueva en A100
y el entrenamiento de fragmentos se ejecutarán en Colab.

Referencias: [Trainer 4.57.1](https://huggingface.co/docs/transformers/v4.57.1/en/main_classes/trainer)
y [precisión mixta de PyTorch 2.11](https://docs.pytorch.org/docs/2.11/amp.html).
