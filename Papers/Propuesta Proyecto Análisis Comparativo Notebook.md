# Propuesta Proyecto — Análisis Comparativo Notebook

**Fecha:** 7 de noviembre de 2026. Comparación del [PDF de la universidad](<Propuesta_Proyecto PLN.pdf>), [nuestra propuesta](../PropuestaProyectoGrado.md) y los notebooks ejecutados de A4. No se modificaron propuestas, datos ni notebooks. Se excluyó `entrega1/`.

## Conclusión

**A4 está alineado**: SciBERT, nueve clases, entropía cruzada y comparación **contexto + título/abstract** frente a **contexto + sección/Top-3**. SPECTER es un ejemplo del PDF, no obliga a añadir otro encoder. Reducir compromisos en nuestra propuesta no elimina requisitos universitarios: las diferencias deben acordarse con el director.

## Diferencias y pendientes prioritarios

| Tema | Universidad / nuestra propuesta | Avance y recomendación |
|---|---|---|
| **Volumen y balance** | PDF pp. 2, 6–7: **≥2.000 por cada categoría**. Nuestro §5.3 permite mínimos menores. | G15 tiene 545 filas Improvement/Modification V0 o 174 V2 antes del split; no son el dataset final completo. Documentar conteos finales y acordar mínimos diferenciados. El PDF exige 2.000 por clase en el **dataset**, no necesariamente en train. |
| **Test humano** | PDF pp. 6–7: ≥15%, muestreo por categoría, dos evaluadores, Kappa/Alpha y reserva exclusiva. Nuestra propuesta lo recoge. | Usamos preetiquetas y `RUN_TEST=False`. Falta acreditar gold T_B, IAA y porcentaje real. **300/clase cubre el 15% de 18.000**, no de cualquier tamaño mayor. Los 20 casos diagnósticos no sustituyen A3. |
| **Aislamiento** | PDF pp. 6–7: estricto por documento. Nuestro §5.3 explicita citante; §5.1.1 menciona citante/citado. | Las corridas son **V0**. Recomiendo **V2**, que elimina solapamientos incluso con roles inversos. El PDF no nombra V2: es la interpretación conservadora. Que el contrato permita V0 no acredita aceptación universitaria de esa flexibilización. |
| **Prompts comerciales** | PDF p. 8: zero-shot/few-shot **y** genéricos/específicos por categoría. Nuestro F5 explicita solo el primer eje. | Añadir el segundo eje en A5: proponer un modelo API y cuatro configuraciones (2×2), misma información y nueve puntajes. Confirmar ese alcance sin sumar proveedores automáticamente. |
| **Evaluación y eficiencia** | PDF p. 8: Precision/Recall/F1 macro y micro, confusiones, costo, latencia y errores de formato. Nuestra propuesta los contempla. | Ya hay matrices, métricas, tiempos y MLflow; falta comparación humana/API. Explicitar Precision/Recall micro (aquí equivalen a accuracy/F1 micro). Medir latencia y costo comparables, no solo tiempo de entrenamiento. |
| **Demostrador** | PDF pp. 8–9: encoder, open-weight 1–8B y API; Top-3/sección y distribución visual de candidatos. | Las tres opciones ya están comprometidas en ambos documentos. Exportar modelos no acredita la aplicación integrada; añadir la visualización al checklist. |

## Qué ajustar antes de otra corrida

1. **Acordar dataset final y V2**. El notebook ya implementa sus exclusiones: usar otro `RUN_ID`, reconstruir particiones y entrenar **base y Top-3** desde SciBERT preentrenado, sin reutilizar pesos V0. El análisis previo estima 11.015 train y 1.539 val; recalcular si cambian datos/etiquetas.
2. Cerrar A3: porcentaje humano, adjudicación y exclusiones. T_B queda fuera de selección y ejemplos few-shot. El uso de T_A para entrenar está permitido por el contrato; documentar su acuerdo con el director frente a la reserva exclusiva del PDF.
3. Mantener **Top-1 como ablación adicional**, sin sustituir la comparación Top-3 exigida. En validación V0: base **0,8478**, Top-3 **0,8398**, Top-1 **0,8445** de F1 macro, contra preetiquetas. No son resultados finales humanos.

## Cómo acotar compromisos sin perder lo esencial

- Cambiar, previa revisión, «el éxito se define como una mejora consistente» (§7) por **«medir y analizar si Top-3 mejora F1 macro frente al base»**. No prometer un resultado favorable ni ocultar la diferencia observada.
- **P@3 manual con 150–200 contextos**, corte temporal y estratificación por sección son compromisos propios, no exigencias expresas del PDF. A4 usa hash por citante, sin corte temporal ni estratificación exacta. Precisar alcance o proponerlos como complementarios; no declararlos completados.
- Actualizar el apéndice de infraestructura a lo implementado: **Colab + MLflow/SQLite + Drive y EC2 para consulta**. DVC/S3/PostgreSQL no son requisitos del PDF ni hace falta introducirlos ahora.

**Prioridad:** resolver aislamiento y mínimos de datos, cerrar el test humano y completar A5–A7. Más modelos o nuevas ablaciones no solucionan esas brechas.

Fuentes de contraste: [contrato, §10](../Folder_trabajo_Equipos_14_y_15/Contrato_Datos_A3_2026-10-28_guia_rev3.1.md), [análisis de datos y particiones](../A4/analisis_y_plan_A4.md), [corrida base/Top-3](../A4/pruebascolab/A4_SciBERT_G15_Colab_A100_corrida3_VSCode.ipynb) y [resultados Top-1](../A4/README_TOP1.md).
