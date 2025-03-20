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

 Date: 18/03/2025 19:22:19
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for sitting_records
-- ----------------------------
DROP TABLE IF EXISTS `sitting_records`;
CREATE TABLE `sitting_records`  (
  `record_id` int(11) NOT NULL AUTO_INCREMENT,
  `elderly_id` int(11) NOT NULL,
  `device_id` int(11) NOT NULL,
  `start_time` datetime NOT NULL,
  `end_time` datetime NULL DEFAULT NULL,
  `duration` int(11) NULL DEFAULT NULL,
  `is_notified` tinyint(1) NULL DEFAULT NULL,
  PRIMARY KEY (`record_id`) USING BTREE,
  INDEX `elderly_id`(`elderly_id`) USING BTREE,
  INDEX `device_id`(`device_id`) USING BTREE,
  CONSTRAINT `sitting_records_ibfk_1` FOREIGN KEY (`elderly_id`) REFERENCES `users` (`user_id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `sitting_records_ibfk_2` FOREIGN KEY (`device_id`) REFERENCES `devices` (`device_id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 164 CHARACTER SET = latin1 COLLATE = latin1_swedish_ci ROW_FORMAT = Dynamic;

SET FOREIGN_KEY_CHECKS = 1;
