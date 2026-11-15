"""Crea una copia Gemini independiente sin reescribir el notebook o auxiliares de Luna."""
from copy import deepcopy
from pathlib import Path
import hashlib
import json

import crear_notebook

ROOT = Path(__file__).resolve().parent
FILES = ('a5_runtime.py', 'a5_drive.py', 'a5_alignment.py', 'a5_providers.py',
         'a5_tracking.py', 'prompt_v11_1_snapshot.json')


def replace_once(source, old, new):
    if source.count(old) != 1:
        raise ValueError('La plantilla cambió; revisar la copia Gemini antes de regenerar: ' + old[:70])
    return source.replace(old, new, 1)


def build_bundle(destination=None, *, recover_incomplete=False):
    destination = Path(destination) if destination is not None else ROOT / 'Gemini'
    if destination.exists() and any(destination.iterdir()) and not recover_incomplete:
        raise ValueError('La carpeta Gemini ya contiene archivos: no se sobrescribe una copia potencialmente en uso')
    if recover_incomplete and destination.exists() and any(p.name not in FILES or not p.is_file() for p in destination.iterdir()):
        raise ValueError('Solo se recupera una copia incompleta que todavía no contiene un notebook')
    hashes, helper_contents = {}, {}
    for name in FILES:
        content = (ROOT / name).read_text(encoding='utf-8')
        if name in {'a5_drive.py', 'a5_alignment.py'}:
            content = replace_once(content, '/ "A5" / "prepared"', '/ "A5" / "Gemini" / "prepared"')
        helper_contents[name] = content
    cells = deepcopy(crear_notebook.CELLS)
    cells[0]['source'] = '''# A5 · Gemini · consulta de modelos y pruebas independientes

Usa una segunda sesión de Colab. Esta copia tiene código, preparación y resultados
propios en `Mi unidad/MAIA_TESIS/A5/Gemini/`; no actualices los auxiliares de Luna
mientras su evaluación esté ejecutándose.

Primero ejecuta 1, 2, 3, 4 y 4.1 para consultar el catálogo. No necesitas 3.1 ni
3.2 para esa consulta. Mantén ENABLE_API=False. En 4.1 activa
QUERY_GEMINI_MODELS=True e introduce la clave Gemini en el campo oculto.
El listado no confirma saldo ni cuota de inferencia.

Después elegiremos modelo y tarifas, haremos conexión con un caso y cuatro
condiciones, y luego el piloto de 45 casos con las mismas entradas/prompts de
Sol y Luna. T_B no se evalúa en esta etapa. El modelo y sus precios quedan vacíos
hasta revisar el catálogo. No se incluyen datos ni claves en esta carpeta.

El bloque 15 queda desactivado. Su ejecución deberá coordinarse con Luna para
añadir ambos resultados al mismo historial, de uno en uno. Leer LEEME_Gemini.md.
'''
    for cell in cells:
        if cell['cell_type'] != 'code':
            continue
        s = cell['source']
        if 'A5_DIR = Path.cwd()' in s:
            start = s.index('# AQUÍ:')
            end = s.index('for name in ')
            s = (s[:start] + '# Carpeta exclusiva de Gemini. No cargar el código de la raíz A5.\n'
                 'A5_DIR = Path("/content/drive/MyDrive/MAIA_TESIS/A5/Gemini") if USE_DRIVE else Path.cwd()\n'
                 + s[end:])
        if 'FINAL_TEST_MODE = True' in s:
            s = replace_once(s, 'FINAL_TEST_MODE = True', 'FINAL_TEST_MODE = False')
            s = replace_once(s, 'RESULTS_ROOT / "A5" if USE_DRIVE else A5_DIR',
                             'RESULTS_ROOT / "A5" / "Gemini" if USE_DRIVE else A5_DIR')
            s = s.replace('Luna, cuatro condiciones, mismos prompts y banco revisado del piloto.',
                          'Gemini todavía en desarrollo: no se congela ni se evalúa T_B.')
        if 'PROVIDER = "openai"' in s:
            s = replace_once(s, 'PROVIDER = "openai"', 'PROVIDER = "gemini"')
            s = replace_once(s, 'RUN_STAGE = "test" if FINAL_TEST_MODE else "piloto45"', 'RUN_STAGE = "conexion"')
            s = replace_once(s,
                'BUDGET_USD = None  # AQUÍ: None = sin tope local de gasto, según lo autorizado. No activa recargas del proveedor.',
                'BUDGET_USD = 0.25  # AQUÍ: propuesta para conexión; revisar tras elegir modelo y tarifas.')
            s = replace_once(s,
                'RESERVE_PER_ATTEMPT_USD = 0.01 if MODEL_ID == "gpt-6-luna" else 0.0',
                'RESERVE_PER_ATTEMPT_USD = 0.15')
        if 'LIMIT_CASES = None if SPLIT == "test" else 45' in s:
            s = replace_once(s, 'LIMIT_CASES = None if SPLIT == "test" else 45',
                             'LIMIT_CASES = 1  # Después de la conexión: 45 para el piloto. Nunca limitar T_B final.')
        if 'TRACKING_A5_DIR = Path(' in s:
            s = replace_once(s, 'TRACKING_A5_DIR = Path("/content/drive/MyDrive/MAIA_TESIS/A5")',
                             'TRACKING_CODE_DIR = Path("/content/drive/MyDrive/MAIA_TESIS/A5/Gemini")\n'
                             'TRACKING_A5_DIR = TRACKING_CODE_DIR.parent')
            s = replace_once(s, 'TRACKING_A5_DIR / "outputs/a5_sol_piloto45_02"',
                             'TRACKING_CODE_DIR / "outputs/REEMPLAZAR_RUN_GEMINI"')
            if s.count('str(TRACKING_A5_DIR)') != 2:
                raise ValueError('Revisar importación de tracking en la plantilla')
            s = s.replace('str(TRACKING_A5_DIR)', 'str(TRACKING_CODE_DIR)')
            s = replace_once(s, 'TRACKING_A5_DIR / "a5_tracking.py"', 'TRACKING_CODE_DIR / "a5_tracking.py"')
            s = replace_once(s, 'PUBLISH_TO_SHARED_DRIVE = True', 'PUBLISH_TO_SHARED_DRIVE = False')
        cell['source'] = s
    for i, cell in enumerate(cells):
        cell['id'] = f'gemini-cell-{i:02d}'
        if cell['cell_type'] == 'code':
            compile(cell['source'], cell['id'], 'exec')
            cell['outputs'], cell['execution_count'] = [], None
    book = {'cells': cells, 'metadata': {'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'},
                                       'language_info': {'name': 'python', 'version': '3.11'}},
            'nbformat': 4, 'nbformat_minor': 5}
    destination.mkdir(parents=True, exist_ok=True)
    for name, content in helper_contents.items():
        if recover_incomplete and (destination / name).exists() and (destination / name).read_text(encoding='utf-8') != content:
            raise ValueError('El auxiliar parcial fue modificado; no se sobrescribe: ' + name)
        (destination / name).write_text(content, encoding='utf-8')
        hashes[name] = hashlib.sha256((destination / name).read_bytes()).hexdigest()
    (destination / 'A5_Gemini_G15.ipynb').write_text(json.dumps(book, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    (destination / '.gitignore').write_text('data/\nprepared/\noutputs/\ntracking/\n__pycache__/\n.ipynb_checkpoints/\n.env\n.env.*\n*.log\n', encoding='utf-8')
    (destination / 'bundle_manifest.json').write_text(json.dumps({'purpose': 'Gemini isolated development; no API calls',
        'helper_sha256': hashes, 'source': 'A5 helpers copied without modifying originals',
        'private_drive_root': '/content/drive/MyDrive/MAIA_TESIS/A5/Gemini',
        'shared_tracking_import': 'A5/tracking/snapshots; sequential registration only'}, indent=2)+'\n', encoding='utf-8')
    return destination


if __name__ == '__main__':
    print('Copia independiente creada:', build_bundle())
