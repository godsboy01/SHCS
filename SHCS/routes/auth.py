import os
import random
import time
import uuid
import re

from flask import Blueprint, request, jsonify, current_app, send_from_directory, abort
from werkzeug.utils import secure_filename

from models.models import User, db, Family
from utils.password import hash_password
from utils.password import check_password
from utils.upload import handle_upload  # 导入上传工具
from utils.security import SecurityUtils, require_auth, require_role


auth_bp = Blueprint('auth', __name__)
# 设置上传目录
UPLOAD_FOLDER = 'D:/zwd/Pictures/Saved Pictures'
# auth_bp.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@auth_bp.route('/get_avatar/<int:user_id>')
def serve_avatar(user_id):
    # 假设头像文件名是 user_id.jpg
    filename = f"{user_id}.jpg"
    avatar_path = os.path.join('static', 'avatars', filename)

    if os.path.exists(avatar_path):
        return send_from_directory('static/avatars', filename)
    else:
        # 如果找不到对应的头像文件，返回404错误
        abort(404, description="Avatar not found")
# 上传头像
@auth_bp.route('/upload_avatar/<int:user_id>', methods=['POST'])
def upload_avatar(user_id):
    if 'file' not in request.files:
        return jsonify({'message': '未上传文件'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': '未选择文件'}), 400

    # 使用 user_id 作为文件名
    unique_filename = f"{user_id}.jpg"

    # 使用 Flask 应用的配置来获取上传目录
    upload_folder = os.path.join(current_app.root_path, 'static', 'avatars')
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)  # 如果目录不存在则创建

    file_path = os.path.join(upload_folder, unique_filename)

    # 保存文件
    file.save(file_path)

    # 更新用户头像 URL
    user = User.query.get(user_id)
    # avatar_url = f"/uploads/avatars/{unique_filename}"  # 相对于服务器根目录的路径
    avatar_url = f"/static/avatars/{unique_filename}"  # 相对于服务器根目录的路径
    user.avatar = avatar_url
    db.session.commit()

    # 返回完整的URL以便前端可以直接使用
    full_avatar_url = f"http://{request.host}{avatar_url}"
    return jsonify({'message': '头像上传成功', 'avatar_url': full_avatar_url}), 200


# 存储验证码信息
verification_codes = {}

# 发送验证码的模拟函数
def send_sms(phone, code):
    print(f"Sending SMS to {phone} with code: {code}")
    # 这里可以调用实际的短信服务API，例如阿里云、腾讯云等
    return True

@auth_bp.route('/send_code', methods=['POST'])
def send_code():
    data = request.get_json()
    phone = data.get('phone')

    if not phone:
        return jsonify({'message': '手机号不能为空'}), 400

    # 生成随机验证码
    code = str(random.randint(100000, 999999))

    # 模拟发送验证码
    result = send_sms(phone, code)
    if not result:
        return jsonify({'message': '发送验证码失败'}), 500

    # 存储验证码信息
    verification_codes[phone] = {
        'code': code,
        'timestamp': int(time.time())
    }
    print(verification_codes[phone]['code'])

    return jsonify({'message': '验证码已发送'}), 200


# 注册功能 (routes/auth.py)
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # 验证必要字段
    required_fields = ['username', 'password', 'role', 'name', 'phone']
    for field in required_fields:
        if field not in data:
            return jsonify({'message': f'缺少必要字段: {field}'}), 400
    
    # 验证密码强度
    is_valid, msg = security.validate_password_strength(data['password'])
    if not is_valid:
        return jsonify({'message': msg}), 400
    
    # 验证用户名是否已存在
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': '用户名已存在'}), 400
        
    # 验证手机号格式
    if not re.match(r'^1[3-9]\d{9}$', data['phone']):
        return jsonify({'message': '无效的手机号码'}), 400
    
    # 创建新用户
    try:
        new_user = User(
            username=data['username'],
            password=hash_password(data['password']),
            role=data['role'],
            name=data['name'],
            phone=data['phone'],
            email=data.get('email'),
            address=data.get('address'),
            family_id=data.get('family_id')
        )
        db.session.add(new_user)
        db.session.commit()
        
        # 生成token
        token = security.generate_token(new_user.user_id, new_user.role)
        
        return jsonify({
            'message': '注册成功',
            'token': token,
            'user': {
                'user_id': new_user.user_id,
                'username': new_user.username,
                'role': new_user.role,
                'name': new_user.name
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'注册失败: {str(e)}'}), 500

# 登录功能 (routes/auth.py)
@auth_bp.route('/login', methods=['POST'])
def login():
    # 检查请求频率限制
    if not security.rate_limit(f"login:{request.remote_addr}", limit=5, period=300):
        return jsonify({'message': '登录尝试次数过多，请稍后再试'}), 429
        
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'message': '用户名和密码不能为空'}), 400
        
    user = User.query.filter_by(username=username).first()
    if not user or not check_password(password, user.password):
        return jsonify({'message': '用户名或密码错误'}), 401
        
    # 生成token
    token = security.generate_token(user.user_id, user.role)
    
    return jsonify({
        'message': '登录成功',
        'token': token,
        'user': {
            'user_id': user.user_id,
            'username': user.username,
            'role': user.role,
            'name': user.name,
            'avatar': user.avatar
        }
    }), 200

