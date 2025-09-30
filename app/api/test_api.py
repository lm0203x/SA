from flask import Blueprint, jsonify
from datetime import datetime
import random

test_bp = Blueprint('test', __name__)

@test_bp.route('/test/hello', methods=['GET'])
def hello():
    """测试API连接"""
    return jsonify({
        'success': True,
        'message': 'Hello from Flask!',
        'timestamp': datetime.now().isoformat()
    })

@test_bp.route('/test/market-data', methods=['GET'])
def mock_market_data():
    """模拟市场数据"""
    mock_data = []
    stocks = ['000001.SZ', '600000.SH', '000002.SZ']
    
    for stock in stocks:
        mock_data.append({
            'ts_code': stock,
            'name': f'股票{stock}',
            'price': round(10 + random.random() * 20, 2),
            'change': round((random.random() - 0.5) * 2, 2),
            'change_pct': round((random.random() - 0.5) * 10, 2),
            'volume': random.randint(100000, 1000000),
            'amount': random.randint(1000000, 10000000),
            'timestamp': datetime.now().isoformat()
        })
    
    return jsonify({
        'success': True,
        'data': mock_data,
        'timestamp': datetime.now().isoformat()
    })

@test_bp.route('/test/anomaly', methods=['GET'])
def mock_anomaly():
    """模拟异动数据"""
    anomalies = [
        {
            'id': '1',
            'ts_code': '000001.SZ',
            'name': '平安银行',
            'type': 'price',
            'severity': 'high',
            'message': '价格异常上涨5.2%',
            'details': {
                'current_value': 11.52,
                'threshold': 11.00,
                'change_rate': 5.2
            },
            'timestamp': datetime.now().isoformat()
        },
        {
            'id': '2',
            'ts_code': '600000.SH',
            'name': '浦发银行',
            'type': 'volume',
            'severity': 'medium',
            'message': '成交量异常放大300%',
            'details': {
                'current_value': 3000000,
                'threshold': 1000000,
                'change_rate': 300
            },
            'timestamp': datetime.now().isoformat()
        }
    ]
    
    return jsonify({
        'success': True,
        'data': anomalies,
        'timestamp': datetime.now().isoformat()
    })