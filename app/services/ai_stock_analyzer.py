"""
AI股票分析服务
支持多种AI提供者（通义千问、OpenAI等）
"""

import requests
import json
from loguru import logger
from datetime import datetime
from flask import current_app


class AIStockAnalyzer:
    """AI股票分析服务"""

    def __init__(self):
        """初始化AI分析服务"""
        self._load_config()

    def _load_config(self):
        """加载配置（支持动态配置）"""
        try:
            # 优先从数据库AI配置加载
            from app.models.ai_config import AIConfig
            self.config = AIConfig.get_config_dict()
            self.provider = self.config.get('provider', 'zhipu')
        except Exception as e:
            logger.warning(f"从数据库AI配置加载失败,使用默认配置: {e}")
            # 回退到系统配置
            try:
                from app.models.system_config import SystemConfig
                self.config = SystemConfig.get_ai_config()
                self.provider = self.config.get('provider', 'zhipu')
            except Exception as e2:
                logger.warning(f"从系统配置加载AI配置失败: {e2}")
                # 回退到应用配置
                self.config = current_app.config.get('AI_CONFIG', {})
                self.provider = self.config.get('provider', 'zhipu')

    def reload_config(self):
        """重新加载配置"""
        logger.info("重新加载AI配置...")
        self._load_config()

    def analyze_stock(self, ts_code, stock_name, stock_data):
        """
        分析股票并给出建议

        Args:
            ts_code: 股票代码
            stock_name: 股票名称
            stock_data: 股票数据字典

        Returns:
            分析结果字典
        """
        news_analysis = self._analyze_news_impact(stock_data.get('news_list', []))
        try:
            # 检查配置
            if not self._check_config():
                return self._get_default_result(ts_code, stock_name, "AI服务未配置")

            # 确定分析模式
            is_watchlist = stock_data.get('is_watchlist', False)
            
            # 构建分析提示词
            if is_watchlist and stock_data.get('current_price', 0) > 0:
                # 自选股且有数据,进行详细技术分析
                prompt = self._build_analysis_prompt(ts_code, stock_name, stock_data)
            else:
                # 非自选股或无数据,进行市场舆论分析
                prompt = self._build_market_analysis_prompt(ts_code, stock_name, stock_data)

            # 调用AI API
            response_text = self._call_ai_api(prompt)

            # 解析结果
            result = self._parse_response(response_text)
            result = self._apply_news_confidence_adjustment(result, news_analysis)

            # 补充数据
            result.update({
                'ts_code': ts_code,
                'stock_name': stock_name,
                'analysis_time': datetime.now().isoformat(),
                'ai_provider': self.provider,
                'news_sentiment': news_analysis['sentiment'],
                'news_impact_score': news_analysis['impact_score'],
                'news_highlights': news_analysis['highlights'],
                'news_risk_note': news_analysis['risk_note']
            })

            logger.info(f"AI分析完成: {ts_code} - {result['recommendation']}")
            return result

        except Exception as e:
            logger.error(f"AI分析失败: {e}")
            result = self._get_default_result(ts_code, stock_name, f"分析失败: {str(e)}")
            result = self._apply_news_confidence_adjustment(result, news_analysis)
            result.update({
                'news_sentiment': news_analysis['sentiment'],
                'news_impact_score': news_analysis['impact_score'],
                'news_highlights': news_analysis['highlights'],
                'news_risk_note': news_analysis['risk_note']
            })
            return result

    def _check_config(self):
        """检查AI配置是否有效"""
        if not self.config:
            return False

        provider_config = self.config.get(self.provider)
        if not provider_config:
            return False

        api_key = provider_config.get('api_key')
        if not api_key or api_key.strip() == '':
            return False

        return True

    def _call_ai_api(self, prompt):
        """调用AI API"""
        try:
            if self.provider == 'zhipu':
                return self._call_zhipu_api(prompt)
            elif self.provider == 'minmax':
                return self._call_minmax_api(prompt)
            elif self.provider == 'kimi':
                return self._call_kimi_api(prompt)
            elif self.provider == 'custom':
                return self._call_custom_api(prompt)
            else:
                raise ValueError(f"不支持的AI提供者: {self.provider}")

        except Exception as e:
            logger.error(f"AI API调用失败: {e}")
            raise e

    def _call_minmax_api(self, prompt):
        """调用Minmax API"""
        config = self.config.get('minmax', {})

        headers = {
            'Authorization': f'Bearer {config["api_key"]}',
            'Content-Type': 'application/json'
        }

        data = {
            "model": config.get("model", "abab6.5s-chat"),
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.1,
        }

        # 获取并验证timeout
        timeout_val = config.get('timeout', 3000000)
        try:
            timeout_int = int(timeout_val) if timeout_val else 3000000
            # 如果值小于等于3600（1小时），当作秒处理，转换为毫秒
            if timeout_int <= 3600:
                timeout_int = timeout_int * 1000
            timeout = timeout_int / 1000
        except (ValueError, TypeError):
            timeout = 3000

        base_url = config.get('base_url', 'https://api.minimax.chat/v1')

        # 记录请求日志
        logger.info(f"调用Minmax API请求: {json.dumps(data, ensure_ascii=False)}")

        response = requests.post(
            f"{base_url}/text/chatcompletion_v2",
            headers=headers,
            json=data,
            timeout=timeout
        )

        if response.status_code == 200:
            result = response.json()
            logger.info(f"Minmax API原始响应: {json.dumps(result, ensure_ascii=False)}")

            if 'choices' in result and len(result['choices']) > 0:
                return result['choices'][0]['message']['content']
            else:
                error_msg = f"Minmax API响应格式错误: {result}"
                logger.error(error_msg)
                raise Exception(error_msg)
        else:
            try:
                error_data = response.json()
                if 'error' in error_data:
                    error_info = error_data['error']
                    error_msg = f"Minmax API调用失败: {response.status_code}, 错误: {error_info.get('message', 'unknown')}"
                else:
                    error_msg = f"Minmax API调用失败: {response.status_code}, {error_data}"
            except:
                error_msg = f"Minmax API调用失败: {response.status_code}, {response.text}"
            raise Exception(error_msg)

    def _call_kimi_api(self, prompt):
        """调用Kimi API"""
        config = self.config.get('kimi', {})

        headers = {
            'Authorization': f'Bearer {config["api_key"]}',
            'Content-Type': 'application/json'
        }

        data = {
            "model": config.get("model", "moonshot-v1-8k"),
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.1,
        }

        # 获取并验证timeout
        timeout_val = config.get('timeout', 3000000)
        try:
            timeout_int = int(timeout_val) if timeout_val else 3000000
            # 如果值小于等于3600（1小时），当作秒处理，转换为毫秒
            if timeout_int <= 3600:
                timeout_int = timeout_int * 1000
            timeout = timeout_int / 1000
        except (ValueError, TypeError):
            timeout = 3000

        base_url = config.get('base_url', 'https://api.moonshot.cn/v1')

        # 记录请求日志
        logger.info(f"调用Kimi API请求: {json.dumps(data, ensure_ascii=False)}")

        response = requests.post(
            f"{base_url}/chat/completions",
            headers=headers,
            json=data,
            timeout=timeout
        )

        if response.status_code == 200:
            result = response.json()
            logger.info(f"Kimi API原始响应: {json.dumps(result, ensure_ascii=False)}")

            if 'choices' in result and len(result['choices']) > 0:
                return result['choices'][0]['message']['content']
            else:
                error_msg = f"Kimi API响应格式错误: {result}"
                logger.error(error_msg)
                raise Exception(error_msg)
        else:
            try:
                error_data = response.json()
                if 'error' in error_data:
                    error_info = error_data['error']
                    error_msg = f"Kimi API调用失败: {response.status_code}, 错误: {error_info.get('message', 'unknown')}"
                else:
                    error_msg = f"Kimi API调用失败: {response.status_code}, {error_data}"
            except:
                error_msg = f"Kimi API调用失败: {response.status_code}, {response.text}"
            raise Exception(error_msg)

    def _call_zhipu_api(self, prompt):
        """调用智谱GLM API"""
        config = self.config.get('zhipu', {})

        headers = {
            'Authorization': f'Bearer {config["api_key"]}',
            'Content-Type': 'application/json'
        }

        data = {
            "model": config.get("model", "glm-4-flash"),
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.1,
        }

        # 获取并验证timeout
        timeout_val = config.get('timeout', 3000000)
        try:
            timeout_int = int(timeout_val) if timeout_val else 3000000
            # 如果值小于等于3600（1小时），当作秒处理，转换为毫秒
            if timeout_int <= 3600:
                timeout_int = timeout_int * 1000
            timeout = timeout_int / 1000
        except (ValueError, TypeError):
            timeout = 3000

        base_url = config.get('base_url', 'https://open.bigmodel.cn/api/paas/v4')

        # 记录请求日志
        logger.info(f"调用智谱GLM API请求: {json.dumps(data, ensure_ascii=False)}")

        response = requests.post(
            f"{base_url}/chat/completions",
            headers=headers,
            json=data,
            timeout=timeout
        )

        if response.status_code == 200:
            result = response.json()
            # 记录原始响应日志
            logger.info(f"智谱GLM API原始响应: {json.dumps(result, ensure_ascii=False)}")

            # 智谱GLM使用与OpenAI相同的响应格式
            if 'choices' in result and len(result['choices']) > 0:
                return result['choices'][0]['message']['content']
            else:
                error_msg = f"智谱GLM API响应格式错误: {result}"
                logger.error(error_msg)
                raise Exception(error_msg)
        else:
            # 尝试解析错误信息
            try:
                error_data = response.json()
                if 'error' in error_data:
                    error_info = error_data['error']
                    error_msg = f"智谱GLM API调用失败: {response.status_code}, 错误码: {error_info.get('code', 'unknown')}, 消息: {error_info.get('message', 'unknown')}"
                else:
                    error_msg = f"智谱GLM API调用失败: {response.status_code}, {error_data}"
            except:
                error_msg = f"智谱GLM API调用失败: {response.status_code}, {response.text}"
            raise Exception(error_msg)


    def _call_custom_api(self, prompt):
        """调用自定义API（兼容OpenAI格式）"""
        config = self.config.get('custom', {})

        headers = {
            'Authorization': f'Bearer {config["api_key"]}',
            'Content-Type': 'application/json'
        }

        data = {
            "model": config.get("model", "custom-model"),
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.1
        }

        # 获取并验证timeout
        timeout_val = config.get('timeout', 3000000)
        try:
            timeout_int = int(timeout_val) if timeout_val else 3000000
            # 如果值小于等于3600（1小时），当作秒处理，转换为毫秒
            if timeout_int <= 3600:
                timeout_int = timeout_int * 1000
            timeout = timeout_int / 1000
        except (ValueError, TypeError):
            timeout = 3000

        base_url = config.get('base_url', 'https://api.example.com/v1')
        
        # 记录请求日志
        logger.info(f"调用自定义API请求: {json.dumps(data, ensure_ascii=False)}")
        
        response = requests.post(
            f"{base_url}/chat/completions",
            headers=headers,
            json=data,
            timeout=timeout
        )

        if response.status_code == 200:
            result = response.json()
            # 假设使用OpenAI兼容格式
            if 'choices' in result and len(result['choices']) > 0:
                return result['choices'][0]['message']['content']
            else:
                error_msg = f"自定义API响应格式错误: {result}"
                logger.error(error_msg)
                raise Exception(error_msg)
        else:
            # 尝试解析错误信息
            try:
                error_data = response.json()
                if 'error' in error_data:
                    error_msg = f"自定义API调用失败: {response.status_code}, 错误: {error_data['error']}"
                else:
                    error_msg = f"自定义API调用失败: {response.status_code}, {error_data}"
            except:
                error_msg = f"自定义API调用失败: {response.status_code}, {response.text}"
            raise Exception(error_msg)



    def _build_analysis_prompt(self, ts_code, stock_name, stock_data):
        """构建专业分析提示词"""

        # 准备数据字段
        current_price = stock_data.get('current_price', 0)
        change_pct = stock_data.get('change_pct', 0)
        volume_ratio = stock_data.get('volume_ratio', 0)
        pe_ratio = stock_data.get('pe_ratio', 0)
        pb_ratio = stock_data.get('pb_ratio', 0)
        turnover_rate = stock_data.get('turnover_rate', 0)
        total_mv = stock_data.get('total_mv', 0)
        news_analysis = self._analyze_news_impact(stock_data.get('news_list', []))
        news_summary = self._build_news_prompt_section(news_analysis)
        news = stock_data.get('news', '暂无最新资讯')

        # 判断市场状态
        market_status = self._get_market_status(change_pct, volume_ratio, turnover_rate)

        prompt = f"""<system>
你是一位具有10年以上经验的资深股票分析师,专门为机构投资者提供投资决策支持.你的分析风格稳健客观,注重风险控制,善于识别市场情绪和资金流向.
</system>

<role>
作为专业分析师,请从以下几个维度对股票进行综合分析:
- 【技术面】价格走势、成交量、换手率、均线形态
- 【基本面】估值水平（PE/PB）、盈利能力、市场地位
- 【资金面】主力资金流向、换手率异常、市场情绪
- 【消息面】最新资讯、市场传闻、政策影响
- 【风险提示】潜在风险点,回撤预警因素
</role>

<analysis_framework>
请严格按照以下框架进行分析:
- 若涨幅>5%且量比>1.5:重点分析是否处于主升浪,警惕放量滞涨
- 若跌幅>5%:分析是否破位下跌,评估支撑位
- 若PE<0或PE>100:说明估值异常原因
- 若换手率>15%:提示资金博弈剧烈风险
- 若总市值<50亿:提示小盘股波动风险
- 若总市值>1000亿:提示大盘股弹性不足
</analysis_framework>

<data>
股票代码: {ts_code}
股票名称:{stock_name}
当前价格:¥{current_price:.2f}
涨跌幅:{change_pct:.2f}%
量比:{volume_ratio:.2f}
换手率:{turnover_rate:.2f}%
市盈率(PE):{pe_ratio:.2f}
市净率(PB):{pb_ratio:.2f}
总市值:{total_mv/10000:.2f}亿
市场状态:{market_status}

【最新资讯】
{news}
</data>

<output_format>
请返回以下JSON格式（必须严格遵循,不要任何额外文字）:
{{
    "recommendation": "buy" | "sell" | "hold",
    "reasons": ["分析理由1（包含具体数据和指标）", "分析理由2", "分析理由3"],
    "target_price": 目标价位（当前价格±30%以内为合理区间）,
    "risk_level": "low" | "medium" | "high",
    "confidence": 0.0-1.0（置信度,综合考虑数据完整性,分析确定性）,
    "key_points": ["要点1", "要点2", "要点3"],
    "risk_warning": "风险提示（50字以内）"
}}
</output_format>

<important>
- recommendation只能是buy/sell/hold之一
- reasons必须包含具体数值,如"PE为XX高于行业平均"
- target_price必须考虑当前价格±30%合理区间
- risk_level必须与风险提示一致
- 只返回JSON,不要任何解释性文字
- 如果数据不足导致无法判断,confidence应低于0.6
- 必须结合最新资讯进行分析,资讯可能影响短期走势
</important>
"""
        return prompt

    def _build_market_analysis_prompt(self, ts_code, stock_name, stock_data):
        """构建市场分析提示词（针对无数据/非自选股）"""
        news = stock_data.get('news', '暂无最新资讯')

        prompt = f"""<system>
你是一位具有10年以上经验的资深股票分析师,专门为机构投资者提供投资决策支持.你的分析风格稳健客观,注重风险控制,善于识别市场情绪和资金流向.
</system>

<role>
作为专业分析师,请基于最新资讯和市场舆论对股票进行分析:
- 【消息面】最新资讯、公告、传闻的影响
- 【市场情绪】资金关注度、散户情绪
- 【行业趋势】所属板块走势、政策影响
- 【风险提示】潜在风险
</role>

<data>
股票代码: {ts_code}
股票名称:{stock_name}

【最新资讯】
{news}
</data>

<output_format>
请返回以下JSON格式（必须严格遵循,不要任何额外文字）:
{{
    "recommendation": "buy" | "sell" | "hold",
    "reasons": ["分析理由1（基于资讯内容）", "分析理由2", "分析理由3"],
    "target_price": 0,
    "risk_level": "low" | "medium" | "high",
    "confidence": 0.0-1.0,
    "key_points": ["要点1", "要点2"],
    "risk_warning": "风险提示（50字以内）"
}}
</output_format>

<important>
- recommendation只能是buy/sell/hold之一
- 必须重点分析最新资讯对股价的影响
- 若无实质资讯,confidence应低于0.5
- 只返回JSON,不要任何解释性文字
</important>
"""
        return prompt

    def _get_market_status(self, change_pct, volume_ratio, turnover_rate):
        """判断市场状态"""
        if change_pct > 5 and volume_ratio > 1.5:
            return "强势突破"
        elif change_pct > 3:
            return "强势上涨"
        elif change_pct < -5:
            return "大幅下跌"
        elif change_pct < -3:
            return "弱势下跌"
        elif turnover_rate > 15:
            return "资金博弈剧烈"
        elif volume_ratio > 2:
            return "放量异动"
        else:
            return "横盘震荡"

    def _analyze_news_impact(self, news_list):
        """杩斿洖鏂伴椈鎯呯华鍜屽奖鍝嶅己搴︾殑鏈€灏忕粨鏋?"""
        normalized_news = [item for item in (news_list or []) if item and item.get('title')]
        if not normalized_news:
            return {
                'sentiment': 'neutral',
                'impact_score': 0,
                'highlights': [],
                'risk_note': '\u6682\u65e0\u660e\u786e\u65b0\u95fb\u5f71\u54cd',
            }

        positive_keywords = [
            '\u589e\u957f', '\u9884\u589e', '\u5408\u540c', '\u7a81\u7834', '\u56de\u8d2d',
            '\u4e0a\u6da8', '\u6539\u5584', '\u5229\u597d', '\u4e2d\u6807', '\u589e\u6301'
        ]
        negative_keywords = [
            '\u4e8f\u635f', '\u4e0b\u6ed1', '\u5904\u7f5a', '\u8c03\u67e5', '\u51cf\u6301',
            '\u8dcc\u8dcc', '\u8fdd\u89c4', '\u98ce\u9669', '\u8bc9\u53f8', '\u8d1f\u9762'
        ]
        high_impact_keywords = [
            '\u5e74\u62a5', '\u5b63\u62a5', '\u516c\u544a', '\u91cd\u7ec4', '\u5e76\u8d2d',
            '\u505c\u724c', '\u590d\u724c', '\u76d1\u7ba1', '\u653f\u7b56'
        ]

        positive_hits = 0
        negative_hits = 0
        impact_hits = 0
        highlights = []

        for item in normalized_news[:3]:
            title = item.get('title', '')
            highlights.append(title)
            positive_hits += self._count_keyword_hits(title, positive_keywords)
            negative_hits += self._count_keyword_hits(title, negative_keywords)
            impact_hits += self._count_keyword_hits(title, high_impact_keywords)

        if positive_hits > negative_hits:
            sentiment = 'positive'
        elif negative_hits > positive_hits:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'

        impact_score = min(100, len(normalized_news) * 15 + impact_hits * 20 + abs(positive_hits - negative_hits) * 10)

        if sentiment == 'negative':
            risk_note = '\u8fd1\u671f\u8d44\u8baf\u504f\u8d1f\u9762\uff0c\u5efa\u8bae\u5728\u63a8\u8350\u89e3\u8bfb\u4e2d\u5f3a\u5316\u98ce\u9669\u63d0\u793a'
        elif sentiment == 'positive':
            risk_note = '\u8fd1\u671f\u8d44\u8baf\u504f\u6b63\u9762\uff0c\u53ef\u4f5c\u4e3a\u77ed\u671f\u60c5\u7eea\u52a0\u5206\u56e0\u5b50'
        else:
            risk_note = '\u8fd1\u671f\u8d44\u8baf\u504f\u4e2d\u6027\uff0c\u5bf9\u63a8\u8350\u7684\u5f71\u54cd\u6709\u9650'

        return {
            'sentiment': sentiment,
            'impact_score': impact_score,
            'highlights': highlights,
            'risk_note': risk_note,
        }

    def _build_news_prompt_section(self, news_analysis):
        highlights = news_analysis.get('highlights') or []
        highlight_text = '\uff1b'.join(highlights) if highlights else '\u6682\u65e0\u5173\u952e\u65b0\u95fb'
        default_risk_note = '\u6682\u65e0'
        return (
            f"\u60c5\u7eea\u503e\u5411: {news_analysis.get('sentiment', 'neutral')}\uff1b"
            f"\u5f71\u54cd\u5f3a\u5ea6: {news_analysis.get('impact_score', 0)}\uff1b"
            f"\u5173\u952e\u65b0\u95fb: {highlight_text}\uff1b"
            f"\u98ce\u9669\u63d0\u793a: {news_analysis.get('risk_note', default_risk_note)}"
        )

    def _count_keyword_hits(self, text, keywords):
        return sum(1 for keyword in keywords if keyword and keyword in (text or ''))

    def _apply_news_confidence_adjustment(self, result, news_analysis):
        confidence = float(result.get('confidence', 0.0) or 0.0)
        impact_score = float(news_analysis.get('impact_score', 0) or 0.0)
        normalized_impact = min(1.0, impact_score / 100.0)
        sentiment = news_analysis.get('sentiment', 'neutral')

        if sentiment == 'positive':
            confidence += 0.1 * normalized_impact
        elif sentiment == 'negative':
            confidence -= 0.1 * normalized_impact

        result['confidence'] = max(0.0, min(1.0, round(confidence, 4)))
        return result

    def _parse_response(self, response_text):
        """解析AI响应"""
        try:
            # 尝试解析JSON
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1

            if start_idx != -1 and end_idx != 0:
                json_str = response_text[start_idx:end_idx]
                result = json.loads(json_str)

                # 验证必需字段
                required_fields = ['recommendation', 'reasons', 'confidence']
                for field in required_fields:
                    if field not in result:
                        logger.warning(f"AI响应缺少必需字段: {field}")
                        # 设置默认值
                        if field == 'recommendation':
                            result[field] = 'hold'
                        elif field == 'reasons':
                            result[field] = ['分析结果不完整']
                        elif field == 'confidence':
                            result[field] = 0.0

                # 验证推荐值
                if result['recommendation'] not in ['buy', 'sell', 'hold']:
                    result['recommendation'] = 'hold'

                # 验证风险等级
                if 'risk_level' in result and result['risk_level'] not in ['low', 'medium', 'high']:
                    result['risk_level'] = 'medium'

                # 确保置信度在合理范围
                try:
                    confidence = float(result['confidence'])
                    result['confidence'] = max(0.0, min(1.0, confidence))
                except (ValueError, TypeError):
                    result['confidence'] = 0.0

                # 确保目标价格是数字
                if 'target_price' in result:
                    try:
                        result['target_price'] = float(result['target_price'])
                    except (ValueError, TypeError):
                        result['target_price'] = 0.0

                return result
            else:
                logger.warning("AI响应中未找到有效的JSON格式")
                logger.warning(f"原始响应内容: {response_text}")
                return self._get_default_result()

        except json.JSONDecodeError as e:
            logger.error(f"解析AI响应JSON失败: {e}")
            logger.error(f"原始响应内容: {response_text}")
            return self._get_default_result()

        except Exception as e:
            logger.error(f"解析AI响应失败: {e}")
            return self._get_default_result()

    def _get_default_result(self, ts_code="000001.SZ", stock_name="平安银行", error_msg=""):
        """获取默认分析结果"""
        return {
            'recommendation': 'hold',
            'reasons': ['AI分析暂时不可用,建议谨慎投资'],
            'target_price': 0.0,
            'risk_level': 'medium',
            'confidence': 0.0,
            'news_sentiment': 'neutral',
            'news_impact_score': 0,
            'news_highlights': [],
            'news_risk_note': '\u6682\u65e0\u660e\u786e\u65b0\u95fb\u5f71\u54cd',
            'ts_code': ts_code,
            'stock_name': stock_name,
            'analysis_time': datetime.now().isoformat(),
            'ai_provider': self.provider,
            'error_message': error_msg
        }


# 全局实例延迟初始化
ai_stock_analyzer = None

def get_ai_analyzer():
    """获取AI分析器实例"""
    global ai_stock_analyzer
    if ai_stock_analyzer is None:
        ai_stock_analyzer = AIStockAnalyzer()
    return ai_stock_analyzer

def reload_ai_analyzer():
    """重新加载AI分析器配置"""
    global ai_stock_analyzer
    if ai_stock_analyzer is not None:
        ai_stock_analyzer.reload_config()
    return ai_stock_analyzer
