#!/usr/bin/env python3
"""
WSGI 入口文件
用于 Gunicorn 等生产环境服务器
"""
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 确保 backend 目录也在路径中
backend_dir = Path(__file__).parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from backend.app_factory import AppFactory

# 创建应用实例
app, socketio = AppFactory.create_app()
