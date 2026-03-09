from types import SimpleNamespace
from unittest.mock import patch

from flask import Flask, has_app_context

from app.tasks.sync_task import start_sync_task


class ImmediateThread:
    def __init__(self, target=None, daemon=None):
        self.target = target
        self.daemon = daemon

    def start(self):
        if self.target:
            self.target()


def test_start_sync_task_runs_stock_sync_inside_app_context():
    app = Flask(__name__)
    watchlist_item = SimpleNamespace(ts_code="000001.SZ", name="Ping An")
    sync_context_flags = []

    def fake_sync_daily_data(*_args, **_kwargs):
        sync_context_flags.append(has_app_context())
        return {"success": True, "added": 1}

    def fake_sync_daily_basic(*_args, **_kwargs):
        sync_context_flags.append(has_app_context())
        return {"success": True, "added": 1}

    def fake_sync_moneyflow(*_args, **_kwargs):
        sync_context_flags.append(has_app_context())
        return {"success": True, "added": 1}

    with patch("app.tasks.sync_task.create_app", return_value=app), \
         patch("app.tasks.sync_task.threading.Thread", ImmediateThread), \
         patch("app.tasks.sync_task.Watchlist.query") as mock_query, \
         patch("app.tasks.sync_task.StockDataService.sync_daily_data", side_effect=fake_sync_daily_data), \
         patch("app.tasks.sync_task.StockDataService.sync_daily_basic", side_effect=fake_sync_daily_basic), \
         patch("app.tasks.sync_task.StockDataService.sync_moneyflow", side_effect=fake_sync_moneyflow), \
         patch("app.tasks.sync_task.Watchlist.query.update"), \
         patch("app.tasks.sync_task.db.session.commit"), \
         patch("app.tasks.sync_task.alert_trigger_engine.run_alert_check", return_value={"message": "ok"}), \
         patch("app.tasks.sync_task.socketio.emit"):
        mock_query.all.return_value = [watchlist_item]
        start_sync_task("task-1")

    assert sync_context_flags == [True, True, True]
