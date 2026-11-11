# Colab en VS Code y ejecución desde Codex

Configuración comprobada el 4 de noviembre de 2026 en este equipo Windows.

El notebook se abre en el repositorio local de VS Code; las celdas se ejecutan en
el kernel remoto de Colab. El puente Notebook MCP permite consultar las salidas,
leer variables y ejecutar celdas del notebook abierto. Los datos, modelos e
historial de A4 continúan en Drive, con el visor de snapshots en AWS.

## Configuración instalada

| Componente | Configuración comprobada |
|---|---|
| Google Colab para VS Code | `google.colab`, 0.9.7 |
| Python y Jupyter | Extensiones de Microsoft instaladas |
| Puente Notebook MCP | `yukhin.vscode-notebook-mcp`, 0.6.2; extensión de terceros |
| Node.js | 22.16.0 |
| Servidor MCP en Codex | `maia_notebook`, transporte STDIO |
| Selector del workspace | `NOTEBOOK_MCP_WORKSPACE` apunta a este repositorio |

El servidor está registrado en la configuración local de Codex del usuario.
El puente utiliza el archivo administrado por la extensión:
`C:\Users\storo\.vscode-notebook-mcp\bridge.js`.
Los tokens se gestionan fuera del repositorio; no es necesario copiarlos al chat.

## Prueba realizada

Archivo: [Prueba_Colab_VSCode.ipynb](Prueba_Colab_VSCode.ipynb).

1. El usuario ejecutó el notebook en VS Code conectado a Colab.
2. Se detectó una Tesla T4, con 14,56 GiB de memoria.
3. El cálculo pequeño en GPU coincidió con la referencia CPU.
4. Se montó Drive, se encontraron las tres carpetas requeridas y se leyó el
   marcador `TRAINING_COMPLETE.json` del modelo base.
5. El usuario ejecutó el contador hasta 2.
6. Codex conectó al servidor MCP, encontró el notebook y consultó el kernel activo.
7. Codex leyó `MAIA_KERNEL_PROBE` y ejecutó únicamente la celda `probe-09`.
8. El contador pasó de 2 a 3, con el mismo `session_id`, y se guardó la salida
   mediante la API de notebooks de VS Code.

La prueba valida ejecución remota desde Codex; no inició entrenamiento ni runs de MLflow.

## Uso en siguientes sesiones

1. Abre este repositorio como carpeta de VS Code.
2. Abre el notebook de trabajo y selecciona su kernel de Colab. Para el entrenamiento
   de SciBERT utiliza A100; la T4 fue suficiente para la prueba de conexión.
3. Comprueba que Notebook MCP esté habilitado. El comando
   `Notebook MCP: Show Server Info` permite consultar su estado en VS Code.
4. En Codex, comprueba que `maia_notebook` esté habilitado en la configuración de
   servidores MCP. Si acabas de configurarlo y sus herramientas no aparecen,
   reinicia la integración de Codex o abre una nueva sesión del cliente local.
5. Antes de una corrida, verifica el notebook exacto, el kernel seleccionado y
   los parámetros. Un notebook con salidas guardadas puede tener un kernel nuevo
   sin sus variables; se comprueba el estado en vivo antes de reanudar.
6. Para un notebook abierto se utilizan las herramientas de edición, ejecución
   y guardado de Notebook MCP. Así se preservan los cambios del editor y sus salidas.
7. El notebook puede requerir autorización interactiva de Google para montar Drive
   y de Jupyter para que la extensión acceda al kernel.
8. Al terminar el trabajo, libera el runtime con `Colab: Remove Server` cuando ya
   no necesites mantener la sesión de Colab.

La conexión depende de que VS Code, la extensión y el runtime estén disponibles.
La integración MCP de un cliente local debe verificarse de nuevo si se cambia a
otro equipo o a un entorno de ejecución distinto.

## Referencias

- [Guía oficial de Colab para VS Code](https://github.com/googlecolab/colab-vscode/wiki/User-Guide).
- [Notebook MCP: instalación, herramientas y permisos](https://marketplace.visualstudio.com/items?itemName=yukhin.vscode-notebook-mcp).
- [Configuración MCP de Codex](https://developers.openai.com/codex/mcp).
