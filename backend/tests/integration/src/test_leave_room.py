#!/usr/bin/env python3
"""
离开房间功能的集成测试
"""

import time
from unittest.mock import MagicMock, patch

import pytest
import jwt


@pytest.mark.usefixtures("app_with_mock_services")
class TestLeaveRoomIntegration:
    """离开房间集成测试"""

    def test_leave_room_success(self, client, mock_auth_service, mock_notification_service):
        """测试离开房间成功"""
        # Mock auth service
        mock_auth_service.verify_token.return_value = "test_user_123"
        
        # 生成有效token
        token = jwt.encode(
            {"sub": "test_user_123", "exp": time.time() + 3600},
            mock_auth_service.secret_key,
            algorithm="HS256"
        )
        
        # 模拟用户在房间中
        with client.application.app_context():
            # Mock用户仓库
            mock_user = MagicMock()
            mock_user.openid = "test_user_123"
            mock_user.nickname = "测试用户"
            mock_user.current_room = "room_123"
            mock_user.has_joined_room.return_value = True
            mock_user.leave_room.return_value = None
            
            # Mock房间
            mock_room = MagicMock()
            mock_room.room_id = "room_123"
            mock_room.creator = "other_user"  # 不是房主
            mock_room.players = ["test_user_123", "other_user"]
            mock_room.status = MagicMock()
            mock_room.status.value = "waiting"
            
            mock_user_repo = MagicMock()
            mock_user_repo.get.return_value = mock_user
            mock_room_repo = MagicMock()
            mock_room_repo.get.return_value = mock_room
            
            # 设置必要的配置
            original_config = client.application.config.copy()
            client.application.config['user_repository'] = mock_user_repo
            client.application.config['room_repository'] = mock_room_repo
            client.application.config['notification_service'] = mock_notification_service
            
            try:
                # 发送离开房间请求
                response = client.post(
                    "/api/v1/room/leave",
                    headers={"Authorization": f"Bearer {token}"}
                )
            finally:
                # 恢复原始配置
                client.application.config.update(original_config)
            
            # 验证响应
            assert response.status_code == 200
            data = response.json
            assert data["code"] == 200
            assert data["message"] == "success"
            
            # 验证用户状态更新
            mock_user.leave_room.assert_called_once()
            mock_user_repo.save.assert_called_with(mock_user)
            
            # 验证房间状态更新
            assert "test_user_123" not in mock_room.players
            mock_room_repo.save.assert_called_with(mock_room)

    def test_leave_room_creator_transfer(self, client, mock_auth_service, mock_notification_service):
        """测试房主离开时转移权限"""
        # Mock auth service
        mock_auth_service.verify_token.return_value = "creator_user"
        
        # 生成有效token
        token = jwt.encode(
            {"sub": "creator_user", "exp": time.time() + 3600},
            mock_auth_service.secret_key,
            algorithm="HS256"
        )
        
        # 模拟房主离开房间
        with client.application.app_context():
            # Mock用户（房主）
            mock_creator = MagicMock()
            mock_creator.openid = "creator_user"
            mock_creator.nickname = "房主用户"
            mock_creator.current_room = "room_123"
            mock_creator.has_joined_room.return_value = True
            mock_creator.leave_room.return_value = None
            
            # Mock房间
            mock_room = MagicMock()
            mock_room.room_id = "room_123"
            mock_room.creator = "creator_user"  # 是房主
            mock_room.players = ["creator_user", "player1", "player2"]
            mock_room.status = MagicMock()
            mock_room.status.value = "waiting"
            
            mock_user_repo = MagicMock()
            mock_user_repo.get.return_value = mock_creator
            mock_room_repo = MagicMock()
            mock_room_repo.get.return_value = mock_room
            
            # 设置必要的配置
            original_config = client.application.config.copy()
            client.application.config['user_repository'] = mock_user_repo
            client.application.config['room_repository'] = mock_room_repo
            client.application.config['notification_service'] = mock_notification_service
            
            try:
                # 发送离开房间请求
                response = client.post(
                    "/api/v1/room/leave",
                    headers={"Authorization": f"Bearer {token}"}
                )
            finally:
                # 恢复原始配置
                client.application.config.update(original_config)
            
            # 验证响应
            assert response.status_code == 200
            
            # 验证房主权限转移
            assert mock_room.creator != "creator_user"
            assert mock_room.creator in ["player1", "player2"]
            mock_room_repo.save.assert_called_with(mock_room)

    def test_leave_room_disband(self, client, mock_auth_service, mock_notification_service):
        """测试房间解散（最后一个玩家离开）"""
        # Mock auth service
        mock_auth_service.verify_token.return_value = "last_user"
        
        # 生成有效token
        token = jwt.encode(
            {"sub": "last_user", "exp": time.time() + 3600},
            mock_auth_service.secret_key,
            algorithm="HS256"
        )
        
        # 模拟最后一个玩家离开
        with client.application.app_context():
            # Mock用户
            mock_user = MagicMock()
            mock_user.openid = "last_user"
            mock_user.nickname = "最后玩家"
            mock_user.current_room = "room_123"
            mock_user.has_joined_room.return_value = True
            mock_user.leave_room.return_value = None
            
            # Mock房间（只有一个玩家）
            mock_room = MagicMock()
            mock_room.room_id = "room_123"
            mock_room.creator = "last_user"
            mock_room.players = ["last_user"]  # 只有一个人
            mock_room.status = MagicMock()
            mock_room.status.value = "waiting"
            
            mock_user_repo = MagicMock()
            mock_user_repo.get.return_value = mock_user
            mock_room_repo = MagicMock()
            mock_room_repo.get.return_value = mock_room
            
            # 设置必要的配置
            original_config = client.application.config.copy()
            client.application.config['user_repository'] = mock_user_repo
            client.application.config['room_repository'] = mock_room_repo
            client.application.config['notification_service'] = mock_notification_service
            
            try:
                # 发送离开房间请求
                response = client.post(
                    "/api/v1/room/leave",
                    headers={"Authorization": f"Bearer {token}"}
                )
            finally:
                # 恢复原始配置
                client.application.config.update(original_config)
            
            # 验证响应
            assert response.status_code == 200
            
            # 验证房间被解散
            mock_room_repo.delete.assert_called_once_with("room_123")

    def test_leave_room_without_auth(self, client):
        """测试未认证离开房间"""
        response = client.post("/api/v1/room/leave")
        
        assert response.status_code == 401
        data = response.json
        assert data["code"] == 401
        assert "Missing token" in data["message"]

    def test_leave_room_not_in_room(self, client, mock_auth_service):
        """测试用户不在房间中"""
        # Mock auth service
        mock_auth_service.verify_token.return_value = "test_user_123"
        
        # 生成有效token
        token = jwt.encode(
            {"sub": "test_user_123", "exp": time.time() + 3600},
            mock_auth_service.secret_key,
            algorithm="HS256"
        )
        
        # 模拟用户不在房间中
        with client.application.app_context():
            mock_user = MagicMock()
            mock_user.openid = "test_user_123"
            mock_user.has_joined_room.return_value = False  # 不在房间中
            
            mock_user_repo = MagicMock()
            mock_user_repo.get.return_value = mock_user
            
            # 设置必要的配置
            original_config = client.application.config.copy()
            client.application.config['user_repository'] = mock_user_repo
            client.application.config['room_repository'] = MagicMock()
            client.application.config['notification_service'] = MagicMock()
            
            try:
                # 发送离开房间请求
                response = client.post(
                    "/api/v1/room/leave",
                    headers={"Authorization": f"Bearer {token}"}
                )
            finally:
                # 恢复原始配置
                client.application.config.update(original_config)
            
            # 验证响应
            assert response.status_code == 404
            data = response.json
            assert data["code"] == 404
            assert "User not in any room" in data["message"]

    def test_leave_room_during_game(self, client, mock_auth_service):
        """测试游戏中不能离开房间"""
        # Mock auth service
        mock_auth_service.verify_token.return_value = "test_user_123"
        
        # 生成有效token
        token = jwt.encode(
            {"sub": "test_user_123", "exp": time.time() + 3600},
            mock_auth_service.secret_key,
            algorithm="HS256"
        )
        
        # 模拟游戏中状态
        with client.application.app_context():
            from backend.models.room import RoomStatus
            
            mock_user = MagicMock()
            mock_user.openid = "test_user_123"
            mock_user.current_room = "room_123"
            mock_user.has_joined_room.return_value = True
            
            mock_room = MagicMock()
            mock_room.room_id = "room_123"
            mock_room.status = RoomStatus.PLAYING  # 游戏中
            
            mock_user_repo = MagicMock()
            mock_user_repo.get.return_value = mock_user
            mock_room_repo = MagicMock()
            mock_room_repo.get.return_value = mock_room
            
            # 设置必要的配置
            original_config = client.application.config.copy()
            client.application.config['user_repository'] = mock_user_repo
            client.application.config['room_repository'] = mock_room_repo
            client.application.config['notification_service'] = MagicMock()
            
            try:
                # 发送离开房间请求
                response = client.post(
                    "/api/v1/room/leave",
                    headers={"Authorization": f"Bearer {token}"}
                )
            finally:
                # 恢复原始配置
                client.application.config.update(original_config)
            
            # 验证响应
            assert response.status_code == 400
            data = response.json
            assert data["code"] == 400
            assert "Cannot leave room during game" in data["message"]

    def test_leave_room_websocket_notification(self, client, mock_auth_service, mock_notification_service):
        """测试离开房间WebSocket通知"""
        # Mock auth service
        mock_auth_service.verify_token.return_value = "test_user_123"
        
        # 生成有效token
        token = jwt.encode(
            {"sub": "test_user_123", "exp": time.time() + 3600},
            mock_auth_service.secret_key,
            algorithm="HS256"
        )
        
        # 模拟离开房间
        with client.application.app_context():
            mock_user = MagicMock()
            mock_user.openid = "test_user_123"
            mock_user.nickname = "测试用户"
            mock_user.current_room = "room_123"
            mock_user.has_joined_room.return_value = True
            
            mock_room = MagicMock()
            mock_room.room_id = "room_123"
            mock_room.creator = "other_user"
            mock_room.players = ["test_user_123", "other_user"]
            mock_room.status = MagicMock()
            mock_room.status.value = "waiting"
            
            mock_user_repo = MagicMock()
            mock_user_repo.get.return_value = mock_user
            mock_room_repo = MagicMock()
            mock_room_repo.get.return_value = mock_room
            
            # 设置必要的配置
            original_config = client.application.config.copy()
            client.application.config['user_repository'] = mock_user_repo
            client.application.config['room_repository'] = mock_room_repo
            client.application.config['notification_service'] = mock_notification_service
            
            try:
                # 发送离开房间请求
                response = client.post(
                    "/api/v1/room/leave",
                    headers={"Authorization": f"Bearer {token}"}
                )
            finally:
                # 恢复原始配置
                client.application.config.update(original_config)
            
            # 验证WebSocket通知被发送
            mock_notification_service.broadcast_room_event.assert_called_once()
            call_args = mock_notification_service.broadcast_room_event.call_args
            
            # 验证通知参数
            assert call_args[1]["event_type"] == "room.player_left"
            assert call_args[1]["room_id"] == "room_123"
            assert call_args[1]["data"]["user_id"] == "test_user_123"
            assert call_args[1]["data"]["user_nickname"] == "测试用户"
            assert call_args[1]["data"]["is_creator"] == False
            assert call_args[1]["data"]["room_disbanded"] == False