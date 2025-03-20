from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from models.models import HealthRecord, HealthThreshold
from extensions import db
from sqlalchemy import and_, func

health_bp = Blueprint('health', __name__)

@health_bp.route('/record', methods=['POST'])
def add_health_record():
    """添加健康记录"""
    data = request.get_json()
    
    # 创建健康记录
    record = HealthRecord(
        user_id=data['user_id'],
        height=data.get('height'),
        weight=data.get('weight'),
        systolic_pressure=data.get('systolic_pressure'),
        diastolic_pressure=data.get('diastolic_pressure'),
        heart_rate=data.get('heart_rate'),
        temperature=data.get('temperature'),
        recorded_at=datetime.now()
    )
    
    # 如果提供了身高和体重，计算BMI
    if data.get('height') and data.get('weight'):
        height_m = float(data['height']) / 100  # 转换为米
        record.bmi = round(float(data['weight']) / (height_m * height_m), 2)
    
    try:
        db.session.add(record)
        db.session.commit()
        return jsonify({'code': 200, 'message': '添加成功', 'data': record.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'添加失败: {str(e)}'})

@health_bp.route('/record/<int:record_id>', methods=['PUT'])
def update_health_record(record_id):
    """更新健康记录"""
    data = request.get_json()
    record = HealthRecord.query.get_or_404(record_id)
    
    # 更新记录
    if 'height' in data:
        record.height = data['height']
    if 'weight' in data:
        record.weight = data['weight']
    if 'systolic_pressure' in data:
        record.systolic_pressure = data['systolic_pressure']
    if 'diastolic_pressure' in data:
        record.diastolic_pressure = data['diastolic_pressure']
    if 'heart_rate' in data:
        record.heart_rate = data['heart_rate']
    if 'temperature' in data:
        record.temperature = data['temperature']
    
    # 重新计算BMI
    if ('height' in data or 'weight' in data) and record.height and record.weight:
        height_m = float(record.height) / 100  # 转换为米
        record.bmi = round(float(record.weight) / (height_m * height_m), 2)
    
    try:
        db.session.commit()
        return jsonify({'code': 200, 'message': '更新成功', 'data': record.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'更新失败: {str(e)}'})

@health_bp.route('/record/<int:record_id>', methods=['DELETE'])
def delete_health_record(record_id):
    """删除健康记录"""
    record = HealthRecord.query.get_or_404(record_id)
    try:
        db.session.delete(record)
        db.session.commit()
        return jsonify({'code': 200, 'message': '删除成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'删除失败: {str(e)}'})

@health_bp.route('/records/<int:user_id>', methods=['GET'])
def get_health_records(user_id):
    """获取健康记录"""
    # 获取查询参数
    days = request.args.get('days', type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = HealthRecord.query.filter_by(user_id=user_id)
    
    # 根据时间范围筛选
    if days:
        start_time = datetime.now() - timedelta(days=days)
        query = query.filter(HealthRecord.recorded_at >= start_time)
    elif start_date and end_date:
        start_time = datetime.strptime(start_date, '%Y-%m-%d')
        end_time = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
        query = query.filter(and_(
            HealthRecord.recorded_at >= start_time,
            HealthRecord.recorded_at < end_time
        ))
    
    # 按时间排序
    records = query.order_by(HealthRecord.recorded_at.desc()).all()
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': [record.to_dict() for record in records]
    })

@health_bp.route('/threshold', methods=['POST'])
def set_health_threshold():
    """设置健康阈值"""
    data = request.get_json()
    threshold = HealthThreshold(
        user_id=data['user_id'],
        metric_type=data['metric_type'],
        min_value=data.get('min_value'),
        max_value=data.get('max_value'),
        warning_level=data.get('warning_level', 'normal')
    )
    
    try:
        db.session.add(threshold)
        db.session.commit()
        return jsonify({'code': 200, 'message': '设置成功', 'data': threshold.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'设置失败: {str(e)}'})

@health_bp.route('/charts/<int:user_id>', methods=['GET'])
def get_chart_data(user_id):
    """获取用于图表展示的健康数据"""
    # 获取查询参数
    days = request.args.get('days', default=7, type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = HealthRecord.query.filter_by(user_id=user_id)
    
    # 根据时间范围筛选
    if days:
        start_time = datetime.now() - timedelta(days=days)
        query = query.filter(HealthRecord.recorded_at >= start_time)
    elif start_date and end_date:
        start_time = datetime.strptime(start_date, '%Y-%m-%d')
        end_time = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
        query = query.filter(and_(
            HealthRecord.recorded_at >= start_time,
            HealthRecord.recorded_at < end_time
        ))
    
    # 按时间排序
    records = query.order_by(HealthRecord.recorded_at.asc()).all()
    
    # 准备图表数据
    dates = []
    bmi_data = []
    blood_pressure_data = []
    heart_rate_data = []
    temperature_data = []
    weight_data = []
    
    for record in records:
        date_str = record.recorded_at.strftime('%Y-%m-%d %H:%M')
        dates.append(date_str)
        
        # BMI数据
        bmi_data.append(float(record.bmi) if record.bmi else None)
        
        # 血压数据（收缩压和舒张压）
        if record.systolic_pressure and record.diastolic_pressure:
            blood_pressure_data.append([
                record.systolic_pressure,
                record.diastolic_pressure
            ])
        else:
            blood_pressure_data.append([None, None])
        
        # 心率数据
        heart_rate_data.append(record.heart_rate)
        
        # 体温数据
        temperature_data.append(float(record.temperature) if record.temperature else None)
        
        # 体重数据
        weight_data.append(float(record.weight) if record.weight else None)
    
    # 获取健康阈值
    thresholds = HealthThreshold.query.filter_by(user_id=user_id).all()
    threshold_data = {}
    for threshold in thresholds:
        threshold_data[threshold.metric_type] = {
            'min': float(threshold.min_value) if threshold.min_value else None,
            'max': float(threshold.max_value) if threshold.max_value else None,
            'level': threshold.warning_level
        }
    
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': {
            'dates': dates,
            'bmi': {
                'data': bmi_data,
                'threshold': threshold_data.get('bmi', {})
            },
            'blood_pressure': {
                'data': blood_pressure_data,
                'threshold': threshold_data.get('blood_pressure', {})
            },
            'heart_rate': {
                'data': heart_rate_data,
                'threshold': threshold_data.get('heart_rate', {})
            },
            'temperature': {
                'data': temperature_data,
                'threshold': threshold_data.get('temperature', {})
            },
            'weight': {
                'data': weight_data
            }
        }
    })

