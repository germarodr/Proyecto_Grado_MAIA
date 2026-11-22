# Resumen — Pool A2 y selección de jueces

Fuentes: `A2 Pool Results and A3 Plan.pptx`, `A2 — Prompt v11.1 and the frozen judges (1).pptx`,
`eval60 Results 101226 Meeting.pptx`, contrato rev2. Datos al 15 oct 2026.

## 1. Jueces congelados (producción)
Tres modelos de pesos abiertos, con revisión de Hub fijada:
- `Qwen/Qwen3.8-27B` (`1d4bf0f2ff`)
- `google/gemma-4-26B-A4B-it` (`4d7ae4984b`)
- `mistralai/Mistral-Small-3.2-24B-Instruct-2506` (`95a6d26c4b`)

Entorno: vLLM 0.29.0, transformers 5.16.1, torch 2.13.0; decodificación *greedy*, semilla 0, salida
JSON con esquema (`evidence`, `primary`, `secondary`). Prompt **v11.1** congelado, con el contexto de
cita, el Top-3 de fragmentos y (opcional) título+abstract del citado.

**Corrida de producción:** 3 jueces, ~8 h 44 min en una sesión A100.
| Juez | Tiempo | Velocidad | Fallos JSON |
|---|---|---|---|
| Qwen3.8-27B | 4 h 40 | 1,8 inst/s | 0 |
| Gemma 4 26B-A4B | 1 h 14 | 8,0 inst/s | 23 |
| Mistral Small 3.2 24B | 2 h 49 | 2,9 inst/s | 7 |

Solo 30 de 85.659 respuestas fallaron (no votan); ninguna entrada superó el límite de tokens.

## 2. Resultado del pool
- **29.363 instancias** en el pool (tras excluir las 90 de eval60+calib30).
- **28.212 de alta confianza** (96%): ≥2 de 3 jueces coinciden. **1.145 empates** sin pre-etiqueta.
- **Reproducibilidad:** 294/300 misma pre-etiqueta al re-juzgar (98%).
- **Acuerdo entre jueces (re-judge):** Fleiss κ **0,67**; los tres coinciden en 63%.
  Pareja: Qwen–Gemma 0,76; Qwen–Mistral 0,61; Gemma–Mistral 0,63.
- **Fundamentación:** >99% de las citas de evidencia provienen del párrafo citante; 56 se abstuvieron.
- Archivos: `pool_v11.1/prelabels_pool.jsonl` (29.363), `high_confidence_pool.jsonl` (28.212),
  `pool_summary.json`, `counts.md`. **Solo identificadores, sin texto de unarXive.**

## 3. Cobertura por categoría (alta confianza, elegibles para test)
| Categoría | Instancias | ¿Alcanza 2.000? |
|---|---|---|
| Background | 11.671 | Sí (mayoritaria) |
| Comparison | 3.685 | Sí |
| Gap | 3.431 | Sí |
| Evidence | 3.287 | Sí |
| Application | 3.019 | Sí |
| Identification of the Originator | 1.377 | No (faltan 623) |
| Further Reading | 569 | No (faltan 1.431) |
| Improvement/Modification | 568 | No (faltan 1.432) |
| Basis | 502 | No (faltan 1.498) |

**5 de 9 categorías** llegan a la meta de 2.000; **4 quedan cortas**.

## 4. Por qué el muestreo aleatorio no basta
Tasa de aparición por clase en muestreo aleatorio (`pool_single_7000`): Basis 2,6%, Originator 1,2%,
Improvement/Mod. 1,4%, Further Reading 0,3% → requeriría decenas/cientos de miles de instancias
juzgadas (hasta "no viable" para Further Reading). Las frases *cue* funcionan (aciertos en su clase:
Improvement/Mod. 73%, Originator 67%, Further Reading 55%) pero **ya se agotaron** en el corpus piloto.

**Opciones acordadas:** (A) lote *cue* de Basis ahora ("following [x]", "we extend [x]"); (B) ampliar
el corpus a más subcategorías cs.* (contando primero si rinde); (C) *fallback*: cuotas documentadas
(el test toma ~15% del suministro real).

## 5. Selección de jueces y prompt v11.1
- **v11.1 = v8 + reglas de adjudicación** (R0, R-EV, R-GAP, R-IM, R-CMP, R-FR).
- **eval60:** el trío pasó de **43 → 48 de 60** aciertos (v8 → v11.1); v11.1 es la mejor versión para
  cada juez. Puntajes individuales v11.1: Qwen 50, Gemma 47, Mistral Small 41, Ministral 35.
- **Tercer juez:** se eligió **Mistral Small** sobre Ministral (nuevas etiquetas Gap 85% vs 60%
  correctas; como tercer juez, 48 vs 45 en eval60).
- En el pool, con v11.1 las etiquetas Gap se multiplican ~5× (23 → 109) sin degradar otras clases.
