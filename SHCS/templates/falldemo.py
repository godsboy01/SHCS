import torch
import cv2 as cv
import numpy as np
import time
from ultralytics.data.augment import LetterBox
from ultralytics.utils import ops

# ------------------------
# 系统参数配置
# ------------------------
camera_index = 0
device = 'cpu'
conf = 0.25
iou = 0.7

# ------------------------
# 初始化摄像头
# ------------------------
cap = cv.VideoCapture(camera_index)
if not cap.isOpened():
    print("错误: 无法打开摄像头.")
    exit()

# ------------------------
# 加载模型
# ------------------------
# 姿态估计模型
pose_model = torch.load(
    'D:\\12103\\Desktop\\myDemo\\SHCS\\SHCS\\models\\yolov8n-pose.pt',
    map_location='cpu'
)['model'].to(device).float().eval()

# 跌倒检测模型（检测模型，非分类）
fall_model = torch.load(
    'D:\\12103\\Desktop\\myDemo\\SHCS\\SHCS\\models\\fall.pt',
    map_location=device
)['model'].to(device).float().eval()

# ------------------------
# 状态标签定义
# ------------------------
state_labels = ['Fall Detected', 'Walking', 'Sitting']

# ------------------------
# COCO关键点分组（17关键点）
# ------------------------
HEAD_KEYPOINTS = [0, 1, 2, 3, 4]  # 头部关键点
BODY_KEYPOINTS = [5, 6, 11, 12]  # 身体关键点
LEG_KEYPOINTS = [13, 14, 15, 16]  # 腿部关键点

class PostureAnalyzer:
    def __init__(self):
        self.HEAD_KEYPOINTS = [0, 1, 2, 3, 4]
        self.BODY_KEYPOINTS = [5, 6, 11, 12]
        self.LEG_KEYPOINTS = [13, 14, 15, 16]
        
        self.height_ratio_threshold = 0.6
        self.angle_threshold = 65
        
    def analyze_keypoints(self, keypoints):
        head_center = np.mean(keypoints[self.HEAD_KEYPOINTS], axis=0)
        body_center = np.mean(keypoints[self.BODY_KEYPOINTS], axis=0)
        leg_center = np.mean(keypoints[self.LEG_KEYPOINTS], axis=0)
        
        height = head_center[1] - leg_center[1]
        width = np.max(keypoints[:, 0]) - np.min(keypoints[:, 0])
        height_width_ratio = height / width if width != 0 else 0
        
        body_angle = np.abs(np.degrees(np.arctan2(
            body_center[1] - head_center[1],
            body_center[0] - head_center[0]
        )))
        
        head_foot_horizontal = abs(head_center[0] - leg_center[0])
        vertical_angle = 90 - body_angle
        
        key_points = np.vstack([head_center, body_center, leg_center])
        vertical_spread = np.std(key_points[:, 1])
        horizontal_spread = np.std(key_points[:, 0])
        vertical_horizontal_ratio = vertical_spread / horizontal_spread if horizontal_spread != 0 else float('inf')
        
        upper_body_angle = np.abs(np.degrees(np.arctan2(
            body_center[1] - head_center[1],
            body_center[0] - head_center[0]
        )))
        
        lower_body_angle = np.abs(np.degrees(np.arctan2(
            leg_center[1] - body_center[1],
            leg_center[0] - body_center[0]
        )))
        
        leg_points = keypoints[self.LEG_KEYPOINTS]
        leg_height_range = np.max(leg_points[:, 1]) - np.min(leg_points[:, 1])
        leg_width_range = np.max(leg_points[:, 0]) - np.min(leg_points[:, 0])
        leg_ratio = leg_height_range / leg_width_range if leg_width_range != 0 else float('inf')
        
        head_body_height_ratio = (head_center[1] - body_center[1]) / (
                                body_center[1] - leg_center[1]) if (body_center[1] - leg_center[1]) != 0 else 0
        
        body_compression = height / (np.max(keypoints[:, 1]) - np.min(keypoints[:, 1])) if (np.max(keypoints[:, 1]) - np.min(keypoints[:, 1])) != 0 else 0
        
        return {
            'height_width_ratio': height_width_ratio,
            'body_angle': body_angle,
            'head_height': head_center[1],
            'body_height': body_center[1],
            'leg_height': leg_center[1],
            'head_foot_horizontal': head_foot_horizontal,
            'vertical_angle': vertical_angle,
            'head_body_height_ratio': head_body_height_ratio,
            'body_compression': body_compression,
            'vertical_horizontal_ratio': vertical_horizontal_ratio,
            'vertical_spread': vertical_spread,
            'horizontal_spread': horizontal_spread,
            'upper_body_angle': upper_body_angle,
            'lower_body_angle': lower_body_angle,
            'leg_ratio': leg_ratio
        }

