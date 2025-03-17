# routes/family.py

from flask import Blueprint, request, jsonify, g
from models.models import User, Family, Device, db
from utils.password import hash_password
from utils.auth import login_required
import re

family_bp = Blueprint('family', __name__)

# 创建家庭
@family_bp.route('/create_family', methods=['POST'])
def create_family():
    data = request.get_json()
    family_name = data.get('family_name')

    if not family_name or len(family_name.strip()) == 0:
        return jsonify({'message': '家庭名称不能为空'}), 400

    # 检查家庭是否已存在
    if Family.query.filter_by(family_name=family_name).first():
        return jsonify({'message': '家庭名称已存在'}), 400

    new_family = Family(family_name=family_name)
    db.session.add(new_family)
    db.session.commit()

    return jsonify({'message': '家庭创建成功', 'family_id': new_family.family_id}), 201

# 获取家庭信息
@family_bp.route('/info', methods=['GET'])
@login_required
def get_family_info():
    user = g.current_user
    if not user.family_id:
        return jsonify({'message': '用户未加入家庭'}), 404

    family = Family.query.get(user.family_id)
    if not family:
        return jsonify({'message': '家庭不存在'}), 404

    # 获取家庭成员信息
    members = User.query.filter_by(family_id=user.family_id).all()
    members_list = [{
        'user_id': member.user_id,
        'name': member.name,
        'phone': member.phone,
        'role': member.role,
        'avatar': member.avatar
    } for member in members]

    return jsonify({
        'address': family.family_address,
        'members': members_list
    }), 200

# 更新家庭地址
@family_bp.route('/address', methods=['PUT'])
@login_required
def update_family_address():
    user = g.current_user
    if not user.family_id:
        return jsonify({'message': '用户未加入家庭'}), 404

    data = request.get_json()
    address = data.get('address')
    
    if not address or not address.strip():
        return jsonify({'message': '地址不能为空'}), 400

    family = Family.query.get(user.family_id)
    if not family:
        return jsonify({'message': '家庭不存在'}), 404

    family.family_address = address.strip()
    db.session.commit()

    return jsonify({'message': '地址更新成功'}), 200

# 添加家庭成员
@family_bp.route('/members', methods=['POST'])
@login_required
def add_family_member():
    user = g.current_user
    if not user.family_id:
        return jsonify({'message': '用户未加入家庭'}), 404

    data = request.get_json()
    phone = data.get('phone')

    if not phone:
        return jsonify({'message': '缺少手机号'}), 400

    if not re.match(r'^1[3-9]\d{9}$', phone):
        return jsonify({'message': '无效的手机号码'}), 400

    # 检查手机号是否已注册
    target_user = User.query.filter_by(phone=phone).first()
    if not target_user:
        return jsonify({'message': '该用户未注册'}), 404

    try:
        # 直接更新用户的family_id
        target_user.family_id = user.family_id
        db.session.commit()
        return jsonify({'message': '成员添加成功'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'添加失败: {str(e)}'}), 500

# 删除家庭成员
@family_bp.route('/members', methods=['DELETE'])
@login_required
def delete_family_member():
    user = g.current_user
    if not user.family_id:
        return jsonify({'message': '用户未加入家庭'}), 404

    data = request.get_json()
    user_id = data.get('userId')

    if not user_id:
        return jsonify({'message': '缺少必要参数'}), 400

    target_user = User.query.get(user_id)
    if not target_user or target_user.family_id != user.family_id:
        return jsonify({'message': '用户不存在或不属于当前家庭'}), 404

    # 不能删除自己
    if target_user.user_id == user.user_id:
        return jsonify({'message': '不能删除自己'}), 400

    target_user.family_id = None
    db.session.commit()

    return jsonify({'message': '成员删除成功'}), 200

# 编辑家人信息
@family_bp.route('/update_member/<int:user_id>', methods=['PUT'])
def update_family_member(user_id):
    data = request.get_json()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': '用户不存在'}), 404

    if 'email' in data and data['email'] and not re.match(r"[^@]+@[^@]+\.[^@]+", data['email']):
        return jsonify({'message': '无效的邮箱地址'}), 400

    for key, value in data.items():
        if hasattr(user, key):
            setattr(user, key, value)

    db.session.commit()
    return jsonify({'message': '家人信息更新成功'}), 200

