import time
from datetime import datetime
from utils.logger import notification_logger
from models.models import Notification, db

class NotificationManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(NotificationManager, cls).__new__(cls)
        return cls._instance
        
    def send_fall_alert(self, user_id, device_id, snapshot_path):
        """发送跌倒预警通知"""
        try:
            notification = Notification(
                user_id=user_id,
                type='fall',
                title='跌倒预警',
                content=f'检测到可能的跌倒事件，请及时查看。',
                status='unread',
                image_path=snapshot_path,
                device_id=device_id,
                timestamp=datetime.now()
            )
            db.session.add(notification)
            db.session.commit()
            notification_logger.info(f"已发送跌倒预警通知，ID: {notification.id}")
            return True
        except Exception as e:
            notification_logger.error(f"发送跌倒预警通知失败: {str(e)}")
            db.session.rollback()
            return False
            
    def send_sitting_alert(self, user_id, device_id, duration):
        """发送久坐预警通知"""
        try:
            notification = Notification(
                user_id=user_id,
                type='sitting',
                title='久坐提醒',
                content=f'您已持续久坐{duration}分钟，请适当活动。',
                status='unread',
                device_id=device_id,
                timestamp=datetime.now()
            )
            db.session.add(notification)
            db.session.commit()
            notification_logger.info(f"已发送久坐提醒通知，ID: {notification.id}")
            return True
        except Exception as e:
            notification_logger.error(f"发送久坐提醒通知失败: {str(e)}")
            db.session.rollback()
            return False
            
    def get_unread_notifications(self, user_id):
        """获取用户未读通知"""
        try:
            notifications = Notification.query.filter_by(
                user_id=user_id,
                status='unread'
            ).order_by(
                Notification.timestamp.desc()
            ).all()
            
            return [{
                'id': n.id,
                'type': n.type,
                'title': n.title,
                'content': n.content,
                'timestamp': n.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'image_path': n.image_path
            } for n in notifications]
        except Exception as e:
            notification_logger.error(f"获取未读通知失败: {str(e)}")
            return []
            
    def mark_as_read(self, notification_id):
        """将通知标记为已读"""
        try:
            notification = Notification.query.get(notification_id)
            if notification:
                notification.status = 'read'
                db.session.commit()
                notification_logger.info(f"通知 {notification_id} 已标记为已读")
                return True
            return False
        except Exception as e:
            notification_logger.error(f"标记通知已读失败: {str(e)}")
            db.session.rollback()
            return False 