"""
AI 分析推送服务
定时对自选股进行 AI 分析并推送到 Webhook
"""

import requests
from loguru import logger
from datetime import datetime
from app.extensions import db
from app.models.watchlist import Watchlist
from app.models.webhook_config import WebhookConfig
from app.services.ai_stock_analyzer import AIStockAnalyzer
from app.services.news_service import NewsService
from app.services.stock_service import StockService


class AnalysisPushService:
    """AI 分析推送服务"""

    @staticmethod
    def push_analysis(watchlist_item):
        """
        对单个自选股进行 AI 分析并推送

        Args:
            watchlist_item: Watchlist 模型实例

        Returns:
            dict: 推送结果
        """
        ts_code = watchlist_item.ts_code
        stock_name = watchlist_item.name or ts_code

        logger.info(f"开始分析推送: {ts_code} {stock_name}")

        # 1. 获取股票数据
        stock_data = AnalysisPushService._get_stock_data(ts_code)

        # 2. 获取最新资讯
        logger.info(f"[AI推送] 正在获取 {ts_code} 的最新资讯...")
        news_list = NewsService.get_stock_news(ts_code, stock_name, limit=3)
        logger.info(f"[AI推送] 获取到 {len(news_list)} 条资讯: {[n.get('title', '')[:20] for n in news_list]}")
        news_text = NewsService.format_news_for_prompt(news_list)

        # 3. 构建提示词
        prompt = AnalysisPushService._build_prompt(ts_code, stock_name, stock_data, news_text)

        # 4. 调用 AI 分析
        analyzer = AIStockAnalyzer()
        # 构造符合 analyze_stock 格式的数据
        stock_data['is_watchlist'] = True
        result = analyzer.analyze_stock(ts_code, stock_name, stock_data)

        # 5. 格式化 AI 分析结果
        recommendation = result.get('recommendation', 'hold')
        reasons = result.get('reasons', [])
        risk_level = result.get('risk_level', 'medium')
        confidence = result.get('confidence', 0.0)

        # 构建可读的分析文本
        recommendation_text = {'buy': '买入', 'sell': '卖出', 'hold': '持有'}.get(recommendation, '持有')
        risk_text = {'low': '低', 'medium': '中', 'high': '高'}.get(risk_level, '中')

        analysis_content = f"推荐: {recommendation_text}\n"
        analysis_content += f"风险等级: {risk_text}\n"
        analysis_content += f"置信度: {confidence:.0%}\n\n"
        analysis_content += "分析理由:\n"
        for i, reason in enumerate(reasons, 1):
            analysis_content += f"{i}. {reason}\n"

        push_result = AnalysisPushService._push_to_webhook(
            ts_code, stock_name, analysis_content, news_list
        )

        # 6. 更新最后推送时间
        watchlist_item.last_push_at = datetime.utcnow()
        db.session.commit()

        logger.info(f"推送完成: {ts_code}, 结果: {push_result}")
        return push_result

    @staticmethod
    def _format_message_by_type(webhook, message):
        """
        根据 webhook 类型格式化消息

        Args:
            webhook: WebhookConfig 实例
            message: 原始消息字典

        Returns:
            dict: 格式化后的消息体
        """
        webhook_type = webhook.webhook_type

        # 构建文本内容
        content = f"📊 股票分析推送\n\n" \
                  f"股票: {message['stock_name']}({message['ts_code']})\n" \
                  f"时间: {message['push_time']}\n\n" \
                  f"📈 分析结果:\n{message['analysis']}"

        if message.get('news'):
            content += f"\n\n📰 最新资讯:"
            for news in message['news'][:3]:
                content += f"\n• {news.get('title', '无标题')}"

        if webhook_type == 'feishu':
            # 飞书机器人格式
            return {
                'msg_type': 'text',
                'content': {
                    'text': content
                }
            }
        elif webhook_type == 'dingtalk':
            # 钉钉机器人格式
            return {
                'msgtype': 'text',
                'text': {
                    'content': content
                }
            }
        elif webhook_type == 'wechat_work':
            # 企业微信格式
            return {
                'msgtype': 'text',
                'text': {
                    'content': content
                }
            }
        else:
            # 通用格式
            return message

    @staticmethod
    def _get_stock_data(ts_code):
        """获取股票数据"""
        stock_service = StockService()

        data = {}

        try:
            # 获取最新行情
            daily_basic = stock_service.get_daily_basic(ts_code)
            if daily_basic:
                data.update(daily_basic)
        except Exception as e:
            logger.warning(f"获取行情数据失败: {e}")

        try:
            # 获取资金流向
            moneyflow = stock_service.get_moneyflow(ts_code)
            if moneyflow:
                data.update(moneyflow)
        except Exception as e:
            logger.warning(f"获取资金流向失败: {e}")

        try:
            # 获取技术指标
            factors = stock_service.get_stock_factors(ts_code)
            if factors:
                data.update(factors)
        except Exception as e:
            logger.warning(f"获取技术指标失败: {e}")

        return data

    @staticmethod
    def _build_prompt(ts_code, stock_name, stock_data, news_text):
        """构建分析提示词"""
        # 格式化行情数据
        price_info = []
        if stock_data.get('current_price'):
            price_info.append(f"当前价格: {stock_data.get('current_price')}元")
        if stock_data.get('change_pct'):
            price_info.append(f"涨跌幅: {stock_data.get('change_pct')}%")
        if stock_data.get('volume'):
            price_info.append(f"成交量: {stock_data.get('volume')}手")
        if stock_data.get('turnover_rate'):
            price_info.append(f"换手率: {stock_data.get('turnover_rate')}%")

        # 技术指标
        tech_info = []
        for key in ['ma5', 'ma10', 'ma20', 'macd', 'kdj', 'boll']:
            if stock_data.get(key):
                tech_info.append(f"{key.upper()}: {stock_data.get(key)}")

        prompt = f"""请作为专业股票分析师，简明扼要分析以下股票：

## 股票信息
代码: {ts_code}
名称: {stock_name}

## 今日行情
{chr(10).join(price_info) if price_info else '暂无数据'}

## 技术指标
{chr(10).join(tech_info) if tech_info else '暂无数据'}

## 最新资讯
{news_text}

请给出：
1. 今日走势简述（50字内）
2. 短期判断（支撑/压力位）
3. 操作建议（买入/卖出/持有）
"""

        return prompt

    @staticmethod
    def _push_to_webhook(ts_code, stock_name, analysis_content, news_list):
        """
        推送到 Webhook

        Args:
            ts_code: 股票代码
            stock_name: 股票名称
            analysis_content: AI 分析内容
            news_list: 新闻列表

        Returns:
            dict: 推送结果
        """
        # 获取激活的 Webhook 配置
        webhooks = WebhookConfig.query.filter_by(is_enabled=True).all()

        if not webhooks:
            logger.warning(f"[AI推送] 没有激活的 Webhook 配置，无法推送 {ts_code}")
            return {'success': False, 'message': '没有激活的 Webhook'}

        logger.info(f"[AI推送] 找到 {len(webhooks)} 个激活的 Webhook，将推送 {ts_code}")

        # 构建推送消息
        message = {
            'type': 'stock_analysis',
            'ts_code': ts_code,
            'stock_name': stock_name,
            'analysis': analysis_content,
            'news': news_list,
            'push_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        results = []
        for webhook in webhooks:
            try:
                # 从 config_data 中获取 webhook_url
                webhook_url = webhook.config_data.get('webhook_url') if webhook.config_data else None
                if not webhook_url:
                    logger.warning(f"[AI推送] Webhook 配置缺少 webhook_url: {webhook.webhook_name}")
                    continue

                # 根据 webhook 类型格式化消息
                payload = AnalysisPushService._format_message_by_type(webhook, message)

                response = requests.post(
                    webhook_url,
                    json=payload,
                    timeout=30,
                    headers={'Content-Type': 'application/json'}
                )

                if response.status_code == 200:
                    results.append({'url': webhook_url, 'success': True})
                    logger.info(f"[AI推送] Webhook 推送成功: {webhook_url}")
                else:
                    results.append({
                        'url': webhook_url,
                        'success': False,
                        'status': response.status_code
                    })
                    logger.warning(f"[AI推送] Webhook 推送失败: {webhook_url}, 状态码: {response.status_code}")

            except Exception as e:
                results.append({'url': webhook_url, 'success': False, 'error': str(e)})
                logger.error(f"[AI推送] Webhook 推送异常: {webhook_url}, 错误: {e}")

        success_count = sum(1 for r in results if r.get('success'))
        return {
            'success': success_count > 0,
            'total': len(webhooks),
            'success_count': success_count,
            'results': results
        }

    @staticmethod
    def push_all_enabled():
        """
        推送所有开启推送的自选股

        Returns:
            dict: 推送结果汇总
        """
        # 获取需要推送的自选股
        watchlist = Watchlist.query.filter_by(push_enabled=True).all()

        if not watchlist:
            logger.info("没有开启推送的自选股")
            return {'success': True, 'message': '没有需要推送的自选股', 'count': 0}

        logger.info(f"开始推送 {len(watchlist)} 个自选股")

        results = []
        for item in watchlist:
            try:
                result = AnalysisPushService.push_analysis(item)
                results.append({
                    'ts_code': item.ts_code,
                    'success': result.get('success', False)
                })
            except Exception as e:
                logger.error(f"推送失败 {item.ts_code}: {e}")
                results.append({
                    'ts_code': item.ts_code,
                    'success': False,
                    'error': str(e)
                })

        success_count = sum(1 for r in results if r.get('success'))
        return {
            'success': success_count > 0,
            'total': len(watchlist),
            'success_count': success_count,
            'results': results
        }
