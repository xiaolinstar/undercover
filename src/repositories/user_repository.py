#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户仓储类
负责用户数据的持久化操作
"""

import json
import redis
from typing import Optional
from src.models.user import User


class UserRepository:
    """用户仓储类"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.prefix = "user:"
    
    def _get_key(self, user_id: str) -> str:
        """获取用户在Redis中的键"""
        return f"{self.prefix}{user_id}"
    
    def save(self, user: User) -> bool:
        """保存用户信息"""
        try:
            # 转换为字典并序列化
            user_data = user.to_dict()
            user_json = json.dumps(user_data, ensure_ascii=False)
            
            # 保存到Redis
            key = self._get_key(user.openid)
            self.redis.set(key, user_json)
            return True
        except Exception as e:
            print(f"保存用户失败: {e}")
            return False
    
    def get(self, user_id: str) -> Optional[User]:
        """获取用户信息"""
        try:
            key = self._get_key(user_id)
            user_json = self.redis.get(key)
            
            if user_json is None:
                return None
            
            # 处理bytes类型的JSON数据
            if isinstance(user_json, bytes):
                user_json = user_json.decode('utf-8')
            
            user_data = json.loads(user_json)
            return User.from_dict(user_data)
        except Exception as e:
            print(f"获取用户失败: {e}")
            return None
    
    def delete(self, user_id: str) -> bool:
        """删除用户"""
        try:
            key = self._get_key(user_id)
            self.redis.delete(key)
            return True
        except Exception as e:
            print(f"删除用户失败: {e}")
            return False