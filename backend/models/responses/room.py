from pydantic import BaseModel, Field


class PlayerInfo(BaseModel):
    """玩家信息模型"""
    uid: str = Field(..., description="用户ID")
    seat: int = Field(..., description="座位号")
    nickname: str = Field(..., description="用户昵称")
    avatar: str = Field(..., description="用户头像URL")
    is_ready: bool = Field(default=False, description="是否准备")
    is_eliminated: bool = Field(default=False, description="是否被淘汰")


class RoomConfig(BaseModel):
    """房间配置模型"""
    player_count: int = Field(default=6, description="玩家数量")
    undercover_count: int = Field(default=1, description="卧底数量")
    whiteboard_count: int = Field(default=0, description="白板数量")


class RoomInfo(BaseModel):
    """房间信息模型"""
    room_id: str = Field(..., description="房间ID")
    room_code: str = Field(..., description="房间短码")
    host_id: str = Field(..., description="房主ID")
    status: str = Field(..., description="房间状态")
    players: list[PlayerInfo] = Field(default_factory=list, description="玩家列表")


class CreateRoomData(BaseModel):
    """创建房间响应数据"""
    room_id: str = Field(..., description="房间ID")
    room_code: str = Field(..., description="房间短码")
    host_id: str = Field(..., description="房主ID")
    status: str = Field(..., description="房间状态")
    players: list[PlayerInfo] = Field(default_factory=list, description="玩家列表")
    max_players: int = Field(default=6, description="最大玩家数量")
    created_at: str = Field(..., description="创建时间")


class CreateRoomResponse(BaseModel):
    """创建房间响应模型"""
    code: int = Field(default=200, description="响应码")
    message: str = Field(default="success", description="响应消息")
    data: CreateRoomData = Field(..., description="响应数据")


class JoinRoomData(BaseModel):
    """加入房间响应数据"""
    room_id: str = Field(..., description="房间ID")
    room_code: str = Field(..., description="房间短码")
    host_id: str = Field(..., description="房主ID")
    status: str = Field(..., description="房间状态")
    players: list[PlayerInfo] = Field(default_factory=list, description="玩家列表")


class JoinRoomResponse(BaseModel):
    """加入房间响应模型"""
    code: int = Field(default=200, description="响应码")
    message: str = Field(default="success", description="响应消息")
    data: JoinRoomData = Field(..., description="响应数据")


class GetRoomData(BaseModel):
    """获取房间响应数据"""
    room_id: str = Field(..., description="房间ID")
    room_code: str = Field(..., description="房间短码")
    host_id: str = Field(..., description="房主ID")
    status: str = Field(..., description="房间状态")
    player_count: int = Field(..., description="玩家数量")
    players: list[PlayerInfo] = Field(default_factory=list, description="玩家列表")


class GetRoomResponse(BaseModel):
    """获取房间响应模型"""
    code: int = Field(default=200, description="响应码")
    message: str = Field(default="success", description="响应消息")
    data: GetRoomData = Field(..., description="响应数据")
