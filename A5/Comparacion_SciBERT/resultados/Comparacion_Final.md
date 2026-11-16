# Comparacion final: SciBERT base, Luna y Gemini

Los tres modelos se evaluan sobre los mismos 2968 casos y las mismas etiquetas humanas.
Las respuestas invalidas se conservan como errores. F1 micro coincide con accuracy.

| Modelo | Condicion | F1 macro | F1 micro | Delta macro vs SciBERT | IC 95% del delta |
|---|---|---:|---:|---:|---|
| SciBERT base | base | 0.7967 | 0.7921 | +0.0000 | Referencia |
| gpt-6-luna | base-generic-few | 0.7217 | 0.7325 | -0.0751 | [-0.0948, -0.0561] |
| gpt-6-luna | base-generic-zero | 0.6635 | 0.6715 | -0.1332 | [-0.1538, -0.1129] |
| gpt-6-luna | base-specific-few | 0.7953 | 0.8012 | -0.0014 | [-0.0197, 0.0162] |
| gpt-6-luna | base-specific-zero | 0.7925 | 0.7968 | -0.0042 | [-0.0223, 0.0122] |
| gemini-3.5-flash-lite | base-generic-few | 0.6422 | 0.6469 | -0.1545 | [-0.1743, -0.1353] |
| gemini-3.5-flash-lite | base-generic-zero | 0.5821 | 0.5809 | -0.2147 | [-0.2356, -0.1954] |
| gemini-3.5-flash-lite | base-specific-few | 0.7139 | 0.7102 | -0.0828 | [-0.1007, -0.0653] |
| gemini-3.5-flash-lite | base-specific-zero | 0.7481 | 0.7476 | -0.0487 | [-0.0669, -0.0311] |

## Interpretacion

SciBERT base obtiene F1 macro 0,7967; Luna especifico con ejemplos obtiene 0,7953.
La diferencia descriptiva es pequena; revisar el intervalo pareado antes de atribuir superioridad.
No se seleccionan ni modifican prompts con los resultados de T_B.

## Metodo y alcance

Bootstrap pareado con 2000 repeticiones, semilla 20261113, agrupado por articulo citante.
Mismas muestras bootstrap para todos los modelos. Intervalos percentiles bilaterales del 95%.
Comparaciones exploratorias sin ajuste por multiplicidad; no representan una prueba de equivalencia.
Se comparan etiquetas finales; esta verificacion no certifica identidad byte a byte del texto de entrada.
Los costos API y las latencias por lote de SciBERT no se usan para afirmar una ventaja directa de eficiencia.
No hubo entrenamiento ni nuevas inferencias. Originales conservados y hashes incluidos en el JSON.
