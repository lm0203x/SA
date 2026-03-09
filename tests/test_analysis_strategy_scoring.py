import unittest

from app.api.ai_routes import _score_metrics_by_strategy_type


class AnalysisStrategyScoringTestCase(unittest.TestCase):
    def test_different_strategy_types_use_different_scoring_rules(self):
        metrics = {
            "close": 10.5,
            "pct_chg": -1.2,
            "volume_ratio": 0.8,
            "turnover_rate": 2.5,
            "pb": 0.7,
            "pe": 8.0,
            "net_mf_amount": 5000.0,
        }

        trend_result = _score_metrics_by_strategy_type(metrics, "trend")
        fund_flow_result = _score_metrics_by_strategy_type(metrics, "fund_flow")
        value_result = _score_metrics_by_strategy_type(metrics, "value")

        self.assertEqual(trend_result["signal"], "avoid")
        self.assertEqual(fund_flow_result["signal"], "watch")
        self.assertEqual(value_result["signal"], "buy")
        self.assertLess(trend_result["score"], fund_flow_result["score"])
        self.assertLess(fund_flow_result["score"], value_result["score"])


if __name__ == "__main__":
    unittest.main()
