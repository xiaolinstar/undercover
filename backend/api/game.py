from flask import jsonify, request, current_app

from . import api_bp
from .decorators import login_required
from backend.models.room import RoomStatus
from backend.exceptions import (
    RoomNotFoundException,
    GameNotStartedError,
    GameAlreadyStartedError,
    InsufficientPlayersError,
    InvalidPlayerStateError,
    RoomPermissionError,
    InvalidStateTransitionError
)


@api_bp.route("/game/start", methods=["POST"])
@login_required
def start_game():
    """
    开始游戏发牌
    ---
    tags:
      - Game 模块
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
      - in: header
        name: Authorization
        type: string
        required: true
        description: "Bearer Token (包含用户信息)"
        example: "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    responses:
      200:
        description: "发牌成功，获取本人持有的词汇等身份信息"
        schema:
          type: object
          properties:
            code:
              type: integer
              example: 200
            data:
              type: object
              properties:
                word:
                  type: string
                  example: "苹果"
                role:
                  type: integer
                  description: "1为平民, 2为卧底, 3为白板"
                  example: 1
    """
    data = request.get_json() or {}
    room_id = data.get("room_id")
    user_id = getattr(request, 'current_user_id', None)

    if not room_id:
        return jsonify({"code": 400, "message": "Missing room_id"}), 400
    if not user_id:
        return jsonify({"code": 401, "message": "User not authenticated", "data": {}}), 401

    # 获取 GameService
    game_service = current_app.config.get('game_service')
    if not game_service:
        return jsonify({"code": 500, "message": "Service not available", "data": {}}), 500

    try:
        # 开始游戏
        success, result = game_service.start_game(room_id, user_id)
        
        if not success:
            return jsonify({"code": 400, "message": result, "data": {}}), 400
        
        # 构建响应
        return jsonify({"code": 200, "message": "success", "data": {
            "word": "游戏已开始",
            "role": 1,
            "status": "DESCRIBING"
        }})
    except RoomNotFoundException as e:
        current_app.logger.warning(f"Room not found: {room_id}")
        return jsonify({"code": 404, "message": "房间不存在", "data": {}}), 404
    except InsufficientPlayersError as e:
        current_app.logger.warning(f"Insufficient players: {str(e)}")
        return jsonify({"code": 400, "message": str(e), "data": {}}), 400
    except GameAlreadyStartedError as e:
        current_app.logger.warning(f"Game already started: {str(e)}")
        return jsonify({"code": 400, "message": "游戏已经开始", "data": {}}), 400
    except RoomPermissionError as e:
        current_app.logger.warning(f"Permission denied: {str(e)}")
        return jsonify({"code": 403, "message": str(e), "data": {}}), 403
    except InvalidStateTransitionError as e:
        current_app.logger.warning(f"Invalid state: {str(e)}")
        return jsonify({"code": 400, "message": str(e), "data": {}}), 400
    except Exception as e:
        current_app.logger.exception(f"Start game failed: {str(e)}")
        return jsonify({"code": 500, "message": "系统繁忙，请稍后重试", "data": {}}), 500


@api_bp.route("/game/word", methods=["GET"])
@login_required
def get_word():
    """
    获取玩家词语
    ---
    tags:
      - Game 模块
    parameters:
      - in: query
        name: room_id
        type: string
        required: true
        example: "8888"
      - in: query
        name: user_id
        type: string
        required: true
        example: "user_001"
    responses:
      200:
        description: "返回玩家的词语和角色"
        schema:
          type: object
          properties:
            code:
              type: integer
              example: 200
            data:
              type: object
              properties:
                word:
                  type: string
                  example: "苹果"
                role:
                  type: integer
                  description: "1为平民, 2为白板"
                  example: 1
    """
    room_id = request.args.get('room_id')
    user_id = getattr(request, 'current_user_id', None)

    if not room_id or not user_id:
        return jsonify({"code": 400, "message": "Missing room_id or user_id"}), 400

    # 获取 GameService
    game_service = current_app.config.get('game_service')
    if not game_service:
        return jsonify({"code": 500, "message": "Service not available", "data": {}}), 500

    try:
        # 获取玩家词语
        word_info = game_service.get_player_word(room_id, user_id)
        
        return jsonify({"code": 200, "message": "success", "data": {
            "word": word_info.get('word', '苹果'),
            "role": word_info.get('role', 1)
        }})
    except RoomNotFoundException as e:
        current_app.logger.warning(f"Room not found: {room_id}")
        return jsonify({"code": 404, "message": "房间不存在", "data": {}}), 404
    except GameNotStartedError as e:
        current_app.logger.warning(f"Game not started: {str(e)}")
        return jsonify({"code": 400, "message": "游戏尚未开始", "data": {}}), 400
    except InvalidPlayerStateError as e:
        current_app.logger.warning(f"Invalid player state: {str(e)}")
        return jsonify({"code": 400, "message": str(e), "data": {}}), 400
    except Exception as e:
        current_app.logger.exception(f"Get word failed: {str(e)}")
        return jsonify({"code": 500, "message": "系统繁忙，请稍后重试", "data": {}}), 500


