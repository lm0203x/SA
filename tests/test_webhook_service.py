import types
from unittest.mock import patch

from app.services.webhook_service import WebhookService


class DummyConfig:
    def __init__(self, retry_count=3, retry_interval=0):
        self.retry_count = retry_count
        self.retry_interval = retry_interval
        self.webhook_name = "dummy"
        self.webhook_type = "webhook"


def test_send_with_retry_succeeds_after_retry():
    service = WebhookService()
    attempts = []

    def fake_sender(config, *_args, **_kwargs):
        attempts.append(1)
        return {"success": len(attempts) >= 2, "error_message": "fail"}

    with patch("app.services.webhook_service.time.sleep"):
        result = service._send_with_retry(fake_sender, DummyConfig(retry_count=3, retry_interval=0))

    assert result["success"] is True
    assert len(attempts) == 2


def test_send_with_retry_returns_error_after_exhaustion():
    service = WebhookService()

    def always_fail(_config, *_args, **_kwargs):
        return {"success": False, "error_message": "fail"}

    with patch("app.services.webhook_service.time.sleep"):
        result = service._send_with_retry(always_fail, DummyConfig(retry_count=2, retry_interval=0))

    assert result["success"] is False
    assert "已重试2次" in result["error_message"]


def test_process_response_parses_platform_success():
    service = WebhookService()

    response = types.SimpleNamespace(
        status_code=200,
        content=b"{}",
        json=lambda: {"errcode": 0, "errmsg": "ok"},
    )

    result = service._process_response(response, "钉钉")

    assert result["success"] is True
    assert "消息发送成功" in result["message"]


def test_process_response_handles_http_error():
    service = WebhookService()

    response = types.SimpleNamespace(status_code=500, content=b"error", json=lambda: {})
    result = service._process_response(response, "通用Webhook")

    assert result["success"] is False
    assert "HTTP错误: 500" in result["error_message"]
