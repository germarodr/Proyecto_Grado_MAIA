# Cómo funciona el notebook de A5

El archivo principal es [A5_Modelo_Comercial_G15.ipynb](A5_Modelo_Comercial_G15.ipynb). Está dividido en 14 bloques y cada bloque tiene una descripción antes del código. Su propósito es preparar, ejecutar y evaluar las comparaciones de A5; no entrena un modelo comercial.

La estrategia completa está en [Desarrollo_A5.md](Desarrollo_A5.md). Esta primera implementación deja listo el recorrido en modo demostración y el adaptador de API. La ejecución real permanece pendiente de los datos, del modelo seleccionado y de su presupuesto.

## 1. Archivos y requisitos

| Archivo | Función |
|---|---|
| `A5_Modelo_Comercial_G15.ipynb` | Configuración y ejecución por bloques |
| `a5_runtime.py` | Validación, prompts, API, registros, reanudación y métricas |
| `prompt_v11_1_snapshot.json` | Copia identificada de las instrucciones v11.1 y adaptación explícita de A5 |
| `crear_notebook.py` | Regenera el notebook, sin ejecutarlo ni llamar a una API |
| `tests/test_a5_runtime.py` | Pruebas locales del flujo y de los controles, sin consumo comercial |
| `.gitignore` | Mantiene datos, resultados y archivos de credenciales fuera de Git |

El flujo usa Python 3.10 o superior y su biblioteca estándar. No necesita GPU, SciBERT instalado, un SDK comercial ni dependencias para calcular las métricas. Los resultados se guardan como JSON y CSV; las matrices pueden abrirse en Excel o visualizarse posteriormente.

En VS Code selecciona un kernel de Python y abre el notebook. En Colab, abrir el notebook desde GitHub **no descarga sus auxiliares**: copia al menos el notebook, `a5_runtime.py` y `prompt_v11_1_snapshot.json` a una misma carpeta de Drive, o sube los dos auxiliares a la sesión. Configura `A5_DIR` en el bloque 2. Si usas Drive, activa `USE_DRIVE` en el bloque 1.

## 2. Primera ejecución sin datos finales ni token

Mantén `DEMO=True`, `ENABLE_API=False`, `SPLIT="dev"` y los demás valores iniciales. Ejecuta los bloques en orden. Se cargarán nueve casos inventados, nueve demostraciones inventadas y respuestas simuladas deliberadamente correctas.

Esto permite comprobar las ocho condiciones, el formato JSON, los registros y las matrices **sin pagar ni enviar textos a ningún proveedor**. Un F1 perfecto en ese modo solo confirma que el software une y cuenta los datos correctamente: no es desempeño de un modelo ni resultado sobre anotaciones humanas. Los artefactos están marcados como sintéticos.

No se incluyen datos privados ni etiquetas humanas reales en los archivos creados. La demostración tampoco implica que el dataset final ya esté disponible.

## 3. Qué hace cada bloque

| Bloque | Qué hace | Qué debes editar |
|---|---|---|
| 1. Python y Drive | Comprueba Python; monta Drive solo si se solicita | `USE_DRIVE` |
| 2. Carpeta A5 | Carga el módulo y el snapshot del prompt | `A5_DIR` |
| 3. Datos | Define rutas, versión de datos, aislamiento y estado del gold | `PATHS`, `DATASET_VERSION`, `VARIANT`, `GOLD_FINAL`, `PROTOCOL_FROZEN` |
| 4. API y costo | Define URL completa, identificador del modelo, parámetros y presupuesto | `API_ENDPOINT`, `MODEL_ID`, tarifas, reserva y límites |
| 5. Comparaciones | Selecciona entradas, instrucciones y ejemplos; construye `CFG` | Matriz experimental, límite de piloto y estabilidad |
| 6. Auditoría | Carga y valida datos, ejemplos y separación de T_B | No hay cambios rutinarios |
| 7. Vista previa | Muestra parte del prompt y cuenta solicitudes/reservas | Revisar antes de habilitar una ejecución pagada |
| 8. Credencial | Lee una variable de entorno o solicita el token oculto | Token en el campo oculto, nunca en el código |
| 9. Ejecución | Prepara archivos, simula o llama a la API según el modo | Mantener el mismo `RUN_ID` solo para una reanudación idéntica |
| 10. Gold | Lee etiquetas humanas por clave después de inferir | Ruta al gold consolidado |
| 11. Métricas | Calcula macro/micro, cobertura y matrices | Número de réplicas bootstrap |
| 12. Estabilidad y errores | Resume repeticiones, modelos devueltos y diario de intentos | Revisar costos desconocidos y respuestas inválidas |
| 13. SciBERT | Compara sobre exactamente los mismos IDs del test | CSV final de A4, entrada y referencia del run |
| 14. Cierre | Limpia la referencia al token y muestra el estado | No hay cambios rutinarios |

