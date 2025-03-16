import os
import time
from threading import Thread, Lock
from flask import Blueprint, render_template, Response, jsonify
from flask_cors import cross_origin
import cv2
import numpy as np
from ultralytics import YOLO
from models.models import FallDetectionRecord, db
from app import create_app  # 导入应用工厂函数
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
            cls._instance = super(VideoCamera, cls).__new__(cls)
            cls._instance.video = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            if not cls._instance.video.isOpened():
                camera_logger.error("无法打开摄像头，请检查权限或摄像头连接。")
                return None
            cls._instance.model = YOLO("models/fall.pt")
            # 初始化跌倒检测相关变量
            cls._instance.fall_start_time = None
            cls._instance.is_falling = False
            cls._instance.fall_snapshots_taken = []
            cls._instance.fall_message_id = 1
            # 初始化坐下检测相关变量
            cls._instance.sit_start_time = None
            cls._instance.is_sitting = False
            cls._instance.sit_snapshot_taken = False
            cls._instance.sit_message_id = 1
            cls._instance.sit_consecutive_count = 0  # 连续检测到坐下的次数
        return cls._instance

    def add_client(self):
        self._clients += 1

    def remove_client(self):
        self._clients -= 1
        if self._clients <= 0:
            self.release()

    def release(self):
        if hasattr(self, 'video') and self.video.isOpened():
            self.video.release()
            camera_logger.info("摄像头资源已释放。")
            # print("摄像头资源已释放。")

    def get_frame(self):
        if self.video.isOpened():
            success, image = self.video.read()
            if success:
                # print("摄像头成功读取帧")
                ret, jpeg = cv2.imencode('.jpg', image)
                return jpeg.tobytes(), 0  # 返回帧数据和警报级别
            else:
                camera_logger.error("无法读取帧，可能是摄像头问题。")
                print("无法读取帧，可能是摄像头问题。")
        else:
            print("摄像头未打开")
        return None, 0

    def detect_fall_and_sit(self, frame_np):
        if frame_np is None:
            camera_logger.error("无效的帧数据")
            print("无效的帧数据")
            return frame_np, 0

        # 使用 YOLOv8 模型检测跌倒和坐下，设置 verbose=False 隐藏输出信息
        results = self.model(frame_np, verbose=False)
        fall_flag = False
        sit_flag = False
        for result in results:
            for box in result.boxes:
                label = self.model.names[int(box.cls)]
                detection_logger.debug(f"检测到标签: {label} (类型: {type(label)})") 
                # print(f"检测到标签: {label} (类型: {type(label)})")
                if label.lower() == 'fall detected':
                    fall_flag = True
                elif label.lower() == 'sitting':
                    sit_flag = True

        with self._lock:
            # 处理跌倒检测
            if fall_flag:
                if not self.is_falling:
                    # 记录跌倒开始时间
                    self.fall_start_time = time.time()
                    self.is_falling = True
                    self.fall_snapshots_taken = []
                    # 创建新的跌倒子文件夹
                    self.fall_sub_dir = os.path.join(FALL_DIR, str(self.fall_message_id))
                    os.makedirs(self.fall_sub_dir, exist_ok=True)
                    detection_logger.info(f"开始记录跌倒事件，fall_start_time: {self.fall_start_time}")  # L112
                    print(f"开始记录跌倒事件，fall_start_time: {self.fall_start_time}")
                else:
                    # 检查跌倒持续时间是否达到截图时间点
                    elapsed_time = time.time() - self.fall_start_time
                    detection_logger.debug(f"跌倒持续时间: {elapsed_time}")  # L116
                    print(f"跌倒持续时间: {elapsed_time}")
                    for snapshot_time in FALL_SNAPSHOT_TIMES:
                        if elapsed_time >= snapshot_time and snapshot_time not in self.fall_snapshots_taken:
                            # 保存截图
                            snapshot_filename = f"{self.fall_message_id}-{len(self.fall_snapshots_taken)}.jpg"
                            snapshot_path = os.path.join(self.fall_sub_dir, snapshot_filename)
                            cv2.imwrite(snapshot_path, frame_np)
                            detection_logger.info(f"跌倒截图已保存: {snapshot_path}")  # L123
                            # print(f"跌倒截图已保存: {snapshot_path}")
                            self.fall_snapshots_taken.append(snapshot_time)

                            # 如果所有截图都已保存，重置状态并保存到数据库
                            if len(self.fall_snapshots_taken) == len(FALL_SNAPSHOT_TIMES):
                                self.fall_message_id += 1
                                self.is_falling = False
                                self.fall_start_time = None
                                detection_logger.info("跌倒截图保存完成，重置状态")  # L131
                                print("跌倒截图保存完成，重置状态")
                                # 调用保存函数（默认 user_id=1, device_id=1）
                                self.save_fall_record_to_db(
                                    user_id=1,
                                    device_id=1,
                                    confidence=0.9,  # 假设置信度为 0.9
                                    status='fall',
                                    detection_type='Fall Detected',
                                    video_frame_path=self.fall_sub_dir
                                )
                                break
            else:
                # 如果没有检测到跌倒，重置状态
                if self.is_falling:
                    detection_logger.info("跌倒结束，重置状态")  # L145
                    print("跌倒结束，重置状态")
                self.is_falling = False
                self.fall_start_time = None

            # 处理坐下检测
            if sit_flag:
                self.sit_consecutive_count += 1
                if self.sit_consecutive_count >= self.SIT_CONSECUTIVE_THRESHOLD:
                    if not self.is_sitting:
                        # 记录坐下开始时间
                        self.sit_start_time = time.time()
                        self.is_sitting = True
                        self.sit_snapshot_taken = False
                        # 创建新的坐下子文件夹
                        self.sit_sub_dir = os.path.join(SIT_DIR, str(self.sit_message_id))
                        os.makedirs(self.sit_sub_dir, exist_ok=True)
                        detection_logger.info(f"开始记录坐下事件，sit_start_time: {self.sit_start_time}")  # L161
                        print(f"开始记录坐下事件，sit_start_time: {self.sit_start_time}")
                    else:
                        # 检查坐下持续时间是否达到截图时间点
                        current_time = time.time()
                        elapsed_time = current_time - self.sit_start_time
                        detection_logger.info(f"坐下截图已保存: {snapshot_path}")  # L173
                        print(f"坐下开始时间: {self.sit_start_time}, 当前时间: {current_time}, 坐下持续时间: {elapsed_time}")
                        # 增加一个小的误差范围
                        if elapsed_time >= SIT_SNAPSHOT_TIME - 0.1 and not self.sit_snapshot_taken:
                            # 保存截图
                            snapshot_filename = f"{self.sit_message_id}-0.jpg"
                            snapshot_path = os.path.join(self.sit_sub_dir, snapshot_filename)
                            cv2.imwrite(snapshot_path, frame_np)
                            print(f"坐下截图已保存: {snapshot_path}")
                            self.sit_snapshot_taken = True
                            self.sit_message_id += 1
                            self.is_sitting = False
                            self.sit_start_time = None
                            print("坐下截图保存完成，重置状态")
                            
            else:
                self.sit_consecutive_count = 0
                # 如果没有检测到坐下，重置状态
                if self.is_sitting:
                    print("坐下结束，重置状态")
                self.is_sitting = False
                self.sit_start_time = None

        alert_level = 10 if fall_flag or sit_flag else 0
        return frame_np, alert_level

    def save_fall_record_to_db(self, user_id, device_id, confidence, status, detection_type, video_frame_path):
        """保存跌倒记录到数据库"""
        app = create_app()  # 调用应用工厂函数获取应用实例
        try:
            with app.app_context():
                new_record = FallDetectionRecord(
                    user_id=user_id,
                    device_id=device_id,
                    confidence=confidence,
                    status=status,
                    detection_type=detection_type,
                    video_frame_path=video_frame_path
                )
                db.session.add(new_record)
                db.session.commit()

                print(f"数据库记录保存成功，ID: {new_record.record_id}")
        except Exception as e:
            db.session.rollback()
            print(f"数据库保存失败: {str(e)}")

