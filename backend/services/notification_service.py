#!/usr/bin/env python3
"""
通知服务
负责向客户端发送 WebSocket 事件通知

支持两种 WebSocket 协议：
1. Socket.IO（用于 Web 端）
2. 原生 WebSocket（用于微信小程序）
"""

import time
from typing import Any

from flask_socketio import SocketIO

from backend.utils.logger import setup_logger

logger = setup_logger(__name__)


class NotificationService:
    """
    通知服务
    
    职责：
    - 向房间内所有订阅者发送事件通知
    - 统一的消息格式化
    - 简化业务代码的通知发送
    - 同时支持 Socket.IO 和原生 WebSocket
    
    设计说明：
    - 单实例部署：直接通过 socketio.emit() 和 native_ws.broadcast() 发送
    - 未来多实例：只需配置 message_queue，代码无需改变
    """
    
    def __init__(self, socketio: SocketIO):
        """
        初始化通知服务
        
        Args:
            socketio: Flask-SocketIO 实例
        """
        self.socketio = socketio
        self.native_ws_broadcast = None  # 将在 app_factory 中设置
    
    def set_native_ws_broadcast(self, broadcast_func):
        """设置原生 WebSocket 广播函数"""
        self.native_ws_broadcast = broadcast_func
    
    def broadcast_room_event(
        self,
        room_id: str,
        event_type: str,
        data: dict[str, Any] | None = None
    ) -> None:
        """
        广播房间事件（别名方法，与notify_room功能相同）
        
        Args:
            room_id: 房间ID
            event_type: 事件类型（如 'room.created'）
            data: 事件数据
        """
        self.notify_room(room_id, event_type, data)
    
    def notify_room(
        self,
        room_id: str,
        event: str,
        data: dict[str, Any] | None = None,
        exclude_user: str | None = None
    ) -> None:
        """
        向房间内所有订阅者发送通知
        
        同时发送到 Socket.IO 和原生 WebSocket 客户端
        
        Args:
            room_id: 房间ID
            event: 事件类型（如 'room.player_joined'）
            data: 事件数据（轻量级提示信息）
            exclude_user: 排除的用户ID（可选，如操作发起者）
        
        Example:
            notification_service.notify_room(
                room_id="8888",
                event="room.player_joined",
                data={"player_count": 4, "hint": "新玩家加入"}
            )
        """
        message = self._format_message(room_id, event, data)
        
        try:
            # 发送到 Socket.IO 客户端（Web 端）
            self.socketio.emit(
                event,
                message,
                room=room_id
            )
            
            # 发送到原生 WebSocket 客户端（小程序）
            if self.native_ws_broadcast:
                self.native_ws_broadcast(room_id, event, message)
            
            logger.debug(
                f"Notification sent to room",
                extra={
                    'room_id': room_id,
                    'event': event,
                    'exclude_user': exclude_user
                }
            )
            
        except Exception as e:
            logger.error(
                f"Failed to send notification",
                extra={
                    'room_id': room_id,
                    'event': event,
                    'error': str(e)
                }
            )
    
    def notify_user(
        self,
        user_id: str,
        event: str,
        data: dict[str, Any] | None = None
    ) -> None:
        """
        向特定用户发送通知（未来扩展）
        
        Args:
            user_id: 用户ID
            event: 事件类型
            data: 事件数据
        """
        # 未来实现：需要维护 user_id -> sid 的映射
        pass
    
    def _format_message(
        self,
        room_id: str,
        event: str,
        data: dict[str, Any] | None
    ) -> dict[str, Any]:
        """
        格式化消息
        
        统一的消息格式：
        {
            "event": "room.player_joined",
            "room_id": "8888",
            "timestamp": 1708675200,
            "data": {"player_count": 4, "hint": "新玩家加入"}
        }
        """
        return {
            "event": event,
            "room_id": room_id,
            "timestamp": int(time.time()),
            "data": data or {}
        }
