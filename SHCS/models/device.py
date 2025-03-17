from extensions import db
from datetime import datetime

class Device(db.Model):
    __tablename__ = 'devices'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    device_name = db.Column(db.String(100), nullable=False)
    device_type = db.Column(db.String(50), nullable=False)  # camera, weight_scale, blood_pressure
    device_id = db.Column(db.String(100), unique=True, nullable=False)
    status = db.Column(db.String(20), default='offline')  # online, offline
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_active = db.Column(db.DateTime)
    
    # 可选：添加设备特定字段
    location = db.Column(db.String(200))
    description = db.Column(db.Text)
    
    def to_dict(self):
        return {
            'id': self.id,
            'device_name': self.device_name,
            'device_type': self.device_type,
            'device_id': self.device_id,
            'status': self.status,
            'user_id': self.user_id,
            'location': self.location,
            'description': self.description,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'last_active': self.last_active.strftime('%Y-%m-%d %H:%M:%S') if self.last_active else None
        } 