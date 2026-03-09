from pydantic import BaseModel, Field


class UserInfo(BaseModel):
    """用户信息模型"""
    id: str = Field(..., description="用户ID")
    openid: str = Field(..., description="微信OpenID")
    nickname: str = Field(..., description="用户昵称")
    avatar: str = Field(..., description="用户头像URL")
    total_games: int = Field(default=0, description="总游戏场次")
    wins: int = Field(default=0, description="胜利场次")


class LoginData(BaseModel):
    """登录响应数据"""
    token: str = Field(..., description="JWT Token")
    user: UserInfo = Field(..., description="用户信息")


class LoginResponse(BaseModel):
    """登录响应模型"""
    code: int = Field(default=200, description="响应码")
    message: str = Field(default="success", description="响应消息")
    data: LoginData = Field(..., description="响应数据")


class LogoutResponse(BaseModel):
    """登出响应模型"""
    code: int = Field(default=200, description="响应码")
    message: str = Field(default="success", description="响应消息")
    data: dict = Field(default_factory=dict, description="响应数据")
