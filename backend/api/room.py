from flask import jsonify, request, current_app
import uuid

from . import api_bp
from .decorators import login_required
from backend.models.room import Room, RoomStatus
from backend.models.responses import (
    CreateRoomResponse, CreateRoomData,
    JoinRoomResponse, JoinRoomData, PlayerInfo,
    GetRoomResponse, GetRoomData
)


@api_bp.route("/room/create", methods=["POST"])
@login_required
def create_room():
    """
    创建房间接口
    ---
    tags:
      - Room 模块
    parameters:
      - in: header
        name: Authorization
        type: string
        required: true
        description: "Bearer Token (包含用户信息)"
        example: "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    responses:
      200:
        description: "创建成功，返回房间信息"
        schema:
          type: object
          properties:
            code:
              type: integer
              example: 200
            message:
              type: string
              example: "success"
            data:
              type: object
              properties:
                room_id:
                  type: string
                  example: "abc12345"
                room_code:
                  type: string
                  example: "1234"
                host_id:
                  type: string
                  example: "user_123"
                status:
                  type: string
                  example: "waiting"
    """
    # 从Token中获取用户信息（通过@login_required装饰器设置）
    creator = getattr(request, 'current_user_id', None)
    if not creator:
        return jsonify({"code": 401, "message": "User not authenticated", "data": {}}), 401

    # 获取 RoomRepository
    room_repo = current_app.config.get('room_repository')
    if not room_repo:
        return jsonify({"code": 500, "message": "Service not available", "data": {}}), 500

    try:
        # 获取游戏服务
        game_service = current_app.config.get('game_service')
        if not game_service:
            return jsonify({"code": 500, "message": "Game service not available", "data": {}}), 500
        
        # 使用游戏服务创建房间
        success, room_id = game_service.create_room(creator)
        if not success:
            return jsonify({"code": 500, "message": "Failed to create room", "data": {}}), 500
        
        # 获取创建的房间信息
        room = room_repo.get(room_id)
        if not room:
            return jsonify({"code": 500, "message": "Room not found after creation", "data": {}}), 500
        
        # 获取用户信息（创建房间的用户一定存在）
        user_repo = current_app.config.get('user_repository')
        if not user_repo:
            return jsonify({"code": 500, "message": "User repository not available", "data": {}}), 500
        
        user = user_repo.get(creator)
        if not user:
            return jsonify({"code": 500, "message": "User not found", "data": {}}), 500
        
        # 打印日志，查看user信息
        current_app.logger.info(f"[create_room] creator={creator}, user={user}")

        # 构建玩家列表（房主作为第一个玩家）
        players = [
            PlayerInfo(
                uid=user.openid,
                seat=1,
                nickname=user.nickname or "玩家1",
                avatar=user.avatar,  # 使用用户的头像信息
                is_ready=False,
                is_eliminated=False
            )
        ]
        
        # 构建响应数据
        create_room_data = CreateRoomData(
            room_id=room_id,
            room_code=room.room_code,
            host_id=creator,
            status=room.status.value,
            players=players,
            max_players=6,  # 默认最大6人
            created_at=room.created_at.isoformat()
        )
        
        response = CreateRoomResponse(
            code=200,
            message="success",
            data=create_room_data
        )

        # 发送WebSocket通知 - 房间创建事件
        notification_service = current_app.config.get('notification_service')
        if notification_service:
            try:
                # 构建房间创建事件数据
                event_data = {
                    "room_id": room_id,
                    "room_code": room.room_code,
                    "creator": creator,
                    "creator_nickname": user.nickname if user else "未知用户",
                    "player_count": len(room.players),
                    "status": room.status.value,
                    "created_at": room.created_at.isoformat() if room.created_at else None
                }
                
                # 发送房间创建通知
                notification_service.broadcast_room_event(
                    room_id=room_id,
                    event_type="room.created",
                    data=event_data
                )
                
                current_app.logger.info(f"Room creation notification sent for room {room_id}")
                
            except Exception as e:
                current_app.logger.warning(f"Failed to send room creation notification: {str(e)}")

        return jsonify(response.model_dump())
    except Exception as e:
        current_app.logger.exception(f"Create room failed: {str(e)}")
        return jsonify({"code": 500, "message": "Create room failed", "data": {}}), 500


