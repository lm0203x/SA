import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { TrendingUp, Shield, Zap, Activity, ArrowRight, BarChart2, Brain } from 'lucide-react';

const LandingPage = () => {
    const navigate = useNavigate();

    return (
        <div className="min-h-screen bg-gradient-to-b from-slate-50 to-slate-100 dark:from-slate-950 dark:to-slate-900 flex flex-col">
            {/* Navigation */}
            <nav className="w-full px-6 py-4 flex justify-between items-center max-w-7xl mx-auto">
                <div className="flex items-center gap-2">
                    <div className="bg-blue-600 p-2 rounded-lg">
                        <TrendingUp className="h-6 w-6 text-white" />
                    </div>
                    <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-indigo-600">
                        StockGuard
                    </span>
                </div>
                <div className="flex gap-4">
                    <Button variant="ghost" onClick={() => navigate('/dashboard')}>
                        控制台
                    </Button>
                    <Button onClick={() => navigate('/dashboard')}>
                        立即开始
                    </Button>
                </div>
            </nav>

            {/* Hero Section */}
            <main className="flex-1 flex flex-col items-center justify-center px-4 text-center mt-10 mb-20">
                <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-blue-50 text-blue-700 text-sm font-medium mb-8 animate-in fade-in slide-in-from-bottom-4 duration-1000">
                    <span className="relative flex h-2 w-2">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
                        <span className="relative inline-flex rounded-full h-2 w-2 bg-blue-500"></span>
                    </span>
                    AI 驱动的智能股票分析系统
                </div>

                <h1 className="text-5xl md:text-7xl font-bold tracking-tight text-slate-900 dark:text-white mb-6 max-w-4xl animate-in fade-in slide-in-from-bottom-8 duration-1000 delay-100">
                    洞察市场脉搏 <br />
                    <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600">
                        把握投资先机
                    </span>
                </h1>

                <p className="text-xl text-slate-600 dark:text-slate-400 mb-10 max-w-2xl animate-in fade-in slide-in-from-bottom-8 duration-1000 delay-200">
                    集成实时异动检测、AI 深度分析与智能预警。让数据为您说话，让决策更加精准。
                </p>

                <div className="flex flex-col sm:flex-row gap-4 animate-in fade-in slide-in-from-bottom-8 duration-1000 delay-300">
                    <Button size="lg" className="h-12 px-8 text-lg gap-2" onClick={() => navigate('/dashboard')}>
                        进入系统 <ArrowRight className="h-5 w-5" />
                    </Button>
                    <Button size="lg" variant="outline" className="h-12 px-8 text-lg">
                        了解更多
                    </Button>
                </div>

                {/* Feature Grid */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-24 max-w-6xl w-full px-4 animate-in fade-in slide-in-from-bottom-12 duration-1000 delay-500">
                    <FeatureCard
                        icon={<Zap className="h-8 w-8 text-amber-500" />}
                        title="实时异动检测"
                        description="毫秒级监控市场交易数据，即时捕捉主力资金动向与异常交易行为。"
                    />
                    <FeatureCard
                        icon={<Brain className="h-8 w-8 text-purple-500" />} // Using Brain icon which is available in lucide-react
                        title="AI 深度分析"
                        description="基于大语言模型的多维度分析，整合技术面、基本面与市场舆情。"
                    />
                    <FeatureCard
                        icon={<Shield className="h-8 w-8 text-green-500" />}
                        title="智能风控预警"
                        description="自定义预警规则，多渠道实时推送，全方位守护您的投资安全。"
                    />
                </div>
            </main>

            {/* Footer */}
            <footer className="w-full py-8 text-center text-slate-500 text-sm border-t border-slate-200 dark:border-slate-800">
                <p>© 2025 StockGuard Analysis System. All rights reserved.</p>
            </footer>
        </div>
    );
};

const FeatureCard = ({ icon, title, description }) => (
    <div className="p-6 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm hover:shadow-md transition-all hover:-translate-y-1">
        <div className="mb-4 inline-flex p-3 rounded-xl bg-slate-50 dark:bg-slate-800">
            {icon}
        </div>
        <h3 className="text-xl font-semibold mb-2 text-slate-900 dark:text-white">{title}</h3>
        <p className="text-slate-600 dark:text-slate-400 leading-relaxed">
            {description}
        </p>
    </div>
);



export default LandingPage;
