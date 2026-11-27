# Modelos finales de SciBERT

Esta carpeta contiene la distribución de los dos clasificadores supervisados seleccionados en A4: **SciBERT base** y **SciBERT Top-3**. Ambos asignan una de nueve funciones a una cita académica. Se entrenaron sobre las mismas particiones y se evaluaron, sin modificar sus parámetros, sobre 2.968 citas con referencia humana.

Los paquetes se gestionan mediante **Git Large File Storage (Git LFS)** debido a su tamaño. Los enlaces de Drive se conservan como alternativa de descarga. Cada ZIP debe extraerse completo: los pesos, el tokenizador y la política de entrada forman una misma exportación.

## 1. Inventario y procedencia

| Modelo | Paquete | Tamaño comprimido | Entrada | Descarga alternativa |
|---|---|---:|---|---|
| SciBERT base | `scibert_base_final.zip` | 408.779.494 bytes · 408,78 MB | Contexto de la cita, título y resumen del citado. | [Modelo base en Drive](https://drive.google.com/file/d/1R1bOASEXroBe22lgI57qp-g28iZqaynG/view) |
| SciBERT Top-3 | `scibert_fragmentos_final.zip` | 408.780.338 bytes · 408,78 MB | Contexto de la cita y tres fragmentos del citado, con sus secciones. | [Modelo Top-3 en Drive](https://drive.google.com/file/d/1Y6_RADwbvXl9VY5OLfpaOY8BL77syUrd/view) |

El total comprimido es **817,56 MB**, aproximadamente **0,76 GiB**. Los tamaños en MB utilizan unidades decimales; los ZIP requieren espacio adicional al extraerse.

Los dos modelos proceden del estudio `g15_scibert_reparto_v2_01`, cuyo cierre está en [SciBERT_Reparto_Tokens_Recuperacion.ipynb](../A4/Final/Experimentos/SciBERT_Reparto_Tokens_Recuperacion.ipynb). La selección conservó contexto de hasta 192 tokens, pérdida sin pesos por clase, tasa de aprendizaje `3e-5`, weight decay `0,1` y semilla principal 42. Los checkpoints seleccionados corresponden a las épocas 5 para base y 7 para Top-3.

| Evidencia | Referencia |
|---|---|
| Selección de modelos y archivos de origen | [Selección congelada](../A4/Evaluacion_Final/seleccion_congelada.json) |
| Identificadores, tamaños y huellas de los paquetes | [Manifiesto de distribución](modelos_manifest.json) |
| Inferencia sobre el test humano | [Notebook de evaluación final](../A4/Evaluacion_Final/SciBERT_Evaluacion_Final.ipynb) |
| Métricas, limitaciones y archivos de resultados | [Métricas de A4](../A4/Final/M%C3%A9tricas.md) |

La exploración Top-1 y el diagnóstico posterior de regularización no sustituyen estos modelos finales. La ponderación de clases seleccionó los mismos pesos que el estudio de reparto, por lo que no se distribuye otra copia equivalente. Los modelos comerciales se consultan mediante API; sus pesos no forman parte de esta entrega.

## 2. Descarga mediante Git LFS

Instalar Git LFS en el equipo de destino antes de clonar el repositorio. El seguimiento de los paquetes está definido en [`.gitattributes`](../.gitattributes).

```sh
git lfs install
git clone https://github.com/germarodr/Proyecto_Grado_MAIA.git
cd Proyecto_Grado_MAIA
git lfs pull --include="Modelos/*.zip"
git lfs ls-files
```

Si el repositorio ya está clonado, ejecutar los dos últimos comandos desde su raíz. Sin Git LFS, los ZIP pueden ser archivos de referencia pequeños y no los paquetes reales. La descarga desde Drive permite obtener las mismas exportaciones sin utilizar LFS; su acceso depende de los permisos del recurso.

Git LFS utiliza las cuotas de almacenamiento y descarga del propietario del repositorio. Cada versión nueva de un archivo grande consume almacenamiento adicional; deben evitarse publicaciones repetidas de paquetes que no hayan cambiado. Referencia: [configuración de Git LFS](https://docs.github.com/en/repositories/working-with-files/managing-large-files/configuring-git-large-file-storage).

## 3. Contenido de cada paquete

Los ZIP contienen los archivos en su raíz, sin un directorio intermedio. Entre ellos se encuentran:

```text
model.safetensors           # pesos ajustados
config.json                 # arquitectura y configuración del clasificador
tokenizer.json              # tokenizador y archivos complementarios
input_policy.json           # preparación y recorte de las entradas
label_mapping.json          # correspondencia de las nueve categorías
inference.py                # clase CitationClassifier
api_contract.json           # contrato de entrada y salida
run_manifest.json           # procedencia del modelo
```

Extraer cada ZIP en un directorio independiente. La aplicación del demostrador utiliza la exportación Top-3 en `Demostrador/models/top3/`; debe conservarse esa ubicación según su [guía de instalación](../Demostrador/README.md).

## 4. Uso para inferencia

`inference.py` proporciona la clase `CitationClassifier` y su método `predict`. Recibe textos, aplica la política exportada y devuelve una categoría, nueve puntajes y una auditoría de tokens. No constituye por sí solo un servidor web ni ejecuta la recuperación de fragmentos.

| Modelo | Campos del ejemplo |
|---|---|
| Base | `context`, `title`, `abstract` |
| Top-3 | `context`, `chunks`: tres elementos con `text` y `section` |

El contexto debe contener exactamente un marcador `[[TARGET]]` para identificar la cita objetivo. La política conserva hasta 192 tokens de contexto y un máximo de 512 tokens en toda la entrada. Los fragmentos se proporcionan como texto; no se envían los embeddings utilizados previamente para recuperarlos.

Los contratos completos y los ejemplos se documentan en [Modelos, entradas y salidas](../A4/Final/Modelos_Entradas_Salidas.md). Para utilizar una API HTTP y la interfaz de consulta, seguir la [documentación del demostrador](../Demostrador/README.md).

## 5. Verificación de los paquetes

El archivo `modelos_manifest.json` conserva los tamaños y SHA-256 de los ZIP y de los pesos seleccionados. Estas huellas permiten identificar los modelos evaluados y detectar una descarga incompleta o una sustitución accidental. El manifiesto reproduce la selección congelada de A4; no se recalculan ni se modifican los modelos al distribuirlos.

La evaluación final obtuvo F1 macro **0,7967** para base y **0,8000** para Top-3. La diferencia no fue concluyente: el intervalo de confianza incluye cero. Estas cifras corresponden al test humano del proyecto y no garantizan el mismo desempeño en otros corpus.
