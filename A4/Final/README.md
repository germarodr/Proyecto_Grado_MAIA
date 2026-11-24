# A4 · Modelos, experimentos y resultados

Esta carpeta reúne los experimentos de SciBERT y la documentación de sus entradas y resultados. Los dos modelos seleccionados para la evaluación final son **base** y **Top-3**. Las variantes anteriores se conservan para documentar la evolución del trabajo.

## Entrega principal

| Recurso | Contenido |
|---|---|
| [Métricas](M%C3%A9tricas.md) | Datos utilizados, selección congelada, resultados del test y enlaces a los modelos y reportes de Drive. |
| [Experimentos](Experimentos/README.md) | Búsquedas de parámetros, reparto de tokens y pesos por clase. |
| [Regularización](Experimentos/README_Regularizacion.md) | Diagnóstico adicional de pérdida, dropout y weight decay. |
| [Entradas y salidas](Modelos_Entradas_Salidas.md) | Campos de texto, tokenización y contrato de inferencia. |
| [Evaluación final](../Evaluacion_Final/README.md) | Inferencia de base y Top-3 sobre el test humano separado. |

## Selección y resultados

Los estudios de reparto y ponderación conservaron contexto de hasta 192 tokens y pérdida sin pesos por clase. Los modelos principales utilizan semilla 42, LR 3e-5 y weight decay 0,1; los checkpoints seleccionados corresponden a las épocas 5 y 7 para base y Top-3, respectivamente.

Evaluamos ambos modelos sobre 2.968 citas humanas. Base alcanzó F1 macro 0,7967 y Top-3 0,8000; el intervalo de confianza de la diferencia incluye cero. Las tablas completas y las limitaciones están en [Métricas](M%C3%A9tricas.md) y en las [conclusiones de evaluación](../Evaluacion_Final/conclusiones.md).

## Comparación exploratoria Top-1 frente a Top-3

El archivo [SciBERT_Entrenamiento_Final.ipynb](SciBERT_Entrenamiento_Final.ipynb) conserva una iteración exploratoria Top-1 frente a Top-3. Su nombre es anterior a la selección final; no debe confundirse con los modelos entregados para el test.

En esa validación interna, Top-1 obtuvo F1 macro medio 0,8304 ± 0,0063 y Top-3 0,8261 ± 0,0016. La ventaja media fue de 0,44 puntos porcentuales y apareció en dos de tres semillas; Top-1 mostró mayor variación. Estos resultados corresponden a esa comparación, no al test humano.

La [copia revisada](Historico/Iteracion_02_2026-11-11_Revisada/README.md) conserva las auditorías y las salidas de la exploración. Las iteraciones anteriores están en el [índice del histórico](Historico/README.md). Se mantienen como evidencia de sus respectivas ejecuciones.
