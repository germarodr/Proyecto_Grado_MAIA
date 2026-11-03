# Instalación paso a paso · Colab, Drive y visor MLflow en AWS Academy

**Grupo 15 · 29 de octubre de 2026.**

**Rutas actualizadas el 1 de noviembre de 2026:** entradas desde el acceso directo
`Mi unidad/MAIA_PROYECTO`; resultados y respaldos en `Mi unidad/MAIA_TESIS`.

Esta guía permite **instalar y comprobar el recorrido completo del historial**:
crear métricas de ejemplo en Colab, guardar un snapshot en Drive, restaurarlo en
AWS Academy y abrir el panel en el navegador del computador.

La arquitectura está en [README.md](README.md). El modelo y la configuración de
entrenamiento de SciBERT se conservan; se actualizaron las rutas de entrada y salida.
**Instalar MLflow no activa por sí solo su seguimiento**.
Al final se enlaza la guía para iniciar el entrenamiento con el seguimiento integrado.

## 0. Orden de ejecución y requisitos

| Orden | Dónde | Qué harás | Frecuencia |
|---|---|---|---|
| 1 | Drive y computador | Organizar carpetas, archivos y clave SSH | Primera vez |
| 2 | Colab | Instalar MLflow y generar un historial de prueba | Primera vez; reinstalar paquetes en cada sesión nueva |
| 3 | Colab → Drive | Crear un snapshot manual de prueba | Cada vez que quieras publicar esa copia |
| 4 | AWS Academy | Crear una instancia e instalar Docker | Primera vez o si el laboratorio elimina la instancia |
| 5 | Computador → AWS | Transferir y restaurar el snapshot | Para cada versión del historial que quieras consultar |
| 6 | AWS y computador | Iniciar el visor y el túnel SSH | Cada sesión de consulta |
| 7 | Colab | Preparar el entrenamiento real | Después de integrar y validar el seguimiento automático |

Necesitas tu cuenta de Colab, acceso de escritura a una carpeta de Drive, acceso al
laboratorio de Academy y una clave SSH válida para la instancia. No necesitas S3,
credenciales de AWS en Colab ni una instancia GPU en AWS.

Los bloques indican **dónde ejecutarlos**. Python corresponde a celdas de Colab;
PowerShell a tu computador Windows; Bash a la terminal SSH de AWS. No ejecutar los
comandos de AWS en PowerShell, salvo los marcados expresamente como SSH/SCP.

