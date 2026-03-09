from unittest.mock import MagicMock, patch

import pytest

from backend.exceptions import ClientException, ExternalServiceException
from backend.models.user import User
from backend.repositories.user_repository import UserRepository
from backend.services.auth_service import AuthService


@pytest.fixture
def mock_redis():
    """模拟 Redis 客户端"""
    return MagicMock()


@pytest.fixture
def user_repo(mock_redis):
    """创建用户仓储实例"""
    return UserRepository(mock_redis)


@pytest.fixture
def auth_service(user_repo):
    """创建认证服务实例"""
    return AuthService(
        app_id="test_app_id",
        app_secret="test_app_secret",
        user_repo=user_repo,
        secret_key="test_secret_key",
        redis_client=MagicMock()
    )


class TestAuthService:
    """AuthService 单元测试类"""

    def test_login_new_user(self, auth_service, user_repo):
        """测试新用户登录"""
        with patch.object(auth_service, '_code2session', return_value='test_openid_123'):
            with patch.object(user_repo, 'get', return_value=None):
                with patch.object(user_repo, 'save') as mock_save:
                    token, user = auth_service.login("test_code")
                    
                    assert token is not None
                    assert user.openid == 'test_openid_123'
                    assert user.nickname == "微信用户"
                    assert user.current_room is None
                    mock_save.assert_called_once()

    def test_login_existing_user(self, auth_service, user_repo):
        """测试已有用户登录"""
        existing_user = User(
            openid='test_openid_123',
            nickname="测试用户",
            current_room=None,
            total_games=10,
            wins=5
        )
        
        with patch.object(auth_service, '_code2session', return_value='test_openid_123'):
            with patch.object(user_repo, 'get', return_value=existing_user):
                token, user = auth_service.login("test_code")
                
                assert token is not None
                assert user.openid == 'test_openid_123'
                assert user.nickname == "测试用户"
                assert user.total_games == 10
                assert user.wins == 5

    def test_code2session_with_placeholder(self, auth_service):
        """测试开发环境模拟 openid（占位符）"""
        with patch('requests.get') as mock_get:
            result = auth_service._code2session("test_code")
            
            assert result == "mock_openid_test_code"
            mock_get.assert_not_called()

    def test_code2session_with_empty_credentials(self, auth_service):
        """测试开发环境模拟 openid（空凭据）"""
        auth_service_empty = AuthService(
            app_id="",
            app_secret="",
            user_repo=auth_service.user_repo,
            secret_key="test_secret_key"
        )
        
        result = auth_service_empty._code2session("test_code")
        
        assert result == "mock_openid_test_code"

    def test_code2session_wechat_success(self):
        """测试微信接口成功调用"""
        auth_service = AuthService(
            app_id="real_app_id",
            app_secret="real_app_secret",
            user_repo=MagicMock(),
            secret_key="test_secret_key"
        )
        
        mock_response = MagicMock()
        mock_response.json.return_value = {"openid": "real_openid_123"}
        
        with patch('requests.get', return_value=mock_response) as mock_get:
            result = auth_service._code2session("test_code")
            
            assert result == "real_openid_123"
            mock_get.assert_called_once()

    def test_code2session_wechat_failure(self):
        """测试微信接口失败调用"""
        auth_service = AuthService(
            app_id="real_app_id",
            app_secret="real_app_secret",
            user_repo=MagicMock(),
            secret_key="test_secret_key"
        )
        
        mock_response = MagicMock()
        mock_response.json.return_value = {"errcode": 40001, "errmsg": "invalid code"}
        
        with patch('requests.get', return_value=mock_response):
            with pytest.raises(ClientException) as exc_info:
                auth_service._code2session("invalid_code")
            
            assert "微信登录失败" in str(exc_info.value)

    def test_code2session_wechat_unavailable(self):
        """测试微信接口不可用"""
        auth_service = AuthService(
            app_id="real_app_id",
            app_secret="real_app_secret",
            user_repo=MagicMock(),
            secret_key="test_secret_key"
        )
        
        import requests
        with patch('requests.get', side_effect=requests.RequestException("Network error")):
            with pytest.raises(ExternalServiceException) as exc_info:
                auth_service._code2session("test_code")
            
            assert "微信登录服务不可用" in str(exc_info.value)

    def test_generate_token(self, auth_service):
        """测试 Token 生成"""
        import jwt
        
        token = auth_service._generate_token("test_openid")
        
        assert token is not None
        assert isinstance(token, str)
        
        # 验证 Token 可以被解码
        payload = jwt.decode(token, auth_service.secret_key, algorithms=["HS256"])
        assert payload["sub"] == "test_openid"
        assert "exp" in payload
        assert "iat" in payload

    def test_verify_token_success(self, auth_service):
        """测试 Token 验证成功"""
        import jwt
        
        token = jwt.encode(
            {"sub": "test_openid", "exp": 9999999999},
            auth_service.secret_key,
            algorithm="HS256"
        )
        
        openid = auth_service.verify_token(token)
        
        assert openid == "test_openid"

    def test_verify_token_expired(self, auth_service):
        """测试 Token 验证过期"""
        import jwt
        import time
        
        expired_token = jwt.encode(
            {"sub": "test_openid", "exp": time.time() - 3600},
            auth_service.secret_key,
            algorithm="HS256"
        )
        
        with pytest.raises(ClientException) as exc_info:
            auth_service.verify_token(expired_token)
        
        assert "登录已过期" in str(exc_info.value)

    def test_verify_token_invalid(self, auth_service):
        """测试 Token 验证无效"""
        invalid_token = "invalid.token.string"
        
        with pytest.raises(ClientException) as exc_info:
            auth_service.verify_token(invalid_token)
        
        assert "无效的登录凭证" in str(exc_info.value)

    def test_logout_success(self, auth_service):
        """测试成功登出"""
        import jwt
        import time
        
        # 生成一个有效的 Token
        token = jwt.encode(
            {"sub": "test_openid", "exp": time.time() + 3600},
            auth_service.secret_key,
            algorithm="HS256"
        )
        
        # 调用 logout
        auth_service.logout(token)
        
        # 验证 Redis 的 setex 方法被调用
        auth_service.redis_client.setex.assert_called_once()
        
        # 验证调用参数
        call_args = auth_service.redis_client.setex.call_args
        key = call_args[0][0]
        ttl = call_args[0][1]
        value = call_args[0][2]
        
        assert "token:blacklist:test_openid:" in key
        assert ttl > 0
        assert value == "1"

    def test_logout_expired_token(self, auth_service):
        """测试登出过期 Token"""
        import jwt
        import time
        
        # 生成一个过期的 Token
        expired_token = jwt.encode(
            {"sub": "test_openid", "exp": time.time() - 3600},
            auth_service.secret_key,
            algorithm="HS256"
        )
        
        # 应该抛出异常
        with pytest.raises(ClientException) as exc_info:
            auth_service.logout(expired_token)
        
        assert "登录已过期" in str(exc_info.value)
        
        # Redis 的 setex 方法不应该被调用
        auth_service.redis_client.setex.assert_not_called()

    def test_logout_invalid_token(self, auth_service):
        """测试登出无效 Token"""
        invalid_token = "invalid.token.string"
        
        # 应该抛出异常
        with pytest.raises(ClientException) as exc_info:
            auth_service.logout(invalid_token)
        
        assert "无效的登录凭证" in str(exc_info.value)
        
        # Redis 的 setex 方法不应该被调用
        auth_service.redis_client.setex.assert_not_called()

    def test_is_token_blacklisted_true(self, auth_service):
        """测试 Token 在黑名单中"""
        import jwt
        import time
        
        # 生成一个有效的 Token
        token = jwt.encode(
            {"sub": "test_openid", "exp": time.time() + 3600},
            auth_service.secret_key,
            algorithm="HS256"
        )
        
        # Mock Redis 返回 True
        auth_service.redis_client.exists.return_value = 1
        
        # 检查 Token 是否在黑名单中
        result = auth_service.is_token_blacklisted(token)
        
        assert result is True
        auth_service.redis_client.exists.assert_called_once()

    def test_is_token_blacklisted_false(self, auth_service):
        """测试 Token 不在黑名单中"""
        import jwt
        import time
        
        # 生成一个有效的 Token
        token = jwt.encode(
            {"sub": "test_openid", "exp": time.time() + 3600},
            auth_service.secret_key,
            algorithm="HS256"
        )
        
        # Mock Redis 返回 False
        auth_service.redis_client.exists.return_value = 0
        
        # 检查 Token 是否在黑名单中
        result = auth_service.is_token_blacklisted(token)
        
        assert result is False
        auth_service.redis_client.exists.assert_called_once()

    def test_is_token_blacklisted_no_redis(self):
        """测试没有 Redis 客户端时"""
        auth_service = AuthService(
            app_id="test_app_id",
            app_secret="test_app_secret",
            user_repo=MagicMock(),
            secret_key="test_secret_key",
            redis_client=None
        )
        
        import jwt
        import time
        
        # 生成一个有效的 Token
        token = jwt.encode(
            {"sub": "test_openid", "exp": time.time() + 3600},
            auth_service.secret_key,
            algorithm="HS256"
        )
        
        # 没有 Redis 客户端时，应该返回 False
        result = auth_service.is_token_blacklisted(token)
        
        assert result is False
