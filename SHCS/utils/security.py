import re
import jwt
import datetime  # 直接导入datetime模块
from functools import wraps
from flask import request, jsonify, current_app
import redis
from time import time
import bcrypt
from typing import Dict, Optional
from config import Config

class SecurityUtils:
    def __init__(self):
        # Redis连接配置
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
        
    @staticmethod
    def validate_password_strength(password):
        """
        验证密码强度
        要求：至少8个字符，包含大小写字母、数字和特殊字符
        """
        if len(password) < 8:
            return False, "密码长度至少为8个字符"
            
        if not re.search(r"[A-Z]", password):
            return False, "密码必须包含大写字母"
            
        if not re.search(r"[a-z]", password):
            return False, "密码必须包含小写字母"
            
        if not re.search(r"\d", password):
            return False, "密码必须包含数字"
            
        if not re.search(r"[ !@#$%&'()*+,-./[\\\]^_`{|}~"+r'"]', password):
            return False, "密码必须包含特殊字符"
            
        return True, "密码强度符合要求"

    def generate_token(self, user_id, role=None):
        """
        生成JWT token
        """
        payload = {
            'user_id': user_id,
            'role': role,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)  # 1天过期
        }
        token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
        if isinstance(token, bytes):
            return token.decode('utf-8')
        return token

    def verify_token(self, token):
        """
        验证JWT token
        """
        try:
            payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            return True, payload
        except jwt.ExpiredSignatureError:
            return False, "Token已过期"
        except jwt.InvalidTokenError:
            return False, "无效的Token"

    def rate_limit(self, key, limit=10, period=60):
        """
        请求频率限制
        key: 限制的键（如IP或用户ID）
        limit: 允许的请求次数
        period: 时间周期（秒）
        """
        current = time()
        pipeline = self.redis_client.pipeline()
        pipeline.zadd(key, {current: current})
        pipeline.zremrangebyscore(key, 0, current - period)
        pipeline.zcard(key)
        pipeline.expire(key, period)
        _, _, count, _ = pipeline.execute()
        return count <= limit

def require_auth(f):
    """
    认证装饰器
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': '缺少认证token'}), 401

        security = SecurityUtils()
        success, result = security.verify_token(token.split(' ')[1] if ' ' in token else token)
        if not success:
            return jsonify({'message': result}), 401

        return f(*args, **kwargs)
    return decorated

def require_role(roles):
    """
    角色验证装饰器
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = request.headers.get('Authorization')
            if not token:
                return jsonify({'message': '缺少认证token'}), 401

            security = SecurityUtils()
            success, result = security.verify_token(token.split(' ')[1] if ' ' in token else token)
            if not success:
                return jsonify({'message': result}), 401

            if result['role'] not in roles:
                return jsonify({'message': '权限不足'}), 403

            return f(*args, **kwargs)
        return decorated
    return decorator

def hash_password(password):
    """对密码进行哈希"""
    if isinstance(password, str):
        password = password.encode('utf-8')
    return bcrypt.hashpw(password, bcrypt.gensalt())

def verify_password(password, hashed_password):
    """验证密码"""
    if isinstance(password, str):
        password = password.encode('utf-8')
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode('utf-8')
    try:
        return bcrypt.checkpw(password, hashed_password)
    except Exception as e:
        print(f"Password verification error: {str(e)}")
        return False

def generate_token(user_id, role=None):
    """生成JWT token"""
    payload = {
        'user_id': user_id,
        'role': role
    }
    return jwt.encode(payload, Config.SECRET_KEY, algorithm='HS256')

def verify_token(token: str, secret_key: str) -> Optional[Dict]:
    """
    验证JWT令牌
    """
    try:
        return jwt.decode(token, secret_key, algorithms=['HS256'])
    except jwt.InvalidTokenError:
        return None

# 添加一个简单的内存型速率限制器
_rate_limits = {}

def rate_limit(key, limit=5, period=300):
    """
    简单的速率限制实现
    :param key: 限制的键（比如IP地址）
    :param limit: 允许的最大请求次数
    :param period: 时间周期（秒）
    :return: 是否允许请求
    """
    current = time.time()
    if key not in _rate_limits:
        _rate_limits[key] = []
    
    # 清理过期的记录
    _rate_limits[key] = [t for t in _rate_limits[key] if t > current - period]
    
    if len(_rate_limits[key]) >= limit:
        return False
    
    _rate_limits[key].append(current)
    return True 