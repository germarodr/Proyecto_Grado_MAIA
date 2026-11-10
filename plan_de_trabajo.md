# Plan de Trabajo
### Recuperación semántica y clasificación de la función de citas académicas en Computer Science

> **Equipo:** Grupo 15 (conjunto de prueba **T_B**). A1–A3 se hicieron con el Grupo 14; desde A4 trabajamos solos.
>
> **Quedan 2 semanas:** del 9 al 27-nov-2026.
>
> **Entregas finales (Coursera, 11:55 p. m. hora Colombia):**
>
> | Entrega | Fecha límite | Peso |
> |---|---|---|
> | Informe final | 23-nov | 55% |
> | Despliegue de la aplicación | 26-nov | 15% |
> | Sustentación | 27-nov | 15% |

## 1. Qué tenemos que entregar

| Entrega | Mínimo que debe contener | Responsable |
|---|---|---|
| **Informe final** (23-nov) | Artículo científico en formato IEEE (`Informes/Informe Final/Plantilla_Articulo.docx`): título, autores, resumen de 200–300 palabras con 3–5 palabras clave, introducción, estado del arte, metodología (datos, ciclo de ML, arquitectura y despliegue), resultados (métricas y matrices de confusión), discusión, conclusiones y trabajo futuro, referencias y enlaces a los repositorios | GR (borrador); cada uno escribe su parte |
| **Despliegue** (26-nov) | Aplicación web en AWS: ingresar un contexto de cita → ver el Top-3 con su sección → elegir clasificador (SciBERT, open-weight, API comercial) → ver la función predicha y su confianza | CB (backend), ST (frontend) |
| **Sustentación** (27-nov) | Presentación con demo en vivo | Todos |

## 2. Punto de partida (9-nov)

- **Hecho:** A0–A3 completos al 9-nov, con todos sus artefactos (gold de T_B, métricas de anotación, lista de exclusión y artefactos del G14). Partición V0 lista (28.039 train / 3.226 val). Notebook de A4 con MLflow listo para Colab A100.
- **Por confirmar:** SciBERT base v0 entrenado.

## 3. Alcance congelado

**Lo que sí hacemos (mínimo para entregar):**

1. SciBERT en 2 configuraciones: **base** (contexto + título + abstract) y **con fragmentos** (contexto + sección + Top-3), evaluado en T_B.
2. Un LLM comercial, **zero-shot y few-shot**, con contexto + título + abstract y puntaje 0–1 por clase.
3. Precision, Recall y F1 macro/micro; matrices de confusión; tabla comparativa de los modelos.
4. Costo y latencia por modelo; tasa de errores de formato del LLM.
5. Aplicación desplegada con los 3 clasificadores.
6. Informe y sustentación.

**Solo si sobra tiempo (después del 19-nov):** prompts específicos por categoría vs. genérico; P@3 manual del retrieval en una muestra pequeña; F1 por citados vistos/no vistos; más semillas.

**Fuera de alcance:** SPECTER, multietiqueta, variantes V1/V2, nuevas rondas de anotación.

## 4. Tareas por persona

| Responsable | Entregable | Fecha | Estado |
|---|---|---|---|
| **ST** (A4) | SciBERT base v0 a CB: pesos + contrato de entrada/salida | 11-nov | Pendiente |
| | SciBERT base final + predicciones sobre T_B | 12-nov | Pendiente |
| | SciBERT con fragmentos final + predicciones sobre T_B | 13-nov | Pendiente |
| **ST** (frontend) | Versión 1 conectada al backend | 14-nov | Pendiente |
| | Versión final con visualización de resultados | 20-nov | Pendiente |
| **JA** (A5) | Modelo comercial elegido + prompts zero-/few-shot | 10-nov | Pendiente |
| | Predicciones sobre T_B (zero y few-shot) con tokens, costo y latencia por llamada | 13-nov | Pendiente |
| **CB** (backend) | Modelo open-weight elegido; API con Top-3 + SciBERT v0 | 13-nov | Pendiente |
| | API con los 3 clasificadores | 18-nov | Pendiente |
| **CB + ST** | Aplicación desplegada en AWS (URL pública) | 21-nov | Pendiente |
| **GR** (A6, A7, informe) | Script de métricas probado sobre validación + esqueleto del informe en la plantilla | 12-nov | Pendiente |
| | Resultados finales (A6 + A7): tabla P/R/F1 macro-micro de los 4 modelos, F1 por clase, matrices de confusión, base vs. con fragmentos, costos, latencia y errores de formato del LLM | 16-nov (festivo) | Pendiente |
| | Borrador completo del informe (único editor; integra insumos y sugerencias) | 21-nov | Pendiente |
| **Todos** | Insumos para el informe según la tabla "Qué entrega cada uno" de `Informes/Informe Final/Borrador_v0_Informe_Final.md` | 13–21-nov | Pendiente |
| | Comentarios sobre el PDF del informe: v1 (19-nov) y final (22-nov) | 22-nov | Pendiente |
| | Diapositivas y ensayo de la sustentación con demo | 25-nov | Pendiente |

**Formato común de predicciones** (ST y JA entregan a GR un CSV por modelo y configuración): `inst_key`, `pred_label`, un `score_<clase>` por cada una de las 9 clases, `latency_ms`.

## 5. Puntos de control

| Fecha | Debe estar listo |
|---|---|
| Vie 13-nov | **A4 y A5 terminados:** todas las predicciones sobre T_B entregadas; API con SciBERT v0 |
| Lun 16-nov (festivo) | Resultados finales (A6 + A7) |
| Mié 18-nov | API con los 3 clasificadores |
| Sáb 21-nov | Aplicación desplegada + borrador del informe |
| **Lun 23-nov** | **Entrega del informe** |
| **Jue 26-nov** | **Entrega del despliegue** |
| **Vie 27-nov** | **Sustentación** |

Regla: si una tarea se atrasa más de un día, se avisa al grupo y se recorta de lo opcional, nunca del mínimo.

## 6. Decisiones vigentes

- 9 clases, etiqueta única.
- Aislamiento V0; train/val separado por citante; test = gold de T_B.
- Éxito: F1 macro de la configuración con fragmentos frente a la base.
- El LLM comercial recibe contexto + título + abstract, como pide el enunciado.
- El modelo open-weight (1–8B) solo se usa en la demo.

## 7. Limitaciones a declarar en el informe

- Las clases escasas quedan por debajo de los 2.000 ejemplos que pide el enunciado.
- T_B se tomó solo de pre-etiquetas de alta confianza (≥2 votos), lo que puede inflar el F1.
- Los anotadores veían la pre-etiqueta del modelo, lo que puede inflar el acuerdo (κ).
