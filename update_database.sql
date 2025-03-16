SET FOREIGN_KEY_CHECKS = 0;

-- 删除原有的相关表
DROP TABLE IF EXISTS `notifications`;
DROP TABLE IF EXISTS `fall_detection_records`;
DROP TABLE IF EXISTS `devices`;
DROP TABLE IF EXISTS `health_data`;
DROP TABLE IF EXISTS `health_records`;
DROP TABLE IF EXISTS `blood_pressure`;
DROP TABLE IF EXISTS `heart_rate`;
DROP TABLE IF EXISTS `height_weight`;
DROP TABLE IF EXISTS `temperature`;
DROP TABLE IF EXISTS `health_alerts`;
DROP TABLE IF EXISTS `health_thresholds`;
DROP TABLE IF EXISTS `users`;
DROP TABLE IF EXISTS `families`;

-- 创建新的用户表
CREATE TABLE `users` (
  `user_id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL COMMENT '用户名',
  `password` varchar(255) NOT NULL COMMENT '密码',
  `role` enum('admin', 'guardian', 'elderly') NOT NULL COMMENT '用户角色：管理员/监护人/被监护人',
  `name` varchar(50) NOT NULL COMMENT '真实姓名',
  `phone` varchar(15) NOT NULL COMMENT '联系电话',
  `email` varchar(100) COMMENT '邮箱',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `avatar` varchar(255) COMMENT '头像',
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `uk_username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- 创建监护关系表
CREATE TABLE `care_relationships` (
  `relationship_id` int(11) NOT NULL AUTO_INCREMENT,
  `guardian_id` int(11) NOT NULL COMMENT '监护人ID',
  `elderly_id` int(11) NOT NULL COMMENT '被监护人ID',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`relationship_id`),
  UNIQUE KEY `uk_guardian_elderly` (`guardian_id`, `elderly_id`),
  FOREIGN KEY (`guardian_id`) REFERENCES `users` (`user_id`),
  FOREIGN KEY (`elderly_id`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='监护关系表';

-- 创建设备表
CREATE TABLE `devices` (
  `device_id` int(11) NOT NULL AUTO_INCREMENT,
  `elderly_id` int(11) NOT NULL COMMENT '被监护人ID',
  `device_name` varchar(100) COMMENT '设备名称',
  `device_type` enum('camera', 'sensor') NOT NULL COMMENT '设备类型',
  `ip_address` varchar(15) NOT NULL COMMENT 'IP地址',
  `location` varchar(255) DEFAULT '未知位置' COMMENT '设备位置',
  `status` enum('active', 'inactive') DEFAULT 'active' COMMENT '设备状态',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`device_id`),
  FOREIGN KEY (`elderly_id`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='设备表';

-- 创建跌倒检测记录表
CREATE TABLE `fall_detection_records` (
  `record_id` int(11) NOT NULL AUTO_INCREMENT,
  `elderly_id` int(11) NOT NULL COMMENT '被监护人ID',
  `device_id` int(11) NOT NULL COMMENT '检测设备ID',
  `detection_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '检测时间',
  `detection_type` enum('Fall', 'Normal') NOT NULL COMMENT '检测类型',
  `confidence` float COMMENT '置信度',
  `video_frame_path` varchar(255) COMMENT '视频帧路径',
  `is_notified` tinyint(1) DEFAULT 0 COMMENT '是否已通知',
  PRIMARY KEY (`record_id`),
  INDEX `idx_elderly_time` (`elderly_id`, `detection_time`),
  FOREIGN KEY (`elderly_id`) REFERENCES `users` (`user_id`),
  FOREIGN KEY (`device_id`) REFERENCES `devices` (`device_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='跌倒检测记录表';

-- 创建久坐记录表
CREATE TABLE `sitting_records` (
  `record_id` int(11) NOT NULL AUTO_INCREMENT,
  `elderly_id` int(11) NOT NULL COMMENT '被监护人ID',
  `device_id` int(11) NOT NULL COMMENT '检测设备ID',
  `start_time` datetime NOT NULL COMMENT '开始时间',
  `end_time` datetime COMMENT '结束时间',
  `duration` int COMMENT '持续时间(分钟)',
  `is_notified` tinyint(1) DEFAULT 0 COMMENT '是否已提醒',
  PRIMARY KEY (`record_id`),
  INDEX `idx_elderly_time` (`elderly_id`, `start_time`),
  FOREIGN KEY (`elderly_id`) REFERENCES `users` (`user_id`),
  FOREIGN KEY (`device_id`) REFERENCES `devices` (`device_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='久坐记录表';

-- 创建健康数据记录表
CREATE TABLE `health_records` (
  `record_id` int(11) NOT NULL AUTO_INCREMENT,
  `elderly_id` int(11) NOT NULL COMMENT '被监护人ID',
  `height` decimal(5,2) COMMENT '身高(cm)',
  `weight` decimal(5,2) COMMENT '体重(kg)',
  `bmi` decimal(4,2) COMMENT 'BMI指数',
  `systolic_pressure` int COMMENT '收缩压',
  `diastolic_pressure` int COMMENT '舒张压',
  `heart_rate` int COMMENT '心率',
  `temperature` decimal(3,1) COMMENT '体温',
  `recorded_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '记录时间',
  PRIMARY KEY (`record_id`),
  INDEX `idx_elderly_time` (`elderly_id`, `recorded_at`),
  FOREIGN KEY (`elderly_id`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='健康数据记录表';

-- 创建健康预警阈值表
CREATE TABLE `health_thresholds` (
  `threshold_id` int(11) NOT NULL AUTO_INCREMENT,
  `elderly_id` int(11) NOT NULL COMMENT '被监护人ID',
  `metric_type` enum('bmi', 'blood_pressure', 'heart_rate', 'temperature', 'sitting_duration') NOT NULL COMMENT '指标类型',
  `min_value` decimal(5,2) COMMENT '最小值',
  `max_value` decimal(5,2) COMMENT '最大值',
  `warning_level` enum('normal', 'warning', 'danger') NOT NULL DEFAULT 'normal' COMMENT '警告级别',
  PRIMARY KEY (`threshold_id`),
  UNIQUE KEY `uk_elderly_metric` (`elderly_id`, `metric_type`),
  FOREIGN KEY (`elderly_id`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='健康预警阈值表';

-- 创建通知表
CREATE TABLE `notifications` (
  `notification_id` int(11) NOT NULL AUTO_INCREMENT,
  `elderly_id` int(11) NOT NULL COMMENT '被监护人ID',
  `guardian_id` int(11) NOT NULL COMMENT '通知接收的监护人ID',
  `title` varchar(100) NOT NULL COMMENT '通知标题',
  `message` text NOT NULL COMMENT '通知内容',
  `type` enum('fall', 'sitting', 'health') NOT NULL COMMENT '通知类型',
  `level` enum('info', 'warning', 'danger') NOT NULL COMMENT '通知级别',
  `source_type` enum('fall_detection', 'sitting_record', 'health_record') NOT NULL COMMENT '来源类型',
  `source_id` int NOT NULL COMMENT '来源记录ID',
  `is_read` tinyint(1) DEFAULT 0 COMMENT '是否已读',
  `read_at` datetime DEFAULT NULL COMMENT '阅读时间',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `thumbnail` varchar(255) DEFAULT NULL COMMENT '缩略图（跌倒检测时的图片）',
  PRIMARY KEY (`notification_id`),
  INDEX `idx_guardian_read` (`guardian_id`, `is_read`),
  INDEX `idx_guardian_time` (`guardian_id`, `created_at`),
  INDEX `idx_source` (`source_type`, `source_id`),
  FOREIGN KEY (`elderly_id`) REFERENCES `users` (`user_id`),
  FOREIGN KEY (`guardian_id`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='通知表';

-- 创建通知详情表
CREATE TABLE `notification_details` (
  `detail_id` int(11) NOT NULL AUTO_INCREMENT,
  `notification_id` int(11) NOT NULL COMMENT '通知ID',
  `detail_type` varchar(50) NOT NULL COMMENT '详情类型',
  `detail_key` varchar(50) NOT NULL COMMENT '详情键',
  `detail_value` text COMMENT '详情值',
  PRIMARY KEY (`detail_id`),
  INDEX `idx_notification` (`notification_id`),
  FOREIGN KEY (`notification_id`) REFERENCES `notifications` (`notification_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='通知详情表';

-- 创建通知阅读状态表
CREATE TABLE `notification_read_status` (
  `status_id` int(11) NOT NULL AUTO_INCREMENT,
  `notification_id` int(11) NOT NULL COMMENT '通知ID',
  `guardian_id` int(11) NOT NULL COMMENT '监护人ID',
  `is_read` tinyint(1) DEFAULT 0 COMMENT '是否已读',
  `read_at` datetime DEFAULT NULL COMMENT '阅读时间',
  PRIMARY KEY (`status_id`),
  UNIQUE KEY `uk_notification_guardian` (`notification_id`, `guardian_id`),
  FOREIGN KEY (`notification_id`) REFERENCES `notifications` (`notification_id`) ON DELETE CASCADE,
  FOREIGN KEY (`guardian_id`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='通知阅读状态表';

SET FOREIGN_KEY_CHECKS = 1; 