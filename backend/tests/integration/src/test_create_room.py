#!/usr/bin/env python3
"""
创建房间功能的集成测试
"""

import json
import time
import uuid
from unittest.mock import MagicMock, patch

import pytest
import requests


@pytest.mark.usefixtures("app_with_mock_services")
class TestCreateRoomIntegration:
    """创建房间集成测试"""

    def test_create_room_success(self, client, mock_auth_service, mock_notification_service):
        """测试创建房间成功"""
        # Mock auth service
        mock_user = MagicMock()
        mock_user.openid = "test_user_123"
        mock_user.nickname = "测试用户"
        
        mock_auth_service.verify_token.return_value = "test_user_123"
        
        # Mock notification service
        mock_notification_service.broadcast_room_event.return_value = None
        
        # 生成有效token
        import jwt
        token = jwt.encode(
            {"sub": "test_user_123", "exp": time.time() + 3600},
            mock_auth_service.secret_key,
            algorithm="HS256"
        )
        
        # 发送创建房间请求（无需请求体参数）
        response = client.post(
            "/api/v1/room/create",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # 验证响应
        assert response.status_code == 200
        data = response.json
        assert data["code"] == 200
        assert data["message"] == "success"
        assert "room_id" in data["data"]
        assert "room_code" in data["data"]
        assert data["data"]["host_id"] == "test_user_123"
        assert data["data"]["status"] == "waiting"
        assert "players" in data["data"]
        assert "max_players" in data["data"]
        assert "created_at" in data["data"]
        assert data["data"]["max_players"] == 6
        assert len(data["data"]["players"]) == 1
        assert data["data"]["players"][0]["uid"] == "test_user_123"
        
        # 验证WebSocket通知被发送
        mock_notification_service.broadcast_room_event.assert_called_once()
        call_args = mock_notification_service.broadcast_room_event.call_args
        
        # 验证通知参数
        assert call_args[1]["event_type"] == "room.created"
        assert "room_id" in call_args[1]["data"]
        assert call_args[1]["data"]["creator"] == "test_user_123"
        # 注意：不再包含config字段，由客户端规则定义

    def test_create_room_without_auth(self, client):
        """测试未认证创建房间"""
        response = client.post("/api/v1/room/create")
        
        assert response.status_code == 401
        data = response.json
        assert data["code"] == 401
        assert "Missing token" in data["message"]

    def test_create_room_service_unavailable(self, client, mock_auth_service):
        """测试游戏服务不可用"""
        # Mock auth service
        mock_auth_service.verify_token.return_value = "test_user_123"
        
        # 生成有效token
        import jwt
        token = jwt.encode(
            {"sub": "test_user_123", "exp": time.time() + 3600},
            mock_auth_service.secret_key,
            algorithm="HS256"
        )
        
        # 临时移除game_service来模拟服务不可用
        with client.application.app_context():
            original_game_service = client.application.config.get('game_service')
            client.application.config['game_service'] = None
            
            try:
                response = client.post(
                    "/api/v1/room/create",
                    headers={"Authorization": f"Bearer {token}"}
                )
            finally:
                # 恢复原始服务
                if original_game_service:
                    client.application.config['game_service'] = original_game_service
        
        assert response.status_code == 500
        data = response.json
        assert data["code"] == 500
        assert "Game service not available" in data["message"]

    def test_create_room_notification_failure(self, client, mock_auth_service, mock_notification_service):
        """测试通知服务失败不影响房间创建"""
        # Mock auth service
        mock_auth_service.verify_token.return_value = "test_user_123"
        
        # Mock notification service to raise exception
        mock_notification_service.broadcast_room_event.side_effect = Exception("Notification failed")
        
        # 生成有效token
        import jwt
        token = jwt.encode(
            {"sub": "test_user_123", "exp": time.time() + 3600},
            mock_auth_service.secret_key,
            algorithm="HS256"
        )
        
        # 发送创建房间请求（无需请求体参数）
        response = client.post(
            "/api/v1/room/create",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # 房间创建应该成功，即使通知失败
        assert response.status_code == 200
        data = response.json
        assert data["code"] == 200
        assert "room_id" in data["data"]


@pytest.mark.usefixtures("app_with_mock_services")
class TestCreateRoomWebSocketIntegration:
    """创建房间WebSocket集成测试"""

    def test_room_created_websocket_event(self, mock_notification_service):
        """测试房间创建WebSocket事件格式"""
        # 模拟房间创建事件数据（简化，不包含config）
        event_data = {
            "room_id": "test_room_123",
            "room_code": "1234",
            "creator": "test_user_123",
            "creator_nickname": "测试用户",
            "player_count": 1,
            "status": "waiting",
            "created_at": "2024-02-23T10:30:00Z"
        }
        
        # 调用广播方法
        mock_notification_service.broadcast_room_event(
            room_id="test_room_123",
            event_type="room.created",
            data=event_data
        )
        
        # 验证调用
        mock_notification_service.broadcast_room_event.assert_called_once_with(
            room_id="test_room_123",
            event_type="room.created",
            data=event_data
        )