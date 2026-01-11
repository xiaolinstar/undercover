#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证异常
定义输入验证相关的异常
"""

from src.exceptions.base import BaseGameException


class ValidationException(BaseGameException):
    """验证异常基类"""
    pass


class InvalidInputError(ValidationException):
    """无效输入"""
    def __init__(self, field: str, value: str):
        super().__init__(
            message=f"无效的输入: {field}",
            error_code="VALID-INPUT-001",
            details={'field': field, 'value': value}
        )


class InvalidRoomIdError(ValidationException):
    """无效房间号"""
    def __init__(self, room_id: str):
        super().__init__(
            message=f"无效的房间号: {room_id}",
            error_code="VALID-ROOM-002",
            details={'room_id': room_id}
        )


class InvalidCommandError(ValidationException):
    """无效命令"""
    def __init__(self, command: str):
        super().__init__(
            message=f"无效的命令: {command}",
            error_code="VALID-CMD-003",
            details={'command': command}
        )
