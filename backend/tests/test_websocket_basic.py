#!/usr/bin/env python3
"""
WebSocket 基础功能测试脚本
用于验证 Phase 1 的基础设施是否正常工作
"""

import time
import jwt
from socketio import Client

# 配置
SERVER_URL = "http://localhost:5001"
SECRET_KEY = "your-secret-key-here"  # 与 .env 中的 SECRET_KEY 一致


def generate_test_token(user_id: str) -> str:
    """生成测试用的 JWT token"""
    payload = {
        'user_id': user_id,
        'exp': int(time.time()) + 3600  # 1小时后过期
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')


def test_websocket_connection():
    """测试 WebSocket 连接"""
    print("=" * 60)
    print("测试 1: WebSocket 连接")
    print("=" * 60)
    
    # 创建客户端
    client = Client()
    
    # 生成 token
    token = generate_test_token("test_user_001")
    print(f"✓ 生成 JWT token: {token[:50]}...")
    
    # 连接到服务器
    try:
        client.connect(
            SERVER_URL,
            auth={'token': token},
            transports=['websocket']
        )
        print("✓ WebSocket 连接成功")
        
        # 等待接收连接成功消息
        time.sleep(1)
        
        # 断开连接
        client.disconnect()
        print("✓ 断开连接成功")
        
        return True
        
    except Exception as e:
        print(f"✗ 连接失败: {e}")
        return False


def test_room_subscription():
    """测试房间订阅"""
    print("\n" + "=" * 60)
    print("测试 2: 房间订阅")
    print("=" * 60)
    
    client = Client()
    token = generate_test_token("test_user_002")
    
    # 用于接收消息的标志
    received_messages = []
    
    @client.on('connected')
    def on_connected(data):
        print(f"✓ 收到连接成功消息: {data}")
        received_messages.append(('connected', data))
    
    @client.on('subscribed')
    def on_subscribed(data):
        print(f"✓ 收到订阅成功消息: {data}")
        received_messages.append(('subscribed', data))
    
    @client.on('subscribe_error')
    def on_subscribe_error(data):
        print(f"✗ 订阅失败: {data}")
        received_messages.append(('subscribe_error', data))
    
    try:
        # 连接
        client.connect(SERVER_URL, auth={'token': token}, transports=['websocket'])
        time.sleep(0.5)
        
        # 订阅房间
        print("发送订阅请求: room_id=test_room_001")
        client.emit('subscribe', {'room_id': 'test_room_001'})
        time.sleep(0.5)
        
        # 取消订阅
        print("发送取消订阅请求")
        client.emit('unsubscribe', {'room_id': 'test_room_001'})
        time.sleep(0.5)
        
        # 断开连接
        client.disconnect()
        
        # 检查是否收到预期消息
        if len(received_messages) >= 2:
            print(f"✓ 测试通过，收到 {len(received_messages)} 条消息")
            return True
        else:
            print(f"✗ 测试失败，只收到 {len(received_messages)} 条消息")
            return False
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False


def test_heartbeat():
    """测试心跳"""
    print("\n" + "=" * 60)
    print("测试 3: 心跳机制")
    print("=" * 60)
    
    client = Client()
    token = generate_test_token("test_user_003")
    
    pong_received = []
    
    @client.on('pong')
    def on_pong(data):
        print(f"✓ 收到 pong 响应: {data}")
        pong_received.append(data)
    
    try:
        # 连接
        client.connect(SERVER_URL, auth={'token': token}, transports=['websocket'])
        time.sleep(0.5)
        
        # 发送 ping
        print("发送 ping 消息")
        client.emit('ping')
        time.sleep(0.5)
        
        # 断开连接
        client.disconnect()
        
        if len(pong_received) > 0:
            print("✓ 心跳测试通过")
            return True
        else:
            print("✗ 未收到 pong 响应")
            return False
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False


def test_invalid_token():
    """测试无效 token"""
    print("\n" + "=" * 60)
    print("测试 4: 无效 Token 拒绝连接")
    print("=" * 60)
    
    client = Client()
    
    try:
        # 使用无效 token 连接
        client.connect(
            SERVER_URL,
            auth={'token': 'invalid_token'},
            transports=['websocket']
        )
        print("✗ 测试失败：应该拒绝连接但却成功了")
        client.disconnect()
        return False
        
    except Exception as e:
        print(f"✓ 正确拒绝了无效 token: {e}")
        return True


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("WebSocket 基础功能测试")
    print("=" * 60)
    print(f"服务器地址: {SERVER_URL}")
    print(f"请确保服务器正在运行: python -m src.main")
    print("=" * 60 + "\n")
    
    time.sleep(2)  # 等待用户准备
    
    results = []
    
    # 运行测试
    results.append(("连接测试", test_websocket_connection()))
    results.append(("订阅测试", test_room_subscription()))
    results.append(("心跳测试", test_heartbeat()))
    results.append(("无效Token测试", test_invalid_token()))
    
    # 输出结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{name}: {status}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print("=" * 60)
    print(f"总计: {passed}/{total} 通过")
    print("=" * 60)
    
    return passed == total


if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
        exit(1)
    except Exception as e:
        print(f"\n\n测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
