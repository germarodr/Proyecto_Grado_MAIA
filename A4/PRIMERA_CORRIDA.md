# Primera corrida de SciBERT con MLflow

La primera corrida de base ya está completada y su notebook se conserva en
`pruebascolab/`. Para continuar con la comparación y la evaluación versionada,
usa [SEGUNDA_CORRIDA.md](SEGUNDA_CORRIDA.md).

El notebook entrena en Colab A100 y registra en SQLite local. Publica snapshots
en `MAIA_TESIS/a4/_tracking/snapshots/`. AWS sirve una copia de ese historial:
no necesita estar encendido para entrenar. La UI no se actualiza en vivo desde Colab.

## 1. Subir el notebook

1. Descarga del repositorio `A4_SciBERT_G15_Colab_A100.ipynb` actualizado.
2. En Colab selecciona **Archivo → Subir notebook** y abre ese archivo.
   También puedes guardarlo en `MAIA_TESIS/notebooks/` y abrirlo con Colab.
3. Guarda tu copia en Drive con un nombre reconocible, por ejemplo
   `A4_SciBERT_G15_primera_corrida.ipynb`.
4. Selecciona **Entorno de ejecución → Cambiar tipo de entorno → A100**.
5. Cierra el notebook de instalación si aún está registrando datos. Solo una
   sesión Colab debe escribir este historial. No abras dos entrenamientos a la vez.

El notebook es autónomo: no debes subir `crear_notebook.py` ni `tracking_runtime.py`.
No debes configurar una IP de AWS, un token MLflow ni un bucket S3.

## 2. Configurar y revisar antes de entrenar

Ejecuta la celda inicial de instalación en una sesión limpia. Si Colab solicita
reiniciar por bibliotecas ya importadas, reinicia y ejecuta desde el principio.

En la sección **1**, deja las rutas de Drive existentes y configura:

```python
RUN_ID = "g15_a4_v0_seed42_mlflow_01"
CONFIGS = ["base"]
VARIANT = "V0"
RESUME = False
RUN_TEST = False
GOLD_FINAL = False
SNAPSHOT_INTERVAL_SECONDS = 300
```

Conserva los demás hiperparámetros. Es un entrenamiento real, hasta cuatro épocas;
no es el ensayo con métricas ficticias de instalación. Si ese RUN_ID ya tiene
entrenamiento de otra configuración experimental, usa uno nuevo.

Autoriza el montaje de Drive y ejecuta las secciones **2 a 10.1**, en orden.
Antes de ejecutar la sección 11 verifica:

- GPU A100 detectada y BF16 disponible.
- `MAIA_TESIS/TrainingData_Grupo15` y los ocho lotes de
  `MAIA_PROYECTO/a2/batches_norw/` encontrados.
- Para los datos actuales V0: 28.039 ejemplos de entrenamiento y 3.226 de validación.
- Sin errores de hashes, exclusiones ni reconstrucción de textos.
- Sección 10.1: mensaje `MLflow listo` y primer `MLflow respaldado` en Drive.

La sección 10.1 recupera automáticamente el último snapshot con `COMPLETE.json`,
incluido el ensayo de instalación. Si falla su integridad, se detiene;
no descarta silenciosamente el historial ni crea una base vacía para reemplazarlo.

## 3. Entrenar y terminar la ejecución

1. Ejecuta **11**. Se registra un padre `RUN_ID/base` y un hijo por intento
   dentro del experimento **`G15_A4_SciBERT`**.
2. Las curvas incluyen loss, learning rate, grad norm y época cuando Trainer los
   emite, cada 50 pasos de optimización. La validación se registra por época.
3. El respaldo de historial se comprueba al terminar cada paso; cuando han pasado
   300 segundos publica una copia consistente. Durante validación o preparación
   puede transcurrir más tiempo. También publica al guardar checkpoints y al cerrar.
4. Ejecuta **12**: comprueba toda la validación contra el checkpoint, compara las
   precisiones y genera reportes FP32 en `evaluations/v2_fp32_<id>/`, también en MLflow.
5. Ejecuta **13**: con la configuración inicial informa que T_B final está pendiente.
6. Ejecuta **14**: empaqueta el modelo, actualiza los reportes y publica el snapshot final.
7. Guarda el notebook con sus salidas en Drive antes de cerrar Colab.

Los archivos se guardan en:

```text
MAIA_TESIS/a4/g15_a4_v0_seed42_mlflow_01/
  base/checkpoints/checkpoint-*/     # pesos, optimizador, estado y A4_COMPLETE.json
  base/model/                      # pesos, tokenizer y módulo de inferencia
  base/TRAINING_COMPLETE.json       # hashes de la exportación e ID del intento
  base/validation_*.json|csv|png
  scibert_g15_base.zip
  ...manifiestos y auditorías...
MAIA_TESIS/a4/_tracking/snapshots/<id>/
  snapshot.zip
  snapshot.sha256
  COMPLETE.json
```

