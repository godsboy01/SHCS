from flask import Blueprint, request, jsonify
from models.models import Device, db
from utils.security import require_auth
from datetime import datetime
import logging

device_bp = Blueprint('device', __name__)
logger = logging.getLogger(__name__)

# 获取设备列表
@device_bp.route('/devices', methods=['GET'])
@require_auth
def get_devices():
    try:
        elderly_id = request.args.get('elderly_id')
        device_type = request.args.get('type')
        
        # 构建基础查询
        query = Device.query
        
        # 添加过滤条件
        if elderly_id:
            query = query.filter(Device.elderly_id == elderly_id)
        if device_type:
            query = query.filter(Device.device_type == device_type)
            
        # 执行查询
        devices = query.all()
        
        # 构建响应数据
        device_list = []
        for device in devices:
            device_data = {
                'device_id': device.device_id,
                'device_name': device.device_name,
                'device_type': device.device_type,
                'location': device.location,
                'ip_address': device.ip_address,
                'status': device.status,
                'last_active': device.last_active.strftime('%Y-%m-%d %H:%M:%S') if device.last_active else None
            }
            device_list.append(device_data)
            
        return jsonify({
            'code': 200,
            'message': '获取设备列表成功',
            'data': {
                'devices': device_list
            }
        }), 200
        
    except Exception as e:
        logger.error(f"获取设备列表失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'获取设备列表失败: {str(e)}'
        }), 500

# 获取单个设备详情
@device_bp.route('/devices/<int:device_id>', methods=['GET'])
@require_auth
def get_device_detail(device_id):
    try:
        device = Device.query.get(device_id)
        if not device:
            return jsonify({
                'code': 404,
                'message': '设备不存在'
            }), 404
            
        device_data = {
            'device_id': device.device_id,
            'device_name': device.device_name,
            'device_type': device.device_type,
            'location': device.location,
            'ip_address': device.ip_address,
            'status': device.status,
            'last_active': device.last_active.strftime('%Y-%m-%d %H:%M:%S') if device.last_active else None,
            'description': device.description
        }
        
        return jsonify({
            'code': 200,
            'message': '获取设备详情成功',
            'data': device_data
        }), 200
        
    except Exception as e:
        logger.error(f"获取设备详情失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'获取设备详情失败: {str(e)}'
        }), 500

# 添加设备
@device_bp.route('/devices', methods=['POST'])
@require_auth
def add_device():
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'code': 400,
                'message': '请求数据不能为空'
            }), 400
            
        # 验证必填字段
        required_fields = ['elderly_id', 'device_name', 'device_type']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'code': 400,
                    'message': f'缺少必填字段: {field}'
                }), 400
                
        # 创建新设备
        new_device = Device(
            elderly_id=data['elderly_id'],
            device_name=data['device_name'],
            device_type=data['device_type'],
            location=data.get('location'),
            ip_address=data.get('ip_address'),
            status='offline'  # 默认离线状态
        )
        
        db.session.add(new_device)
        db.session.commit()
        
        return jsonify({
            'code': 201,
            'message': '设备添加成功',
            'data': {
                'device_id': new_device.device_id
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"添加设备失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'添加设备失败: {str(e)}'
        }), 500

# 更新设备信息
@device_bp.route('/devices/<int:device_id>', methods=['PUT'])
@require_auth
def update_device(device_id):
    try:
        device = Device.query.get(device_id)
        if not device:
            return jsonify({
                'code': 404,
                'message': '设备不存在'
            }), 404
            
        data = request.get_json()
        if not data:
            return jsonify({
                'code': 400,
                'message': '请求数据不能为空'
            }), 400
            
        # 更新设备信息
        update_fields = {
            'device_name': str,
            'location': str,
            'ip_address': str,
            'status': str,
            'description': str
        }
        
        for field, field_type in update_fields.items():
            if field in data:
                setattr(device, field, field_type(data[field]))
                
        # 如果状态更新为在线，更新最后活跃时间
        if data.get('status') == 'online':
            device.last_active = datetime.now()
            
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '设备信息更新成功'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"更新设备信息失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'更新设备信息失败: {str(e)}'
        }), 500

# 删除设备
@device_bp.route('/devices/<int:device_id>', methods=['DELETE'])
@require_auth
def delete_device(device_id):
    try:
        device = Device.query.get(device_id)
        if not device:
            return jsonify({
                'code': 404,
                'message': '设备不存在'
            }), 404
            
        db.session.delete(device)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '设备删除成功'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"删除设备失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'删除设备失败: {str(e)}'
        }), 500

# 更新设备状态
@device_bp.route('/devices/<int:device_id>/status', methods=['PUT'])
@require_auth
def update_device_status(device_id):
    try:
        device = Device.query.get(device_id)
        if not device:
            return jsonify({
                'code': 404,
                'message': '设备不存在'
            }), 404
            
        data = request.get_json()
        if not data or 'status' not in data:
            return jsonify({
                'code': 400,
                'message': '缺少状态参数'
            }), 400
            
        # 验证状态值
        valid_statuses = ['online', 'offline', 'error']
        if data['status'] not in valid_statuses:
            return jsonify({
                'code': 400,
                'message': f'无效的状态值，有效值为: {", ".join(valid_statuses)}'
            }), 400
            
        device.status = data['status']
        if data['status'] == 'online':
            device.last_active = datetime.now()
            
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '设备状态更新成功'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"更新设备状态失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'更新设备状态失败: {str(e)}'
        }), 500 