class StateTracker:
    def __init__(self, window_size=5):
        self.states = []
        self.confidences = []
        self.window_size = window_size
        self.fall_threshold = 0.7
        self.current_state_start_time = None
        self.last_state = None
        self.fall_alert_sent = False
        self.sitting_alert_sent = False
        self.sitting_confidence_history = []
        self.sitting_history_size = 10
        
    def update(self, state, confidence):
        self.states.append(state)
        self.confidences.append(confidence)
        
        if state == 'Sitting':
            self.sitting_confidence_history.append(confidence)
            if len(self.sitting_confidence_history) > self.sitting_history_size:
                self.sitting_confidence_history.pop(0)
        
        if state != self.last_state:
            self.current_state_start_time = time.time()
            self.fall_alert_sent = False
            self.sitting_alert_sent = False
            if state != 'No Valid Person':
                print(f"\n状态变化: {state} (置信度: {confidence:.2f})")
        
        self.last_state = state
        
        if self.current_state_start_time is not None:
            duration = time.time() - self.current_state_start_time
            
            if state == 'Fall Detected' and duration >= 3 and not self.fall_alert_sent:
                print(f"\n[警告] 检测到持续跌倒状态！持续时间: {duration:.1f}秒")
                print("建议采取紧急措施！")
                self.fall_alert_sent = True
            
            if state == 'Sitting':
                if (len(self.sitting_confidence_history) >= 5 and
                    np.mean(self.sitting_confidence_history) > 0.6 and
                    duration >= 8 and not self.sitting_alert_sent):
                    print(f"\n[提示] 检测到稳定久坐状态！持续时间: {duration:.1f}秒")
                    print("建议适当活动，避免久坐！")
                    self.sitting_alert_sent = True
        
        if len(self.states) > self.window_size:
            self.states.pop(0)
            self.confidences.pop(0)
            
    def get_stable_state(self):
        if not self.states:
            return 'No State', 0.0
            
        recent_states = self.states[-3:]
        recent_confs = self.confidences[-3:]
        
        if 'Fall Detected' in recent_states:
            fall_frames = sum(1 for s in recent_states if s == 'Fall Detected')
            fall_confs = [conf for s, conf in zip(recent_states, recent_confs) 
                         if s == 'Fall Detected']
            
            if (fall_frames >= 2 and max(fall_confs) > self.fall_threshold):
                return 'Fall Detected', max(fall_confs)
        
        if recent_states[-1] == 'Sitting':
            if 'Fall Detected' in recent_states:
                return 'Fall Detected', max(recent_confs)
                
        return max(set(self.states), key=self.states.count), np.mean(self.confidences)

def process_roi(roi):
    h, w = roi.shape[:2]
    ratio = 640.0 / max(h, w)
    new_size = (int(w * ratio), int(h * ratio))
    resized = cv.resize(roi, new_size)
    
    square_img = np.zeros((640, 640, 3), dtype=np.uint8)
    y_offset = (640 - new_size[1]) // 2
    x_offset = (640 - new_size[0]) // 2
    square_img[y_offset:y_offset+new_size[1], 
              x_offset:x_offset+new_size[0]] = resized
    
    return square_img

