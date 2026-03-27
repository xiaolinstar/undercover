#!/usr/bin/env python3
"""
应用启动入口
支持直接运行 python main.py
同时也推荐使用 python -m backend.main
"""
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
# 无论从父目录还是 backend 目录运行，都能正确找到项目根目录
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 确保 backend 目录也在路径中（用于从 backend 目录运行）
backend_dir = Path(__file__).parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from backend.app_factory import AppFactory

def main():
    """启动应用"""
    # 开发环境默认使用 dev
    app, socketio = AppFactory.create_app(env='dev')
    socketio.run(app, host="0.0.0.0", port=5001, debug=True)

if __name__ == "__main__":
    main()
