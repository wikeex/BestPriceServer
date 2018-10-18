import unittest
from flask import current_app
from app import create_app, tokenmanager


class ServerTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    def test_app_exist(self):
        self.assertFalse(current_app is None)

    def test_app_is_testing(self):
        self.assertFalse(current_app.config.get('TESTING') is None)

    def test_get_access_token(self):
        self.assertFalse(tokenmanager.get_access_token() is None)


if __name__ == '__main__':
    unittest.main()
