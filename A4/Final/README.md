# SciBERT · Segunda iteración: Top-1 frente a Top-3

Las pruebas actuales están en [Experimentos](Experimentos/README.md):
[reparto de tokens](Experimentos/SciBERT_Reparto_Tokens.ipynb) e
[importancia de las clases](Experimentos/SciBERT_Pesos_Clases.ipynb).
Ambas conservan las dos entradas de la propuesta, base y Top-3, con hasta
12 épocas y paciencia 3. Tienen resultados e historiales separados.

[SciBERT_Entrenamiento_Final.ipynb](SciBERT_Entrenamiento_Final.ipynb) conserva
la segunda iteración ejecutada, con su portada, análisis gráfico de los datos
y nueve secciones con explicación y código.

Las dos corridas ejecutadas quedaron en el [histórico](Historico/README.md),
con sus salidas y sus conclusiones en tres párrafos. El archivo principal conserva
la segunda corrida como evidencia; el histórico permite consultar el avance.

La tabla [Modelos, entradas y salidas](Modelos_Entradas_Salidas.md) explica qué
textos recibe cada variante, cómo se convierten a números y qué devuelve la interfaz,
con las fuentes de la propuesta, la guía y el código.

## Revisión de salidas y conclusiones

La [copia revisada de la segunda corrida](Historico/Iteracion_02_2026-11-11_Revisada/README.md)
conserva las salidas de entrenamiento y añade una [verificación reproducible](Historico/Iteracion_02_2026-11-11_Revisada/validation_review.json)
de los seis archivos de predicciones, la referencia, el aislamiento de documentos,
el paquete principal y el cierre de MLflow. Las métricas recalculadas coinciden con las guardadas.

Top-1 obtuvo F1 macro medio **0.8304 ± 0.0063** y Top-3, **0.8261 ± 0.0016**.
La ventaja media fue de 0,44 puntos porcentuales y apareció en dos de tres semillas;
Top-1 mostró mayor variación. Conservó el 33,77 % de la evidencia original frente
al 59,32 % de Top-3. En Improvement/Modification recuperó 13 de 19 citas, frente
a 12 de 19, con F1 0.7222 frente a 0.7059 y precisión 0.7647 frente a 0.8000.

Las conclusiones del notebook quedaron en tres párrafos. La validación contiene
125 etiquetas humanas y 1.528 automáticas; el test propio continúa separado.

## Qué probamos ahora

En la primera iteración, base obtuvo F1 macro 0.8306 y Top-3, 0.8254. Top-3 recortó
texto en el 91,59 % de la validación. Esta observación motiva probar un fragmento;
las nuevas mediciones permitirán comprobar si cambia el desempeño.

Comparamos Top-1 con Top-3 en las mismas 1.653 citas de validación y mantenemos:

- Los 11.616 ejemplos de entrenamiento, las etiquetas y la separación por documento.
- Ritmo de aprendizaje `3e-5`, regularización `0.01`, máximo ocho épocas y parada tras dos sin mejorar.
- Semillas `42`, `17` y `73`; la semilla `42` conserva el modelo principal.
- Límite de 512 tokens, 192 para el contexto y la misma preparación de la cita objetivo.
- Medición final en FP32 y verificación de la exportación sobre toda la validación.

Se realizaron **tres entrenamientos nuevos Top-1** y se reutilizaron los **tres Top-3
verificados** de la primera corrida. Sus parámetros coinciden. Esta iteración no
vuelve a buscar hiperparámetros ni elige el modelo por la mejor semilla.

Top-1 significa el **primer fragmento del orden publicado en A2**, con su sección.
Además del recorte del fragmento elegido, se cuenta el texto de los otros dos
fragmentos omitidos y la fracción de los tres originales que recibe cada modelo.
Así, una reducción del recorte no se confunde con conservar más evidencia.

## Datos y referencia

