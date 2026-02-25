"""
股票资讯获取服务
通过爬虫获取新浪财经最新资讯
"""

import requests
from loguru import logger
from bs4 import BeautifulSoup
from datetime import datetime
import time


class NewsService:
    """股票资讯服务"""

    # 请求头
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    }

    @staticmethod
    def get_stock_news(ts_code, stock_name, limit=3):
        """
        获取股票相关新闻

        Args:
            ts_code: 股票代码（如 000001.SZ）
            stock_name: 股票名称
            limit: 返回数量

        Returns:
            list: 新闻列表 [{title, url, time}, ...]
        """
        news_list = []

        try:
            # 尝试获取新浪财经新闻
            news_list = NewsService._fetch_sina_news(stock_name, limit)
        except Exception as e:
            logger.warning(f"获取新浪财经资讯失败: {e}")

        # 如果新浪失败，尝试东方财富
        if not news_list:
            try:
                news_list = NewsService._fetch_eastmoney_news(stock_name, limit)
            except Exception as e:
                logger.warning(f"获取东方财富资讯失败: {e}")

        return news_list

    @staticmethod
    def _fetch_sina_news(stock_name, limit):
        """获取新浪财经新闻"""
        news_list = []

        # 新浪财经股票新闻页
        # 去掉股票名称中的非中文字符
        import re
        clean_name = re.sub(r'[^\u4e00-\u9fa5]', '', stock_name)

        url = f"https://finance.sina.com.cn/stock/"

        try:
            response = requests.get(url, headers=NewsService.HEADERS, timeout=10)
            response.encoding = 'utf-8'

            soup = BeautifulSoup(response.text, 'html.parser')

            # 查找新闻标题
            news_items = soup.select('.news-list li a')[:limit]

            for item in news_items:
                title = item.get_text(strip=True)
                href = item.get('href', '')

                if title and href:
                    news_list.append({
                        'title': title,
                        'url': href,
                        'source': '新浪财经',
                        'time': datetime.now().strftime('%Y-%m-%d %H:%M')
                    })

        except Exception as e:
            logger.error(f"新浪财经爬取失败: {e}")

        return news_list

    @staticmethod
    def _fetch_eastmoney_news(stock_name, limit):
        """获取东方财富新闻"""
        news_list = []

        import re
        clean_name = re.sub(r'[^\u4e00-\u9fa5]', '', stock_name)

        # 东方财富个股新闻
        # 这里的 ts_code 需要转换为不带后缀的纯数字
        # 例如 000001.SZ -> 000001
        code_match = re.search(r'(\d+)', stock_name)
        if code_match:
            stock_code = code_match.group(1)
            url = f"https://stock.eastmoney.com/a/{stock_code}.html"
        else:
            url = "https://stock.eastmoney.com/"

        try:
            response = requests.get(url, headers=NewsService.HEADERS, timeout=10)
            response.encoding = 'utf-8'

            soup = BeautifulSoup(response.text, 'html.parser')

            # 查找新闻
            news_items = soup.select('.news_list li a')[:limit]

            for item in news_items:
                title = item.get_text(strip=True)
                href = item.get('href', '')

                if title and len(title) > 5:  # 过滤太短的标题
                    news_list.append({
                        'title': title,
                        'url': href,
                        'source': '东方财富',
                        'time': datetime.now().strftime('%Y-%m-%d %H:%M')
                    })

        except Exception as e:
            logger.error(f"东方财富爬取失败: {e}")

        return news_list

    @staticmethod
    def format_news_for_prompt(news_list):
        """
        将新闻列表格式化为提示词格式

        Args:
            news_list: 新闻列表

        Returns:
            str: 格式化后的字符串
        """
        if not news_list:
            return "暂无最新资讯"

        formatted = []
        for i, news in enumerate(news_list, 1):
            formatted.append(f"{i}. {news.get('title', '')} ({news.get('source', '')})")

        return "\n".join(formatted)
