#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
谁是卧底游戏主应用
"""
from src.app_factory import AppFactory

# 创建应用实例
app = AppFactory.create_app()


if __name__ == '__main__':
    # 运行应用
    app.run(host='0.0.0.0', port=5000, debug=True)