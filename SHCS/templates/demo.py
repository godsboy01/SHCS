import torch
import cv2 as cv
import numpy as np
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
                break
        if valid_person: break

    # ------------------------
    # 4. 跌倒检测（解析检测模型输出）
    # ------------------------
    if valid_person and fall_roi is not None:
        try:
            # 预处理（适配模型输入尺寸）
            fall_input = cv.resize(fall_roi, (640, 640))  # 需与fall_model训练尺寸一致
            fall_input = cv.cvtColor(fall_input, cv.COLOR_BGR2RGB)
            fall_input = torch.from_numpy(fall_input).permute(2, 0, 1).float() / 255
            fall_input = fall_input.unsqueeze(0).to(device)

            # 推理
            with torch.no_grad():
                fall_output = fall_model(fall_input)

            # 解析检测结果（假设输出格式为YOLO）
            # 输出格式说明：
            #   - fall_output[0]: 检测结果张量 [batch, anchors, (x, y, w, h, conf, cls1, cls2, cls3)]
            #   - fall_output[1]: 可能为辅助输出（如特征图）
            detections = fall_output[0]

            # 后处理（置信度过滤 + NMS）
            conf_threshold = 0.5
            detections = detections[detections[..., 4] > conf_threshold]  # 筛选置信度
            if len(detections) > 0:
                # 提取类别概率（最后3个维度对应 ['Fall Detected', 'Walking', 'Sitting']）
                cls_probs = detections[..., 5:5 + 3]  # 5: 前5列是(x,y,w,h,conf)
                class_ids = torch.argmax(cls_probs, dim=-1)

                # 取置信度最高的检测结果
                max_conf_idx = torch.argmax(detections[..., 4])
                final_class = class_ids[max_conf_idx].item()
                state = state_labels[final_class]
            else:
                state = 'No Fall Detected'

        except Exception as e:
            print(f"Fall detection error: {str(e)}")
            state = 'Error'
    else:
        state = 'No Valid Person'

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

    text_color = (0, 255, 0) if 'Fall' not in state else (0, 0, 255)
    cv.putText(
        vis_img, f"State: {state}",
        (20, 50), cv.FONT_HERSHEY_SIMPLEX,
        1, text_color, 2, cv.LINE_AA
    )

    cv.imshow('Pose & Fall Detection', vis_img)
    if cv.waitKey(1) == ord('q'):
        break

cap.release()
cv.destroyAllWindows()