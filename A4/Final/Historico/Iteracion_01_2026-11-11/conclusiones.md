## Conclusiones

Entrenamos con 11,616 ejemplos y validamos con 1,653. Comparamos 12 combinaciones y añadimos 4 entrenamientos para medir la variación entre semillas. En la evaluación FP32, base obtuvo **F1 macro 0.8306** y Top-3 **0.8254**: Top-3 quedó 0.52 puntos porcentuales por debajo de base. Los ajustes elegidos fueron ritmo 2e-05 y regularización 0.1 para base; ritmo 3e-05 y regularización 0.01 para Top-3.

Con 3 semillas, el F1 macro medio y su desviación fueron **base: 0.8309 ± 0.0007; fragmentos: 0.8261 ± 0.0016**. La clase Improvement/Modification contó con 140 ejemplos de entrenamiento y 19 de validación; base: 12/19 citas recuperadas; Top-3: 12/19 citas recuperadas. Ese soporte reducido limita cuánto podemos generalizar el resultado de esta clase.

Top-3 recortó texto en el **91.59%** de los ejemplos de validación. Ese dato describe la información que llegó al modelo; por sí solo no demuestra la causa de la diferencia de desempeño. Los modelos principales conservan la semilla 42 y quedaron guardados con sus reportes y verificaciones. Todas estas cifras corresponden a validación interna; el conjunto humano de test permanece separado del entrenamiento y de la selección de parámetros.
