#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
谁是卧底游戏集成测试
用于测试核心游戏逻辑的集成流程
"""

import pytest
import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 导入游戏逻辑相关函数
from app import (
    create_room, join_room, start_game, show_status, 
    handle_vote_by_index, check_game_end, get_room, get_user,
    show_word
)


class TestIntegrationFlow:
    """集成流程测试类"""

    def test_complete_game_flow(self):
        """测试完整游戏流程"""
        print("=====================================")
        print("    谁是卧底游戏完整流程测试")
        print("=====================================")
        
        # 1. 创建房间
        print("=== 测试创建房间 ===")
        user_id = "test_user_1"
        result = create_room(user_id)
        print(f"创建房间结果: {result}")
        
        # 验证房间是否创建成功
        assert "房间创建成功" in result
        assert "房间号：" in result
        
        # 从结果中提取房间号
        room_id = result.split("房间号：")[1].split("\n")[0]
        print(f"提取到房间号: {room_id}")
        
        # 验证房间数据
        room = get_room(room_id)
        assert room is not None
        print(f"房间数据验证通过: {room}")
        
        # 2. 加入房间
        print("\n=== 测试加入房间 ===")
        # 创建测试用户
        test_users = [f"test_user_{i}" for i in range(2, 5)]
        
        for user_id in test_users:
            result = join_room(user_id, room_id)
            print(f"用户 {user_id} 加入房间结果: {result}")
            assert "成功加入房间" in result
        
        # 验证房间人数
        room = get_room(room_id)
        assert room is not None
        assert len(room['players']) == 4
        print(f"房间人数验证通过: {len(room['players'])}人")
        
        # 3. 开始游戏
        print("\n=== 测试开始游戏 ===")
        result = start_game("test_user_1")
        print(f"开始游戏结果: {result}")
        assert result == "success"
        
        # 验证游戏状态
        room = get_room(room_id)
        assert room is not None
        assert room['status'] == 'playing'
        print("游戏状态验证通过")
        print(f"卧底数量: {len(room['undercovers'])}")
        print(f"卧底列表: {room['undercovers']}")
        
        # 4. 查看状态
        print("\n=== 测试查看状态 ===")
        result = show_status("test_user_1")
        print(f"查看状态结果:\n{result}")
        
        # 验证是否包含关键信息
        assert "您的信息" in result
        assert "房间号" in result
        print("状态信息验证通过")
        
        # 5. 查看词语
        print("\n=== 测试查看词语 ===")
        result = show_word("test_user_1")
        print(f"查看词语结果: {result}")
        
        # 验证是否包含词语信息
        assert "您的词语：" in result
        print("词语信息验证通过")
        
        # 6. 投票
        print("\n=== 测试投票功能 ===")
        room = get_room(room_id)
        
        assert room is not None
        assert len(room['players']) >= 2
        
        # 房主投票给2号玩家
        result = handle_vote_by_index("test_user_1", 2)
        print(f"投票结果: {result}")
        assert result == "success"
        
        # 验证投票结果
        room = get_room(room_id)
        assert room is not None
        assert len(room['eliminated']) == 1
        print(f"投票验证通过，已淘汰玩家: {room['eliminated']}")
        
        print("\n=====================================")
        print("    游戏流程测试完成")
        print("=====================================")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])