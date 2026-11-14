# Histórico de A4

Las copias ejecutadas conservan el notebook, sus salidas, la portada y las
conclusiones de cada corrida. Cada carpeta incluye un manifiesto de huellas para
comprobar que la evidencia guardada sigue intacta.

| Iteración | Estudio | Evidencia | Resultado de validación |
|---|---|---|---|
| 1 · 11 de noviembre de 2026 | `g15_scibert_final_v2_grid_01` | [Notebook y reportes](Iteracion_01_2026-11-11/README.md) | Base 0.8306; Top-3 0.8254. Doce combinaciones y cuatro repeticiones. |
| 2 · 11 de noviembre de 2026 | `g15_scibert_final_v2_top1_02` | [Notebook y reportes](Iteracion_02_2026-11-11/README.md) | Modelos principales de semilla 42: Top-1 0.8311; Top-3 0.8254. Tres entrenamientos nuevos y tres referencias. |
| 2 · revisión del cierre | Mismo estudio; conserva las salidas de entrenamiento | [Notebook revisado y verificación](Iteracion_02_2026-11-11_Revisada/README.md) | Seis archivos de predicciones cotejados. Conclusiones ampliadas: ventaja en dos de tres semillas, variación y precisión de la clase minoritaria. |

El [notebook de trabajo](../SciBERT_Entrenamiento_Final.ipynb) contiene la segunda
iteración ejecutada, Top-1 frente a Top-3, cuya copia ya está en este histórico.
Los modelos y los reportes completos permanecen en las
carpetas de cada estudio en `MAIA_TESIS/a4/` y en el historial de MLflow.
