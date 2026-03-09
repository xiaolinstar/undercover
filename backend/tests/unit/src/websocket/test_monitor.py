import pytest

from backend.websocket.monitor import WSMonitor


@pytest.fixture
def monitor():
    # Because it is a singleton, reset its internal state for pure unit tests
    m = WSMonitor()
    m._init_counters()
    return m


def test_monitor_singleton():
    m1 = WSMonitor()
    m2 = WSMonitor()
    assert m1 is m2


def test_record_connection(monitor):
    monitor.record_connection()
    assert monitor.active_connections == 1
    assert monitor.total_connections == 1

    monitor.record_connection()
    assert monitor.active_connections == 2
    assert monitor.total_connections == 2


def test_record_disconnection(monitor):
    monitor.record_connection()
    monitor.record_connection()

    monitor.record_disconnection()
    assert monitor.active_connections == 1
    assert monitor.total_connections == 2

    monitor.record_disconnection()
    monitor.record_disconnection()  # Should not drop below 0
    assert monitor.active_connections == 0
    assert monitor.total_connections == 2


def test_record_message_sent(monitor):
    monitor.record_message_sent()
    assert monitor.messages_sent == 1

    monitor.record_message_sent(5)
    assert monitor.messages_sent == 6


def test_record_error(monitor):
    monitor.record_error("AUTH_ERROR")
    monitor.record_error("AUTH_ERROR")
    monitor.record_error("INTERNAL_ERROR")

    stats = monitor.get_stats()
    assert stats["errors_count"] == 3
    assert stats["errors_by_type"]["AUTH_ERROR"] == 2
    assert stats["errors_by_type"]["INTERNAL_ERROR"] == 1


def test_get_stats(monitor):
    monitor.record_connection()
    monitor.record_message_sent(10)
    monitor.record_error("TEST_ERROR")

    stats = monitor.get_stats()
    assert stats["active_connections"] == 1
    assert stats["total_connections"] == 1
    assert stats["messages_sent"] == 10
    assert stats["errors_count"] == 1
    assert "TEST_ERROR" in stats["errors_by_type"]
