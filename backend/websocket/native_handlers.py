#!/usr/bin/env python3
"""
原生 WebSocket 处理器（用于微信小程序）

与 Socket.IO 不同，这是标准的 WebSocket 协议实现
兼容微信小程序的 wx.connectSocket API
"""

import json

from flask import current_app, request
from flask_sock import Sock

from backend.utils.logger import setup_logger
from backend.utils.naming import camel_to_snake_dict, snake_to_camel_dict
from backend.websocket.auth import check_rate_limit, decode_token
from backend.websocket.errors import WSErrorCode, format_ws_error
from backend.websocket.events import SystemEvent
from backend.websocket.monitor import ws_monitor

logger = setup_logger(__name__)

# 创建 Sock 实例
sock = Sock()

# 存储连接映射：{ws_id: {'user_id': str, 'rooms': set}}
connections = {}

# 存储房间订阅：{room_id: set(ws_id)}
room_subscriptions = {}


def init_native_websocket(app):
    """初始化原生 WebSocket"""
    sock.init_app(app)
    logger.info("Native WebSocket initialized for mini-program")


@sock.route("/ws")
def websocket_handler(ws):
    """
    原生 WebSocket 连接处理器

    路径: ws://localhost:5001/ws

    消息格式（JSON）:
    {
        "type": "auth|subscribe|unsubscribe|ping",
        "data": {...}
    }
    """
    ws_id = id(ws)
    user_id = None

    try:
        remote_addr = request.remote_addr or "unknown"
        logger.info(f"Native WebSocket connection attempt: {ws_id} from {remote_addr}")

        # 速率限制
        if not check_rate_limit(f"native_connect:{remote_addr}", limit=20, window=60):
            logger.warning(f"Connection rejected: rate limit exceeded for {remote_addr}")
            ws_monitor.record_error("RATE_LIMIT")
            error_msg = format_ws_error("auth_error", WSErrorCode.RATE_LIMIT_EXCEEDED, "请求过于频繁")
            ws.send(json.dumps(snake_to_camel_dict(error_msg)))
            return

        # 等待认证消息
        auth_message = ws.receive(timeout=10)
        print("auth_message:", auth_message)
        if not auth_message:
            ws_monitor.record_error("AUTH_TIMEOUT")
            error_msg = format_ws_error("auth_error", WSErrorCode.AUTH_TIMEOUT, "认证超时")
            ws.send(json.dumps(snake_to_camel_dict(error_msg)))
            return

        # 解析认证消息
        try:
            auth_data = json.loads(auth_message)
            # 转换为 snake_case
            auth_data = camel_to_snake_dict(auth_data)
        except json.JSONDecodeError:
            ws_monitor.record_error("INVALID_JSON")
            error_msg = format_ws_error("auth_error", WSErrorCode.INVALID_JSON, "无效的 JSON 格式")
            ws.send(json.dumps(snake_to_camel_dict(error_msg)))
            return

        # 验证消息类型
        if auth_data.get("type") != "auth":
            ws_monitor.record_error("AUTH_REQUIRED")
            error_msg = format_ws_error("auth_error", WSErrorCode.AUTH_REQUIRED, "需要先认证")
            ws.send(json.dumps(snake_to_camel_dict(error_msg)))
            return

        # 验证 token
        token = auth_data.get("data", {}).get("token")
        if not token:
            ws_monitor.record_error("MISSING_TOKEN")
            error_msg = format_ws_error("auth_error", WSErrorCode.MISSING_TOKEN, "缺少 token")
            ws.send(json.dumps(snake_to_camel_dict(error_msg)))
            return

        # 解析 JWT token
        user_id, error = decode_token(token)
        if error:
            error_code, error_message = error
            ws_monitor.record_error(f"AUTH_{error_code.value}")
            error_msg = format_ws_error("auth_error", error_code, error_message)
            ws.send(json.dumps(snake_to_camel_dict(error_msg)))
            return

        # 认证成功，存储连接信息
        connections[ws_id] = {"user_id": user_id, "rooms": set(), "ws": ws}
        ws_monitor.record_connection()

        logger.info(f"Native WebSocket authenticated: user_id={user_id}, ws_id={ws_id}")

        # 发送认证成功消息
        success_msg = {
            "type": "system",
            "event": SystemEvent.CONNECTED.value,
            "data": {"connection_id": str(ws_id), "user_id": user_id},
        }
        ws.send(json.dumps(snake_to_camel_dict(success_msg)))
        ws_monitor.record_message_sent()

        # 消息循环
        while True:
            message = ws.receive()
            if message is None:
                break

            try:
                data = json.loads(message)
                # 转换为 snake_case
                data = camel_to_snake_dict(data)
                message_type = data.get("type")

                if message_type == "subscribe":
                    handle_subscribe(ws, ws_id, user_id, data.get("data", {}))
                elif message_type == "unsubscribe":
                    handle_unsubscribe(ws, ws_id, data.get("data", {}))
                elif message_type == "ping":
                    handle_ping(ws)
                else:
                    ws_monitor.record_error("UNKNOWN_TYPE")
                    error_msg = format_ws_error("unknown_type", WSErrorCode.UNKNOWN_TYPE, f"未知的消息类型: {message_type}")
                    ws.send(json.dumps(snake_to_camel_dict(error_msg)))
                    ws_monitor.record_message_sent()

            except json.JSONDecodeError:
                ws_monitor.record_error("INVALID_JSON")
                error_msg = format_ws_error("parse_error", WSErrorCode.INVALID_JSON, "无效的 JSON 格式")
                ws.send(json.dumps(snake_to_camel_dict(error_msg)))
                ws_monitor.record_message_sent()
            except Exception as e:
                logger.error(f"Message handling error: {e}")
                ws_monitor.record_error("INTERNAL_ERROR")
                # 检查是否是 Redis 连接错误
                if "redis" in str(e).lower() or "connection" in str(e).lower():
                    error_msg = format_ws_error("internal_error", WSErrorCode.INTERNAL_ERROR, "Redis 服务未启动，请启动 Redis 服务后重试")
                else:
                    error_msg = format_ws_error("internal_error", WSErrorCode.INTERNAL_ERROR, "服务器内部错误")
                ws.send(json.dumps(snake_to_camel_dict(error_msg)))
                ws_monitor.record_message_sent()

    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        ws_monitor.record_error("WEBSOCKET_EXCEPTION")

    finally:
        # 清理连接
        if ws_id in connections:
            # 从所有房间取消订阅
            for room_id in list(connections[ws_id]["rooms"]):
                if room_id in room_subscriptions:
                    room_subscriptions[room_id].discard(ws_id)
                    if not room_subscriptions[room_id]:
                        del room_subscriptions[room_id]

            del connections[ws_id]
            ws_monitor.record_disconnection()
            logger.info(f"Native WebSocket disconnected: user_id={user_id}, ws_id={ws_id}")


