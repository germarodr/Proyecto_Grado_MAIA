# A4 independiente · Grupo 15

> Esta guía documenta la variante independiente y las decisiones de aislamiento utilizadas en esa iteración. La selección posterior y el test humano están en [Métricas de A4](Final/M%C3%A9tricas.md).

**Alcance de nuestros datos.** Trabajamos con la entrega preparada para el Grupo 15,
con las exclusiones acordadas en A1–A3. Aprendemos y validamos con las etiquetas
automáticas de A2. Nuestro conjunto humano T_B contiene 2.968 citas válidas para
la prueba final. En el resto de la guía hablaremos de entrenamiento, validación
interna y prueba final.

**Notebook:** [A4_SciBERT_G15_Independiente_Colab_A100.ipynb](A4_SciBERT_G15_Independiente_Colab_A100.ipynb).
**Copia de ejecución:** [corrida7_VSCode](pruebascolab/A4_SciBERT_G15_Independiente_corrida7_VSCode.ipynb).
**RUN_ID:** `g15_a4_trainv2_prelabels_sinTA_seed42_01`.
**Experimento MLflow:** `G15_A4_SciBERT_Independiente`.
**Estado:** corrida 7 completada el 10 de noviembre de 2026, hora de Colombia.

## Qué contiene el notebook

La portada deja un recuadro para el logo de la universidad, el título «Proyecto de
grado», el nombre completo de la propuesta y los integrantes del Grupo 15. Se puede
reemplazar el recuadro por una imagen al preparar la entrega. Siguen una introducción
breve y 16 secciones consecutivas, cada una con explicación y código.

El notebook cuenta cómo llegamos de los archivos de A1/A2/A3 a los datos utilizados,
muestra un EDA, comprueba la separación, entrena base y Top-3, audita las exportaciones
y conserva reportes/modelos. Esta corrida completa entrenamiento y validación
interna; la prueba final es el siguiente paso de A4.

## Separación aplicada

Aplicamos las listas de exclusión de la entrega a los dos artículos de cada cita,
el que cita y el citado. Después separamos entrenamiento y validación por documento
y retiramos los cruces. Las cantidades definitivas de esta corrida son:

| Etapa | Ejemplos |
|---|---:|
| Entrega training v2 de G15 | 32.023 |
| Después de V2 propio | 16.440 |
| Retirados por las exclusiones complementarias de la entrega | 5.902 |
| Disponibles antes de separar train/val | 10.538 |
| Retirados para separar documentos de validación | 1.285 |
| Entrenamiento | **8.170** |
| Validación interna | **1.083** |
| Prueba final humana | **2.968 válidos** |

No hay documentos compartidos entre entrenamiento, validación y prueba final.
Las nueve clases permanecen presentes. Improvement/Modification tiene
**46 ejemplos en train y 3 en val**: un solo acierto cambia su recall de validación
en 33,3 puntos porcentuales. Las pequeñas diferencias de F1 deben interpretarse
con esa limitación. El test humano conserva 268 casos de esa categoría.

Las reservas propias nunca anotadas pueden permanecer si la entrega v2 las liberó
y pasan las exclusiones. No se usan como etiquetas humanas ni forman parte del test final.

## Dónde están los archivos y cómo correr

Las rutas de Colab están preparadas:

```text
MAIA_PROYECTO/a2/batches_norw/          # textos y Top-3
MAIA_PROYECTO/a3/                      # cierre de nuestra revisión humana
MAIA_TESIS/TrainingData_Grupo15_v2/     # entrega nueva de G15
MAIA_TESIS/TrainingData_Grupo15/        # identificadores originales propios
MAIA_TESIS/a4_inputs/g15_independent_v1/ # exclusiones complementarias
```

