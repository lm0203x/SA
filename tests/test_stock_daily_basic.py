from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import patch

from flask import Flask

from app.models.stock_daily_basic import StockDailyBasic
from app.services.stock_data_service import StockDataService


class StockDailyBasicTestCase(TestCase):
    def test_to_dict_keeps_zero_values(self):
        record = StockDailyBasic(
            ts_code="000001.SZ",
            trade_date=date(2026, 3, 9),
            close=Decimal("10.76"),
            turnover_rate=Decimal("0.00"),
            volume_ratio=Decimal("0.00"),
            pe=Decimal("0.00"),
            pb=Decimal("0.00"),
            total_mv=Decimal("0.00"),
            circ_mv=Decimal("0.00"),
        )

        payload = record.to_dict()

        self.assertEqual(payload["turnover_rate"], 0.0)
        self.assertEqual(payload["volume_ratio"], 0.0)
        self.assertEqual(payload["pe"], 0.0)
        self.assertEqual(payload["pb"], 0.0)
        self.assertEqual(payload["total_mv"], 0.0)
        self.assertEqual(payload["circ_mv"], 0.0)

    def test_sync_daily_basic_updates_existing_record(self):
        app = Flask(__name__)
        existing = SimpleNamespace(
            close=None,
            turnover_rate=None,
            turnover_rate_f=None,
            volume_ratio=None,
            pe=None,
            pe_ttm=None,
            pb=None,
            ps=None,
            ps_ttm=None,
            dv_ratio=None,
            dv_ttm=None,
            total_share=None,
            float_share=None,
            free_share=None,
            total_mv=None,
            circ_mv=None,
        )
        fake_service = SimpleNamespace(
            get_daily_basic=lambda *_args, **_kwargs: [
                {
                    "trade_date": "20260309",
                    "close": 10.76,
                    "turnover_rate": 0.43,
                    "turnover_rate_f": 1.02,
                    "volume_ratio": 0.83,
                    "pe": 4.69,
                    "pe_ttm": 4.84,
                    "pb": 0.47,
                    "ps": 1.42,
                    "ps_ttm": 1.54,
                    "dv_ratio": 5.53,
                    "dv_ttm": 5.53,
                    "total_share": 1940591.82,
                    "float_share": 1940560.07,
                    "free_share": 816048.12,
                    "total_mv": 20880767.98,
                    "circ_mv": 20880426.3,
                }
            ]
        )

        with app.app_context():
            with patch.object(StockDataService, "get_active_tushare_service", return_value=fake_service), \
                 patch("app.services.stock_data_service.StockDailyBasic.query") as mock_query, \
                 patch("app.services.stock_data_service.db.session.add") as mock_add, \
                 patch("app.services.stock_data_service.db.session.commit"):
                mock_query.filter_by.return_value.first.return_value = existing

                result = StockDataService.sync_daily_basic("000001.SZ")

        self.assertTrue(result["success"])
        self.assertEqual(result["added"], 0)
        self.assertEqual(existing.volume_ratio, 0.83)
        self.assertEqual(existing.dv_ratio, 5.53)
        self.assertEqual(existing.total_mv, 20880767.98)
        mock_add.assert_not_called()
