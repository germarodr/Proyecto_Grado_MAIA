# Prueba adicional: un fragmento frente a tres

**RUN_ID:** `g15_a4_v0_seed42_top1_01`.
**Configuración:** `fragmentos_top1`.
**Notebook:** [A4_SciBERT_G15_Top1_Colab_A100.ipynb](A4_SciBERT_G15_Top1_Colab_A100.ipynb).
**Copia de ejecución:** [corrida4_VSCode](pruebascolab/A4_SciBERT_G15_Top1_corrida4_VSCode.ipynb).

Se usa únicamente el primer elemento del Top-3 suministrado por A1, sin reordenar
ni repetir la recuperación. Se conservan V0, semilla 42, datos, split, revisión
exacta de SciBERT, ventana de contexto de 192 tokens, límite de 512, learning rate
2e-5, batch 16 con acumulación 2 y cuatro épocas máximas. La selección sigue usando
F1 macro de validación, con paciencia dos y sin pesos por clase.

La prueba cambia la selección de fragmentos y el presupuesto que recibe cada
pasaje. No identifica por separado el efecto de esas dos modificaciones.
Se permite un solo entrenamiento adicional. El test humano T_B permanece cerrado.

## Controles y trazabilidad

- Un RUN_ID nuevo conserva las corridas anteriores.
- Se compara el manifiesto con el original antes de entrenar: datos, particiones
  e hiperparámetros deben coincidir. El entorno se registra de nuevo.
- El encoder exportado conserva la política Top-1 en su código de inferencia.
- MLflow mantiene un padre para Top-1, hijos por intento y evaluaciones nuevas.
- La comparación final usa las referencias FP32 de
  `g15_a4_v0_seed42_mlflow_01/evaluations/v2_fp32_37dc6f909cde/`.
- Tres pruebas locales verifican los argumentos de entrenamiento, que modificar
  los fragmentos 2/3 no cambia la entrada Top-1 y que el paquete manual es ciego,
  reproducible y contiene 20 casos. Ejecutar: `python A4/verificar_top1.py`.

## Auditoría inicial de entradas

| Validación | Top-3 | Top-1 |
|---|---:|---:|
| Tokens medios por ejemplo | 504,01 | 366,53 |
| Ejemplos con algún recorte de evidencia | 90,92 % | 10,26 % |
| Ejemplos con recorte de contexto | 35,71 % | 35,71 % |

El porcentaje indica ejemplos que sufren algún recorte, no la fracción del texto
eliminada. Menos recorte no garantiza un mayor F1.

## Revisión manual en paralelo

Se generó el paquete de 20 casos en Drive:

```text
MAIA_TESIS/a4/revision_manual/evidence_im_b43d4f0f25/
```

Las instrucciones están en [REVISION_MANUAL_EVIDENCE_IM.md](REVISION_MANUAL_EVIDENCE_IM.md).
Se trata de diagnóstico de validación, sin modificar etiquetas de entrenamiento,
sin medir accuracy poblacional con la muestra dirigida y sin producir gold final.

## Lectura del resultado

La ejecución del 4 de noviembre de 2026 terminó: 18 celdas de código ejecutadas,
sin errores, con el notebook guardado. Comparación sobre las mismas 3.226
instancias de validación, todas con preetiquetas A2, usando FP32:

| Configuración | F1 macro | Accuracy | F1 Evidence | F1 Improvement/Modification |
|---|---:|---:|---:|---:|
| Base: título y abstract | 0,847831 | 0,866088 | 0,797364 | 0,725490 |
| Top-3 | 0,839801 | 0,858648 | 0,747541 | 0,711538 |
| Top-1 | 0,844525 | 0,862678 | 0,782609 | 0,723810 |

Top-1 mejora frente a Top-3 **0,4724 puntos porcentuales de F1 macro**, pero queda
**0,3306 puntos por debajo del base**. También recupera parte de la diferencia
en las dos categorías objetivo. El base sigue siendo la referencia preferida
según esta validación; reducir los fragmentos no ha demostrado superarlo.

Se seleccionó el checkpoint de la época 4 (`checkpoint-3508`). El entrenamiento
tardó 880,42 segundos y registró un pico de 9,27 GiB de memoria GPU asignada.
La auditoría `passed_full_validation` verificó probabilidades y etiquetas idénticas
entre checkpoint y exportación FP32 en las 3.226 instancias. La repetición BF16
reproduce el F1 del Trainer (0,844791); hay cuatro cambios de etiqueta frente a
FP32, por lo que la comparación anterior utiliza exclusivamente FP32.

El resultado corresponde a una sola semilla y no demuestra por sí solo estabilidad
o significancia. No se amplía el entrenamiento ni se cambia la política después
de consultar el test humano.

## Dónde quedó guardado

Rutas relativas a `MAIA_TESIS/a4/` en Drive:

```text
g15_a4_v0_seed42_top1_01/
  fragmentos_top1/model/
  scibert_g15_fragmentos_top1.zip
  evaluations/v2_fp32_431ab1619b25/
    validation_comparison_with_baseline.csv
    fragmentos_top1/export_precision_audit.json
    fragmentos_top1/validation_per_class.csv
_tracking/snapshots/20261104T171939960505Z_7b389a29/
```

El último snapshot contiene el historial acumulado de MLflow. Para verlo en EC2,
restaura ese snapshot completo con la guía de instalación; no es necesario copiar
los snapshots intermedios. `RUN_TEST=False` y `GOLD_FINAL=False`: esta ejecución
no constituye la evaluación humana final.

El siguiente paso es completar la revisión manual de los 20 casos antes de decidir
nuevos ajustes. La GPU ya no se necesita para llenar esa hoja.