La [lista de exclusión preparada](https://drive.google.com/file/d/17WhgSynIzjIPQaiMPtLUKcXUvv3CiCPN/view)
contiene documentos y procedencia, sin etiquetas. Se puede reconstruir con
`python A4/preparar_exclusiones_independiente.py` a partir de los identificadores
originales. Su SHA256 es `fd02b54442f8cf96381abed8e8ecbf6fa9830f4e34a05e85a75bbb861c4def9b`.

1. Abrir la copia `corrida7_VSCode.ipynb`.
2. Seleccionar **Select Kernel → Colab** y la A100 disponible. Si el agente ejecuta
   las celdas, no iniciar otro «Run All» en paralelo.
3. Autorizar Drive si se solicita y ejecutar las secciones en orden.
4. Comprobar en el EDA 8.170 train / 1.083 val, etiquetas `pre_label` exclusivamente
   y cero cruces de documentos antes de entrenar.
5. Esperar a ambos modelos, auditorías, ZIP y snapshot final; guardar el notebook
   y finalizar el entorno cuando ya no se necesite la GPU.

Para retomar una interrupción, conservar el RUN_ID y los datos y usar `RESUME=True`.
Se verifican los archivos guardados antes de continuar. Cada entrada empieza desde
SciBERT preentrenado, semilla 42, hasta cuatro épocas y los mismos ajustes ya probados.
Las etiquetas humanas y el test no intervienen en elegir el checkpoint.

Los resultados irán a `MAIA_TESIS/a4/g15_a4_trainv2_prelabels_sinTA_seed42_01/`.
El historial anterior se conserva, pero esta corrida aparece en el experimento
independiente indicado arriba. El último snapshot completo permite restaurar todos
los experimentos en EC2. Solo una sesión escribe ese historial a la vez.

Comprobaciones locales: `python A4/verificar_independiente.py`. Verifican los datos
reales, los documentos reservados en ambos roles, el rechazo de etiquetas humanas
y que ambas entradas mantengan los mismos argumentos de entrenamiento.
Las tres comprobaciones pasaron; también se reconstruyeron los 9.253 ejemplos
de train/val con sus textos y tres fragmentos completos, a partir de los ocho lotes
reales de A2. En Colab terminaron las 16 celdas de código, con salidas guardadas y
sin errores pendientes. Las dos exportaciones reprodujeron sus checkpoints en
toda la validación.

## Qué nos dejó la primera corrida independiente

Las dos entradas aprendieron desde SciBERT preentrenado con los mismos datos y
ajustes. Estas son las métricas definitivas en FP32 sobre las 1.083 preetiquetas
de validación; todavía no son resultados del test humano.

| Entrada | Época seleccionada | F1 macro | Accuracy |
|---|---:|---:|---:|
| Contexto + título y resumen (base) | 3 | **0,740253** | **0,848569** |
| Contexto + tres fragmentos (Top-3) | 4 | 0,729754 | 0,835642 |

Base quedó 1,05 puntos porcentuales por encima en F1 macro en esta partición y
semilla. Improvement/Modification tuvo F1 y recall cero en ambas entradas, con
solo tres referencias en validación. Esto pide cautela al interpretar esa clase;
su resultado final se conocerá cuando ejecutemos la prueba humana con los modelos ya fijados.
Evidence alcanzó F1 0,715789 en base y 0,708738 en Top-3. La referencia de predecir
siempre Background obtuvo F1 macro 0,071145.

Top-3 recortó los fragmentos en el 90,77% de los ejemplos de validación para caber
en el límite de 512 tokens (base recortó título/resumen en el 8,13%). Es una
limitación de la entrada que queda registrada, sin cambiar ajustes durante esta
corrida. Estos resultados no se comparan directamente con los números históricos:
ahora usamos otros ejemplos y un aislamiento más estricto.

Los entrenamientos tardaron aproximadamente 312 y 318 segundos, con unos 9,27 GiB
de memoria GPU máxima. El paso de BF16 a FP32 cambió una predicción de base y
ninguna de Top-3; los reportes finales usan FP32 en los dos casos.

**Evaluación:** `evaluations/v2_fp32_f6f948cf3ff2/`, dentro de la carpeta del RUN_ID.
**Snapshot final completo:** `20261111T035414850950Z_292df6df` en
`MAIA_TESIS/a4/_tracking/snapshots/`. Conserva también los experimentos anteriores.
Para actualizar el visor de EC2 se restaura ese snapshot completo.

Los paquetes `scibert_g15_base.zip` y `scibert_g15_fragmentos.zip` quedaron en la
carpeta del RUN_ID, junto a manifiestos, particiones y reportes. El notebook de
ejecución conserva la gráfica de clases y las dos matrices de confusión.

El siguiente paso de A4 es evaluar ambos modelos ya fijados una vez sobre las
2.968 citas revisadas por humanos, sin reajustarlos con sus etiquetas. La validación
interna que ya completamos sirvió para seleccionar los modelos; la prueba final
permitirá medirlos frente a la referencia humana. Después se entregan al resto
del equipo los modelos, la preparación de entradas y las métricas. Los artefactos
ya están guardados y se puede finalizar el servidor A100 desde Colab.
