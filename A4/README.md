# A4 · Clasificación supervisada de funciones de cita

En esta etapa entrenamos SciBERT para distinguir nueve funciones de cita y comparamos dos entradas: contexto, título y resumen del artículo citado, frente a contexto y tres fragmentos recuperados con sus secciones. La evaluación final utiliza los mismos modelos seleccionados en validación y un test humano separado por documento.

## Documentación principal

| Contenido | Referencia |
|---|---|
| Resultados finales, datos y modelos seleccionados | [Métricas de A4](Final/M%C3%A9tricas.md) |
| Experimentos de reparto de tokens y ponderación de clases | [Estudios y procedimiento](Final/Experimentos/README.md) |
| Diagnóstico de regularización y sobreajuste | [Regularización](Final/Experimentos/README_Regularizacion.md) y [conclusiones](Final/Experimentos/Conclusiones_Regularizacion.md) |
| Modelos, entradas y salidas | [Contrato de inferencia](Final/Modelos_Entradas_Salidas.md) |
| Evaluación con referencias humanas | [Protocolo y resultados](Evaluacion_Final/README.md) y [notebook ejecutado](Evaluacion_Final/SciBERT_Evaluacion_Final.ipynb) |
| Evolución de las iteraciones | [Índice de Final](Final/README.md), [histórico](Final/Historico/README.md) y [copias iniciales](pruebascolab/) |

## Qué encontramos

Los estudios de reparto del texto y pesos por clase conservaron el control con contexto de hasta 192 tokens y pérdida sin ponderación. Ninguna alternativa mejoró el F1 macro medio de tres semillas. Seleccionamos los modelos de semilla 42 con LR 3e-5 y weight decay 0,1: época 5 para base y época 7 para Top-3.

Sobre 2.968 citas humanas, base obtuvo F1 macro 0,7967 y Top-3 0,8000. La diferencia de +0,32 puntos porcentuales tuvo un intervalo del 95 % de [−0,75; +1,39], por lo que no permite afirmar una ventaja clara de Top-3. El diagnóstico posterior de regularización conservó señales de sobreajuste y no sustituyó los modelos evaluados ni sus resultados.

Fuentes: [métricas finales](Final/M%C3%A9tricas.md), [comparación de experimentos](Final/Experimentos/Comparacion_Reparto_vs_Pesos.md) y [conclusiones del test](Evaluacion_Final/conclusiones.md).

## Seguimiento y recuperación

Los entrenamientos registran parámetros, métricas y artefactos en MLflow con SQLite en el servidor de ejecución. Google Drive conserva los modelos, checkpoints y snapshots completos. El visor en AWS restaura una copia del historial; no necesita estar encendido durante el entrenamiento ni actualiza esa copia en tiempo real.

La [guía de instalación](README_INSTALACION.md) describe la preparación y restauración del visor. Cada estudio conserva su propio identificador y ruta de resultados: deben respetarse al recuperar una ejecución para no mezclar experimentos.

## Procedimientos e iteraciones iniciales

[Primera corrida](PRIMERA_CORRIDA.md), [segunda corrida](SEGUNDA_CORRIDA.md), [aislamiento V2](README_V2.md), [training v2 con etiquetas humanas](README_TRAINING_V2_GOLD.md), [variante independiente](README_INDEPENDIENTE.md) y [comparación Top-1](README_TOP1.md) documentan decisiones anteriores. Sus datos y métricas corresponden a esas iteraciones; la entrega final se identifica en los documentos principales.

Los notebooks ejecutados y sus históricos conservan sus salidas. La exploración Top-1 no forma parte de la comparación final base frente a Top-3.
