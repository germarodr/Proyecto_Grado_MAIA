## Conclusiones

Comparamos Top-1 y Top-3 con las mismas 1,653 citas de validación, tres semillas y los mismos parámetros. Top-1 obtuvo F1 macro medio **0.8304 ± 0.0063** y Top-3, **0.8261 ± 0.0016**. La diferencia media emparejada fue de 0.44 puntos porcentuales por encima de Top-3.

El texto elegido necesitó recorte en el **12.04%** de Top-1 y en el **91.59%** de Top-3. Top-1 eligió el primer fragmento y dejó fuera otros dos: conservó, en promedio, el 33.77% de los tokens disponibles en los tres fragmentos originales. Estas dos medidas permiten distinguir el recorte del fragmento elegido de la información descartada al seleccionar uno solo.

Improvement/Modification tuvo 140 ejemplos de entrenamiento y 19 de validación. En los modelos de semilla 42, Top-1: 13/19 citas recuperadas; Top-3: 12/19 citas recuperadas. Guardamos el modelo Top-1 principal con esa semilla y conservamos Top-3 como referencia de la primera iteración. Las cifras corresponden a validación interna; el test propio permanece separado.
