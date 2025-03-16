from flask import Blueprint, request, jsonify, current_app
from app import db
from models.models import HealthRecord, HeightWeight, HealthThreshold, HealthAlert, Notification, BloodPressure, User
from datetime import datetime, timedelta

health_bp = Blueprint('health', __name__)

@health_bp.route('/height-weight', methods=['POST'])
def record_height_weight():
    data = request.json
    user_id = data.get('user_id')
    height = data.get('height')
    weight = data.get('weight')
    recorded_at_str = data.get('recorded_at')  # 新增：接收用户指定的时间

    # 参数校验
    if not user_id or not height or not weight:
        return jsonify({"status": "error", "message": "缺少必要参数（user_id、height、weight）"}), 400
    try:
        # 将 recorded_at 转换为 datetime 对象（格式：YYYY-MM-DD HH:MM:SS）
        recorded_at = datetime.strptime(recorded_at_str, "%Y-%m-%d %H:%M:%S") if recorded_at_str else datetime.utcnow()

        # 创建健康记录
        health_record = HealthRecord(user_id=user_id, recorded_at=recorded_at)
        db.session.add(health_record)
        db.session.flush()

        # 计算 BMI 并保存
        bmi = calculate_bmi(height, weight)
        hw = HeightWeight(
            record_id=health_record.record_id,
            height=height,
            weight=weight,
            bmi=bmi
        )
        db.session.add(hw)

        # 检查阈值并生成警报
        check_threshold_and_alert('bmi', bmi, health_record)

        db.session.commit()
        return jsonify({"status": "success"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500


from sqlalchemy.orm import joinedload  # 新增导入


@health_bp.route('/weight-record', methods=['GET'])
def get_weight_records():
    user_id = request.args.get('user_id')
    days = request.args.get('days', 7)  # 默认7天

    if not user_id:
        return jsonify({"status": "error", "message": "缺少用户ID"}), 400

    try:
        days = int(days)
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
    except ValueError:
        return jsonify({"status": "error", "message": "days 参数格式错误"}), 400

    records = HealthRecord.query \
        .options(joinedload(HealthRecord.height_weight)) \
        .filter(
            HealthRecord.user_id == user_id,
            HealthRecord.recorded_at >= start_date,
            HealthRecord.recorded_at <= end_date
        ) \
        .order_by(HealthRecord.recorded_at.asc()) \
        .all()

    data = {
        "dates": [],
        "bmi_values": []
    }
    for record in records:
        if record.height_weight:
            data["dates"].append(record.recorded_at.strftime('%Y-%m-%d'))
            data["bmi_values"].append(float(record.height_weight.bmi))

    return jsonify({"status": "success", "data": data})


@health_bp.route('/blood-pressure', methods=['POST'])
def record_blood_pressure():
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        systolic = data.get('systolic')
        diastolic = data.get('diastolic')
        recorded_at_str = data.get('recorded_at')

        # 参数校验
        if not (user_id and systolic and diastolic):
            return jsonify({"status": "error", "message": "缺少必要参数"}), 400

        # 数据类型转换
        try:
            systolic = float(systolic)
            diastolic = float(diastolic)
        except ValueError:
            return jsonify({"status": "error", "message": "血压值必须为数值类型"}), 400

        # 处理时间
        recorded_at = datetime.strptime(recorded_at_str, "%Y-%m-%d %H:%M:%S") if recorded_at_str else datetime.utcnow()

        # 创建 HealthRecord
        health_record = HealthRecord(
            user_id=user_id,
            recorded_at=recorded_at
        )
        db.session.add(health_record)
        db.session.flush()  # 确保 record_id 生成

        # 保存血压数据
        bp = BloodPressure(
            record_id=health_record.record_id,
            systolic=systolic,
            diastolic=diastolic
        )
        db.session.add(bp)

        # 检查阈值（调试时可注释该函数）
        # check_threshold_and_alert('blood_pressure_systolic', systolic, health_record)
        # check_threshold_and_alert('blood_pressure_diastolic', diastolic, health_record)

        db.session.commit()
        return jsonify({"status": "success"}), 201

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error recording blood pressure: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@health_bp.route('/alerts', methods=['GET'])
def get_health_alerts():
    user_id = request.args.get('user_id')  # 从查询参数获取用户ID
    if not user_id:
        return jsonify({"status": "error", "message": "缺少用户ID"}), 400

    alerts = HealthAlert.query \
        .filter_by(user_id=user_id) \
        .join(HealthThreshold) \
        .order_by(HealthAlert.sent_at.desc()) \
        .all()

    return jsonify([{
        "alert_id": a.alert_id,
        "metric": a.threshold.metric_type,
        "value": a.actual_value,
        "threshold_min": a.threshold.min_value,
        "threshold_max": a.threshold.max_value,
        "alert_type": a.threshold.alert_type,
        "sent_at": a.sent_at.strftime('%Y-%m-%d %H:%M')
    } for a in alerts])


from datetime import datetime, timedelta

@health_bp.route('/analysis/blood-pressure', methods=['GET'])
def get_blood_pressure_analysis():
    user_id = request.args.get('user_id')
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')

    if not user_id:
        return jsonify({"status": "error", "message": "缺少用户ID"}), 400

    try:
        # 处理日期参数（默认为最近一周）
        end_date = datetime.utcnow()
        if start_date_str:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        else:
            start_date = end_date - timedelta(days=7)
        if end_date_str:
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
    except ValueError:
        return jsonify({"status": "error", "message": "日期格式错误"}), 400

    # 查询指定时间段内的血压数据
    records = HealthRecord.query \
        .options(joinedload(HealthRecord.blood_pressure)) \
        .filter(
            HealthRecord.user_id == user_id,
            HealthRecord.recorded_at >= start_date,
            HealthRecord.recorded_at <= end_date
        ) \
        .order_by(HealthRecord.recorded_at.asc()) \
        .all()

    data = {
        "dates": [],
        "systolic_values": [],
        "diastolic_values": []
    }

    for record in records:
        if record.blood_pressure:
            data["dates"].append(record.recorded_at.strftime('%Y-%m-%d'))
            data["systolic_values"].append(float(record.blood_pressure.systolic))
            data["diastolic_values"].append(float(record.blood_pressure.diastolic))

    return jsonify(data)



def calculate_bmi(height_cm, weight_kg):
    if height_cm is None or weight_kg is None:
        return None
    height_m = height_cm / 100
    return round(weight_kg / (height_m ** 2), 2)

def check_threshold_and_alert(metric_type, value, health_record):
    threshold = HealthThreshold.query \
        .filter_by(metric_type=metric_type) \
        .first()

    if threshold and threshold.min_value is not None and threshold.max_value is not None:
        if (value < threshold.min_value) or (value > threshold.max_value):
            alert = HealthAlert(
                user_id=health_record.user_id,
                record_id=health_record.record_id,
                threshold_id=threshold.threshold_id,
                actual_value=value
            )
            db.session.add(alert)
            send_notification(alert)

def send_notification(alert):
    notification = Notification(
        user_id=alert.user_id,
        record_id=alert.record_id,
        message=f"您的{alert.threshold.metric_type}超出正常范围：{alert.actual_value}",
        type=alert.threshold.alert_type
    )
    db.session.add(notification)


# # 定义检查健康提醒的函数
# def check_health_alerts():
#     with current_app.app_context():  # 确保在 Flask 应用上下文中运行
#         # 获取所有健康阈值配置
#         thresholds = HealthThreshold.query.all()
#
#         for threshold in thresholds:
#             # 查询超出阈值的用户
#             users = User.query.join(HealthRecord) \
#                 .filter(getattr(HealthRecord, threshold.metric_type) > threshold.max_value) \
#                 .all()
#
#             for user in users:
#                 # 获取用户最新的健康记录
#                 latest_health_record = user.latest_health_record
#
#                 # 创建健康提醒
#                 alert = HealthAlert(
#                     user_id=user.user_id,
#                     metric_type=threshold.metric_type,
#                     current_value=getattr(latest_health_record, threshold.metric_type),
#                     suggestions=threshold.suggestions
#                 )
#                 db.session.add(alert)
#
#                 # 创建通知
#                 notification = Notification(
#                     user_id=user.user_id,
#                     type='health',
#                     message=f"{threshold.metric_type}异常: {alert.current_value}",
#                     health_alert=alert
#                 )
#                 db.session.add(notification)
#
#         # 提交数据库会话
#         db.session.commit()
#
# # 初始化定时任务调度器
# scheduler = BackgroundScheduler()
#
# # 添加定时任务，每30分钟执行一次
# scheduler.add_job(check_health_alerts, 'interval', minutes=30)
#
# # 启动定时任务调度器
# scheduler.start()
