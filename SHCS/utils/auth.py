from functools import wraps
from flask import request, jsonify, g
from models.models import User
from utils.security import SecurityUtils
from config import Config

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'message': '无效的认证头部'}), 401

        if not token:
            return jsonify({'message': '缺少认证令牌'}), 401

        try:
            # 使用 SecurityUtils 验证 token
            security_utils = SecurityUtils()
            success, payload = security_utils.verify_token(token)
            
            if not success:
                return jsonify({'message': payload}), 401

            # 从数据库获取用户信息
            user = User.query.get(payload['user_id'])
            if not user:
                return jsonify({'message': '用户不存在'}), 401
                
            # 设置当前用户到 g 对象
            g.current_user = user
        except Exception as e:
            return jsonify({'message': '认证失败', 'error': str(e)}), 401

        return f(*args, **kwargs)
    return decorated_function 