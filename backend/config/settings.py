from __future__ import annotations

import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App Env
    APP_ENV: str = "dev"  # dev, staging, prod

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

    @classmethod
    def get_env(cls) -> str:
        """获取运行环境
        
        优先级：
        1. 命令行参数 --env
        2. 从 APP_ENV 环境变量读取（显式指定）
        3. 从 ENV_FILE 环境变量推导（Docker Compose env_file）
        4. 从配置文件名推导（本地开发环境）
        
        Returns:
            str: 运行环境 (dev, staging, prod)
        """
        # 1. 从命令行参数读取
        import sys
        if '--env' in sys.argv:
            idx = sys.argv.index('--env')
            if idx + 1 < len(sys.argv):
                return sys.argv[idx + 1]
        
        # 2. 从 APP_ENV 环境变量读取（显式指定）
        app_env = os.environ.get('APP_ENV')
        if app_env:
            return app_env
        
        # 3. 从 ENV_FILE 环境变量推导（Docker Compose env_file）
        env_file = os.environ.get('ENV_FILE')
        if env_file:
            # 从文件名推导环境
            # backend/.env.staging -> staging
            # backend/.env.production -> prod
            env_file_name = Path(env_file).name
            if env_file_name == ".env.production":
                return "prod"
            elif env_file_name == ".env.staging":
                return "staging"
            elif env_file_name == ".env.development":
                return "dev"
        
        # 4. 从配置文件名推导（本地开发环境）
        backend_dir = Path(__file__).parent.parent
        
        # 检查环境变量文件是否存在
        env_files = [
            (".env.production", "prod"),
            (".env.staging", "staging"),
            (".env.development", "dev"),
        ]
        
        for env_file, env in env_files:
            env_file_path = backend_dir / env_file
            if env_file_path.exists():
                return env
        
        return "dev"

    @classmethod
    def _get_env_file(cls, env: str = "dev") -> str:
        """根据环境参数获取对应的环境变量文件"""
        env_file_map = {
            "dev": ".env.development",
            "staging": ".env.staging",
            "prod": ".env.production",
        }
        env_file_name = env_file_map.get(env, ".env.development")
        backend_dir = Path(__file__).parent.parent
        env_file_path = backend_dir / env_file_name
        return str(env_file_path)

    @classmethod
    def _get_app_env(cls, env: str = "dev") -> str:
        """根据环境参数获取 APP_ENV"""
        return env

    @classmethod
    def create(cls, env: str = None) -> "Settings":
        """创建指定环境的 Settings 实例
        
        Args:
            env: 运行环境 (dev, staging, prod)，如果为 None 则自动推导
        
        Returns:
            Settings: Settings 实例
        
        说明:
            - 在本地开发时，从 .env 文件读取配置
            - 在容器环境中，从环境变量读取配置
        """
        if env is None:
            env = cls.get_env()
        
        backend_dir = Path(__file__).parent.parent
        env_file = cls._get_env_file(env)
        env_file_path = backend_dir / env_file
        
        # 检查环境变量文件是否存在
        if env_file_path.exists():
            # 本地开发：从 .env 文件读取配置
            return cls(
                _env_file=env_file,
                APP_ENV=env,
            )
        else:
            # 容器环境：从环境变量读取配置
            # Docker Compose 的 env_file 已经将环境变量注入到容器的环境变量中
            return cls(
                APP_ENV=env,
            )

    model_config = SettingsConfigDict(
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


settings = Settings()
