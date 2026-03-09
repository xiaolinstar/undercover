import jwt
import time
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def mock_auth_service():
    """模拟 AuthService"""
    service = MagicMock()
    service.secret_key = "test_secret_key"
    return service


@pytest.fixture
def app_with_mock_auth(app, mock_auth_service):
    """创建带有 Mock AuthService 的应用"""
    app.config['auth_service'] = mock_auth_service
    return app


@pytest.mark.usefixtures("app_with_mock_auth")
class TestAuthAPI:
    """Auth API 单元测试类"""

    def test_login_success(self, client, mock_auth_service):
        """测试登录成功"""
        # Mock 返回值
        mock_user = MagicMock()
        mock_user.openid = "test_openid_123"
        mock_user.nickname = "测试用户"
        mock_user.avatar = "https://example.com/avatar.png"
        mock_user.total_games = 10
        mock_user.wins = 5
        
        mock_auth_service.login.return_value = ("test_token", mock_user)
        
        # 调用登录接口
        resp = client.post("/api/v1/auth/login", json={"code": "test_code"})
        
        # 验证响应
        assert resp.status_code == 200
        data = resp.json
        assert data["code"] == 200
        assert data["message"] == "success"
        assert data["data"]["token"] == "test_token"
        assert data["data"]["user"]["openid"] == "test_openid_123"
        assert data["data"]["user"]["nickname"] == "测试用户"
        
        # 验证 AuthService.login 被调用
        mock_auth_service.login.assert_called_once_with("test_code")

    def test_login_missing_code(self, client):
        """测试缺少 code 参数"""
        resp = client.post("/api/v1/auth/login", json={})
        
        assert resp.status_code == 400
        data = resp.json
        assert data["code"] == 400
        assert "Missing 'code' parameter" in data["message"]

    def test_logout_success(self, client, mock_auth_service):
        """测试登出成功"""
        # Mock logout 方法
        mock_auth_service.logout.return_value = None
        
        # 生成一个有效的 Token
        token = jwt.encode(
            {"sub": "test_openid", "exp": time.time() + 3600},
            mock_auth_service.secret_key,
            algorithm="HS256"
        )
        
        # 调用登出接口
        resp = client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # 验证响应
        assert resp.status_code == 200
        data = resp.json
        assert data["code"] == 200
        assert data["message"] == "success"
        
        # 验证 AuthService.logout 被调用
        mock_auth_service.logout.assert_called_once_with(token)

    def test_logout_missing_auth_header(self, client):
        """测试缺少 Authorization header"""
        resp = client.post("/api/v1/auth/logout")
        
        assert resp.status_code == 401
        data = resp.json
        assert data["code"] == 401
        assert "Missing or invalid Authorization header" in data["message"]

    def test_logout_invalid_auth_header(self, client):
        """测试无效的 Authorization header"""
        resp = client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": "InvalidFormat token"}
        )
        
        assert resp.status_code == 401
        data = resp.json
        assert data["code"] == 401
        assert "Missing or invalid Authorization header" in data["message"]

    def test_logout_service_error(self, client, mock_auth_service):
        """测试登出时服务错误"""
        # Mock logout 方法抛出异常
        mock_auth_service.logout.side_effect = Exception("Service error")
        
        # 生成一个有效的 Token
        token = jwt.encode(
            {"sub": "test_openid", "exp": time.time() + 3600},
            mock_auth_service.secret_key,
            algorithm="HS256"
        )
        
        # 调用登出接口
        resp = client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # 验证响应
        assert resp.status_code == 500
        data = resp.json
        assert data["code"] == 500
        assert "系统繁忙" in data["message"]