@api_bp.route("/room/join", methods=["POST"])
@login_required
def join_room():
    """
    加入房间
    ---
    tags:
      - Room 模块
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            room_id:
              type: string
              example: "8888"
            room_code:
              type: string
              example: "1234"
            user_id:
              type: string
              example: "user_002"
    responses:
      200:
        description: "加入成功，返回最新房间和座位状态"
    """
    data = request.get_json() or {}
    room_id = data.get("room_id")
    room_code = data.get("room_code")
    user_id = getattr(request, 'current_user_id', f"user_{uuid.uuid4().hex[:6]}")

    if not room_id and not room_code:
        return jsonify({"code": 400, "message": "Missing room_id or room_code parameter", "data": {}}), 400

    # 获取 RoomRepository
    room_repo = current_app.config.get('room_repository')
    if not room_repo:
        return jsonify({"code": 500, "message": "Service not available", "data": {}}), 500

    try:
        # 获取房间
        room = None
        if room_id:
            room = room_repo.get(room_id)
        elif room_code:
            # 通过 room_code 查找房间
            room = room_repo.get_by_code(room_code)
        
        if not room:
            return jsonify({"code": 404, "message": "Room not found", "data": {}}), 404

        # 加入房间
        if user_id not in room.players:
            room.players.append(user_id)
            room_repo.save(room)
        
        # 更新用户的当前房间
        user_repo = current_app.config.get('user_repository')
        if user_repo:
            from backend.models.user import User
            user = user_repo.get(user_id)
            if user:
                user.current_room = room.room_id
                user_repo.save(user)

        # 使用 Pydantic 模型构建玩家信息
        players = []
        for i, player in enumerate(room.players):
            player_info = PlayerInfo(
                uid=player,
                seat=i + 1,
                nickname=f"玩家{i+1}",
                avatar="https://example.com/avatar.png",
                is_ready=i == 0,  # 房主默认准备
                is_eliminated=room.is_eliminated(player)
            )
            players.append(player_info)
        
        # 使用 Pydantic 模型构建响应
        join_room_data = JoinRoomData(
            room_id=room.room_id,
            room_code=room.room_code,
            host_id=room.creator,
            status=room.status.value,
            players=players
        )
        
        response = JoinRoomResponse(
            code=200,
            message="success",
            data=join_room_data
        )

        return jsonify(response.model_dump())
    except Exception as e:
        return jsonify({"code": 500, "message": f"Join room failed: {str(e)}", "data": {}}), 500


@api_bp.route("/room/<room_id>", methods=["GET"])
@login_required
def get_room(room_id):
    """
    获取房间状态
    ---
    tags:
      - Room 模块
    parameters:
      - in: path
        name: room_id
        type: string
        required: true
        description: "房间ID"
    responses:
      200:
        description: "返回房间详细信息"
    """
    # 获取 RoomRepository
    room_repo = current_app.config.get('room_repository')
    if not room_repo:
        return jsonify({"code": 500, "message": "Service not available", "data": {}}), 500

    try:
        # 获取房间
        room = room_repo.get(room_id)
        if not room:
            return jsonify({"code": 404, "message": "Room not found", "data": {}}), 404

        # 使用 Pydantic 模型构建玩家信息
        players = []
        for i, player in enumerate(room.players):
            player_info = PlayerInfo(
                uid=player,
                seat=i + 1,
                nickname=f"玩家{i+1}",
                avatar="https://example.com/avatar.png",
                is_ready=i == 0,  # 房主默认准备
                is_eliminated=room.is_eliminated(player)
            )
            players.append(player_info)
        
        # 使用 Pydantic 模型构建响应
        get_room_data = GetRoomData(
            room_id=room_id,
            room_code=room.room_code,
            host_id=room.creator,
            status=room.status.value,
            player_count=len(room.players),
            players=players
        )
        
        response = GetRoomResponse(
            code=200,
            message="success",
            data=get_room_data
        )

        return jsonify(response.model_dump())
    except Exception as e:
        return jsonify({"code": 500, "message": f"Get room failed: {str(e)}", "data": {}}), 500


