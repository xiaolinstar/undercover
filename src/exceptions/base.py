#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础异常类
定义所有自定义异常的基类
"""

from dataclasses import dataclass
from typing import Optional, Dict


@dataclass
class BaseGameException(Exception):
    """基础游戏异常"""
    message: str
    error_code: str
    details: Optional[Dict] = None
    cause: Optional[Exception] = None
    
    def __str__(self) -> str:
        return f"[{self.error_code}] {self.message}"
