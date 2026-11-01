"""HTTP contract for the content service, run with python -m unittest discover -s tests."""
import http.client
import json
import os
import subprocess
import sys
import time
import unittest
from pathlib import Path


class ApiContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import socket
        probe = socket.socket()
        probe.bind(('127.0.0.1', 0))
        cls.port = probe.getsockname()[1]
        probe.close()
        root = Path(__file__).resolve().parents[1]
        cls.server = subprocess.Popen(
            [sys.executable, str(root / 'app' / 'server.py')],
            env={**os.environ, 'PORT': str(cls.port), 'APP_ENV': 'lab'},
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        for _ in range(100):
            try:
                cls.request('/healthz')
                break
            except OSError:
                time.sleep(0.05)
        else:
            cls.server.terminate()
            cls.server.wait()
            raise RuntimeError('API did not start')

    @classmethod
    def tearDownClass(cls):
        cls.server.terminate()
        cls.server.wait(timeout=5)

    @classmethod
    def request(cls, path):
        connection = http.client.HTTPConnection('127.0.0.1', cls.port, timeout=2)
        try:
            connection.request('GET', path)
            response = connection.getresponse()
            return response.status, json.loads(response.read())
        finally:
            connection.close()

    def test_health_and_readiness(self):
        for path in ('/healthz', '/readyz'):
            status, body = self.request(path)
            self.assertEqual(status, 200)
            self.assertEqual(body['status'], 'ok')

    def test_info_preserves_contract_and_identifies_version(self):
        status, body = self.request('/api/info')
        self.assertEqual(status, 200)
        self.assertEqual(body['service'], 'content-api')
        self.assertEqual(body['environment'], 'lab')
        self.assertTrue(body['instance'])
        self.assertEqual(body['version'], 'v2')

    def test_features_and_unknown_path(self):
        status, body = self.request('/api/features')
        self.assertEqual(status, 200)
        self.assertIn('drafts', body['features'])
        self.assertEqual(self.request('/not-found')[0], 404)

    def test_feature_details_and_unknown_feature(self):
        status, body = self.request('/api/features/drafts')
        self.assertEqual(status, 200)
        self.assertEqual(body['name'], 'drafts')
        self.assertTrue(body['description'])
        self.assertEqual(body['version'], 'v2')
        self.assertEqual(self.request('/api/features/unknown')[0], 404)


if __name__ == '__main__':
    unittest.main()
