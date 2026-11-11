# A4 · Prueba exploratoria V2

**RUN_ID:** `g15_a4_v2_seed42_mlflow_01`.
**Notebook:** [A4_SciBERT_G15_V2_Colab_A100.ipynb](A4_SciBERT_G15_V2_Colab_A100.ipynb).
**Copia para ejecutar:** [corrida5_VSCode](pruebascolab/A4_SciBERT_G15_V2_corrida5_VSCode.ipynb).

Se usa la entrega actual `training_v1_G15.jsonl`, con **aislamiento V2**, no una
nueva entrega ni gold humano. Se entrenan `base` y `fragmentos` (Top-3) desde la
misma revisión preentrenada de SciBERT de V0. T_B sigue cerrado.

## Qué conserva y qué cambia

- Mismos datos de origen, semilla 42, revisión de SciBERT, tokenización, CE sin pesos,
  LR 2e-5, batch 16 con acumulación 2, cuatro épocas máximas y selección por F1 macro.
- Nuevo directorio de modelos y nuevos padres/intentos en el mismo historial MLflow.
- V2 excluye documentos del test incluso con roles inversos; también separa los
  documentos de train/val. Tamaños comprobados: **11.015 train / 1.539 val**.
- Se exige igualdad con el manifiesto V0 salvo aislamiento, partición y entorno.
  Si cambian archivos o etiquetas, se detiene: esa nueva entrega será otra prueba.
- El EDA muestra distribución de clases V2 y conteos frente a V0, con dos líneas
  de interpretación. PNG/CSV quedan en Drive y en los reportes de MLflow.

## Cómo correr

1. Abrir la copia `corrida5_VSCode.ipynb` en VS Code.
2. Seleccionar **Select Kernel → Colab** y conectar una **A100**. También se puede
   subir el notebook a Colab web y elegir GPU A100.
3. Ejecutar las parejas explicación/código en orden. Si el agente supervisa las
   celdas, no iniciar simultáneamente otro «Run All».
4. Autorizar el montaje de Drive cuando Colab lo solicite. Deben existir:

   ```text
   Mi unidad/MAIA_PROYECTO/a2/batches_norw/
   Mi unidad/MAIA_TESIS/TrainingData_Grupo15/
   Mi unidad/MAIA_TESIS/a4/g15_a4_v0_seed42_mlflow_01/
     run_manifest.json
     split_class_counts.csv
     evaluations/v2_fp32_37dc6f909cde/
   ```

5. Antes del entrenamiento, comprobar V2, `base` + `fragmentos`, tamaños 11.015/1.539,
   EDA y restauración del historial. `GOLD_FILES=[]`, `RUN_TEST=False`, `GOLD_FINAL=False`.
6. Esperar al entrenamiento de ambos modelos, auditorías, comparación, ZIP y snapshot
   final. Guardar el notebook ejecutado. Después finalizar el entorno Colab para
   liberar la GPU.

Si se interrumpe, conservar RUN_ID y decisiones, usar `RESUME=True` y ejecutar en orden:
los modelos completos se verifican y omiten; se retoma el último checkpoint completo.
No cambiar datos, hiperparámetros ni versiones de bibliotecas durante esa recuperación.

## Cómo comparar

La sección 12.1 exporta:

- `isolation_own_validation.csv`: resultados en cada validación completa; sus tamaños
  son distintos y la comparación es descriptiva.
- `isolation_common_validation.csv`: V0 y V2 sobre **las mismas citas** de validación.
  Se alinea por `inst_key`, se comprueban etiquetas y se recalculan las métricas FP32.
- `isolation_common_per_class.csv`, claves comunes y `isolation_common_f1.png`.

El efecto combina aislamiento y menor tamaño de train; una semilla con preetiquetas
no demuestra una mejora estable ni equivale a evaluación humana. No se usa el test
para elegir configuración. La etiqueta `v2_fp32` de las carpetas de evaluación es
la versión del procedimiento de evaluación, independiente del aislamiento V0/V2.

Los resultados irán a `MAIA_TESIS/a4/g15_a4_v2_seed42_mlflow_01/`. Los snapshots
completos y acumulados siguen en `MAIA_TESIS/a4/_tracking/snapshots/`; basta restaurar
el último completo para consultar V0 y V2 en EC2. Solo una sesión escribe ese historial.

Verificación local, sin GPU: `python A4/verificar_v2.py`.

## Resultado de la corrida del 7 de noviembre de 2026

Ejecución completada en A100 de 40 GB: **17 celdas de código, sin errores**.
Se verificaron hashes de origen, revisión de SciBERT, hiperparámetros y aislamiento
de documentos. MLflow restauró el historial anterior, que incluye V0 y Top-1.

Comparación FP32 sobre **las mismas 1.539 citas de validación**:

| Aislamiento | Train | Base: F1 macro | Top-3: F1 macro |
|---|---:|---:|---:|
| V0 | 28.039 | 0,836247 | 0,820989 |
| V2 | 11.015 | 0,804197 | 0,799938 |
| Diferencia V2 − V0 | | −3,2051 puntos porcentuales | −2,1051 puntos porcentuales |

Los F1 V0 sobre su validación completa de 3.226 filas son 0,847831 y 0,839801;
se conservan en el CSV de validaciones propias, pero **no son la referencia de la
tabla anterior**, que utiliza las mismas filas para las cuatro evaluaciones.

Dentro de V2, Top-3 queda **0,4259 puntos porcentuales por debajo del base**.
En Evidence obtiene F1 0,759076 frente a 0,739274 del base (152 casos).
Ambos obtienen F1 0,533333 y recall 0,421053 en Improvement/Modification:
ocho aciertos de 19 casos de referencia. Esa clase tiene solo 129 ejemplos en train;
su resultado de validación debe interpretarse con cautela.

El resultado muestra una caída con esta combinación de aislamiento estricto y
reducción del suministro, no un efecto causal aislado de V2. No demuestra que
compartir documentos sea preferible para la evaluación definitiva. Sigue siendo
una prueba de una sola semilla contra preetiquetas A2, con T_B humano cerrado.

Ambos modelos seleccionaron la época 4 (`checkpoint-1380`). El entrenamiento
registró 386,75 segundos para base y 387,60 para Top-3, con pico de memoria GPU
asignada de aproximadamente 9,26 GiB. Las auditorías `passed_full_validation`
verificaron las exportaciones contra sus checkpoints en las 1.539 filas; BF16 y
FP32 difieren en tres etiquetas para base y cuatro para Top-3. La comparación usa FP32.

Rutas en Drive, relativas a `MAIA_TESIS/a4/`:

```text
g15_a4_v2_seed42_mlflow_01/
  eda_class_distribution.png
  eda_class_distribution.csv
  base/model/
  fragmentos/model/
  scibert_g15_base.zip
  scibert_g15_fragmentos.zip
  evaluations/v2_fp32_0e59a5e7aba8/
    isolation_own_validation.csv
    isolation_common_validation.csv
    isolation_common_per_class.csv
    isolation_common_keys.csv
    isolation_common_f1.png
    isolation_comparison_notes.json
_tracking/snapshots/20261107T170547963517Z_550771da/
```

Ese último snapshot completo contiene el historial acumulado para restaurar el
visor EC2. El siguiente paso de A4 es repetir el diseño con la nueva entrega
ampliada y su procedencia documentada, usando otro RUN_ID y manteniendo el test
fuera de las decisiones de desarrollo. No iniciar otra corrida con este RUN_ID
al incorporar archivos o etiquetas nuevos.
