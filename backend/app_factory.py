#!/usr/bin/env python3
"""
应用工厂
负责创建和配置Flask应用
"""

import redis
from flask import Flask

# Import models for migration detection
from backend.api import api_bp
from backend.config.settings import settings
from backend.extensions import db, migrate
from backend.repositories.room_repository import RoomRepository
from backend.repositories.user_repository import UserRepository
from backend.services.auth_service import AuthService
from backend.services.exception_handler import register_global_exception_handlers
from backend.services.game_service import GameService
from backend.services.message_service import MessageService
from backend.services.notification_service import NotificationService
from backend.services.push_service import PushService
from backend.services.wechat_client import WeChatClient
from backend.utils.logger import setup_logger
from backend.wechat.handlers import wechat_bp
from backend.websocket import socketio


class AppFactory:
    """应用工厂类"""

    @staticmethod
    def create_app() -> tuple[Flask, any]:
        """
        创建Flask应用
        
        Returns:
            tuple: (app, socketio) - Flask应用实例和SocketIO实例
        """
        app = Flask(__name__)

        # 配置日志
        app.logger = setup_logger(app.name)
        app.logger.info(f"Application starting in {settings.APP_ENV} mode")

        # 配置应用
        app.config.from_object(settings)

        # 初始化扩展
        db.init_app(app)
        migrate.init_app(app, db)
        
        # 初始化雪花算法
        from backend.utils.snowflake import init_snowflake
        init_snowflake(app.config.get("SNOWFLAKE_MACHINE_ID", 0))
        app.logger.info(f"Snowflake generator initialized with machine_id={app.config.get('SNOWFLAKE_MACHINE_ID', 0)}")
        
        # 初始化 SocketIO（单实例模式）
        # 在测试环境下使用threading模式，避免Python 3.13与eventlet的兼容性问题
        async_mode = app.config.get('SOCKETIO_ASYNC_MODE', 'eventlet')
        if settings.TESTING:
            async_mode = 'threading'
        
        socketio.init_app(
            app,
            cors_allowed_origins=app.config.get('SOCKETIO_CORS_ALLOWED_ORIGINS', '*'),
            async_mode=async_mode,
            logger=app.config.get('DEBUG', False),
            engineio_logger=app.config.get('DEBUG', False)
        )
        app.logger.info(f"SocketIO initialized in {async_mode} mode")

        # 初始化 Swagger API 前端文档
        from flasgger import Swagger

        swagger = Swagger(
            app,
            template={
                "info": {
                    "title": "谁是卧底桌游发牌器 API",
                    "version": "1.0.0",
                    "description": "提供给小程序/App客户端的核心发牌器与状态同步接口(MOCK优先)",
                },
                "components": {"securitySchemes": {"BearerAuth": {"type": "http", "scheme": "bearer"}}},
                "security": [{"BearerAuth": []}],
            },
        )

        # 生产环境校验
        if settings.APP_ENV == "prod":
            AppFactory._validate_prod_config(app)

        # 初始化服务
        (room_repo, user_repo, game_service, message_service, 
         auth_service, notification_service, ws_manager) = AppFactory._init_services(app)

        # 将服务存储在应用上下文中（必须在注册蓝图前完成）
        app.room_repo = room_repo
        app.user_repo = user_repo
        app.game_service = game_service
        app.message_service = message_service
        app.auth_service = auth_service
        app.notification_service = notification_service
        
        # 同时存储到 config 中，方便在视图函数中访问
        app.config['room_repository'] = room_repo
        app.config['user_repository'] = user_repo
        app.config['game_service'] = game_service
        app.config['auth_service'] = auth_service
        app.config['notification_service'] = notification_service
        app.config['ws_manager'] = ws_manager
        
        # 注册蓝图
        AppFactory._register_blueprints(app)

        # 注册全局异常处理器
        register_global_exception_handlers(app)
        
        # 注册 WebSocket 处理器
        AppFactory._register_websocket_handlers(app)

        return app, socketio

    @staticmethod
    def _validate_prod_config(app: Flask) -> None:
        """校验生产环境配置是否安全（非默认值）"""
        critical_configs = {
            "WECHAT_TOKEN": ["", "your_token_here"],
            "WECHAT_APP_ID": ["", "your_app_id_here"],
            "WECHAT_APP_SECRET": ["", "your_app_secret_here"],
            "SECRET_KEY": ["default-secret-key", "your-secret-key-here"],
        }

        missing_or_default = []
        for key, defaults in critical_configs.items():
            val = app.config.get(key)
            if not val or val in defaults:
                missing_or_default.append(key)

        if missing_or_default:
            missing_str = ", ".join(missing_or_default)
            error_msg = (
                "Production environment security check failed! "
                f"The following configs are missing or using defaults: {missing_str}"
            )
            app.logger.error(error_msg)
            # 在生产环境下，配置不安全应该拒绝启动
            raise ValueError(error_msg)

        app.logger.info("Production environment security check passed.")

    @staticmethod
    def _init_services(app: Flask) -> tuple:
        """初始化服务"""
        # 创建Redis客户端
        if app.config.get("TESTING"):
            import fakeredis

            redis_client = fakeredis.FakeRedis(decode_responses=False)
            app.logger.info("Using fakeredis for testing")
        else:
            redis_client = redis.Redis.from_url(app.config["REDIS_URL"])

        # 创建仓储
        room_repo = RoomRepository(redis_client)
        user_repo = UserRepository(redis_client)

        # 创建通知服务
        notification_service = NotificationService(socketio)
        
        # 初始化原生 WebSocket（用于微信小程序）
        from backend.websocket.native_handlers import init_native_websocket, broadcast_to_room, connections, room_subscriptions
        init_native_websocket(app)
        notification_service.set_native_ws_broadcast(broadcast_to_room)
        
        # 初始化 WebSocket 管理器
        from backend.websocket.websocket_manager import ws_manager
        ws_manager.set_connections(connections)
        ws_manager.set_room_subscriptions(room_subscriptions)

        # 创建服务
        client = None
        push_service = None
        # Pydantic settings will have boolean logic already applied if using bool type
        # But app.config might hold the value. If from_object copied it, it's boolean.
        # Verify: app.config['ENABLE_WECHAT_PUSH'] will be bool True/False from settings
        if app.config.get("ENABLE_WECHAT_PUSH"):
            client = WeChatClient(
                app.config["WECHAT_APP_ID"], app.config["WECHAT_APP_SECRET"], redis_client=redis_client
            )
            push_service = PushService(client)
        game_service = GameService(room_repo, user_repo, push_service, notification_service)
        message_service = MessageService(
            game_service,
            app.config["WECHAT_TOKEN"],
            redis_client=redis_client,
            staging_url=app.config.get("STAGING_URL"),
        )

        # Initialize AuthService
        auth_service = AuthService(
            app_id=app.config.get("MINI_PROGRAM_APP_ID", ""),
            app_secret=app.config.get("MINI_PROGRAM_APP_SECRET", ""),
            user_repo=user_repo,
            secret_key=app.config.get("SECRET_KEY"),
            redis_client=redis_client,
        )

        return room_repo, user_repo, game_service, message_service, auth_service, notification_service, ws_manager

    @staticmethod
    def _register_blueprints(app: Flask) -> None:
        """注册蓝图"""
        import time

        # 注册功能蓝图
        app.register_blueprint(wechat_bp)
        app.register_blueprint(api_bp)

        # 注册应用级路由（如健康检查）
        @app.route("/health")
        def health_check():
            """健康检查接口，可用于kube-probe"""
            return {"status": "healthy", "timestamp": int(time.time())}

    @staticmethod
    def _register_websocket_handlers(app: Flask) -> None:
        """注册 WebSocket 处理器"""
        # 导入处理器模块，自动注册所有 @socketio.on 装饰的函数
        import backend.websocket.handlers  # noqa: F401
        
        app.logger.info("WebSocket handlers registered")
