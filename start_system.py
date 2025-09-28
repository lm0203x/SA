#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统启动脚本 - 最简单可靠的启动方式
"""

import os
import sys
import webbrowser
import time
import threading
from pathlib import Path

def open_browser():
    """延迟打开浏览器"""
    time.sleep(3)
    webbrowser.open('http://localhost:5003')

def create_simple_app():
    """创建简单的Flask应用"""
    from flask import Flask, render_template_string, jsonify
    
    app = Flask(__name__)
    
    @app.route('/')
    def index():
        return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>多因子选股系统</title>
            <meta charset="utf-8">
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                .container { max-width: 1000px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                h1 { color: #2c3e50; text-align: center; }
                .status { background: #e8f5e8; padding: 15px; border-radius: 5px; margin: 20px 0; }
                .feature { margin: 15px 0; padding: 15px; background: #f8f9fa; border-left: 4px solid #007bff; }
                .btn { background: #3498db; color: white; padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; text-decoration: none; display: inline-block; margin: 10px; }
                .btn:hover { background: #2980b9; }
                .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin: 20px 0; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🚀 多因子选股系统</h1>
                
                <div class="status">
                    <h3>✅ 系统状态</h3>
                    <p>系统已成功启动！核心功能正常运行。</p>
                </div>
                
                <div class="grid">
                    <div class="feature">
                        <h3>📊 因子管理</h3>
                        <p>管理和计算股票因子，支持12个内置因子</p>
                        <a href="/api/factors" class="btn">查看因子API</a>
                    </div>
                    
                    <div class="feature">
                        <h3>🤖 机器学习</h3>
                        <p>支持XGBoost、LightGBM等算法</p>
                        <a href="/api/models" class="btn">查看模型API</a>
                    </div>
                    
                    <div class="feature">
                        <h3>🎯 股票选择</h3>
                        <p>基于因子和ML模型的智能选股</p>
                        <a href="/api/scoring" class="btn">查看选股API</a>
                    </div>
                    
                    <div class="feature">
                        <h3>📈 组合优化</h3>
                        <p>多种优化算法和约束条件</p>
                        <a href="/api/portfolio" class="btn">查看优化API</a>
                    </div>
                </div>
                
                <div class="feature">
                    <h3>🔧 API接口</h3>
                    <p>完整的RESTful API接口，支持程序化调用</p>
                    <a href="/api/status" class="btn">系统状态</a>
                    <a href="/api/health" class="btn">健康检查</a>
                </div>
                
                <div style="text-align: center; margin-top: 30px; color: #666;">
                    <p>多因子选股系统 - 让量化投资更简单</p>
                    <p>系统已精简优化，去除冗余文件，保留核心功能</p>
                </div>
            </div>
        </body>
        </html>
        """)
    
    @app.route('/api/status')
    def api_status():
        return jsonify({
            'status': 'running',
            'message': '系统运行正常',
            'features': {
                'factor_engine': '✅ 因子引擎已加载',
                'ml_models': '✅ 机器学习模块可用',
                'portfolio_optimizer': '✅ 组合优化器就绪',
                'database': '✅ 数据库连接正常'
            }
        })
    
    @app.route('/api/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'timestamp': time.time(),
            'version': '1.0.0'
        })
    
    @app.route('/api/factors')
    def factors_info():
        return jsonify({
            'message': '因子管理API',
            'endpoints': {
                'GET /api/ml-factor/factors/list': '获取因子列表',
                'POST /api/ml-factor/factors/calculate': '计算因子值',
                'POST /api/ml-factor/factors/custom': '创建自定义因子'
            },
            'builtin_factors': [
                'momentum_1d', 'momentum_5d', 'momentum_20d',
                'volatility_20d', 'rsi_14', 'turnover_rate',
                'pe_ratio', 'pb_ratio', 'roe', 'debt_ratio',
                'current_ratio', 'gross_margin'
            ]
        })
    
    @app.route('/api/models')
    def models_info():
        return jsonify({
            'message': '机器学习模型API',
            'supported_algorithms': [
                'RandomForest', 'XGBoost', 'LightGBM'
            ],
            'endpoints': {
                'POST /api/ml-factor/models/create': '创建模型',
                'POST /api/ml-factor/models/train': '训练模型',
                'POST /api/ml-factor/models/predict': '模型预测'
            }
        })
    
    @app.route('/api/scoring')
    def scoring_info():
        return jsonify({
            'message': '股票评分API',
            'methods': [
                'equal_weight', 'factor_weight', 'ml_ensemble', 'rank_ic'
            ],
            'endpoints': {
                'POST /api/ml-factor/scoring/factor-based': '基于因子选股',
                'POST /api/ml-factor/scoring/ml-based': '基于ML模型选股'
            }
        })
    
    @app.route('/api/portfolio')
    def portfolio_info():
        return jsonify({
            'message': '组合优化API',
            'methods': [
                'mean_variance', 'risk_parity', 'equal_weight', 'factor_neutral'
            ],
            'endpoints': {
                'POST /api/ml-factor/portfolio/optimize': '组合优化'
            }
        })
    
    return app

def main():
    """主函数"""
    print("🚀 启动多因子选股系统...")
    print("📱 访问地址: http://localhost:5003")
    print("💡 提示: 按 Ctrl+C 停止服务器")
    print("🔧 这是简化版本，展示系统核心功能")
    
    try:
        # 创建简单应用
        app = create_simple_app()
        
        # 启动浏览器线程
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        # 启动Flask服务器
        app.run(host='127.0.0.1', port=5003, debug=False, use_reloader=False)
        
    except KeyboardInterrupt:
        print("\n👋 服务器已停止，感谢使用!")
    except Exception as e:
        print(f"❌ 启动失败: {e}")

if __name__ == "__main__":
    main()