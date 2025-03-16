import pytest
import jwt
from datetime import datetime, timedelta
from utils.security import SecurityUtils
from flask import Flask
import redis

@pytest.fixture
def app():
    """创建测试用的 Flask 应用"""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'test-secret-key'
    app.config['TESTING'] = True
    return app

@pytest.fixture
def security():
    """创建 SecurityUtils 实例"""
    return SecurityUtils()

def test_password_strength_valid(security):
    """测试有效的密码强度"""
    password = "Test123!@#"
    is_valid, message = security.validate_password_strength(password)
    assert is_valid is True
    assert message == "密码强度符合要求"

def test_password_strength_invalid_length(security):
    """测试密码长度不足"""
    password = "Test1!"
    is_valid, message = security.validate_password_strength(password)
    assert is_valid is False
    assert "密码长度至少为8个字符" in message

def test_password_strength_no_uppercase(security):
    """测试密码缺少大写字母"""
    password = "test123!@#"
    is_valid, message = security.validate_password_strength(password)
    assert is_valid is False
    assert "密码必须包含大写字母" in message

def test_password_strength_no_lowercase(security):
    """测试密码缺少小写字母"""
    password = "TEST123!@#"
    is_valid, message = security.validate_password_strength(password)
    assert is_valid is False
    assert "密码必须包含小写字母" in message

def test_password_strength_no_number(security):
    """测试密码缺少数字"""
    password = "TestTest!@#"
    is_valid, message = security.validate_password_strength(password)
    assert is_valid is False
    assert "密码必须包含数字" in message

def test_password_strength_no_special_char(security):
    """测试密码缺少特殊字符"""
    password = "TestTest123"
    is_valid, message = security.validate_password_strength(password)
    assert is_valid is False
    assert "密码必须包含特殊字符" in message

def test_token_generation_and_verification(app, security):
    """测试 Token 生成和验证"""
    with app.app_context():
        # 生成 token
        user_id = 1
        role = "admin"
        token = security.generate_token(user_id, role)
        
        # 验证 token
        is_valid, payload = security.verify_token(token)
        assert is_valid is True
        assert payload["user_id"] == user_id
        assert payload["role"] == role

def test_token_expiration(app, security):
    """测试 Token 过期"""
    with app.app_context():
        # 创建一个已过期的 token
        user_id = 1
        role = "admin"
        payload = {
            'user_id': user_id,
            'role': role,
            'exp': datetime.utcnow() - timedelta(days=1)
        }
        expired_token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
        
        # 验证过期的 token
        is_valid, message = security.verify_token(expired_token)
        assert is_valid is False
        assert "Token已过期" in message

def test_rate_limit(security):
    """测试请求频率限制"""
    key = "test_rate_limit"
    limit = 3
    period = 10
    
    # 清除之前的测试数据
    security.redis_client.delete(key)
    
    # 前三次请求应该成功
    for _ in range(limit):
        assert security.rate_limit(key, limit, period) is True
    
    # 第四次请求应该失败
    assert security.rate_limit(key, limit, period) is False
    
    # 清理测试数据
    security.redis_client.delete(key)

def test_invalid_token(app, security):
    """测试无效的 Token"""
    with app.app_context():
        invalid_token = "invalid.token.string"
        is_valid, message = security.verify_token(invalid_token)
        assert is_valid is False
        assert "无效的Token" in message 