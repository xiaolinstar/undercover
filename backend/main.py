#!/usr/bin/env python3
"""
应用启动入口
支持直接运行 python main.py
同时也推荐使用 python -m backend.main
"""
import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
# 无论从父目录还是 backend 目录运行，都能正确找到项目根目录
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 确保 backend 目录也在路径中（用于从 backend 目录运行）
backend_dir = Path(__file__).parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# 设置环境变量，确保 .env 文件被正确加载
# 根据环境加载对应的环境变量文件
env_files = [
    backend_dir / ".env.development",
    backend_dir / ".env.staging",
    backend_dir / ".env.production",
    backend_dir / ".env",
]
for env_file in env_files:
    if env_file.exists():
        os.environ.setdefault("ENV_FILE", str(env_file))
        break

from backend.app_factory import AppFactory
from backend.config.settings import settings

def main():
    """启动应用"""
    app, socketio = AppFactory.create_app()
    debug_mode = settings.FLASK_DEBUG if hasattr(settings, 'FLASK_DEBUG') else False
    socketio.run(app, host="0.0.0.0", port=5001, debug=debug_mode)

if __name__ == "__main__":
    main()
