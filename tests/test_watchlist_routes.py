from datetime import date, datetime
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import patch

from flask import Flask

from app.api.watchlist_routes import get_watchlist


class WatchlistRoutesTestCase(TestCase):
    def test_get_watchlist_returns_latest_daily_summary_fields(self):
        app = Flask(__name__)
        watchlist_item = SimpleNamespace(
            id=1,
            ts_code="000001.SZ",
            symbol="000001",
            name="平安银行",
            note="观察",
            added_at=datetime(2026, 3, 9, 10, 0, 0),
            last_sync=datetime(2026, 3, 9, 10, 30, 0),
            push_enabled=False,
            push_time=None,
            last_push_at=None,
            to_dict=lambda: {
                "id": 1,
                "ts_code": "000001.SZ",
                "symbol": "000001",
                "name": "平安银行",
                "note": "观察",
                "added_at": "2026-03-09T10:00:00",
                "last_sync": "2026-03-09T10:30:00",
                "push_enabled": False,
                "push_time": None,
                "last_push_at": None,
            },
        )
        latest_daily = SimpleNamespace(close=10.76, pct_chg=-0.55, trade_date=date(2026, 3, 8))

        with app.app_context(), app.test_request_context("/watchlist"):
            with patch("app.api.watchlist_routes.Watchlist.query") as mock_watchlist_query, \
                 patch("app.api.watchlist_routes.StockDailyHistory.query") as mock_daily_query:
                mock_watchlist_query.order_by.return_value.all.return_value = [watchlist_item]
                mock_daily_query.filter_by.return_value.order_by.return_value.first.return_value = latest_daily

                response = get_watchlist()

        payload = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(payload["success"])
        self.assertEqual(payload["data"][0]["latest_close"], 10.76)
        self.assertEqual(payload["data"][0]["latest_pct_chg"], -0.55)
        self.assertEqual(payload["data"][0]["latest_trade_date"], "2026-03-08")
