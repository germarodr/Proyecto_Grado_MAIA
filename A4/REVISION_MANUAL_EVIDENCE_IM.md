# Tu revisión manual mientras corre Top-1

La prueba adicional entrena un solo modelo con el primer fragmento recuperado,
conservando la partición V0 y los hiperparámetros. Nos interesa saber si usar un
pasaje más completo funciona mejor que repartir el presupuesto entre tres.

Tu tarea es revisar **20 citas de validación**, seleccionadas alrededor de Evidence
e Improvement/Modification. Se mezclan discrepancias de los modelos y controles.
No son 20 errores confirmados: las referencias actuales son preetiquetas de A2.

Es un diagnóstico de desarrollo, distinto de la anotación formal de A3: aquí se
ocultan las predicciones y preetiquetas en la primera lectura. Se conservan las
definiciones y reglas de la guía rev3.1. Esta revisión no genera gold final de T_B,
no cambia su protocolo y no se incorporará automáticamente al entrenamiento.

## Qué debes abrir

El notebook ya generó este paquete en tu Drive:

```text
MAIA_TESIS/a4/revision_manual/evidence_im_b43d4f0f25/
  revision_manual.xlsx          # archivo que llenas; si no está, usa el CSV
  revision_manual.csv
  casos_revision.html           # lectura cómoda de los 20 casos
  manifest.json
  _analisis/clave_modelos.csv   # conservar cerrado hasta terminar
```

1. Abre `revision_manual.xlsx` en Excel o súbelo/ábrelo con Google Sheets. Usa
   solo una versión como archivo de respuestas; no hace falta llenar también el CSV.
2. Para leer con comodidad, descarga `casos_revision.html` y ábrelo en el navegador.
   Cada caso tiene el mismo `review_id` que su fila de la hoja.
3. No abras `_analisis/clave_modelos.csv` hasta entregar tus decisiones.

## Qué hacer en cada fila

1. Lee primero la oración de **`[[TARGET]]`**. Usa otras oraciones del contexto
   únicamente si se refieren de vuelta a esa misma cita. `[CITE]` representa otra cita.
2. Decide para qué se usa esa referencia en el texto citante. El tema del párrafo
   o lo que el citado cuenta de sí mismo no determinan la función.
3. Consulta título/abstract y abre los fragmentos solo cuando ayuden a verificar
   qué trabajo es, qué método propone o qué afirmación respalda.
4. Llena estos campos:

| Campo | Qué escribir |
|---|---|
| `primary_label` | Una de las nueve categorías o `unclear`; no fuerces las dos categorías objetivo |
| `confidence` | `Alta`, `Media` o `Baja` |
| `supporting_quote` | Copia la frase corta del contexto citante que justifica tu decisión |
| `notes` | Una explicación breve y, si aplica, la regla usada; obligatoria con `unclear` |
| `chunks_needed` | `Si` si consultaste fragmentos para decidir/verificar; en otro caso `No` |
| `cited_text_quality` | `Suficiente` o `Insuficiente`; explica en notas si el material es irrelevante o solo un apéndice |

Conserva los `review_id` y las columnas de texto. Puedes decidir cualquiera de:
`Background`, `Gap`, `Basis`, `Comparison`, `Application`, `Improvement/Modification`,
`Evidence`, `Identification of the Originator`, `Further Reading`, `unclear`.

## Las dos preguntas clave

**Evidence:** ¿qué afirmación, decisión o resultado de los autores citantes respalda
la cita objetivo? Escribe esa afirmación en tu justificación.

- Describir lo que hizo otro trabajo suele ser Background.
- Usar directamente su método o dataset es Application.
- El trabajo que tiene una limitación puede ser Gap; la fuente que demuestra una
  limitación de otro método puede ser Evidence.
- «e.g.» o «for example» no bastan por sí solos para decidir Evidence.

**Improvement/Modification:** ¿el trabajo actual modifica, adapta o extiende un
método, herramienta o dato de **la cita objetivo**?

- Puede ser esta categoría aunque no se detalle el cambio.
- Si usa una modificación que ya propuso el propio citado, es Application.
- Si la cita solo inspira la idea, puede ser Basis.
- No cuentes un cambio aplicado a otro método del párrafo como cambio de `[[TARGET]]`.

Las reglas que mandan son R0, R-IM, R-EV y R-GAP de la
[guía rev3.1](../Folder_trabajo_Equipos_14_y_15/guia_anotacion_funcion_cita_rev3.1.md).

## Qué devolver

Guarda el XLSX o CSV con los 20 casos respondidos como `revision_manual_completada`
y déjalo en esta carpeta del repositorio:

```text
A4/revision_manual/respuestas/
```

También puedes guardarlo en la misma carpeta privada de Drive y comunicarme la ruta.
Con tus decisiones revisaremos las fronteras de categorías, la utilidad de los
fragmentos y posibles problemas de preetiquetado. El muestreo es dirigido: no se
usa para estimar una accuracy general ni reemplaza la evaluación humana final.
