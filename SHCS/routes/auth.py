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
    try:
        # 确保头像目录存在
        avatar_dir = os.path.join(current_app.root_path, 'static', 'avatars')
        if not os.path.exists(avatar_dir):
            os.makedirs(avatar_dir)

        # 假设头像文件名是 user_id.jpg
        filename = f"{user_id}.jpg"
        avatar_path = os.path.join(avatar_dir, filename)

        if os.path.exists(avatar_path):
            return send_from_directory(os.path.join(current_app.root_path, 'static', 'avatars'), filename)
        else:
            # 如果找不到对应的头像文件，返回默认头像
            default_avatar = os.path.join(current_app.root_path, 'static', 'default-avatar.jpg')
            if os.path.exists(default_avatar):
                return send_from_directory(os.path.join(current_app.root_path, 'static'), 'default-avatar.jpg')
            return jsonify({'message': '头像不存在'}), 404
    except Exception as e:
        print(f"Error serving avatar: {str(e)}")
        return jsonify({'message': '服务器错误'}), 500

@auth_bp.route('/upload_avatar', methods=['POST'])
@require_auth
def upload_avatar():
    if 'avatar' not in request.files:
        return jsonify({
            'code': 400,
            'message': '未上传文件'
        }), 400

    file = request.files['avatar']
    if file.filename == '':
        return jsonify({
            'code': 400,
            'message': '未选择文件'
        }), 400

    user_id = request.form.get('user_id')
    if not user_id:
        return jsonify({
            'code': 400,
            'message': '缺少用户ID'
        }), 400

    try:
        # 确保上传目录存在
        upload_folder = os.path.join(current_app.root_path, 'static', 'avatars')
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)

        # 使用 user_id 作为文件名
        filename = f"{user_id}.jpg"
        file_path = os.path.join(upload_folder, filename)

        # 保存文件
        file.save(file_path)

        # 更新用户头像 URL
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'code': 404,
                'message': '用户不存在'
            }), 404

        # 设置相对路径
        avatar_url = f"/static/avatars/{filename}"
        user.avatar = avatar_url
        db.session.commit()

        # 返回完整的URL
        full_avatar_url = f"http://{request.host}{avatar_url}"
        return jsonify({
            'code': 200,
            'message': '头像上传成功',
            'data': {
                'avatar_url': full_avatar_url
            }
        }), 200

    except Exception as e:
        print(f"Error uploading avatar: {str(e)}")
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': f'上传失败: {str(e)}'
        }), 500


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
    try:
        data = request.get_json()
        
        # 检查用户是否已存在
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'code': 400, 'message': '用户名已存在'}), 400
            
        # 创建新用户
        hashed_password = hash_password(data['password'])
        new_user = User(
            username=data['username'],
            password=hashed_password,
            phone=data.get('phone', ''),
            role=data.get('role', 'user'),
            name=data.get('name', ''),
            email=data.get('email', '')
        )
        db.session.add(new_user)
        db.session.flush()  # 获取用户ID
        
        # 创建默认家庭
        default_family = Family(
            family_name=f"{data['name']}的家",
            family_address=""
        )
        db.session.add(default_family)
        db.session.flush()
        
        # 更新用户的家庭ID
        new_user.family_id = default_family.family_id
        
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '注册成功',
            'data': {
                'user_id': new_user.user_id,
                'username': new_user.username,
                'family_id': new_user.family_id
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e)}), 500

# 登录功能 (routes/auth.py)
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': '用户名和密码不能为空'}), 400

    user = User.query.filter_by(username=username).first()
    if user and check_password(password, user.password):
        security_utils = SecurityUtils()  # 创建 SecurityUtils 实例
        token = security_utils.generate_token(user.user_id, user.role)  # 使用实例方法生成 token
        return jsonify({
            'message': '登录成功',
            'token': token,
            'user_id': user.user_id,
            'role': user.role
        }), 200
    return jsonify({'message': '用户名或密码错误'}), 401

@auth_bp.route('/profile', methods=['GET'])
@require_auth
def get_profile():
    token = request.headers.get('Authorization').split(' ')[1]
    security_utils = SecurityUtils()  # 创建 SecurityUtils 实例
    success, payload = security_utils.verify_token(token)  # 使用实例方法验证 token
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
            user.password = hash_password(data['password'])

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

    # 获取家庭地址
    family_address = user.family.family_address if user.family else None

    # 返回用户信息
    user_info = {
        'user_id': user.user_id,
        'username': user.username,
        'role': user.role,
        'name': user.name,
        'phone': user.phone,
        'email': user.email,
        'avatar': user.avatar,  # 用户头像 URL
        'family_id': user.family_id,
        'family_address': family_address,
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