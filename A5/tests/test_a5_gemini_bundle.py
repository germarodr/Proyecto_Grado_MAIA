"""Verifica la copia Gemini y sus rutas sin tocar la ejecución original de Luna."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import crear_notebook_gemini as generator


class GeminiBundleTests(unittest.TestCase):
    def test_generator_preserves_originals_and_refuses_overwriting(self):
        names = generator.FILES + ('A5_Modelo_Comercial_G15.ipynb',)
        before = {n: hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in names}
        with tempfile.TemporaryDirectory() as tmp:
            dest = generator.build_bundle(Path(tmp)/'Gemini')
            self.assertTrue((dest/'A5_Gemini_G15.ipynb').is_file())
            self.assertEqual(before, {n: hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in names})
            with self.assertRaisesRegex(ValueError, 'no se sobrescribe'):
                generator.build_bundle(dest)
            code = '\n'.join(c['source'] for c in json.loads((dest/'A5_Gemini_G15.ipynb').read_text(encoding='utf-8'))['cells'] if c['cell_type']=='code')
            for setting in ('PROVIDER = "gemini"', 'FINAL_TEST_MODE = False', 'ENABLE_API = False',
                            'RUN_STAGE = "conexion"', 'LIMIT_CASES = 1', 'PUBLISH_TO_SHARED_DRIVE = False'):
                self.assertIn(setting, code)

    def test_copied_preparation_writes_only_inside_gemini(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = generator.build_bundle(Path(tmp)/'Gemini')
            script = '''
from pathlib import Path
import sys,tempfile
sys.path.insert(0, sys.argv[1])
import a5_drive as drive
import a5_alignment as alignment
sys.path.append(sys.argv[2])
from test_a5_alignment import development_fixture,FakeBertTokenizer
with tempfile.TemporaryDirectory() as tmp:
    shared,own,expected=development_fixture(tmp)
    prepared=drive.prepare_tb(shared,own,expected)
    aligned=alignment.prepare_aligned(shared,own,prepared,FakeBertTokenizer(),expected_manifest_sha256=expected)
    assert Path(prepared['prepared_dir']).is_relative_to(own/'A5/Gemini/prepared')
    assert Path(aligned['prepared_dir']).is_relative_to(own/'A5/Gemini/prepared')
    assert not (own/'A5/prepared').exists()
print('ISOLATION_OK')
'''
            result = subprocess.run([sys.executable,'-B','-c',script,str(dest),str(ROOT/'tests')],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            self.assertIn('ISOLATION_OK', result.stdout)

    def test_complete_gemini_notebook_demo_is_offline_and_uses_four_connection_requests(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = generator.build_bundle(Path(tmp)/'Gemini')
            script = '''
from pathlib import Path
from unittest.mock import patch
import sys,json,tempfile,urllib.request
dest=Path(sys.argv[1])
sys.path.insert(0,str(dest))
book=json.loads((dest/'A5_Gemini_G15.ipynb').read_text(encoding='utf-8'))
ns={'__name__':'__main__'}
with tempfile.TemporaryDirectory() as tmp, patch.object(Path,'cwd',return_value=dest), patch.object(urllib.request.OpenerDirector,'open',side_effect=AssertionError('NETWORK_FORBIDDEN')):
    for cell in book['cells']:
        if cell['cell_type']!='code':continue
        exec(compile(cell['source'],'gemini-cell','exec'),ns)
        if 'DATA_DIR =' in cell['source']:
            ns['OUTPUT_DIR']=Path(tmp)/'outputs'
    assert ns['PROVIDER']=='gemini'
    assert ns['SPLIT']=='dev'
    assert ns['run']['status']=='SIMULATED'
    assert len(ns['predictions'])==4
    assert ns['ENABLE_MLFLOW_IMPORT'] is False
    assert ns['PUBLISH_TO_SHARED_DRIVE'] is False
print('DEMO_OK')
'''
            result = subprocess.run([sys.executable,'-B','-c',script,str(dest)],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            self.assertIn('DEMO_OK', result.stdout)


if __name__=='__main__': unittest.main()
