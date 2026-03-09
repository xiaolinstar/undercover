#!/usr/bin/env python3
"""
WebSocket 错误码及异常处理模块
"""

from enum import Enum


class WSErrorCode(str, Enum):
    """WebSocket 错误码枚举"""

    # 认证错误
    UNAUTHORIZED = "UNAUTHORIZED"
    MISSING_TOKEN = "MISSING_TOKEN"
    INVALID_TOKEN = "INVALID_TOKEN"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    AUTH_TIMEOUT = "AUTH_TIMEOUT"
    AUTH_REQUIRED = "AUTH_REQUIRED"

    # 速率和限制
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"

    # 请求错误
    INVALID_REQUEST = "INVALID_REQUEST"
    INVALID_JSON = "INVALID_JSON"
    UNKNOWN_TYPE = "UNKNOWN_TYPE"

    # 业务错误
    ROOM_NOT_FOUND = "ROOM_NOT_FOUND"
    PERMISSION_DENIED = "PERMISSION_DENIED"

    # 系统错误
    INTERNAL_ERROR = "INTERNAL_ERROR"


def format_ws_error(event: str, code: WSErrorCode, message: str, **kwargs) -> dict:
    """
    生成标准化的 WebSocket 错误响应
    :param event: 触发错误的事件类型字符串
    :param code: 错误代码 (WSErrorCode 枚举)
    :param message: 返回给客户端的错误描述
    :param kwargs: 其他需要直接暴露在根部的字段 (如 room_id 等)
    :return: 序列化好的错误数据字典
    """
    error_data = {"type": "error", "event": event, "data": {"error": code.value, "message": message}}
    error_data.update(kwargs)
    return error_data