Usamos training v2 de G15 y el cierre humano de A3 según el
[contrato, §§10 y 12](https://drive.google.com/file/d/1X7JXN5ZvoYJodhRxdT5Y-8wOaDlXwRXi/view)
y el [README de A3, §§3 y 4](https://drive.google.com/file/d/1m55jsSkHlb-MlCTJKgy36X4EIK8x23GN/view).
Las etiquetas humanas permitidas se incorporan por identificador. El test propio
permanece separado del entrenamiento y de esta comparación.

```text
MAIA_PROYECTO/a2/batches_norw/
MAIA_PROYECTO/a3/
MAIA_TESIS/TrainingData_Grupo15_v2/
MAIA_TESIS/TrainingData_Grupo15/
MAIA_TESIS/a4/g15_scibert_final_v2_grid_01/    ← referencia Top-3
```

La sección 5 verifica los archivos, los tres modelos Top-3, sus auditorías, las
particiones, las etiquetas, el código de preparación y los parámetros. Una
referencia ausente o modificada detiene la ejecución antes de entrenar Top-1.

## Cómo correrlo

1. Conectar el servidor y reiniciar el intérprete para comenzar esta versión.
2. Ejecutar las secciones **1 a 5**, en orden, y autorizar Drive cuando se solicite.
3. Revisar las gráficas de datos y la tabla de los tres resultados Top-3 recuperados.
4. Ejecutar la sección **6** una sola vez: entrena las tres semillas Top-1.
5. Ejecutar las secciones **7 a 9**: comparación, paquete y conclusiones con las cifras obtenidas.
6. Guardar el notebook con sus salidas al terminar y archivar esa copia antes de otra iteración.

La primera celda comprueba la aceleración requerida. Las bibliotecas y el modelo
base conservan sus versiones fijadas. El estudio nuevo se identifica como
`g15_scibert_final_v2_top1_02` y guarda sus resultados en
`MAIA_TESIS/a4/g15_scibert_final_v2_top1_02/`. MLflow continúa en `G15_SciBERT_Final`.

Si se pierde la conexión, comprobar primero si la ejecución anterior continúa
activa. Solo una sesión debe escribir el historial. Esta versión adquiere un
bloqueo local antes de abrir MLflow y lo libera al completar el cierre. La
recuperación se realiza con los mismos datos, ajustes y RUN_ID: se comprueban los
ensayos completos y los interrumpidos retoman su último checkpoint íntegro.

## Archivos de la segunda iteración

- `data_manifest.json`, particiones, distribución de clases y procedencia de etiquetas.
- `trial_plan.csv`, `study_manifest.json` y `reference_manifest.json`: plan y referencia fijados.
- `top1_results.csv` y `trials/<id>/`: tres entrenamientos, curvas, auditorías y modelos.
- `paired_seed_results.csv`: diferencia Top-1 menos Top-3 para cada semilla.
- `seed_stability.csv`: media y desviación de las dos entradas.
- `reading_comparison.csv`: recorte y evidencia conservada frente al texto original.
- `scibert_top1_final.zip` y `selected_models.json`: modelo principal y procedencia.
- `conclusiones.md` y `STUDY_COMPLETE.json`: cierre en tres párrafos y huellas de sus reportes.
- `validation_review.json`: revisión de predicciones y métricas, paquete, aislamiento e integridad del historial.

El notebook contiene el código necesario para ejecutarlo. Las herramientas
locales utilizadas para generarlo y verificarlo se excluyen de la entrega Git.
Las seis pruebas locales verificaron selección de texto, integridad de la
referencia, comparación por semilla, conclusiones y exportación con un BERT pequeño
aleatorio en CPU. Estas verificaciones no son resultados de calidad de SciBERT.

## Primera iteración

El [índice del histórico](Historico/README.md) enlaza el notebook ejecutado, sus
conclusiones, las métricas y el manifiesto de archivos de la primera corrida.
El respaldo de MLflow que incluye su cierre documentado es
`20261111T221940871690Z_de61cc40`.

La [segunda corrida ejecutada](Historico/Iteracion_02_2026-11-11/README.md) conserva
la comparación Top-1 frente a Top-3. Su respaldo de cierre es
`20261111T233716289682Z_dbbb5577`.

La revisión de sus salidas y conclusiones quedó respaldada en
`20261112T001120318089Z_0f8d76df` (identificador en hora UTC).