def enhanced_state_detection(frame, pose_keypoints, fall_output):
    try:
        posture_analyzer = PostureAnalyzer()
        pose_features = posture_analyzer.analyze_keypoints(pose_keypoints)
        
        # 处理模型输出
        if isinstance(fall_output, (list, tuple)):
            detections = fall_output[0]  # 获取第一个批次的输出
        else:
            detections = fall_output
            
        if len(detections) == 0:
            print("\n无有效检测结果")
            return 'No Valid Detection', 0.0
            
        # 将张量转移到CPU并转换为numpy数组以便处理
        detections_np = detections.cpu().numpy()
        
        # 使用numpy操作处理检测结果
        conf_threshold = 0.5
        valid_detections = detections_np[detections_np[..., 4] > conf_threshold]
        
        if len(valid_detections) == 0:
            print("\n检测置信度过低")
            return 'Low Confidence Detection', 0.0
            
        # 获取置信度最高的检测结果
        max_conf_idx = np.argmax(valid_detections[..., 4])
        detection = valid_detections[max_conf_idx]
        
        if len(detection) < 8:
            print("\n检测格式无效")
            return 'Invalid Detection Format', 0.0
            
        # 显示原始模型输出结果
        class_scores = detection[5:8]
        fall_score = float(class_scores[0])
        walking_score = float(class_scores[1])
        sitting_score = float(class_scores[2])
        
        print("\n模型原始输出:")
        print(f"Fall检测分数: {fall_score:.3f}")
        print(f"Walking检测分数: {walking_score:.3f}")
        print(f"Sitting检测分数: {sitting_score:.3f}")
        
        # 使用模型输出分数作为主要判断依据
        score_threshold = 0.3
        max_score = max(fall_score, walking_score, sitting_score)
        
        if max_score < score_threshold:
            print("\n模型置信度过低")
            return 'Low Confidence Detection', max_score
            
        # 计算姿态特征
        keypoints_x = pose_keypoints[:, 0]
        keypoints_y = pose_keypoints[:, 1]
        vertical_distribution = np.std(keypoints_y)
        horizontal_distribution = np.std(keypoints_x)
        distribution_ratio = vertical_distribution / horizontal_distribution if horizontal_distribution != 0 else float('inf')
        trunk_angle = np.abs(90 - pose_features['body_angle'])
        
        # 确定状态
        if fall_score >= max(sitting_score, walking_score):
            state = 'Fall Detected'
            confidence = fall_score
            
            if trunk_angle < 30 and distribution_ratio < 0.8:
                confidence *= 1.2
                print("\n姿态特征支持跌倒判断:")
                print(f"- 躯干角度: {trunk_angle:.2f}°")
                print(f"- 分布比率: {distribution_ratio:.2f}")
            
        elif walking_score >= max(fall_score, sitting_score):
            state = 'Walking'
            confidence = walking_score
            
            if pose_features['vertical_angle'] > 75:
                confidence *= 1.1
                
        else:
            state = 'Sitting'
            confidence = sitting_score
            
            if trunk_angle < 30 and distribution_ratio < 0.8:
                confidence *= 0.5
                print("\n检测到跌倒特征，降低坐姿置信度")
                if fall_score > score_threshold:
                    return 'Fall Detected', fall_score * 1.2
        
        print(f"\n最终判断:")
        print(f"状态: {state}")
        print(f"置信度: {confidence:.3f}")
        print("-" * 30)
        
        return state, confidence
        
    except Exception as e:
        print(f"\n状态检测出错: {str(e)}")
        return 'Detection Error', 0.0

# 初始化状态跟踪器
state_tracker = StateTracker(window_size=5)

# ------------------------
# 主处理循环
# ------------------------
print("开始姿态检测和跌倒识别...")
# print("按'q'键退出程序")

