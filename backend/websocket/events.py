#!/usr/bin/env python3
"""
WebSocket 事件类型定义
"""

from enum import Enum


class RoomEvent(str, Enum):
    """房间事件"""

    CREATED = "room.created"
    PLAYER_JOINED = "room.player_joined"
    PLAYER_LEFT = "room.player_left"
    PLAYER_READY = "room.player_ready"  # 未来扩展
    DISBANDED = "room.disbanded"  # 未来扩展


class GameEvent(str, Enum):
    """游戏事件"""

    STARTED = "game.started"
    PHASE_CHANGED = "game.phase_changed"  # 未来扩展
    PLAYER_ELIMINATED = "game.player_eliminated"
    ENDED = "game.ended"


class VoteEvent(str, Enum):
    """投票事件"""

    SUBMITTED = "vote.submitted"
    COMPLETED = "vote.completed"  # 未来扩展


class SystemEvent(str, Enum):
    """系统事件"""
    
    CONNECTED = "connected"
    SUBSCRIBED = "subscribed"
    SUBSCRIBE_ERROR = "subscribe_error"
    PONG = "pong"
    SERVER_SHUTDOWN = "server_shutdown"


# 所有事件类型
ALL_EVENTS = {
    **{e.value: e for e in RoomEvent},
    **{e.value: e for e in GameEvent},
    **{e.value: e for e in VoteEvent},
    **{e.value: e for e in SystemEvent},
}
