import time
from unittest.mock import MagicMock
import pytest

from backend.services.notification_service import NotificationService


@pytest.fixture
def mock_socketio():
    return MagicMock()


@pytest.fixture
def notification_service(mock_socketio):
    return NotificationService(mock_socketio)


def test_format_message(notification_service):
    room_id = "8888"
    event = "test.event"
    data = {"key": "value"}

    msg = notification_service._format_message(room_id, event, data)

    assert msg["event"] == event
    assert msg["room_id"] == room_id
    assert msg["data"] == data
    assert "timestamp" in msg
    assert isinstance(msg["timestamp"], int)


def test_notify_room_socketio(notification_service, mock_socketio):
    room_id = "8888"
    event = "room.player_joined"
    data = {"player_id": "user1"}

    notification_service.notify_room(room_id, event, data)

    mock_socketio.emit.assert_called_once()
    called_event, called_msg = mock_socketio.emit.call_args[0]
    called_kwargs = mock_socketio.emit.call_args[1]

    assert called_event == event
    assert called_msg["event"] == event
    assert called_msg["room_id"] == room_id
    assert called_msg["data"] == data
    assert called_kwargs["room"] == room_id


def test_notify_room_with_native_ws(notification_service, mock_socketio):
    mock_native_broadcast = MagicMock()
    notification_service.set_native_ws_broadcast(mock_native_broadcast)

    room_id = "8888"
    event = "game.started"
    data = {}

    notification_service.notify_room(room_id, event, data)

    mock_socketio.emit.assert_called_once()
    mock_native_broadcast.assert_called_once()

    args, _ = mock_native_broadcast.call_args
    assert args[0] == room_id
    assert args[1] == event
    assert isinstance(args[2], dict)
    assert args[2]["event"] == event
