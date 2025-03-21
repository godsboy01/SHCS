from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from config import Config

# 初始化数据库
db = SQLAlchemy()
socketio = SocketIO(async_mode='eventlet')  # 先初始化 SocketIO 但不传入 app

def create_app():
    app = Flask(__name__)
    CORS(app)  # 添加 CORS 支持

    app.config.from_object(Config)

    # 初始化数据库和 SocketIO
    db.init_app(app)
    socketio.init_app(app)

    # 导入蓝图
    from routes.auth import auth_bp
    from routes.family import family_bp
    from routes.message import message_bp
    from routes.camera import camera_bp, get_camera_instance
    from routes.health import health_bp

    # 将摄像头实例注入到应用上下文中
    app.camera = get_camera_instance()
    # 将 SocketIO 实例注入到应用上下文中
    app.socketio = socketio

    # 注册蓝图
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(family_bp, url_prefix='/api/family')
    app.register_blueprint(message_bp, url_prefix='/api/message')
    app.register_blueprint(camera_bp, url_prefix='/api/camera')
    app.register_blueprint(health_bp, url_prefix='/api/health')

    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()  # 创建数据库表
    socketio.run(app, debug=True)