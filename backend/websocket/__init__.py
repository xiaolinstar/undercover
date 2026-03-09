#!/usr/bin/env python3
"""
WebSocket 模块
提供实时通知功能
"""

from flask_socketio import SocketIO

_socketio_instance = None


def get_socketio():
    """获取 SocketIO 实例"""
    global _socketio_instance
    if _socketio_instance is None:
        _socketio_instance = SocketIO()
    return _socketio_instance


def reset_socketio():
    """重置 SocketIO 实例（仅用于测试）"""
    global _socketio_instance
    _socketio_instance = SocketIO()
    return _socketio_instance


socketio = get_socketio()

__all__ = ["socketio", "get_socketio", "reset_socketio"]
