"""
股票资讯获取服务
"""

from datetime import datetime
import re

import requests
from bs4 import BeautifulSoup
from loguru import logger


class NewsService:
    """股票资讯服务"""

    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    }

    @staticmethod
    def _normalize_stock_code(ts_code):
        if not ts_code:
            return ""
        return ts_code.split(".")[0].strip()

    @staticmethod
    def _normalize_market_prefix(ts_code):
        if not ts_code or "." not in ts_code:
            return ""
        market = ts_code.split(".")[-1].strip().upper()
        if market == "SZ":
            return "sz"
        if market == "SH":
            return "sh"
        return ""

    @staticmethod
    def _build_sina_search_url(ts_code):
        stock_code = NewsService._normalize_stock_code(ts_code)
        market_prefix = NewsService._normalize_market_prefix(ts_code)
        if not stock_code or not market_prefix:
            return "https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/"
        return (
            "https://vip.stock.finance.sina.com.cn/corp/go.php/"
            f"vCB_AllNewsStock/symbol/{market_prefix}{stock_code}.phtml"
        )

    @staticmethod
    def _build_eastmoney_news_url(ts_code):
        stock_code = NewsService._normalize_stock_code(ts_code)
        market_prefix = NewsService._normalize_market_prefix(ts_code)
        if not stock_code or not market_prefix or not re.fullmatch(r"\d{6}", stock_code):
            return "https://stock.eastmoney.com/"
        return f"https://quote.eastmoney.com/{market_prefix}{stock_code}.html"

    @staticmethod
    def _extract_publish_date(href):
        if not href:
            return datetime.now().strftime("%Y-%m-%d %H:%M")
        match = re.search(r"/(\d{4}-\d{2}-\d{2})/", href)
        if match:
            return match.group(1)
        return datetime.now().strftime("%Y-%m-%d %H:%M")

    @staticmethod
    def get_stock_news(ts_code, stock_name, limit=3):
        news_list = []

        try:
            news_list = NewsService._fetch_sina_news(ts_code, stock_name, limit)
        except Exception as exc:
            logger.warning(f"获取新浪财经资讯失败: {exc}")

        if not news_list:
            try:
                news_list = NewsService._fetch_eastmoney_news(ts_code, stock_name, limit)
            except Exception as exc:
                logger.warning(f"获取东方财富资讯失败: {exc}")

        return news_list

    @staticmethod
    def _fetch_sina_news(ts_code, stock_name, limit):
        news_list = []
        clean_name = re.sub(r"[^\u4e00-\u9fa5]", "", stock_name or "")
        url = NewsService._build_sina_search_url(ts_code)

        try:
            response = requests.get(url, headers=NewsService.HEADERS, timeout=10)
            response.encoding = "gbk"
            soup = BeautifulSoup(response.text, "html.parser")

            for item in soup.find_all("a", href=True):
                title = item.get_text(strip=True)
                href = item.get("href", "")
                if not title or len(title) <= 8 or "javascript:" in href:
                    continue
                if not href.startswith("http"):
                    continue
                if "finance.sina.com.cn" not in href:
                    continue
                if any(
                    token in href for token in (
                        "/realstock/company/",
                        "vip.stock.finance.sina.com.cn",
                        "/stock/index.shtml",
                        "/stock/hkstock/index.shtml",
                        "/stock/usstock/index.shtml",
                        "/stock/newstock/index.shtml",
                    )
                ):
                    continue
                if clean_name and clean_name not in title:
                    continue

                news_list.append({
                    "title": title,
                    "url": href,
                    "source": "新浪财经",
                    "time": NewsService._extract_publish_date(href),
                })
                if len(news_list) >= limit:
                    break
        except Exception as exc:
            logger.error(f"新浪财经抓取失败: url={url}, error={exc}")

        return news_list

    @staticmethod
    def _fetch_eastmoney_news(ts_code, stock_name, limit):
        news_list = []
        clean_name = re.sub(r"[^\u4e00-\u9fa5]", "", stock_name or "")
        stock_code = NewsService._normalize_stock_code(ts_code)
        url = NewsService._build_eastmoney_news_url(ts_code)

        try:
            response = requests.get(url, headers=NewsService.HEADERS, timeout=10)
            response.encoding = "utf-8"
            soup = BeautifulSoup(response.text, "html.parser")

            selectors = [".news_list li a", ".articleh li a", 'a[href*="eastmoney.com"]']
            news_items = []
            for selector in selectors:
                news_items = soup.select(selector)
                if news_items:
                    break

            for item in news_items:
                title = item.get_text(strip=True)
                href = item.get("href", "")
                if not title or len(title) <= 5:
                    continue
                if clean_name and clean_name not in title and stock_code not in title:
                    continue

                news_list.append({
                    "title": title,
                    "url": href,
                    "source": "东方财富",
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                })
                if len(news_list) >= limit:
                    break
        except Exception as exc:
            logger.error(f"东方财富抓取失败: url={url}, error={exc}")

        return news_list

    @staticmethod
    def format_news_for_prompt(news_list):
        if not news_list:
            return "暂无最新资讯"

        formatted = []
        for index, news in enumerate(news_list, 1):
            formatted.append(f"{index}. {news.get('title', '')} ({news.get('source', '')})")

        return "\n".join(formatted)
