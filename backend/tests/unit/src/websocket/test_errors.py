import pytest

from backend.websocket.errors import WSErrorCode, format_ws_error


def test_format_ws_error_basic():
    event = "auth_error"
    code = WSErrorCode.MISSING_TOKEN
    message = "No token provided"

    result = format_ws_error(event, code, message)

    assert result["type"] == "error"
    assert result["event"] == event
    assert result["data"]["error"] == code.value
    assert result["data"]["message"] == message


def test_format_ws_error_with_kwargs():
    event = "subscribe_error"
    code = WSErrorCode.ROOM_NOT_FOUND
    message = "Room 1234 not found"
    room_id = "1234"
    extra_field = "extra_value"

    result = format_ws_error(event, code, message, room_id=room_id, extra=extra_field)

    assert result["event"] == event
    assert result["data"]["error"] == code.value
    assert result["room_id"] == room_id
    assert result["extra"] == extra_field
