from flask import Blueprint, request, jsonify, current_app
from models.models import User, Family, Device
from utils.auth import login_required
from extensions import db
import os
from werkzeug.utils import secure_filename

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/api/profile', methods=['GET'])
@login_required
def get_profile():
    """获取用户个人信息"""
    try:
        user = User.query.get(current_user.id)
        family = Family.query.get(user.family_id)
        devices = Device.query.filter_by(user_id=current_user.id).all()
        
        return jsonify({
            'code': 200,
            'data': {
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'phone': user.phone,
                    'avatar': user.avatar
                },
                'family': {
                    'id': family.family_id if family else None,
                    'name': family.family_name if family else None,
                    'address': family.family_address if family else None
                },
                'devices': [device.to_dict() for device in devices]
            }
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e)}), 500

@profile_bp.route('/api/profile', methods=['PUT'])
@login_required
def update_profile():
    """更新用户个人信息"""
    try:
        data = request.get_json()
        user = User.query.get(current_user.id)
        
        if 'username' in data:
            user.username = data['username']
        if 'phone' in data:
            user.phone = data['phone']
            
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '更新成功',
            'data': {
                'id': user.id,
                'username': user.username,
                'phone': user.phone
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e)}), 500

@profile_bp.route('/api/profile/avatar', methods=['POST'])
@login_required
def update_avatar():
    """更新用户头像"""
    try:
        if 'avatar' not in request.files:
            return jsonify({'code': 400, 'message': '没有文件'}), 400
            
        file = request.files['avatar']
        if file.filename == '':
            return jsonify({'code': 400, 'message': '没有选择文件'}), 400
            
        if file:
            filename = secure_filename(f"avatar_{current_user.id}_{file.filename}")
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], 'avatars', filename)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            file.save(filepath)
            
            user = User.query.get(current_user.id)
            user.avatar = f"/uploads/avatars/{filename}"
            db.session.commit()
            
            return jsonify({
                'code': 200,
                'message': '上传成功',
                'data': {'avatar_url': user.avatar}
            })
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e)}), 500 