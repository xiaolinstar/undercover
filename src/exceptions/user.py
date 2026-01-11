#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户相关异常
"""

from src.exceptions.domain import DomainException


class UserException(DomainException):
    """用户异常基类"""
    pass


class UserNotFoundError(UserException):
    """用户不存在"""
    def __init__(self, user_id: str):
        super().__init__(
            message="用户不存在",
            error_code="USER-NOT_FOUND-001",
            details={'user_id': user_id}
        )


class UserNotInRoomError(UserException):
    """用户不在房间"""
    def __init__(self, user_id: str):
        super().__init__(
            message="您不在任何房间中",
            error_code="USER-STATE-002",
            details={'user_id': user_id}
        )


class UserAlreadyInRoomError(UserException):
    """用户已在房间"""
    def __init__(self, user_id: str, room_id: str):
        super().__init__(
            message="您已经在房间中",
            error_code="USER-STATE-003",
            details={'user_id': user_id, 'room_id': room_id}
        )
