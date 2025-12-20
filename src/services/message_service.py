#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
消息服务类
负责处理微信消息和响应
"""

import hashlib
import xml.etree.ElementTree as ET
from src.services.game_service import GameService
# 修复导入路径，messages.py 在项目根目录下
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.messages import HELP_MESSAGES, ERROR_MESSAGES


class MessageService:
    """消息服务类"""
    
    def __init__(self, game_service: GameService, token: str):
        self.game_service = game_service
        self.token = token
    
    def verify_wechat_signature(self, signature: str, timestamp: str, nonce: str) -> bool:
        """验证微信签名"""
        # 将token、timestamp、nonce三个参数进行字典序排序
        params = [self.token, timestamp, nonce]
        params.sort()
        
        # 将三个参数字符串拼接成一个字符串进行sha1加密
        sha1 = hashlib.sha1()
        sha1.update("".join(params).encode('utf-8'))
        hashcode = sha1.hexdigest()
        
        # 开发者获得加密后的字符串可与signature对比，标识该请求来源于微信
        return hashcode == signature
    
    def handle_wechat_message(self, xml_data: str) -> str:
        """处理微信消息"""
        try:
            # 解析XML数据
            root = ET.fromstring(xml_data)
            
            # 提取消息基本信息
            msg_type = root.find("MsgType").text
            from_user = root.find("FromUserName").text
            to_user = root.find("ToUserName").text
            
            # 根据消息类型处理
            if msg_type == "text":
                content = root.find("Content").text
                response_content = self._handle_text_message(from_user, content)
            elif msg_type == "event":
                event = root.find("Event").text
                response_content = self._handle_event_message(from_user, event)
            else:
                response_content = HELP_MESSAGES["INSTRUCTIONS"]
            
            # 构造响应XML
            return self._build_response_xml(to_user, from_user, response_content)
        except Exception as e:
            print(f"处理微信消息异常: {e}")
            return self._build_response_xml(
                to_user, 
                from_user, 
                ERROR_MESSAGES["SYSTEM_ERROR"]
            )
    
    def _handle_text_message(self, user_id: str, content: str) -> str:
        """处理文本消息"""
        content = content.strip().lower()
        
        # 处理用户命令
        if content in ['谁是卧底', '帮助']:
            return HELP_MESSAGES["INSTRUCTIONS"]
        elif content == '创建房间':
            success, result = self.game_service.create_room(user_id)
            if success:
                return f"房间创建成功！房间号：{result}\n请其他玩家输入'加入房间{result}'加入房间\n房主输入'开始游戏'即可开始游戏"
            else:
                return result
        elif content.startswith('加入房间'):
            room_id = content[4:].strip()  # 去掉"加入房间"前缀
            if not room_id:
                return "请输入房间号，格式：加入房间1234"
            
            success, result = self.game_service.join_room(user_id, room_id)
            return result
        elif content == '开始游戏':
            success, result = self.game_service.start_game(user_id)
            if success:
                # 获取用户词语
                word_success, word_result = self.game_service.show_word(user_id)
                if word_success:
                    return f"游戏开始！\n{word_result}\n请根据您的词语进行描述，注意不要暴露自己的身份\n线下进行描述和讨论，结束后由房主进行最终投票决定胜负"
                else:
                    return "游戏开始成功！\n请根据您的词语进行描述，注意不要暴露自己的身份\n线下进行描述和讨论，结束后由房主进行最终投票决定胜负"
            else:
                return result
        elif content == '查看状态':
            success, result = self.game_service.show_status(user_id)
            return result
        elif content == '查看词语':
            success, result = self.game_service.show_word(user_id)
            return result
        elif content.startswith('t'):
            # 房主投票，格式为 t+序号
            try:
                target_index = int(content[1:])
                success, result = self.game_service.vote_player(user_id, target_index)
                return result
            except ValueError:
                return ERROR_MESSAGES["VOTE_FORMAT_ERROR"]
        else:
            return ERROR_MESSAGES["UNKNOWN_COMMAND"]

    @staticmethod
    def _handle_event_message(user_id: str, event: str) -> str:
        """处理事件消息"""
        if event == "subscribe":
            return HELP_MESSAGES["WELCOME"]
        else:
            return HELP_MESSAGES["INSTRUCTIONS"]

    @staticmethod
    def _build_response_xml(to_user: str, from_user: str, content: str) -> str:
        """构造响应XML"""
        response_template = f"""
        <xml>
        <ToUserName><![CDATA[{to_user}]]></ToUserName>
        <FromUserName><![CDATA[{from_user}]]></FromUserName>
        <CreateTime>123456789</CreateTime>
        <MsgType><![CDATA[text]]></MsgType>
        <Content><![CDATA[{content}]]></Content>
        </xml>
        """
        return response_template.strip()