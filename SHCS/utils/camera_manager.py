import cv2
import threading
from utils.logger import camera_logger

class CameraManager:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CameraManager, cls).__new__(cls)
            cls._instance._init_camera()
        return cls._instance
    
    def _init_camera(self):
        """初始化摄像头"""
        self.video = None
        self.clients = 0
        self.is_running = False
        self.frame = None
        self.last_error = None
        
    def start(self):
        """启动摄像头"""
        try:
            if self.video is None:
                self.video = cv2.VideoCapture(0, cv2.CAP_DSHOW)
                if not self.video.isOpened():
                    raise Exception("无法打开摄像头，请检查权限或连接。")
                self.is_running = True
                camera_logger.info("摄像头已成功启动")
                return True
        except Exception as e:
            self.last_error = str(e)
            camera_logger.error(f"启动摄像头失败: {str(e)}")
            return False
            
    def stop(self):
        """停止摄像头"""
        if self.video and self.video.isOpened():
            self.video.release()
            self.video = None
            self.is_running = False
            camera_logger.info("摄像头已停止")


            
    def get_frame(self):
        """获取一帧图像"""
        if not self.is_running:
            if not self.start():
                return None
                
        if self.video and self.video.isOpened():
            success, frame = self.video.read()
            if success:
                ret, jpeg = cv2.imencode('.jpg', frame)
                if ret:
                    return jpeg.tobytes()
            camera_logger.error("读取摄像头帧失败")
        return None
        
    def add_client(self):
        """添加客户端"""
        with self._lock:
            self.clients += 1
            if self.clients == 1:
                self.start()
                
    def remove_client(self):
        """移除客户端"""
        with self._lock:
            self.clients = max(0, self.clients - 1)
            if self.clients == 0:
                self.stop()
                
    def get_status(self):
        """获取摄像头状态"""
        return {
            'is_running': self.is_running,
            'clients': self.clients,
            'last_error': self.last_error
        }
        
    def __del__(self):
        """析构函数"""
        self.stop() 