# routes/message.py

from flask import Blueprint, request, jsonify, url_for
from models.models import db, FallDetectionRecord, Notification,  User
from datetime import datetime

message_bp = Blueprint('message', __name__)


@message_bp.route('/messages_user/<int:user_id>', methods=['GET'])
def get_user_messages(user_id):
    notifications = Notification.query.filter_by(user_id=user_id).all()
    if not notifications:   
        return jsonify({'error': 'No messages found for this user'}), 404

    # 如果找到了通知，返回详细数据
    data = [
        {
            "message_id": notification.notification_id,
            "type": notification.type,
            "timestamp": notification.sent_at.strftime('%Y-%m-%d %H:%M:%S'),
            "location": notification.device.location if notification.device else "未知位置",
            "device_name": notification.device.device_name if notification.device else "未知设备",
            "snapshots": [url_for('static', filename=f'snapshots/{notification.record_id}-{i}.jpg') for i in range(3)],
        }
        for notification in notifications
    ]

    return jsonify({"code": 200, "data": data})


@message_bp.route('/messages/<int:message_id>', methods=['GET'])
def get_message_detail(message_id):
    notification = Notification.query.get(message_id)
    if not notification:
        return jsonify({'error': 'Message not found'}), 404

    # 确保 notification.device 存在
    if not notification.device:
        return jsonify({'error': 'Device not found for this notification'}), 404

    detail_data = {
        "message_id": notification.notification_id,
        "type": notification.type,
        "timestamp": notification.sent_at.strftime('%Y-%m-%d %H:%M:%S'),
        "location": notification.device.location if notification.device else "未知位置",
        "device_name": notification.device.device_name if notification.device else "未知设备",
        "snapshots": [url_for('static', filename=f'snapshots/{notification.record_id}-{i}.jpg') for i in range(3)],
        "emergency_contacts": [
            {"name": contact.name, "phone": contact.phone}
            for contact in notification.user.family.users if contact.role == 'family'
        ]
    }

    return jsonify({"code": 200, "data": detail_data})




@message_bp.route('/fall_detection_records/<int:record_id>', methods=['GET'])
def get_fall_detection_record(record_id):
    record = FallDetectionRecord.query.get(record_id)
    if not record:
        return jsonify({'error': 'Fall detection record not found'}), 404

    detail_data = {
        "record_id": record.record_id,
        "user_id": record.user_id,
        "device_id": record.device_id,
        "detection_type": record.detection_type,
        "confidence": record.confidence,
        "video_frame_path": record.video_frame_path,  # 存储为 "fall/1"
        "status": record.status,
        "snapshots": [
            url_for('camera.get_fall_snapshot', fall_dir=record.video_frame_path, filename=f'{record.record_id}-{i}.jpg')
            for i in range(3)
        ]
    }
    return jsonify({"code": 200, "data": detail_data})
@message_bp.route('/fall-detection', methods=['POST'])
def store_fall_detection():
    data = request.json
    user_id = data.get('user_id')
    device_id = data.get('device_id')
    detection_type = data.get('detection_type')
    confidence = data.get('confidence')
    video_frame_path = data.get('video_frame_path')

    if not user_id or not device_id or not detection_type or not confidence or not video_frame_path:
        return jsonify({'error': 'Missing required fields'}), 400

    # 创建 FallDetectionRecord
    record = FallDetectionRecord(
        user_id=user_id,
        device_id=device_id,
        detection_type=detection_type,
        confidence=confidence,
        video_frame_path=video_frame_path,
        status='fall' if detection_type == 'Fall Detected' else 'normal'
    )
    db.session.add(record)
    db.session.commit()

    # 创建 Notification
    notification = Notification(
        user_id=user_id,
        record_id=record.record_id,
        message=f"{detection_type} event detected with confidence {confidence}",
        type='emergency' if detection_type == 'Fall Detected' else 'info',
        detection_type=detection_type
    )
    db.session.add(notification)
    db.session.commit()

    return jsonify({
        "code": 200,
        "message": "Detection record and notification created successfully"
    })
