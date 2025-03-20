import cv2
import numpy as np
import time
from ultralytics import YOLO

# ====================
# 配置参数
# ====================
# 模型路径
DETECT_MODEL_PATH = "models/fall.pt"  # 您的三分类模型
POSE_MODEL_PATH = "models/yolov8n-pose.pt"  # 官方姿态模型

# 检测参数
CONF_THRESH = 0.6  # 检测置信度阈值
IOU_THRESH = 0.45  # NMS阈值

# 姿态参数
POSE_CONF = 0.5  # 姿态关键点置信度阈值

# 显示设置
FONT = cv2.FONT_HERSHEY_SIMPLEX
COLORS = {
    "Fall": (0, 0, 255),  # 红色
    "Sit": (0, 255, 255),  # 黄色
    "Stand": (0, 255, 0)  # 绿色
}

# ====================
# 工具函数
# ====================
def calculate_torso_angle(kpts):
    """计算躯干倾斜角度（基于髋部和肩部）"""
    try:
        # 关键点索引（COCO格式）
        left_shoulder = kpts[5]
        right_shoulder = kpts[6]
        left_hip = kpts[11]
        right_hip = kpts[12]

        # 计算躯干中线
        shoulder_center = (left_shoulder + right_shoulder) / 2
        hip_center = (left_hip + right_hip) / 2

        # 计算角度（相对于垂直轴）
        dx = hip_center[0] - shoulder_center[0]
        dy = hip_center[1] - shoulder_center[1]
        angle = np.degrees(np.arctan2(dx, dy))

        return abs(angle)
    except:
        return 90  # 默认直立角度

# ====================
# 主程序
# ====================
def main():
    # 初始化模型
    detect_model = YOLO(DETECT_MODEL_PATH)
    pose_model = YOLO(POSE_MODEL_PATH)

    # 初始化摄像头
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    # 状态变量
    fps = 0
    last_time = time.time()

    while cap.isOpened():
        # 读取帧
        success, frame = cap.read()
        if not success:
            print("摄像头读取失败")
            break

        # 执行检测
        detect_results = detect_model(frame,
                                    conf=CONF_THRESH,
                                    iou=IOU_THRESH,
                                    verbose=False)[0]

        # 处理每个检测结果
        for box in detect_results.boxes:
            cls_id = int(box.cls)
            conf = float(box.conf)
            label = detect_model.names[cls_id]
            x1, y1, x2, y2 = map(int, box.xyxy[0])

            # 仅处理目标类别（Stand/Sit/Fall）
            if label not in ["Stand", "Sit", "Fall"]:
                continue

            # 截取ROI区域
            roi = frame[y1:y2, x1:x2]
            if roi.size == 0:
                continue

            # 执行姿态估计
            pose_results = pose_model(roi,
                                    conf=POSE_CONF,
                                    verbose=False)[0]

            if pose_results.keypoints is None:
                continue

            # 获取关键点并转换坐标
            kpts = pose_results.keypoints.xy[0].cpu().numpy()
            kpts[:, 0] += x1  # X坐标偏移
            kpts[:, 1] += y1  # Y坐标偏移

            # 计算躯干角度
            angle = calculate_torso_angle(kpts)

            # 绘制边界框
            color = COLORS.get(label, (255, 255, 255))
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

            # 绘制关键点
            for x, y in kpts:
                cv2.circle(frame, (int(x), int(y)), 3, (0, 150, 255), -1)

            # 显示标签和置信度
            label_text = f"{label} {conf:.2f}"
            cv2.putText(frame, label_text, (x1, y1 - 10), FONT, 0.7, color, 2)

            # 显示躯干角度
            angle_text = f"Angle: {angle:.1f}°"
            cv2.putText(frame, angle_text, (x1, y2 + 20), FONT, 0.6, (255, 0, 0), 2)

        # 计算FPS
        current_time = time.time()
        fps = 1 / (current_time - last_time)
        last_time = current_time

        # 显示FPS
        cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30), FONT, 0.7, (0, 255, 0), 2)

        # 显示画面
        cv2.imshow("Fall Detection Demo", frame)

        # 退出按键（Q键）
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # 释放资源
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()