"""Recorte y selección: datos inventados; comprobación opcional con tokenizer real en caché."""
from pathlib import Path
import ast
import hashlib
import importlib.util
import json
import re
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import a5_alignment as alignment
import a5_drive as drive
import a5_runtime as runtime
from test_a5_drive import fixture


class FakeBertTokenizer:
    cls_token_id, sep_token_id, unk_token_id = 101, 102, 100
    def __init__(self):
        self.vocab = {m: 200 + i for i, m in enumerate(alignment.MARKERS)}
        self.inverse = {v: k for k, v in self.vocab.items()}
    def num_special_tokens_to_add(self, pair=True): return 3
    def convert_tokens_to_ids(self, token): return self.vocab.get(token, self.unk_token_id)
    def get_vocab(self): return dict(self.vocab)
    def encode(self, text, add_special_tokens=False):
        tokens = re.findall(r'\[\[TARGET\]\]|\[(?:CITE|FORMULA|FIGURE|TABLE)\]|\w+|[^\w\s]', text)
        result = []
        for token in tokens:
            if token not in alignment.MARKERS: token = token.lower()
            if token not in self.vocab:
                key = 1000 + int(hashlib.sha256(token.encode()).hexdigest()[:12], 16)
                self.vocab[token] = key; self.inverse[key] = token
            result.append(self.vocab[token])
        return result
    def decode(self, ids, **kwargs): return ' '.join(self.inverse[x] for x in ids)


def reference_functions():
    nb = json.loads((ROOT / 'Resultado_Sebas/SciBERT_Entrenamiento_Final.ipynb').read_text(encoding='utf-8'))
    defs = []
    for c in nb['cells']:
        if c['cell_type'] != 'code': continue
        source = ''.join(c['source']) if isinstance(c['source'], list) else c['source']
        for node in ast.parse(source).body:
            if isinstance(node, ast.FunctionDef) and node.name in ('fair_caps', 'encode_example_reference'):
                defs.append(node)
    if {d.name for d in defs} != {'fair_caps', 'encode_example_reference'}: raise AssertionError('Referencia no encontrada')
    namespace = {}
    exec(compile(ast.Module(body=defs, type_ignores=[]), 'sebas-reference-functions-only', 'exec'), namespace)
    return namespace


def development_fixture(root):
    shared, own, expected, bp = fixture(root)
    gold = list(drive.rows(shared / 'a3/test_set_gold.jsonl'))
    texts = list(drive.rows(bp))
    for i, label in enumerate(runtime.LABELS):
        for j in range(8):
            key = f'A{i}-{j}|1|10-20|C{i}-{j}'
            gold.append({'inst_key': key, 'set': 'A', 'in_eval': True, 'source': 'agreement', 'gold_primary': label})
            texts.append({'inst_key': key, 'context': 'Prior text. We use [[TARGET]] in our experiment.',
                          'cited_title': 'Invented Title', 'cited_abstract': 'Invented Abstract',
                          'top3': [{'text': 'Passage ' * 300, 'section': 'Methods'} for _ in range(3)]})
    gp = shared / 'a3/test_set_gold.jsonl'
    gp.write_text(''.join(json.dumps(r) + '\n' for r in gold), encoding='utf-8')
    bp.write_text(''.join(json.dumps(r) + '\n' for r in texts), encoding='utf-8')
    mp = shared / 'a3/manifest_metrics.json'
    manifest = {'packages': len(gold), 'in_eval': {'A': 73, 'B': 1}, 'unclear': {'A': 0, 'B': 1},
                'files': {gp.name: drive.sha256(gp)}}
    mp.write_text(json.dumps(manifest), encoding='utf-8')
    return shared, own, drive.sha256(mp)


