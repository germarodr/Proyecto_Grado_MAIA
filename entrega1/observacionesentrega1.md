## Instrucción
Entregue en este espacio la primera versión de la solución inicial y el informe de avance que documente el enfoque adoptado, los avances logrados y los desafíos encontrados.

---

## Rúbrica de evaluación

| Criterio | Ponderación |
| :--- | :--- |
| Descripción breve de la propuesta de solución | 10% |
| Recolección y preparación de los datos | 15% |
| Descripción del proceso de construcción de los modelos o solución | 35% |
| Resultados obtenidos | 10% |
| Análisis de los resultados obtenidos | 20% |
| Referencias | 5% |
| Presentación y redacción | 5% |

---

## Calificación obtenida: 81 / 100 puntos (81%)

### Retroalimentación por criterio

* **Descripción breve de la propuesta de solución**
  * **Puntaje:** 10 / 10 puntos
  * **Comentarios:** Es sólido y puede mejorarse el sintetizar el aporte diferenciador de la solución y sus beneficios.

* **Recolección y preparación de los datos**
  * **Puntaje:** 12 / 15 puntos
  * **Comentarios:** Cuando mencionan que se usa el promedio de extracción de representaciones con máscara de atención, ¿a qué se refieren? ¿Por qué el promedio, qué consideran? También se observa desbalance entre las categorías minoritarias y una concentración temática importante en `cs.CV`; de existir una razón importante de selección, deben incorporarlo en el documento.

* **Descripción del proceso de construcción de los modelos**
  * **Puntaje:** 20 / 35 puntos
  * **Comentarios:** ¿Por qué escogen 60 para la muestra (`eval60`) y cómo escogen el set de esos 60? No se describe cómo se plantea abordar el modelo del proyecto para clasificación por medio de *fine-tuning*. ¿Qué modelos proponen? ¿Con qué configuración?

* **Resultados obtenidos**
  * **Puntaje:** 10 / 10 puntos
  * **Comentarios:** Faltó la evaluación humana de P@3. Recomendación: consolidar una tabla de los indicadores para los resultados de recuperación, pre-etiquetado y validación humana.

* **Análisis de los resultados obtenidos**
  * **Puntaje:** 20 / 20 puntos
  * **Comentarios:** En la experimentación realizada hasta el momento, es importante presentar de mejor manera con un conjunto de experimentos de hipótesis y resultados buscando ese mejor modelo.

* **Referencias**
  * **Puntaje:** 5 / 5 puntos
  * **Comentarios:** Buena presentación e incluye fuentes bibliográficas.

* **Presentación y redacción (No se excede del número de páginas)**
  * **Puntaje:** 4 / 5 puntos
  * **Comentarios:** Cuidado cuando usan nombres para referirse a términos y no los han definido previamente. No excede el límite de páginas; deben mejorar la redacción e hilo conductor del documento, dado que al estar enfocado muy técnicamente, no queda claro en algunos puntos si hablan de decisiones o de resultados principales.