**Versión fijada para este ensayo: MLflow `3.17.2`**, disponible para Python ≥3.10.
Usaremos la misma versión en Colab y en el contenedor del visor. Esta instalación
todavía no constituye una validación de compatibilidad con el entrenamiento
SciBERT completo. [Paquete publicado](https://pypi.org/project/mlflow/3.17.2/).

## 1. Preparar Drive y los archivos del proyecto

### 1.1. En el navegador de Drive

1. Utiliza el acceso directo **`Mi unidad/MAIA_PROYECTO`** que ya creaste. Será el
   origen de los datos compartidos; no se guardarán allí resultados.
2. Comprueba que `a2/batches_norw/` contiene los ocho lotes requeridos por A4. Ya
   están descargados en el repositorio bajo `A4/a2/batches_norw/`; no necesitas el
   corpus de 58 GB para este entrenamiento.
3. La carpeta `TrainingData_Grupo15/` ya está subida directamente dentro de
   **`Mi unidad/MAIA_TESIS`**, como muestra tu captura. Esa ubicación es correcta:
   **`MAIA_TESIS/TrainingData_Grupo15/`**, con su manifiesto y sus cinco archivos
   JSONL. No necesitas crear `inputs/` ni reproducir en Drive las carpetas
   `Proyecto_Grado_MAIA/Folder_trabajo_Equipos_14_y_15/` del repositorio local.
   El notebook usa `IDS_DIR = RESULTS_ROOT / "TrainingData_Grupo15"`.
4. Los resultados, modelos y respaldos se escribirán únicamente bajo
   **`MAIA_TESIS/a4/`**. La celda de configuración comprueba que esa carpeta es escribible.

Las rutas se ajustaron a los nombres exactos de tu captura. En Colab el acceso
directo se lee con `DATA_ROOT` y la carpeta propia se configura con `RESULTS_ROOT`.
Montar Drive permite utilizar las entradas desde su ubicación; no descarga todo
el corpus ni modifica la carpeta compartida.

### 1.2. En tu computador Windows

Abre PowerShell y comprueba que tienes los clientes SSH y SCP:

```powershell
Get-Command ssh, scp
```

La clave que ya utilizaste es `aia-g15-mlflow-viewerKEY.pem` y está en la carpeta
raíz del proyecto. Los comandos de esta guía parten de una consola PowerShell
abierta en esa carpeta; no buscan la clave ni el snapshot en Descargas. La clave
no se sube a Git ni a Colab; `*.pem` ya está excluido mediante `.gitignore`.

## 2. Preparar Colab para el ensayo de instalación

### 2.1. Crear un notebook de prueba

1. Abre [Colab](https://colab.research.google.com/) y crea un notebook llamado
   `A4_Instalacion_MLflow`.
2. Para este ensayo utiliza **CPU**: no estamos entrenando SciBERT y no hace falta
   consumir A100.
3. Añade las siguientes celdas en orden. Este notebook de prueba es independiente
   de `A4_SciBERT_G15_Colab_A100.ipynb`.

### 2.2. Instalar MLflow — celda Python en Colab

```python
import subprocess
import sys

MLFLOW_VERSION = "3.17.2"
subprocess.check_call([
    sys.executable, "-m", "pip", "install", f"mlflow=={MLFLOW_VERSION}"
])
```

Si Colab solicita reiniciar la sesión por una biblioteca ya importada, reiníciala
y vuelve a ejecutar desde la celda siguiente. Al arrancar una máquina nueva de
Colab deberás instalar de nuevo los paquetes; los archivos guardados en Drive
permanecerán allí.

### 2.3. Montar Drive y fijar rutas — celda Python en Colab

```python
from pathlib import Path
from google.colab import drive

drive.mount("/content/drive")

DATA_ROOT = Path("/content/drive/MyDrive/MAIA_PROYECTO")  # acceso directo: entradas
RESULTS_ROOT = Path("/content/drive/MyDrive/MAIA_TESIS")  # carpeta propia: salidas
assert DATA_ROOT.is_dir(), f"Revisa el acceso directo DATA_ROOT: {DATA_ROOT}"
assert RESULTS_ROOT.is_dir(), f"Revisa la carpeta RESULTS_ROOT: {RESULTS_ROOT}"
if RESULTS_ROOT.resolve().is_relative_to(DATA_ROOT.resolve()):
    raise ValueError("RESULTS_ROOT debe estar fuera del origen compartido DATA_ROOT.")

SNAPSHOTS_ROOT = RESULTS_ROOT / "a4/_tracking/snapshots"
SNAPSHOTS_ROOT.mkdir(parents=True, exist_ok=True)

# Comprueba escritura con un archivo nuevo, sin tocar datos existentes.
import uuid
probe = SNAPSHOTS_ROOT / f"write_probe_{uuid.uuid4().hex}.txt"
probe.write_text("OK", encoding="utf-8")
assert probe.read_text(encoding="utf-8") == "OK"
probe.unlink()

TRACKING_ROOT = Path("/opt/maia/a4_tracking")
TRACKING_ROOT.mkdir(parents=True, exist_ok=True)
(TRACKING_ROOT / "artifacts").mkdir(exist_ok=True)
DB_PATH = TRACKING_ROOT / "mlflow.db"

print("Snapshots en Drive:", SNAPSHOTS_ROOT)
print("Base activa local:", DB_PATH)
```

Si falla el permiso de escritura, revisa que `RESULTS_ROOT` apunte a tu carpeta
`MAIA_TESIS`, no al acceso directo de datos. La base activa estará en el disco
local de Colab; los respaldos se guardarán en `MAIA_TESIS/a4/_tracking/snapshots/`.

### 2.4. Inicializar un experimento de prueba — celda Python en Colab

**Primera sesión:** ejecuta esta celda directamente. **En una sesión posterior con
historial previo:** restaura primero el snapshot siguiendo la sección 7. No abras
dos sesiones escritoras del mismo historial en paralelo.

```python
import os
os.environ["MLFLOW_ENABLE_ASYNC_LOGGING"] = "false"

import mlflow
from mlflow.tracking import MlflowClient

assert mlflow.__version__ == MLFLOW_VERSION
mlflow.set_tracking_uri(f"sqlite:///{DB_PATH}")
client = MlflowClient()

SMOKE_EXPERIMENT = "G15_A4_instalacion_smoke"
artifact_root = (TRACKING_ROOT / "artifacts/installation_smoke").as_uri()
experiment = client.get_experiment_by_name(SMOKE_EXPERIMENT)
if experiment is None:
    experiment_id = client.create_experiment(
        SMOKE_EXPERIMENT, artifact_location=artifact_root
    )
else:
    assert experiment.artifact_location == artifact_root
    experiment_id = experiment.experiment_id

mlflow.set_experiment(experiment_id=experiment_id)
print("MLflow:", mlflow.__version__)
print("Experimento:", experiment_id)
print("Tracking URI:", mlflow.get_tracking_uri())
```

El resultado debe apuntar a `sqlite:////opt/maia/a4_tracking/mlflow.db`, no a la IP
de AWS. La prueba tiene un nombre distinto del experimento de entrenamiento.
[MLflow con SQLite local](https://mlflow.org/docs/latest/ml/tracking/tutorials/local-database/).

### 2.5. Escribir métricas de ejemplo — celda Python en Colab

Los siguientes números son **datos ficticios de instalación**, no resultados de SciBERT.

```python
import time

with mlflow.start_run(run_name="prueba_instalacion") as run:
    smoke_run_id = run.info.run_id
    mlflow.set_tags({"purpose": "installation_smoke", "group": "G15"})
    mlflow.log_params({"config": "smoke", "seed": 42})
    for step, loss in enumerate([1.8, 1.2, 0.9], start=1):
        mlflow.log_metric("train_loss", loss, step=step)
        time.sleep(0.1)
    mlflow.log_metric("validation_f1_macro", 0.50, step=3)
    mlflow.log_dict(
        {"message": "Prueba de instalación; no es una evaluación del modelo."},
        "installation_check.json",
    )

assert client.get_run(smoke_run_id).info.status == "FINISHED"
assert len(client.get_metric_history(smoke_run_id, "train_loss")) == 3
print("Run de prueba:", smoke_run_id)
print("URI de artefactos:", client.get_run(smoke_run_id).info.artifact_uri)
```

Debes ver un run finalizado y una ruta de artefactos que empiece por
`file:///opt/maia/a4_tracking/artifacts/`. En este momento aún no hay una copia
durable del historial: continúa con el respaldo.

## 3. Crear el primer respaldo de prueba en Drive

### 3.1. Respaldo manual — celda Python en Colab

Esta celda se utiliza con **todos los runs cerrados y sin entrenamiento en marcha**.
Es una prueba manual de instalación. El respaldo periódico durante entrenamiento
requiere la coordinación de callbacks y el temporizador descritos en la arquitectura;
no se implementa un temporizador con esta celda.

El bloque crea un ZIP nuevo con SQLite y artefactos pequeños. No modifica ni elimina
snapshots anteriores. Durante este ensayo solo hemos registrado un JSON pequeño.

```python
import hashlib
import json
import shutil
import sqlite3
import zipfile
from contextlib import closing
from datetime import datetime, timezone

def file_sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()

assert mlflow.active_run() is None, "Cierra el run antes del respaldo manual."
open_runs = client.search_runs(
    [e.experiment_id for e in client.search_experiments()],
    filter_string="attributes.status = 'RUNNING'",
    max_results=1,
)
assert not open_runs, "Hay un run RUNNING. Revisa su estado antes de respaldar."
assert DB_PATH.is_file()

created_at = datetime.now(timezone.utc)
snapshot_id = created_at.strftime("%Y%m%dT%H%M%SZ_") + uuid.uuid4().hex[:8]
stage = TRACKING_ROOT / "staging" / snapshot_id
stage.mkdir(parents=True, exist_ok=False)

with closing(sqlite3.connect(DB_PATH)) as source:
    with closing(sqlite3.connect(stage / "mlflow.db")) as destination:
        source.backup(destination)
        result = destination.execute("PRAGMA integrity_check").fetchone()[0]
        assert result == "ok", result

shutil.copytree(TRACKING_ROOT / "artifacts", stage / "artifacts")
files_to_pack = sorted(p for p in stage.rglob("*") if p.is_file())
assert not any(p.is_symlink() for p in stage.rglob("*"))
file_index = {
    p.relative_to(stage).as_posix(): {
        "sha256": file_sha256(p), "size": p.stat().st_size
    }
    for p in files_to_pack
}
snapshot_manifest = {
    "schema_version": 1,
    "snapshot_id": snapshot_id,
    "created_at_utc": created_at.isoformat(),
    "mlflow_version": mlflow.__version__,
    "canonical_root": str(TRACKING_ROOT),
    "purpose": "installation_smoke",
    "files": file_index,
}
(stage / "snapshot_manifest.json").write_text(
    json.dumps(snapshot_manifest, indent=2), encoding="utf-8"
)

local_zip = stage.parent / f"{snapshot_id}.zip"
with zipfile.ZipFile(local_zip, "w", compression=zipfile.ZIP_DEFLATED) as archive:
    for path in sorted(p for p in stage.rglob("*") if p.is_file()):
        archive.write(path, path.relative_to(stage).as_posix())
with zipfile.ZipFile(local_zip) as archive:
    assert archive.testzip() is None

zip_sha = file_sha256(local_zip)
snapshot_dir = SNAPSHOTS_ROOT / snapshot_id
snapshot_dir.mkdir(exist_ok=False)
shutil.copyfile(local_zip, snapshot_dir / "snapshot.zip")
assert file_sha256(snapshot_dir / "snapshot.zip") == zip_sha
(snapshot_dir / "snapshot.sha256").write_text(
    f"{zip_sha}  snapshot.zip\n", encoding="utf-8"
)
(snapshot_dir / "COMPLETE.json").write_text(json.dumps({
    "schema_version": 1,
    "snapshot_id": snapshot_id,
    "created_at_utc": created_at.isoformat(),
    "zip_sha256": zip_sha,
    "zip_size": local_zip.stat().st_size,
    "mlflow_version": mlflow.__version__,
}, indent=2), encoding="utf-8")
print("Snapshot publicado:", snapshot_dir)
print("SHA-256:", zip_sha)
```

La copia de SQLite usa su API de respaldo, que obtiene una base consistente.
[Documentación de Python](https://docs.python.org/3/library/sqlite3.html#sqlite3.Connection.backup).
La verificación sobre el montaje de Drive debe complementarse comprobando que los
archivos aparecen en su navegador; si una transferencia queda incompleta, la
validación al restaurar la rechazará.

### 3.2. Descargar el snapshot al computador

1. Abre Drive y navega a `MAIA_TESIS/a4/_tracking/snapshots/<snapshot_id>/`.
2. Comprueba que están `snapshot.zip`, `snapshot.sha256` y `COMPLETE.json`.
3. Los **tres archivos** están en `snapshot_A4/`, dentro de la carpeta actual del
   repositorio. Conserva esa ubicación para los comandos de transferencia:
   `C:\Source\Maestria\Tesis\code\Proyecto_Grado_MAIA\snapshot_A4\`.
4. Si Drive envuelve la descarga en otro ZIP, extrae ese envoltorio. Conserva el
   archivo interior `snapshot.zip` sin extraer: lo validará el restaurador.

No necesitas transferir los datasets ni los pesos del modelo para esta prueba.

## 4. Preparar AWS Academy

### 4.1. Crear o reutilizar la instancia — consola de AWS

1. En Academy inicia el laboratorio y abre la consola de AWS.
2. Ve a **EC2 → Instances → Launch instances**, o reutiliza una instancia destinada
   al visor si ya existe.
3. Nombre sugerido: `maia-g15-mlflow-viewer`.
4. Sistema: **Ubuntu Server LTS, x86_64**, como la instancia a la que ya conectaste.
   Su usuario es `ubuntu`. Si utilizas Amazon Linux 2023, su usuario es `ec2-user`
   y debes elegir la rama de instalación correspondiente en la sección 4.3.
5. Como punto inicial para el visor utiliza una instancia con aproximadamente
   **2 vCPU y 4 GiB de RAM**, por ejemplo `t3.medium` si tu laboratorio la permite.
   No necesita GPU. Ajustaremos recursos después de medir el consumo del visor.
6. Disco: **20 GiB EBS** como punto inicial para Docker y snapshots pequeños. No se
   va a copiar el Drive completo a ese disco.
7. Selecciona el par de claves cuya clave privada tienes en el computador.
8. Red: una subred con salida a Internet e IP pública para descargar paquetes y
   recibir la conexión SSH.
9. Grupo de seguridad: entrada **SSH, TCP 22, desde tu IP pública actual**. No añadas
   una regla pública para el puerto 5000; accederemos por túnel.
10. Lanza la instancia y espera a que esté `Running` y pase sus comprobaciones.
    Anota su IPv4 pública y su Instance ID.

Las opciones permitidas dependen del laboratorio. Si Academy rechaza un tipo de
instancia o una operación, utiliza una opción permitida; no hace falta cambiar la
arquitectura ni crear una instancia GPU. El tiempo de cuatro horas corresponde a
la restricción que reportaste para tu laboratorio.
[Creación de una instancia EC2](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EC2_GetStarted.html).

### 4.2. Conectar por SSH — PowerShell en tu computador

Abre PowerShell en la raíz del repositorio, como en la consola que ya utilizaste:

```text
PS C:\Source\Maestria\Tesis\code\Proyecto_Grado_MAIA>
```

La estructura local es:

```text
Proyecto_Grado_MAIA/
├── aia-g15-mlflow-viewerKEY.pem
└── snapshot_A4/
    ├── snapshot.zip
    ├── snapshot.sha256
    └── COMPLETE.json
```

Los comandos resuelven ambas rutas desde la carpeta actual y utilizan la última
IP pública que confirmaste, `54.92.218.212`. Si reinicias Academy y cambia esa IP,
actualiza `$A4Host` en los bloques de conexión, transferencia y túnel.

Ejecuta:

```powershell
$A4Key = (Resolve-Path -LiteralPath '.\aia-g15-mlflow-viewerKEY.pem' -ErrorAction Stop).Path
$A4Host = '54.92.218.212'
$A4User = 'ubuntu'
$A4SnapshotLocal = (Resolve-Path -LiteralPath '.\snapshot_A4' -ErrorAction Stop).Path

Test-Path -LiteralPath $A4Key
Get-ChildItem -LiteralPath $A4SnapshotLocal
ssh -i "$A4Key" "${A4User}@${A4Host}"
```

Comprueba en EC2 la huella de la clave del host cuando SSH te pida aceptarla por
primera vez. Debes quedar en una terminal Linux como `ubuntu@ip-...`.

Si `Resolve-Path` falla, comprueba `Get-Location`: la consola debe estar en la raíz
del proyecto. Las rutas resueltas quedan absolutas para los comandos posteriores.
Conserva `$A4User` al ejecutar SCP y el túnel. `apt-get` corresponde a Ubuntu y
`dnf` a Amazon Linux 2023; elige únicamente la rama de tu distribución.

#### Si aparece `UNPROTECTED PRIVATE KEY FILE` en PowerShell

En Windows, OpenSSH comprueba la ACL del archivo. `chmod 400` desde otro entorno
puede no modificar esa ACL. Ejecuta estos comandos en la misma terminal donde
definiste `$A4Key`, comprobando primero que apunta a la clave correcta:

```powershell
$A4Key = (Resolve-Path -LiteralPath $A4Key).Path
$A4OwnerSid = (Get-Acl -LiteralPath $A4Key).GetOwner([System.Security.Principal.SecurityIdentifier]).Value
icacls.exe $A4Key /reset
icacls.exe $A4Key /grant:r ('*' + $A4OwnerSid + ':R')
icacls.exe $A4Key /inheritance:r
icacls.exe $A4Key
```

Cada comando debe terminar sin errores. El resultado debe mostrar únicamente al
propietario con lectura, sin permisos heredados de otros usuarios. Se utiliza el
SID del propietario para evitar depender de la resolución del nombre del dominio.
Esto modifica los permisos, no el contenido de la clave. Si la terminal no tiene
permiso para cambiar la ACL, ejecútala como administrador y repite los comandos
sobre ese mismo archivo. No copies una ACL de referencia sin comprobarla: en esta
revisión ambas claves locales tenían los mismos permisos heredados amplios.
[Procedimiento de AWS para permisos de claves en Windows](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/TroubleshootingInstancesConnecting.html#troubleshoot-unprotected-key).

### 4.3. Instalar Docker — Bash dentro de la instancia AWS

Tu instancia actual es **Ubuntu**. El error `dnf: command not found` indica que
se ejecutó el bloque de Amazon Linux en ella; los errores posteriores aparecen
porque Docker todavía no estaba instalado. Continúa en esa misma instancia.

Comprueba el sistema si tienes dudas:

```bash
cat /etc/os-release
```

#### Ubuntu — usar este bloque en tu instancia actual

```bash
sudo apt-get update
sudo apt-get install -y docker.io python3 curl
sudo systemctl enable --now docker
sudo docker version
sudo docker run --rm hello-world
mkdir -p "$HOME/maia-mlflow/build" "$HOME/maia-mlflow/incoming" "$HOME/maia-mlflow/restores"
```

Se instala `docker.io`, el paquete de los repositorios de Ubuntu utilizado por
la documentación de Canonical. No se necesita Docker Compose para este visor.
Debes ver versiones de **Client** y **Server**, y el mensaje `Hello from Docker!`.
[Docker en Ubuntu Server](https://ubuntu.com/server/docs/how-to/containers/docker-for-system-admins/).

#### Amazon Linux 2023 — solo si utilizas esa distribución

```bash
sudo dnf install -y docker python3 curl
sudo systemctl enable --now docker
sudo docker version
mkdir -p "$HOME/maia-mlflow/build" "$HOME/maia-mlflow/incoming" "$HOME/maia-mlflow/restores"
```

Se usa `sudo docker` para que no tengas que cerrar y reabrir SSH por cambios de
grupo. `enable --now` inicia el servicio y lo habilita para futuros reinicios de la
misma instancia. [Docker en Amazon Linux 2023](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-docker.html).

Cuando Docker responda correctamente, continúa con la sección **4.4**. No vuelvas
a ejecutar el bloque de la otra distribución.

### 4.4. Construir la imagen del visor — Bash dentro de AWS

El comando crea un Dockerfile en la carpeta de trabajo de la instancia:

```bash
cat > "$HOME/maia-mlflow/build/Dockerfile" <<'DOCKERFILE'
FROM python:3.12-slim
ARG MLFLOW_VERSION=3.17.2
RUN python -m pip install --no-cache-dir "mlflow==${MLFLOW_VERSION}"
WORKDIR /opt/maia/a4_tracking
EXPOSE 5000
ENTRYPOINT ["mlflow", "server"]
CMD ["--backend-store-uri", "sqlite:////opt/maia/a4_tracking/mlflow.db", "--default-artifact-root", "file:///opt/maia/a4_tracking/artifacts", "--host", "0.0.0.0", "--port", "5000", "--workers", "1"]
DOCKERFILE

sudo docker build --build-arg MLFLOW_VERSION=3.17.2 -t maia-mlflow:3.17.2 "$HOME/maia-mlflow/build"
sudo docker run --rm --entrypoint mlflow maia-mlflow:3.17.2 --version
```

Debe mostrar MLflow `3.17.2`. La imagen base se identifica por etiqueta en este
ensayo; guarda su digest y las versiones instaladas si después necesitas fijar
también todas las dependencias transitivas de la imagen.

El proceso escucha en `0.0.0.0` **dentro del contenedor** para que Docker pueda
conectarlo. En el siguiente paso el puerto del host se publicará únicamente en
`127.0.0.1` de la instancia.

## 5. Transferir y restaurar el historial

### 5.1. Copiar los tres archivos — otra terminal PowerShell en tu computador

Abre otra terminal PowerShell **en la raíz del repositorio**. El bloque es autónomo:
vuelve a configurar la clave y `snapshot_A4/` desde la carpeta actual, el usuario
Ubuntu y la IP conocida. Usa la IP nueva si Academy la cambió. La carpeta remota
`maia-mlflow/incoming/` debe haberse creado en la sección 4.3.

```powershell
$A4Key = (Resolve-Path -LiteralPath '.\aia-g15-mlflow-viewerKEY.pem' -ErrorAction Stop).Path
$A4Host = '54.92.218.212'
$A4User = 'ubuntu'
$A4SnapshotLocal = (Resolve-Path -LiteralPath '.\snapshot_A4' -ErrorAction Stop).Path

foreach ($A4File in @("snapshot.zip", "snapshot.sha256", "COMPLETE.json")) {
    if (-not (Test-Path -LiteralPath (Join-Path $A4SnapshotLocal $A4File))) {
        throw "Falta $A4File en $A4SnapshotLocal"
    }
}
scp -i "$A4Key" (Join-Path $A4SnapshotLocal "snapshot.zip") (Join-Path $A4SnapshotLocal "snapshot.sha256") (Join-Path $A4SnapshotLocal "COMPLETE.json") "${A4User}@${A4Host}:maia-mlflow/incoming/"
```

Esta carpeta de entrada recibe un snapshot cada vez. Los historiales restaurados
se guardarán por separado; copiar una entrada nueva no cambia el visor ya abierto.

### 5.2. Crear el restaurador — Bash dentro de AWS

Este bloque crea un script autónomo con bibliotecas estándar de Python. No depende
de un script inexistente del repositorio ni requiere instalar MLflow en el host.
Comprobará versión, hashes, rutas e integridad antes de iniciar el panel.

```bash
cat > "$HOME/maia-mlflow/restore_snapshot.py" <<'PY'
from pathlib import Path, PurePosixPath
import hashlib
import json
import re
import sqlite3
import stat
import uuid
import zipfile
from contextlib import closing

EXPECTED_MLFLOW = "3.17.2"
CANONICAL_ROOT = "/opt/maia/a4_tracking"
base = Path.home() / "maia-mlflow"
incoming = base / "incoming"
receipt = json.loads((incoming / "COMPLETE.json").read_text(encoding="utf-8"))
assert receipt["schema_version"] == 1
assert receipt["mlflow_version"] == EXPECTED_MLFLOW
snapshot_id = receipt["snapshot_id"]
assert re.fullmatch(r"[A-Za-z0-9_-]+", snapshot_id)

def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

archive_path = incoming / "snapshot.zip"
expected_sha = receipt["zip_sha256"]
assert archive_path.stat().st_size == receipt["zip_size"]
assert sha(archive_path) == expected_sha, "SHA-256 del ZIP incorrecto"
assert (incoming / "snapshot.sha256").read_text().split()[0] == expected_sha

destination = base / "restores" / (snapshot_id + "_" + uuid.uuid4().hex[:8])
destination.mkdir(parents=True, exist_ok=False)
with zipfile.ZipFile(archive_path) as archive:
    names = [item.filename for item in archive.infolist()]
    assert len(names) == len(set(names)), "Entradas duplicadas en ZIP"
    assert archive.testzip() is None, "ZIP dañado"
    for item in archive.infolist():
        relative = PurePosixPath(item.filename)
        assert not relative.is_absolute() and ".." not in relative.parts
        assert "\\" not in item.filename
        assert not stat.S_ISLNK(item.external_attr >> 16), "Enlace simbólico en ZIP"
        target = (destination / item.filename).resolve()
        assert target.is_relative_to(destination.resolve())
        assert (item.filename in {"mlflow.db", "snapshot_manifest.json"}
                or item.filename.startswith("artifacts/")), "Archivo fuera del contrato"
    manifest = json.loads(archive.read("snapshot_manifest.json"))
    assert manifest["schema_version"] == 1
    assert manifest["snapshot_id"] == snapshot_id
    assert manifest["mlflow_version"] == EXPECTED_MLFLOW
    assert manifest["canonical_root"] == CANONICAL_ROOT
    assert set(names) == set(manifest["files"]) | {"snapshot_manifest.json"}
    archive.extractall(destination)

for relative, metadata in manifest["files"].items():
    path = destination / relative
    assert path.is_file()
    assert path.stat().st_size == metadata["size"], relative
    assert sha(path) == metadata["sha256"], relative
(destination / "artifacts").mkdir(exist_ok=True)
db = destination / "mlflow.db"
assert db.is_file()
with closing(sqlite3.connect(db.as_uri() + "?mode=ro", uri=True)) as conn:
    assert conn.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
(base / "last_restore.txt").write_text(str(destination) + "\n", encoding="utf-8")
print("Snapshot validado:", snapshot_id)
print("Restaurado en:", destination)
PY

python3 "$HOME/maia-mlflow/restore_snapshot.py"
```

Debe terminar con `Snapshot validado` y una carpeta nueva bajo `restores/`. Si falla,
no arranques el visor con una base nueva vacía para aparentar una restauración:
corrige los archivos de entrada o utiliza un respaldo completo anterior.

### 5.3. Iniciar el visor — Bash dentro de AWS

Primera ejecución, sin un contenedor anterior llamado `maia-mlflow`:

```bash
A4_RESTORE="$(cat "$HOME/maia-mlflow/last_restore.txt")"
if test -f "$A4_RESTORE/mlflow.db"; then
    sudo docker run -d --name maia-mlflow --restart unless-stopped --publish 127.0.0.1:5000:5000 --mount "type=bind,source=${A4_RESTORE},target=/opt/maia/a4_tracking" maia-mlflow:3.17.2
else
    printf 'No existe la base restaurada. Revisa la sección 5.2.\n'
fi
```

La salida con un identificador largo indica que Docker creó e inició el contenedor;
no confirma todavía que MLflow haya terminado de arrancar. Una consulta inmediata
puede dar `Connection reset by peer` o `Connection refused`.
Si ya apareció ese identificador, **no repitas `docker run`**: continúa con el bloque
de espera y comprobación de abajo. Si falla, sus logs permiten distinguir una demora
de un error real del servidor. [Inicio en segundo plano de Docker](https://docs.docker.com/reference/cli/docker/container/run/).

```bash
a4_wait_for_mlflow() {
    local attempt
    for attempt in $(seq 1 30); do
        if curl --fail --silent --connect-timeout 2 --max-time 3 http://127.0.0.1:5000/health >/dev/null 2>&1; then
            printf 'MLflow listo. Continúa con la sección 6.1.\n'
            curl --fail --show-error http://127.0.0.1:5000/health
            printf '\n'
            return 0
        fi
        sleep 2
    done
    printf 'MLflow no respondió dentro de los 30 intentos. Diagnóstico:\n'
    sudo docker ps -a --filter name=maia-mlflow
    sudo docker inspect --format 'estado={{.State.Status}} reinicios={{.RestartCount}} OOM={{.State.OOMKilled}} salida={{.State.ExitCode}} error={{.State.Error}}' maia-mlflow
    sudo docker logs --tail 100 maia-mlflow
    return 1
}
a4_wait_for_mlflow
```

El health check debe responder correctamente antes de abrir el túnel. Si el
contenedor aparece como `Restarting` o `Exited`, revisa el error concreto de los
logs; si `OOM=true`, el proceso se quedó sin memoria. El contador de reinicios
ayuda a detectar un fallo repetido, en lugar de esperar indefinidamente.

El volumen conserva la ruta interna
de Colab para que los URI de los artefactos sigan resolviendo. El visor utiliza una
copia local; cualquier cambio en él no se copiará de vuelta a Drive.

## 6. Abrir el panel desde tu computador

### 6.1. Crear el túnel — PowerShell en Windows

En otra terminal PowerShell **abierta en la raíz del repositorio**, ejecuta este
bloque. Resuelve la clave local y no depende de variables de otra ventana:

```powershell
$A4Key = (Resolve-Path -LiteralPath '.\aia-g15-mlflow-viewerKEY.pem' -ErrorAction Stop).Path
$A4Host = '54.92.218.212'
$A4User = 'ubuntu'

ssh -i "$A4Key" -N -o ExitOnForwardFailure=yes -o ServerAliveInterval=30 -L 5000:127.0.0.1:5000 "${A4User}@${A4Host}"
```

La terminal quedará ocupada y puede no imprimir nada: es normal. Déjala abierta.
En tu navegador visita **http://localhost:5000**.

### 6.2. Comprobar la instalación en el panel

1. Abre el experimento `G15_A4_instalacion_smoke`.
2. Selecciona la vista **Runs / Ejecuciones** si aparecen pestañas. Esta prueba
   registra un run con métricas y un JSON; las vistas de modelos o trazas pueden
   estar vacías porque no se registró un modelo ni una traza.
3. Quita filtros de búsqueda, estado y fechas que pudieran ocultar el run. Si hay
   un selector temporal, selecciona todo el historial; el run está finalizado.
4. Abre el run `prueba_instalacion` más reciente y comprueba su identificador.
5. Verifica tres valores de `train_loss`: **1,8; 1,2; 0,9**.
6. Verifica el valor ficticio `validation_f1_macro = 0,50`.
7. En **Artifacts**, abre o descarga `installation_check.json` y confirma su mensaje.

#### Si el experimento se ve vacío

Se revisó el snapshot local `20261102T003906Z_2595a28e`: su hash coincide, SQLite
supera `integrity_check` y contiene:

| Campo | Valor comprobado en ese snapshot |
|---|---|
| Experimento | `G15_A4_instalacion_smoke`, ID `1` |
| Run | `prueba_instalacion` |
| Run ID | `86571fa0554045368bc774c434e48673` |
| Estado | `FINISHED`, activo, no eliminado |
| Métricas | Tres puntos de `train_loss` y uno de `validation_f1_macro` |
| Artefacto | `installation_check.json` incluido en el ZIP |

Esto confirma el contenido del respaldo local; no demuestra por sí solo qué
snapshot está sirviendo el contenedor de AWS. Primero revisa la pestaña y los
filtros indicados arriba. Después consulta el servidor que está detrás del mismo
túnel, sin crear otro experimento ni volver a registrar métricas:

```text
http://localhost:5000/api/2.0/mlflow/runs/get?run_id=86571fa0554045368bc774c434e48673
```

Abre esa dirección en el navegador con el túnel activo. También puedes hacer la
misma consulta desde la terminal Ubuntu:

```bash
curl --silent --show-error 'http://127.0.0.1:5000/api/2.0/mlflow/runs/get?run_id=86571fa0554045368bc774c434e48673' | python3 -m json.tool
```

- Si devuelve `run` con ese ID y sus métricas, el servidor sí lee la ejecución:
  revisa la vista de runs, sus filtros y la consola de errores del navegador.
- Si devuelve `RESOURCE_DOES_NOT_EXIST`, compara el montaje y la base del visor
  con el snapshot validado. El siguiente comando muestra la ruta que realmente
  usa el contenedor, que puede diferir de `last_restore.txt` si se restauró después:

```bash
sudo docker inspect --format '{{range .Mounts}}{{println .Source "->" .Destination}}{{end}}' maia-mlflow
sudo docker logs --tail 100 maia-mlflow
```

Si fuera necesario cargar otro snapshot, sigue la sección 7.1. No reemplaces la
base de un visor en marcha ni vuelvas a ejecutar la prueba en Colab para intentar
corregir una vista vacía. El endpoint devuelve el run y el último valor de cada
métrica, no toda su serie temporal. [Consulta de runs por API](https://mlflow.org/docs/latest/api_reference/rest-api.html#get-run).

Si métricas y artefactos son visibles, quedó probado el recorrido **Colab → Drive →
AWS → navegador**. AWS puede apagarse después sin afectar el historial en Drive.
El túnel controla el acceso al panel; no necesitamos abrir TCP 5000 al público.
[Opciones del servidor MLflow](https://mlflow.org/docs/latest/api_reference/cli.html#mlflow-server).

### 6.3. Cerrar la consulta

En PowerShell cierra el túnel con `Ctrl+C`. Si terminaste de consultar, detén el
visor en AWS y luego detén la instancia desde EC2 cuando corresponda:

```bash
sudo docker stop maia-mlflow
```

Utiliza **Stop instance**, no **Terminate instance**, si quieres conservar esa
instancia para otra sesión. Drive es la fuente del historial respaldado; no dependemos
de que el laboratorio conserve el disco de la máquina.

## 7. Qué repetir en sesiones posteriores

### 7.1. Actualizar el panel con un snapshot nuevo

1. Publica el snapshot nuevo en Drive y coloca sus tres archivos juntos en la
   carpeta local `snapshot_A4/`, sustituyendo la copia anterior de esa carpeta.
2. Abre PowerShell en la raíz del proyecto. Si cambió la IP, reemplaza
   `54.92.218.212` en `$A4Host` en los bloques que vayas a ejecutar y transfiere los
   archivos siguiendo la sección 5.1.
3. En AWS ejecuta nuevamente `restore_snapshot.py`. Siempre crea una copia nueva.
4. Detén el contenedor anterior y elimínalo **sin borrar la carpeta restaurada**:

```bash
sudo docker stop maia-mlflow
sudo docker rm maia-mlflow
```

5. Ejecuta de nuevo la sección 5.3 para montar la nueva carpeta. Nunca reemplaces
   la base del contenedor mientras MLflow la está utilizando.
6. Reconecta el túnel y revisa el panel. Es una consulta al snapshot elegido;
   no es actualización en vivo desde Colab.

### 7.2. Volver a entrar después de apagarse Academy

1. Inicia otra sesión del laboratorio.
2. Si la instancia persiste, arráncala y toma su IP pública actual. Reemplaza el
   valor de `$A4Host` si ya no es `54.92.218.212`. Actualiza también
   la regla de SSH «My IP» si tu conexión a Internet cambió de IP.
3. Conecta con SSH y comprueba `sudo docker ps -a`.
4. Si el contenedor está detenido, ejecuta `sudo docker start maia-mlflow`.
5. Abre el túnel hacia la nueva IP. Se mostrará el snapshot que estaba restaurado.
6. Para datos más recientes, sigue la sección 7.1. Si el laboratorio eliminó la
   instancia, repite su instalación y restaura desde Drive.

### 7.3. Restaurar el historial en una nueva sesión de Colab

Para el ensayo manual, instala MLflow y monta Drive como en las secciones 2.2 y 2.3,
pero **no inicialices todavía un experimento ni registres un run nuevo**.

Selecciona el identificador del respaldo que quieres recuperar y ejecuta esta celda
**antes de la inicialización de MLflow de la sección 2.4**. Rechaza la operación si
ya existe una base local o hay artefactos previos, para no sobrescribir otro historial:

```python
import hashlib
import json
import shutil
import sqlite3
import stat
import uuid
import zipfile
from contextlib import closing
from pathlib import PurePosixPath

RESTORE_ID = "IDENTIFICADOR_DEL_SNAPSHOT"  # EDITAR: nombre de carpeta en Drive
assert RESTORE_ID == Path(RESTORE_ID).name and RESTORE_ID not in {".", ".."}
incoming = SNAPSHOTS_ROOT / RESTORE_ID
assert not DB_PATH.exists(), "Ya hay una base local: no se sobrescribe."
assert not any((TRACKING_ROOT / "artifacts").iterdir()), "Ya hay artefactos locales."
receipt = json.loads((incoming / "COMPLETE.json").read_text(encoding="utf-8"))
assert receipt["schema_version"] == 1 and receipt["snapshot_id"] == RESTORE_ID
assert receipt["mlflow_version"] == MLFLOW_VERSION

def restore_sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

zip_path = incoming / "snapshot.zip"
assert zip_path.stat().st_size == receipt["zip_size"]
assert restore_sha(zip_path) == receipt["zip_sha256"]
assert (incoming / "snapshot.sha256").read_text().split()[0] == receipt["zip_sha256"]
stage = TRACKING_ROOT / "staging" / ("restore_" + uuid.uuid4().hex)
stage.mkdir(parents=True, exist_ok=False)
with zipfile.ZipFile(zip_path) as archive:
    names = [item.filename for item in archive.infolist()]
    assert len(names) == len(set(names)) and archive.testzip() is None
    for item in archive.infolist():
        relative = PurePosixPath(item.filename)
        assert not relative.is_absolute() and ".." not in relative.parts
        assert "\\" not in item.filename and not stat.S_ISLNK(item.external_attr >> 16)
        assert (stage / item.filename).resolve().is_relative_to(stage.resolve())
        assert item.filename in {"mlflow.db", "snapshot_manifest.json"} or item.filename.startswith("artifacts/")
    manifest = json.loads(archive.read("snapshot_manifest.json"))
    assert manifest["schema_version"] == 1 and manifest["snapshot_id"] == RESTORE_ID
    assert manifest["mlflow_version"] == MLFLOW_VERSION
    assert manifest["canonical_root"] == str(TRACKING_ROOT)
    assert set(names) == set(manifest["files"]) | {"snapshot_manifest.json"}
    archive.extractall(stage)
for relative, metadata in manifest["files"].items():
    path = stage / relative
    assert path.is_file() and path.stat().st_size == metadata["size"]
    assert restore_sha(path) == metadata["sha256"], relative
with closing(sqlite3.connect(stage / "mlflow.db")) as conn:
    assert conn.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
if (stage / "artifacts").exists():
    shutil.copytree(stage / "artifacts", TRACKING_ROOT / "artifacts", dirs_exist_ok=True)
shutil.copyfile(stage / "mlflow.db", DB_PATH)
print("Historial restaurado:", RESTORE_ID)
```

Después ejecuta la inicialización de MLflow. El experimento anterior debe aparecer
con sus runs originales; no vuelvas a crear una base independiente para fusionarla
después. La celda no restaura pesos de SciBERT ni sus estados de optimización.

El notebook de entrenamiento ya incorpora selección automática del último snapshot,
cierre de intentos interrumpidos y checkpoints verificados. Los pasos manuales de
esta sección sirven para comprobar la instalación; para entrenar usa la
[guía de primera corrida](PRIMERA_CORRIDA.md).

## 8. Preparar el entrenamiento de SciBERT en Colab

El seguimiento automático está integrado. Sigue la [guía de primera corrida](PRIMERA_CORRIDA.md).

1. Abre [A4_SciBERT_G15_Colab_A100.ipynb](A4_SciBERT_G15_Colab_A100.ipynb) en Colab.
2. Selecciona **Entorno de ejecución → Cambiar tipo de entorno → GPU A100** y verifica
   la GPU asignada. Usa el notebook de instalación CPU para probar el visor primero.
3. Verifica `DATA_ROOT = /content/drive/MyDrive/MAIA_PROYECTO` y
   `RESULTS_ROOT = /content/drive/MyDrive/MAIA_TESIS`. El notebook deriva de ellas
   `IDS_DIR`, `BATCH_DIR` y `OUTPUT_ROOT`; los resultados quedan en `MAIA_TESIS/a4/`.
4. Conserva `RUN_TEST=False` y `GOLD_FINAL=False` mientras no haya gold consolidado.
5. Restaura el historial antes de abrir los runs de seguimiento.
6. Comprueba hashes, particiones y los ocho lotes con las celdas del notebook.
7. Inicia el entrenamiento con runs de MLflow vinculados a `RUN_ID`, callbacks y
   respaldo periódico ya integrados y probados.
8. Consulta en AWS los snapshots publicados sin mantener la instancia encendida
   durante el entrenamiento.

**Estado actual:** el notebook usa un callback propio de MLflow. `report_to="none"`
evita el callback automático de Hugging Face para no duplicar runs ni subir pesos
al historial. Se guardan intentos padre/hijo, snapshots y hashes de checkpoints.
La ejecución real de SciBERT en A100 debe validarse en Colab.

## 9. Solución de problemas

| Problema | Qué comprobar |
|---|---|
| Colab no encuentra `MAIA_PROYECTO` | Drive montado, nombre del acceso directo y ruta real en Mi unidad |
| Colab no encuentra `MAIA_TESIS` | Revisar el nombre exacto de tu carpeta y la variable `RESULTS_ROOT` |
| No puede crear `_tracking` | Comprobar permiso de escritura en `MAIA_TESIS`, no en `MAIA_PROYECTO` |
| Reiniciaste Colab y no hay base | Restaurar el snapshot de Drive antes de registrar nuevas ejecuciones |
| SSH da timeout | Instancia encendida, IP actual, subred con acceso y TCP 22 desde tu IP |
| SSH indica `Permission denied (publickey)` | `$A4User="ubuntu"` para tu instancia; `ec2-user` solo para Amazon Linux; verificar clave y par asociado |
| `dnf: command not found` | Es Ubuntu: usar el bloque `apt-get` de la sección 4.3 |
| Windows dice `UNPROTECTED PRIVATE KEY FILE` | Aplicar la corrección de ACL de la sección 4.2; no basta con `chmod` ni con copiar permisos amplios de otra clave |
| Docker no responde | Ejecutar `sudo systemctl start docker` y usar `sudo docker` |
| Contenedor con ese nombre ya existe | Ver sección 7.1; no lanzar una segunda copia con el mismo nombre |
| Docker falla al instalar MLflow | Revisar conexión a PyPI, memoria, espacio y mensajes del build; mantener la misma versión en ambos entornos |
| `COMPLETE.json` o SHA no coincide | Repetir la descarga de los tres archivos del mismo snapshot |
| Métricas visibles, artefactos fallan | Verificar que el snapshot incluya `artifacts/` y el montaje conserve `/opt/maia/a4_tracking` |
| `localhost:5000` no abre | Health check en AWS, logs del contenedor y terminal del túnel todavía abierta |
| El primer `curl /health` da `Connection reset by peer` | Ejecutar el bloque de espera de 5.3 sin repetir `docker run`; si persiste, revisar estado, reinicios y logs |
| Puerto 5000 ocupado en Windows | Usar `-L 5001:127.0.0.1:5000` y abrir `http://localhost:5001` |
| Panel muestra resultados antiguos | El visor es una réplica: restaurar el snapshot nuevo y recrear el contenedor |
| El experimento aparece vacío | Revisar Runs/Ejecuciones, filtros y consulta API del run de prueba según 6.2 |
| Host key cambió tras reutilizar una IP | Comprobar la identidad desde EC2 antes de actualizar `known_hosts`; no desactivar la verificación SSH |

Para problemas de permisos de clave, usa la
[guía oficial de conexión SSH de EC2](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/connect-to-linux-instance.html).

## 10. Lista de comprobación de instalación

- [ ] Drive accesible y carpeta de resultados escribible.
- [ ] MLflow `3.17.2` instalado en el notebook de prueba.
- [ ] Run de prueba finalizado con tres valores de pérdida.
- [ ] ZIP, SHA-256 y `COMPLETE.json` publicados en Drive.
- [ ] Instancia Ubuntu accesible por SSH; distribución y `$A4User` coherentes.
- [ ] Imagen Docker construida con la misma versión de MLflow.
- [ ] Restauración validada y health check correcto.
- [ ] Panel abierto por túnel SSH, con métricas y JSON de prueba visibles.
- [ ] Procedimiento de actualización identificado para la próxima sesión de Academy.

Los comandos se documentan para que los ejecutes en tus cuentas. No se han creado
recursos de AWS ni ejecutado esta instalación remota desde el repositorio. Los
fragmentos Python tienen sintaxis verificada; se comprobó localmente el respaldo
de una base SQLite de ejemplo, su restauración en ambos flujos y el rechazo de un
ZIP alterado. Esa prueba no instaló MLflow ni arrancó Docker. La comprobación real
de Colab, MLflow y Academy se realiza siguiendo esta lista.
