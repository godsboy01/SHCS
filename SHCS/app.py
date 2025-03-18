from flask import Flask
from flask_cors import CORS
from extensions import db, socketio  # 从extensions导入db和socketio
from config import Config
from multiprocessing import freeze_support

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
    from routes.camera import camera_bp
    from routes.device import device_bp
    from routes.profile import profile_bp
    # from routes.health import health_bp

    # 注册蓝图
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(family_bp, url_prefix='/api/family')
    app.register_blueprint(message_bp, url_prefix='/api/message')
    app.register_blueprint(camera_bp, url_prefix='/api/camera')
    app.register_blueprint(device_bp, url_prefix='/api/device')
    app.register_blueprint(profile_bp)
    # app.register_blueprint(health_bp, url_prefix='/api/health')

    return app

if __name__ == '__main__':
    # Windows下多进程支持
    freeze_support()
    
    app = create_app()
    with app.app_context():
        db.create_all()  # 创建数据库表
    socketio.run(app, debug=True)