# Muestra de datos de CiteScope

Esta carpeta contiene [ejemplos_citas.jsonl](ejemplos_citas.jsonl), una muestra de **40 citas con etiquetas humanas** utilizada por el demostrador. Cada línea es un objeto JSON con el contexto citante, información del artículo citado y sus tres fragmentos recuperados.

La muestra permite inspeccionar la estructura de las entradas y los datos que presenta la aplicación. **No es el corpus completo ni una partición de entrenamiento**: procede del test humano y no debe incorporarse al entrenamiento para evaluar después esos mismos casos.

## 1. Procedencia

El archivo es una copia sin modificaciones de [examples_TB_con_resumen.jsonl](../Demostrador/api/examples_TB_con_resumen.jsonl). La construcción de los ejemplos y la incorporación del resumen y los fragmentos se describen en la [documentación del conjunto del demostrador](../A3/Demostrador/README.md).

El corpus de origen es unarXive 2022, derivado de las fuentes de artículos de arXiv. Los registros conservan los identificadores del citante y del citado, sus títulos, enlaces y licencias. Las claves de las instancias permiten relacionarlos con los datos de recuperación y anotación del proyecto.

## 2. Estructura de los registros

| Campo | Descripción |
|---|---|
| `example_id` | Identificador del ejemplo de la aplicación, como `B-001`. |
| `inst_key` | Clave estable de la instancia de cita. |
| `citing_paper_id`, `cited_paper_id` | Identificadores de los artículos citante y citado. |
| `context` | Párrafo citante, con `[[TARGET]]` en la cita objetivo. |
| `citing_title`, `cited_title` | Títulos de ambos artículos. |
| `cited_abstract` | Resumen del artículo citado. |
| `top3` | Tres fragmentos con rango, texto, sección e identificador del fragmento. |
| `a2_top3` | Referencias de los fragmentos seleccionados en la recuperación previa. |
| `label` | Función de cita humana utilizada como referencia. |
| `label_source`, `status` | Procedencia y estado de la anotación. |
| `citing_url`, `cited_url` | Enlaces de los artículos en arXiv. |
| `citing_license`, `cited_license` | Condiciones de licencia de los textos de cada artículo. |

Los campos adicionales conservan información de agrupación, anotación y procedencia. La etiqueta humana se muestra para contrastar el resultado y no debe enviarse como entrada al modelo.

Los marcadores `[CITE]`, `[FORMULA]`, `[FIGURE]` y `[TABLE]` representan otras referencias y elementos no textuales. Los fragmentos están precalculados: esta muestra no ejecuta una recuperación nueva.

## 3. Distribución de la muestra

| Función | Ejemplos |
|---|---:|
| Background | 4 |
| Gap | 5 |
| Basis | 5 |
| Comparison | 3 |
| Application | 1 |
| Improvement/Modification | 10 |
| Evidence | 6 |
| Identification of the Originator | 0 |
| Further Reading | 6 |
| **Total** | **40** |

La selección no reproduce la distribución del corpus ni cubre las nueve categorías con ejemplos. Sus resultados no deben presentarse como una evaluación representativa del test completo.

## 4. Lectura y correspondencia con los modelos

El archivo puede leerse con Python sin bibliotecas adicionales, ejecutando desde la raíz del repositorio:

```python
import json
from pathlib import Path

ruta = Path("Datos/ejemplos_citas.jsonl")
ejemplos = [json.loads(linea) for linea in ruta.read_text(encoding="utf-8").splitlines() if linea.strip()]
ejemplo = ejemplos[0]
print(len(ejemplos), ejemplo["example_id"], ejemplo["label"])
```

SciBERT base utiliza `context`, `cited_title` y `cited_abstract`, adaptados a `context`, `title` y `abstract`. Top-3 utiliza `context` y los textos y secciones de `top3`, adaptados a `chunks`. Los contratos y límites se describen en [Modelos, entradas y salidas](../A4/Final/Modelos_Entradas_Salidas.md).

## 5. Licencia y atribución

Los 40 artículos citantes tienen licencia CC BY 4.0. De los artículos citados de los registros, 39 tienen CC BY 4.0 y uno CC BY 3.0. Los textos conservan las condiciones de sus artículos de origen; la publicación de esta muestra no establece una licencia nueva para ellos.

Cada reutilización o visualización debe conservar el título, enlace y licencia de los artículos. Los textos proceden de unarXive 2022 (Saier, Krause y Färber, 2023), con sustitución de marcas de citas y elementos no textuales por los marcadores documentados. Véase la [atribución del conjunto original del demostrador](../A3/Demostrador/README.md).

## 6. Datos de entrenamiento y evaluación

Las particiones completas y su reconstrucción se describen en [Métricas de A4](../A4/Final/M%C3%A9tricas.md) y en el [protocolo de evaluación](../A4/Evaluacion_Final/README.md). El repositorio no distribuye aquí el corpus íntegro ni las hojas privadas de anotación. Los cuadernos de reproducción requieren los recursos y permisos indicados en sus respectivas configuraciones.
