"""
数据验证工具
"""
import re

def validate_email(email: str) -> bool:
    """
    验证邮箱格式
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone(phone: str) -> bool:
    """
    验证手机号格式（中国大陆手机号）
    """
    pattern = r'^1[3-9]\d{9}$'
    return bool(re.match(pattern, phone))

def validate_username(username: str) -> bool:
    """
    验证用户名格式（字母开头，允许字母数字下划线，4-16位）
    """
    pattern = r'^[a-zA-Z][a-zA-Z0-9_]{3,15}$'
    return bool(re.match(pattern, username)) 