while True:
    ret, frame = cap.read()
    if not ret: break

    # 1. 姿态估计预处理
    processed_img = LetterBox([640, 640], auto=True, stride=32)(image=frame)
    processed_img = processed_img[..., ::-1].transpose(2, 0, 1)
    processed_img = np.ascontiguousarray(processed_img)
    model_input = torch.from_numpy(processed_img).to(device).float() / 255
    model_input = model_input.unsqueeze(0)

    # 2. 姿态估计推理
    with torch.no_grad():
        pose_outputs = pose_model(model_input)

    pose_preds = ops.non_max_suppression(
        pose_outputs, conf, iou,
        classes=None,
        nc=pose_model.model[-1].nc,
        max_det=10
    )

    # 3. 关键点有效性检测
    valid_person = False
    fall_roi = None
    valid_kpts = None

    for pred in pose_preds:
        if len(pred) == 0: continue

        pred[:, :4] = ops.scale_boxes(
            model_input.shape[2:],
            pred[:, :4],
            frame.shape
        ).round()

        kpts = ops.scale_coords(
            model_input.shape[2:],
            pred[:, 6:].view(len(pred), *pose_model.kpt_shape),
            frame.shape
        )

        for i, kpt in enumerate(kpts):
            head_conf = any(kpt[idx, 2] > 0.25 for idx in HEAD_KEYPOINTS)
            body_conf = any(kpt[idx, 2] > 0.25 for idx in BODY_KEYPOINTS)
            leg_conf = any(kpt[idx, 2] > 0.25 for idx in LEG_KEYPOINTS)

            if head_conf and body_conf and leg_conf:
                valid_person = True
                x1, y1, x2, y2 = map(int, pred[i, :4])
                x1, y1 = max(x1, 0), max(y1, 0)
                x2, y2 = min(x2, frame.shape[1]), min(y2, frame.shape[0])
                if x2 > x1 and y2 > y1:
                    fall_roi = frame[y1:y2, x1:x2]
                    valid_kpts = kpt.cpu().numpy()
                break
        if valid_person: break

    # 4. 跌倒检测
    if valid_person and fall_roi is not None and valid_kpts is not None:
        try:
            fall_input = process_roi(fall_roi)
            fall_input = cv.cvtColor(fall_input, cv.COLOR_BGR2RGB)
            fall_input = torch.from_numpy(fall_input).permute(2, 0, 1).float() / 255
            fall_input = fall_input.unsqueeze(0).to(device)
            
            with torch.no_grad():
                fall_output = fall_model(fall_input)
                
            # 显示fall模型的原始输出
            print("\n" + "="*50)
            print("Fall模型原始输出:")
            
            # 处理模型输出
            if isinstance(fall_output, (list, tuple)):
                detections = fall_output[0]
            else:
                detections = fall_output
                
            if len(detections) > 0:
                # 将输出重塑为正确的形状
                output_shape = detections.shape
                if len(output_shape) == 3:  # 如果输出是3维的 (batch, anchors, features)
                    detections = detections.reshape(-1, output_shape[-1])
                
                # 获取置信度最高的检测结果
                box_confidences = detections[:, 4]
                max_conf_idx = torch.argmax(box_confidences).item()
                det = detections[max_conf_idx]
                
                # 提取边界框置信度和类别分数
                box_conf = det[4].item()
                class_scores = det[5:8]
                predicted_class = torch.argmax(class_scores).item()
                class_conf = class_scores[predicted_class].item()
                
                print(f"\n最佳检测结果:")
                print(f"边界框置信度: {box_conf:.3f}")
                print(f"类别分数:")
                print(f"- Fall: {class_scores[0].item():.3f}")
                print(f"- Walking: {class_scores[1].item():.3f}")
                print(f"- Sitting: {class_scores[2].item():.3f}")
                print(f"预测类别: {state_labels[predicted_class]}")
                print(f"类别置信度: {class_conf:.3f}")
            else:
                print("没有检测到有效结果")
            print("="*50)
            
            state, confidence = enhanced_state_detection(
                frame, 
                valid_kpts.reshape(-1, 3),
                fall_output
            )
            
            state_tracker.update(state, confidence)
            state, confidence = state_tracker.get_stable_state()
            
        except Exception as e:
            print(f"\n主循环错误: {str(e)}")
            state = 'Error'
            confidence = 0.0
    else:
        state = 'No Valid Person'
        confidence = 0.0

    # 检查退出条件
    if cv.waitKey(1) == ord('q'):
        break

cap.release()
print("\n程序已退出")
