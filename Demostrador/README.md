# CiteScope · Demostrador de función de citas

Demostrador del proyecto de grado (FLAG, Uniandes). Para un ejemplo validado por humanos muestra los
3 fragmentos recuperados del artículo citado y clasifica la función de la cita con tres tipos de modelo.

```
demo-citas-PRD/
├── docker-compose.yml   db · model-init · ollama · ollama-pull · api · frontend
├── api/
│   ├── main.py                          endpoints, carga del encoder, llamadas a los LLM
│   ├── database.py                      tabla inference_logs
│   ├── schemas.py                       contratos de entrada y salida
│   ├── a5_runtime.py, a5_drive.py,      código de A5/Gemini: perfil del proveedor, recorte,
│   │   a5_alignment.py, a5_providers.py prompt y validación de la respuesta
│   ├── prompt_v11_1_snapshot.json       prompt v11.1 de A5
│   └── examples_TB_con_resumen.jsonl    los 40 ejemplos del Test (fuente única de datos)
├── frontend/            Next.js
└── models/top3/         paquete exportado de SciBERT Top-3 (se descarga al iniciar)
```

## Flujo

1. **Ejemplo:** menú fijo con los 40 ejemplos; no hay texto libre.
2. **Top-3:** fragmentos guardados en el ejemplo (`top3`), en orden de rango y con su sección; no se calcula similitud.
3. **Clasificar:** tres opciones.
   - **Encoder:** SciBERT Top-3 (contexto + 3 fragmentos con su sección).
   - **Comercial:** Gemini 3.5 Flash-Lite con el flujo de A5: contexto + título + resumen recortados con la
     política de SciBERT base, prompt v11.1 en la condición `base-specific-zero`, `json_schema` estricto y
     validación de los 9 puntajes (suma 1).
   - **Open-weight:** Llama 3.1 8B Instruct (GGUF Q4_K_M de Hugging Face) servido por Ollama, con el mismo
     prompt, entrada, esquema y validación que el comercial.
4. **Resultados:** función predicha y su definición, puntajes de las 9 funciones, fragmentos y etiqueta humana ✓/✗.

Los textos provienen de artículos de arXiv con licencia CC BY (unarXive 2022); la aplicación muestra el título,
el enlace y la licencia de cada artículo.

## API

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/health` | Disponibilidad de los tres modelos |
| GET | `/examples` | Los 40 ejemplos |
| POST | `/predictions` | `{"example_id": "B-001", "model_type": "encoder" \| "open_weight" \| "commercial"}`; el encoder responde 201 con el resultado y los LLM 202 con estado `pending` |
| GET | `/predictions` | Historial de `inference_logs` |

Las consultas a los LLM se procesan en segundo plano: la interfaz revisa el estado cada 3 s, así que una
respuesta lenta de Llama no se corta en el navegador. La API la cancela a los 10 minutos
(`OPEN_WEIGHT_TIMEOUT`, en segundos). Una respuesta cuyos 9 puntajes no sumen 1 (±0,001) se registra como error,
con el mismo validador para Gemini y Llama.

La documentación interactiva queda en `http://localhost:8002/docs`, accesible solo desde la misma máquina.

## Configuración

Copiar `.env.example` a `.env`:

| Variable | Uso |
|---|---|
| `GEMINI_API_KEY` | Clave de Google AI Studio para el modelo comercial |
| `OPEN_WEIGHT_MODEL` | Modelo de Ollama; por defecto Llama 3.1 8B Instruct Q4_K_M |
| `TOP3_GDRIVE_ID` | Archivo de Drive con el paquete de SciBERT Top-3 |
| `POSTGRES_PASSWORD` | Contraseña de la base; si se deja vacía se usa `citas` |
| `FRONTEND_PORT` | Puerto público del frontend (3001 en local, 80 en EC2) |
| `API_PORT` | Puerto local de la API, solo en `127.0.0.1` (8002 por defecto) |

`POSTGRES_PASSWORD` solo se aplica al crear el volumen `pgdata`. Si la base ya existe, cambiarla exige borrar
el volumen (`docker compose down -v`), lo que borra también el historial.

## Ejecución local

```
docker compose up -d --build
```

El proyecto se llama `demo-citas-prd`: sus contenedores, red y volúmenes no se comparten con ninguna otra
copia, y sus puertos (3001 y 8002) le permiten correr al mismo tiempo que DEV. La primera vez se descargan
SciBERT (≈440 MB) en `models/` y el modelo de Ollama (≈4,9 GB) en su volumen. La aplicación queda en
`http://localhost:3001`. Sin GPU, cada inferencia de Llama 3.1 8B puede tardar varios minutos y requiere
unos 12 GB de memoria disponibles para Docker.

## Despliegue en Amazon EC2

1. **Instancia.** Ubuntu Server 24.04 LTS, x86_64, con disco gp3 de 50 GB.
   - Solo CPU: `m7i.2xlarge` (8 vCPU, 32 GB) o, como mínimo, `m7i.xlarge` (4 vCPU, 16 GB).
   - Con GPU: `g4dn.xlarge` (NVIDIA T4). Usar la AMI *Deep Learning Base OSS Nvidia Driver GPU AMI (Ubuntu)*,
     que ya trae el controlador y NVIDIA Container Toolkit. Las cuentas nuevas suelen requerir solicitar cupo
     para instancias G en *Service Quotas*.
2. **Grupo de seguridad.** Entrada 22 (SSH) solo desde la IP propia y 80 (HTTP) desde cualquier origen.
   No abrir 8001 ni 11434.
3. **Docker.**
   ```
   curl -fsSL https://get.docker.com | sudo sh
   sudo usermod -aG docker ubuntu
   ```
   Cerrar la sesión SSH y volver a entrar.
4. **Código.** Desde el equipo local:
   ```
   scp -i llave.pem -r demo-citas-PRD ubuntu@<IP_PUBLICA>:~/demo-citas-PRD
   ```
5. **Variables.** En la instancia, dentro de `~/demo-citas-PRD`, crear `.env` a partir de `.env.example` con
   `GEMINI_API_KEY`, una `POSTGRES_PASSWORD` propia y `FRONTEND_PORT=80`.
6. **Arranque.**
   ```
   docker compose up -d --build
   docker compose logs -f ollama-pull
   ```
   Cuando termine la descarga, la aplicación queda en `http://<IP_PUBLICA>`.

Los contenedores se reinician solos si la instancia se reinicia. Para conservar la misma dirección, asociar
una IP elástica. Para no pagar horas sin uso, detener la instancia (`Stop`); los volúmenes se conservan.

### GPU

En una instancia con GPU, agregar al servicio `ollama` de `docker-compose.yml`:

```yaml
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
```

y ejecutar `docker compose up -d`. El mismo bloque funciona en Docker Desktop con una GPU NVIDIA.