class AlignmentTests(unittest.TestCase):
    def test_decoded_target_is_separate_from_surrounding_sentences(self):
        case = {'inst_key': 'A|1|1-2|B', 'citing_id': 'A', 'cited_id': 'B', 'split': 'dev',
                'context': 'Prior work. Following Smith et al. [CITE], we use [[TARGET]]. Other work.',
                'target_sentence': 'Following Smith et al. [CITE], we use [[TARGET]].',
                'cited_title': 'Title', 'cited_abstract': 'Abstract'}
        aligned, _ = alignment.align_case(case, FakeBertTokenizer())
        view = aligned['a4_inputs']['base']
        self.assertEqual(view['target_sentence'], 'following smith et al . [CITE] , we use [[TARGET]] .')
        self.assertIn(view['target_sentence'], view['context'])

    def test_review_exclusion_replaces_candidate_without_changing_human_gold(self):
        with tempfile.TemporaryDirectory() as root:
            shared, own, expected = development_fixture(root)
            gold = drive.inspect_drive(shared, own, expected)['gold']
            original = json.dumps(gold, sort_keys=True)
            bank, _, _ = alignment.select_development(gold)
            rejected = next(r['inst_key'] for r in bank if r['gold_primary'] == 'Application')
            new_bank, pilot, audit = alignment.select_development(gold, excluded_keys=[rejected])
            self.assertNotIn(rejected, [r['inst_key'] for r in new_bank + pilot])
            self.assertEqual(len(new_bank), 9)
            self.assertEqual(len(pilot), 45)
            self.assertEqual({r['gold_primary'] for r in new_bank}, set(runtime.LABELS))
            self.assertEqual(audit['development_excluded_keys'], [rejected])
            self.assertEqual(original, json.dumps(gold, sort_keys=True))
            with self.assertRaisesRegex(ValueError, 'T_A'):
                alignment.select_development(gold, excluded_keys=['2003.00003|2|10-20|2004.00004'])

    def test_policy_matches_reference_on_long_inputs_and_target_positions(self):
        ref = reference_functions()['encode_example_reference']; tok = FakeBertTokenizer()
        for prefix in (0, 10, 190, 700):
            case = {'context': 'previous ' * prefix + 'We use [[TARGET]]. ' + 'later ' * 500,
                    'title': 'title ' * 100, 'abstract': 'abstract ' * 600,
                    'chunks': [{'text': 'passage ' * n, 'section': 'Methods'} for n in (50, 400, 700)]}
            for rep in ('base',):
                actual = alignment.encode_example_reference(case, rep, tok)
                self.assertEqual(actual, ref(case, rep, tok))
                self.assertLessEqual(len(actual[0]['input_ids']), 512)
                self.assertEqual(actual[0]['input_ids'].count(tok.convert_tokens_to_ids('[[TARGET]]')), 1)

    def test_aligned_text_does_not_add_unseen_original_sentence(self):
        tok = FakeBertTokenizer()
        source = {'inst_key': 'A|1|1-2|B', 'citing_id': 'A', 'cited_id': 'B', 'split': 'test',
                  'context': 'Capitalized ' * 400 + '[[TARGET]] ' + 'Original ' * 400,
                  'cited_title': 'Title', 'cited_abstract': 'Abstract',
                  'top3': [{'text': 'passage ' * 400, 'section': 'Methods'} for _ in range(3)]}
        source['target_sentence'] = source['context']
        aligned, audit = alignment.align_case(source, tok)
        runtime.normalize_cases([aligned], 'test')
        for rep in ('base',):
            view = runtime.input_view(aligned, rep, True)
            self.assertIn(view['target_sentence'], view['context'])
            self.assertNotEqual(view['context'], source['context'])
            self.assertNotIn(source['context'], view['context'])
        self.assertEqual(len(audit), 1)
        self.assertEqual(set(aligned['a4_inputs']), {'base'})
        self.assertNotIn('top3', aligned)

    def test_selection_uses_only_ta_and_is_disjoint_deterministic(self):
        with tempfile.TemporaryDirectory() as root:
            shared, own, expected = development_fixture(root)
            inspected = drive.inspect_drive(shared, own, expected)
            a = alignment.select_development(inspected['gold'])
            b = alignment.select_development(list(reversed(inspected['gold'])))
            self.assertEqual(a, b)
            bank, pilot, summary = a
            self.assertEqual(len(bank), 9); self.assertEqual(len(pilot), 45)
            self.assertEqual(set(r['gold_primary'] for r in bank), set(runtime.LABELS))
            self.assertTrue(all(r['set'] == 'A' for r in bank + pilot))
            self.assertFalse({p for r in bank for p in alignment.docs(r)} & {p for r in pilot for p in alignment.docs(r)})
            bad = [r for r in inspected['gold'] if r['gold_primary'] != 'Evidence']
            with self.assertRaisesRegex(ValueError, 'Evidence'): alignment.select_development(bad)

    def test_complete_private_pipeline_with_mock_tokenizer(self):
        with tempfile.TemporaryDirectory() as root:
            shared, own, expected = development_fixture(root)
            prepared = drive.prepare_tb(shared, own, expected)
            before = {str(p): drive.sha256(p) for p in shared.rglob('*') if p.is_file()}
            tok = FakeBertTokenizer()
            aligned = alignment.prepare_aligned(shared, own, prepared, tok, expected_manifest_sha256=expected)
            paths = aligned['paths']
            self.assertEqual(len(runtime.read_jsonl(paths['cases'])), 45)
            self.assertEqual(len(runtime.read_jsonl(paths['examples'])), 9)
            cases = runtime.normalize_cases(runtime.read_jsonl(paths['cases']), 'dev')
            examples = runtime.normalize_cases(runtime.read_jsonl(paths['examples']), 'dev')
            runtime.audit_isolation(cases, examples, runtime.read_jsonl(paths['heldout']), runtime.read_jsonl(paths['exclusions']), 'V2')
            self.assertTrue(all('a4_inputs' in r for r in cases + examples))
            self.assertFalse(any('gold_primary' in r for r in runtime.read_jsonl(paths['cases'])))
            again = alignment.prepare_aligned(shared, own, prepared, tok, expected_manifest_sha256=expected)
            self.assertEqual(aligned['fingerprint'], again['fingerprint'])
            self.assertEqual(before, {str(p): drive.sha256(p) for p in shared.rglob('*') if p.is_file()})

    def test_real_cached_scibert_matches_reference_and_preserves_marker(self):
        if importlib.util.find_spec('transformers') is None:
            self.skipTest('Transformers no instalado; prueba real se ejecuta con el entorno científico local')
        cached = Path.home() / '.cache/huggingface/hub/models--allenai--scibert_scivocab_uncased/snapshots' / alignment.MODEL_REVISION
        if not (cached / 'vocab.txt').is_file(): self.skipTest('No hay vocabulario local; no se descarga en pruebas')
        tok = alignment.load_tokenizer(cached)
        ref = reference_functions()['encode_example_reference']
        data = json.loads((ROOT / 'Resultado_Sebas/Ejemplos_Reales_Entradas_Salidas.json').read_text(encoding='utf-8'))
        examples = [r['normalized_text_record'] for r in data['cases']]
        examples.append({'context': 'Long context. ' * 200 + 'We use [[TARGET]]. ' + 'Following text. ' * 200,
                         'title': 'Long scientific title ' * 50, 'abstract': 'A scientific abstract. ' * 400,
                         'chunks': [{'text': 'Scientific passage. ' * 400, 'section': 'Methods'} for _ in range(3)]})
        for ex in examples:
            for rep in ('base',):
                actual = alignment.encode_example_reference(ex, rep, tok)
                self.assertEqual(actual, ref(ex, rep, tok))
            c = {'inst_key': 'source|1|1-2|target', 'citing_id': 'source', 'cited_id': 'target', 'split': 'test',
                 'context': ex['context'], 'target_sentence': drive.target_sentence(ex['context']),
                 'cited_title': ex['title'], 'cited_abstract': ex['abstract'], 'top3': ex['chunks']}
            aligned, _ = alignment.align_case(c, tok)
            runtime.normalize_cases([aligned], 'test')

    def test_alignment_rejects_fragment_variant(self):
        tok = FakeBertTokenizer()
        example = {'context': 'We use [[TARGET]].', 'title': 'Title', 'abstract': 'Summary',
                   'chunks': [{'text': 'Never use', 'section': 'Never use'}]}
        with self.assertRaisesRegex(ValueError, 'base'):
            alignment.encode_example_reference(example, 'fragmentos', tok)


if __name__ == '__main__': unittest.main()