@camera_bp.route('/')
def index():
    return render_template('index.html')

def gen(camera):
    while True:
        frame, alert_level = camera.get_frame()  # 获取帧和警报级别
        if frame:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
            # 如果警报级别大于 0，表示检测到跌倒或坐下
            if alert_level > 0:
                print(f"检测到事件，警报级别: {alert_level}")
        else:
            print("未获取到有效帧，跳过本次传输。")
        time.sleep(0.5)  # 控制帧率

camera = VideoCamera()

@camera_bp.route('/video_feed')
@cross_origin()  # 添加跨域支持
def video_feed():
    return Response(gen(camera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# 提供一个方法供其他模块使用摄像头资源
def get_camera_instance():
    return camera

# 添加一个新路由来获取警报级别
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

# 添加路由获取跌倒记录
@camera_bp.route('/fall_records')
@cross_origin()
def get_fall_records():
    """获取所有跌倒记录（测试用）"""
    app = create_app()  # 调用应用工厂函数获取应用实例
    try:
        with app.app_context():
            records = FallDetectionRecord.query.all()
            return jsonify([{
                'record_id': r.record_id,
                'user_id': r.user_id,
                'device_id': r.device_id,
                'detection_time': r.detection_time.strftime('%Y-%m-%d %H:%M:%S'),
                'confidence': r.confidence,
                'status': r.status,
                'detection_type': r.detection_type,
                'video_frame_path': r.video_frame_path
            } for r in records])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@camera_bp.route('/fall_snapshots/<path:fall_dir>/<path:filename>')
def get_fall_snapshot(fall_dir, filename):
    full_path = os.path.join('static', 'snapshots', fall_dir, filename)
    if not os.path.exists(full_path):
        return jsonify({"error": "Image not found"}), 404
    return send_from_directory(os.path.dirname(full_path), filename)
def start_detection(camera):
    print("检测线程已启动")
    while True:
        frame, _ = camera.get_frame()
        if frame:
            # 将字节流解码为 NumPy 数组
            frame_np = cv2.imdecode(np.frombuffer(frame, np.uint8), cv2.IMREAD_COLOR)
            if frame_np is not None:
                # 调用检测逻辑
                _, alert_level = camera.detect_fall_and_sit(frame_np)
                if alert_level > 0:
                    print(f"检测到事件，警报级别: {alert_level}")
            else:
                print("Failed to decode frame")  # 如果解码失败，打印错误信息
        else:
            print("未获取到有效帧，跳过本次传输。")
        time.sleep(0.5)  # 控制帧率

# 启动检测线程
detection_thread = Thread(target=start_detection, args=(camera,))
detection_thread.daemon = True
detection_thread.start()