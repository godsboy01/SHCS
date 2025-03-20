import torch
import cv2 as cv
import numpy as np
import time  # 添加time模块
from ultralytics.data.augment import LetterBox
from ultralytics.utils import ops
from ultralytics.engine.results import Results

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
    print("Error: Could not open camera.")
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
# 状态标签定义（需与fall_model的names顺序一致）
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
        # 关键点索引定义
        self.HEAD_KEYPOINTS = [0, 1, 2, 3, 4]  # 头部关键点
        self.BODY_KEYPOINTS = [5, 6, 11, 12]   # 身体关键点
        self.LEG_KEYPOINTS = [13, 14, 15, 16]  # 腿部关键点
        
        # 状态判断阈值
        self.height_ratio_threshold = 0.6  # 高宽比阈值
        self.angle_threshold = 65          # 调整角度阈值
        
    def analyze_keypoints(self, keypoints):
        """分析关键点空间关系"""
        # 获取各部位的平均位置
        head_center = np.mean(keypoints[self.HEAD_KEYPOINTS], axis=0)
        body_center = np.mean(keypoints[self.BODY_KEYPOINTS], axis=0)
        leg_center = np.mean(keypoints[self.LEG_KEYPOINTS], axis=0)
        
        # 计算身体特征
        height = head_center[1] - leg_center[1]  # 总高度
        width = np.max(keypoints[:, 0]) - np.min(keypoints[:, 0])  # 总宽度
        height_width_ratio = height / width if width != 0 else 0
        
        # 计算身体倾斜角度
        body_angle = np.abs(np.degrees(np.arctan2(
            body_center[1] - head_center[1],
            body_center[0] - head_center[0]
        )))
        
        # 添加新的特征计算
        head_foot_horizontal = abs(head_center[0] - leg_center[0])
        vertical_angle = 90 - body_angle
        
        # 计算关节点的排列方向特征
        # 计算主要关键点的垂直和水平分布
        key_points = np.vstack([
            head_center,
            body_center,
            leg_center
        ])
        
        # 计算关键点的垂直和水平分散度
        vertical_spread = np.std(key_points[:, 1])
        horizontal_spread = np.std(key_points[:, 0])
        
        # 计算垂直-水平比率（值大于1表示更偏向垂直排列）
        vertical_horizontal_ratio = vertical_spread / horizontal_spread if horizontal_spread != 0 else float('inf')
        
        # 添加新的特征：头部相对于身体的高度变化率
        head_body_height_ratio = (head_center[1] - body_center[1]) / (
                                body_center[1] - leg_center[1]) if (body_center[1] - leg_center[1]) != 0 else 0
        
        # 添加新的特征：身体的压缩率
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
            'horizontal_spread': horizontal_spread
        }

