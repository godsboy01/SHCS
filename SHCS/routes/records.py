from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
from models.models import FallDetectionRecord, SittingRecord
from app import create_app
from datetime import datetime, timedelta
from utils.logger import db_logger

records_bp = Blueprint('records', __name__)

@records_bp.route('/api/records/fall', methods=['GET'])
@cross_origin()
def get_fall_records():
    """
    获取跌倒检测记录
    支持分页和时间范围筛选
    """
    try:
        app = create_app()
        with app.app_context():
            # 获取查询参数
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            start_date = request.args.get('start_date')
            end_date = request.args.get('end_date')
            elderly_id = request.args.get('elderly_id', type=int)

            # 构建查询
            query = FallDetectionRecord.query

            # 添加筛选条件
            if elderly_id:
                query = query.filter_by(elderly_id=elderly_id)
            
            if start_date:
                query = query.filter(FallDetectionRecord.detection_time >= datetime.strptime(start_date, '%Y-%m-%d'))
            
            if end_date:
                query = query.filter(FallDetectionRecord.detection_time <= datetime.strptime(end_date, '%Y-%m-%d'))

            # 按时间倒序排序
            query = query.order_by(FallDetectionRecord.detection_time.desc())

            # 分页
            pagination = query.paginate(page=page, per_page=per_page, error_out=False)
            records = pagination.items

            # 格式化返回数据
            records_data = [{
                'record_id': record.record_id,
                'elderly_id': record.elderly_id,
                'device_id': record.device_id,
                'detection_time': record.detection_time.strftime('%Y-%m-%d %H:%M:%S'),
                'detection_type': record.detection_type,
                'confidence': record.confidence,
                'video_frame_path': record.video_frame_path,
                'is_notified': record.is_notified,
                'status': record.status,
                'processed': record.processed,
                'processed_at': record.processed_at.strftime('%Y-%m-%d %H:%M:%S') if record.processed_at else None
            } for record in records]

            return jsonify({
                'code': 200,
                'message': '获取成功',
                'data': {
                    'records': records_data,
                    'total': pagination.total,
                    'pages': pagination.pages,
                    'current_page': page
                }
            })

    except Exception as e:
        db_logger.error(f"获取跌倒记录失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'获取跌倒记录失败: {str(e)}'
        }), 500

@records_bp.route('/api/records/sitting', methods=['GET'])
@cross_origin()
def get_sitting_records():
    """
    获取久坐记录
    支持分页和时间范围筛选
    """
    try:
        app = create_app()
        with app.app_context():
            # 获取查询参数
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            start_date = request.args.get('start_date')
            end_date = request.args.get('end_date')
            elderly_id = request.args.get('elderly_id', type=int)

            # 构建查询
            query = SittingRecord.query

            # 添加筛选条件
            if elderly_id:
                query = query.filter_by(elderly_id=elderly_id)
            
            if start_date:
                query = query.filter(SittingRecord.start_time >= datetime.strptime(start_date, '%Y-%m-%d'))
            
            if end_date:
                query = query.filter(SittingRecord.start_time <= datetime.strptime(end_date, '%Y-%m-%d'))

            # 按时间倒序排序
            query = query.order_by(SittingRecord.start_time.desc())

            # 分页
            pagination = query.paginate(page=page, per_page=per_page, error_out=False)
            records = pagination.items

            # 格式化返回数据
            records_data = [{
                'record_id': record.record_id,
                'elderly_id': record.elderly_id,
                'device_id': record.device_id,
                'start_time': record.start_time.strftime('%Y-%m-%d %H:%M:%S'),
                'end_time': record.end_time.strftime('%Y-%m-%d %H:%M:%S') if record.end_time else None,
                'duration': record.duration,
                'is_notified': record.is_notified,
                'alert_threshold': record.alert_threshold,
                'alert_sent': record.alert_sent,
                'alert_sent_time': record.alert_sent_time.strftime('%Y-%m-%d %H:%M:%S') if record.alert_sent_time else None,
                'status': record.status,
                'break_count': record.break_count,
                'last_break_time': record.last_break_time.strftime('%Y-%m-%d %H:%M:%S') if record.last_break_time else None
            } for record in records]

            return jsonify({
                'code': 200,
                'message': '获取成功',
                'data': {
                    'records': records_data,
                    'total': pagination.total,
                    'pages': pagination.pages,
                    'current_page': page
                }
            })

    except Exception as e:
        db_logger.error(f"获取久坐记录失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'获取久坐记录失败: {str(e)}'
        }), 500 