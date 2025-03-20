from flask import Blueprint, jsonify, request
from extensions import db
from datetime import datetime
from sqlalchemy import text

monitor_bp = Blueprint('monitor', __name__)

@monitor_bp.route('/sitting/list', methods=['GET'])
def get_sitting_records():
    """获取久坐提醒记录列表"""
    try:
        # 获取分页参数
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('pageSize', 10, type=int)
        
        # 计算偏移量
        offset = (page - 1) * page_size
        
        # 查询总记录数
        count_sql = text("""
        SELECT COUNT(*) as total
        FROM sitting_records s
        LEFT JOIN users u ON s.elderly_id = u.user_id
        """)
        total = db.session.execute(count_sql).scalar()
        
        # 查询记录列表
        sql = text("""
        SELECT 
            s.record_id,
            s.start_time,
            s.end_time,
            s.duration,
            s.is_notified,
            u.name as elderly_name
        FROM sitting_records s
        LEFT JOIN users u ON s.elderly_id = u.user_id
        ORDER BY s.start_time DESC
        LIMIT :limit OFFSET :offset
        """)
        
        records = db.session.execute(sql, {
            "limit": page_size,
            "offset": offset
        }).fetchall()
        
        # 格式化数据
        result = []
        for record in records:
            start_time = record.start_time
            formatted_time = start_time.strftime("%Y年%m月%d日%H时%M分%S秒")
            result.append({
                "record_id": record.record_id,
                "message": f"{formatted_time}久坐提醒",
                "elderly_name": record.elderly_name,
                "duration": record.duration,
                "is_notified": record.is_notified
            })
        
        return jsonify({
            "code": 200,
            "message": "获取成功",
            "data": {
                "records": result,
                "total": total,
                "page": page,
                "pageSize": page_size,
                "totalPages": (total + page_size - 1) // page_size
            }
        })
    except Exception as e:
        return jsonify({
            "code": 500,
            "message": f"获取失败: {str(e)}"
        })

@monitor_bp.route('/sitting/detail/<int:record_id>', methods=['GET'])
def get_sitting_record_detail(record_id):
    """获取久坐提醒记录详情"""
    try:
        sql = text("""
        SELECT 
            s.*,
            u.name as elderly_name,
            d.device_name
        FROM sitting_records s
        LEFT JOIN users u ON s.elderly_id = u.user_id
        LEFT JOIN devices d ON s.device_id = d.device_id
        WHERE s.record_id = :record_id
        """)
        
        record = db.session.execute(sql, {"record_id": record_id}).first()
        
        if not record:
            return jsonify({
                "code": 404,
                "message": "记录不存在"
            })
        
        # 格式化数据
        start_time = record.start_time
        end_time = record.end_time
        formatted_start = start_time.strftime("%Y年%m月%d日%H时%M分%S秒")
        formatted_end = end_time.strftime("%Y年%m月%d日%H时%M分%S秒") if end_time else "尚未结束"
        
        result = {
            "record_id": record.record_id,
            "elderly_name": record.elderly_name,
            "device_name": record.device_name,
            "start_time": formatted_start,
            "end_time": formatted_end,
            "duration": record.duration,
            "is_notified": record.is_notified
        }
        
        return jsonify({
            "code": 200,
            "message": "获取成功",
            "data": result
        })
    except Exception as e:
        return jsonify({
            "code": 500,
            "message": f"获取失败: {str(e)}"
        })

@monitor_bp.route('/fall/list', methods=['GET'])
def get_fall_records():
    """获取跌倒检测记录列表"""
    try:
        # 获取分页参数
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('pageSize', 10, type=int)
        
        # 计算偏移量
        offset = (page - 1) * page_size
        
        # 查询总记录数
        count_sql = text("""
        SELECT COUNT(*) as total
        FROM fall_detection_records f
        LEFT JOIN users u ON f.elderly_id = u.user_id
        """)
        total = db.session.execute(count_sql).scalar()
        
        # 查询记录列表
        sql = text("""
        SELECT 
            f.record_id,
            f.detection_time,
            f.detection_type,
            f.confidence,
            f.video_frame_path,
            f.is_notified,
            f.status,
            f.processed,
            f.processed_at,
            u.name as elderly_name
        FROM fall_detection_records f
        LEFT JOIN users u ON f.elderly_id = u.user_id
        ORDER BY f.detection_time DESC
        LIMIT :limit OFFSET :offset
        """)
        
        records = db.session.execute(sql, {
            "limit": page_size,
            "offset": offset
        }).fetchall()
        
        # 格式化数据
        result = []
        for record in records:
            detection_time = record.detection_time
            formatted_time = detection_time.strftime("%Y年%m月%d日%H时%M分%S秒")
            result.append({
                "record_id": record.record_id,
                "message": f"{formatted_time}跌倒检测",
                "elderly_name": record.elderly_name,
                "detection_type": record.detection_type,
                "confidence": record.confidence,
                "video_frame_path": record.video_frame_path,
                "is_notified": record.is_notified,
                "status": record.status,
                "processed": record.processed,
                "processed_at": record.processed_at.strftime("%Y年%m月%d日%H时%M分%S秒") if record.processed_at else None
            })
        
        return jsonify({
            "code": 200,
            "message": "获取成功",
            "data": {
                "records": result,
                "total": total,
                "page": page,
                "pageSize": page_size,
                "totalPages": (total + page_size - 1) // page_size
            }
        })
    except Exception as e:
        return jsonify({
            "code": 500,
            "message": f"获取失败: {str(e)}"
        })

@monitor_bp.route('/fall/detail/<int:record_id>', methods=['GET'])
def get_fall_record_detail(record_id):
    """获取跌倒检测记录详情"""
    try:
        sql = text("""
        SELECT 
            f.*,
            u.name as elderly_name,
            d.device_name
        FROM fall_detection_records f
        LEFT JOIN users u ON f.elderly_id = u.user_id
        LEFT JOIN devices d ON f.device_id = d.device_id
        WHERE f.record_id = :record_id
        """)
        
        record = db.session.execute(sql, {"record_id": record_id}).first()
        
        if not record:
            return jsonify({
                "code": 404,
                "message": "记录不存在"
            })
        
        # 格式化数据
        detection_time = record.detection_time
        formatted_time = detection_time.strftime("%Y年%m月%d日%H时%M分%S秒")
        
        result = {
            "record_id": record.record_id,
            "elderly_name": record.elderly_name,
            "device_name": record.device_name,
            "detection_time": formatted_time,
            "detection_type": record.detection_type,
            "confidence": record.confidence,
            "video_frame_path": record.video_frame_path,
            "is_notified": record.is_notified,
            "status": record.status,
            "processed": record.processed,
            "processed_at": record.processed_at.strftime("%Y年%m月%d日%H时%M分%S秒") if record.processed_at else None
        }
        
        return jsonify({
            "code": 200,
            "message": "获取成功",
            "data": result
        })
    except Exception as e:
        return jsonify({
            "code": 500,
            "message": f"获取失败: {str(e)}"
        }) 