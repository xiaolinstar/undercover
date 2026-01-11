#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础设施异常
定义基础设施层相关的异常
"""

from typing import Optional
from src.exceptions.base import BaseGameException


class InfrastructureException(BaseGameException):
    """基础设施异常基类"""
    pass


# ============================================================================
# 仓储异常
# ============================================================================

class RepositoryException(InfrastructureException):
    """仓储异常基类"""
    pass


class DataAccessError(RepositoryException):
    """数据访问错误"""
    pass


class SerializationError(RepositoryException):
    """序列化错误"""
    pass


class CacheError(RepositoryException):
    """缓存错误"""
    pass


# ============================================================================
# 外部服务异常
# ============================================================================

class ExternalServiceException(InfrastructureException):
    """外部服务异常基类"""
    pass


class WeChatAPIError(ExternalServiceException):
    """微信API错误"""
    def __init__(self, message: str, cause: Optional[Exception] = None):
        super().__init__(
            message=f"微信API调用失败: {message}",
            error_code="SYS-CONN-002",
            cause=cause
        )


class RedisConnectionError(ExternalServiceException):
    """Redis连接错误"""
    def __init__(self, operation: str, cause: Optional[Exception] = None):
        super().__init__(
            message=f"Redis连接失败: {operation}",
            error_code="SYS-CONN-001",
            details={'operation': operation},
            cause=cause
        )
