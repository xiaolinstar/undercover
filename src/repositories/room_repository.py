#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
房间仓储类
负责房间数据的持久化操作
"""

import json
import redis
from typing import Optional
from src.models.room import Room
from src.config.game_config import GameConfig


class RoomRepository:
    """房间仓储类"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.prefix = "room:"
    
    def _get_key(self, room_id: str) -> str:
        """获取房间在Redis中的键"""
        return f"{self.prefix}{room_id}"
    
    def save(self, room: Room) -> bool:
        """保存房间信息"""
        try:
            # 更新最后活跃时间
            room.update_last_active()
            
            # 转换为字典并序列化
            room_data = room.to_dict()
            room_json = json.dumps(room_data, ensure_ascii=False)
            
            # 保存到Redis，设置过期时间
            key = self._get_key(room.room_id)
            self.redis.setex(
                key, 
                GameConfig.ROOM_TIMEOUT_SECONDS, 
                room_json
            )
            return True
        except Exception as e:
            print(f"保存房间失败: {e}")
            return False
    
    def get(self, room_id: str) -> Optional[Room]:
        """获取房间信息"""
        try:
            key = self._get_key(room_id)
            room_json = self.redis.get(key)
            
            if room_json is None:
                return None
            
            # 处理bytes类型的JSON数据
            if isinstance(room_json, bytes):
                room_json = room_json.decode('utf-8')
            
            room_data = json.loads(room_json)
            return Room.from_dict(room_data)
        except Exception as e:
            print(f"获取房间失败: {e}")
            return None
    
    def delete(self, room_id: str) -> bool:
        """删除房间"""
        try:
            key = self._get_key(room_id)
            self.redis.delete(key)
            return True
        except Exception as e:
            print(f"删除房间失败: {e}")
            return False
    
    def exists(self, room_id: str) -> bool:
        """检查房间是否存在"""
        try:
            key = self._get_key(room_id)
            return self.redis.exists(key) > 0
        except Exception as e:
            print(f"检查房间存在性失败: {e}")
            return False