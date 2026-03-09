#!/usr/bin/env python3
"""
原生 WebSocket 测试脚本（用于微信小程序）

测试原生 WebSocket 端点的连接、认证、订阅等功能
"""

import json
import time
import jwt
import sys
import pytest

# 添加websocket-client的导入
try:
    from websocket import create_connection
except ImportError:
    pytest.skip("需要安装 websocket-client: pip install websocket-client", allow_module_level=True)

# 配置
WS_URL = "ws://localhost:5001/ws"
SECRET_KEY = "your-secret-key-here"  # 与 .env 中的 SECRET_KEY 一致


def generate_token(user_id: str) -> str:
    """生成 JWT token"""
    payload = {
        'user_id': user_id,
        'exp': int(time.time()) + 3600
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')


def test_connection():
    """测试 WebSocket 连接"""
    print("\n" + "=" * 60)
    print("原生 WebSocket 测试（微信小程序兼容）")
    print("=" * 60)

    # 生成测试token
    token = generate_token("test_user_123")
    print(f"\n生成测试token: {token[:50]}...")

    try:
        # 建立WebSocket连接
        print(f"\n尝试连接到: {WS_URL}")
        ws = create_connection(f"{WS_URL}?token={token}")
        print("✅ WebSocket连接成功")

        # 接收欢迎消息
        result = ws.recv()
        print(f"\n收到消息: {result}")

        # 发送测试消息
        test_message = {
            "type": "ping",
            "data": {"timestamp": int(time.time())}
        }
        ws.send(json.dumps(test_message))
        print(f"发送消息: {test_message}")

        # 接收响应
        response = ws.recv()
        print(f"收到响应: {response}")

        # 关闭连接
        ws.close()
        print("\n✅ WebSocket连接已关闭")

    except Exception as e:
        print(f"\n❌ WebSocket连接失败: {e}")
        return False

    return True


if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
