"""
安全性功能测试
"""
import pytest
from SHCS.utils.security import SecurityUtils
from SHCS import create_app

@pytest.fixture
def app():
    """创建测试应用"""
    app = create_app()
    app.config['SECRET_KEY'] = 'test_secret_key'
    return app

@pytest.fixture
def client(app):
    """创建测试客户端"""
    return app.test_client()

def test_password_strength_validation():
    """测试密码强度验证功能"""
    security = SecurityUtils()
    
    # 测试弱密码
    success, msg = security.validate_password_strength("weak")
    assert not success
    assert "密码长度至少为8个字符" in msg
    
    # 测试缺少大写字母的密码
    success, msg = security.validate_password_strength("password123!")
    assert not success
    assert "密码必须包含大写字母" in msg
    
    # 测试缺少小写字母的密码
    success, msg = security.validate_password_strength("PASSWORD123!")
    assert not success
    assert "密码必须包含小写字母" in msg
    
    # 测试缺少数字的密码
    success, msg = security.validate_password_strength("Password!")
    assert not success
    assert "密码必须包含数字" in msg
    
    # 测试缺少特殊字符的密码
    success, msg = security.validate_password_strength("Password123")
    assert not success
    assert "密码必须包含特殊字符" in msg
    
    # 测试强密码
    success, msg = security.validate_password_strength("Password123!")
    assert success
    assert "密码强度符合要求" in msg

def test_token_operations(app):
    """测试令牌生成和验证功能"""
    with app.app_context():
        security = SecurityUtils()
        user_id = 123
        role = "admin"
        
        # 测试令牌生成
        token = security.generate_token(user_id, role)
        assert token is not None
        
        # 测试令牌验证
        success, payload = security.verify_token(token)
        assert success
        assert payload['user_id'] == user_id
        assert payload['role'] == role
        
        # 测试无效令牌
        success, msg = security.verify_token("invalid.token.here")
        assert not success
        assert "无效的Token" in msg 