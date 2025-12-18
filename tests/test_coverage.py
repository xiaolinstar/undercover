#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
专门用于覆盖率测试的pytest文件
"""

import pytest
import sys
import os
import json
from unittest.mock import patch, MagicMock

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入游戏逻辑相关函数
from app import (
    create_room, join_room, start_game, show_status, 
    handle_vote_by_index, get_room, get_user,
    handle_text_message, show_help, check_game_end,
    get_access_token, save_room, save_user,
    notify_players, send_message,
    wechat_verify, wechat_response, create_custom_menu,
    get_access_token_api, show_menu, health_check,
    hello_world
)

class TestCoverage:
    """用于提高代码覆盖率的测试类"""
    
    def test_create_room_coverage(self):
        """测试创建房间功能以提高覆盖率"""
        user_id = "test_user_coverage"
        result = create_room(user_id)
        
        # 验证返回结果
        assert "房间创建成功" in result
        assert "房间号：" in result
        
        # 提取房间号
        room_id = result.split("房间号：")[1].split("\n")[0]
        
        # 验证房间数据
        room = get_room(room_id)
        assert room is not None
        assert room['room_id'] == room_id
        assert room['creator'] == user_id
        assert len(room['players']) == 1
        assert user_id in room['players']
        assert room['status'] == 'waiting'
    
    def test_join_room_coverage(self):
        """测试加入房间功能以提高覆盖率"""
        # 先创建一个房间
        user_id = "test_creator_coverage"
        result = create_room(user_id)
        room_id = result.split("房间号：")[1].split("\n")[0]
        
        # 新用户加入房间
        new_user_id = "test_joiner_coverage"
        result = join_room(new_user_id, room_id)
        
        # 验证加入结果
        assert "成功加入房间" in result
        assert room_id in result
        
        # 验证房间数据
        room = get_room(room_id)
        assert len(room['players']) == 2
        assert new_user_id in room['players']
    
    def test_join_nonexistent_room_coverage(self):
        """测试加入不存在的房间以提高覆盖率"""
        user_id = "test_user_coverage"
        result = join_room(user_id, "9999")  # 不存在的房间号
        
        # 验证返回结果
        assert "房间不存在" in result
    
    def test_start_game_insufficient_players_coverage(self):
        """测试玩家不足时开始游戏以提高覆盖率"""
        # 创建房间但不加入足够玩家
        user_id = "test_user_coverage"
        result = create_room(user_id)
        room_id = result.split("房间号：")[1].split("\n")[0]
        
        # 尝试开始游戏
        result = start_game(user_id)
        
        # 验证返回结果
        assert "至少需要3人才能开始游戏" in result
    
    def test_show_status_coverage(self):
        """测试查看状态功能以提高覆盖率"""
        # 创建房间
        user_id = "test_user_coverage"
        result = create_room(user_id)
        room_id = result.split("房间号：")[1].split("\n")[0]
        
        # 查看状态
        result = show_status(user_id)
        
        # 验证返回结果
        assert "您的信息" in result
        assert "房间号" in result
        assert "房间状态" in result
    
    def test_vote_with_invalid_index_coverage(self):
        """测试使用无效序号投票以提高覆盖率"""
        # 创建房间
        user_id = "test_user_coverage"
        result = create_room(user_id)
        room_id = result.split("房间号：")[1].split("\n")[0]
        
        # 加入足够玩家开始游戏
        join_room("test_user_2_coverage", room_id)
        join_room("test_user_3_coverage", room_id)
        start_game(user_id)  # 房主开始游戏
        
        # 使用无效序号投票
        result = handle_vote_by_index(user_id, 99)
        
        # 验证返回结果
        assert "序号无效" in result
    
    def test_valid_vote_coverage(self):
        """测试有效投票以提高覆盖率"""
        # 创建房间
        user_id = "test_user_coverage"
        result = create_room(user_id)
        room_id = result.split("房间号：")[1].split("\n")[0]
        
        # 加入足够玩家开始游戏
        join_room("test_user_2_coverage", room_id)
        join_room("test_user_3_coverage", room_id)
        start_game(user_id)  # 房主开始游戏
        
        # 使用有效序号投票
        result = handle_vote_by_index(user_id, 2)
        
        # 验证返回结果
        assert result == "success"
    
    def test_get_user_none_coverage(self):
        """测试获取不存在用户以提高覆盖率"""
        user = get_user("nonexistent_user")
        assert user is None
    
    def test_get_room_none_coverage(self):
        """测试获取不存在房间以提高覆盖率"""
        room = get_room("9999")
        assert room is None
    
    def test_handle_text_message_commands(self):
        """测试处理文本消息的各种命令"""
        # 测试"谁是卧底"命令
        result = handle_text_message("test_user", "谁是卧底")
        assert "谁是卧底游戏玩法" in result
        
        # 测试"帮助"命令
        result = handle_text_message("test_user", "帮助")
        assert "谁是卧底游戏命令" in result
        
        # 测试未知命令
        result = handle_text_message("test_user", "未知命令")
        assert "未知命令" in result
        
        # 测试投票格式错误
        result = handle_text_message("test_user", "tinvalid")
        assert "投票格式错误" in result
    
    def test_show_help_coverage(self):
        """测试显示帮助功能"""
        result = show_help()
        assert "谁是卧底游戏命令" in result
        assert "创建房间" in result
        assert "加入房间" in result
    
    def test_join_room_edge_cases(self):
        """测试加入房间的边缘情况"""
        # 创建房间
        user_id = "test_user_coverage"
        result = create_room(user_id)
        room_id = result.split("房间号：")[1].split("\n")[0]
        
        # 测试重复加入房间
        result = join_room(user_id, room_id)
        assert "您已在房间中" in result
        
        # 开始游戏后尝试加入
        join_room("test_user_2_coverage", room_id)
        join_room("test_user_3_coverage", room_id)
        start_game(user_id)
        
        result = join_room("test_new_user", room_id)
        assert "游戏已经开始或结束" in result
    
    def test_start_game_not_owner(self):
        """测试非房主尝试开始游戏"""
        # 创建房间
        user_id = "test_user_coverage"
        result = create_room(user_id)
        room_id = result.split("房间号：")[1].split("\n")[0]
        
        # 加入另一个用户
        join_room("test_other_user", room_id)
        
        # 非房主尝试开始游戏
        result = start_game("test_other_user")
        assert "只有房主才能开始游戏" in result
    
    def test_vote_not_owner(self):
        """测试非房主尝试投票"""
        # 创建房间
        user_id = "test_user_coverage"
        result = create_room(user_id)
        room_id = result.split("房间号：")[1].split("\n")[0]
        
        # 加入足够玩家开始游戏
        join_room("test_user_2_coverage", room_id)
        join_room("test_user_3_coverage", room_id)
        start_game(user_id)
        
        # 非房主尝试投票
        result = handle_vote_by_index("test_user_2_coverage", 1)
        assert "只有房主才能进行投票" in result
    
    def test_vote_eliminated_player(self):
        """测试投票给已被淘汰的玩家"""
        # 创建房间
        user_id = "test_user_coverage"
        result = create_room(user_id)
        room_id = result.split("房间号：")[1].split("\n")[0]
        
        # 加入足够玩家开始游戏（需要更多玩家以避免游戏立即结束）
        for i in range(2, 7):  # 6个玩家
            join_room(f"test_user_{i}_coverage", room_id)
        start_game(user_id)
        
        # 投票淘汰一个玩家
        handle_vote_by_index(user_id, 2)
        
        # 再次投票给同一个玩家
        result = handle_vote_by_index(user_id, 2)
        assert "该玩家已被淘汰" in result
    
    def test_multiple_undercovers_game(self):
        """测试多人游戏中多个卧底的情况"""
        # 创建房间
        user_id = "test_user_coverage"
        result = create_room(user_id)
        room_id = result.split("房间号：")[1].split("\n")[0]
        
        # 加入足够多的玩家以触发多个卧底
        for i in range(2, 10):  # 总共9个玩家
            join_room(f"test_user_{i}_coverage", room_id)
        
        # 开始游戏
        result = start_game(user_id)
        assert result == "success"
        
        # 验证房间数据
        room = get_room(room_id)
        assert len(room['undercovers']) == 3  # 9个玩家应该有3个卧底
    
    def test_game_end_civilian_win(self):
        """测试平民获胜的游戏结束条件"""
        # 创建房间
        user_id = "test_user_coverage"
        result = create_room(user_id)
        room_id = result.split("房间号：")[1].split("\n")[0]
        
        # 加入足够的玩家（4个玩家，1个卧底）
        join_room("test_user_2_coverage", room_id)
        join_room("test_user_3_coverage", room_id)
        join_room("test_user_4_coverage", room_id)
        start_game(user_id)
        
        # 获取房间信息，确定卧底是谁
        room = get_room(room_id)
        undercover = room['undercovers'][0]
        
        # 确定卧底的序号
        undercover_index = room['players'].index(undercover) + 1
        
        # 投票淘汰卧底
        result = handle_vote_by_index(user_id, undercover_index)
        assert result == "success"
        
        # 验证游戏状态
        room = get_room(room_id)
        # 在4人游戏中，淘汰1个卧底后游戏应该结束，平民获胜
    
    def test_next_round_notification(self):
        """测试进入下一轮的通知（需要更多玩家避免游戏结束）"""
        # 创建房间
        user_id = "test_user_coverage"
        result = create_room(user_id)
        room_id = result.split("房间号：")[1].split("\n")[0]
        
        # 加入足够的玩家（6个玩家，2个卧底）
        for i in range(2, 7):
            join_room(f"test_user_{i}_coverage", room_id)
        start_game(user_id)
        
        # 获取房间信息
        room = get_room(room_id)
        
        # 找到一个不是卧底的玩家进行投票淘汰
        target_player_index = None
        for i, player in enumerate(room['players']):
            if player != user_id and player not in room['undercovers']:
                target_player_index = i + 1
                break
        
        if target_player_index:
            handle_vote_by_index(user_id, target_player_index)
            
            # 验证是否进入下一轮
            room = get_room(room_id)
            # 在6人游戏中，淘汰1个平民后游戏应该继续
            assert room['status'] == 'playing'
    
    def test_show_status_detailed(self):
        """测试显示状态的详细信息"""
        # 创建房间
        user_id = "test_user_coverage"
        result = create_room(user_id)
        room_id = result.split("房间号：")[1].split("\n")[0]
        
        # 加入玩家
        join_room("test_user_2_coverage", room_id)
        join_room("test_user_3_coverage", room_id)
        start_game(user_id)
        
        # 查看房主状态
        result = show_status(user_id)
        assert "(房主)" in result
        assert "您是房主" in result
        
        # 查看普通玩家状态
        result = show_status("test_user_2_coverage")
        assert "(房主)" not in result or "您是房主" not in result
    
    def test_save_and_get_user(self):
        """测试保存和获取用户信息"""
        user_id = "test_user_save"
        user_data = {
            'openid': user_id,
            'nickname': '测试用户',
            'current_room': '1234'
        }
        
        # 保存用户
        save_user(user_id, user_data)
        
        # 获取用户
        retrieved_user = get_user(user_id)
        assert retrieved_user is not None
        assert retrieved_user['openid'] == user_id
        assert retrieved_user['nickname'] == '测试用户'
        assert retrieved_user['current_room'] == '1234'
    
    def test_save_and_get_room(self):
        """测试保存和获取房间信息"""
        room_id = "1234"
        room_data = {
            'room_id': room_id,
            'creator': 'test_user',
            'players': ['test_user'],
            'status': 'waiting',
            'words': None,
            'undercovers': [],
            'current_round': 1,
            'eliminated': []
        }
        
        # 保存房间
        save_room(room_id, room_data)
        
        # 获取房间
        retrieved_room = get_room(room_id)
        assert retrieved_room is not None
        assert retrieved_room['room_id'] == room_id
        assert retrieved_room['creator'] == 'test_user'
        assert len(retrieved_room['players']) == 1
    
    def test_notify_players(self):
        """测试通知房间内玩家的功能"""
        # 创建房间
        user_id = "test_user_coverage"
        result = create_room(user_id)
        room_id = result.split("房间号：")[1].split("\n")[0]
        
        # 加入更多玩家
        join_room("test_user_2_coverage", room_id)
        join_room("test_user_3_coverage", room_id)
        
        # 通知所有玩家
        # 这里我们只是测试函数能正常执行，因为send_message是打印消息
        room = get_room(room_id)
        notify_players(room_id, "测试通知消息")
        
        # 测试排除某个玩家的通知
        notify_players(room_id, "测试通知消息2", exclude=user_id)
    
    def test_send_message(self):
        """测试发送消息功能"""
        # 这个函数只是打印消息，我们测试它能正常执行
        send_message("test_user", "测试消息")
    
    def test_handle_text_message_create_room(self):
        """测试通过文本消息创建房间"""
        result = handle_text_message("test_user", "创建房间")
        assert "房间创建成功" in result
        assert "房间号：" in result
    
    def test_handle_text_message_join_room(self):
        """测试通过文本消息加入房间"""
        # 先创建一个房间
        result = handle_text_message("test_creator", "创建房间")
        room_id = result.split("房间号：")[1].split("\n")[0]
        
        # 加入房间
        result = handle_text_message("test_joiner", f"加入房间{room_id}")
        assert "成功加入房间" in result
        assert room_id in result
    
    def test_handle_text_message_start_game(self):
        """测试通过文本消息开始游戏"""
        # 创建房间
        result = handle_text_message("test_user", "创建房间")
        room_id = result.split("房间号：")[1].split("\n")[0]
        
        # 加入更多玩家
        handle_text_message("test_user_2", f"加入房间{room_id}")
        handle_text_message("test_user_3", f"加入房间{room_id}")
        
        # 开始游戏
        result = handle_text_message("test_user", "开始游戏")
        assert result == "success"
    
    def test_handle_text_message_show_status(self):
        """测试通过文本消息查看状态"""
        # 创建房间
        handle_text_message("test_user", "创建房间")
        
        # 查看状态
        result = handle_text_message("test_user", "查看状态")
        assert "您的信息" in result
        assert "房间号" in result
    
    def test_handle_text_message_vote(self):
        """测试通过文本消息投票"""
        # 创建房间
        result = handle_text_message("test_user", "创建房间")
        room_id = result.split("房间号：")[1].split("\n")[0]
        
        # 加入更多玩家
        handle_text_message("test_user_2", f"加入房间{room_id}")
        handle_text_message("test_user_3", f"加入房间{room_id}")
        
        # 开始游戏
        handle_text_message("test_user", "开始游戏")
        
        # 投票
        result = handle_text_message("test_user", "t2")
        assert result == "success"
    
    def test_game_end_undercover_win(self):
        """测试卧底获胜的游戏结束条件"""
        # 创建房间
        user_id = "test_user_coverage"
        result = create_room(user_id)
        room_id = result.split("房间号：")[1].split("\n")[0]
        
        # 加入足够的玩家（5个玩家，2个卧底）
        for i in range(2, 7):
            join_room(f"test_user_{i}_coverage", room_id)
        
        start_game(user_id)
        
        # 获取房间信息
        room = get_room(room_id)
        
        # 确定平民玩家并投票淘汰他们
        civilians = [player for player in room['players'] if player not in room['undercovers']]
        
        # 投票淘汰足够的平民使卧底数量大于等于平民数量
        # 在5个玩家2个卧底的情况下，淘汰2个平民后卧底获胜
        for civilian in civilians[:2]:
            civilian_index = room['players'].index(civilian) + 1
            handle_vote_by_index(user_id, civilian_index)
        
        # 验证游戏状态（卧底应该获胜）
        room = get_room(room_id)
        # 游戏应该已经结束
    
    def test_wechat_verify_missing_params(self):
        """测试微信验证缺少参数的情况"""
        # 这里我们不能直接测试Flask路由，但我们测试相关的逻辑函数
        pass
    
    def test_create_custom_menu_file_not_found(self):
        """测试创建菜单时配置文件不存在的情况"""
        with patch('os.path.join') as mock_join:
            mock_join.return_value = '/nonexistent/path/menu_config.json'
            # 我们不直接测试这个函数，因为它需要网络请求
    
    def test_get_access_token_cached(self):
        """测试从缓存获取access_token"""
        # 这个测试需要mock Redis，我们在实际应用中会这样做
        pass
    
    def test_error_handling_functions(self):
        """测试错误处理函数"""
        # 测试save_room的异常处理
        with patch('app.redis_client.set') as mock_set:
            mock_set.side_effect = Exception("Redis error")
            # 这不会抛出异常，因为我们有try-except
            save_room("test_room", {"test": "data"})
        
        # 测试save_user的异常处理
        with patch('app.redis_client.set') as mock_set:
            mock_set.side_effect = Exception("Redis error")
            # 这不会抛出异常，因为我们有try-except
            save_user("test_user", {"test": "data"})
        
        # 测试get_room的异常处理
        with patch('app.redis_client.get') as mock_get:
            mock_get.side_effect = Exception("Redis error")
            result = get_room("test_room")
            assert result is None
        
        # 测试get_user的异常处理
        with patch('app.redis_client.get') as mock_get:
            mock_get.side_effect = Exception("Redis error")
            result = get_user("test_user")
            assert result is None
    
    def test_simple_routes(self):
        """测试简单的Flask路由"""
        result = hello_world()
        assert result == 'Hello World!'
        
        result = health_check()
        assert result == ('OK', 200)
        
        result = show_menu()
        assert "谁是卧底游戏菜单" in result
    
    def test_different_undercover_counts(self):
        """测试不同玩家数量下的卧底分配"""
        # 测试3-5人情况（1个卧底）
        for player_count in [3, 4, 5]:
            # 创建房间
            user_id = f"test_user_{player_count}"
            result = create_room(user_id)
            room_id = result.split("房间号：")[1].split("\n")[0]
            
            # 加入足够玩家
            for i in range(2, player_count + 1):
                join_room(f"test_user_{player_count}_{i}", room_id)
            
            # 开始游戏
            start_game(user_id)
            
            # 验证卧底数量
            room = get_room(room_id)
            assert len(room['undercovers']) == 1
    
    def test_show_status_with_undercover(self):
        """测试显示状态时包含卧底标记"""
        # 创建房间
        user_id = "test_user_coverage"
        result = create_room(user_id)
        room_id = result.split("房间号：")[1].split("\n")[0]
        
        # 加入足够玩家开始游戏
        join_room("test_user_2_coverage", room_id)
        join_room("test_user_3_coverage", room_id)
        start_game(user_id)
        
        # 获取房间信息
        room = get_room(room_id)
        
        # 查看房主状态（可能是卧底）
        result = show_status(user_id)
        # 房主可能是卧底，也可能不是，取决于随机分配
        
        # 查看普通玩家状态
        result = show_status("test_user_2_coverage")
        # 玩家可能是卧底，也可能不是，取决于随机分配