@auth_bp.route('/profile', methods=['GET'])
@require_auth
def get_profile():
    token = request.headers.get('Authorization').split(' ')[1]
    success, payload = security.verify_token(token)
    if not success:
        return jsonify({'message': payload}), 401
        
    user = User.query.get(payload['user_id'])
    if not user:
        return jsonify({'message': '用户不存在'}), 404
        
    return jsonify({
        'user_id': user.user_id,
        'username': user.username,
        'role': user.role,
        'name': user.name,
        'phone': user.phone,
        'email': user.email,
        'address': user.address,
        'avatar': user.avatar,
        'family_id': user.family_id
    }), 200

@auth_bp.route('/update_user/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json()
    print("Received data:", data)  # 打印接收到的数据
    user = User.query.get(user_id)

    if not user:
        return jsonify({'message': '用户不存在'}), 404

    current_family_id = data.get('current_family_id')
    new_family_id = data.get('family_id')

    try:
        if current_family_id is not None:
            current_family_id = int(current_family_id)  # 确保是整数
        new_family_id = int(new_family_id)  # 确保是整数
    except (ValueError, TypeError) as e:
        return jsonify({'message': '请求参数错误: family_id 或 current_family_id 不是有效的整数'}), 400

    print("Current family ID:", current_family_id)
    print("New family ID:", new_family_id)

    # 确保 user.family_id 也是整数类型
    user_family_id = int(user.family_id)

    if current_family_id is not None and user_family_id == current_family_id:
        return jsonify({'message': '用户已经是当前家庭的成员'}), 400
    elif user_family_id == new_family_id:
        return jsonify({'message': '用户已经是该家庭的成员'}), 400
    else:
        # 确保新家庭ID存在
        family = Family.query.get(new_family_id)
        if not family:
            return jsonify({'message': '家庭不存在'}), 404

        user.family_id = new_family_id

    # 更新其他信息
    if 'name' in data:
        user.name = data['name']
    if 'phone' in data:
        user.phone = data['phone']
    if 'email' in data:
        user.email = data['email']
    if 'address' in data:
        user.address = data['address']
    if 'password' in data:
        user.password = hash_password(data['password'])
    if 'role' in data:
        user.role = data['role']

    # 保存到数据库
    db.session.commit()

    return jsonify({'message': '用户信息更新成功', 'user': {'username': user.username, 'role': user.role}}), 200


# 删除账号(routes/auth.py)
@auth_bp.route('/delete_user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get(user_id)

    if not user:
        return jsonify({'message': '用户不存在'}), 404

    # 删除用户
    db.session.delete(user)
    db.session.commit()

    return jsonify({'message': '用户删除成功'}), 200

# 删除账号通过username
# @auth_bp.route('/delete_user/<string:username>', methods=['DELETE'])
# def delete_user(username):
#     user = User.query.filter_by(username=username).first()  # 通过 username 查找用户
#
#     if not user:
#         return jsonify({'message': '用户不存在'}), 404
#
#     # 删除用户
#     db.session.delete(user)
#     db.session.commit()
#
#     return jsonify({'message': '用户删除成功'}), 200

# 获取个人信息
@auth_bp.route('/get_info/<int:user_id>', methods=['GET'])
def get_user_info(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': '用户不存在'}), 404

    # 返回用户信息
    user_info = {
        'user_id': user.user_id,
        'username': user.username,
        'role': user.role,
        'name': user.name,
        'phone': user.phone,
        'email': user.email,
        'address': user.address,
        'avatar': user.avatar,  # 用户头像 URL
        'family_id': user.family_id,
        'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S')  # 格式化时间
    }

    return jsonify(user_info), 200

# 获取个人信息使用名称
@auth_bp.route('/get_infostring/<string:username>', methods=['GET'])
def get_username_info(username):
    user = User.query.filter_by(username=username).first()  # 通过 username 查找用户
    if not user:
        return jsonify({'message': '用户不存在'}), 404

    # 返回用户信息
    user_info = {
        'user_id': user.user_id,
        'username': user.username,
        'role': user.role,
        'name': user.name,
        'phone': user.phone,
        'email': user.email,
        'address': user.address,
        'avatar': user.avatar,  # 用户头像 URL
        'family_id': user.family_id,
        'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S')  # 格式化时间
    }

    return jsonify(user_info), 200


@auth_bp.route('/users', methods=['GET'])
def get_users():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search_query = request.args.get('q', '')

    query = User.query

    if search_query:
        query = query.filter(User.username.like(f"%{search_query}%") | User.name.like(f"%{search_query}%"))

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    users = pagination.items

    user_list = []
    for user in users:
        family_info = None
        if user.family_id:
            family = Family.query.get(user.family_id)
            family_info = {
                'family_id': family.family_id,
                'family_name': family.family_name,
            }

        user_info = {
            'user_id': user.user_id,
            'username': user.username,
            'name': user.name,
            'phone': user.phone,
            'email': user.email,
            'avatar': user.avatar,
            'role': user.role,
            'family': family_info,
        }
        user_list.append(user_info)

    return jsonify({
        'users': user_list,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': pagination.page
    }), 200