def handle_subscribe(ws, ws_id, user_id, data):
    """处理房间订阅"""
    room_id = data.get("room_id")

    if not room_id:
        error_msg = format_ws_error(
            event=SystemEvent.SUBSCRIBE_ERROR.value,
            code=WSErrorCode.INVALID_REQUEST,
            message="缺少 room_id 参数",
            room_id=None,
        )
        ws.send(json.dumps(snake_to_camel_dict(error_msg)))
        ws_monitor.record_error("INVALID_REQUEST")
        ws_monitor.record_message_sent()
        return

    # 验证用户是否在房间内
    room_repo = current_app.config.get("room_repository")

    if room_repo:
        room = room_repo.get(room_id)
        if not room:
            error_msg = format_ws_error(
                event=SystemEvent.SUBSCRIBE_ERROR.value,
                code=WSErrorCode.ROOM_NOT_FOUND,
                message="房间不存在",
                room_id=room_id,
            )
            ws.send(json.dumps(snake_to_camel_dict(error_msg)))
            ws_monitor.record_error("ROOM_NOT_FOUND")
            ws_monitor.record_message_sent()
            return

        if not room.is_player(user_id):
            error_msg = format_ws_error(
                event=SystemEvent.SUBSCRIBE_ERROR.value,
                code=WSErrorCode.PERMISSION_DENIED,
                message="您不在该房间内",
                room_id=room_id,
            )
            ws.send(json.dumps(snake_to_camel_dict(error_msg)))
            ws_monitor.record_error("PERMISSION_DENIED")
            ws_monitor.record_message_sent()
            return

    # 添加订阅
    if room_id not in room_subscriptions:
        room_subscriptions[room_id] = set()
    room_subscriptions[room_id].add(ws_id)
    connections[ws_id]["rooms"].add(room_id)

    logger.info(f"Room subscribed: user_id={user_id}, room_id={room_id}, ws_id={ws_id}")

    # 发送订阅成功消息
    success_msg = {"type": "system", "event": SystemEvent.SUBSCRIBED.value, "room_id": room_id, "data": {"success": True}}
    ws.send(json.dumps(snake_to_camel_dict(success_msg)))
    ws_monitor.record_message_sent()


def handle_unsubscribe(ws, ws_id, data):
    """处理取消订阅"""
    room_id = data.get("room_id")

    if not room_id:
        return

    # 移除订阅
    if room_id in room_subscriptions:
        room_subscriptions[room_id].discard(ws_id)
        if not room_subscriptions[room_id]:
            del room_subscriptions[room_id]

    if ws_id in connections:
        connections[ws_id]["rooms"].discard(room_id)

    logger.info(f"Room unsubscribed: room_id={room_id}, ws_id={ws_id}")


def handle_ping(ws):
    """处理心跳"""
    ping_msg = {"type": "system", "event": SystemEvent.PONG.value}
    ws.send(json.dumps(snake_to_camel_dict(ping_msg)))
    ws_monitor.record_message_sent()


def broadcast_to_room(room_id: str, event: str, data: dict):
    """
    向房间内所有订阅者广播消息

    Args:
        room_id: 房间ID
        event: 事件类型
        data: 事件数据
    """
    if room_id not in room_subscriptions:
        return

    message_data = {
        "type": "event",
        "event": event,
        "room_id": room_id,
        "timestamp": data.get("timestamp", 0),
        "data": data.get("data", {}),
    }
    # 转换为 camelCase
    message_data = snake_to_camel_dict(message_data)
    message = json.dumps(message_data)

    # 发送给所有订阅者
    disconnected = set()
    for ws_id in room_subscriptions[room_id]:
        if ws_id in connections:
            try:
                connections[ws_id]["ws"].send(message)
                ws_monitor.record_message_sent()
            except Exception as e:
                logger.error(f"Failed to send message to ws_id={ws_id}: {e}")
                ws_monitor.record_error("BROADCAST_EXCEPTION")
                disconnected.add(ws_id)

    # 清理断开的连接
    for ws_id in disconnected:
        room_subscriptions[room_id].discard(ws_id)
        if ws_id in connections:
            del connections[ws_id]

    if not room_subscriptions[room_id]:
        del room_subscriptions[room_id]

    logger.debug(f"Broadcast to room {room_id}: {event}, subscribers: {len(room_subscriptions.get(room_id, []))}")