@api_bp.route("/room/leave", methods=["POST"])
@login_required
def leave_room():
    """
    离开房间接口
    ---
    tags:
      - Room 模块
    parameters:
      - in: header
        name: Authorization
        type: string
        required: true
        description: "Bearer Token (包含用户信息)"
        example: "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    responses:
      200:
        description: "离开房间成功"
        schema:
          type: object
          properties:
            code:
              type: integer
              example: 200
            message:
              type: string
              example: "success"
            data:
              type: object
              properties: {}
      404:
        description: "用户不在任何房间中"
      500:
        description: "服务器错误"
    """
    # 从Token中获取用户信息（通过@login_required装饰器设置）
    user_id = getattr(request, 'current_user_id', None)
    if not user_id:
        return jsonify({"code": 401, "message": "User not authenticated", "data": {}}), 401

    # 获取用户和房间仓库
    user_repo = current_app.config.get('user_repository')
    room_repo = current_app.config.get('room_repository')
    game_service = current_app.config.get('game_service')
    
    if not user_repo or not room_repo or not game_service:
        return jsonify({"code": 500, "message": "Service not available", "data": {}}), 500

    try:
        # 获取用户信息
        user = user_repo.get(user_id)
        if not user:
            return jsonify({"code": 404, "message": "User not found", "data": {}}), 404
        
        # 检查用户是否在房间中
        if not user.has_joined_room():
            return jsonify({"code": 404, "message": "User not in any room", "data": {}}), 404
        
        room_id = user.current_room
        room = room_repo.get(room_id)
        if not room:
            # 如果房间不存在，直接清理用户状态
            user.leave_room()
            user_repo.save(user)
            return jsonify({"code": 200, "message": "success", "data": {}}), 200
        
        # 检查游戏状态，游戏中不能离开
        if room.status == RoomStatus.PLAYING:
            return jsonify({"code": 400, "message": "Cannot leave room during game", "data": {}}), 400
        
        # 检查是否为房主，如果是房主需要转移或解散房间
        is_creator = (room.creator == user_id)
        if is_creator and len(room.players) > 1:
            # 房主离开且房间还有其他玩家，转移房主权限
            room.creator = next((p for p in room.players if p != user_id), room.players[0])
            room_repo.save(room)
        
        # 从房间中移除玩家
        if user_id in room.players:
            room.players.remove(user_id)
            room_repo.save(room)
        
        # 更新用户状态
        user.leave_room()
        user_repo.save(user)
        
        # 如果房间为空，解散房间
        if len(room.players) == 0:
            room_repo.delete(room_id)
            current_app.logger.info(f"Room {room_id} disbanded (no players left)")
        else:
            current_app.logger.info(f"User {user_id} left room {room_id}")
        
        # 发送WebSocket通知 - 玩家离开事件
        notification_service = current_app.config.get('notification_service')
        ws_manager = current_app.config.get('ws_manager')
        
        if notification_service:
            try:
                # 构建玩家离开事件数据
                event_data = {
                    "room_id": room_id,
                    "user_id": user_id,
                    "user_nickname": user.nickname or "未知用户",
                    "player_count": len(room.players),
                    "is_creator": is_creator,
                    "new_creator": room.creator if len(room.players) > 0 else None,
                    "room_disbanded": len(room.players) == 0
                }
                
                # 发送玩家离开通知
                notification_service.broadcast_room_event(
                    room_id=room_id,
                    event_type="room.player_left",
                    data=event_data
                )
                
                current_app.logger.info(f"Player leave notification sent for user {user_id}")
                
            except Exception as e:
                current_app.logger.warning(f"Failed to send player leave notification: {str(e)}")
        
        # 取消用户的房间订阅（防止WebSocket重连）
        if ws_manager:
            try:
                removed_count = ws_manager.unsubscribe_user_from_room(user_id, room_id)
                if removed_count > 0:
                    current_app.logger.info(f"Removed {removed_count} WebSocket subscription(s) for user {user_id} from room {room_id}")
            except Exception as e:
                current_app.logger.warning(f"Failed to unsubscribe user from room: {str(e)}")
        
        # 构建响应
        response = {
            "code": 200,
            "message": "success",
            "data": {}
        }
        
        return jsonify(response)
        
    except Exception as e:
        current_app.logger.exception(f"Leave room failed: {str(e)}")
        return jsonify({"code": 500, "message": "Leave room failed", "data": {}}), 500
