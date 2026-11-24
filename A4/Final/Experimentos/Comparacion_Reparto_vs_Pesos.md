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

La selección conservó los dos modelos de semilla 42 del estudio de reparto: contexto 192, pérdida sin pesos, LR 3e-5 y weight decay 0,1 en ambos; mejores épocas 5 (base) y 7 (Top-3). Su F1 macro individual de validación fue 0,830298 y 0,830071, distinto de la media entre semillas. Después se evaluaron los modelos congelados sobre 2.968 citas humanas: base alcanzó F1 macro 0,796728 y Top-3 0,799951. El intervalo del 95 % de la diferencia fue [−0,75; +1,39] puntos porcentuales, sin una ventaja concluyente. El test no se utilizó para elegir parámetros. La escasez de varias categorías continúa siendo una limitación de los datos.

## Entrega para la evaluación comparativa

La [evaluación final](../../Evaluacion_Final/README.md) conserva los identificadores
de los modelos, las particiones, las predicciones, los nueve puntajes, las métricas
por clase, las matrices de confusión y el bootstrap pareado por artículo citante.
Los modelos permanecieron congelados durante esa medición. El diagnóstico posterior
de regularización se documentó por separado y no reemplazó los resultados del test.

Fuentes: MAIA_TESIS/a4/g15_scibert_{reparto,pesos}_v2_01/{condition_summary.csv,selected_models.json,validation_review.json,STUDY_COMPLETE.json}; auditoría cruzada guardada junto a este documento.
