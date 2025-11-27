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
            self.provider = self.config.get('provider', 'tongyi')
        except Exception as e:
            logger.warning(f"从数据库AI配置加载失败，使用默认配置: {e}")
            # 回退到系统配置
            try:
                from app.models.system_config import SystemConfig
                self.config = SystemConfig.get_ai_config()
                self.provider = self.config.get('provider', 'tongyi')
            except Exception as e2:
                logger.warning(f"从系统配置加载AI配置失败: {e2}")
                # 回退到应用配置
                self.config = current_app.config.get('AI_CONFIG', {})
                self.provider = self.config.get('provider', 'tongyi')

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
        try:
            # 检查配置
            if not self._check_config():
                return self._get_default_result(ts_code, stock_name, "AI服务未配置")

            # 确定分析模式
            is_watchlist = stock_data.get('is_watchlist', False)
            
            # 构建分析提示词
            if is_watchlist and stock_data.get('current_price', 0) > 0:
                # 自选股且有数据，进行详细技术分析
                prompt = self._build_analysis_prompt(ts_code, stock_name, stock_data)
            else:
                # 非自选股或无数据，进行市场舆论分析
                prompt = self._build_market_analysis_prompt(ts_code, stock_name)

            # 调用AI API
            response_text = self._call_ai_api(prompt)

            # 解析结果
            result = self._parse_response(response_text)

            # 补充数据
            result.update({
                'ts_code': ts_code,
                'stock_name': stock_name,
                'analysis_time': datetime.now().isoformat(),
                'ai_provider': self.provider
            })

            logger.info(f"AI分析完成: {ts_code} - {result['recommendation']}")
            return result

        except Exception as e:
            logger.error(f"AI分析失败: {e}")
            return self._get_default_result(ts_code, stock_name, f"分析失败: {str(e)}")

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
            if self.provider == 'tongyi':
                return self._call_tongyi_api(prompt)
            elif self.provider == 'openai':
                return self._call_openai_api(prompt)
            elif self.provider == 'zhipu':
                return self._call_zhipu_api(prompt)
            elif self.provider == 'ollama':
                return self._call_ollama_api(prompt)
            elif self.provider == 'custom':
                return self._call_custom_api(prompt)
            else:
                raise ValueError(f"不支持的AI提供者: {self.provider}")

        except Exception as e:
            logger.error(f"AI API调用失败: {e}")
            raise e

    def _call_tongyi_api(self, prompt):
        """调用通义千问API"""
        config = self.config['tongyi']

        headers = {
            'Authorization': f'Bearer {config["api_key"]}',
            'Content-Type': 'application/json'
        }

        data = {
            "model": config.get("model", "qwen-plus"),
            "input": {
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            },
            "parameters": {
                "temperature": 0.1
            }
        }

        # 获取并验证timeout
        timeout = config.get('timeout', 600)
        try:
            timeout = int(timeout) if timeout else 600
        except (ValueError, TypeError):
            timeout = 600

        # 记录请求日志
        logger.info(f"调用通义千问API请求: {json.dumps(data, ensure_ascii=False)}")

        response = requests.post(
            f"{config['base_url']}/services/aigc/text-generation/generation",
            headers=headers,
            json=data,
            timeout=timeout
        )

        if response.status_code == 200:
            result = response.json()
            return result['output']['text']
        else:
            error_msg = f"通义千问API调用失败: {response.status_code}"
            if response.text:
                error_msg += f", {response.text}"
            raise Exception(error_msg)

    def _call_openai_api(self, prompt):
        """调用OpenAI API"""
        config = self.config['openai']

        headers = {
            'Authorization': f'Bearer {config["api_key"]}',
            'Content-Type': 'application/json'
        }

        data = {
            "model": config.get("model", "gpt-3.5-turbo"),
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.1
        }

        # 获取并验证timeout
        timeout = config.get('timeout', 600)
        try:
            timeout = int(timeout) if timeout else 600
        except (ValueError, TypeError):
            timeout = 600

        base_url = config.get('base_url', 'https://api.openai.com/v1')
        
        # 记录请求日志
        logger.info(f"调用OpenAI API请求: {json.dumps(data, ensure_ascii=False)}")
        
        response = requests.post(
            f"{base_url}/chat/completions",
            headers=headers,
            json=data,
            timeout=timeout
        )

        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            error_msg = f"OpenAI API调用失败: {response.status_code}"
            if response.text:
                error_msg += f", {response.text}"
            raise Exception(error_msg)

    def _call_ollama_api(self, prompt):
        """调用Ollama本地API"""
        config = self.config.get('ollama', {})

        # 获取并验证timeout
        timeout = config.get('timeout', 30)
        try:
            timeout = int(timeout) if timeout else 30
        except (ValueError, TypeError):
            timeout = 30

        # 记录请求日志
        request_data = {
            "model": config.get('model', 'qwen2.5-coder'),
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1
            }
        }
        logger.info(f"调用Ollama API请求: {json.dumps(request_data, ensure_ascii=False)}")

        response = requests.post(
            f"{config.get('base_url', 'http://localhost:11434')}/api/generate",
            json=request_data,
            timeout=timeout
        )

        if response.status_code == 200:
            result = response.json()
            return result['response']
        else:
            error_msg = f"Ollama API调用失败: {response.status_code}"
            if response.text:
                error_msg += f", {response.text}"
            raise Exception(error_msg)

    def _call_zhipu_api(self, prompt):
        """调用智谱GLM API"""
        config = self.config.get('zhipu', {})

        headers = {
            'Authorization': f'Bearer {config["api_key"]}',
            'Content-Type': 'application/json'
        }

        data = {
            "model": config.get("model", "glm-4"),
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.1,
        }

        # 获取并验证timeout
        timeout = config.get('timeout', 600)
        try:
            timeout = int(timeout) if timeout else 600
        except (ValueError, TypeError):
            timeout = 600

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
        timeout = config.get('timeout', 600)
        try:
            timeout = int(timeout) if timeout else 600
        except (ValueError, TypeError):
            timeout = 600

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
        """构建分析提示词"""

        # 准备数据字段
        current_price = stock_data.get('current_price', 0)
        change_pct = stock_data.get('change_pct', 0)
        volume_ratio = stock_data.get('volume_ratio', 0)
        pe_ratio = stock_data.get('pe_ratio', 0)
        pb_ratio = stock_data.get('pb_ratio', 0)

        prompt = f"""
你是专业的股票分析师，请分析以下股票并给出投资建议：

股票代码：{ts_code}
股票名称：{stock_name}
当前价格：¥{current_price}
今日涨跌：{change_pct:.2f}%
成交量比：{volume_ratio}
市盈率：{pe_ratio}
市净率：{pb_ratio}

请基于以上信息给出投资建议，以JSON格式返回：
{{
    "recommendation": "buy/sell/hold",
    "reasons": ["理由1", "理由2"],
    "target_price": 目标价格数字,
    "risk_level": "low/medium/high",
    "confidence": 0.0-1.0
}}

注意：
1. recommendation必须是buy/sell/hold之一
2. reasons数组包含2-3条简要理由
3. target_price是数字类型
4. risk_level是low/medium/high之一
5. confidence是0到1之间的数字
6. 只返回JSON，不要其他文字
"""
        return prompt

    def _build_market_analysis_prompt(self, ts_code, stock_name):
        """构建市场分析提示词（针对无数据/非自选股）"""
        prompt = f"""
你是专业的股票分析师，请分析以下股票的市场情况和舆论风向：

股票代码：{ts_code}
股票名称：{stock_name}

由于缺乏详细的技术指标数据，请重点从以下角度进行分析：
1. 宏观经济环境对该行业的影响
2. 该公司近期的重大新闻或公告
3. 市场情绪和资金关注度
4. 行业发展趋势

请基于以上信息给出投资建议，以JSON格式返回：
{{
    "recommendation": "buy/sell/hold",
    "reasons": ["理由1", "理由2"],
    "target_price": 0,
    "risk_level": "low/medium/high",
    "confidence": 0.0-1.0
}}

注意：
1. recommendation必须是buy/sell/hold之一
2. reasons数组包含2-3条基于市场和基本面的理由
3. target_price设为0即可
4. risk_level是low/medium/high之一
5. confidence是0到1之间的数字
6. 只返回JSON，不要其他文字
"""
        return prompt

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
            'reasons': ['AI分析暂时不可用，建议谨慎投资'],
            'target_price': 0.0,
            'risk_level': 'medium',
            'confidence': 0.0,
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