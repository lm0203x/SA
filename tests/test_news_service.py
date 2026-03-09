import unittest
from unittest.mock import patch

from app.services.news_service import NewsService


class NewsServiceTestCase(unittest.TestCase):
    def test_build_sina_search_url_uses_full_ts_code(self):
        self.assertEqual(
            NewsService._build_sina_search_url("000002.SZ"),
            "https://search.sina.com.cn/?q=000002.SZ&range=all&c=news&sort=time",
        )

    def test_build_eastmoney_news_url_uses_ts_code(self):
        self.assertEqual(
            NewsService._build_eastmoney_news_url("000002.SZ"),
            "https://stock.eastmoney.com/a/000002.html",
        )
        self.assertEqual(
            NewsService._build_eastmoney_news_url("600519.SH"),
            "https://stock.eastmoney.com/a/600519.html",
        )

    def test_build_eastmoney_news_url_falls_back_for_invalid_code(self):
        self.assertEqual(
            NewsService._build_eastmoney_news_url("VANKE"),
            "https://stock.eastmoney.com/",
        )
        self.assertEqual(
            NewsService._build_eastmoney_news_url(""),
            "https://stock.eastmoney.com/",
        )

    @patch.object(NewsService, "_fetch_eastmoney_news", return_value=[{"title": "news"}])
    @patch.object(NewsService, "_fetch_sina_news", return_value=[])
    def test_get_stock_news_falls_back_to_eastmoney_with_ts_code(self, mock_sina, mock_eastmoney):
        result = NewsService.get_stock_news("000002.SZ", "万科A", limit=3)

        self.assertEqual(result, [{"title": "news"}])
        mock_sina.assert_called_once_with("000002.SZ", "万科A", 3)
        mock_eastmoney.assert_called_once_with("000002.SZ", "万科A", 3)


if __name__ == "__main__":
    unittest.main()
