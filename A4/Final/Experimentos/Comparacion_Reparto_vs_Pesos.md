# Reparto de tokens frente a pesos por clase

Los dos estudios terminaron: 28 entrenamientos y 18 resultados comparables por estudio (dos controles se reutilizan). La revisión de cada cierre recalculó métricas y comprobó referencias, probabilidades, archivos de modelo y aislamiento por documento sobre 46.284 filas de predicciones. En esta revisión se verificaron además los hashes de los reportes de ambos cierres y la igualdad de las particiones.

| Prueba | F1 macro medio base | F1 macro medio Top-3 |
|---|---:|---:|
| Control: 192 tokens, sin pesos | 0,832861 | 0,826120 |
| Contexto 128 | 0,832815 | 0,820338 |
| Contexto 256 | 0,825601 | 0,824624 |
| Pesos: raíz inversa | 0,828316 | 0,824820 |
| Pesos: inversa limitada | 0,827102 | 0,815310 |

Ninguna alternativa superó el F1 macro medio del control de su entrada. Los pesos raíz inversa e inversa limitada cambiaron el F1 de base en −0,45 y −0,58 puntos porcentuales; en Top-3, −0,13 y −1,08 puntos. Esto no implica que ninguna clase individual mejore. Ambos estudios seleccionan los mismos pesos de modelo, verificados por SHA-256, y los controles coincidentes no constituyen evidencia independiente adicional. La media de tres semillas describe estabilidad; no es un intervalo de confianza.

Es viable cerrar la selección y preparar el test final, sin más búsqueda sobre su resultado. Se congelan los dos modelos de semilla 42 del estudio de reparto: contexto 192, pérdida sin pesos, LR 3e-5 y weight decay 0,1 en ambos; mejores épocas 5 (base) y 7 (Top-3). Su F1 macro individual de validación es 0,830298 y 0,830071, distinto de la media entre semillas. Antes de inferir se validan los hashes y las 2.968 instancias evaluables de T_B, se reconstruyen ambas entradas y se comprueba ausencia de documentos compartidos con train/validación. El test se utiliza para la evaluación final, no para elegir parámetros. La insuficiencia respecto de 2.000 ejemplos por clase debe declararse y acordarse con el asesor; evaluar no subsana ese requisito.

## Entrega para A6

1. Congelar IDs de modelos, hashes, preparación del texto, nueve etiquetas y lista de instancias de test.
2. Ejecutar únicamente inferencia de base y Top-3 sobre las mismas instancias, con etiquetas humanas como referencia.
3. Exportar predicciones, nueve probabilidades y latencia; P/R/F1 macro y micro, métricas por clase y matrices de confusión.
4. Calcular la diferencia de F1 con bootstrap pareado por artículo citante, conservar errores representativos y entregar los CSV a A6.
5. No retocar los modelos según el test. Cualquier experimento posterior se identifica como tal y no reemplaza la medición final.

Fuentes: MAIA_TESIS/a4/g15_scibert_{reparto,pesos}_v2_01/{condition_summary.csv,selected_models.json,validation_review.json,STUDY_COMPLETE.json}; auditoría cruzada guardada junto a este documento.
