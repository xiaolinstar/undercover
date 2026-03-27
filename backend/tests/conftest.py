#!/usr/bin/env python3
"""
测试配置文件
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pytest

from backend.config.settings import Settings


@pytest.fixture(scope="session")
def app_and_socketio():
    """创建应用实例和 SocketIO 实例"""
    from backend.app_factory import AppFactory

    return AppFactory.create_app(env="test")


@pytest.fixture(scope="session")
def app(app_and_socketio):
    """创建应用实例"""
    return app_and_socketio[0]


@pytest.fixture(scope="session")
def socketio(app_and_socketio):
    """创建 SocketIO 实例"""
    return app_and_socketio[1]


@pytest.fixture(scope="session")
def client(app):
    """创建测试客户端"""
    return app.test_client()


@pytest.fixture(scope="session")
def runner(app):
    """创建CLI运行器"""
    return app.test_cli_runner()


@pytest.fixture
def mock_auth_service():
    """模拟 AuthService"""
    from unittest.mock import MagicMock
    service = MagicMock()
    service.secret_key = "test_secret_key"
    return service


@pytest.fixture
def mock_notification_service():
    """模拟 NotificationService"""
    from unittest.mock import MagicMock
    service = MagicMock()
    service.broadcast_room_event.return_value = None
    return service


@pytest.fixture
def app_with_mock_services(app, mock_auth_service, mock_notification_service):
    """创建带有 Mock 服务的应用"""
    app.config['auth_service'] = mock_auth_service
    app.config['notification_service'] = mock_notification_service
    # 同时设置到app属性中，供装饰器使用
    app.auth_service = mock_auth_service
    app.notification_service = mock_notification_service
    return app
