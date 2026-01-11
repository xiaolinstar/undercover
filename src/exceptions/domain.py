#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
领域异常
定义业务领域相关的异常
"""

from src.exceptions.base import BaseGameException


class DomainException(BaseGameException):
    """领域异常基类"""
    pass