Los cambios en variables de los bloques 3–5 requieren volver a ejecutar el bloque 5 para reconstruir `CFG`, y después los bloques 6 en adelante. Si cambias el modelo, el prompt, los datos o los parámetros de una ejecución ya guardada, usa un `RUN_ID` nuevo.

## 4. Dónde van la URL del modelo y el token

En el bloque 4 hay dos datos distintos:

- `API_ENDPOINT`: URL HTTPS completa del servicio de inferencia. No es la página de descripción del modelo. El ejemplo es un marcador y no funciona hasta reemplazarlo.
- `MODEL_ID`: nombre exacto del modelo o snapshot aceptado por ese servicio.

El token se introduce en el **bloque 8**, mediante `getpass`, que oculta lo escrito. También puede configurarse fuera del notebook en una variable de entorno llamada `A5_API_KEY`. `API_KEY_ENV` contiene solo el nombre de esa variable.

No pegues la clave en `MODEL_ID`, `EXTRA_BODY`, `CFG`, una URL, una celda ni un archivo versionado. El módulo no guarda las cabeceras de autenticación y oculta la clave si el servidor la devuelve literalmente en su respuesta.

El adaptador implementado usa el formato no streaming de **Chat Completions**: envía `model` y `messages`, y lee `choices[0].message.content` y `usage`. Su referencia es la [documentación oficial de Chat Completions](https://developers.openai.com/api/reference/resources/chat/subresources/completions/methods/create). Esto no convierte automáticamente cualquier API comercial en compatible: una API nativa diferente requiere adaptar `http_call`, `payload_for` y `unpack_response` antes del piloto.

`TEMPERATURE=None` evita enviar un parámetro que algunos modelos no aceptan. `OUTPUT_TOKEN_PARAMETER` permite seleccionar `max_completion_tokens` o `max_tokens`; `RESPONSE_FORMAT` permite omitir el campo, usar JSON o un esquema estricto según lo admita el proveedor. Se comprobará el soporte con el modelo elegido; no se ha verificado todavía con una cuenta real.

## 5. Formato de los datos

Los archivos son **JSONL UTF-8**: un objeto JSON completo por línea. No es posible pasar directamente una hoja de votos ni los archivos de A4 que solo contienen identificadores. Se deben unir con los textos y consolidar el gold mediante la clave canónica `inst_key`, conservando el mapeo de paquete cuando proceda.

El notebook no interpreta automáticamente qué voto de una hoja es final ni transforma un voto individual en adjudicación. Ese paso corresponde al cierre de A3.

### 5.1 Casos de desarrollo o de test

Cada caso debe tener esta estructura. El ejemplo ilustra el esquema y no es un caso científico real:

```json
{
  "inst_key": "CLAVE_CANONICA_REAL",
  "citing_id": "ID_ARTICULO_CITANTE",
  "cited_id": "ID_ARTICULO_CITADO",
  "split": "dev",
  "context": "We use the method of [[TARGET]] in our experiments.",
  "target_sentence": "We use the method of [[TARGET]] in our experiments.",
  "cited_title": "Título real del artículo citado",
  "cited_abstract": "Abstract real del artículo citado",
  "top3": [
    {"section": "Methods", "text": "Texto real del primer fragmento"},
    {"section": "Results", "text": "Texto real del segundo fragmento"},
    {"section": "Introduction", "text": "Texto real del tercer fragmento"}
  ]
}
```

En JSONL este objeto se escribe en una sola línea. Usa `split="test"` para el test final. Contexto y oración deben contener exactamente un `[[TARGET]]`, y la oración debe aparecer literalmente dentro del contexto. Se conservará el orden del Top-3. Una sección vacía se muestra como `Unknown`; no se inventa una sección retórica.

Los campos de preetiquetas, votos, notas o gold que pudiera contener la fuente no se pasan a los mensajes del caso: el módulo selecciona únicamente los campos admitidos. Es preferible exportar los casos sin esos campos.

### 5.2 Entradas equivalentes a A4

Para un piloto se pueden usar los textos completos del formato anterior. Eso no demuestra igualdad con la entrada truncada de SciBERT. El test final exige `ALIGNED_INPUTS=True` y una exportación `a4_inputs` en cada caso y en cada ejemplo few-shot:

```json
"a4_inputs": {
  "base": {
    "context": "Contexto visible tras aplicar la política de A4, con [[TARGET]].",
    "target_sentence": "Oración del contexto visible con [[TARGET]].",
    "evidence": "Título y abstract visibles para SciBERT base."
  },
  "fragmentos": {
    "context": "Contexto visible tras aplicar la política de A4, con [[TARGET]].",
    "target_sentence": "Oración del contexto visible con [[TARGET]].",
    "evidence": "Secciones y fragmentos visibles para SciBERT con fragmentos."
  }
}
```

La oración de cada entrada debe existir tanto en el contexto preparado como en el original. Los textos de este ejemplo son marcadores: no cumplen esa relación hasta reemplazarlos por la exportación real.

La exportación debe proceder del preparador de entradas de A4, no de una reconstrucción manual que afirme cumplir sus límites. Registra `INPUT_POLICY_VERSION` y conserva su manifiesto. El notebook comprueba presencia/estructura y guarda hashes; no puede certificar por sí solo que una exportación declarada provenga realmente de A4. La creación de ese exportador depende del paquete final y queda como punto de integración.

### 5.3 Gold humano

Cada línea de `dev_gold.jsonl`, `test_gold.jsonl` o `fewshot_gold.jsonl` tiene:

```json
{"inst_key":"CLAVE_CANONICA_REAL","gold_primary":"Application","label_source":"human_gold","adjudicated":true}
```

Solo se aceptan las nueve categorías del proyecto. No se aceptan `unclear`, etiquetas nulas, casos excluidos ni registros sin adjudicar. Para el test, los IDs deben coincidir exactamente con los casos finales. El gold de desarrollo puede contener más casos que el piloto; se seleccionan por clave los evaluados.

### 5.4 IDs reservados de T_B

`tb_reserved_ids.jsonl` enumera todos los casos reservados, incluidas reservas y colchón, con artículos citante y citado:

```json
{"inst_key":"CLAVE_RESERVADA","citing_id":"ID_CITANTE","cited_id":"ID_CITADO"}
```

Estos IDs se usan incluso durante el piloto para evitar que los ejemplos o el desarrollo invadan T_B. El conjunto final es un subconjunto adjudicado de esa reserva, no todos los IDs automáticamente.

### 5.5 Exclusiones

`exclusion_list.jsonl` acepta registros con `inst_key`, con `citing_id` o con ambos:

```json
{"inst_key":"CLAVE_EXCLUIDA"}
{"citing_id":"ARTICULO_CITANTE_EXCLUIDO"}
```

Un archivo vacío representa una lista explícitamente vacía. Antes de usarlo así se debe confirmar el contrato: no se asume que las calibraciones u otras exclusiones han desaparecido.

### 5.6 Banco few-shot

`fewshot_cases.jsonl` usa el formato de casos con `split="dev"`. `fewshot_gold.jsonl` contiene sus etiquetas humanas. Esta implementación requiere exactamente nueve ejemplos, uno por categoría, y mantiene su orden fijo entre condiciones.

Los ejemplos no pueden ser casos del piloto evaluado ni compartir citantes con T_B. En V1 también se separan los citados; en V2 se separan ambos roles. La auditoría se basa en IDs: conserva las normalizaciones del contrato para que distintas versiones de un arXiv ID no oculten coincidencias. La separación de texto duplicado o paráfrasis requiere además revisión del banco antes de congelarlo.

Las respuestas de demostración few-shot codifican la etiqueta como un vector one-hot solo para mostrar el formato esperado. No representan una confianza humana del 100 %. Esta es una decisión explícita de A5, común a las condiciones few-shot; el banco se debe revisar en el piloto.

## 6. Cómo se usa el prompt v11.1

El snapshot conserva las instrucciones originales para trazabilidad y los SHA-256 de `a2_common.py` y `a2_prompt_v11.py`. La implementación no importa ni modifica esos archivos del otro repositorio al ejecutar el notebook.

El prompt genérico contiene las definiciones breves de las nueve funciones. El específico añade las aclaraciones y reglas de v11.1. Ambos mantienen la lectura prioritaria del target. La versión A5 se identifica como una adaptación: cambia la salida `evidence/primary/secondary` por `scores`, retira `unclear` como salida y usa la información del citado correspondiente a la condición.

Por tanto, **no se afirma que A5 envíe el prompt A2 byte por byte**. La diferencia genérico/específico, el esquema de puntuaciones y las demostraciones son el experimento nuevo. Antes del test se revisará su correspondencia con la guía rev3.1, especialmente si el gold final incorpora reglas posteriores al baseline.

## 7. Pasar de demostración a piloto y test

Para el piloto, cambia `DEMO=False`, configura archivos reales de desarrollo, IDs reservados y exclusiones; prepara el banco few-shot y empieza con 30–50 casos mediante `LIMIT_CASES`. Con `ENABLE_API=False` todavía puedes auditar y guardar mensajes sin llamadas pagadas.

Después define un modelo y un endpoint compatible, verifica sus parámetros y tarifas, fija una reserva por intento y el presupuesto. Usa un `RUN_ID` nuevo al activar `ENABLE_API=True` e ingresa la credencial oculta. El piloto detectará costos, formatos, límites de contexto y problemas de integración. No se fija aquí un modelo ni un precio inventado.

Para el test se requieren `SPLIT="test"`, `GOLD_FINAL=True`, `PROTOCOL_FROZEN=True`, `LIMIT_CASES=None`, `ALIGNED_INPUTS=True`, entradas exportadas de A4 y gold completo por clave. Se comprueba la meta de 300 por categoría. Si existe una desviación acordada, se debe explicar en `QUOTA_DEVIATION_REASON`; no se completará la cuota con preetiquetas.

Las ocho condiciones pueden costar 8 × N solicitudes. `STABILITY_CASES` añade dos repeticiones a los casos seleccionados, para un total de tres por condición. La submuestra se fija por semilla/orden antes de consultar resultados.

## 8. Costos, errores y reanudación

El diario `attempts.jsonl` registra un evento antes y después de cada intento. Reintenta solo fallos transitorios, como 429 o 5xx, hasta `MAX_RETRIES`. Un JSON inválido, una negativa o una respuesta truncada se conserva como fallo; no se insiste para conseguir una etiqueta válida.

La reserva local cobra al presupuesto como mínimo `RESERVE_PER_ATTEMPT_USD` por intento, incluso cuando el costo no se conoce. Si el costo estimado con tokens supera esa reserva, detiene las llamadas posteriores. Las tarifas se aplican sin descuento de caché y se conserva `usage` para contrastar con la factura. Los intentos con costo desconocido se muestran, no se presentan como gratuitos.

Este control **no garantiza el gasto máximo facturado**: una solicitud puede superar la reserva antes de que se conozca su consumo. Configura también el límite disponible en el proveedor y dimensiona la reserva con el piloto. El resumen del diario incluye reintentos y repeticiones; la columna de costo del último intento por predicción no es el costo total de la ejecución.

Para reanudar usa los mismos datos, configuración, código y `RUN_ID`. Los resultados terminales se reconstruyen del diario y no se vuelven a solicitar. Cambios incompatibles requieren un nombre nuevo. Si un proceso murió después de enviar y antes de registrar respuesta, el módulo bloquea el reenvío automático: comprueba en el proveedor qué ocurrió y decide un nuevo run después de resolver la incertidumbre.

`RUNNING.lock` evita dos escritores sobre la misma ejecución. Si quedó tras una caída, confirma que no hay otra sesión ejecutando ese run antes de retirarlo manualmente. No se quitan bloqueos automáticamente ni se mezclan diarios de sesiones concurrentes. La persistencia en Drive depende de su sincronización; la garantía local del diario no elimina los riesgos de una desconexión del montaje.

## 9. Artefactos y lectura de resultados

Cada run conserva:

- `manifest.json`: configuración pública, versiones y hashes; no contiene el token.
- `plan.json` y `requests.jsonl`: matriz, auditoría y mensajes exactos, sin soluciones del caso objetivo.
- `attempts.jsonl`: respuesta HTTP original y resultado de validación por intento.
- `predictions.json`: predicción, nueve puntuaciones, modelo devuelto, uso de tokens y tiempos.
- `run_summary.json`: estado, registros, fallos y costos/reservas agregados.
- `metrics.json` y `confusion_*.csv`: métricas generales, por clase y matrices.
- `stability.json`: coincidencia de etiquetas y variación de puntuaciones en repeticiones.
- `comparison_scibert_*.json`: comparación emparejada cuando se aporta un CSV final equivalente de A4.

Los mensajes guardados contienen texto del corpus. Conservarlos en el almacenamiento permitido es parte de la reproducibilidad; no implica autorización para publicarlos.

El F1 macro se promedia sobre las nueve funciones. Las respuestas inválidas cuentan como fallos, se muestran en una columna adicional de las matrices y no se eliminan del denominador. El micro incluye esa salida inválida y coincide con accuracy en etiqueta única. Se ofrecen también métricas sobre respuestas válidas, identificadas como complemento.

Las puntuaciones del modelo no están calibradas. Los empates se resuelven con el orden fijo de categorías y se registran. No se normalizan ni se reparan silenciosamente respuestas que incumplan el contrato. Las matrices y métricas descriptivas no sustituyen el análisis de errores ni la revisión de posibles sesgos.

El bootstrap agrupa por artículo citante; los intervalos describen la incertidumbre del conjunto evaluado. En el bloque 13, el intervalo de la diferencia LLM–SciBERT usa los mismos grupos remuestreados para ambos modelos. El CSV de A4 debe tener `inst_key` y `predicted_label`, corresponder al mismo gold y cubrir exactamente T_B. Se filtran las condiciones de entrada equivalente antes de comparar.

## 10. Verificación local sin API

Desde la carpeta A5:

```powershell
python -B -m unittest discover -s tests -v
```

Para regenerar el notebook sin ejecutarlo:

```powershell
python -B crear_notebook.py
```

Las pruebas usan un transporte simulado, directorios temporales y fixtures inventados. No necesitan token, no contactan un proveedor y no cambian los datos de anotación. Ejecutar una API real y confirmar su esquema, parámetros, tarifas y latencia sigue siendo una tarea del piloto.
