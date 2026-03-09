#!/usr/bin/env python3
"""
WebSocket 事件处理器
处理客户端的 WebSocket 连接、订阅等事件
"""

from flask import current_app, request
from flask_socketio import emit, join_room, leave_room

from backend.utils.logger import setup_logger
from backend.websocket import socketio
from backend.websocket.auth import check_rate_limit, decode_token, socketio_auth_required
from backend.websocket.errors import WSErrorCode, format_ws_error
from backend.websocket.events import SystemEvent
from backend.websocket.monitor import ws_monitor

logger = setup_logger(__name__)


@socketio.on("connect")
def handle_connect(auth):
    """
    处理客户端连接

    流程：
    1. 验证 JWT token
    2. 存储用户信息到 session
    3. 返回连接成功消息

    Args:
        auth: 认证信息，格式 {"token": "jwt_token"}

    Returns:
        False: 拒绝连接
        None: 接受连接
    """
    try:
        remote_addr = request.remote_addr or "unknown"

        # 速率限制：按 IP 限制频繁连接 (60秒内最多充许 20 次连接尝试)
        if not check_rate_limit(f"connect:{remote_addr}", limit=20, window=60):
            logger.warning(f"Connection rejected: rate limit exceeded for {remote_addr}")
            ws_monitor.record_error("RATE_LIMIT")
            emit("error", format_ws_error("auth_error", WSErrorCode.RATE_LIMIT_EXCEEDED, "请求过于频繁"))
            return False

        # 验证 token
        if not auth or "token" not in auth:
            logger.warning("Connection rejected: missing token", extra={"remote_addr": remote_addr})
            ws_monitor.record_error("AUTH_MISSING")
            return False

        token = auth["token"]

        # 解析 JWT token
        user_id, error = decode_token(token)
        if error:
            error_code, error_message = error
            logger.warning(
                f"Connection rejected: {error_code.value} - {error_message}", extra={"remote_addr": remote_addr}
            )
            ws_monitor.record_error(f"AUTH_{error_code.value}")
            return False

        # 存储用户信息（flask-socketio 会自动管理 session）
        # 注意：这里不使用 flask session，而是使用 socketio 的 session
        # 可以通过 request.sid 获取连接ID

        logger.info(
            "WebSocket connected", extra={"user_id": user_id, "sid": request.sid, "remote_addr": request.remote_addr}
        )

        # 返回连接成功消息
        emit(
            SystemEvent.CONNECTED.value,
            {"event": SystemEvent.CONNECTED.value, "data": {"connection_id": request.sid, "user_id": user_id}},
        )

        # 将 user_id 存储在连接的环境中（用于后续验证）
        # flask-socketio 会自动管理这个映射
        try:
            socketio.server.save_session(request.sid, {"user_id": user_id})
        except KeyError:
            # 兼容 flask_socketio test_client 环境
            pass

        ws_monitor.record_connection()
        ws_monitor.record_message_sent()

    except Exception as e:
        logger.error(f"Connection error: {e}", extra={"remote_addr": request.remote_addr})
        ws_monitor.record_error("CONNECT_EXCEPTION")
        return False


@socketio.on("disconnect")
def handle_disconnect():
    """
    处理客户端断开连接

    flask-socketio 会自动清理 room 订阅
    """
    try:
        try:
            session = socketio.server.get_session(request.sid)
        except KeyError:
            session = None
        user_id = session.get("user_id") if session else None

        logger.info("WebSocket disconnected", extra={"user_id": user_id, "sid": request.sid})
        ws_monitor.record_disconnection()

    except Exception as e:
        logger.error(f"Disconnect error: {e}")
        ws_monitor.record_error("DISCONNECT_EXCEPTION")


