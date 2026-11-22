# Regularización del modelo base

Este experimento adicional estudia las señales de sobreajuste observadas después
de la tercera época. No reemplaza el test humano final ni lo utiliza para elegir
los ajustes. El [notebook](SciBERT_Base_Regularizacion.ipynb) es autónomo y conserva
la presentación, distribución de datos y secciones explicadas de los anteriores.

| Condición | Dropout oculto, atención y clasificador | Weight decay |
|---|---:|---:|
| Control | 0,10 | 0,10 |
| Más dropout | 0,20 | 0,10 |
| Mayor penalización de pesos | 0,10 | 0,20 |

Son nueve entrenamientos: tres condiciones por semillas 42, 17 y 73. Todos
empiezan desde la misma revisión preentrenada de SciBERT; ritmo 3e-5, contexto
192, máximo 512 tokens, batch efectivo 32, seis épocas máximas y paciencia dos.
El checkpoint se selecciona por menor pérdida de validación BF16; los modelos
exportados se comprueban y las métricas se calculan en FP32. Se informan pérdida,
F1, variación entre semillas y curvas. La candidata por menor pérdida media
conserva la semilla 42; no implica automáticamente mejor F1.

El control usa la misma nueva regla de parada que las alternativas. Comparar
directamente contra la antigua selección por F1 mezclaría ese cambio con el
efecto de la regularización. Las curvas registradas de train son promedios de
minibatches, no pérdida de entrenamiento medida sobre todo el conjunto.

Los hashes deben reproducir las particiones anteriores: 11.616 train y 1.653
validación. La validación contiene 125 etiquetas humanas y 1.528 automáticas.
El test propio se utiliza únicamente para auditar su separación por documento.

## Para ejecutarlo

1. Abrir el notebook y conectar el servidor con la GPU requerida.
2. Ejecutar las secciones en orden y autorizar Drive cuando se solicite.
3. Si solicita reiniciar el intérprete por versiones ya cargadas, reiniciar y
   volver a ejecutar desde el principio. No lanzar dos ejecuciones en paralelo.
4. Si se pierde la sesión, recuperar con el mismo ID. Los ensayos completos se
   verifican y reutilizan; los incompletos recuperan su checkpoint válido.
5. Guardar el notebook al terminar. Conservar después una copia ejecutada en el
   histórico, con sus conclusiones; no regenerar ni sobrescribir las anteriores.

ID: `g15_scibert_base_regularizacion_01`. Resultados:
`MAIA_TESIS/a4/g15_scibert_base_regularizacion_01/`.
Experimento MLflow: `G15_SciBERT_Base_Regularizacion`.
Los snapshots se guardan en la subcarpeta `_tracking/snapshots/` del estudio;
su raíz técnica es `/opt/maia/a4_tracking_experiments/g15_scibert_base_regularizacion_01`.
Mantener una sola sesión escritora para este ID.

Archivos principales: `trial_plan.csv`, `study_manifest.json`,
`trial_results.csv`, `regularization_results.csv`, `condition_summary.csv`,
`curvas_regularizacion.png`, `selected_models.json`, `conclusiones.md` y
`STUDY_COMPLETE.json`. Cada ensayo conserva `training_log.json`, metadatos,
exportación, predicciones y matriz de confusión de validación.

Referencias: [comparación anterior](Comparacion_Reparto_vs_Pesos.md),
[estudio fuente en Drive](https://drive.google.com/drive/folders/1UvtcwLFYgN48_atCVkB5XECjW24dvXu6),
[métricas finales históricas](../M%C3%A9tricas.md) y
[guía universitaria A4, pp. 7–8](https://github.com/germarodr/Proyecto_Grado_MAIA/blob/58f0bb8/Papers/Propuesta_Proyecto%20PLN.pdf).
La hipótesis no cambia las dos entradas de la propuesta; esta prueba examina
únicamente la regularización de la entrada base.
