/*
 Navicat Premium Data Transfer

 Source Server         : mysql
 Source Server Type    : MySQL
 Source Server Version : 50719
 Source Host           : localhost:3306
 Source Schema         : smart_home_care

 Target Server Type    : MySQL
 Target Server Version : 50719
 File Encoding         : 65001

 Date: 15/03/2025 19:46:06
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for blood_pressure
-- ----------------------------
DROP TABLE IF EXISTS `blood_pressure`;
CREATE TABLE `blood_pressure`  (
  `bp_id` int(11) NOT NULL AUTO_INCREMENT,
  `record_id` int(11) NOT NULL,
  `systolic` int(11) NULL DEFAULT NULL,
  `diastolic` int(11) NULL DEFAULT NULL,
  `temperature` decimal(4, 1) NULL DEFAULT NULL,
  `recorded_at` datetime NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`bp_id`) USING BTREE,
  INDEX `record_id`(`record_id`) USING BTREE,
  CONSTRAINT `blood_pressure_ibfk_1` FOREIGN KEY (`record_id`) REFERENCES `health_records` (`record_id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 4 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of blood_pressure
-- ----------------------------
INSERT INTO `blood_pressure` VALUES (1, 6, 120, 80, NULL, '2025-03-12 14:21:22');
INSERT INTO `blood_pressure` VALUES (2, 7, 120, 80, NULL, '2025-03-12 14:22:05');
INSERT INTO `blood_pressure` VALUES (3, 8, 120, 80, NULL, '2025-03-12 14:22:20');

-- ----------------------------
-- Table structure for devices
-- ----------------------------
DROP TABLE IF EXISTS `devices`;
CREATE TABLE `devices`  (
  `device_id` int(11) NOT NULL AUTO_INCREMENT COMMENT '设备id',
  `user_id` int(11) NOT NULL,
  `device_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `device_type` enum('camera','sensor') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `ip_address` varchar(15) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `status` enum('active','inactive') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT 'active',
  `created_at` datetime NULL DEFAULT CURRENT_TIMESTAMP,
  `family_id` int(11) NULL DEFAULT NULL,
  `location` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '未知位置',
  PRIMARY KEY (`device_id`) USING BTREE,
  INDEX `user_id`(`user_id`) USING BTREE,
  INDEX `fk_devices_family_id`(`family_id`) USING BTREE,
  CONSTRAINT `devices_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `fk_devices_family_id` FOREIGN KEY (`family_id`) REFERENCES `families` (`family_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB AUTO_INCREMENT = 5 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of devices
-- ----------------------------
INSERT INTO `devices` VALUES (1, 1, 'Camera 1', 'camera', '192.168.1.100', 'active', '2025-03-14 12:45:14', 1, '客厅');
INSERT INTO `devices` VALUES (2, 1, 'Sensor 1', 'sensor', '192.168.1.101', 'active', '2025-03-14 12:45:14', 1, '卧室');
INSERT INTO `devices` VALUES (3, 1, 'Camera 1', 'camera', '192.168.1.100', 'active', '2025-03-14 12:45:42', 1, '客厅');
INSERT INTO `devices` VALUES (4, 1, 'Sensor 1', 'sensor', '192.168.1.101', 'active', '2025-03-14 12:45:42', 1, '卧室');

-- ----------------------------
-- Table structure for fall_detection_records
-- ----------------------------
DROP TABLE IF EXISTS `fall_detection_records`;
CREATE TABLE `fall_detection_records`  (
  `record_id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `device_id` int(11) NOT NULL,
  `detection_time` datetime NULL DEFAULT CURRENT_TIMESTAMP,
  `confidence` float NULL DEFAULT NULL,
  `status` enum('fall','normal') CHARACTER SET latin1 COLLATE latin1_swedish_ci NOT NULL,
  `detection_type` enum('Fall Detected','Walking','Sitting') CHARACTER SET latin1 COLLATE latin1_swedish_ci NOT NULL,
  `video_frame_path` varchar(255) CHARACTER SET latin1 COLLATE latin1_swedish_ci NOT NULL,
  `is_notified` tinyint(1) NULL DEFAULT 0,
  PRIMARY KEY (`record_id`) USING BTREE,
  INDEX `user_id`(`user_id`) USING BTREE,
  INDEX `device_id`(`device_id`) USING BTREE,
  CONSTRAINT `fall_detection_records_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `fall_detection_records_ibfk_2` FOREIGN KEY (`device_id`) REFERENCES `devices` (`device_id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 149 CHARACTER SET = latin1 COLLATE = latin1_swedish_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of fall_detection_records
-- ----------------------------
INSERT INTO `fall_detection_records` VALUES (1, 1, 1, '2025-03-15 11:35:03', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\1', 0);
INSERT INTO `fall_detection_records` VALUES (2, 1, 1, '2025-03-15 11:40:19', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\1', 0);
INSERT INTO `fall_detection_records` VALUES (3, 1, 1, '2025-03-15 11:40:25', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\2', 0);
INSERT INTO `fall_detection_records` VALUES (6, 1, 1, '2025-03-15 11:40:31', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\3', 0);
INSERT INTO `fall_detection_records` VALUES (7, 1, 1, '2025-03-15 11:40:37', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\4', 0);
INSERT INTO `fall_detection_records` VALUES (8, 1, 1, '2025-03-15 11:40:43', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\5', 0);
INSERT INTO `fall_detection_records` VALUES (9, 1, 1, '2025-03-15 11:42:13', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\1', 0);
INSERT INTO `fall_detection_records` VALUES (10, 1, 1, '2025-03-15 11:42:19', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\2', 0);
INSERT INTO `fall_detection_records` VALUES (11, 1, 1, '2025-03-15 11:42:25', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\3', 0);
INSERT INTO `fall_detection_records` VALUES (12, 1, 1, '2025-03-15 11:42:31', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\4', 0);
INSERT INTO `fall_detection_records` VALUES (13, 1, 1, '2025-03-15 12:01:41', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\1', 0);
INSERT INTO `fall_detection_records` VALUES (14, 1, 1, '2025-03-15 12:01:47', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\2', 0);
INSERT INTO `fall_detection_records` VALUES (15, 1, 1, '2025-03-15 12:01:53', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\3', 0);
INSERT INTO `fall_detection_records` VALUES (16, 1, 1, '2025-03-15 12:01:59', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\4', 0);
INSERT INTO `fall_detection_records` VALUES (17, 1, 1, '2025-03-15 12:02:05', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\5', 0);
INSERT INTO `fall_detection_records` VALUES (18, 1, 1, '2025-03-15 12:06:26', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\1', 0);
INSERT INTO `fall_detection_records` VALUES (19, 1, 1, '2025-03-15 12:06:32', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\2', 0);
INSERT INTO `fall_detection_records` VALUES (20, 1, 1, '2025-03-15 12:06:38', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\3', 0);
INSERT INTO `fall_detection_records` VALUES (21, 1, 1, '2025-03-15 12:06:44', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\4', 0);
INSERT INTO `fall_detection_records` VALUES (22, 1, 1, '2025-03-15 12:06:50', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\5', 0);
INSERT INTO `fall_detection_records` VALUES (23, 1, 1, '2025-03-15 12:06:56', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\6', 0);
INSERT INTO `fall_detection_records` VALUES (24, 1, 1, '2025-03-15 12:07:02', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\7', 0);
INSERT INTO `fall_detection_records` VALUES (25, 1, 1, '2025-03-15 12:07:08', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\8', 0);
INSERT INTO `fall_detection_records` VALUES (26, 1, 1, '2025-03-15 12:07:14', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\9', 0);
INSERT INTO `fall_detection_records` VALUES (27, 1, 1, '2025-03-15 12:07:20', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\10', 0);
INSERT INTO `fall_detection_records` VALUES (28, 1, 1, '2025-03-15 12:07:26', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\11', 0);
INSERT INTO `fall_detection_records` VALUES (29, 1, 1, '2025-03-15 12:07:32', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\12', 0);
INSERT INTO `fall_detection_records` VALUES (30, 1, 1, '2025-03-15 12:07:38', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\13', 0);
INSERT INTO `fall_detection_records` VALUES (31, 1, 1, '2025-03-15 12:07:44', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\14', 0);
INSERT INTO `fall_detection_records` VALUES (32, 1, 1, '2025-03-15 12:16:11', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\1', 0);
INSERT INTO `fall_detection_records` VALUES (33, 1, 1, '2025-03-15 12:16:17', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\2', 0);
INSERT INTO `fall_detection_records` VALUES (34, 1, 1, '2025-03-15 12:16:23', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\3', 0);
INSERT INTO `fall_detection_records` VALUES (35, 1, 1, '2025-03-15 12:16:29', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\4', 0);
INSERT INTO `fall_detection_records` VALUES (36, 1, 1, '2025-03-15 12:16:35', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\5', 0);
INSERT INTO `fall_detection_records` VALUES (38, 1, 1, '2025-03-15 12:19:24', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\1', 0);
INSERT INTO `fall_detection_records` VALUES (39, 1, 1, '2025-03-15 12:19:30', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\2', 0);
INSERT INTO `fall_detection_records` VALUES (40, 1, 1, '2025-03-15 12:24:59', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\1', 0);
INSERT INTO `fall_detection_records` VALUES (41, 1, 1, '2025-03-15 12:25:05', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\2', 0);
INSERT INTO `fall_detection_records` VALUES (42, 1, 1, '2025-03-15 12:25:11', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\3', 0);
INSERT INTO `fall_detection_records` VALUES (43, 1, 1, '2025-03-15 12:25:17', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\4', 0);
INSERT INTO `fall_detection_records` VALUES (44, 1, 1, '2025-03-15 12:25:23', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\5', 0);
INSERT INTO `fall_detection_records` VALUES (45, 1, 1, '2025-03-15 12:25:29', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\6', 0);
INSERT INTO `fall_detection_records` VALUES (46, 1, 1, '2025-03-15 12:25:35', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\7', 0);
INSERT INTO `fall_detection_records` VALUES (47, 1, 1, '2025-03-15 12:25:41', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\8', 0);
INSERT INTO `fall_detection_records` VALUES (48, 1, 1, '2025-03-15 12:25:47', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\9', 0);
INSERT INTO `fall_detection_records` VALUES (49, 1, 1, '2025-03-15 12:25:53', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\10', 0);
INSERT INTO `fall_detection_records` VALUES (50, 1, 1, '2025-03-15 12:25:59', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\11', 0);
INSERT INTO `fall_detection_records` VALUES (51, 1, 1, '2025-03-15 12:26:05', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\12', 0);
INSERT INTO `fall_detection_records` VALUES (52, 1, 1, '2025-03-15 12:26:11', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\13', 0);
INSERT INTO `fall_detection_records` VALUES (53, 1, 1, '2025-03-15 12:26:17', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\14', 0);
INSERT INTO `fall_detection_records` VALUES (54, 1, 1, '2025-03-15 12:26:23', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\15', 0);
INSERT INTO `fall_detection_records` VALUES (55, 1, 1, '2025-03-15 12:26:29', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\16', 0);
INSERT INTO `fall_detection_records` VALUES (56, 1, 1, '2025-03-15 12:26:35', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\17', 0);
INSERT INTO `fall_detection_records` VALUES (57, 1, 1, '2025-03-15 12:26:41', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\18', 0);
INSERT INTO `fall_detection_records` VALUES (58, 1, 1, '2025-03-15 12:26:47', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\19', 0);
INSERT INTO `fall_detection_records` VALUES (59, 1, 1, '2025-03-15 12:26:52', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\20', 0);
INSERT INTO `fall_detection_records` VALUES (60, 1, 1, '2025-03-15 12:26:58', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\21', 0);
INSERT INTO `fall_detection_records` VALUES (61, 1, 1, '2025-03-15 12:27:04', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\22', 0);
INSERT INTO `fall_detection_records` VALUES (62, 1, 1, '2025-03-15 12:27:10', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\23', 0);
INSERT INTO `fall_detection_records` VALUES (63, 1, 1, '2025-03-15 12:27:16', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\24', 0);
INSERT INTO `fall_detection_records` VALUES (64, 1, 1, '2025-03-15 12:27:23', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\25', 0);
INSERT INTO `fall_detection_records` VALUES (65, 1, 1, '2025-03-15 12:27:29', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\26', 0);
INSERT INTO `fall_detection_records` VALUES (66, 1, 1, '2025-03-15 12:27:35', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\27', 0);
INSERT INTO `fall_detection_records` VALUES (67, 1, 1, '2025-03-15 12:27:40', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\28', 0);
INSERT INTO `fall_detection_records` VALUES (68, 1, 1, '2025-03-15 12:27:46', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\29', 0);
INSERT INTO `fall_detection_records` VALUES (69, 1, 1, '2025-03-15 12:27:52', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\30', 0);
INSERT INTO `fall_detection_records` VALUES (70, 1, 1, '2025-03-15 12:27:58', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\31', 0);
INSERT INTO `fall_detection_records` VALUES (71, 1, 1, '2025-03-15 12:28:04', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\32', 0);
INSERT INTO `fall_detection_records` VALUES (72, 1, 1, '2025-03-15 12:28:10', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\33', 0);
INSERT INTO `fall_detection_records` VALUES (73, 1, 1, '2025-03-15 12:28:16', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\34', 0);
INSERT INTO `fall_detection_records` VALUES (74, 1, 1, '2025-03-15 12:28:22', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\35', 0);
INSERT INTO `fall_detection_records` VALUES (75, 1, 1, '2025-03-15 12:28:28', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\36', 0);
INSERT INTO `fall_detection_records` VALUES (76, 1, 1, '2025-03-15 12:28:34', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\37', 0);
INSERT INTO `fall_detection_records` VALUES (77, 1, 1, '2025-03-15 12:28:45', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\38', 0);
INSERT INTO `fall_detection_records` VALUES (78, 1, 1, '2025-03-15 12:28:51', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\39', 0);
INSERT INTO `fall_detection_records` VALUES (79, 1, 1, '2025-03-15 12:28:57', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\40', 0);
INSERT INTO `fall_detection_records` VALUES (80, 1, 1, '2025-03-15 12:29:03', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\41', 0);
INSERT INTO `fall_detection_records` VALUES (81, 1, 1, '2025-03-15 12:29:09', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\42', 0);
INSERT INTO `fall_detection_records` VALUES (82, 1, 1, '2025-03-15 12:29:15', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\43', 0);
INSERT INTO `fall_detection_records` VALUES (83, 1, 1, '2025-03-15 12:29:21', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\44', 0);
INSERT INTO `fall_detection_records` VALUES (84, 1, 1, '2025-03-15 12:29:27', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\45', 0);
INSERT INTO `fall_detection_records` VALUES (85, 1, 1, '2025-03-15 12:29:33', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\46', 0);
INSERT INTO `fall_detection_records` VALUES (86, 1, 1, '2025-03-15 12:29:39', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\47', 0);
INSERT INTO `fall_detection_records` VALUES (87, 1, 1, '2025-03-15 12:29:45', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\48', 0);
INSERT INTO `fall_detection_records` VALUES (88, 1, 1, '2025-03-15 12:29:51', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\49', 0);
INSERT INTO `fall_detection_records` VALUES (89, 1, 1, '2025-03-15 12:29:57', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\50', 0);
INSERT INTO `fall_detection_records` VALUES (90, 1, 1, '2025-03-15 12:30:03', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\51', 0);
INSERT INTO `fall_detection_records` VALUES (91, 1, 1, '2025-03-15 12:30:09', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\52', 0);
INSERT INTO `fall_detection_records` VALUES (92, 1, 1, '2025-03-15 12:30:15', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\53', 0);
INSERT INTO `fall_detection_records` VALUES (93, 1, 1, '2025-03-15 12:30:21', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\54', 0);
INSERT INTO `fall_detection_records` VALUES (94, 1, 1, '2025-03-15 12:30:27', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\55', 0);
INSERT INTO `fall_detection_records` VALUES (95, 1, 1, '2025-03-15 12:30:33', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\56', 0);
INSERT INTO `fall_detection_records` VALUES (96, 1, 1, '2025-03-15 12:30:39', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\57', 0);
INSERT INTO `fall_detection_records` VALUES (97, 1, 1, '2025-03-15 12:30:45', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\58', 0);
INSERT INTO `fall_detection_records` VALUES (98, 1, 1, '2025-03-15 12:30:51', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\59', 0);
INSERT INTO `fall_detection_records` VALUES (99, 1, 1, '2025-03-15 12:30:57', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\60', 0);
INSERT INTO `fall_detection_records` VALUES (100, 1, 1, '2025-03-15 12:31:03', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\61', 0);
INSERT INTO `fall_detection_records` VALUES (101, 1, 1, '2025-03-15 12:31:09', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\62', 0);
INSERT INTO `fall_detection_records` VALUES (102, 1, 1, '2025-03-15 12:31:15', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\63', 0);
INSERT INTO `fall_detection_records` VALUES (103, 1, 1, '2025-03-15 12:31:21', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\64', 0);
INSERT INTO `fall_detection_records` VALUES (104, 1, 1, '2025-03-15 12:31:27', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\65', 0);
INSERT INTO `fall_detection_records` VALUES (105, 1, 1, '2025-03-15 12:31:33', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\66', 0);
INSERT INTO `fall_detection_records` VALUES (106, 1, 1, '2025-03-15 12:31:39', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\67', 0);
INSERT INTO `fall_detection_records` VALUES (107, 1, 1, '2025-03-15 12:31:45', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\68', 0);
INSERT INTO `fall_detection_records` VALUES (108, 1, 1, '2025-03-15 12:31:51', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\69', 0);
INSERT INTO `fall_detection_records` VALUES (109, 1, 1, '2025-03-15 12:31:57', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\70', 0);
INSERT INTO `fall_detection_records` VALUES (110, 1, 1, '2025-03-15 12:32:03', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\71', 0);
INSERT INTO `fall_detection_records` VALUES (111, 1, 1, '2025-03-15 12:32:09', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\72', 0);
INSERT INTO `fall_detection_records` VALUES (112, 1, 1, '2025-03-15 12:32:15', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\73', 0);
INSERT INTO `fall_detection_records` VALUES (113, 1, 1, '2025-03-15 12:32:20', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\74', 0);
INSERT INTO `fall_detection_records` VALUES (114, 1, 1, '2025-03-15 12:32:26', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\75', 0);
INSERT INTO `fall_detection_records` VALUES (115, 1, 1, '2025-03-15 12:32:32', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\76', 0);
INSERT INTO `fall_detection_records` VALUES (116, 1, 1, '2025-03-15 12:32:38', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\77', 0);
INSERT INTO `fall_detection_records` VALUES (117, 1, 1, '2025-03-15 12:32:44', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\78', 0);
INSERT INTO `fall_detection_records` VALUES (118, 1, 1, '2025-03-15 12:32:50', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\79', 0);
INSERT INTO `fall_detection_records` VALUES (119, 1, 1, '2025-03-15 12:32:56', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\80', 0);
INSERT INTO `fall_detection_records` VALUES (120, 1, 1, '2025-03-15 12:33:02', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\81', 0);
INSERT INTO `fall_detection_records` VALUES (121, 1, 1, '2025-03-15 12:33:08', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\82', 0);
INSERT INTO `fall_detection_records` VALUES (122, 1, 1, '2025-03-15 12:33:14', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\83', 0);
INSERT INTO `fall_detection_records` VALUES (123, 1, 1, '2025-03-15 12:33:23', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\84', 0);
INSERT INTO `fall_detection_records` VALUES (124, 1, 1, '2025-03-15 12:33:29', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\85', 0);
INSERT INTO `fall_detection_records` VALUES (125, 1, 1, '2025-03-15 12:33:35', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\86', 0);
INSERT INTO `fall_detection_records` VALUES (126, 1, 1, '2025-03-15 12:33:41', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\87', 0);
INSERT INTO `fall_detection_records` VALUES (127, 1, 1, '2025-03-15 12:33:47', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\88', 0);
INSERT INTO `fall_detection_records` VALUES (128, 1, 1, '2025-03-15 12:33:53', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\89', 0);
INSERT INTO `fall_detection_records` VALUES (129, 1, 1, '2025-03-15 12:33:59', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\90', 0);
INSERT INTO `fall_detection_records` VALUES (130, 1, 1, '2025-03-15 12:34:05', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\91', 0);
INSERT INTO `fall_detection_records` VALUES (131, 1, 1, '2025-03-15 12:34:11', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\92', 0);
INSERT INTO `fall_detection_records` VALUES (132, 1, 1, '2025-03-15 12:34:17', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\93', 0);
INSERT INTO `fall_detection_records` VALUES (133, 1, 1, '2025-03-15 12:34:23', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\94', 0);
INSERT INTO `fall_detection_records` VALUES (134, 1, 1, '2025-03-15 12:34:29', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\95', 0);
INSERT INTO `fall_detection_records` VALUES (135, 1, 1, '2025-03-15 12:34:35', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\96', 0);
INSERT INTO `fall_detection_records` VALUES (136, 1, 1, '2025-03-15 12:34:40', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\97', 0);
INSERT INTO `fall_detection_records` VALUES (137, 1, 1, '2025-03-15 12:34:46', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\98', 0);
INSERT INTO `fall_detection_records` VALUES (138, 1, 1, '2025-03-15 12:34:52', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\99', 0);
INSERT INTO `fall_detection_records` VALUES (139, 1, 1, '2025-03-15 12:34:58', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\100', 0);
INSERT INTO `fall_detection_records` VALUES (140, 1, 1, '2025-03-15 12:35:04', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\101', 0);
INSERT INTO `fall_detection_records` VALUES (141, 1, 1, '2025-03-15 12:35:10', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\102', 0);
INSERT INTO `fall_detection_records` VALUES (142, 1, 1, '2025-03-15 12:35:16', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\103', 0);
INSERT INTO `fall_detection_records` VALUES (143, 1, 1, '2025-03-15 12:35:22', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\104', 0);
INSERT INTO `fall_detection_records` VALUES (144, 1, 1, '2025-03-15 12:35:28', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\105', 0);
INSERT INTO `fall_detection_records` VALUES (145, 1, 1, '2025-03-15 12:35:34', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\106', 0);
INSERT INTO `fall_detection_records` VALUES (146, 1, 1, '2025-03-15 12:35:40', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\107', 0);
INSERT INTO `fall_detection_records` VALUES (147, 1, 1, '2025-03-15 12:35:46', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\108', 0);
INSERT INTO `fall_detection_records` VALUES (148, 1, 1, '2025-03-15 12:35:52', 0.9, 'fall', 'Fall Detected', 'static/snapshots\\fall\\109', 0);

-- ----------------------------
-- Table structure for families
-- ----------------------------
DROP TABLE IF EXISTS `families`;
CREATE TABLE `families`  (
  `family_id` int(11) NOT NULL AUTO_INCREMENT COMMENT '家庭id',
  `family_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '家庭名称',
  `created_at` datetime NULL DEFAULT CURRENT_TIMESTAMP,
  `family_address` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '家庭地址',
  PRIMARY KEY (`family_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 5 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of families
-- ----------------------------
INSERT INTO `families` VALUES (1, 'zwd‘s Family', '2025-02-01 16:11:21', '南新');
INSERT INTO `families` VALUES (2, 'zdl‘s Family', '2025-02-01 19:15:05', NULL);
INSERT INTO `families` VALUES (3, 'zcj\'s Family', '2025-03-10 19:00:11', NULL);
INSERT INTO `families` VALUES (4, '李四的家庭', '2025-03-14 12:33:52', NULL);

-- ----------------------------
-- Table structure for health_alerts
-- ----------------------------
DROP TABLE IF EXISTS `health_alerts`;
CREATE TABLE `health_alerts`  (
  `alert_id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `record_id` int(11) NOT NULL,
  `threshold_id` int(11) NOT NULL,
  `actual_value` decimal(10, 2) NULL DEFAULT NULL,
  `sent_at` datetime NULL DEFAULT CURRENT_TIMESTAMP,
  `status` enum('sent','failed') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT 'sent',
  PRIMARY KEY (`alert_id`) USING BTREE,
  INDEX `user_id`(`user_id`) USING BTREE,
  INDEX `record_id`(`record_id`) USING BTREE,
  INDEX `threshold_id`(`threshold_id`) USING BTREE,
  CONSTRAINT `health_alerts_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `health_alerts_ibfk_2` FOREIGN KEY (`record_id`) REFERENCES `health_records` (`record_id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `health_alerts_ibfk_3` FOREIGN KEY (`threshold_id`) REFERENCES `health_thresholds` (`threshold_id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of health_alerts
-- ----------------------------

-- ----------------------------
-- Table structure for health_data
-- ----------------------------
DROP TABLE IF EXISTS `health_data`;
CREATE TABLE `health_data`  (
  `health_id` int(11) NOT NULL AUTO_INCREMENT COMMENT '成员健康数据id',
  `user_id` int(11) NOT NULL,
  `recorded_at` datetime NULL DEFAULT NULL,
  `created_at` datetime NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  `height` float NULL DEFAULT NULL,
  `weight` float NULL DEFAULT NULL,
  `temperature` float NULL DEFAULT NULL,
  `heart_rate` int(11) NULL DEFAULT NULL,
  PRIMARY KEY (`health_id`) USING BTREE,
  INDEX `user_id`(`user_id`) USING BTREE,
  CONSTRAINT `health_data_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 3 CHARACTER SET = latin1 COLLATE = latin1_swedish_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of health_data
-- ----------------------------
INSERT INTO `health_data` VALUES (2, 1, '2025-03-11 15:10:12', NULL, 170, 65, 36.5, 75);

-- ----------------------------
-- Table structure for health_records
-- ----------------------------
DROP TABLE IF EXISTS `health_records`;
CREATE TABLE `health_records`  (
  `record_id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `recorded_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`record_id`) USING BTREE,
  INDEX `user_id`(`user_id`) USING BTREE,
  CONSTRAINT `health_records_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 41 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of health_records
-- ----------------------------
INSERT INTO `health_records` VALUES (1, 1, '2025-03-12 13:14:26');
INSERT INTO `health_records` VALUES (2, 1, '2024-01-01 12:00:00');
INSERT INTO `health_records` VALUES (6, 1, '2024-01-01 08:00:00');
INSERT INTO `health_records` VALUES (7, 1, '2025-03-12 14:22:05');
INSERT INTO `health_records` VALUES (8, 1, '2025-03-12 14:22:20');
INSERT INTO `health_records` VALUES (9, 1, '2024-01-01 12:00:00');
INSERT INTO `health_records` VALUES (10, 1, '2024-01-02 12:00:00');
INSERT INTO `health_records` VALUES (11, 1, '2024-01-03 12:00:00');
INSERT INTO `health_records` VALUES (12, 1, '2024-01-14 12:00:00');
INSERT INTO `health_records` VALUES (13, 1, '2024-03-12 12:00:00');
INSERT INTO `health_records` VALUES (14, 1, '2024-03-13 12:00:00');
INSERT INTO `health_records` VALUES (15, 1, '2025-01-01 12:34:56');
INSERT INTO `health_records` VALUES (16, 1, '2025-03-13 16:19:13');
INSERT INTO `health_records` VALUES (18, 1, '2025-03-13 16:20:57');
INSERT INTO `health_records` VALUES (19, 1, '2025-03-13 16:24:54');
INSERT INTO `health_records` VALUES (20, 1, '2025-03-13 16:24:57');
INSERT INTO `health_records` VALUES (21, 1, '2025-03-13 16:24:59');
INSERT INTO `health_records` VALUES (22, 1, '2025-03-13 16:24:59');
INSERT INTO `health_records` VALUES (23, 1, '2025-03-13 16:24:59');
INSERT INTO `health_records` VALUES (24, 1, '2025-03-13 16:25:00');
INSERT INTO `health_records` VALUES (25, 1, '2025-03-13 16:25:00');
INSERT INTO `health_records` VALUES (26, 1, '2025-03-13 16:25:00');
INSERT INTO `health_records` VALUES (27, 1, '2025-03-13 16:25:00');
INSERT INTO `health_records` VALUES (28, 1, '2025-03-13 16:25:00');
INSERT INTO `health_records` VALUES (29, 1, '2025-03-13 16:29:09');
INSERT INTO `health_records` VALUES (30, 1, '2025-03-10 12:00:00');
INSERT INTO `health_records` VALUES (31, 1, '2025-03-09 12:00:00');
INSERT INTO `health_records` VALUES (32, 1, '2025-02-09 12:00:00');
INSERT INTO `health_records` VALUES (33, 1, '2025-02-19 12:00:00');
INSERT INTO `health_records` VALUES (34, 1, '2025-03-13 19:50:23');
INSERT INTO `health_records` VALUES (35, 1, '2025-03-13 19:50:25');
INSERT INTO `health_records` VALUES (36, 1, '2025-03-13 19:50:25');
INSERT INTO `health_records` VALUES (38, 1, '2025-03-13 19:53:15');
INSERT INTO `health_records` VALUES (39, 1, '2025-03-13 19:55:24');
INSERT INTO `health_records` VALUES (40, 1, '2025-03-13 20:07:20');

-- ----------------------------
-- Table structure for health_thresholds
-- ----------------------------
DROP TABLE IF EXISTS `health_thresholds`;
CREATE TABLE `health_thresholds`  (
  `threshold_id` int(11) NOT NULL AUTO_INCREMENT,
  `metric_type` enum('blood_pressure_systolic','heart_rate','bmi','temperature') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `min_value` decimal(10, 2) NULL DEFAULT NULL,
  `max_value` decimal(10, 2) NULL DEFAULT NULL,
  `alert_type` enum('warning','emergency') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`threshold_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of health_thresholds
-- ----------------------------

-- ----------------------------
-- Table structure for heart_rate
-- ----------------------------
DROP TABLE IF EXISTS `heart_rate`;
CREATE TABLE `heart_rate`  (
  `hr_id` int(11) NOT NULL AUTO_INCREMENT,
  `record_id` int(11) NOT NULL,
  `rate` int(11) NULL DEFAULT NULL,
  PRIMARY KEY (`hr_id`) USING BTREE,
  INDEX `record_id`(`record_id`) USING BTREE,
  CONSTRAINT `heart_rate_ibfk_1` FOREIGN KEY (`record_id`) REFERENCES `health_records` (`record_id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of heart_rate
-- ----------------------------

-- ----------------------------
-- Table structure for height_weight
-- ----------------------------
DROP TABLE IF EXISTS `height_weight`;
CREATE TABLE `height_weight`  (
  `hw_id` int(11) NOT NULL AUTO_INCREMENT,
  `record_id` int(11) NOT NULL,
  `height` decimal(5, 2) NULL DEFAULT NULL,
  `weight` decimal(5, 2) NULL DEFAULT NULL,
  `bmi` decimal(4, 2) NULL DEFAULT NULL,
  PRIMARY KEY (`hw_id`) USING BTREE,
  INDEX `record_id`(`record_id`) USING BTREE,
  CONSTRAINT `height_weight_ibfk_1` FOREIGN KEY (`record_id`) REFERENCES `health_records` (`record_id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 33 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of height_weight
-- ----------------------------
INSERT INTO `height_weight` VALUES (1, 1, 170.00, 60.00, 20.76);
INSERT INTO `height_weight` VALUES (2, 2, 170.00, 60.00, 20.76);
INSERT INTO `height_weight` VALUES (3, 9, 170.00, 60.00, 20.76);
INSERT INTO `height_weight` VALUES (4, 10, 170.00, 60.00, 20.76);
INSERT INTO `height_weight` VALUES (5, 11, 170.00, 60.00, 20.76);
INSERT INTO `height_weight` VALUES (6, 12, 170.00, 60.00, 20.76);
INSERT INTO `height_weight` VALUES (7, 13, 170.00, 60.00, 20.76);
INSERT INTO `height_weight` VALUES (8, 14, 170.00, 60.00, 20.76);
INSERT INTO `height_weight` VALUES (9, 15, 170.00, 65.00, 22.49);
INSERT INTO `height_weight` VALUES (10, 16, 121.00, 12.00, 8.20);
INSERT INTO `height_weight` VALUES (11, 18, 121.00, 22.00, 15.03);
INSERT INTO `height_weight` VALUES (12, 19, 121.00, 12.00, 8.20);
INSERT INTO `height_weight` VALUES (13, 20, 121.00, 12.00, 8.20);
INSERT INTO `height_weight` VALUES (14, 21, 121.00, 12.00, 8.20);
INSERT INTO `height_weight` VALUES (15, 22, 121.00, 12.00, 8.20);
INSERT INTO `height_weight` VALUES (16, 23, 121.00, 12.00, 8.20);
INSERT INTO `height_weight` VALUES (17, 24, 121.00, 12.00, 8.20);
INSERT INTO `height_weight` VALUES (18, 25, 121.00, 12.00, 8.20);
INSERT INTO `height_weight` VALUES (19, 26, 121.00, 12.00, 8.20);
INSERT INTO `height_weight` VALUES (20, 27, 121.00, 12.00, 8.20);
INSERT INTO `height_weight` VALUES (21, 28, 121.00, 12.00, 8.20);
INSERT INTO `height_weight` VALUES (22, 29, 122.00, 22.00, 14.78);
INSERT INTO `height_weight` VALUES (23, 30, 172.00, 60.00, 20.28);
INSERT INTO `height_weight` VALUES (24, 31, 172.00, 63.00, 21.30);
INSERT INTO `height_weight` VALUES (25, 32, 172.00, 63.00, 21.30);
INSERT INTO `height_weight` VALUES (26, 33, 172.00, 63.00, 21.30);
INSERT INTO `height_weight` VALUES (27, 34, 121.00, 2.00, 1.37);
INSERT INTO `height_weight` VALUES (28, 35, 121.00, 22.00, 15.03);
INSERT INTO `height_weight` VALUES (29, 36, 121.00, 22.00, 15.03);
INSERT INTO `height_weight` VALUES (30, 38, 123.00, 33.00, 21.81);
INSERT INTO `height_weight` VALUES (31, 39, 170.00, 34.00, 11.76);
INSERT INTO `height_weight` VALUES (32, 40, 178.00, 50.00, 15.78);

-- ----------------------------
-- Table structure for notifications
-- ----------------------------
DROP TABLE IF EXISTS `notifications`;
CREATE TABLE `notifications`  (
  `notification_id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `record_id` int(11) NULL DEFAULT NULL,
  `device_id` int(11) NULL DEFAULT NULL,
  `message` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `sent_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `status` enum('sent','failed') CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT 'sent',
  `type` enum('emergency','warning','info') CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `detection_type` enum('Fall Detected','Walking','Sitting') CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `is_read` tinyint(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`notification_id`) USING BTREE,
  INDEX `user_id`(`user_id`) USING BTREE,
  INDEX `record_id`(`record_id`) USING BTREE,
  INDEX `fk_notifications_device`(`device_id`) USING BTREE,
  CONSTRAINT `fk_notifications_device` FOREIGN KEY (`device_id`) REFERENCES `devices` (`device_id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `fk_notifications_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `notifications_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `notifications_ibfk_2` FOREIGN KEY (`record_id`) REFERENCES `fall_detection_records` (`record_id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 3 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of notifications
-- ----------------------------

-- ----------------------------
-- Table structure for temperature
-- ----------------------------
DROP TABLE IF EXISTS `temperature`;
CREATE TABLE `temperature`  (
  `temp_id` int(11) NOT NULL AUTO_INCREMENT,
  `record_id` int(11) NOT NULL,
  `value` decimal(4, 1) NULL DEFAULT NULL,
  PRIMARY KEY (`temp_id`) USING BTREE,
  INDEX `record_id`(`record_id`) USING BTREE,
  CONSTRAINT `temperature_ibfk_1` FOREIGN KEY (`record_id`) REFERENCES `health_records` (`record_id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of temperature
-- ----------------------------

-- ----------------------------
-- Table structure for users
-- ----------------------------
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users`  (
  `user_id` int(11) NOT NULL AUTO_INCREMENT COMMENT '用户id',
  `username` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `password` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `role` enum('elderly','family','admin') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '用户权限',
  `name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `phone` varchar(15) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `address` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `created_at` datetime NULL DEFAULT CURRENT_TIMESTAMP,
  `family_id` int(11) NULL DEFAULT NULL,
  `avatar` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  PRIMARY KEY (`user_id`) USING BTREE,
  UNIQUE INDEX `username`(`username`) USING BTREE,
  INDEX `family_id`(`family_id`) USING BTREE,
  CONSTRAINT `family_id` FOREIGN KEY (`family_id`) REFERENCES `families` (`family_id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `fk_users_family_id` FOREIGN KEY (`family_id`) REFERENCES `families` (`family_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB AUTO_INCREMENT = 7 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of users
-- ----------------------------
INSERT INTO `users` VALUES (1, 'zwd', 'scrypt:32768:8:1$OzLdr7LEjRnznA3p$973d512fa0a4bb9d23d28fdd39cc34b6f181c170cfc533686c8b967f926e4cc7931df5afc1c3ae67cee760eb16bab4886bef8addb7c47fcde62323d55b83ec41', 'admin', 'zwd', '11221122111', 'zhangweidong0730@outlook.com', '南新', '2025-03-01 21:32:41', 1, '/static/avatars/1.jpg');
INSERT INTO `users` VALUES (2, 'zdl', 'scrypt:32768:8:1$5QISfHLanHLAH20V$9c6bbc7b670eef32e8356150bfbfb0f8686ab22a4f2a5678e651cad3a9578548a9c6ac5d9ff2d63ea590f3063404eaf3401929593aef0a08f08c083c197e0e0d', 'elderly', 'zdl', '11111111111', '111', '南新', '2025-03-08 20:27:07', 1, '/static/avatars/2.jpg');
INSERT INTO `users` VALUES (3, 'zcj', 'scrypt:32768:8:1$OJxV5j9XqxolEB8K$867fdc498e3bcf96fc89e070ec339f7e8c427a1b2a83dba34f856de0f30e978a3c437b98f4a6931e70201cf742b4bac803b33e780db1886ad4c99ae0b9dd4ff7', 'elderly', 'zcj', '12111112222', '', '', '2025-03-10 19:00:11', 1, '/static/avatars/3.jpg');
INSERT INTO `users` VALUES (4, 'primary_user', '123456', 'admin', '李四', '13800138000', NULL, NULL, '2025-03-14 12:33:38', 1, NULL);
INSERT INTO `users` VALUES (5, 'family_member_1', '123456', 'family', '张三', '13800138001', NULL, NULL, '2025-03-14 12:33:38', 1, NULL);
INSERT INTO `users` VALUES (6, 'family_member_2', '123456', 'family', '王五', '13800138002', NULL, NULL, '2025-03-14 12:33:38', 1, NULL);

SET FOREIGN_KEY_CHECKS = 1;
