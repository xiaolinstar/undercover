from flask import Blueprint, jsonify

"""API 路由模块"""

api_bp = Blueprint("api", __name__, url_prefix="/api/v1")


@api_bp.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "api-v1", "version": "0.1.0"})


# Import views to register routes
from . import auth as auth, game as game, room as room  # noqa: E402