MLflow contiene parámetros, métricas, reportes y referencias al modelo en Drive.
Los snapshots **no contienen los pesos**; para recuperar entrenamiento necesitas
también la carpeta del RUN_ID. La base SQLite activa no está sobre Drive.

## 4. Consultar la primera corrida en AWS

1. Elige el último snapshot completo de Drive; espera a que termine su publicación.
2. Descarga juntos sus tres archivos a `snapshot_A4/` en la carpeta local del proyecto.
3. Sigue la [guía de instalación, sección 7.1](README_INSTALACION.md#71-actualizar-el-panel-con-un-snapshot-nuevo):
   transfiere los archivos, detén el visor, restaura a una carpeta nueva y recrea
   el contenedor con ese montaje. Conserva MLflow **3.17.2**.
4. Abre el túnel SSH con la IP pública vigente y entra en `http://localhost:5000`.
5. Selecciona **G15_A4_SciBERT → Runs/Ejecuciones**, limpia filtros y expande
   `g15_a4_v0_seed42_mlflow_01/base` para abrir el intento. En **Metrics** verás las curvas;
   en **Artifacts**, reportes y manifiestos. Las etiquetas indican rutas de Drive.

El experimento `G15_A4_instalacion_smoke` seguirá siendo el ensayo anterior.
Para ver avances posteriores debes restaurar otro snapshot; la copia de AWS
no devuelve cambios al historial original de Colab.

## 5. Recuperar una interrupción

En un Colab nuevo con A100 abre la misma copia, conserva RUN_ID, datos, versiones
e hiperparámetros y cambia **solo `RESUME = True`**. Ejecuta desde el principio.
La revisión exacta de SciBERT se toma del manifiesto previo.

La sección 10.1 restaura el historial, cierra como `KILLED` los runs pendientes
de ese RUN_ID y la sección 11 crea otro intento hijo. El entrenamiento continúa
desde el checkpoint más reciente con `A4_COMPLETE.json` y hashes válidos.
Los checkpoints parciales se omiten; si no hay ninguno válido se detiene.
Los pasos posteriores al checkpoint se vuelven a calcular en el intento nuevo.

Si la exportación ya tiene `TRAINING_COMPLETE.json` y todos sus hashes coinciden,
se omite el entrenamiento de ese modelo y puedes continuar con 12–14.
No se garantiza recuperar antes de terminar la primera época: todavía no hay
checkpoint. No cambies el batch ni otros parámetros para retomar el mismo RUN_ID.

Si aparece una excepción, conserva el mensaje y la salida de la celda. Los errores
atrapados se registran como `FAILED`; la pérdida brusca de la sesión solo puede
reconstruirse hasta el último snapshot y checkpoint terminados.

## 6. Entrenar fragmentos después

En una sesión limpia, conserva `RUN_ID`, V0, semilla y demás decisiones;
establece `CONFIGS = ["base", "fragmentos"]` y `RESUME = True`.
Se verificará y omitirá `base` ya terminado; `fragmentos` partirá del SciBERT
original, entrenará su propia cabeza y usará la misma partición. Ejecuta hasta 14
para obtener la tabla de comparación de validación. T_B sigue desactivado.

Para otro experimento (semilla, variante o hiperparámetros), usa **otro RUN_ID**.

## Validación previa a la entrega

Pasaron seis pruebas del notebook (contratos, aislamiento, reconstrucción de los
34.775 textos, sintaxis y exportación con un BERT pequeño), cuatro del seguimiento
y cuatro de evaluación. Las pruebas con MLflow 3.17.2 y Transformers 4.57.1 comprueban curvas,
artefactos, cierre con error, restauración, intentos separados, rechazo de copias
alteradas y entrenamiento/reanudación reales con un BERT pequeño en CPU.
El ensayo parte sin carpeta de modelo, interrumpe después de la primera época y
reanuda con la misma configuración, incluida la selección del mejor checkpoint.
La evaluación comprueba todos los ejemplos de un conjunto pequeño, reproduce BF16
en CPU y rechaza pesos exportados diferentes. También verifica reportes por clase
y conserva los archivos de métricas previos.
La primera corrida de SciBERT base ya terminó en Colab A100. La evaluación
versionada y la comparación con fragmentos se validarán en la siguiente corrida.

Referencias de implementación: [callbacks de Transformers 4.57.1](https://huggingface.co/docs/transformers/v4.57.1/en/main_classes/callback)
y [cliente de MLflow](https://mlflow.org/docs/latest/api_reference/python_api/mlflow.client.html).
