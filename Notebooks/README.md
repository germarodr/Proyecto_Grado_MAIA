# Cuadernos de análisis, entrenamiento y evaluación

Esta carpeta reúne una selección de los cuadernos de la entrega. Las copias conservan el código, los identificadores de celda, los metadatos, los contadores de ejecución y las salidas de sus archivos de origen. Los enlaces de las celdas Markdown se adaptaron a esta ubicación. No se ejecutaron nuevamente los experimentos para preparar estas copias.

Los originales permanecen en `A4/` y `A5/`, junto con la documentación y los históricos. Las copias permiten localizar los entregables; para mantener la evolución de los estudios debe utilizarse una única versión de trabajo y actualizar la copia de entrega cuando corresponda.

## 1. Entrenamiento y evaluación de SciBERT

| Cuaderno de entrega | Contenido | Original |
|---|---|---|
| [Reparto de tokens](A4/SciBERT_Reparto_Tokens.ipynb) | Análisis de los datos, búsqueda de hiperparámetros y comparación de presupuestos de contexto para base y Top-3. Conserva el cierre de la ejecución recuperada. | [Cuaderno del estudio](../A4/Final/Experimentos/SciBERT_Reparto_Tokens_Recuperacion.ipynb) |
| [Ponderación de clases](A4/SciBERT_Pesos_Clases.ipynb) | Comparación del control sin pesos con raíz inversa e inversa limitada. | [Cuaderno del estudio](../A4/Final/Experimentos/SciBERT_Pesos_Clases.ipynb) |
| [Regularización](A4/SciBERT_Base_Regularizacion.ipynb) | Diagnóstico del modelo base mediante pérdida de validación, dropout y weight decay. No sustituye el test final. | [Cuaderno del estudio](../A4/Final/Experimentos/SciBERT_Base_Regularizacion.ipynb) |
| [Evaluación final](A4/SciBERT_Evaluacion_Final.ipynb) | Inferencia de los modelos congelados, métricas, matrices de confusión, contraste pareado y conclusiones sobre el test humano. | [Cuaderno de evaluación](../A4/Evaluacion_Final/SciBERT_Evaluacion_Final.ipynb) |

Estos cuatro cuadernos conservan sus salidas guardadas. Para reproducirlos se requieren los datos y paquetes indicados en sus configuraciones, acceso autorizado a Drive y el entorno verificado por sus primeras celdas. La [guía de experimentos](../A4/Final/Experimentos/README.md) y el [protocolo de evaluación](../A4/Evaluacion_Final/README.md) describen la ejecución y la recuperación.

## 2. Evaluación comercial y comparación

| Cuaderno de entrega | Contenido | Original |
|---|---|---|
| [Modelo comercial](A5/A5_Modelo_Comercial_G15.ipynb) | Preparación y evaluación del flujo comercial de A5. | [Cuaderno de A5](../A5/A5_Modelo_Comercial_G15.ipynb) |
| [Gemini](A5/A5_Gemini_G15.ipynb) | Flujo específico de Gemini, prompts, consultas y registro de resultados. | [Cuaderno de Gemini](../A5/Gemini/A5_Gemini_G15.ipynb) |
| [Comparación de métricas](A5/Comparacion_Metricas_A5.ipynb) | Lectura de reportes y comparación de SciBERT con los modelos comerciales. | [Cuaderno de comparación](../A5/Comparacion_Metricas_A5.ipynb) |

Los cuadernos comerciales se distribuyen con el estado de salidas de sus originales; su presencia no implica que incluyan todas las respuestas de las evaluaciones. La evidencia consolidada está en [Análisis final de A5](../A5/Analisis_Final_A5.md) y [Comparación final](../A5/Comparacion_SciBERT/resultados/Comparacion_Final.md).

### Dependencias y rutas de A5

Las copias no duplican los módulos funcionales. Antes de ejecutar, configurar `A5_DIR` con la ruta absoluta de `A5/` para el cuaderno comercial o `A5/Gemini/` para Gemini, según el entorno. Esas carpetas contienen `a5_runtime.py`, `a5_drive.py`, `a5_alignment.py`, `a5_providers.py` y el snapshot del prompt. Si se activa el seguimiento, deben conservarse también las rutas de sus módulos de MLflow.

Para la comparación, `RESULTS_DIR` debe apuntar a `A5/Comparacion_SciBERT/resultados/` o a la ubicación de los CSV completos. Las rutas de Drive y las credenciales se configuran en el entorno de ejecución; no deben incorporarse al repositorio. Las consultas a proveedores pueden generar cargos.

## 3. Recursos relacionados

- [Modelos finales mediante Git LFS](../Modelos/README.md).
- [Muestra de datos y estructura](../Datos/README.md).
- [Métricas de SciBERT](../A4/Final/M%C3%A9tricas.md).
- [Aplicación y despliegue](../Demostrador/README.md).

La muestra de `Datos/` permite examinar las entradas del demostrador. No sustituye las particiones completas de entrenamiento, validación y test que requieren los cuadernos.
