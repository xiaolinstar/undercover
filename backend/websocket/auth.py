#!/usr/bin/env python3
"""
WebSocket 认证与限流模块
"""

import time
from functools import wraps

import jwt
from flask import current_app, request
from flask_socketio import emit

from backend.utils.logger import setup_logger
from backend.websocket import socketio
from backend.websocket.errors import WSErrorCode, format_ws_error
from backend.websocket.events import SystemEvent

logger = setup_logger(__name__)

# 一个简单的基于内存的速率限制存储器字典: { "ip:action": [timestamps] }
_rate_limit_store = {}


def decode_token(token: str) -> tuple[str | None, tuple[WSErrorCode, str] | None]:
    """
    解析 JWT token

    :param token: JWT token 字符串
    :return: (user_id, error_tuple)
             如果成功, 返回 (user_id, None)
             如果失败, 返回 (None, (WSErrorCode, error_message))
    """
    if not token:
        return None, (WSErrorCode.MISSING_TOKEN, "缺少 token")

    try:
        payload = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
        user_id = payload.get("sub")
        if not user_id:
            return None, (WSErrorCode.INVALID_TOKEN, "Token 中缺少用户标识")
        return user_id, None

    except jwt.ExpiredSignatureError:
        return None, (WSErrorCode.TOKEN_EXPIRED, "Token 已过期")
    except jwt.InvalidTokenError as e:
        logger.error(f"Invalid token: {e}")
        return None, (WSErrorCode.INVALID_TOKEN, f"Token 无效: {str(e)}")
    except Exception as e:
        logger.error(f"Failed to decode token: {e}")
        return None, (WSErrorCode.INTERNAL_ERROR, "解析 token 异常")


def check_rate_limit(key: str, limit: int = 10, window: int = 60) -> bool:
    """
    简单内存级别的限流校验，通常用于防止过度连接和滥用频繁调用

    :param key: 被限流的对象标识，如 'ip:action'
    :param limit: 时间窗口内允许的最大次数
    :param window: 时间窗口时长 (秒)
    :return: True 代表允许，False 代表已超限拒绝
    """
    now = time.time()

    if key not in _rate_limit_store:
        _rate_limit_store[key] = []

    # 清理过期记录
    _rate_limit_store[key] = [t for t in _rate_limit_store[key] if now - t < window]

    records = _rate_limit_store[key]
    if len(records) >= limit:
        return False

    records.append(now)
    return True


def socketio_auth_required(f):
    """
    Flask-SocketIO 的 JWT 认证装饰器
    验证用户会话是否存在（说明已在 connect 阶段成功验证过 token 并存下 user_id）
    """

    @wraps(f)
    def wrapped(*args, **kwargs):
        session = socketio.server.get_session(request.sid)
        user_id = session.get("user_id") if session else None

        if not user_id:
            logger.warning("WebSocket event unauthorized", extra={"sid": request.sid})
            # 如果没有指定特定事件的返回方式，通常发送 auth_error 或者通用错误，针对 subscribe 事件直接抛出
            emit(
                SystemEvent.SUBSCRIBE_ERROR.value,
                format_ws_error(
                    event=SystemEvent.SUBSCRIBE_ERROR.value,
                    code=WSErrorCode.UNAUTHORIZED,
                    message="未认证！需重新连接进行 JWT 认证。",
                ),
            )
            return

        return f(*args, **kwargs)

    return wrapped
