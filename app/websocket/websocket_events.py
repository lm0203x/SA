"""
WebSocket事件处理器 - 简化版本
提供基础的实时连接功能
"""

import logging
from datetime import datetime
from flask import request
from flask_socketio import emit, join_room, leave_room, disconnect
from app.extensions import socketio



logger = logging.getLogger(__name__)

# 连接管理
connected_clients = {}
room_subscriptions = {}

@socketio.on('connect')
def handle_connect():
    """客户端连接事件"""
    client_id = request.sid
    connected_clients[client_id] = {
        'connected_at': datetime.now(),
        'subscriptions': set(),
        'user_agent': request.headers.get('User-Agent', ''),
        'remote_addr': request.remote_addr
    }
    
    logger.info(f"客户端连接: {client_id} from {request.remote_addr}")
    
    # 发送连接确认
    emit('connected', {
        'client_id': client_id,
        'server_time': datetime.now().isoformat(),
        'message': '连接成功'
    })

@socketio.on('disconnect')
def handle_disconnect():
    """客户端断开连接事件"""
    client_id = request.sid
    
    if client_id in connected_clients:
        # 清理订阅
        subscriptions = connected_clients[client_id]['subscriptions']
        for subscription in subscriptions:
            if subscription in room_subscriptions:
                room_subscriptions[subscription].discard(client_id)
                if not room_subscriptions[subscription]:
                    del room_subscriptions[subscription]
        
        del connected_clients[client_id]
        logger.info(f"客户端断开连接: {client_id}")

@socketio.on('subscribe')
def handle_subscribe(data):
    """订阅数据推送 - 基础版本"""
    client_id = request.sid
    subscription_type = data.get('type')
    params = data.get('params', {})
    
    if not subscription_type:
        emit('error', {'message': '订阅类型不能为空'})
        return
    
    # 构建房间名称
    if subscription_type == 'market_data':
        symbol = params.get('symbol')
        if not symbol:
            emit('error', {'message': '股票代码不能为空'})
            return
        room_name = f"market_data_{symbol}"
    else:
        room_name = f"{subscription_type}_general"
    
    # 加入房间
    join_room(room_name)
    
    # 更新客户端订阅记录
    if client_id in connected_clients:
        connected_clients[client_id]['subscriptions'].add(room_name)
    
    # 更新房间订阅记录
    if room_name not in room_subscriptions:
        room_subscriptions[room_name] = set()
    room_subscriptions[room_name].add(client_id)
    
    logger.info(f"客户端 {client_id} 订阅了 {room_name}")
    
    # 发送订阅确认
    emit('subscribed', {
        'type': subscription_type,
        'room': room_name,
        'message': '订阅成功'
    })

@socketio.on('unsubscribe')
def handle_unsubscribe(data):
    """取消订阅"""
    client_id = request.sid
    subscription_type = data.get('type')
    params = data.get('params', {})
    
    # 构建房间名称
    if subscription_type == 'market_data':
        symbol = params.get('symbol')
        if not symbol:
            emit('error', {'message': '股票代码不能为空'})
            return
        room_name = f"market_data_{symbol}"
    else:
        room_name = f"{subscription_type}_general"
    
    # 离开房间
    leave_room(room_name)
    
    # 更新客户端订阅记录
    if client_id in connected_clients:
        connected_clients[client_id]['subscriptions'].discard(room_name)
    
    # 更新房间订阅记录
    if room_name in room_subscriptions:
        room_subscriptions[room_name].discard(client_id)
        if not room_subscriptions[room_name]:
            del room_subscriptions[room_name]
    
    logger.info(f"客户端 {client_id} 取消订阅了 {room_name}")
    
    # 发送取消订阅确认
    emit('unsubscribed', {
        'type': subscription_type,
        'room': room_name,
        'message': '取消订阅成功'
    })

@socketio.on('ping')
def handle_ping():
    """心跳检测"""
    emit('pong', {
        'timestamp': datetime.now().isoformat(),
        'message': 'pong'
    })

# 广播消息函数（供其他模块调用）
def broadcast_market_data(symbol, data):
    """广播市场数据更新"""
    room_name = f"market_data_{symbol}"
    if room_name in room_subscriptions and room_subscriptions[room_name]:
        socketio.emit('market_data_update', {
            'symbol': symbol,
            'data': data,
            'timestamp': datetime.now().isoformat()
        }, room=room_name)
        logger.debug(f"广播市场数据到房间 {room_name}: {len(room_subscriptions[room_name])} 个客户端")

def broadcast_risk_alert(alert_data):
    """广播风险预警"""
    room_name = "risk_alerts_general"
    if room_name in room_subscriptions and room_subscriptions[room_name]:
        socketio.emit('risk_alert', {
            'alert': alert_data,
            'timestamp': datetime.now().isoformat()
        }, room=room_name)
        logger.info(f"广播风险预警到房间 {room_name}: {len(room_subscriptions[room_name])} 个客户端")

def get_connection_stats():
    """获取连接统计信息"""
    return {
        'total_clients': len(connected_clients),
        'total_rooms': len(room_subscriptions),
        'room_details': {room: len(clients) for room, clients in room_subscriptions.items()}
    }