@api_bp.route("/game/vote", methods=["POST"])
@login_required
def vote():
    """
    投票淘汰玩家
    ---
    tags:
      - Game 模块
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
            user_id:
              type: string
              example: "user_001"
            target_uid:
              type: string
              description: "目标的玩家ID"
              example: "user_002"
    responses:
      200:
        description: "投票成功提交"
    """
    data = request.get_json() or {}
    room_id = data.get("room_id")
    user_id = getattr(request, 'current_user_id', None)
    target = data.get("target_uid")

    if not room_id or not user_id or not target:
        return jsonify({"code": 400, "message": "Missing room_id, user_id or target_uid"}), 400

    # 获取 GameService
    game_service = current_app.config.get('game_service')
    if not game_service:
        return jsonify({"code": 500, "message": "Service not available", "data": {}}), 500

    try:
        # 提交投票
        game_service.submit_vote(room_id, user_id, target)
        
        return jsonify({"code": 200, "message": "vote recorded", "data": {}})
    except RoomNotFoundException as e:
        current_app.logger.warning(f"Room not found: {room_id}")
        return jsonify({"code": 404, "message": "房间不存在", "data": {}}), 404
    except GameNotStartedError as e:
        current_app.logger.warning(f"Game not started: {str(e)}")
        return jsonify({"code": 400, "message": "游戏尚未开始", "data": {}}), 400
    except InvalidPlayerStateError as e:
        current_app.logger.warning(f"Invalid player state: {str(e)}")
        return jsonify({"code": 400, "message": str(e), "data": {}}), 400
    except Exception as e:
        current_app.logger.exception(f"Vote failed: {str(e)}")
        return jsonify({"code": 500, "message": "系统繁忙，请稍后重试", "data": {}}), 500


@api_bp.route("/game/sync/<room_id>", methods=["GET"])
@login_required
def sync_room(room_id):
    """
    状态同步接口（增强版）
    ---
    tags:
      - Game 模块
    parameters:
      - in: path
        name: room_id
        type: string
        required: true
        description: "房间ID"
      - in: header
        name: Authorization
        type: string
        required: false
        description: "Bearer token (可选，用于获取当前用户信息)"
    responses:
      200:
        description: "返回房间完整状态信息"
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
                  example: "8888"
                status:
                  type: string
                  example: "playing"
                player_count:
                  type: integer
                  example: 4
                updated_at:
                  type: integer
                  description: "房间最后更新时间戳（用于版本控制）"
                  example: 1708675200
                players:
                  type: array
                  items:
                    type: object
                    properties:
                      openid:
                        type: string
                      nickname:
                        type: string
                      seat:
                        type: integer
                      is_eliminated:
                        type: boolean
                      is_creator:
                        type: boolean
                my_info:
                  type: object
                  description: "当前用户信息（如果已认证）"
                  properties:
                    openid:
                      type: string
                    seat:
                      type: integer
                    is_eliminated:
                      type: boolean
                    is_creator:
                      type: boolean
      404:
        description: "房间不存在"
      403:
        description: "无权访问该房间"
    """
    from flask import current_app
    
    # 获取依赖
    room_repo = current_app.config.get('room_repository')
    user_repo = current_app.config.get('user_repository')
    
    if not room_repo:
        return jsonify({
            "code": 500,
            "message": "Service not available",
            "data": {}
        }), 500
    
    # 获取房间信息
    room = room_repo.get(room_id)
    if not room:
        return jsonify({
            "code": 404,
            "message": "房间不存在",
            "data": {}
        }), 404
    
    # 尝试从 token 获取当前用户（可选）
    current_user_id = None
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        # 这里简化处理，实际应该解析 JWT
        # 暂时跳过认证，因为是 Mock 接口
        pass
    
    # 构建玩家列表
    players = []
    for i, player_id in enumerate(room.players):
        user = user_repo.get(player_id) if user_repo else None
        players.append({
            "openid": player_id,
            "nickname": user.nickname if user else f"玩家{i+1}",
            "seat": i + 1,
            "is_eliminated": room.is_eliminated(player_id),
            "is_creator": room.is_creator(player_id)
        })
    
    # 构建响应数据
    response_data = {
        "room_id": room_id,
        "status": room.status.value,
        "player_count": room.get_player_count(),
        "updated_at": int(room.last_active.timestamp()) if hasattr(room, 'last_active') and room.last_active else 0,
        "players": players
    }
    
    # 如果有当前用户信息，添加 my_info
    if current_user_id and room.is_player(current_user_id):
        seat = room.players.index(current_user_id) + 1 if current_user_id in room.players else 0
        response_data["my_info"] = {
            "openid": current_user_id,
            "seat": seat,
            "is_eliminated": room.is_eliminated(current_user_id),
            "is_creator": room.is_creator(current_user_id)
        }
    
    return jsonify({
        "code": 200,
        "message": "success",
        "data": response_data
    })
