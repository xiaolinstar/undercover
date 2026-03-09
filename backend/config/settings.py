from __future__ import annotations

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
    SOCKETIO_ASYNC_MODE: str = "eventlet"  # eventlet, threading, gevent
    SOCKETIO_CORS_ALLOWED_ORIGINS: str = "*"  # 生产环境应限制具体域名
    SOCKETIO_MESSAGE_QUEUE: str = ""  # 未来多实例时使用，如 redis://localhost:6379/1

    # Snowflake
    SNOWFLAKE_MACHINE_ID: int = 0  # 机器ID，范围0-1023，用于雪花算法

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    def __init__(self, **values):
        super().__init__(**values)

        # Adjust flags based on environment
        if self.APP_ENV == "prod":
            self.FLASK_DEBUG = False
            self.DEBUG = False
            self.TESTING = False
        elif self.APP_ENV == "test":
            self.TESTING = True
            # Optional: ensure debug is consistent for tests
            # self.FLASK_DEBUG = False


settings = Settings()
