import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime

# 日志存放目录
LOG_DIR = "d:\\12103\\Desktop\\myDemo\\SHCS\\SHCS\\logs"
os.makedirs(LOG_DIR, exist_ok=True)

def setup_logger(name, log_file, level=logging.INFO):
    """配置日志记录器
    Args:
        name: 日志记录器名称
        log_file: 日志文件名
        level: 日志级别
    """
    # 创建日志记录器
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # 创建按大小轮转的文件处理器 (10MB/文件，保留5个备份)
    file_handler = RotatingFileHandler(
        os.path.join(LOG_DIR, log_file),
        maxBytes=10*1024*1024,
        backupCount=5
    )

    # 创建控制台处理器
    console_handler = logging.StreamHandler()

    # 设置日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # 添加处理器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

# 创建不同模块的日志记录器
camera_logger = setup_logger('camera', 'camera.log')
detection_logger = setup_logger('detection', 'detection.log')
db_logger = setup_logger('database', 'database.log')