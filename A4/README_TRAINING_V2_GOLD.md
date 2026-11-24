# A4 · Nueva corrida con los datos v2 y las correcciones humanas

> Esta guía conserva el procedimiento de una iteración con training v2 y etiquetas humanas. Sus conclusiones se limitan a esa validación. La evaluación posterior está en [Evaluación final](Evaluacion_Final/README.md).

Vamos a entrenar de nuevo las dos entradas de SciBERT para ver cómo se comportan
con las reservas recuperadas y las etiquetas revisadas de T_A. Conservamos la
separación V2 y los ajustes anteriores. Esta corrida termina en validación;
el test T_B se medirá después de dejar fijadas las decisiones del experimento.

**Notebook:** [A4_SciBERT_G15_TrainingV2_GoldTA_Colab_A100.ipynb](A4_SciBERT_G15_TrainingV2_GoldTA_Colab_A100.ipynb).
**Copia para ejecutar:** [corrida6_VSCode](pruebascolab/A4_SciBERT_G15_TrainingV2_GoldTA_corrida6_VSCode.ipynb).
**RUN_ID:** `g15_a4_trainv2_isoV2_goldTA_seed42_01`.

## Los datos que vamos a usar

Se comprobaron los cinco archivos de la entrega del 10 de noviembre de 2026,
el cierre A3 del 9 de noviembre y sus hashes. Se copiaron los archivos nuevos a
[MAIA_TESIS/TrainingData_Grupo15_v2](https://drive.google.com/drive/folders/1E4PuTALKzIeNTVI5DCldqID99eIOUnXc)
para leerlos desde Colab; el origen compartido se conserva.

| Paso | Ejemplos |
|---|---:|
| Entrega training v2, antes de aplicar V2 | 32.023 |
| Reservas recuperadas respecto de training v1 | 758 |
| Después de aplicar aislamiento V2 | 16.440 |
| Casos ambiguos de T_A que retiramos | 2 |
| Etiquetas humanas utilizables antes del split | 1.330 |
| Etiquetas humanas que corrigen la preetiqueta | 113 |
| Filas retiradas al separar documentos de validación | 3.169 |
| Entrenamiento final | **11.616** |
| Validación final | **1.653** |

En entrenamiento hay 944 etiquetas humanas y 10.672 automáticas; en validación,
125 humanas y 1.528 automáticas. Improvement/Modification tiene 140 ejemplos
en entrenamiento y 19 en validación. No es un dataset con 2.000 ejemplos por clase:
recuperar reservas y cerrar A3 no resuelve por sí solo ese objetivo de suministro.

T_B conserva 2.968 referencias humanas válidas y dos casos ambiguos fuera del
puntaje. Su clase Improvement/Modification tiene 268 casos, según el cierre acordado;
no se inventan ejemplos ni se obliga al cupo anterior de 300. Los documentos de
todos sus paquetes anotados quedan reservados, incluidos los dos ambiguos.

## Cómo empezar

1. Abrir la copia `corrida6_VSCode.ipynb` en VS Code.
2. Seleccionar **Select Kernel → Colab → New Colab Server → A100**, o conectar una A100 existente.
3. Si el agente supervisa las celdas, no iniciar otro «Run All» en paralelo.
4. Autorizar el montaje de Drive cuando Colab lo solicite. Las rutas son:

   ```text
   MAIA_PROYECTO/a2/batches_norw/       # los textos que ya usamos
   MAIA_PROYECTO/a3/                   # gold final y manifest_metrics.json
   MAIA_TESIS/TrainingData_Grupo15_v2/  # los cinco archivos nuevos
   MAIA_TESIS/TrainingData_Grupo15/     # identificadores originales para trazabilidad
   MAIA_TESIS/a4/g15_a4_v2_seed42_mlflow_01/  # reportes de la corrida anterior
   ```

5. Ejecutar las parejas explicación/código en orden. Antes de entrenar se ven las
   comprobaciones, los tamaños y la gráfica de clases con dos líneas de interpretación.
6. Esperar al entrenamiento de base y Top-3, sus auditorías, la comparación, los ZIP
   y el respaldo final. Guardar el notebook y finalizar el entorno para liberar la GPU.

Si se interrumpe, conservar nombre, datos y ajustes, cambiar `RESUME=True` y ejecutar
en orden. Cada modelo verifica su último checkpoint completo; los ya terminados se
comprueban y omiten. Esto también permite retomar una interrupción del primer modelo.

## Qué quedará guardado y cómo leer la comparación

Cada modelo empieza desde la revisión SciBERT `24f92d32b1bfb0bcaf9ab193ff3ad01e87732fc1`,
con semilla 42, cuatro épocas máximas, LR 2e-5, batch efectivo 32, 512 tokens y la misma
preparación de entradas que antes. Se conservan las dos configuraciones, sin añadir Top-1.

La sección 12 mide la validación completa de esta corrida. La 12.1 la compara con
la corrida anterior de aislamiento V2, usando solo las citas comunes. **Las predicciones
de ambas se miden contra las etiquetas actuales**; se informa cuántas referencias
cambiaron. Así no mezclamos puntajes calculados sobre etiquetas distintas.
La diferencia combina más datos y correcciones humanas; no identifica sus efectos por separado.

Modelos, EDA y reportes irán a `MAIA_TESIS/a4/g15_a4_trainv2_isoV2_goldTA_seed42_01/`.
MLflow conserva la misma historia y crea padres/intentos nuevos, con etiquetas de
versión de datos, aislamiento y procedencia. Los snapshots completos siguen en
`MAIA_TESIS/a4/_tracking/snapshots/`; solo una sesión debe escribirlos a la vez.

`GOLD_FINAL=True` significa que la anotación A3 cerró. **`RUN_TEST=False`** mantiene
la evaluación T_B desactivada en este notebook. El próximo paso será preparar la
evaluación final con modelos y decisiones congelados; no usar sus resultados para reajustar.

Comprobaciones locales: `python A4/verificar_training_v2_gold.py`. Incluyen los
datos reales, la separación de documentos, el rechazo de etiquetas T_B en entrenamiento
y una comparación que detecta etiquetas actuales inconsistentes entre las dos entradas.

## Qué ocurrió en la corrida 6

Completada el **10 de noviembre de 2026, hora de Bogotá**, en A100 de 40 GB.
Las 17 celdas de código terminaron y conservaron sus salidas, sin errores finales.
Al comenzar se cerró la conexión del kernel; se reinició antes de preparar datos.
VS Code dejó sin contador persistido la primera celda, aunque el puente registra
su ejecución 1 y su salida confirma GPU e instalación. Las otras 16 sí conservan contador.

En la validación completa de **1.653 citas**, medida en FP32:

| Entrada | F1 macro | Accuracy | F1 Evidence | F1 Improvement/Modification |
|---|---:|---:|---:|---:|
| Base: título y resumen | **0,824022** | 0,846340 | 0,782609 | 0,687500 |
| Top-3: fragmentos y secciones | 0,822273 | 0,844525 | 0,757576 | 0,687500 |

El base queda 0,175 puntos porcentuales por encima de Top-3. La diferencia es
pequeña y corresponde a una sola semilla. Improvement/Modification tiene solo
19 referencias en validación: ambos modelos aciertan 11, por lo que su resultado
por clase sigue siendo sensible a pocos casos.

Para comparar con la corrida anterior, usamos **las mismas 1.539 citas y las
etiquetas actuales**. Nueve etiquetas cambiaron respecto de la referencia anterior:

| Entrada | Datos v1, predicciones anteriores reevaluadas | Datos v2 + revisión T_A | Cambio aproximado |
|---|---:|---:|---:|
| Base | 0,811893 | 0,812653 | +0,08 puntos porcentuales |
| Top-3 | 0,805780 | 0,810712 | +0,49 puntos porcentuales |

Los avances son pequeños. No podemos concluir que las correcciones humanas por sí
solas los causaron: también cambió el suministro de entrenamiento. Tampoco debemos
comparar directamente 0,824022 con el 0,804197 original de la corrida anterior:
esos dos valores usan validaciones y referencias distintas.

Los dos modelos eligieron la época 4 (`checkpoint-1452`). Entrenar tomó 414,75
segundos para base y 411,53 para Top-3; la memoria GPU asignada alcanzó unos 9,27 GiB.
Ambas exportaciones pasaron la comprobación contra su checkpoint en toda la validación.
BF16 y FP32 cambian tres etiquetas para base y cinco para Top-3; las tablas usan FP32.

Los archivos finales están en:

```text
MAIA_TESIS/a4/g15_a4_trainv2_isoV2_goldTA_seed42_01/
  base/model/
  fragmentos/model/
  scibert_g15_base.zip
  scibert_g15_fragmentos.zip
  evaluations/v2_fp32_95f588d9dfd0/
    validation_comparison.csv
    release_common_validation.csv
    release_common_per_class.csv
    release_common_f1.png
```

El respaldo completo del historial es
`MAIA_TESIS/a4/_tracking/snapshots/20261111T023059913141Z_d0d1801a/`.
Se puede restaurar en EC2 sin copiar los respaldos intermedios.

**T_B no se evaluó.** El siguiente paso de A4 es dejar fijadas las decisiones y
preparar la evaluación final con sus 2.968 referencias humanas, manteniendo el
cupo real de 268 para Improvement/Modification. No se reajusta después de ver ese test.
