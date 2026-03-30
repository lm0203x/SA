from unittest import TestCase
from unittest.mock import patch

from flask import Flask

from app.api.user_routes import get_users


class UserRoutesTestCase(TestCase):
    def test_get_users_returns_serialized_list(self):
        app = Flask(__name__)
        fake_users = [
            type('User', (), {'to_dict': lambda self=None: {'id': 1, 'username': 'admin', 'is_active': True}})(),
            type('User', (), {'to_dict': lambda self=None: {'id': 2, 'username': 'tester', 'is_active': False}})(),
        ]

        with app.app_context(), app.test_request_context('/users'):
            with patch('app.api.user_routes.User.query') as mock_query, \
                 patch('app.api.user_routes.get_request_user', return_value=None), \
                 patch('app.api.user_routes.OperationLogService.record'):
                mock_query.order_by.return_value.all.return_value = fake_users
                response = get_users()

        payload = response.get_json()
        self.assertTrue(payload['success'])
        self.assertEqual(len(payload['data']), 2)
        self.assertEqual(payload['data'][0]['username'], 'admin')
