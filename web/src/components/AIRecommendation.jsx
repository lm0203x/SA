import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Brain, Settings, TrendingUp, TrendingDown, Minus, Loader2, AlertCircle } from 'lucide-react';
import AIConfigDialog from '@/components/AIConfigDialog';

export default function AIRecommendation() {
    const [selectedStock, setSelectedStock] = useState('');
    const [recommendation, setRecommendation] = useState(null);
    const [analyzing, setAnalyzing] = useState(false);
    const [message, setMessage] = useState({ type: '', text: '' });
    const [showConfigDialog, setShowConfigDialog] = useState(false);
    const [aiConfigured, setAiConfigured] = useState(false);
    // 检查 AI 是否已配置
    useEffect(() => {
        checkAIConfig();

        // 从本地存储加载上次分析结果
        const savedRecommendation = localStorage.getItem('lastAIRecommendation');
        const savedStock = localStorage.getItem('lastAIStock');
        if (savedRecommendation) {
            try {
                setRecommendation(JSON.parse(savedRecommendation));
            } catch (e) {
                console.error('解析保存的分析结果失败:', e);
            }
        }
        if (savedStock) {
            setSelectedStock(savedStock);
        }
    }, []);

    // 保存分析结果到本地存储
    useEffect(() => {
        if (recommendation) {
            localStorage.setItem('lastAIRecommendation', JSON.stringify(recommendation));
        }
    }, [recommendation]);

    // 保存股票代码到本地存储
    useEffect(() => {
        if (selectedStock) {
            localStorage.setItem('lastAIStock', selectedStock);
        }
    }, [selectedStock]);

    const checkAIConfig = async () => {
        try {
            const response = await fetch('http://localhost:5000/api/ai/config');
            const data = await response.json();
            if (data.success) {
                setAiConfigured(data.data.is_configured);
            }
        } catch (error) {
            console.error('检查AI配置失败:', error);
        }
    };

    // 分析股票
    const handleAnalyze = async () => {
        if (!selectedStock.trim()) {
            setMessage({ type: 'error', text: '请输入股票代码' });
            return;
        }

        if (!aiConfigured) {
            setMessage({ type: 'error', text: '请先配置AI服务' });
            setShowConfigDialog(true);
            return;
        }

        try {
            setAnalyzing(true);
            setMessage({ type: '', text: '' });

            const response = await fetch('http://localhost:5000/api/ai/stock-recommendation', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    ts_code: selectedStock
                })
            });

            const data = await response.json();

            if (data.success) {
                setRecommendation(data.data);
                setMessage({ type: 'success', text: '✅ AI分析完成' });
            } else {
                setMessage({ type: 'error', text: `❌ ${data.message}` });
            }
        } catch (error) {
            console.error('AI分析失败:', error);
            setMessage({ type: 'error', text: `❌ 分析失败: ${error.message}` });
        } finally {
            setAnalyzing(false);
        }
    };

    // 获取推荐类型的颜色和图标
    const getRecommendationStyle = (rec) => {
        switch (rec) {
            case 'buy':
                return {
                    color: 'bg-green-500',
                    textColor: 'text-green-700',
                    bgColor: 'bg-green-50',
                    borderColor: 'border-green-200',
                    icon: TrendingUp,
                    text: '买入'
                };
            case 'sell':
                return {
                    color: 'bg-red-500',
                    textColor: 'text-red-700',
                    bgColor: 'bg-red-50',
                    borderColor: 'border-red-200',
                    icon: TrendingDown,
                    text: '卖出'
                };
            case 'hold':
                return {
                    color: 'bg-yellow-500',
                    textColor: 'text-yellow-700',
                    bgColor: 'bg-yellow-50',
                    borderColor: 'border-yellow-200',
                    icon: Minus,
                    text: '持有'
                };
            default:
                return {
                    color: 'bg-gray-500',
                    textColor: 'text-gray-700',
                    bgColor: 'bg-gray-50',
                    borderColor: 'border-gray-200',
                    icon: Minus,
                    text: '未知'
                };
        }
    };

    // 获取风险等级样式
    const getRiskLevelStyle = (level) => {
        switch (level) {
            case 'low':
                return { color: 'bg-green-100 text-green-800', text: '低风险' };
            case 'medium':
                return { color: 'bg-yellow-100 text-yellow-800', text: '中等风险' };
            case 'high':
                return { color: 'bg-red-100 text-red-800', text: '高风险' };
            default:
                return { color: 'bg-gray-100 text-gray-800', text: '未知' };
        }
    };

    return (
        <div className="space-y-4">
            {/* 消息提示 */}
            {message.text && (
                <Alert className={message.type === 'error' ? 'border-red-500' : 'border-green-500'}>
                    <AlertDescription>{message.text}</AlertDescription>
                </Alert>
            )}

            {/* AI配置未完成提示 */}
            {!aiConfigured && (
                <Alert className="border-yellow-500 bg-yellow-50">
                    <AlertCircle className="h-4 w-4" />
                    <AlertDescription className="ml-2">
                        AI服务尚未配置，请点击右上角的"AI设置"按钮进行配置
                    </AlertDescription>
                </Alert>
            )}

            {/* 主功能区 */}
            <Card>
                <CardHeader>
                    <div className="flex items-center justify-between">
                        <div>
                            <CardTitle className="flex items-center gap-2">
                                <Brain className="h-5 w-5 text-purple-500" />
                                AI智能推荐
                            </CardTitle>
                            <CardDescription>
                                使用AI分析股票数据，提供买入/卖出/持有建议
                            </CardDescription>
                        </div>
                        <Button
                            onClick={() => setShowConfigDialog(true)}
                            variant="outline"
                            size="sm"
                        >
                            <Settings className="h-4 w-4 mr-1" />
                            AI设置
                        </Button>
                    </div>
                </CardHeader>
                <CardContent className="space-y-4">
                    {/* 股票输入 */}
                    <div className="flex gap-2">
                        <div className="flex-1">
                            <Input
                                placeholder="输入股票代码，例如：000001.SZ"
                                value={selectedStock}
                                onChange={(e) => setSelectedStock(e.target.value)}
                                onKeyPress={(e) => {
                                    if (e.key === 'Enter') {
                                        handleAnalyze();
                                    }
                                }}
                            />
                        </div>
                        <Button
                            onClick={handleAnalyze}
                            disabled={analyzing || !selectedStock.trim()}
                        >
                            {analyzing ? (
                                <>
                                    <Loader2 className="h-4 w-4 mr-1 animate-spin" />
                                    分析中...
                                </>
                            ) : (
                                <>
                                    <Brain className="h-4 w-4 mr-1" />
                                    AI分析
                                </>
                            )}
                        </Button>
                    </div>

                    {/* 分析结果 */}
                    {recommendation && (
                        <Card className={`border-2 ${getRecommendationStyle(recommendation.recommendation).borderColor}`}>
                            <CardContent className="pt-6">
                                <div className="space-y-4">
                                    {/* 股票信息 */}
                                    <div className="flex items-center justify-between">
                                        <div>
                                            <h3 className="text-xl font-bold">{recommendation.stock_name}</h3>
                                            <p className="text-sm text-gray-500">{recommendation.ts_code}</p>
                                        </div>
                                        {/* 只在有价格数据时显示价格信息 */}
                                        {recommendation.data_summary?.current_price > 0 && (
                                            <div className="text-right">
                                                <div className="text-2xl font-bold">
                                                    ¥{recommendation.data_summary.current_price.toFixed(2)}
                                                </div>
                                                <div className={`text-sm ${recommendation.data_summary.change_pct >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                                    {recommendation.data_summary.change_pct >= 0 ? '+' : ''}
                                                    {recommendation.data_summary.change_pct.toFixed(2)}%
                                                </div>
                                            </div>
                                        )}
                                    </div>

                                    {/* 推荐结果 */}
                                    <div className={`p-4 rounded-lg ${getRecommendationStyle(recommendation.recommendation).bgColor}`}>
                                        <div className="flex items-center justify-between mb-3">
                                            <div className="flex items-center gap-2">
                                                {React.createElement(getRecommendationStyle(recommendation.recommendation).icon, {
                                                    className: `h-6 w-6 ${getRecommendationStyle(recommendation.recommendation).textColor}`
                                                })}
                                                <span className={`text-2xl font-bold ${getRecommendationStyle(recommendation.recommendation).textColor}`}>
                                                    {getRecommendationStyle(recommendation.recommendation).text}
                                                </span>
                                            </div>
                                            <div className="text-right">
                                                <div className="text-sm text-gray-600">置信度</div>
                                                <div className="text-xl font-bold">
                                                    {Math.round(recommendation.confidence * 100)}%
                                                </div>
                                            </div>
                                        </div>

                                        {/* 目标价格和风险等级 */}
                                        <div className="flex gap-4 mt-3">
                                            {recommendation.target_price > 0 && (
                                                <div>
                                                    <span className="text-sm text-gray-600">目标价位：</span>
                                                    <span className="font-medium">¥{recommendation.target_price.toFixed(2)}</span>
                                                </div>
                                            )}
                                            <div>
                                                <Badge className={getRiskLevelStyle(recommendation.risk_level).color}>
                                                    {getRiskLevelStyle(recommendation.risk_level).text}
                                                </Badge>
                                            </div>
                                        </div>
                                    </div>

                                    {/* 推荐理由 */}
                                    <div>
                                        <h4 className="font-medium mb-2">分析理由：</h4>
                                        <ul className="space-y-1">
                                            {recommendation.reasons?.map((reason, index) => (
                                                <li key={index} className="text-sm text-gray-700 flex items-start">
                                                    <span className="mr-2">•</span>
                                                    <span>{reason}</span>
                                                </li>
                                            ))}
                                        </ul>
                                    </div>

                                    {/* 分析时间和提供者 */}
                                    <div className="text-xs text-gray-500 flex items-center justify-between pt-2 border-t">
                                        <span>分析时间: {new Date(recommendation.analysis_time).toLocaleString()}</span>
                                        <span>AI服务: {recommendation.ai_provider}</span>
                                    </div>
                                </div>
                            </CardContent>
                        </Card>
                    )}
                </CardContent>
            </Card>



            {/* AI配置对话框 */}
            <AIConfigDialog
                open={showConfigDialog}
                onClose={() => {
                    setShowConfigDialog(false);
                    checkAIConfig(); // 关闭后重新检查配置
                }}
            />
        </div>
    );
}