class StateTracker:
    def __init__(self, window_size=5):
        self.states = []
        self.confidences = []
        self.window_size = window_size
        self.fall_threshold = 0.7
        # 添加时间跟踪
        self.current_state_start_time = None
        self.last_state = None
        self.fall_alert_sent = False
        self.sitting_alert_sent = False
        
    def update(self, state, confidence):
        self.states.append(state)
        self.confidences.append(confidence)
        
        # 状态改变时更新时间
        if state != self.last_state:
            self.current_state_start_time = time.time()
            self.fall_alert_sent = False
            self.sitting_alert_sent = False
            if state != 'No Valid Person':
                print(f"\n状态变化: {state} (置信度: {confidence:.2f})")
        
        self.last_state = state
        
        # 检查持续时间
        if self.current_state_start_time is not None:
            duration = time.time() - self.current_state_start_time
            
            # 跌倒检测
            if state == 'Fall Detected' and duration >= 3 and not self.fall_alert_sent:
                print(f"\n[警告] 检测到持续跌倒状态！持续时间: {duration:.1f}秒")
                print("建议采取紧急措施！")
                self.fall_alert_sent = True
            
            # 久坐检测
            if state == 'Sitting' and duration >= 8 and not self.sitting_alert_sent:
                print(f"\n[提示] 检测到久坐状态！持续时间: {duration:.1f}秒")
                print("建议适当活动，避免久坐！")
                self.sitting_alert_sent = True
        
        if len(self.states) > self.window_size:
            self.states.pop(0)
            self.confidences.pop(0)
            
    def get_stable_state(self):
        if not self.states:
            return 'No State', 0.0
            
        # 计算加权投票
        recent_states = self.states[-3:]  # 最近3帧
        recent_confs = self.confidences[-3:]
        
        # 跌倒检测的特殊处理
        if 'Fall Detected' in recent_states:
            fall_frames = sum(1 for s in recent_states if s == 'Fall Detected')
            fall_confs = [conf for s, conf in zip(recent_states, recent_confs) 
                         if s == 'Fall Detected']
            
            # 更严格的跌倒确认条件
            if (fall_frames >= 2 and  # 至少2帧检测到跌倒
                max(fall_confs) > self.fall_threshold):  # 置信度要足够高
                return 'Fall Detected', max(fall_confs)
        
        # 如果最近的状态是坐姿，需要额外确认
        if recent_states[-1] == 'Sitting':
            if 'Fall Detected' in recent_states:
                # 如果最近有跌倒检测，倾向于判断为跌倒
                return 'Fall Detected', max(recent_confs)
                
        return max(set(self.states), key=self.states.count), np.mean(self.confidences)
    
def process_roi(roi):
    # 保持长宽比
    h, w = roi.shape[:2]
    ratio = 640.0 / max(h, w)
    new_size = (int(w * ratio), int(h * ratio))
    resized = cv.resize(roi, new_size)
    
    # 创建640x640的画布
    square_img = np.zeros((640, 640, 3), dtype=np.uint8)
    # 将图像放在中心
    y_offset = (640 - new_size[1]) // 2
    x_offset = (640 - new_size[0]) // 2
    square_img[y_offset:y_offset+new_size[1], 
              x_offset:x_offset+new_size[0]] = resized
    
    return square_img
