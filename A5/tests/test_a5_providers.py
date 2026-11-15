"""Catálogo y selección de proveedor con respuestas inventadas, sin red ni claves reales."""
from pathlib import Path
import io
import json
import sys
import unittest
import urllib.error

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import a5_providers as providers
import a5_runtime as runtime


class FakeOpener:
    def __init__(self, pages):
        self.pages, self.requests = iter(pages), []
    def open(self, request, timeout):
        self.requests.append(request)
        value = next(self.pages)
        if isinstance(value, Exception):
            raise value
        return io.BytesIO(json.dumps(value).encode())


class ProvidersTests(unittest.TestCase):
    def test_provider_profiles_isolate_keys_endpoint_and_payload(self):
        for name, model, param in [('openai', 'gpt-6.1-sol', 'max_completion_tokens'),
                                   ('openai', 'gpt-6-luna', 'max_completion_tokens'),
                                   ('gemini', 'gemini-4-argon', 'max_tokens')]:
            cfg = providers.profile(name, model)
            providers.validate_config(cfg)
            cfg.update(max_output_tokens=2048, temperature=None, response_format='json_object', extra_body={})
            payload = runtime.payload_for({'messages': [{'role': 'user', 'content': 'Invented'}]}, cfg)
            self.assertIn(param, payload)
            self.assertNotIn('api_key_env', payload)
            self.assertNotIn('provider', payload)
        with self.assertRaisesRegex(ValueError, 'mezclada'):
            cfg = providers.profile('gemini', 'gemini-4-argon')
            cfg['endpoint'] = providers.PROFILES['openai']['endpoint']
            providers.validate_config(cfg)
        with self.assertRaises(ValueError): providers.profile('openai', 'gemini-4-argon')
        with self.assertRaises(ValueError): providers.profile('invalid')
        with self.assertRaisesRegex(ValueError, 'selecciona'):
            providers.validate_config(providers.profile('gemini', ''))

    def test_run_names_include_selected_model(self):
        self.assertEqual(providers.run_id('openai', 'gpt-6.1-sol', 'piloto45', '03'), 'a5_sol_piloto45_03')
        self.assertEqual(providers.run_id('openai', 'gpt-6-luna', 'piloto45', '01'), 'a5_luna_piloto45_01')
        self.assertEqual(providers.run_id('gemini', 'gemini-4-argon', 'conexion', '03'), 'a5_gemini_4_argon_conexion_03')
        with self.assertRaises(ValueError): providers.run_id('gemini', '', 'conexion', '../other')

    def test_luna_tariffs_are_selected_separately_from_sol(self):
        luna, sol = providers.OPENAI_MODELS['gpt-6-luna'], providers.OPENAI_MODELS['gpt-6.1-sol']
        self.assertEqual(luna['input_usd'], .1)
        self.assertEqual(luna['output_usd'], .5)
        self.assertAlmostEqual(luna['input_usd'] / sol['input_usd'], .05)
        self.assertAlmostEqual(luna['output_usd'] / sol['output_usd'], .05)

    def test_catalog_pages_filter_generation_and_never_put_key_in_url_or_results(self):
        opener = FakeOpener([
            {'models': [{'name': 'models/gemini-test', 'displayName': 'Invented model',
                         'supportedGenerationMethods': ['generateContent'], 'outputTokenLimit': 200},
                        {'name': 'models/embedding-test', 'supportedGenerationMethods': ['embedContent']}],
             'nextPageToken': 'next page'},
            {'models': [{'name': 'models/gemini-test-2', 'supportedGenerationMethods': ['generateContent']}]},
        ])
        rows = providers.list_gemini_models('PRIVATE_FIXTURE_KEY', opener)
        self.assertEqual(len(rows), 2)
        for request in opener.requests:
            self.assertEqual(request.get_method(), 'GET')
            self.assertNotIn('PRIVATE_FIXTURE_KEY', request.full_url)
            self.assertEqual(request.get_header('X-goog-api-key'), 'PRIVATE_FIXTURE_KEY')
            self.assertIsNone(request.data)
        self.assertIn('pageToken=next+page', opener.requests[1].full_url)
        self.assertNotIn('PRIVATE_FIXTURE_KEY', json.dumps(rows))

    def test_catalog_errors_hide_provider_body_and_bad_pagination_is_blocked(self):
        error = urllib.error.HTTPError('https://example.invalid', 403, 'PRIVATE_FIXTURE_KEY', {},
                                       io.BytesIO(b'PRIVATE_FIXTURE_KEY'))
        with self.assertRaisesRegex(RuntimeError, 'HTTP 403') as ctx:
            providers.list_gemini_models('PRIVATE_FIXTURE_KEY', FakeOpener([error]))
        self.assertNotIn('PRIVATE_FIXTURE_KEY', str(ctx.exception))
        with self.assertRaisesRegex(ValueError, 'Paginación'):
            providers.list_gemini_models('fixture', FakeOpener([
                {'models': [], 'nextPageToken': 'same'}, {'models': [], 'nextPageToken': 'same'}]))


if __name__ == '__main__': unittest.main()
