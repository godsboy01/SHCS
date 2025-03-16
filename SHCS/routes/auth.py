import os
import random
import time
import uuid
import re

from flask import Blueprint, request, jsonify, current_app, send_from_directory, abort
from werkzeug.utils import secure_filename

from models.models import User, db, Family, CareRelationship
from utils import security
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
    
    # 验证角色
    if data['role'] not in ['admin', 'guardian', 'elderly']:
        return jsonify({'message': '无效的用户角色'}), 400
    
    # 验证密码强度
    password_valid, password_message = SecurityUtils.validate_password_strength(data['password'])
    if not password_valid:
        return jsonify({'message': password_message}), 400
    
    # 验证用户名是否已存在
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': '用户名已存在'}), 400
        
    # 验证手机号格式
    if not re.match(r'^1[3-9]\d{9}$', data['phone']):
        return jsonify({'message': '无效的手机号码'}), 400
    
    try:
        # 创建新用户
        new_user = User(
            username=data['username'],
            password=security.hash_password(data['password']).decode('utf-8'),  # 存储为字符串
            role=data['role'],
            name=data['name'],
            phone=data['phone'],
            email=data.get('email')
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        # 如果是被监护人，且指定了监护人ID，创建监护关系
        guardian_id = data.get('guardian_id')
        if data['role'] == 'elderly' and guardian_id:
            guardian = User.query.get(guardian_id)
            if guardian and guardian.role == 'guardian':
                care_relationship = CareRelationship(
                    guardian_id=guardian_id,
                    elderly_id=new_user.user_id
                )
                db.session.add(care_relationship)
        
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
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # 查找用户
    user = User.query.filter_by(username=username).first()
    
    # 验证用户和密码
    if user and security.verify_password(password, user.password):
        # 生成token，添加role信息
        token = security.generate_token(user.user_id, user.role)  # 添加role参数
        return jsonify({
            'message': '登录成功',
            'token': token,
            'user': {
                'user_id': user.user_id,
                'username': user.username,
                'name': user.name,
                'role': user.role
            }
        }), 200
    
    return jsonify({'message': '用户名或密码错误'}), 401

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
    
    # 获取监护关系信息
    care_info = None
    if user.role == 'guardian':
        elderly_list = [rel.elderly_person for rel in user.as_guardian]
        care_info = [{
            'elderly_id': elderly.user_id,
            'name': elderly.name,
            'phone': elderly.phone
        } for elderly in elderly_list]
    elif user.role == 'elderly':
        guardian_list = [rel.guardian for rel in user.as_elderly]
        care_info = [{
            'guardian_id': guardian.user_id,
            'name': guardian.name,
            'phone': guardian.phone
        } for guardian in guardian_list]
        
    return jsonify({
        'user_id': user.user_id,
        'username': user.username,
        'role': user.role,
        'name': user.name,
        'phone': user.phone,
        'email': user.email,
        'avatar': user.avatar,
        'care_info': care_info
    }), 200

@auth_bp.route('/update_user/<int:user_id>', methods=['PUT'])
@require_auth
def update_user(user_id):
    data = request.get_json()
    user = User.query.get(user_id)

    if not user:
        return jsonify({'message': '用户不存在'}), 404

    try:
        # 更新基本信息
        if 'name' in data:
            user.name = data['name']
        if 'phone' in data:
            if not re.match(r'^1[3-9]\d{9}$', data['phone']):
                return jsonify({'message': '无效的手机号码'}), 400
            user.phone = data['phone']
        if 'email' in data:
            user.email = data['email']
        if 'password' in data:
            if not SecurityUtils.validate_password_strength(data['password']):
                return jsonify({'message': '密码强度不足'}), 400
            user.password = security.hash_password(data['password']).decode('utf-8')

        # 更新监护关系
        if 'guardian_id' in data and user.role == 'elderly':
            guardian_id = data['guardian_id']
            # 删除现有的监护关系
            CareRelationship.query.filter_by(elderly_id=user.user_id).delete()
            # 添加新的监护关系
            if guardian_id:
                guardian = User.query.get(guardian_id)
                if guardian and guardian.role == 'guardian':
                    care_relationship = CareRelationship(
                        guardian_id=guardian_id,
                        elderly_id=user.user_id
                    )
                    db.session.add(care_relationship)

        db.session.commit()
        return jsonify({'message': '用户信息更新成功'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'更新失败: {str(e)}'}), 500

@auth_bp.route('/delete_user/<int:user_id>', methods=['DELETE'])
@require_auth
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': '用户不存在'}), 404

    try:
        # 删除用户的监护关系
        CareRelationship.query.filter(
            (CareRelationship.guardian_id == user_id) | 
            (CareRelationship.elderly_id == user_id)
        ).delete()
        
        # 删除用户
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': '用户删除成功'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'删除失败: {str(e)}'}), 500

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
@require_auth
def get_users():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    role = request.args.get('role')
    search_query = request.args.get('q', '')

    query = User.query

    if role:
        query = query.filter_by(role=role)
    if search_query:
        query = query.filter(
            (User.username.like(f"%{search_query}%")) | 
            (User.name.like(f"%{search_query}%"))
        )

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    users = pagination.items

    user_list = []
    for user in users:
        care_info = None
        if user.role == 'guardian':
            elderly_list = [rel.elderly_person for rel in user.as_guardian]
            care_info = [{
                'elderly_id': elderly.user_id,
                'name': elderly.name,
                'phone': elderly.phone
            } for elderly in elderly_list]
        elif user.role == 'elderly':
            guardian_list = [rel.guardian for rel in user.as_elderly]
            care_info = [{
                'guardian_id': guardian.user_id,
                'name': guardian.name,
                'phone': guardian.phone
            } for guardian in guardian_list]

        user_info = {
            'user_id': user.user_id,
            'username': user.username,
            'name': user.name,
            'phone': user.phone,
            'email': user.email,
            'avatar': user.avatar,
            'role': user.role,
            'care_info': care_info
        }
        user_list.append(user_info)

    return jsonify({
        'users': user_list,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': pagination.page
    }), 200