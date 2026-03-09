#!/usr/bin/env python3
"""
WebSocket 连接管理服务
负责管理 WebSocket 连接的生命周期，包括订阅管理、连接清理等
"""

from typing import TYPE_CHECKING

from backend.utils.logger import setup_logger

if TYPE_CHECKING:
    pass

logger = setup_logger(__name__)


class WebSocketManager:
    """
    WebSocket 连接管理器
    
    职责：
    - 管理用户与房间订阅关系
    - 处理用户离开房间时的连接清理
    - 提供连接查询和管理接口
    """
    
    def __init__(self):
        """初始化 WebSocket 管理器"""
        self._connections = None  # 将在 app_factory 中设置
        self._room_subscriptions = None  # 将在 app_factory 中设置
    
    def set_connections(self, connections: dict):
        """设置连接字典引用"""
        self._connections = connections
    
    def set_room_subscriptions(self, room_subscriptions: dict):
        """设置房间订阅字典引用"""
        self._room_subscriptions = room_subscriptions
    
    def unsubscribe_user_from_room(self, user_id: str, room_id: str) -> int:
        """
        取消用户对房间的订阅
        
        Args:
            user_id: 用户ID
            room_id: 房间ID
        
        Returns:
            取消的连接数量
        """
        if not self._connections or not self._room_subscriptions:
            logger.warning("WebSocket connections not initialized")
            return 0
        
        if room_id not in self._room_subscriptions:
            logger.debug(f"Room {room_id} has no subscriptions")
            return 0
        
        # 找到该用户的所有WebSocket连接
        ws_ids_to_remove = []
        for ws_id, conn_info in self._connections.items():
            if conn_info.get("user_id") == user_id:
                ws_ids_to_remove.append(ws_id)
        
        # 从房间订阅中移除这些连接
        removed_count = 0
        for ws_id in ws_ids_to_remove:
            if ws_id in self._room_subscriptions[room_id]:
                self._room_subscriptions[room_id].discard(ws_id)
                removed_count += 1
                
                # 从连接的房间列表中移除该房间
                if ws_id in self._connections:
                    self._connections[ws_id]["rooms"].discard(room_id)
        
        # 如果房间没有订阅者了，清理房间订阅记录
        if not self._room_subscriptions[room_id]:
            del self._room_subscriptions[room_id]
            logger.info(f"Room {room_id} subscription cleared (no subscribers)")
        
        if removed_count > 0:
            logger.info(
                f"Unsubscribed user {user_id} from room {room_id}",
                extra={
                    'user_id': user_id,
                    'room_id': room_id,
                    'removed_connections': removed_count
                }
            )
        
        return removed_count
    
    def get_user_connections(self, user_id: str) -> list:
        """
        获取用户的所有WebSocket连接ID
        
        Args:
            user_id: 用户ID
        
        Returns:
            WebSocket连接ID列表
        """
        if not self._connections:
            return []
        
        return [
            ws_id for ws_id, conn_info in self._connections.items()
            if conn_info.get("user_id") == user_id
        ]
    
    def get_room_subscribers(self, room_id: str) -> list:
        """
        获取房间的所有订阅者用户ID
        
        Args:
            room_id: 房间ID
        
        Returns:
            用户ID列表
        """
        if not self._connections or not self._room_subscriptions:
            return []
        
        if room_id not in self._room_subscriptions:
            return []
        
        user_ids = []
        for ws_id in self._room_subscriptions[room_id]:
            if ws_id in self._connections:
                user_id = self._connections[ws_id].get("user_id")
                if user_id:
                    user_ids.append(user_id)
        
        return list(set(user_ids))  # 去重
    
    def disconnect_user(self, user_id: str) -> int:
        """
        断开用户的所有WebSocket连接
        
        Args:
            user_id: 用户ID
        
        Returns:
            断开的连接数量
        """
        if not self._connections:
            return 0
        
        ws_ids_to_disconnect = self.get_user_connections(user_id)
        disconnected_count = 0
        
        for ws_id in ws_ids_to_disconnect:
            if ws_id in self._connections:
                try:
                    ws = self._connections[ws_id].get("ws")
                    if ws:
                        ws.close()
                        disconnected_count += 1
                except Exception as e:
                    logger.warning(f"Failed to close connection {ws_id}: {e}")
        
        if disconnected_count > 0:
            logger.info(
                f"Disconnected {disconnected_count} WebSocket connections for user {user_id}"
            )
        
        return disconnected_count


# 创建全局实例
ws_manager = WebSocketManager()
