import logging
import os
import time
from datetime import datetime
from threading import Thread, Lock
from flask import Blueprint, render_template, Response, jsonify, current_app
from flask_cors import cross_origin
import cv2
import numpy as np

from datetime import datetime
from ultralytics import YOLO
from models.models import FallDetectionRecord, db
from app import create_app
from flask import Blueprint, send_from_directory
from utils.logger import camera_logger, detection_logger, db_logger

camera_bp = Blueprint('camera', __name__)

# 配置参数
FALL_SNAPSHOT_TIMES = [3, 4, 5]  # 跌倒截图时间点（相对于跌倒开始时间）
SIT_SNAPSHOT_TIME = 3  # 坐下截图时间点
SNAPSHOT_DIR = "static/snapshots"  # 截图保存主目录
FALL_DIR = os.path.join(SNAPSHOT_DIR, "fall")  # 跌倒截图保存目录
SIT_DIR = os.path.join(SNAPSHOT_DIR, "sit")  # 坐下截图保存目录

# 创建目录（如果不存在）
os.makedirs(FALL_DIR, exist_ok=True)
os.makedirs(SIT_DIR, exist_ok=True)

class VideoCamera(object):
    _instance = None
    _clients = 0
    _lock = Lock()
    SIT_CONSECUTIVE_THRESHOLD = 3  # 连续检测到坐下的次数阈值

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    instance = super(VideoCamera, cls).__new__(cls)
                    if instance._init_camera():
                        cls._instance = instance
                    else:
                        print("摄像头初始化失败")
                        return None
        return cls._instance

    def _init_camera(self):
        """初始化摄像头，包含重试机制"""
        max_retries = 3
        for i in range(max_retries):
            try:
                # 尝试不同的摄像头初始化方法
                methods = [
                    (0, cv2.CAP_DSHOW),
                    (0, cv2.CAP_ANY),
                    (0, cv2.CAP_MSMF)
                ]
                
                for camera_id, api_preference in methods:
                    try:
                        self.video = cv2.VideoCapture(camera_id, api_preference)
                        if self.video.isOpened():
                            # 设置摄像头参数
                            self.video.set(cv2.CAP_PROP_FRAME_WIDTH, 480)
                            self.video.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)
                            self.video.set(cv2.CAP_PROP_FPS, 15)
                            
                            # 初始化其他属性
                            self.model = YOLO("models/fall.pt")
                            self.fall_start_time = None
                            self.is_falling = False
                            self.fall_snapshots_taken = []
                            self.fall_message_id = 1
                            self.sit_start_time = None
                            self.is_sitting = False
                            self.sit_snapshot_taken = False
                            self.sit_message_id = 1
                            self.sit_consecutive_count = 0
                            
                            print(f"成功使用方法 {api_preference} 初始化摄像头")
                            return True
                    except Exception as e:
                        print(f"摄像头初始化方法 {api_preference} 失败: {str(e)}")
                        continue
                
                print(f"重试 {i+1}/{max_retries}")
                time.sleep(1)
            except Exception as e:
                print(f"摄像头初始化异常: {str(e)}")
        
        return False

    def add_client(self):
        self._clients += 1

    def remove_client(self):
        self._clients -= 1
        if self._clients <= 0:
            self.release()

    def release(self):
        if hasattr(self, 'video') and self.video.isOpened():
            self.video.release()
            print("摄像头资源已释放。")

    def get_frame(self):
        """获取视频帧，包含错误处理"""
        if not hasattr(self, 'video') or self.video is None:
            return None, 0
            
        try:
            if self.video.isOpened():
                success, image = self.video.read()
                if success:
                    # 调整图像大小和压缩率
                    image = cv2.resize(image, (480, 360))
                    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 70]
                    ret, jpeg = cv2.imencode('.jpg', image, encode_param)
                    return jpeg.tobytes(), 0
                else:
                    print("无法读取帧，尝试重新初始化摄像头")
                    if self._init_camera():
                        return self.get_frame()
            else:
                print("摄像头未打开，尝试重新初始化")
                if self._init_camera():
                    return self.get_frame()
        except Exception as e:
            print(f"获取帧时发生错误: {str(e)}")
        
        return None, 0

    def detect_fall_and_sit(self, frame_np):
        if frame_np is None:
            print("无效的帧数据")
            return frame_np, 0

        results = self.model(frame_np, verbose=False)
        fall_flag = False
        sit_flag = False
        
        for result in results:
            for box in result.boxes:
                label = self.model.names[int(box.cls)]
                if label.lower() == 'fall detected':
                    fall_flag = True
                elif label.lower() == 'sitting':
                    sit_flag = True

        with self._lock:
            # 处理跌倒检测
            if fall_flag:
                if not self.is_falling:
                    self.fall_start_time = time.time()
                    self.is_falling = True
                    self.fall_snapshots_taken = []
                    self.fall_sub_dir = os.path.join(FALL_DIR, str(self.fall_message_id))
                    os.makedirs(self.fall_sub_dir, exist_ok=True)
                else:
                    elapsed_time = time.time() - self.fall_start_time
                    for snapshot_time in FALL_SNAPSHOT_TIMES:
                        # 保存
                        if elapsed_time >= snapshot_time and snapshot_time not in self.fall_snapshots_taken:
                            snapshot_filename = f"{self.fall_message_id}-{len(self.fall_snapshots_taken)}.jpg"
                            snapshot_path = os.path.join(self.fall_sub_dir, snapshot_filename)
                            try:
                                cv2.imwrite(snapshot_path, frame_np)
                                logging.info(f"跌倒截图 {snapshot_filename} 保存成功")
                                print("跌倒截图保存成功")
                                self.fall_snapshots_taken.append(snapshot_time)
                                detection_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                                save_fall_record(
                                    elderly_id=1,  # 替换为实际的 elderly_id
                                    device_id=1,  # 替换为实际的 device_id
                                    detection_time=detection_time,
                                    detection_type='Fall',
                                    video_frame_path=snapshot_path
                                )
                                if len(self.fall_snapshots_taken) == len(FALL_SNAPSHOT_TIMES):
                                    self.fall_message_id += 1
                                    self.is_falling = False
                                    self.fall_start_time = None
                                    # save_fall_record(1,1,datetime.time(),Fall)
                                    break
                            except Exception as e:
                                logging.error(f"保存跌倒截图 {snapshot_filename} 失败: {str(e)}")
            else:
                self.is_falling = False
                self.fall_start_time = None

            # 处理坐下检测
            if sit_flag:
                self.sit_consecutive_count += 1
                if self.sit_consecutive_count >= self.SIT_CONSECUTIVE_THRESHOLD:
                    if not self.is_sitting:
                        self.sit_start_time = time.time()
                        self.is_sitting = True
                        self.sit_snapshot_taken = False
                        self.sit_sub_dir = os.path.join(SIT_DIR, str(self.sit_message_id))
                        os.makedirs(self.sit_sub_dir, exist_ok=True)
                    else:
                        current_time = time.time()
                        elapsed_time = current_time - self.sit_start_time
                        if elapsed_time >= SIT_SNAPSHOT_TIME - 0.1 and not self.sit_snapshot_taken:
                            snapshot_filename = f"{self.sit_message_id}-0.jpg"
                            snapshot_path = os.path.join(self.sit_sub_dir, snapshot_filename)
                            cv2.imwrite(snapshot_path, frame_np)
                            print("久坐截图保存成功")
                            self.sit_snapshot_taken = True
                            self.sit_message_id += 1
                            self.is_sitting = False
                            self.sit_start_time = None
            else:
                self.sit_consecutive_count = 0
                self.is_sitting = False
                self.sit_start_time = None

        alert_level = 10 if fall_flag or sit_flag else 0
        return frame_np, alert_level

