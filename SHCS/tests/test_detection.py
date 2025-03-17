import os
import sys
import cv2
import time
import pytest
import numpy as np

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.append(project_root)

from utils.camera_manager import CameraManager
from utils.detection_manager import DetectionManager

@pytest.fixture
def camera():
    """摄像头fixture"""
    cam = CameraManager()
    yield cam
    cam.stop()

@pytest.fixture
def detector():
    """检测器fixture"""
    return DetectionManager()

def test_camera_initialization(camera):
    """测试摄像头初始化"""
    assert camera.start(), "摄像头启动失败"
    frame = camera.get_frame()
    assert frame is not None, "无法获取视频帧"
    print("✓ 摄像头测试通过")

def test_detector_initialization(detector):
    """测试检测器初始化"""
    status = detector.get_status()
    assert status['model_loaded'], "YOLO模型加载失败"
    print("✓ 检测器测试通过")

def test_real_time_detection(camera, detector):
    """测试实时检测功能"""
    assert camera.start(), "摄像头启动失败"
    
    # 获取一帧并进行检测
    frame = camera.get_frame()
    assert frame is not None, "无法获取视频帧"
    
    # 将字节流转换为numpy数组
    nparr = np.frombuffer(frame, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    # 执行检测
    processed_frame, alert_level = detector.detect(frame)
    
    assert processed_frame is not None, "处理后的帧为空"
    assert isinstance(alert_level, int), "警报级别类型错误"
    assert alert_level in [0, 1, 2], "警报级别值错误"
    
    print("✓ 实时检测测试通过")

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 