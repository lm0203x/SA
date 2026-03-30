import unittest
from unittest.mock import Mock, patch

from app.services.news_service import NewsService


class NewsServiceTestCase(unittest.TestCase):
    def test_build_sina_search_url_uses_exchange_symbol_page(self):
        self.assertEqual(
            NewsService._build_sina_search_url("000002.SZ"),
            "https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sz000002.phtml",
        )
        self.assertEqual(
            NewsService._build_sina_search_url("600519.SH"),
            "https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sh600519.phtml",
        )

    def test_build_eastmoney_news_url_uses_ts_code(self):
        self.assertEqual(
            NewsService._build_eastmoney_news_url("000002.SZ"),
            "https://quote.eastmoney.com/sz000002.html",
        )
        self.assertEqual(
            NewsService._build_eastmoney_news_url("600519.SH"),
            "https://quote.eastmoney.com/sh600519.html",
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

    @patch("app.services.news_service.requests.get")
    def test_fetch_sina_news_parses_stock_news_page(self, mock_get):
        mock_response = Mock()
        mock_response.text = """
        <html>
          <body>
            <a href="http://finance.sina.com.cn/realstock/company/sz000002/nc.shtml">万科A (000002.SZ)</a>
            <a href="https://finance.sina.com.cn/roll/2026-03-27/doc-test1.shtml">万科高管被要求退还薪酬</a>
            <a href="https://finance.sina.com.cn/stock/relnews/cn/2026-03-26/doc-test2.shtml">万科据悉再次寻求债券展期</a>
            <a href="https://finance.sina.com.cn/jjxw/2026-03-25/doc-test3.shtml">深圳地铁集团总经理接任万科法定代表人</a>
          </body>
        </html>
        """
        mock_get.return_value = mock_response

        result = NewsService._fetch_sina_news("000002.SZ", "万科A", limit=2)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["title"], "万科高管被要求退还薪酬")
        self.assertEqual(result[0]["source"], "新浪财经")
        self.assertEqual(result[0]["time"], "2026-03-27")
        self.assertEqual(result[1]["title"], "万科据悉再次寻求债券展期")
        self.assertEqual(result[1]["time"], "2026-03-26")


if __name__ == "__main__":
    unittest.main()
