import os
import cv2
import numpy as np
import threading
from datetime import datetime
from ultralytics import YOLO
from utils.logger import detection_logger

class DetectionManager:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DetectionManager, cls).__new__(cls)
            cls._instance._init_detection()
        return cls._instance
    
    def _init_detection(self):
        """初始化检测器"""
        try:
            # 初始化YOLO模型
            model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models", "fall.pt")
            self.model = YOLO(model_path)
            
            # 初始化检测参数
            self.fall_confidence_threshold = 0.8
            self.sit_confidence_threshold = 0.8
            
            # 初始化存储目录
            self._init_directories()
            
            detection_logger.info("检测管理器初始化成功")
        except Exception as e:
            detection_logger.error(f"检测管理器初始化失败: {str(e)}")
            raise
    
    def _init_directories(self):
        """初始化存储目录"""
        try:
            base_dir = os.path.dirname(os.path.dirname(__file__))
            self.snapshot_dir = os.path.join(base_dir, "static", "snapshots")
            os.makedirs(self.snapshot_dir, exist_ok=True)
            detection_logger.info("存储目录初始化成功")
        except Exception as e:
            detection_logger.error(f"存储目录初始化失败: {str(e)}")
            raise
    
    def detect(self, frame):
        """执行检测"""
        if frame is None:
            detection_logger.error("无效的帧数据")
            return frame, 0
            
        try:
            # 使用YOLO模型进行检测
            results = self.model(frame, verbose=False)
            
            # 初始化检测标志
            fall_detected = False
            sit_detected = False
            
            # 处理检测结果
            for result in results:
                for box in result.boxes:
                    cls = int(box.cls)
                    conf = float(box.conf)
                    label = self.model.names[cls]
                    
                    if label.lower() == 'fall detected' and conf >= self.fall_confidence_threshold:
                        fall_detected = True
                        # 在检测框周围画红色边框
                        box_coords = box.xyxy[0].cpu().numpy()
                        cv2.rectangle(frame, 
                                    (int(box_coords[0]), int(box_coords[1])),
                                    (int(box_coords[2]), int(box_coords[3])),
                                    (0, 0, 255), 2)
                        # 添加文本标签
                        cv2.putText(frame, f'Fall {conf:.2f}', 
                                  (int(box_coords[0]), int(box_coords[1]-10)),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
                        
                    elif label.lower() == 'sitting' and conf >= self.sit_confidence_threshold:
                        sit_detected = True
                        # 在检测框周围画黄色边框
                        box_coords = box.xyxy[0].cpu().numpy()
                        cv2.rectangle(frame, 
                                    (int(box_coords[0]), int(box_coords[1])),
                                    (int(box_coords[2]), int(box_coords[3])),
                                    (0, 255, 255), 2)
                        # 添加文本标签
                        cv2.putText(frame, f'Sitting {conf:.2f}', 
                                  (int(box_coords[0]), int(box_coords[1]-10)),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2)
            
            # 保存检测到的异常帧
            if fall_detected or sit_detected:
                filename = f"detection_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                filepath = os.path.join(self.snapshot_dir, filename)
                cv2.imwrite(filepath, frame)
                detection_logger.info(f"保存检测帧: {filepath}")
            
            # 返回处理后的帧和警报级别
            alert_level = 2 if fall_detected else (1 if sit_detected else 0)
            return frame, alert_level
            
        except Exception as e:
            detection_logger.error(f"检测过程发生错误: {str(e)}")
            return frame, 0
            
    def get_status(self):
        """获取检测器状态"""
        return {
            'model_loaded': hasattr(self, 'model'),
            'fall_confidence_threshold': self.fall_confidence_threshold,
            'sit_confidence_threshold': self.sit_confidence_threshold
        } 