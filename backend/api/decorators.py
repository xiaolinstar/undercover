from functools import wraps

from flask import current_app, jsonify, request

from backend.exceptions import ClientException


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            current_app.logger.warning(f"Missing or invalid Authorization header: {auth_header}")
            return jsonify({"code": 401, "message": "Missing token", "error_code": "AUTH-MISSING-TOKEN"}), 401

        # 更安全的token提取方式
        parts = auth_header.split(" ")
        if len(parts) != 2 or parts[0] != "Bearer":
            current_app.logger.warning(f"Invalid Authorization format: {auth_header}")
            return jsonify({"code": 401, "message": "Invalid token format", "error_code": "AUTH-INVALID-FORMAT"}), 401
        
        token = parts[1]
        try:
            # 检查 auth_service 是否存在
            auth_service = getattr(current_app, 'auth_service', None)
            if not auth_service:
                current_app.logger.error("auth_service not found in current_app")
                return jsonify({"code": 500, "message": "Service not available", "data": {}}), 500
            
            # Verify token and get openid
            openid = auth_service.verify_token(token)
            current_app.logger.info(f"Token verified successfully for user: {openid}")

            # Store current user in request context
            request.current_user_id = openid

        except ClientException as e:
            current_app.logger.warning(f"Token verification failed: {e.message} (code: {e.error_code})")
            return jsonify({"code": 401, "message": e.message, "error_code": e.error_code}), 401
        except Exception as e:
            current_app.logger.exception(f"Token verification error: {str(e)}")
            return jsonify({"code": 401, "message": "Invalid token", "error_code": "AUTH-INVALID"}), 401

        return f(*args, **kwargs)

    return decorated_function