def enhanced_state_detection(frame, pose_keypoints, fall_output):
    """增强的状态检测"""
    try:
        # 1. 初始化姿态分析器
        posture_analyzer = PostureAnalyzer()
        
        # 2. 分析姿态特征
        pose_features = posture_analyzer.analyze_keypoints(pose_keypoints)
        
        # 计算图像宽度
        keypoints_x = pose_keypoints[:, 0]
        width = np.max(keypoints_x) - np.min(keypoints_x)
        
        # 3. 获取跌倒检测模型的输出
        if isinstance(fall_output, (list, tuple)):
            detections = fall_output[0]
        else:
            detections = fall_output
            
        if len(detections) == 0:
            print("\n无有效检测结果")
            return 'No Valid Detection', 0.0
            
        # 获取置信度大于阈值的检测
        conf_threshold = 0.5
        valid_detections = detections[detections[..., 4] > conf_threshold]
        
        if len(valid_detections) == 0:
            print("\n检测置信度过低")
            return 'Low Confidence Detection', 0.0
            
        # 获取最高置信度的检测结果
        max_conf_idx = torch.argmax(valid_detections[..., 4])
        detection = valid_detections[max_conf_idx]
        
        if len(detection) < 8:
            print("\n检测格式无效")
            return 'Invalid Detection Format', 0.0
            
        # 获取类别分数
        class_scores = detection[5:8]
        predicted_class = torch.argmax(class_scores).item()
        confidence = class_scores[predicted_class].item()
        
        # 4. 综合判断逻辑
        state = state_labels[predicted_class]
        
        print(f"\n判断过程:")
        print(f"初始状态: {state}")
        print(f"初始置信度: {confidence:.2f}")
        print(f"姿态特征:")
        print(f"- 高宽比: {pose_features['height_width_ratio']:.2f}")
        print(f"- 身体角度: {pose_features['body_angle']:.2f}°")
        print(f"- 垂直角度: {pose_features['vertical_angle']:.2f}°")
        print(f"- 头部水平位移: {pose_features['head_foot_horizontal']:.2f}")
        print(f"- 垂直-水平比率: {pose_features['vertical_horizontal_ratio']:.2f}")
        
        # 改进的状态判断逻辑
        if predicted_class == 0:  # Fall Detected
            horizontal_threshold = width * 0.3
            
            if (pose_features['height_width_ratio'] < 0.6 and
                pose_features['body_angle'] > 65 and
                pose_features['head_foot_horizontal'] > horizontal_threshold and
                pose_features['vertical_angle'] < 30 and
                pose_features['body_compression'] < 0.8 and
                pose_features['head_body_height_ratio'] > 1.2 and
                pose_features['vertical_horizontal_ratio'] < 0.8):  # 更偏向水平排列
                confidence *= 1.8
                print("\n跌倒特征符合:")
                print("- 高宽比低于0.6")
                print("- 身体角度大于65度")
                print("- 头部水平位移显著")
                print("- 垂直角度小于30度")
                print("- 关节点呈水平排列")
                if pose_features['body_angle'] > 80:
                    confidence *= 1.3
                    print("- 身体角度大于80度，进一步提高置信度")
            else:
                confidence *= 0.4
                print("\n跌倒特征不完全符合，降低置信度")
                
        elif predicted_class == 1:  # Walking
            if (pose_features['height_width_ratio'] > 1.2 and
                pose_features['vertical_angle'] > 75 and
                pose_features['head_foot_horizontal'] < width * 0.2 and
                pose_features['vertical_horizontal_ratio'] > 1.5):  # 明显的垂直排列
                confidence *= 1.2
                print("\n行走特征符合:")
                print("- 高宽比大于1.2")
                print("- 垂直角度大于75度")
                print("- 头部水平位移较小")
                print("- 关节点呈垂直排列")
            else:
                confidence *= 0.8
                print("\n行走特征不完全符合，略微降低置信度")
                
        elif predicted_class == 2:  # Sitting
            leg_body_ratio = (pose_features['leg_height'] - 
                            pose_features['body_height']) / (
                            pose_features['body_height'] - 
                            pose_features['head_height'])
            
            # 加强对坐姿的判断要求
            if (0.8 < pose_features['height_width_ratio'] < 1.4 and
                leg_body_ratio < 0.5 and
                pose_features['vertical_angle'] > 70 and
                pose_features['head_foot_horizontal'] < width * 0.25 and
                pose_features['vertical_horizontal_ratio'] > 1.2):  # 要求关节点保持一定的垂直排列
                confidence *= 1.2
                print("\n坐姿特征符合:")
                print("- 高宽比在0.8-1.4之间")
                print("- 腿身比例小于0.5")
                print("- 垂直角度大于70度")
                print("- 头部水平位移适中")
                print("- 关节点保持垂直排列")
            else:
                confidence *= 0.5  # 更大幅度降低不符合条件的坐姿置信度
                print("\n坐姿特征不完全符合，显著降低置信度")
        
        print(f"\n最终置信度: {confidence:.2f}")
        
        # 5. 置信度阈值判断
        if confidence < 0.3:
            return 'Low Confidence Detection', confidence
        
        # 6. 添加状态稳定性检查
        if state == 'Fall Detected' and confidence > 0.6:
            return 'Fall Detected (High Confidence)', confidence
        
        return state, confidence
        
    except Exception as e:
        print(f"\n状态检测出错: {str(e)}")
        return 'Detection Error', 0.0

# 在主循环之前初始化状态跟踪器
state_tracker = StateTracker(window_size=5)

