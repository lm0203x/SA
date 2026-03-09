import unittest

from app.services.ai_stock_analyzer import AIStockAnalyzer
from app import create_app


class AIStockAnalyzerNewsTestCase(unittest.TestCase):
    def test_init_does_not_reference_stock_data(self):
        app = create_app()

        with app.app_context():
            analyzer = AIStockAnalyzer()

        self.assertIsInstance(analyzer, AIStockAnalyzer)

    def _build_analyzer(self):
        analyzer = AIStockAnalyzer.__new__(AIStockAnalyzer)
        analyzer.provider = "mock"
        analyzer.config = {}
        analyzer._check_config = lambda: True
        analyzer._call_ai_api = lambda prompt: (
            '{"recommendation":"buy","reasons":["测试原因"],"confidence":0.8,"risk_level":"medium"}'
        )
        analyzer._build_analysis_prompt = lambda ts_code, stock_name, stock_data: "prompt"
        analyzer._build_market_analysis_prompt = lambda ts_code, stock_name, stock_data: "market-prompt"
        return analyzer

    def test_analyze_stock_adds_positive_news_summary(self):
        analyzer = self._build_analyzer()
        stock_data = {
            "is_watchlist": True,
            "current_price": 12.5,
            "news_list": [
                {"title": "公司签订重大合同，业绩预增", "source": "测试源"},
                {"title": "回购计划落地，市场情绪改善", "source": "测试源"},
            ],
        }

        result = analyzer.analyze_stock("000001.SZ", "平安银行", stock_data)

        self.assertEqual(result["recommendation"], "buy")
        self.assertEqual(result["news_sentiment"], "positive")
        self.assertGreater(result["news_impact_score"], 0)
        self.assertEqual(len(result["news_highlights"]), 2)
        self.assertTrue(result["news_risk_note"])
        self.assertGreater(result["confidence"], 0.8)

    def test_analyze_stock_adds_default_news_summary_when_missing(self):
        analyzer = self._build_analyzer()
        stock_data = {
            "is_watchlist": True,
            "current_price": 12.5,
            "news_list": [],
        }

        result = analyzer.analyze_stock("000001.SZ", "平安银行", stock_data)

        self.assertEqual(result["news_sentiment"], "neutral")
        self.assertEqual(result["news_impact_score"], 0)
        self.assertEqual(result["news_highlights"], [])
        self.assertTrue(result["news_risk_note"])

    def test_analyze_stock_keeps_news_summary_when_ai_call_fails(self):
        analyzer = self._build_analyzer()
        analyzer._call_ai_api = lambda prompt: (_ for _ in ()).throw(RuntimeError("timeout"))
        stock_data = {
            "is_watchlist": True,
            "current_price": 12.5,
            "news_list": [
                {"title": "公司签订重大合同，业绩预增", "source": "测试源"},
                {"title": "回购计划落地，市场情绪改善", "source": "测试源"},
            ],
        }

        result = analyzer.analyze_stock("000001.SZ", "平安银行", stock_data)

        self.assertEqual(result["recommendation"], "hold")
        self.assertEqual(result["news_sentiment"], "positive")
        self.assertGreater(result["news_impact_score"], 0)
        self.assertEqual(len(result["news_highlights"]), 2)

    def test_negative_news_reduces_confidence(self):
        analyzer = self._build_analyzer()
        stock_data = {
            "is_watchlist": True,
            "current_price": 12.5,
            "news_list": [
                {"title": "公司被处罚并遭调查，业绩下滑", "source": "测试源"},
                {"title": "重要股东减持，诉讼风险上升", "source": "测试源"},
            ],
        }

        result = analyzer.analyze_stock("000001.SZ", "平安银行", stock_data)

        self.assertEqual(result["news_sentiment"], "negative")
        self.assertLess(result["confidence"], 0.8)


if __name__ == "__main__":
    unittest.main()
