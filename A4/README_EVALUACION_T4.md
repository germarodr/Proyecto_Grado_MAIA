# Evaluar en T4 los modelos entrenados en A100

La T4 es una GPU CUDA y permite evaluar las exportaciones existentes de SciBERT.
Esta variante usa FP32, atención eager y batch 8. El entrenamiento original de
A100/BF16 conserva sus pesos, manifiestos, checkpoints y reportes históricos.

Notebook autónomo: [A4_SciBERT_G15_Evaluacion_T4.ipynb](A4_SciBERT_G15_Evaluacion_T4.ipynb).
Se genera desde el notebook principal mediante `python A4/crear_notebook_evaluacion_T4.py`.

## Ejecutar en VS Code

1. Abre el notebook T4 o su copia de ejecución en `pruebascolab/`.
2. En **Select Kernel → Colab**, selecciona el servidor T4 disponible.
3. Ejecuta las celdas en orden. La primera comprueba Colab y GPU antes de instalar
   las versiones de las dependencias. Autoriza el montaje de Drive cuando se solicite.
4. Se requieren ambos modelos terminados bajo
   `MAIA_TESIS/a4/g15_a4_v0_seed42_mlflow_01/{base,fragmentos}/model/`, junto con
   sus marcadores `TRAINING_COMPLETE.json` y las métricas de entrenamiento.
5. Se reconstruye la misma partición y se validan los hashes y las decisiones
   científicas contra el manifiesto original. Solo se tokenizan textos de validación.
6. La sección 11 verifica todos los hashes de los modelos. No contiene llamadas
   a `Trainer.train()` ni operaciones de exportación de pesos.
7. La sección 12 compara checkpoint/exportación y vuelve a predecir con Trainer,
   todo en FP32. No reproduce la evaluación BF16 original sobre T4.
8. La última celda publica el respaldo final de MLflow. T_B humano sigue desactivado.

## Procedencia y resultados

Las auditorías de preparación van a un directorio nuevo:

```text
MAIA_TESIS/a4/g15_a4_v0_seed42_mlflow_01/evaluation_preparation/t4_<id>/
```

`evaluation_context.json` conserva por separado el entorno original de entrenamiento
y el entorno y batch de esta evaluación. Los nuevos reportes y la comparación de
base/fragmentos quedan en:

```text
MAIA_TESIS/a4/g15_a4_v0_seed42_mlflow_01/evaluations/v2_fp32_<id>/
```

Las evaluaciones se registran como hijos nuevos de los padres existentes en MLflow.
Los snapshots siguen siendo copias completas del historial acumulado, guardadas
en `MAIA_TESIS/a4/_tracking/snapshots/`.

El cambio de GPU y batch puede producir pequeñas diferencias numéricas. Para
comparar base y fragmentos utiliza los dos resultados de esta misma sesión T4,
manteniendo identificados los resultados anteriores de A100.

Esta variante no sirve para iniciar un entrenamiento nuevo. Para ajustar pesos
en T4 se requiere otra configuración de entrenamiento y un RUN_ID propio.

## Ejecución comprobada desde VS Code

El 4 de noviembre de 2026 Colab terminó asignando **A100-SXM4-40GB** al servidor.
La variante compatible con T4 se ejecutó en esa A100, en FP32 y con batch 8.
Por tanto, esta ejecución no constituye una prueba del pipeline completo en T4.

Ambos modelos pasaron la comparación completa entre checkpoint y exportación.
Trainer FP32 y la exportación FP32 tuvieron cero desacuerdos de etiqueta.

| Validación | Base | Fragmentos |
|---|---:|---:|
| F1 macro | 0,847831 | 0,839801 |
| Accuracy | 0,866088 | 0,858648 |

Las métricas reproducen las de la corrida 2. El test humano no se ejecutó.
Se conservaron los pesos originales; solo se generaron auditorías y evaluaciones.

- Notebook con las salidas: [corrida3_VSCode](pruebascolab/A4_SciBERT_G15_Evaluacion_T4_corrida3_VSCode.ipynb).
- Evaluación en Drive: `evaluations/v2_fp32_aa713456a754/` dentro del RUN_ID original.
- Snapshot final: `20261104T163340437316Z_81168209`.

Referencia: [especificaciones oficiales de NVIDIA T4](https://www.nvidia.com/en-us/data-center/tesla-t4/).
