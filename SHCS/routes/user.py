from flask import Blueprint, jsonify, request, current_app
from models.user import User
from utils.auth import login_required
from extensions import db
import os
from werkzeug.utils import secure_filename
from models.family import Family

user_bp = Blueprint('user', __name__)

@user_bp.route('/api/user/profile', methods=['GET'])
@login_required
def get_user_profile():
    """获取用户个人信息"""
    try:
        # current_user 由 login_required 装饰器提供
        user = User.query.get(current_user.id)
        if not user:
            return jsonify({'code': 404, 'message': '用户不存在'}), 404
            
        return jsonify({
            'code': 200,
            'data': {
                'id': user.id,
                'name': user.username,
                'phone': user.phone,
                'avatar': user.avatar,
                'family': user.family_id,  # 需要在User模型中添加family_id字段
                'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }
        })
    except Exception as e:
        current_app.logger.error(f"获取用户信息失败: {str(e)}")
        return jsonify({'code': 500, 'message': '服务器错误'}), 500

@user_bp.route('/api/user/profile', methods=['PUT'])
@login_required
def update_user_profile():
    """更新用户个人信息"""
    try:
        data = request.get_json()
        user = User.query.get(current_user.id)
        
        if not user:
            return jsonify({'code': 404, 'message': '用户不存在'}), 404

        # 更新用户信息
        if 'username' in data:
            user.username = data['username']
        if 'phone' in data:
            user.phone = data['phone']
        if 'family_id' in data:
            user.family_id = data['family_id']

        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '更新成功',
            'data': {
                'id': user.id,
                'name': user.username,
                'phone': user.phone,
                'avatar': user.avatar,
                'family': user.family_id
            }
        })
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"更新用户信息失败: {str(e)}")
        return jsonify({'code': 500, 'message': '服务器错误'}), 500

@user_bp.route('/api/user/avatar', methods=['POST'])
@login_required
def upload_avatar():
    """上传用户头像"""
    try:
        if 'avatar' not in request.files:
            return jsonify({'code': 400, 'message': '没有文件'}), 400
            
        file = request.files['avatar']
        if file.filename == '':
            return jsonify({'code': 400, 'message': '没有选择文件'}), 400

        if file:
            # 确保文件名安全
            filename = secure_filename(file.filename)
            # 生成唯一文件名
            unique_filename = f"{current_user.id}_{filename}"
            # 保存路径
            avatar_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'avatars', unique_filename)
            
            # 确保目录存在
            os.makedirs(os.path.dirname(avatar_path), exist_ok=True)
            
            # 保存文件
            file.save(avatar_path)
            
            # 更新用户头像路径
            user = User.query.get(current_user.id)
            user.avatar = f"/uploads/avatars/{unique_filename}"
            db.session.commit()
            
            return jsonify({
                'code': 200,
                'message': '上传成功',
                'data': {
                    'avatar_url': user.avatar
                }
            })
            
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"上传头像失败: {str(e)}")
        return jsonify({'code': 500, 'message': '服务器错误'}), 500

@user_bp.route('/api/family', methods=['POST'])
@login_required
def create_family():
    """创建家庭"""
    try:
        data = request.get_json()
        family = Family(
            name=data['name'],
            address=data.get('address'),
            created_by=current_user.id
        )
        db.session.add(family)
        db.session.commit()
        
        # 将创建者加入该家庭
        user = User.query.get(current_user.id)
        user.family_id = family.id
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '创建成功',
            'data': family.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"创建家庭失败: {str(e)}")
        return jsonify({'code': 500, 'message': '服务器错误'}), 500

@user_bp.route('/api/family/join', methods=['POST'])
@login_required
def join_family():
    """加入家庭"""
    try:
        data = request.get_json()
        family_id = data['family_id']
        
        family = Family.query.get(family_id)
        if not family:
            return jsonify({'code': 404, 'message': '家庭不存在'}), 404
            
        user = User.query.get(current_user.id)
        user.family_id = family_id
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '加入成功',
            'data': family.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"加入家庭失败: {str(e)}")
        return jsonify({'code': 500, 'message': '服务器错误'}), 500 