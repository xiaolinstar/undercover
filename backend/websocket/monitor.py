#!/usr/bin/env python3
"""
WebSocket 监控与统计模块
在单实例模式下使用内存进行计数，负责统计连接数、消息数和错误数
"""

import threading

from backend.utils.logger import setup_logger

logger = setup_logger(__name__)


class WSMonitor:
    """WebSocket 监控统计类（单例）"""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._init_counters()
            return cls._instance

    def _init_counters(self):
        """初始化计数器"""
        self.active_connections = 0
        self.total_connections = 0
        self.messages_sent = 0
        self.errors_count = 0
        # 记录特定类型错误的数量
        self.errors_by_type = {}
        # 为了保证线程安全
        self._counter_lock = threading.Lock()

    def record_connection(self):
        """记录新连接"""
        with self._counter_lock:
            self.active_connections += 1
            self.total_connections += 1

    def record_disconnection(self):
        """记录连接断开"""
        with self._counter_lock:
            if self.active_connections > 0:
                self.active_connections -= 1

    def record_message_sent(self, count=1):
        """记录消息发送"""
        with self._counter_lock:
            self.messages_sent += count

    def record_error(self, error_type="UNKNOWN"):
        """记录错误"""
        with self._counter_lock:
            self.errors_count += 1
            self.errors_by_type[error_type] = self.errors_by_type.get(error_type, 0) + 1

    def get_stats(self) -> dict:
        """获取统计信息"""
        with self._counter_lock:
            return {
                "active_connections": self.active_connections,
                "total_connections": self.total_connections,
                "messages_sent": self.messages_sent,
                "errors_count": self.errors_count,
                "errors_by_type": dict(self.errors_by_type),
            }

    def log_stats(self):
        """定期记录统计日志的辅助方法"""
        stats = self.get_stats()
        logger.info(f"WebSocket Stats: {stats}")


# 全局监控实例
ws_monitor = WSMonitor()
