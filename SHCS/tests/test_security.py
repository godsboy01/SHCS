"""
安全性功能测试
"""
import pytest
from SHCS.utils.security import (
    hash_password,
    verify_password,
    generate_token,
    verify_token
)

def test_password_hashing():
    """测试密码哈希功能"""
    password = "test_password123"
    hashed = hash_password(password)
    
    # 验证哈希后的密码不等于原始密码
    assert hashed != password.encode('utf-8')
    
    # 验证密码验证功能
    assert verify_password(password, hashed) is True
    assert verify_password("wrong_password", hashed) is False

def test_token_generation():
    """测试令牌生成和验证功能"""
    secret_key = "test_secret_key"
    user_id = 123
    
    # 生成令牌
    token = generate_token(user_id, secret_key)
    assert token is not None
    
    # 验证令牌
    payload = verify_token(token, secret_key)
    assert payload is not None
    assert payload['user_id'] == user_id
    
    # 验证无效令牌
    invalid_token = "invalid.token.here"
    assert verify_token(invalid_token, secret_key) is None 