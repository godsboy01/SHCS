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

from numpy import angle
from ultralytics import YOLO
from models.models import FallDetectionRecord, SittingRecord, db
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
    SIT_CONSECUTIVE_THRESHOLD = 1  # 连续检测到坐下的次数阈值

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
                            self.detect_model = YOLO("models/fall.pt")
                            self.pose_model = YOLO("models/yolo11n-pose.pt")  # 或使用yolov8s-pose.pt
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

                print(f"重试 {i + 1}/{max_retries}")
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

        # 使用检测核心
        detector = FallDetectionCore()
        fall_flag, sit_flag, detection_info = detector.detect(
            frame_np, 
            self.detect_model, 
            self.pose_model
        )

        # 处理检测结果
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
                        if elapsed_time >= snapshot_time and snapshot_time not in self.fall_snapshots_taken:
                            snapshot_filename = f"{self.fall_message_id}-{len(self.fall_snapshots_taken)}.jpg"
                            snapshot_path = os.path.join(self.fall_sub_dir, snapshot_filename)
                            try:
                                cv2.imwrite(snapshot_path, frame_np)
                                logging.info(f"跌倒截图 {snapshot_filename} 保存成功")
                                print("跌倒截图保存成功")
                                self.fall_snapshots_taken.append(snapshot_time)

                                # 保存检测记录到数据库
                                save_fall_detection(
                                    elderly_id=1,
                                    device_id=1,
                                    snapshot_path=snapshot_path
                                )

                                if len(self.fall_snapshots_taken) == len(FALL_SNAPSHOT_TIMES):
                                    self.fall_message_id += 1
                                    self.is_falling = False
                                    self.fall_start_time = None
                                    break
                            except Exception as e:
                                logging.error(f"保存跌倒截图 {snapshot_filename} 失败: {str(e)}")
            else:
                self.is_falling = False
                self.fall_start_time = None

            # 处理久坐检测
            if sit_flag:
                if not self.is_sitting:
                    self.sit_start_time = time.time()
                    self.is_sitting = True
                    self.sit_snapshot_taken = False
                    self.sit_sub_dir = os.path.join(SIT_DIR, str(self.sit_message_id))
                    os.makedirs(self.sit_sub_dir, exist_ok=True)

                    # 创建新的久坐记录
                    save_sitting_record(
                        elderly_id=1,
                        device_id=1
                    )
                else:
                    current_time = time.time()
                    elapsed_time = current_time - self.sit_start_time
                    if elapsed_time >= SIT_SNAPSHOT_TIME and not self.sit_snapshot_taken:
                        snapshot_filename = f"{self.sit_message_id}-0.jpg"
                        snapshot_path = os.path.join(self.sit_sub_dir, snapshot_filename)
                        cv2.imwrite(snapshot_path, frame_np)
                        print("久坐截图保存成功")
                        self.sit_snapshot_taken = True
                        self.sit_message_id += 1
            else:
                if self.is_sitting:
                    update_sitting_record_end(
                        elderly_id=1,
                        device_id=1
                    )
                self.is_sitting = False
                self.sit_start_time = None

        alert_level = 10 if fall_flag or sit_flag else 0
        return frame_np, alert_level

    def calculate_body_angle(self, kpts):
        """计算身体角度（颈部→臀部→脚部的夹角）"""
        try:
            # 确保关键点索引有效
            if len(kpts) < 17:
                return 0.0
            neck = kpts[5]
            hip = kpts[11]
            foot = kpts[15]

            # 计算向量
            vector1 = hip - neck
            vector2 = foot - hip

            # 计算向量夹角
            dot_product = np.dot(vector1, vector2)
            norm1 = np.linalg.norm(vector1)
            norm2 = np.linalg.norm(vector2)
            if norm1 == 0 or norm2 == 0:
                return 0.0
            angle = np.arccos(dot_product / (norm1 * norm2))
            return np.degrees(angle)  # 返回角度值
        except Exception as e:
            print(f"计算身体角度时出错: {str(e)}")
            return 0.0
        except IndexError as e:
            print(f"关键点索引错误: {str(e)}")
            return 0.0