# ------------------------
# 主处理循环
# ------------------------
while True:
    ret, frame = cap.read()
    if not ret: break

    orig_img = frame.copy()
    state = 'No Valid Person'  # 默认状态

    # ------------------------
    # 1. 姿态估计预处理
    # ------------------------
    processed_img = LetterBox([640, 640], auto=True, stride=32)(image=orig_img)
    processed_img = processed_img[..., ::-1].transpose(2, 0, 1)
    processed_img = np.ascontiguousarray(processed_img)
    model_input = torch.from_numpy(processed_img).to(device).float() / 255
    model_input = model_input.unsqueeze(0)

    # ------------------------
    # 2. 姿态估计推理
    # ------------------------
    with torch.no_grad():
        pose_outputs = pose_model(model_input)

    # 后处理 (NMS)
    pose_preds = ops.non_max_suppression(
        pose_outputs, conf, iou,
        classes=None,
        nc=pose_model.model[-1].nc,
        max_det=10
    )

    # ------------------------
    # 3. 关键点有效性检测
    # ------------------------
    valid_person = False
    fall_roi = None
    valid_kpts = None  # 添加这行来保存有效的关键点

    for pred in pose_preds:
        if len(pred) == 0: continue

        pred[:, :4] = ops.scale_boxes(
            model_input.shape[2:],
            pred[:, :4],
            orig_img.shape
        ).round()

        kpts = ops.scale_coords(
            model_input.shape[2:],
            pred[:, 6:].view(len(pred), *pose_model.kpt_shape),
            orig_img.shape
        )

        for i, kpt in enumerate(kpts):
            head_conf = any(kpt[idx, 2] > 0.25 for idx in HEAD_KEYPOINTS)
            body_conf = any(kpt[idx, 2] > 0.25 for idx in BODY_KEYPOINTS)
            leg_conf = any(kpt[idx, 2] > 0.25 for idx in LEG_KEYPOINTS)

            if head_conf and body_conf and leg_conf:
                valid_person = True
                x1, y1, x2, y2 = map(int, pred[i, :4])
                x1, y1 = max(x1, 0), max(y1, 0)
                x2, y2 = min(x2, orig_img.shape[1]), min(y2, orig_img.shape[0])
                if x2 > x1 and y2 > y1:
                    fall_roi = orig_img[y1:y2, x1:x2]
                    valid_kpts = kpt.cpu().numpy()  # 保存有效的关键点数据
                break
        if valid_person: break

    # ------------------------
    # 4. 跌倒检测（解析检测模型输出）
    # ------------------------
    if valid_person and fall_roi is not None and valid_kpts is not None:
        try:
            # 改进ROI处理
            fall_input = process_roi(fall_roi)
            fall_input = cv.cvtColor(fall_input, cv.COLOR_BGR2RGB)
            fall_input = torch.from_numpy(fall_input).permute(2, 0, 1).float() / 255
            fall_input = fall_input.unsqueeze(0).to(device)
            
            with torch.no_grad():
                fall_output = fall_model(fall_input)
            
            state, confidence = enhanced_state_detection(
                frame, 
                valid_kpts.reshape(-1, 3),
                fall_output
            )
            
            # 使用状态跟踪器
            state_tracker.update(state, confidence)
            state, confidence = state_tracker.get_stable_state()
            
        except Exception as e:
            print(f"Error in main loop: {str(e)}")
            state = 'Error'
            confidence = 0.0
    else:
        state = 'No Valid Person'
        confidence = 0.0

    # ------------------------
    # 5. 可视化渲染
    # ------------------------
    results = Results(
        orig_img=orig_img,
        path=None,
        names=pose_model.names,
        boxes=pose_preds[0][:, :6] if len(pose_preds[0]) else None,
        keypoints=kpts if len(pose_preds[0]) else None
    )
    vis_img = results.plot(conf=True, boxes=True, labels=True, line_width=2)

    # 添加状态显示
    text_color = (0, 255, 0) if 'Fall' not in state else (0, 0, 255)
    status_text = f"State: {state}"
    if state not in ['No Valid Person', 'Error', 'Detection Error']:
        status_text += f" ({confidence:.2f})"

    cv.putText(
        vis_img,
        status_text,
        (20, 50),
        cv.FONT_HERSHEY_SIMPLEX,
        1,
        text_color,
        2,
        cv.LINE_AA
    )

    cv.imshow('Pose & Fall Detection', vis_img)
    if cv.waitKey(1) == ord('q'):
        break

cap.release()
cv.destroyAllWindows()