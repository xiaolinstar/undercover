#!/usr/bin/env python3
"""
命名风格转换工具
用于处理 snake_case 和 camelCase 之间的转换
"""

def snake_to_camel(snake_str):
    """将 snake_case 转换为 camelCase"""
    parts = snake_str.split('_')
    return parts[0] + ''.join(word.capitalize() for word in parts[1:])


def camel_to_snake(camel_str):
    """将 camelCase 转换为 snake_case"""
    snake_str = ""
    for i, char in enumerate(camel_str):
        if char.isupper() and i > 0:
            snake_str += "_"
        snake_str += char.lower()
    return snake_str


def convert_dict_keys(data, convert_func):
    """递归转换字典键的命名风格"""
    if isinstance(data, dict):
        return {convert_func(key): convert_dict_keys(value, convert_func) for key, value in data.items()}
    elif isinstance(data, list):
        return [convert_dict_keys(item, convert_func) for item in data]
    else:
        return data


def snake_to_camel_dict(data):
    """将字典的所有键从 snake_case 转换为 camelCase"""
    return convert_dict_keys(data, snake_to_camel)


def camel_to_snake_dict(data):
    """将字典的所有键从 camelCase 转换为 snake_case"""
    return convert_dict_keys(data, camel_to_snake)