def gen(camera):
    while True:
        frame, alert_level = camera.get_frame()
        if frame:
            frame_np = cv2.imdecode(np.frombuffer(frame, np.uint8), cv2.IMREAD_COLOR)

            # 绘制关键点（调试用）
            results = camera.detect_model(frame_np,conf=0.8)
            for result in results:
                for box in result.boxes:
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                    label = camera.detect_model.names[int(box.cls)]
                    cv2.rectangle(frame_np, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(frame_np, f"{label}:{box.conf[0]:.2f}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9,
                                (0, 255, 0), 2)

                    pose_results = camera.pose_model(frame_np[y1:y2, x1:x2])
                    for pr in pose_results:
                        if pr.keypoints is not None:
                            kpts = pr.keypoints.xy[0].cpu().numpy().astype(int)
                            angle = camera.calculate_body_angle(kpts)
                            # for (x, y) in kpts:
                            #     cv2.circle(frame_np, (x + x1, y + y1), 3, (0, 255, 0), -1)
                            cv2.putText(frame_np, f"Angle:{angle:.1f}°", (x1,y2+30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,0,0), 2)

            ret, jpeg = cv2.imencode('.jpg', frame_np)


            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

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


def save_fall_detection(elderly_id, device_id, snapshot_path):
    """
    保存跌倒检测记录到数据库

    Args:
        elderly_id (int): 老人ID
        device_id (int): 设备ID
        snapshot_path (str): 截图路径
    """
    try:
        # 创建应用上下文
        app = create_app()
        with app.app_context():
            # 创建新的检测记录
            detection_time = datetime.now()
            record = FallDetectionRecord(
                elderly_id=elderly_id,
                device_id=device_id,
                detection_time=detection_time,
                detection_type='Fall',
                confidence=0.8,  # 可以根据实际检测结果调整
                video_frame_path=snapshot_path
            )

            # 添加并保存到数据库
            db.session.add(record)
            db.session.commit()

            camera_logger.info(f"成功保存跌倒检测记录：老人ID={elderly_id}, 设备ID={device_id}, 时间={detection_time}")

    except Exception as e:
        camera_logger.error(f"保存跌倒检测记录失败: {str(e)}")
        # 发生错误时回滚
        with app.app_context():
            db.session.rollback()


def save_sitting_record(elderly_id, device_id):
    """
    保存久坐检测记录到数据库

    Args:
        elderly_id (int): 老人ID
        device_id (int): 设备ID
    """
    try:
        app = create_app()
        with app.app_context():
            current_time = datetime.now()
            # 创建新的久坐记录，只使用模型中存在的字段
            record = SittingRecord(
                elderly_id=elderly_id,
                device_id=device_id,
                start_time=current_time
            )
            db.session.add(record)
            db.session.commit()
            camera_logger.info(f"创建新的久坐记录：老人ID={elderly_id}, 设备ID={device_id}, 开始时间={current_time}")
    except Exception as e:
        camera_logger.error(f"保存久坐记录失败: {str(e)}")
        with app.app_context():
            db.session.rollback()


def update_sitting_record_end(elderly_id, device_id):
    """
    更新久坐记录的结束时间

    Args:
        elderly_id (int): 老人ID
        device_id (int): 设备ID
    """
    try:
        app = create_app()
        with app.app_context():
            active_record = SittingRecord.query.filter_by(
                elderly_id=elderly_id,
                device_id=device_id,
                end_time=None
            ).first()

            if active_record:
                current_time = datetime.now()
                duration = int((current_time - active_record.start_time).total_seconds())

                active_record.end_time = current_time
                active_record.duration = duration

                db.session.commit()
                camera_logger.info(f"结束久坐记录：老人ID={elderly_id}, 设备ID={device_id}, 持续时间={duration}秒")

    except Exception as e:
        camera_logger.error(f"更新久坐记录结束时间失败: {str(e)}")
        with app.app_context():
            db.session.rollback()

class FallDetectionCore:
    def __init__(self):
        self.conf_threshold = 0.8
        self.keypoint_threshold = 0.25  # 关键点置信度阈值
        self.fall_angle_threshold = 30
        self.HEAD_KEYPOINTS = [0, 1, 2, 3, 4]
        self.BODY_KEYPOINTS = [5, 6, 11, 12]
        self.LEG_KEYPOINTS = [13, 14, 15, 16]

    def detect(self, frame, detect_model, pose_model):
        """
        跌倒检测核心逻辑：
        1. 先进行姿态估计，判断关键点有效性
        2. 只有在姿态检测通过后，才进行fall模型判断
        """
        if frame is None:
            return False, False, {}

        # 1. 姿态估计（禁用verbose输出）
        logging.getLogger("ultralytics").setLevel(logging.WARNING)  # 设置更高的日志级别
        pose_results = pose_model(frame, verbose=False)
        if not pose_results:
            return False, False, {}

        valid_poses = []
        for pose_result in pose_results:
            try:
                # 检查关键点是否存在
                if pose_result.keypoints is None:
                    continue

                # 获取关键点坐标和置信度
                kpts = pose_result.keypoints.xy[0].cpu().numpy() if pose_result.keypoints.xy is not None else None
                conf = pose_result.keypoints.conf[0].cpu().numpy() if pose_result.keypoints.conf is not None else None

                if kpts is None or conf is None or len(conf) < 17:
                    continue

                # 检查关键点有效性
                head_conf = any(conf[idx] > self.keypoint_threshold for idx in self.HEAD_KEYPOINTS)
                body_conf = any(conf[idx] > self.keypoint_threshold for idx in self.BODY_KEYPOINTS)
                leg_conf = any(conf[idx] > self.keypoint_threshold for idx in self.LEG_KEYPOINTS)

                if head_conf and body_conf and leg_conf and len(kpts) >= 17:
                    # 计算身体角度
                    angle = self._calculate_body_angle(kpts)
                    if pose_result.boxes is not None and len(pose_result.boxes.xyxy) > 0:
                        box = pose_result.boxes.xyxy[0].cpu().numpy()
                        x1, y1, x2, y2 = map(int, box)
                        
                        # 确保坐标在有效范围内
                        x1, y1 = max(0, x1), max(0, y1)
                        x2, y2 = min(frame.shape[1], x2), min(frame.shape[0], y2)
                        
                        if x2 > x1 and y2 > y1:
                            valid_poses.append({
                                'keypoints': kpts,
                                'angle': angle,
                                'box': (x1, y1, x2, y2)
                            })
            except Exception as e:
                print(f"处理姿态关键点时出错: {str(e)}")
                continue

        if not valid_poses:
            return False, False, {'message': '未检测到有效姿态'}

        # 2. 对有效姿态进行Fall模型检测
        detection_info = {
            'pose_analysis': valid_poses,
            'detection_scores': [],
            'best_detection': None
        }

        for pose in valid_poses:
            try:
                x1, y1, x2, y2 = pose['box']
                target_image = frame[y1:y2, x1:x2]
                if target_image.size == 0:
                    continue

                # Fall模型检测（禁用verbose输出）
                detect_results = detect_model(target_image, conf=self.conf_threshold, verbose=False)
                if not detect_results:
                    continue

                for result in detect_results:
                    for box in result.boxes:
                        label = detect_model.names[int(box.cls)]
                        confidence = float(box.conf)
                        
                        detection = {
                            'label': label,
                            'confidence': confidence,
                            'angle': pose['angle'],
                            'keypoints': pose['keypoints']
                        }
                        detection_info['detection_scores'].append(detection)
            except Exception as e:
                print(f"处理目标检测结果时出错: {str(e)}")
                continue

        # 3. 状态判断
        fall_flag = False
        sit_flag = False

        if detection_info['detection_scores']:
            try:
                # 选择置信度最高的检测结果
                best_detection = max(detection_info['detection_scores'], 
                                   key=lambda x: x['confidence'])
                detection_info['best_detection'] = best_detection

                # 打印检测信息
                print("\n检测结果:")
                print(f"标签: {best_detection['label']}")
                print(f"置信度: {best_detection['confidence']:.3f}")
                print(f"身体角度: {best_detection['angle']:.1f}°")

                # 跌倒判断：必须同时满足姿态和模型判断
                if best_detection['angle'] < self.fall_angle_threshold:
                    if best_detection['label'] == 'Fall Detected':
                        fall_flag = True
                        print("姿态特征和模型都支持跌倒判断")
                    else:
                        print("仅姿态特征支持跌倒判断，等待模型确认")

                # 坐姿判断
                if best_detection['label'] == 'Sitting':
                    if best_detection['angle'] >= self.fall_angle_threshold:
                        sit_flag = True
                        print("检测到正常坐姿")
                    else:
                        print("坐姿角度异常，可能为跌倒")

                print(f"最终状态: {'跌倒' if fall_flag else '坐姿' if sit_flag else '正常'}")
            except Exception as e:
                print(f"处理检测结果时出错: {str(e)}")
                return False, False, {'message': '处理检测结果时出错'}

        return fall_flag, sit_flag, detection_info

    def _calculate_body_angle(self, kpts):
        """计算身体角度"""
        try:
            neck = kpts[5]
            hip = kpts[11]
            foot = kpts[15]

            vector1 = hip - neck
            vector2 = foot - hip

            dot_product = np.dot(vector1, vector2)
            norm1 = np.linalg.norm(vector1)
            norm2 = np.linalg.norm(vector2)

            if norm1 == 0 or norm2 == 0:
                return 0.0

            angle = np.arccos(dot_product / (norm1 * norm2))
            return np.degrees(angle)

        except Exception as e:
            print(f"计算身体角度时出错: {str(e)}")
            return 0.0