@socketio.on("subscribe")
@socketio_auth_required
def handle_subscribe(data):
    """
    处理房间订阅

    流程：
    1. 验证用户是否在房间内
    2. 加入 SocketIO room
    3. 返回订阅成功消息

    Args:
        data: {"room_id": "8888"}
    """
    try:
        room_id = data.get("room_id") if isinstance(data, dict) else None

        if not room_id:
            emit(
                SystemEvent.SUBSCRIBE_ERROR.value,
                format_ws_error(
                    event=SystemEvent.SUBSCRIBE_ERROR.value,
                    code=WSErrorCode.INVALID_REQUEST,
                    message="缺少 room_id 参数",
                    room_id=None,
                ),
            )
            ws_monitor.record_message_sent()
            return

        # 获取用户信息
        try:
            session = socketio.server.get_session(request.sid)
        except KeyError:
            session = None
        user_id = session.get("user_id") if session else None

        # 验证用户是否在房间内
        room_repo = current_app.config.get("room_repository")
        user_repo = current_app.config.get("user_repository")

        if room_repo and user_repo:
            # 检查房间是否存在
            room = room_repo.get(room_id)
            if not room:
                emit(
                    SystemEvent.SUBSCRIBE_ERROR.value,
                    format_ws_error(
                        event=SystemEvent.SUBSCRIBE_ERROR.value,
                        code=WSErrorCode.ROOM_NOT_FOUND,
                        message="房间不存在",
                        room_id=room_id,
                    ),
                )
                ws_monitor.record_message_sent()
                return

            # 检查用户是否在房间内
            if not room.is_player(user_id):
                emit(
                    SystemEvent.SUBSCRIBE_ERROR.value,
                    format_ws_error(
                        event=SystemEvent.SUBSCRIBE_ERROR.value,
                        code=WSErrorCode.PERMISSION_DENIED,
                        message="您不在该房间内",
                        room_id=room_id,
                    ),
                )
                ws_monitor.record_message_sent()
                return
        else:
            logger.warning("Repository not available for permission check")

        # 加入 SocketIO room
        join_room(room_id)

        logger.info("Room subscribed", extra={"user_id": user_id, "room_id": room_id, "sid": request.sid})

        # 返回订阅成功消息
        emit(
            SystemEvent.SUBSCRIBED.value,
            {"event": SystemEvent.SUBSCRIBED.value, "room_id": room_id, "data": {"success": True}},
        )
        ws_monitor.record_message_sent()

    except Exception as e:
        room_id = data.get("room_id") if isinstance(data, dict) else None
        logger.error(f"Subscribe error: {e}", extra={"room_id": room_id})
        emit(
            SystemEvent.SUBSCRIBE_ERROR.value,
            format_ws_error(
                event=SystemEvent.SUBSCRIBE_ERROR.value,
                code=WSErrorCode.INTERNAL_ERROR,
                message="订阅失败",
                room_id=room_id,
            ),
        )
        ws_monitor.record_message_sent()
        ws_monitor.record_error("SUBSCRIBE_EXCEPTION")


@socketio.on("unsubscribe")
@socketio_auth_required
def handle_unsubscribe(data):
    """
    处理取消订阅

    Args:
        data: {"room_id": "8888"}
    """
    try:
        room_id = data.get("room_id")

        if not room_id:
            return

        # 获取用户信息
        session = socketio.server.get_session(request.sid)
        user_id = session.get("user_id")

        # 离开 SocketIO room
        leave_room(room_id)

        logger.info("Room unsubscribed", extra={"user_id": user_id, "room_id": room_id, "sid": request.sid})

    except Exception as e:
        logger.error(f"Unsubscribe error: {e}")
        ws_monitor.record_error("UNSUBSCRIBE_EXCEPTION")


@socketio.on("ping")
@socketio_auth_required
def handle_ping():
    """
    处理心跳

    客户端定期发送 ping，服务器响应 pong
    """
    emit(SystemEvent.PONG.value, {"event": SystemEvent.PONG.value})
    ws_monitor.record_message_sent()
