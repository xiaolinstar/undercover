import time
import jwt
import pytest
from flask import Flask

from backend.websocket.auth import decode_token, check_rate_limit, _rate_limit_store
from backend.websocket.errors import WSErrorCode


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "test-secret"
    return app


def test_decode_token_success(app):
    token = jwt.encode({"sub": "user123", "exp": time.time() + 3600}, app.config["SECRET_KEY"], algorithm="HS256")
    with app.app_context():
        user_id, error = decode_token(token)
    assert user_id == "user123"
    assert error is None


def test_decode_token_missing(app):
    with app.app_context():
        user_id, error = decode_token(None)
    assert user_id is None
    assert error[0] == WSErrorCode.MISSING_TOKEN


def test_decode_token_expired(app):
    token = jwt.encode({"sub": "user123", "exp": time.time() - 3600}, app.config["SECRET_KEY"], algorithm="HS256")
    with app.app_context():
        user_id, error = decode_token(token)
    assert user_id is None
    assert error[0] == WSErrorCode.TOKEN_EXPIRED


def test_decode_token_invalid_signature(app):
    token = jwt.encode({"sub": "user123", "exp": time.time() + 3600}, "wrong-secret", algorithm="HS256")
    with app.app_context():
        user_id, error = decode_token(token)
    assert user_id is None
    assert error[0] == WSErrorCode.INVALID_TOKEN


def test_check_rate_limit():
    _rate_limit_store.clear()
    key = "test_ip"

    # 允许 5 次请求
    for _ in range(5):
        assert check_rate_limit(key, limit=5, window=10) is True

    # 第 6 次应该被拒绝
    assert check_rate_limit(key, limit=5, window=10) is False
