/*
 Navicat Premium Data Transfer

 Source Server         : localhost_3306
 Source Server Type    : MySQL
 Source Server Version : 50719 (5.7.19)
 Source Host           : localhost:3306
 Source Schema         : smart_home_care

 Target Server Type    : MySQL
 Target Server Version : 50719 (5.7.19)
 File Encoding         : 65001

 Date: 17/03/2025 23:10:09
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for care_relationships
-- ----------------------------
DROP TABLE IF EXISTS `care_relationships`;
CREATE TABLE `care_relationships`  (
  `relationship_id` int(11) NOT NULL AUTO_INCREMENT,
  `guardian_id` int(11) NOT NULL COMMENT '???ID',
  `elderly_id` int(11) NOT NULL COMMENT '????ID',
  `created_at` datetime NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`relationship_id`) USING BTREE,
  UNIQUE INDEX `uk_guardian_elderly`(`guardian_id`, `elderly_id`) USING BTREE,
  INDEX `elderly_id`(`elderly_id`) USING BTREE,
  CONSTRAINT `care_relationships_ibfk_1` FOREIGN KEY (`guardian_id`) REFERENCES `users` (`user_id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `care_relationships_ibfk_2` FOREIGN KEY (`elderly_id`) REFERENCES `users` (`user_id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '?????' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for device_status_history
-- ----------------------------
DROP TABLE IF EXISTS `device_status_history`;
CREATE TABLE `device_status_history`  (
  `history_id` int(11) NOT NULL AUTO_INCREMENT,
  `device_id` int(11) NOT NULL COMMENT '设备ID',
  `status` enum('online','offline','error') CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '设备状态',
  `status_change_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '状态变更时间',
  `error_message` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL COMMENT '错误信息',
  PRIMARY KEY (`history_id`) USING BTREE,
  INDEX `idx_device_time`(`device_id`, `status_change_time`) USING BTREE,
  CONSTRAINT `fk_device_status_history` FOREIGN KEY (`device_id`) REFERENCES `devices` (`device_id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '设备状态历史' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for devices
-- ----------------------------
DROP TABLE IF EXISTS `devices`;
CREATE TABLE `devices`  (
  `device_id` int(11) NOT NULL AUTO_INCREMENT,
  `elderly_id` int(11) NOT NULL COMMENT '????ID',
  `device_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `device_type` enum('camera','weight_scale','blood_pressure','other') CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `ip_address` varchar(15) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT 'IP??',
  `location` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '????' COMMENT '????',
  `status` enum('online','offline') CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT 'offline',
  `created_at` datetime NULL DEFAULT CURRENT_TIMESTAMP,
  `last_active` datetime NULL DEFAULT NULL,
  `user_id` int(11) NULL DEFAULT NULL,
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  PRIMARY KEY (`device_id`) USING BTREE,
  INDEX `elderly_id`(`elderly_id`) USING BTREE,
  INDEX `idx_device_id`(`device_id`) USING BTREE,
  INDEX `user_id`(`user_id`) USING BTREE,
  CONSTRAINT `devices_ibfk_1` FOREIGN KEY (`elderly_id`) REFERENCES `users` (`user_id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `devices_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 8 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '???' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for fall_detection_records
-- ----------------------------
DROP TABLE IF EXISTS `fall_detection_records`;
CREATE TABLE `fall_detection_records`  (
  `record_id` int(11) NOT NULL AUTO_INCREMENT,
  `elderly_id` int(11) NOT NULL COMMENT '????ID',
  `device_id` int(11) NOT NULL COMMENT '????ID',
  `detection_time` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '????',
  `detection_type` enum('Fall','Normal','Sitting') CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '检测类型',
  `confidence` float NULL DEFAULT NULL COMMENT '???',
  `video_frame_path` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '?????',
  `is_notified` tinyint(1) NULL DEFAULT 0 COMMENT '?????',
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '状态',
  `processed` tinyint(1) NULL DEFAULT 0 COMMENT '是否已处理',
  `processed_at` datetime NULL DEFAULT NULL COMMENT '处理时间',
  PRIMARY KEY (`record_id`) USING BTREE,
  INDEX `idx_elderly_time`(`elderly_id`, `detection_time`) USING BTREE,
  INDEX `device_id`(`device_id`) USING BTREE,
  CONSTRAINT `fall_detection_records_ibfk_1` FOREIGN KEY (`elderly_id`) REFERENCES `users` (`user_id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `fall_detection_records_ibfk_2` FOREIGN KEY (`device_id`) REFERENCES `devices` (`device_id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '???????' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for families
-- ----------------------------
DROP TABLE IF EXISTS `families`;
CREATE TABLE `families`  (
  `family_id` int(11) NOT NULL AUTO_INCREMENT,
  `family_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `family_address` varchar(256) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `address` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  PRIMARY KEY (`family_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 6 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for health_records
-- ----------------------------
DROP TABLE IF EXISTS `health_records`;
CREATE TABLE `health_records`  (
  `record_id` int(11) NOT NULL AUTO_INCREMENT,
  `elderly_id` int(11) NOT NULL COMMENT '????ID',
  `height` decimal(5, 2) NULL DEFAULT NULL COMMENT '??(cm)',
  `weight` decimal(5, 2) NULL DEFAULT NULL COMMENT '??(kg)',
  `bmi` decimal(4, 2) NULL DEFAULT NULL COMMENT 'BMI??',
  `systolic_pressure` int(11) NULL DEFAULT NULL COMMENT '???',
  `diastolic_pressure` int(11) NULL DEFAULT NULL COMMENT '???',
  `heart_rate` int(11) NULL DEFAULT NULL COMMENT '??',
  `temperature` decimal(3, 1) NULL DEFAULT NULL COMMENT '??',
  `recorded_at` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '????',
  PRIMARY KEY (`record_id`) USING BTREE,
  INDEX `idx_elderly_time`(`elderly_id`, `recorded_at`) USING BTREE,
  CONSTRAINT `health_records_ibfk_1` FOREIGN KEY (`elderly_id`) REFERENCES `users` (`user_id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '???????' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for health_thresholds
-- ----------------------------
DROP TABLE IF EXISTS `health_thresholds`;
CREATE TABLE `health_thresholds`  (
  `threshold_id` int(11) NOT NULL AUTO_INCREMENT,
  `elderly_id` int(11) NOT NULL COMMENT '????ID',
  `metric_type` enum('bmi','blood_pressure','heart_rate','temperature','sitting_duration') CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '????',
  `min_value` decimal(5, 2) NULL DEFAULT NULL COMMENT '???',
  `max_value` decimal(5, 2) NULL DEFAULT NULL COMMENT '???',
  `warning_level` enum('normal','warning','danger') CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT 'normal' COMMENT '????',
  PRIMARY KEY (`threshold_id`) USING BTREE,
  UNIQUE INDEX `uk_elderly_metric`(`elderly_id`, `metric_type`) USING BTREE,
  CONSTRAINT `health_thresholds_ibfk_1` FOREIGN KEY (`elderly_id`) REFERENCES `users` (`user_id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '???????' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for monitoring_settings
-- ----------------------------
DROP TABLE IF EXISTS `monitoring_settings`;
CREATE TABLE `monitoring_settings`  (
  `setting_id` int(11) NOT NULL AUTO_INCREMENT,
  `device_id` int(11) NOT NULL COMMENT '设备ID',
  `setting_type` enum('fall_detection','sitting_alert','camera') CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '设置类型',
  `setting_key` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '设置键',
  `setting_value` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '设置值',
  `created_at` datetime NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `created_by` int(11) NOT NULL COMMENT '创建人ID',
  PRIMARY KEY (`setting_id`) USING BTREE,
  UNIQUE INDEX `uk_device_setting`(`device_id`, `setting_type`, `setting_key`) USING BTREE,
  INDEX `fk_monitoring_user`(`created_by`) USING BTREE,
  CONSTRAINT `fk_monitoring_device` FOREIGN KEY (`device_id`) REFERENCES `devices` (`device_id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `fk_monitoring_user` FOREIGN KEY (`created_by`) REFERENCES `users` (`user_id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 37 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '监控设置' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for notification_details
-- ----------------------------
DROP TABLE IF EXISTS `notification_details`;
CREATE TABLE `notification_details`  (
  `detail_id` int(11) NOT NULL AUTO_INCREMENT,
  `notification_id` int(11) NOT NULL COMMENT '??ID',
  `detail_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '????',
  `detail_key` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '???',
  `detail_value` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL COMMENT '???',
  PRIMARY KEY (`detail_id`) USING BTREE,
  INDEX `idx_notification`(`notification_id`) USING BTREE,
  CONSTRAINT `notification_details_ibfk_1` FOREIGN KEY (`notification_id`) REFERENCES `notifications` (`notification_id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '?????' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for notification_read_status
-- ----------------------------
DROP TABLE IF EXISTS `notification_read_status`;
CREATE TABLE `notification_read_status`  (
  `status_id` int(11) NOT NULL AUTO_INCREMENT,
  `notification_id` int(11) NOT NULL COMMENT '??ID',
  `guardian_id` int(11) NOT NULL COMMENT '???ID',
  `is_read` tinyint(1) NULL DEFAULT 0 COMMENT '????',
  `read_at` datetime NULL DEFAULT NULL COMMENT '????',
  PRIMARY KEY (`status_id`) USING BTREE,
  UNIQUE INDEX `uk_notification_guardian`(`notification_id`, `guardian_id`) USING BTREE,
  INDEX `guardian_id`(`guardian_id`) USING BTREE,
  CONSTRAINT `notification_read_status_ibfk_1` FOREIGN KEY (`notification_id`) REFERENCES `notifications` (`notification_id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `notification_read_status_ibfk_2` FOREIGN KEY (`guardian_id`) REFERENCES `users` (`user_id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '???????' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for notifications
-- ----------------------------
DROP TABLE IF EXISTS `notifications`;
CREATE TABLE `notifications`  (
  `notification_id` int(11) NOT NULL AUTO_INCREMENT,
  `elderly_id` int(11) NOT NULL COMMENT '????ID',
  `guardian_id` int(11) NOT NULL COMMENT '????????ID',
  `title` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '????',
  `message` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '????',
  `type` enum('fall','sitting','health','system') CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '通知类型',
  `level` enum('info','warning','danger','emergency') CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '通知级别',
  `source_type` enum('fall_detection','sitting_record','health_record') CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '????',
  `source_id` int(11) NOT NULL COMMENT '????ID',
  `is_read` tinyint(1) NULL DEFAULT 0 COMMENT '????',
  `read_at` datetime NULL DEFAULT NULL COMMENT '????',
  `created_at` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '????',
  `thumbnail` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '?????????????',
  `action_taken` tinyint(1) NULL DEFAULT 0 COMMENT '是否已采取行动',
  `action_time` datetime NULL DEFAULT NULL COMMENT '行动时间',
  `action_by` int(11) NULL DEFAULT NULL COMMENT '处理人ID',
  PRIMARY KEY (`notification_id`) USING BTREE,
  INDEX `idx_guardian_read`(`guardian_id`, `is_read`) USING BTREE,
  INDEX `idx_guardian_time`(`guardian_id`, `created_at`) USING BTREE,
  INDEX `idx_source`(`source_type`, `source_id`) USING BTREE,
  INDEX `elderly_id`(`elderly_id`) USING BTREE,
  INDEX `fk_action_by`(`action_by`) USING BTREE,
  CONSTRAINT `notifications_ibfk_1` FOREIGN KEY (`elderly_id`) REFERENCES `users` (`user_id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `notifications_ibfk_2` FOREIGN KEY (`guardian_id`) REFERENCES `users` (`user_id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `fk_action_by` FOREIGN KEY (`action_by`) REFERENCES `users` (`user_id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '???' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for sitting_records
-- ----------------------------
DROP TABLE IF EXISTS `sitting_records`;
CREATE TABLE `sitting_records`  (
  `record_id` int(11) NOT NULL AUTO_INCREMENT,
  `elderly_id` int(11) NOT NULL COMMENT '????ID',
  `device_id` int(11) NOT NULL COMMENT '????ID',
  `start_time` datetime NOT NULL COMMENT '????',
  `end_time` datetime NULL DEFAULT NULL COMMENT '????',
  `duration` int(11) NULL DEFAULT NULL COMMENT '????(??)',
  `is_notified` tinyint(1) NULL DEFAULT 0 COMMENT '?????',
  `alert_threshold` int(11) NULL DEFAULT 30 COMMENT '久坐提醒阈值(分钟)',
  `alert_sent` tinyint(1) NULL DEFAULT 0 COMMENT '是否已发送提醒',
  `alert_sent_time` datetime NULL DEFAULT NULL COMMENT '提醒发送时间',
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT 'active' COMMENT '记录状态',
  `break_count` int(11) NULL DEFAULT 0 COMMENT '休息次数',
  `last_break_time` datetime NULL DEFAULT NULL COMMENT '最后休息时间',
  PRIMARY KEY (`record_id`) USING BTREE,
  INDEX `idx_elderly_time`(`elderly_id`, `start_time`) USING BTREE,
  INDEX `device_id`(`device_id`) USING BTREE,
  CONSTRAINT `sitting_records_ibfk_1` FOREIGN KEY (`elderly_id`) REFERENCES `users` (`user_id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `sitting_records_ibfk_2` FOREIGN KEY (`device_id`) REFERENCES `devices` (`device_id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '?????' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for users
-- ----------------------------
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users`  (
  `user_id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(80) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `password` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '??',
  `role` enum('admin','guardian','elderly') CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '????????/???/????',
  `name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `phone` varchar(15) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '????',
  `email` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `created_at` datetime NULL DEFAULT CURRENT_TIMESTAMP,
  `avatar` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '??',
  `family_id` int(11) NULL DEFAULT NULL,
  PRIMARY KEY (`user_id`) USING BTREE,
  UNIQUE INDEX `uk_username`(`username`) USING BTREE,
  INDEX `family_id`(`family_id`) USING BTREE,
  INDEX `idx_username`(`username`) USING BTREE,
  INDEX `idx_phone`(`phone`) USING BTREE,
  CONSTRAINT `users_ibfk_1` FOREIGN KEY (`family_id`) REFERENCES `families` (`family_id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `users_ibfk_2` FOREIGN KEY (`family_id`) REFERENCES `families` (`family_id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 16 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '???' ROW_FORMAT = Dynamic;

SET FOREIGN_KEY_CHECKS = 1;
