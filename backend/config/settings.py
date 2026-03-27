from __future__ import annotations

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App Env
    APP_ENV: str = "dev"  # dev, test, prod

    # Flask
    SECRET_KEY: str = "default-secret-key"
    FLASK_DEBUG: bool = True
    DEBUG: bool = True
    TESTING: bool = False

    # WeChat
    WECHAT_TOKEN: str = ""
    WECHAT_APP_ID: str = ""
    WECHAT_APP_SECRET: str = ""
    ENABLE_WECHAT_PUSH: bool = False

    # Mini Program
    MINI_PROGRAM_APP_ID: str = ""
    MINI_PROGRAM_APP_SECRET: str = ""

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Database
    SQLALCHEMY_DATABASE_URI: str = "mysql+pymysql://undercover:undercover@localhost:3306/undercover"
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False

    # Multi-environment Routing
    STAGING_URL: str = ""  # e.g. http://staging-web-service.staging:8000

    # WebSocket
    SOCKETIO_ASYNC_MODE: str = "threading"  # 默认使用 threading 模式，兼容性更好
    SOCKETIO_CORS_ALLOWED_ORIGINS: str = "*"  # 生产环境应限制具体域名
    SOCKETIO_MESSAGE_QUEUE: str = ""  # 未来多实例时使用，如 redis://localhost:6379/1

    # CORS Configuration
    CORS_ALLOWED_ORIGINS: str = "*"  # 生产环境应限制具体域名

    # Snowflake
    SNOWFLAKE_MACHINE_ID: int = 0  # 机器ID，范围0-1023，用于雪花算法

    model_config = SettingsConfigDict(
        env_file=".env.development",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    def __init__(self, **values):
        super().__init__(**values)

        # 调整 flags 基于环境
        if self.APP_ENV == "prod":
            self.FLASK_DEBUG = False
            self.DEBUG = False
            self.TESTING = False
            # 生产环境限制 CORS
            self.SOCKETIO_CORS_ALLOWED_ORIGINS = "https://yourdomain.com"
            self.CORS_ALLOWED_ORIGINS = "https://yourdomain.com"
        elif self.APP_ENV == "test":
            self.TESTING = True
            # 可选：确保测试时 debug 一致
            # self.FLASK_DEBUG = False


settings = Settings()
