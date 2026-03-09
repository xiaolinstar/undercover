from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """通用 API 响应模型"""
    code: int
    message: str
    data: T