@health_bp.route('/charts/statistics/<int:user_id>', methods=['GET'])
def get_statistics(user_id):
    """获取健康数据统计信息"""
    days = request.args.get('days', default=30, type=int)
    start_time = datetime.now() - timedelta(days=days)
    
    # 查询最新记录
    latest_record = HealthRecord.query.filter_by(user_id=user_id).order_by(HealthRecord.recorded_at.desc()).first()
    
    # 计算平均值
    avg_stats = db.session.query(
        func.avg(HealthRecord.bmi).label('avg_bmi'),
        func.avg(HealthRecord.weight).label('avg_weight'),
        func.avg(HealthRecord.systolic_pressure).label('avg_systolic'),
        func.avg(HealthRecord.diastolic_pressure).label('avg_diastolic'),
        func.avg(HealthRecord.heart_rate).label('avg_heart_rate'),
        func.avg(HealthRecord.temperature).label('avg_temperature')
    ).filter(
        HealthRecord.user_id == user_id,
        HealthRecord.recorded_at >= start_time
    ).first()
    
    # 计算最大最小值
    min_max_stats = db.session.query(
        func.min(HealthRecord.bmi).label('min_bmi'),
        func.max(HealthRecord.bmi).label('max_bmi'),
        func.min(HealthRecord.weight).label('min_weight'),
        func.max(HealthRecord.weight).label('max_weight'),
        func.min(HealthRecord.systolic_pressure).label('min_systolic'),
        func.max(HealthRecord.systolic_pressure).label('max_systolic'),
        func.min(HealthRecord.diastolic_pressure).label('min_diastolic'),
        func.max(HealthRecord.diastolic_pressure).label('max_diastolic'),
        func.min(HealthRecord.heart_rate).label('min_heart_rate'),
        func.max(HealthRecord.heart_rate).label('max_heart_rate'),
        func.min(HealthRecord.temperature).label('min_temperature'),
        func.max(HealthRecord.temperature).label('max_temperature')
    ).filter(
        HealthRecord.user_id == user_id,
        HealthRecord.recorded_at >= start_time
    ).first()
    
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': {
            'latest': latest_record.to_dict() if latest_record else None,
            'averages': {
                'bmi': float(avg_stats.avg_bmi) if avg_stats.avg_bmi else None,
                'weight': float(avg_stats.avg_weight) if avg_stats.avg_weight else None,
                'systolic_pressure': float(avg_stats.avg_systolic) if avg_stats.avg_systolic else None,
                'diastolic_pressure': float(avg_stats.avg_diastolic) if avg_stats.avg_diastolic else None,
                'heart_rate': float(avg_stats.avg_heart_rate) if avg_stats.avg_heart_rate else None,
                'temperature': float(avg_stats.avg_temperature) if avg_stats.avg_temperature else None
            },
            'ranges': {
                'bmi': {
                    'min': float(min_max_stats.min_bmi) if min_max_stats.min_bmi else None,
                    'max': float(min_max_stats.max_bmi) if min_max_stats.max_bmi else None
                },
                'weight': {
                    'min': float(min_max_stats.min_weight) if min_max_stats.min_weight else None,
                    'max': float(min_max_stats.max_weight) if min_max_stats.max_weight else None
                },
                'blood_pressure': {
                    'systolic': {
                        'min': min_max_stats.min_systolic,
                        'max': min_max_stats.max_systolic
                    },
                    'diastolic': {
                        'min': min_max_stats.min_diastolic,
                        'max': min_max_stats.max_diastolic
                    }
                },
                'heart_rate': {
                    'min': min_max_stats.min_heart_rate,
                    'max': min_max_stats.max_heart_rate
                },
                'temperature': {
                    'min': float(min_max_stats.min_temperature) if min_max_stats.min_temperature else None,
                    'max': float(min_max_stats.max_temperature) if min_max_stats.max_temperature else None
                }
            }
        }
    })
