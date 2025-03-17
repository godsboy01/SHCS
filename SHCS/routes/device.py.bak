from flask import Blueprint, request, jsonify
from models.models import Device, db
from utils.security import require_auth
from datetime import datetime

device_bp = Blueprint('device', __name__)

# 获取设备列表
@device_bp.route('/devices', methods=['GET'])
@require_auth
def get_devices():
    elderly_id = request.args.get('elderly_id')
    device_type = request.args.get('type')
    
    query = Device.query
    if elderly_id:
        query = query.filter_by(elderly_id=elderly_id)
    if device_type:
        query = query.filter_by(device_type=device_type)
        
    devices = query.all()
    return jsonify({
        'devices': [{
            'device_id': device.device_id,
            'device_name': device.device_name,
            'device_type': device.device_type,
            'location': device.location,
            'ip_address': device.ip_address,
            'status': device.status,
            'last_active': device.last_active.strftime('%Y-%m-%d %H:%M:%S') if device.last_active else None
        } for device in devices]
    }), 200

# 添加设备
@device_bp.route('/devices', methods=['POST'])
@require_auth
def add_device():
    data = request.get_json()
    
    new_device = Device(
        elderly_id=data['elderly_id'],
        device_name=data['device_name'],
        device_type=data['device_type'],
        location=data.get('location'),
        ip_address=data.get('ip_address')
    )
    
    try:
        db.session.add(new_device)
        db.session.commit()
        return jsonify({
            'message': '设备添加成功',
            'device_id': new_device.device_id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'添加设备失败: {str(e)}'}), 500

# 更新设备信息
@device_bp.route('/devices/<int:device_id>', methods=['PUT'])
@require_auth
def update_device(device_id):
    device = Device.query.get(device_id)
    if not device:
        return jsonify({'message': '设备不存在'}), 404
        
    data = request.get_json()
    try:
        if 'device_name' in data:
            device.device_name = data['device_name']
        if 'location' in data:
            device.location = data['location']
        if 'ip_address' in data:
            device.ip_address = data['ip_address']
        if 'status' in data:
            device.status = data['status']
            if data['status'] == 'online':
                device.last_active = datetime.now()
                
        db.session.commit()
        return jsonify({'message': '设备信息更新成功'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'更新设备失败: {str(e)}'}), 500

# 删除设备
@device_bp.route('/devices/<int:device_id>', methods=['DELETE'])
@require_auth
def delete_device(device_id):
    device = Device.query.get(device_id)
    if not device:
        return jsonify({'message': '设备不存在'}), 404
        
    try:
        db.session.delete(device)
        db.session.commit()
        return jsonify({'message': '设备删除成功'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'删除设备失败: {str(e)}'}), 500

# 更新设备状态
@device_bp.route('/devices/<int:device_id>/status', methods=['PUT'])
@require_auth
def update_device_status(device_id):
    device = Device.query.get(device_id)
    if not device:
        return jsonify({'message': '设备不存在'}), 404
        
    data = request.get_json()
    try:
        device.status = data['status']
        device.last_active = datetime.now()
        db.session.commit()
        return jsonify({'message': '设备状态更新成功'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'更新状态失败: {str(e)}'}), 500 