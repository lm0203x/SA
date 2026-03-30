from unittest import TestCase
from unittest.mock import patch

from flask import Flask

from app.services.operation_log_service import OperationLogService


class OperationLogServiceTestCase(TestCase):
    def test_record_uses_request_context_metadata(self):
        app = Flask(__name__)
        fake_user = type('User', (), {'id': 7, 'username': 'admin'})()

        with app.test_request_context(
            '/api/watchlist',
            method='POST',
            headers={'User-Agent': 'pytest-agent', 'X-Forwarded-For': '1.2.3.4'},
        ):
            with patch('app.services.operation_log_service.db.session') as mock_session:
                log_item = OperationLogService.record(
                    module='watchlist',
                    action_type='create',
                    action_name='添加自选股',
                    user=fake_user,
                    commit=False,
                )

        self.assertEqual(log_item.user_id, 7)
        self.assertEqual(log_item.username, 'admin')
        self.assertEqual(log_item.request_path, '/api/watchlist')
        self.assertEqual(log_item.request_method, 'POST')
        self.assertEqual(log_item.ip, '1.2.3.4')
        self.assertEqual(log_item.user_agent, 'pytest-agent')
        mock_session.add.assert_called_once()
