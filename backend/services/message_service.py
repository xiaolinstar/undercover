#!/usr/bin/env python3
"""
消息服务类
负责处理微信消息和响应
"""

import logging

from wechatpy import parse_message
from wechatpy.exceptions import InvalidSignatureException
from wechatpy.replies import create_reply
from wechatpy.utils import check_signature

from backend.config.messages import HELP_MESSAGES
from backend.services.game_service import GameService
from backend.strategies.commands import CommandRouter

logger = logging.getLogger(__name__)


class MessageService:
    """消息服务类"""

    def __init__(self, game_service: GameService, token: str, redis_client=None, staging_url: str = ""):
        self.game_service = game_service
        self.token = token
        self.redis_client = redis_client
        self.staging_url = staging_url
        self.router = CommandRouter(game_service)

    def verify_wechat_signature(self, signature: str, timestamp: str, nonce: str) -> bool:
        """验证微信签名"""
        try:
            check_signature(self.token, signature, timestamp, nonce)
            return True
        except InvalidSignatureException:
            return False

    def handle_wechat_message(self, xml_data: str, app_env: str = "dev") -> str:
        """处理微信消息"""
        # 解析消息
        msg = parse_message(xml_data)

        if msg is None:
            logger.warning("未能解析微信消息")
            return "抱歉，无法解析您的消息"

        # 1. 检查是否为测试用户且需要路由到 Staging
        # 仅在生产环境下执行路由逻辑
        if app_env == "prod" and self.staging_url:
            is_tester = self.redis_client.get(f"tester:{msg.source}")
            if is_tester and msg.type == "text" and msg.content.strip() != "#exit":
                logger.info(f"路由测试用户 {msg.source} 到 Staging 环境")
                try:
                    import requests

                    resp = requests.post(self.staging_url, data=xml_data.encode("utf-8"), timeout=5)
                    return resp.text
                except Exception as e:
                    logger.error(f"路由到 Staging 失败: {e}")
                    return create_reply("Staging 环境暂时无法连接", msg).render()

        logger.info(f"解析微信消息: 类型={msg.type}, 用户={msg.source}")

        # 根据消息类型处理
        if msg.type == "text":
            content = msg.content.strip().lower()

            # 环境切换指令
            if content == "#debug" and app_env == "prod":
                self.redis_client.setex(f"tester:{msg.source}", 3600, "1")  # 1小时有效期
                return create_reply(
                    "已切换到 Staging 环境，接下来的指令将由预发布版本处理。发送 #exit 退出。", msg
                ).render()
            elif content == "#exit":
                self.redis_client.delete(f"tester:{msg.source}")
                return create_reply("已回到 Production 环境。", msg).render()

            response_content = self.router.route(msg.source, content)
        elif msg.type == "event":
            response_content = self._handle_event_message(msg.source, msg.event)
        else:
            response_content = HELP_MESSAGES["INSTRUCTIONS"]

        # 构造响应
        reply = create_reply(response_content, msg)
        return reply.render()

    def _handle_event_message(self, user_id: str, event: str) -> str:
        """处理事件消息"""
        if event == "subscribe":
            logger.info(f"用户 {user_id} 关注")
            return HELP_MESSAGES["WELCOME"]
        else:
            return HELP_MESSAGES["INSTRUCTIONS"]
