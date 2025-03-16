import os
from datetime import timedelta

class Config:
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:123456@localhost:3306/smart_home_care'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 安全配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'  # 建议使用环境变量
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'your-jwt-secret-key'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1)
    
    # Redis配置
    REDIS_URL = 'redis://localhost:6379/0'
    
    # 文件上传配置
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 最大16MB
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    
    # 安全headers
    SECURITY_HEADERS = {
        'X-Frame-Options': 'SAMEORIGIN',
        'X-XSS-Protection': '1; mode=block',
        'X-Content-Type-Options': 'nosniff',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains'
    }
    
    # 密码策略
    PASSWORD_POLICY = {
        'MIN_LENGTH': 8,
        'REQUIRE_UPPER': True,
        'REQUIRE_LOWER': True,
        'REQUIRE_NUMBERS': True,
        'REQUIRE_SPECIAL': True
    }
    
    # 速率限制
    RATELIMIT_DEFAULT = "200 per day"
    RATELIMIT_STORAGE_URL = REDIS_URL
    RATELIMIT_STRATEGY = 'fixed-window'