# 查看家人信息
@family_bp.route('/get_members/<int:family_id>', methods=['GET'])
def get_family_members(family_id):
    members = User.query.filter_by(family_id=family_id).all()
    members_list = [{
        'user_id': member.user_id,
        'username': member.username,
        'role': member.role,
        'name': member.name,
        'phone': member.phone,
        'email': member.email,
        'address': member.address,
    } for member in members]

    return jsonify(members_list), 200

# 添加设备（假设每个设备属于一个家庭）
@family_bp.route('/device/add_device', methods=['POST'])
def add_device():
    data = request.get_json()
    family_id = data.get('family_id')
    device_name = data.get('device_name')
    device_type = data.get('device_type')
    ip_address = data.get('ip_address')
    user_id = data.get('user_id')

    if not all([family_id, device_name, device_type, ip_address]):
        return jsonify({'message': '缺少必要参数'}), 400

    new_device = Device(
        family_id=family_id,
        device_name=device_name,
        device_type=device_type,
        ip_address=ip_address,
        user_id=user_id
    )

    db.session.add(new_device)
    db.session.commit()

    return jsonify({'message': '设备添加成功', 'device_id': new_device.device_id}), 201

# 删除设备
@family_bp.route('/device/delete_device/<int:device_id>', methods=['DELETE'])
def delete_device(device_id):
    device = Device.query.get(device_id)
    if not device:
        return jsonify({'message': '设备不存在'}), 404

    db.session.delete(device)
    db.session.commit()

    return jsonify({'message': '设备删除成功'}), 200

# 编辑设备信息
@family_bp.route('/device/update_device/<int:device_id>', methods=['PUT'])
def update_device(device_id):
    data = request.get_json()
    device = Device.query.get(device_id)
    if not device:
        return jsonify({'message': '设备不存在'}), 404

    for key, value in data.items():
        if hasattr(device, key):
            setattr(device, key, value)

    db.session.commit()
    return jsonify({'message': '设备信息更新成功'}), 200

# 查看设备信息
@family_bp.route('/device/get_devices/<int:family_id>', methods=['GET'])
def get_devices(family_id):
    devices = Device.query.filter_by(family_id=family_id).all()
    devices_list = [{
        'device_id': device.device_id,
        'device_name': device.device_name,
        'device_type': device.device_type,
        'ip_address': device.ip_address,
        'status': device.status
    } for device in devices]

    return jsonify(devices_list), 200

@family_bp.route('/get_family/<int:family_id>', methods=['GET'])
def get_family(family_id):
    family = Family.query.get(family_id)

    if not family:
        return jsonify({'message': '家庭不存在'}), 404

    # 获取家庭成员信息
    members = [{
        'user_id': member.user_id,
        'username': member.username,
        'name': member.name,
        'role': member.role,
        'avatar_url': member.avatar,
    } for member in family.users]

    family_info = {
        'family_id': family.family_id,
        'family_name': family.family_name,
        'members': members,
        'location': family.family_address,  # 假设你有一个 location 字段
        # 'device_count': family.device_count,  # 假设你有一个 device_count 字段
    }

    return jsonify(family_info), 200

# 转移用户到新家庭
@family_bp.route('/transfer_member', methods=['POST'])
@login_required
def transfer_member():
    user = g.current_user
    if not user.family_id:
        return jsonify({'message': '您未加入家庭'}), 404

    data = request.get_json()
    phone = data.get('phone')

    if not phone:
        return jsonify({'message': '缺少必要参数'}), 400

    if not re.match(r'^1[3-9]\d{9}$', phone):
        return jsonify({'message': '无效的手机号码'}), 400

    # 检查手机号是否已注册
    target_user = User.query.filter_by(phone=phone).first()
    if not target_user:
        return jsonify({'message': '该用户未注册'}), 404

    # 保存原始角色
    original_role = target_user.role

    # 先退出原家庭
    target_user.family_id = None
    db.session.commit()

    # 加入新家庭
    target_user.family_id = user.family_id
    target_user.role = original_role  # 保持原有角色
    db.session.commit()

    return jsonify({'message': '成员转移成功'}), 200