import os
import sys

os.environ["APP_ENV"] = "test"

import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))


@pytest.fixture
def socketio_client(app, socketio):
    """Create a test client for SocketIO."""
    with app.test_request_context():
        token = "test-token"

        _mock_sessions = {}

        def mock_save_session(sid, data):
            _mock_sessions[sid] = data

        def mock_get_session(sid):
            return _mock_sessions.get(sid, {})

        with (
            patch("backend.websocket.handlers.decode_token", return_value=("test_user_id", None)),
            patch("backend.websocket.handlers.check_rate_limit", return_value=True),
            patch.object(
                socketio.server,
                "save_session",
                side_effect=mock_save_session,
            ),
            patch.object(
                socketio.server,
                "get_session",
                side_effect=mock_get_session,
            ),
        ):
            from backend.models.room import Room
            from backend.models.user import User

            room_repo = app.config.get("room_repository")
            user_repo = app.config.get("user_repository")

            if room_repo and user_repo:
                user = User(openid="test_user_id", nickname="Test Player")
                user_repo.save(user)

                room = Room(room_id="8888", creator="test_user_id", room_code="1234")
                if "test_user_id" not in room.players:
                    room.players.append("test_user_id")
                room_repo.save(room)

            client = socketio.test_client(app, flask_test_client=app.test_client(), auth={"token": token})
            yield client


def test_socketio_connection(socketio_client):
    """Test connecting to SocketIO."""
    from backend.websocket.events import SystemEvent

    assert socketio_client.is_connected()

    received = socketio_client.get_received()
    assert len(received) >= 1

    connect_event = [msg for msg in received if msg["name"] == SystemEvent.CONNECTED.value]
    assert len(connect_event) == 1
    assert connect_event[0]["args"][0]["event"] == SystemEvent.CONNECTED.value
    assert connect_event[0]["args"][0]["data"]["user_id"] == "test_user_id"


def test_socketio_ping_pong(socketio_client):
    """Test ping-pong functionality."""
    from backend.websocket.events import SystemEvent

    socketio_client.get_received()

    socketio_client.emit("ping")

    received = socketio_client.get_received()
    assert len(received) == 1
    assert received[0]["name"] == SystemEvent.PONG.value


def test_socketio_subscribe(socketio_client):
    """Test room subscription."""
    from backend.websocket.events import SystemEvent

    socketio_client.get_received()

    socketio_client.emit("subscribe", {"room_id": "8888"})

    received = socketio_client.get_received()
    assert len(received) == 1
    assert received[0]["name"] == SystemEvent.SUBSCRIBED.value
    assert received[0]["args"][0]["room_id"] == "8888"


def test_socketio_subscribe_permission_denied(socketio_client):
    """Test room subscription when player is not in room."""
    from backend.websocket.events import SystemEvent

    socketio_client.get_received()

    app = socketio_client.flask_test_client.application
    room_repo = app.config.get("room_repository")

    from backend.models.room import Room

    room_repo.save(Room(room_id="9999", creator="other_user", room_code="1234"))

    socketio_client.emit("subscribe", {"room_id": "9999"})

    received = socketio_client.get_received()
    assert len(received) == 1
    assert received[0]["name"] == SystemEvent.SUBSCRIBE_ERROR.value
    assert received[0]["args"][0]["data"]["error"] == "PERMISSION_DENIED"
