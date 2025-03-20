# 数据库模型 (models/models.py)
from extensions import db
from sqlalchemy import Enum
from datetime import datetime

class Family(db.Model):
    __tablename__ = 'families'
    family_id = db.Column(db.Integer, primary_key=True)
    family_name = db.Column(db.String(100), nullable=False)
    family_address = db.Column(db.String(256))  # 家庭地址
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    users = db.relationship('User', backref='family', lazy=True)  # 关系定义

class User(db.Model):
    __tablename__ = 'users'
    
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), unique=True)
    role = db.Column(Enum('user', 'guardian', 'cared', 'elderly', name='user_roles'), default='elderly')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    family_id = db.Column(db.Integer, db.ForeignKey('families.family_id'))
    avatar = db.Column(db.String(200))
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100))

    # 关系定义
    devices = db.relationship('Device', backref='owner', lazy=True, foreign_keys='Device.user_id')
    managed_devices = db.relationship('Device', backref='elderly', lazy=True, foreign_keys='Device.elderly_id')
    
    # 监护关系
    as_guardian = db.relationship('CareRelationship', backref='guardian', lazy=True, foreign_keys='CareRelationship.guardian_id')
    as_elderly = db.relationship('CareRelationship', backref='elderly_person', lazy=True, foreign_keys='CareRelationship.elderly_id')

    def __repr__(self):
        return f'<User {self.username}>'

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'username': self.username,
            'phone': self.phone,
            'role': self.role,
            'family_id': self.family_id,
            'avatar': self.avatar
        }

class Device(db.Model):
    __tablename__ = 'devices'
    device_id = db.Column(db.Integer, primary_key=True)
    elderly_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    device_name = db.Column(db.String(100))
    device_type = db.Column(Enum('camera', 'weight_scale', 'blood_pressure', 'other'), nullable=False)
    ip_address = db.Column(db.String(15), nullable=False)
    location = db.Column(db.String(255), default='未设置')
    status = db.Column(Enum('online', 'offline'), default='offline')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_active = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    description = db.Column(db.Text)

class FallDetectionRecord(db.Model):
    __tablename__ = 'fall_detection_records'
    record_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    elderly_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    device_id = db.Column(db.Integer, db.ForeignKey('devices.device_id'), nullable=False)
    detection_time = db.Column(db.DateTime, default=db.func.current_timestamp())
    detection_type = db.Column(db.Enum('Fall', 'Normal', 'Sitting'), nullable=False)
    confidence = db.Column(db.Float)
    video_frame_path = db.Column(db.String(255))
    is_notified = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(20))
    processed = db.Column(db.Boolean, default=False)
    processed_at = db.Column(db.DateTime)

    # 关系定义
    device = db.relationship('Device', backref='fall_records', lazy=True)
    elderly = db.relationship('User', foreign_keys=[elderly_id], backref='fall_records')

class SittingRecord(db.Model):
    __tablename__ = 'sitting_records'
    record_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    elderly_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    device_id = db.Column(db.Integer, db.ForeignKey('devices.device_id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime)
    duration = db.Column(db.Integer)  # 持续时间（分钟）
    is_notified = db.Column(db.Boolean, default=False)

    device = db.relationship('Device', backref='sitting_records', lazy=True)
    elderly = db.relationship('User', foreign_keys=[elderly_id], backref='sitting_records')

class HealthRecord(db.Model):
    __tablename__ = 'health_records'
    record_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    height = db.Column(db.Numeric(5, 2))
    weight = db.Column(db.Numeric(5, 2))
    bmi = db.Column(db.Numeric(4, 2))
    systolic_pressure = db.Column(db.Integer)
    diastolic_pressure = db.Column(db.Integer)
    heart_rate = db.Column(db.Integer)
    temperature = db.Column(db.Numeric(3, 1))
    recorded_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    user = db.relationship('User', foreign_keys=[user_id], backref='health_records')

    def to_dict(self):
        return {
            'record_id': self.record_id,
            'user_id': self.user_id,
            'height': float(self.height) if self.height else None,
            'weight': float(self.weight) if self.weight else None,
            'bmi': float(self.bmi) if self.bmi else None,
            'systolic_pressure': self.systolic_pressure,
            'diastolic_pressure': self.diastolic_pressure,
            'heart_rate': self.heart_rate,
            'temperature': float(self.temperature) if self.temperature else None,
            'recorded_at': self.recorded_at.strftime('%Y-%m-%d %H:%M:%S') if self.recorded_at else None
        }

class HealthThreshold(db.Model):
    __tablename__ = 'health_thresholds'
    threshold_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    metric_type = db.Column(db.Enum('bmi', 'blood_pressure', 'heart_rate', 'temperature', 'sitting_duration'), nullable=False)
    min_value = db.Column(db.Numeric(5, 2))
    max_value = db.Column(db.Numeric(5, 2))
    warning_level = db.Column(db.Enum('normal', 'warning', 'danger'), nullable=False, default='normal')

    user = db.relationship('User', foreign_keys=[user_id], backref='health_thresholds')

    def to_dict(self):
        return {
            'threshold_id': self.threshold_id,
            'user_id': self.user_id,
            'metric_type': self.metric_type,
            'min_value': float(self.min_value) if self.min_value else None,
            'max_value': float(self.max_value) if self.max_value else None,
            'warning_level': self.warning_level
        }

class Notification(db.Model):
    __tablename__ = 'notifications'
    notification_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    elderly_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    guardian_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.Enum('fall', 'sitting', 'health'), nullable=False)
    level = db.Column(db.Enum('info', 'warning', 'danger'), nullable=False)
    source_type = db.Column(db.Enum('fall_detection', 'sitting_record', 'health_record'), nullable=False)
    source_id = db.Column(db.Integer, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    read_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    thumbnail = db.Column(db.String(255))

    details = db.relationship('NotificationDetail', backref='notification', lazy=True, cascade='all, delete-orphan')
    read_status = db.relationship('NotificationReadStatus', backref='notification', lazy=True, cascade='all, delete-orphan')

class NotificationDetail(db.Model):
    __tablename__ = 'notification_details'
    detail_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    notification_id = db.Column(db.Integer, db.ForeignKey('notifications.notification_id', ondelete='CASCADE'), nullable=False)
    detail_type = db.Column(db.String(50), nullable=False)
    detail_key = db.Column(db.String(50), nullable=False)
    detail_value = db.Column(db.Text)

class NotificationReadStatus(db.Model):
    __tablename__ = 'notification_read_status'
    status_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    notification_id = db.Column(db.Integer, db.ForeignKey('notifications.notification_id', ondelete='CASCADE'), nullable=False)
    guardian_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    read_at = db.Column(db.DateTime)

class CareRelationship(db.Model):
    __tablename__ = 'care_relationships'
    relationship_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    guardian_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    elderly_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())