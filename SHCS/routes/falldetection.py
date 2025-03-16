# import os
# import queue
#
# from flask import Blueprint, jsonify, current_app
# import cv2
# import numpy as np
# import time
# from threading import Thread, Event
# from queue import Queue, Empty
# from ultralytics import YOLO
# from flask_socketio import emit
# from werkzeug.utils import secure_filename
#
# falldetection_bp = Blueprint('falldetection', __name__)
# # 加载 YOLOv8 模型
# model = YOLO("models/fall.pt")  # 替换为你的模型路径
# # 阈值设置
# FALL_THRESHOLD_TIME = 3  # 跌倒持续时间阈值（秒）
# desired_fps = 10  # 期望的帧率
# delay = 1.0 / desired_fps  # 每帧之间的延迟时间
#
#
#
# # 截图时间点（相对于跌倒开始时间）
# SNAPSHOT_TIMES = [3, 4, 5]
#
# # 存储截图的目录路径
# SNAPSHOT_DIR = "../static/snapshots"
#
# # 创建截图目录（如果不存在）
# os.makedirs(SNAPSHOT_DIR, exist_ok=True)
#
# # 初始化摄像头
# cap = cv2.VideoCapture(0)
#
# # 跌倒检测相关变量
# fall_start_time = None
# is_falling = False
#
# # 前端传回信息
# message_id=1
#
#
# while cap.isOpened():
#     success, frame = cap.read()
#     if not success:
#         break
#
#     # 使用YOLOv8模型对当前帧进行目标检测
#     results = model.predict(source=frame)
#
#     # 获取检测结果中的标签信息
#     labels = [result.boxes.cls for result in results]
#     fall_detected = any(label == 0 for label in labels[0])  # 假设标签0表示跌倒
#
#     # 如果检测到跌倒
#     if fall_detected:
#         if not is_falling:
#             # 记录跌倒开始时间
#             fall_start_time = time.time()
#             is_falling = True
#             snapshots_taken = []
#         else:
#             # 检查跌倒持续时间是否达到截图时间点
#             elapsed_time = time.time() - fall_start_time
#             for snapshot_time in SNAPSHOT_TIMES:
#                 if elapsed_time >= snapshot_time and snapshot_time not in snapshots_taken:
#                     # 截取视频帧并保存
#                     snapshot_filename = f"{message_id}-{len(snapshots_taken)}.jpg"
#                     snapshot_path = os.path.join(SNAPSHOT_DIR, snapshot_filename)
#                     cv2.imwrite(snapshot_path, frame)
#                     print(f"已保存截图: {snapshot_path}")
#                     snapshots_taken.append(snapshot_time)
#
#                     # 如果已经截取了所有需要的帧，可以提前结束循环或继续监控
#                     if len(snapshots_taken) == len(SNAPSHOT_TIMES):
#                         break
#     else:
#         # 如果没有检测到跌倒，重置跌倒状态
#         is_falling = False
#         fall_start_time = None
#
#     # 如果已经截取了所有需要的帧，可以提前结束循环
#     if len(snapshots_taken) == len(SNAPSHOT_TIMES):
#         break
#
# cap.release()  # 释放摄像头资源
# print("程序结束")
#
