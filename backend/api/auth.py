from flask import jsonify, request, current_app

from . import api_bp
from backend.models.responses import LoginResponse, UserInfo, LoginData, LogoutResponse


@api_bp.route("/auth/login", methods=["POST"])
def login():
    """
    小程序登录授权接口
    ---
    tags:
      - Auth 模块
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            code: 
              type: string
              description: "微信/平台登录换取的 code"
              example: "031w6t0w3h83e..."
    responses:
      200:
        description: "登录成功，返回用户信息及 Token"
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
                token:
                  type: string
                  example: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoidXNlcl8wMDEiLCJleHAiOjE3NjA0ODA4ODF9.7QZ9c4h8f7g6e5d4c3b2a1"
                user:
                  type: object
                  properties:
                    id:
                      type: string
                      example: "user_001"
                    openid:
                      type: string
                      example: "openid_12345"
                    nickname:
                      type: string
                      example: "小明"
                    avatar:
                      type: string
                      example: "https://example.com/avatar.png"
    """
    data = request.get_json() or {}
    code = data.get("code")

    if not code:
        return jsonify({"code": 400, "message": "Missing 'code' parameter", "data": {}}), 400

    # 获取 AuthService
    auth_service = current_app.config.get('auth_service')
    if not auth_service:
        return jsonify({"code": 500, "message": "Service not available", "data": {}}), 500

    # 实际的登录逻辑
    try:
        # 调用 AuthService 进行完整的登录流程
        token, user = auth_service.login(code)
        
        # 使用 Pydantic 模型构建用户信息
        user_info = UserInfo(
            id=user.openid,
            openid=user.openid,
            nickname=user.nickname,
            avatar=user.avatar or "https://xiaolinstar.github.io/xiaolin-docs/sparrow.svg",
            total_games=user.total_games,
            wins=user.wins,
        )
        
        # 使用 Pydantic 模型构建响应
        login_data = LoginData(
            token=token,
            user=user_info
        )
        
        response = LoginResponse(
            code=200,
            message="success",
            data=login_data
        )

        return jsonify(response.model_dump())
    except Exception as e:
        return jsonify({"code": 500, "message": f"Login failed: {str(e)}", "data": {}}), 500


@api_bp.route("/auth/logout", methods=["POST"])
def logout():
    """
    用户登出接口
    ---
    tags:
      - Auth 模块
    consumes:
      - application/json
    parameters:
      - in: header
        name: Authorization
        type: string
        required: true
        description: "Bearer Token"
        example: "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    responses:
      200:
        description: "登出成功"
    """
    # 获取 AuthService
    auth_service = current_app.config.get('auth_service')
    if not auth_service:
        return jsonify({"code": 500, "message": "Service not available", "data": {}}), 500

    # 获取 Token
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return jsonify({"code": 401, "message": "Missing or invalid Authorization header", "data": {}}), 401
    
    token = auth_header[7:]  # 移除 "Bearer " 前缀

    try:
        auth_service.logout(token)
        
        response = LogoutResponse(
            code=200,
            message="success",
            data={}
        )
        
        return jsonify(response.model_dump())
    except ClientException as e:
        return jsonify({"code": 401, "message": e.message, "data": {}}), 401
    except Exception as e:
        return jsonify({"code": 500, "message": f"Logout failed: {str(e)}", "data": {}}), 500
