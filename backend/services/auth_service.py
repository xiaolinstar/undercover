#!/usr/bin/env python3
"""
认证服务
负责小程序登录和 Token 管理
"""

import datetime

import jwt
import requests

from backend.exceptions import ClientException, ExternalServiceException
from backend.models.user import User
from backend.repositories.user_repository import UserRepository


class AuthService:
    """认证服务类"""

    def __init__(self, app_id: str, app_secret: str, user_repo: UserRepository, secret_key: str, redis_client=None):
        self.app_id = app_id
        self.app_secret = app_secret
        self.user_repo = user_repo
        self.secret_key = secret_key
        self.token_expiry_days = 7
        self.redis_client = redis_client
        self.token_blacklist_prefix = "token:blacklist:"

    def login(self, code: str) -> tuple[str, User]:
        """
        小程序登录
        1. 使用 code 换取 openid
        2. 创建或更新用户
        3. 生成 Token
        
        Returns:
            tuple: (token, user) - JWT Token 和用户对象
        """
        # 1. code2session
        openid = self._code2session(code)

        # 2. 获取或创建用户
        user = self.user_repo.get(openid)
        if not user:
            # 新用户，创建一个默认用户
            # 注意：实际生产中可能需要先获取用户授权信息再存入头像昵称等
            user = User(
                openid=openid,
                nickname="微信用户",  # 默认昵称，后续可让用户更新
                avatar="https://xiaolinstar.github.io/xiaolin-docs/sparrow.svg",  # 默认头像为空字符串，后续可用户上传头像更新
                current_room=None,
            )
            self.user_repo.save(user)

        # 3. 生成 Token
        token = self._generate_token(openid)

        return token, user

    def _code2session(self, code: str) -> str:
        """调用微信接口换取 openid"""
        # 开发环境模拟返回 openid（检查是否为空或占位符）
        placeholder_patterns = [
            "your_", "default_", "mock_", "test_"
        ]
        is_placeholder = any(
            self.app_id.startswith(pattern) or self.app_secret.startswith(pattern)
            for pattern in placeholder_patterns
        )
        
        if not self.app_id or not self.app_secret or is_placeholder:
            return f"mock_openid_{code}"
        
        url = "https://api.weixin.qq.com/sns/jscode2session"
        params = {"appid": self.app_id, "secret": self.app_secret, "js_code": code, "grant_type": "authorization_code"}

        try:
            resp = requests.get(url, params=params, timeout=5)
            data = resp.json()
        except requests.RequestException as e:
            raise ExternalServiceException(
                message="微信登录服务不可用",
                error_code="AUTH-WECHAT-UNAVAILABLE",
                cause=e
            ) from e

        if "errcode" in data and data["errcode"] != 0:
            raise ClientException(message=f"微信登录失败: {data.get('errmsg')}", error_code="AUTH-WECHAT-FAIL")

        return data["openid"]

    def _generate_token(self, openid: str) -> str:
        """生成 JWT Token"""
        payload = {
            "sub": openid,
            "iat": datetime.datetime.now(datetime.timezone.utc),
            "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=self.token_expiry_days),
        }
        return jwt.encode(payload, self.secret_key, algorithm="HS256")

    def verify_token(self, token: str) -> str:
        """验证 Token，返回 openid"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            return payload["sub"]
        except jwt.ExpiredSignatureError:
            raise ClientException("登录已过期，请重新登录", error_code="AUTH-EXPIRED") from None
        except jwt.InvalidTokenError:
            raise ClientException("无效的登录凭证", error_code="AUTH-INVALID") from None

    def logout(self, token: str) -> None:
        """
        用户登出
        1. 验证 Token 是否有效
        2. 将 Token 加入黑名单
        
        Args:
            token: JWT Token
            
        Raises:
            ClientException: Token 无效或已过期
        """
        # 1. 验证 Token 并获取过期时间
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            exp = payload.get("exp")
            openid = payload.get("sub")
        except jwt.ExpiredSignatureError:
            raise ClientException("登录已过期，请重新登录", error_code="AUTH-EXPIRED") from None
        except jwt.InvalidTokenError:
            raise ClientException("无效的登录凭证", error_code="AUTH-INVALID") from None
        
        # 2. 将 Token 加入黑名单
        if self.redis_client and exp:
            # 计算剩余过期时间（秒）
            now = datetime.datetime.now(datetime.timezone.utc).timestamp()
            ttl = int(exp - now)
            
            if ttl > 0:
                # 使用 Token 的 openid 和 exp 作为唯一标识
                blacklist_key = f"{self.token_blacklist_prefix}{openid}:{exp}"
                self.redis_client.setex(blacklist_key, ttl, "1")

    def is_token_blacklisted(self, token: str) -> bool:
        """
        检查 Token 是否在黑名单中
        
        Args:
            token: JWT Token
            
        Returns:
            bool: Token 是否在黑名单中
        """
        if not self.redis_client:
            return False
        
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            exp = payload.get("exp")
            openid = payload.get("sub")
            
            if exp and openid:
                blacklist_key = f"{self.token_blacklist_prefix}{openid}:{exp}"
                return self.redis_client.exists(blacklist_key) > 0
        except jwt.InvalidTokenError:
            return False
        
        return False