def gen(camera):
    while True:
        frame, alert_level = camera.get_frame()
        if frame:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
            # if alert_level > 0:
            #     print(f"检测到事件，警报级别: {alert_level}")
        else:
            print("未获取到有效帧，跳过本次传输。")
        time.sleep(0.05)  # 控制帧率为20fps

def start_detection(camera):
    """检测线程的主函数"""
    print("检测线程已启动")
    while True:
        frame, _ = camera.get_frame()
        if frame:
            frame_np = cv2.imdecode(np.frombuffer(frame, np.uint8), cv2.IMREAD_COLOR)
            if frame_np is not None:
                _, alert_level = camera.detect_fall_and_sit(frame_np)
                # if alert_level > 0:
                #     print(f"检测到事件，警报级别: {alert_level}")
        time.sleep(0.5)  # 控制检测频率

camera = VideoCamera()

# 启动检测线程
detection_thread = Thread(target=start_detection, args=(camera,))
detection_thread.daemon = True
detection_thread.start()

@camera_bp.route('/video_feed')
@cross_origin()
def video_feed():
    return Response(gen(camera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@camera_bp.route('/alert_level')
@cross_origin()
def get_alert_level():
    frame, _ = camera.get_frame()
    if frame:
        frame_np = cv2.imdecode(np.frombuffer(frame, np.uint8), cv2.IMREAD_COLOR)
        _, alert_level = camera.detect_fall_and_sit(frame_np)
        return jsonify({"alert_level": alert_level})
    else:
        return jsonify({"error": "无法获取帧数据"}), 500

@camera_bp.route('/fall_snapshots')
@cross_origin()
def get_fall_snapshots():
    fall_snapshots = []
    for sub_dir in os.listdir(FALL_DIR):
        sub_dir_path = os.path.join(FALL_DIR, sub_dir)
        if os.path.isdir(sub_dir_path):
            for filename in os.listdir(sub_dir_path):
                if filename.endswith('.jpg'):
                    fall_snapshots.append({
                        'filename': filename,
                        'path': os.path.join(sub_dir_path, filename)
                    })
    return jsonify(fall_snapshots)

@camera_bp.route('/sit_snapshots')
@cross_origin()
def get_sit_snapshots():
    sit_snapshots = []
    for sub_dir in os.listdir(SIT_DIR):
        sub_dir_path = os.path.join(SIT_DIR, sub_dir)
        if os.path.isdir(sub_dir_path):
            for filename in os.listdir(sub_dir_path):
                if filename.endswith('.jpg'):
                    sit_snapshots.append({
                        'filename': filename,
                        'path': os.path.join(sub_dir_path, filename)
                    })
    return jsonify(sit_snapshots)



def save_fall_record(elderly_id, device_id, detection_time, detection_type, video_frame_path):
    """独立的保存记录函数"""
    try:
        app = create_app()
        with app.app_context():
            record = FallDetectionRecord(
                elderly_id=elderly_id,
                device_id=device_id,
                detection_time=detection_time,
                detection_type=detection_type,
                confidence=0.8,
                video_frame_path=video_frame_path
            )
    except Exception as e:
        app = create_app()
        with app.app_context():
            db.session.rollback()
        logging.error(f"保存 {detection_type} 记录失败: {str(e)}")
    except Exception as e:
        logging.error(f"保存 {detection_type} 记录失败: {str(e)}")
        db.session.rollback()
