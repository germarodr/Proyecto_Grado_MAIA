# Iteración 2: revisión de salidas y conclusiones

Revisión del 11 de noviembre de 2026 (America/Bogota), sobre `g15_scibert_final_v2_top1_02`. La revisión conserva las salidas originales de entrenamiento y actualiza la validación del cierre y sus conclusiones.

El [notebook revisado](SciBERT_Entrenamiento_Final.ipynb) contiene el cierre en [tres párrafos](conclusiones.md). Top-1 tuvo F1 macro medio 0.8304 frente a 0.8261 de Top-3 y lo superó en dos de tres semillas, con mayor variación.

La [verificación de salidas](validation_review.json) coteja los seis archivos de predicciones, con 1.653 citas cada uno, sus métricas, las etiquetas, el aislamiento documental, el paquete principal y el historial de MLflow. Los modelos y archivos completos están en `MAIA_TESIS/a4/g15_scibert_final_v2_top1_02/`. El snapshot de cierre revisado es `20261112T001120318089Z_0f8d76df` (hora UTC).
