# 数据库模型 (models/models.py)
from app import db
from sqlalchemy import Enum
from datetime import datetime
class Family(db.Model):
    __tablename__ = 'families'
    family_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    family_name = db.Column(db.String(100), nullable=False)
    family_address = db.Column(db.String(256))  # 家庭地址
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    users = db.relationship('User', backref='family', lazy=True)  # 关系定义
class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum('elderly', 'family', 'admin'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(100))
    address = db.Column(db.String(255))
    avatar = db.Column(db.String(255))  # 用户头像 URL 或文件路径
    family_id = db.Column(db.Integer, db.ForeignKey('families.family_id', ondelete='CASCADE'))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __repr__(self):
        return f'<User {self.username}>'

class Device(db.Model):
    __tablename__ = 'devices'
    device_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    family_id = db.Column(db.Integer, db.ForeignKey('families.family_id', ondelete='CASCADE'))
    device_name = db.Column(db.String(100), nullable=False)
    device_type = db.Column(db.Enum('camera', 'sensor'), nullable=False)
    ip_address = db.Column(db.String(15), nullable=False)
    status = db.Column(db.Enum('active', 'inactive'), default='active')
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    location = db.Column(db.String(255), nullable=False, default='未知位置')
    user_id = db.Column(db.Integer)


class FallDetectionRecord(db.Model):
    __tablename__ = 'fall_detection_records'
    record_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'))
    device_id = db.Column(db.Integer, db.ForeignKey('devices.device_id', ondelete='CASCADE'))
    detection_time = db.Column(db.DateTime, default=db.func.current_timestamp())
    confidence = db.Column(db.Float)
    status = db.Column(db.Enum('fall', 'normal'), nullable=False)
    detection_type = db.Column(db.Enum('Fall Detected', 'Walking', 'Sitting'), nullable=False)
    video_frame_path = db.Column(db.String(255))
    is_notified = db.Column(db.Boolean, default=False)

    # 关联 User 和 Device 对象，方便查询
    user = db.relationship('User', backref='fall_detection_records', lazy=True)
    device = db.relationship('Device', backref='fall_detection_records', lazy=True)

    # 关联 Notification 对象，方便获取通知信息
    notifications = db.relationship('Notification', backref='fall_detection_record', lazy=True)

class Notification(db.Model):
    __tablename__ = 'notifications'
    notification_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'))
    record_id = db.Column(db.Integer, db.ForeignKey('fall_detection_records.record_id', ondelete='CASCADE'))
    message = db.Column(db.String(255), nullable=False)
    sent_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    status = db.Column(db.Enum('sent', 'failed'), default='sent')
    type = db.Column(db.Enum('emergency', 'warning', 'info'), nullable=False)
    detection_type = db.Column(db.Enum('Fall Detected', 'Walking', 'Sitting'), nullable=False)
    is_read = db.Column(db.Boolean, default=False)

    # 设备关联
    device_id = db.Column(db.Integer, db.ForeignKey('devices.device_id', ondelete='CASCADE'))
    device = db.relationship('Device', backref='notifications', lazy=True)

    # **新增用户关联**
    user = db.relationship('User', backref='notifications', lazy=True)


class HealthRecord(db.Model):
    __tablename__ = 'health_records'
    record_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 新增关系定义（与 HeightWeight 表关联）
    height_weight = db.relationship(
        "HeightWeight",
        backref="health_record",
        uselist=False  # 每个 HealthRecord 对应一条 HeightWeight 记录
    )
    # 新增关系定义
    blood_pressure = db.relationship(
        "BloodPressure",
        backref="health_record",
        uselist=False
    )


class BloodPressure(db.Model):
    __tablename__ = 'blood_pressure'
    bp_id = db.Column(db.Integer, primary_key=True)
    record_id = db.Column(db.Integer, db.ForeignKey('health_records.record_id'), nullable=False)
    systolic = db.Column(db.Numeric(5, 1))  # 收缩压
    diastolic = db.Column(db.Numeric(5, 1)) # 舒张压
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)

class HeightWeight(db.Model):
    __tablename__ = 'height_weight'
    hw_id = db.Column(db.Integer, primary_key=True)
    record_id = db.Column(db.Integer, db.ForeignKey('health_records.record_id'), nullable=False)
    height = db.Column(db.Numeric(5, 2))
    weight = db.Column(db.Numeric(5, 2))
    bmi = db.Column(db.Numeric(4, 2))

class HealthThreshold(db.Model):
    __tablename__ = 'health_thresholds'
    threshold_id = db.Column(db.Integer, primary_key=True)
    metric_type = db.Column(Enum('bmi', 'blood_pressure_systolic', 'heart_rate'), nullable=False)
    min_value = db.Column(db.Numeric(10, 2))
    max_value = db.Column(db.Numeric(10, 2))
    alert_type = db.Column(Enum('warning', 'emergency'), nullable=False)

class HealthAlert(db.Model):
    __tablename__ = 'health_alerts'
    alert_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    record_id = db.Column(db.Integer, db.ForeignKey('health_records.record_id'), nullable=False)
    threshold_id = db.Column(db.Integer, db.ForeignKey('health_thresholds.threshold_id'), nullable=False)
    actual_value = db.Column(db.Numeric(10, 2))
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(Enum('sent', 'failed'), default='sent')