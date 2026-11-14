## Conclusiones

Comparamos Top-1 y Top-3 sobre las mismas 1,653 citas de validación, con tres semillas y los mismos parámetros. Top-1 obtuvo F1 macro medio **0.8304 ± 0.0063** y Top-3, **0.8261 ± 0.0016**: la diferencia media fue de 0.44 puntos porcentuales por encima de Top-3. Top-1 lo superó en **2 de 3 semillas** y tuvo mayor variación entre corridas; esa comparación describe tanto el promedio como su estabilidad.

El texto elegido necesitó recorte en el **12.04%** de Top-1 y el **91.59%** de Top-3. Frente a la evidencia original de los tres fragmentos, Top-1 conservó en promedio el **33.77%** de los tokens y Top-3, el **59.32%**. Top-1 destinó más espacio al primer fragmento y omitió otros dos; por eso el menor recorte del texto elegido debe leerse junto con la cantidad de evidencia conservada.

Improvement/Modification tuvo 140 ejemplos de entrenamiento y 19 de validación. En los modelos de semilla 42, Top-1: 13/19 citas recuperadas, F1 0.7222 y precisión 0.7647; Top-3: 12/19 citas recuperadas, F1 0.7059 y precisión 0.8000. El soporte de esta clase es reducido. La validación reúne 125 etiquetas humanas y 1528 automáticas. Conservamos la semilla 42 como modelo principal y guardamos los modelos y sus reportes. Estas cifras corresponden a validación interna; el test propio permanece separado del entrenamiento y de la selección.
