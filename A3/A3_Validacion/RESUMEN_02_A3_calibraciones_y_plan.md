# Resumen — Calibraciones y plan de anotación A3

Fuentes: `eval60 Results 101226 Meeting.pptx`, `A3 calibration_ 30 citations.pptx`,
`calib2 Results and A3 Round 1.pptx`, contrato rev2, guía rev3.1.

## 1. Las tres calibraciones
| Calibración | Fecha | Instancias | Acuerdo | Setup |
|---|---|---|---|---|
| **eval60** | 9 oct | 60 | Cohen κ **0,63** entre equipos | Guía rev1.4; referencia para elegir jueces |
| **calib30** | 14 oct | 30 | Fleiss κ **0,47** (7 anotadores); 3/21 parejas ≥0,6 | Reglas rev1.1 recién escritas |
| **calib2** | 18 oct | 27 | Fleiss κ **0,87**; **16/16** parejas cruzadas ≥0,6 (mín. 0,71, media 0,87) | **Guía rev3.1**, trabajo individual, pre-etiqueta visible (como A3) |

**calib2 abrió el portón de A3:** todas las parejas G14–G15 superaron el umbral κ ≥ 0,6. Ritmo
mediano 1,7 min/paquete (rango 1,1–2,8).

## 2. eval60 en detalle
- 60 instancias etiquetadas por ambos equipos: **41 concordadas** (referencia) + **19 difíciles**
  (se resolvieron por regla en adjudicación).
- Los 19 casos difíciles caen en 5 fronteras: Evidence vs Background/Application/Basis (7),
  Further Reading vs Background/Evidence (4), Comparison vs ... , etc.
- El trío de jueces acertó 30/41 (el trío antiguo 7–8B: 13/41); 0/3 en Gap → motivó las reglas R-GAP.

## 3. calib2: dónde persiste el desacuerdo
Solo **16 de 216 respuestas** cambiaron la pre-etiqueta. Las correcciones se concentran en tres ítems
y tres fronteras conocidas:
- **K04** — Background vs Evidence (regla 10 / R-EV).
- **K23** — Basis vs Improvement/Modification vs Application (reglas 3 y 5).
- **K13** — Comparison vs Background (regla 4 / R-CMP).

Tasa de corrección por categoría: Background 21%, Basis 21%, Comparison 12%; el resto ≤4%; Gap,
Originator y Further Reading 0%.

## 4. Plan de anotación A3 — Ronda 1 (abierta 18 oct 2026)
- **Alcance ronda 1:** 6 categorías con suministro suficiente (las 5 cubiertas + Originator).
- **Dos test sets:** T_A (dueño G14) y T_B (dueño G15), disjuntos por instancia y por artículo citante.
- **Muestreo:** 360 por categoría y conjunto → **330 activas + 30 de reserva**; ≤2 por artículo
  citante, ≤1 por grupo de co-citas. Semilla `LCR-G14G15-A3-2026`; mitades por `sha256(seed+citing_id)`.
- **3.960 paquetes activos** (330 × 6 categorías × 2 conjuntos), en **72 lotes de 55**.
- **Carga por persona:** 18 lotes = 990 paquetes (9 de su conjunto como *validación* + 9 del otro
  como *segunda anotación*); ≈28 h al ritmo mediano.
- **Anotación en un paso:** pre-etiqueta visible, confirmar o corregir, en solitario; luego κ y
  adjudicación de desacuerdos → etiqueta *gold*.

### Olas de liberación
| Ola | Fecha | Contenido |
|---|---|---|
| Wave 1 | ahora (18 oct) | 8 lotes (4 por conjunto), 440 paquetes |
| Wave 2 | 19 oct | 64 lotes, 3.520 paquetes |
| Wave R | tras revisar wave 1 | Reserva liberada solo si la tasa de corrección >10% por conjunto y categoría (0–720 paquetes) |
| Ronda 2 | tras ampliar el pool | Basis, Improvement/Modification, Further Reading (por cuota) |

## 5. Entregables A3
`test_set_gold.jsonl` (etiqueta gold, ambas anotaciones, adjudicación, pre-etiqueta),
`exclusion_list.jsonl` (artículos citantes del propio test set, por grupo),
`iaa_report.md` (κ, α, tasa de corrección, conteo de *unclear*). Todo con identificadores y
etiquetas, sin texto de unarXive.
