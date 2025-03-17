from extensions import db
from datetime import datetime
from models.family import Family  # 添加这行导入

class User(db.Model):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}  # 添加这行来允许表的重复定义
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), unique=True)
    avatar = db.Column(db.String(200))  # 头像路径
    family_id = db.Column(db.Integer, db.ForeignKey('families.id'))  # 关联家庭ID
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关联关系
    family = db.relationship('Family', foreign_keys=[family_id], backref=db.backref('members', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'phone': self.phone,
            'avatar': self.avatar,
            'family_id': self.family_id,
            'family_name': self.family.name if self.family else None,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        } 