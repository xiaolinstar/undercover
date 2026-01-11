#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
游戏相关异常
"""

from src.exceptions.domain import DomainException


class GameException(DomainException):
    """游戏异常基类"""
    pass


class GameNotStartedError(GameException):
    """游戏未开始"""
    def __init__(self):
        super().__init__(
            message="游戏尚未开始",
            error_code="GAME-STATE-001"
        )


class GameAlreadyStartedError(GameException):
    """游戏已开始"""
    def __init__(self):
        super().__init__(
            message="游戏已经开始",
            error_code="GAME-STATE-002"
        )


class GameEndedError(GameException):
    """游戏已结束"""
    def __init__(self):
        super().__init__(
            message="游戏已结束",
            error_code="GAME-STATE-003"
        )


class InsufficientPlayersError(GameException):
    """人数不足"""
    def __init__(self, current_count: int, min_count: int):
        super().__init__(
            message=f"至少需要{min_count}人才能开始游戏",
            error_code="GAME-INVALID-004",
            details={'current_players': current_count, 'min_players': min_count}
        )


class InvalidPlayerStateError(GameException):
    """玩家状态无效"""
    pass


class PlayerEliminatedError(GameException):
    """玩家已被淘汰"""
    def __init__(self, user_id: str):
        super().__init__(
            message="您已被淘汰",
            error_code="GAME-STATE-005",
            details={'user_id': user_id}
        )


class InvalidPlayerIndexError(GameException):
    """玩家序号无效"""
    def __init__(self, index: int, max_index: int):
        super().__init__(
            message=f"序号无效（有效范围：1-{max_index}）",
            error_code="GAME-INVALID-006",
            details={'index': index, 'max_index': max_index}
        )
