#!/usr/bin/env python3
"""
雪花算法ID生成器
用于生成分布式唯一ID
"""

import time
from typing import Optional


class SnowflakeGenerator:
    """
    雪花算法ID生成器
    
    ID结构（64位）：
    - 1位：符号位（始终为0）
    - 41位：时间戳（毫秒级，可以使用69年）
    - 10位：机器ID（支持1024台机器）
    - 12位：序列号（每毫秒4096个ID）
    """
    
    def __init__(self, machine_id: int = 0):
        """
        初始化雪花算法生成器
        
        Args:
            machine_id: 机器ID，范围0-1023
        """
        if machine_id < 0 or machine_id > 1023:
            raise ValueError("Machine ID must be between 0 and 1023")
        
        self.machine_id = machine_id
        self.sequence = 0
        self.last_timestamp = -1
        
        # 常量定义
        self.EPOCH = 1704067200000  # 2024-01-01 00:00:00 UTC (毫秒)
        self.MACHINE_ID_BITS = 10
        self.SEQUENCE_BITS = 12
        self.MACHINE_ID_SHIFT = 12
        self.TIMESTAMP_SHIFT = 22
        
        self.MACHINE_ID_MAX = (1 << self.MACHINE_ID_BITS) - 1
        self.SEQUENCE_MAX = (1 << self.SEQUENCE_BITS) - 1
    
    def generate(self) -> int:
        """
        生成雪花算法ID
        
        Returns:
            64位整数ID
        """
        current_timestamp = self._current_milliseconds()
        
        # 时钟回拨处理
        if current_timestamp < self.last_timestamp:
            raise RuntimeError(f"Clock moved backwards. Refusing to generate ID for {self.last_timestamp - current_timestamp}ms")
        
        # 同一毫秒内，序列号递增
        if current_timestamp == self.last_timestamp:
            self.sequence = (self.sequence + 1) & self.SEQUENCE_MAX
            if self.sequence == 0:
                # 序列号溢出，等待下一毫秒
                current_timestamp = self._wait_next_millisecond(self.last_timestamp)
        else:
            # 新的毫秒，序列号重置
            self.sequence = 0
        
        self.last_timestamp = current_timestamp
        
        # 组装ID
        snowflake_id = (
            ((current_timestamp - self.EPOCH) << self.TIMESTAMP_SHIFT) |
            (self.machine_id << self.MACHINE_ID_SHIFT) |
            self.sequence
        )
        
        return snowflake_id
    
    def generate_str(self) -> str:
        """
        生成雪花算法ID（字符串格式）
        
        Returns:
            字符串格式的ID
        """
        return str(self.generate())
    
    def _current_milliseconds(self) -> int:
        """获取当前时间戳（毫秒）"""
        return int(time.time() * 1000)
    
    def _wait_next_millisecond(self, last_timestamp: int) -> int:
        """等待下一毫秒"""
        current_timestamp = self._current_milliseconds()
        while current_timestamp <= last_timestamp:
            current_timestamp = self._current_milliseconds()
        return current_timestamp


# 全局实例（单例）
_snowflake_generator: Optional[SnowflakeGenerator] = None


def init_snowflake(machine_id: int = 0) -> None:
    """
    初始化雪花算法生成器
    
    Args:
        machine_id: 机器ID，范围0-1023
    """
    global _snowflake_generator
    _snowflake_generator = SnowflakeGenerator(machine_id)


def generate_snowflake_id() -> str:
    """
    生成雪花算法ID（字符串格式）
    
    Returns:
        字符串格式的雪花算法ID
        
    Raises:
        RuntimeError: 如果雪花算法生成器未初始化
    """
    if _snowflake_generator is None:
        raise RuntimeError("Snowflake generator not initialized. Call init_snowflake() first.")
    return _snowflake_generator.generate_str()


def generate_snowflake_id_int() -> int:
    """
    生成雪花算法ID（整数格式）
    
    Returns:
        整数格式的雪花算法ID
        
    Raises:
        RuntimeError: 如果雪花算法生成器未初始化
    """
    if _snowflake_generator is None:
        raise RuntimeError("Snowflake generator not initialized. Call init_snowflake() first.")
    return _snowflake_generator.generate()
