from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO

# 数据库实例
db = SQLAlchemy()
socketio = SocketIO(async_mode='eventlet')
