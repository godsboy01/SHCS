-- MySQL dump 10.13  Distrib 5.7.19, for Win64 (x86_64)
--
-- Host: localhost    Database: smart_home_care
-- ------------------------------------------------------
-- Server version	5.7.19

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `blood_pressure`
--

DROP TABLE IF EXISTS `blood_pressure`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `blood_pressure` (
  `bp_id` int(11) NOT NULL AUTO_INCREMENT,
  `record_id` int(11) NOT NULL,
  `systolic` int(11) DEFAULT NULL,
  `diastolic` int(11) DEFAULT NULL,
  `temperature` decimal(4,1) DEFAULT NULL,
  `recorded_at` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`bp_id`) USING BTREE,
  KEY `record_id` (`record_id`) USING BTREE,
  CONSTRAINT `blood_pressure_ibfk_1` FOREIGN KEY (`record_id`) REFERENCES `health_records` (`record_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `blood_pressure`
--

LOCK TABLES `blood_pressure` WRITE;
/*!40000 ALTER TABLE `blood_pressure` DISABLE KEYS */;
INSERT INTO `blood_pressure` VALUES (1,6,120,80,NULL,'2025-03-12 14:21:22'),(2,7,120,80,NULL,'2025-03-12 14:22:05'),(3,8,120,80,NULL,'2025-03-12 14:22:20');
/*!40000 ALTER TABLE `blood_pressure` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `devices`
--

DROP TABLE IF EXISTS `devices`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `devices` (
  `device_id` int(11) NOT NULL AUTO_INCREMENT COMMENT '设备id',
  `user_id` int(11) NOT NULL,
  `device_name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `device_type` enum('camera','sensor') COLLATE utf8mb4_unicode_ci NOT NULL,
  `ip_address` varchar(15) COLLATE utf8mb4_unicode_ci NOT NULL,
  `status` enum('active','inactive') COLLATE utf8mb4_unicode_ci DEFAULT 'active',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `family_id` int(11) DEFAULT NULL,
  `location` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '未知位置',
  `is_deleted` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`device_id`) USING BTREE,
  KEY `user_id` (`user_id`) USING BTREE,
  KEY `fk_devices_family_id` (`family_id`) USING BTREE,
  CONSTRAINT `devices_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE,
  CONSTRAINT `devices_ibfk_2` FOREIGN KEY (`family_id`) REFERENCES `families` (`family_id`),
  CONSTRAINT `fk_devices_family_id` FOREIGN KEY (`family_id`) REFERENCES `families` (`family_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `devices`
--

LOCK TABLES `devices` WRITE;
/*!40000 ALTER TABLE `devices` DISABLE KEYS */;
INSERT INTO `devices` VALUES (1,1,'Camera 1','camera','192.168.1.100','active','2025-03-14 12:45:14',1,'客厅',0),(2,1,'Sensor 1','sensor','192.168.1.101','active','2025-03-14 12:45:14',1,'卧室',0),(3,1,'Camera 1','camera','192.168.1.100','active','2025-03-14 12:45:42',1,'客厅',0),(4,1,'Sensor 1','sensor','192.168.1.101','active','2025-03-14 12:45:42',1,'卧室',0);
/*!40000 ALTER TABLE `devices` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `fall_detection_records`
--

DROP TABLE IF EXISTS `fall_detection_records`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `fall_detection_records` (
  `record_id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `device_id` int(11) NOT NULL,
  `detection_time` datetime DEFAULT CURRENT_TIMESTAMP,
  `confidence` float DEFAULT NULL,
  `status` enum('fall','normal') NOT NULL,
  `detection_type` enum('Fall Detected','Walking','Sitting') NOT NULL,
  `video_frame_path` varchar(255) NOT NULL,
  `is_notified` tinyint(1) DEFAULT '0',
  `is_deleted` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`record_id`) USING BTREE,
  KEY `user_id` (`user_id`) USING BTREE,
  KEY `device_id` (`device_id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=214 DEFAULT CHARSET=latin1 ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fall_detection_records`
--

LOCK TABLES `fall_detection_records` WRITE;
/*!40000 ALTER TABLE `fall_detection_records` DISABLE KEYS */;
/*!40000 ALTER TABLE `fall_detection_records` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `families`
--

DROP TABLE IF EXISTS `families`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `families` (
  `family_id` int(11) NOT NULL AUTO_INCREMENT COMMENT '家庭id',
  `family_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '家庭名称',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `family_address` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '家庭地址',
  PRIMARY KEY (`family_id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `families`
--

LOCK TABLES `families` WRITE;
/*!40000 ALTER TABLE `families` DISABLE KEYS */;
INSERT INTO `families` VALUES (1,'zwd‘s Family','2025-02-01 16:11:21','南新'),(2,'zdl‘s Family','2025-02-01 19:15:05',NULL),(3,'zcj\'s Family','2025-03-10 19:00:11',NULL),(4,'李四的家庭','2025-03-14 12:33:52',NULL),(5,'whn\'s Family','2025-03-15 23:28:22',NULL);
/*!40000 ALTER TABLE `families` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `health_alerts`
--

DROP TABLE IF EXISTS `health_alerts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `health_alerts` (
  `alert_id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `record_id` int(11) NOT NULL,
  `threshold_id` int(11) NOT NULL,
  `actual_value` decimal(10,2) DEFAULT NULL,
  `sent_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `status` enum('sent','failed') COLLATE utf8mb4_unicode_ci DEFAULT 'sent',
  PRIMARY KEY (`alert_id`) USING BTREE,
  KEY `user_id` (`user_id`) USING BTREE,
  KEY `record_id` (`record_id`) USING BTREE,
  KEY `threshold_id` (`threshold_id`) USING BTREE,
  CONSTRAINT `health_alerts_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE,
  CONSTRAINT `health_alerts_ibfk_2` FOREIGN KEY (`record_id`) REFERENCES `health_records` (`record_id`) ON DELETE CASCADE,
  CONSTRAINT `health_alerts_ibfk_3` FOREIGN KEY (`threshold_id`) REFERENCES `health_thresholds` (`threshold_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `health_alerts`
--

LOCK TABLES `health_alerts` WRITE;
/*!40000 ALTER TABLE `health_alerts` DISABLE KEYS */;
/*!40000 ALTER TABLE `health_alerts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `health_data`
--

DROP TABLE IF EXISTS `health_data`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `health_data` (
  `health_id` int(11) NOT NULL AUTO_INCREMENT COMMENT '成员健康数据id',
  `user_id` int(11) NOT NULL,
  `recorded_at` datetime DEFAULT NULL,
  `created_at` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  `height` float DEFAULT NULL,
  `weight` float DEFAULT NULL,
  `temperature` float DEFAULT NULL,
  `heart_rate` int(11) DEFAULT NULL,
  PRIMARY KEY (`health_id`) USING BTREE,
  KEY `user_id` (`user_id`) USING BTREE,
  CONSTRAINT `health_data_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=latin1 ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `health_data`
--

LOCK TABLES `health_data` WRITE;
/*!40000 ALTER TABLE `health_data` DISABLE KEYS */;
INSERT INTO `health_data` VALUES (2,1,'2025-03-11 15:10:12',NULL,170,65,36.5,75);
/*!40000 ALTER TABLE `health_data` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `health_records`
--

DROP TABLE IF EXISTS `health_records`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `health_records` (
  `record_id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `recorded_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`record_id`) USING BTREE,
  KEY `user_id` (`user_id`) USING BTREE,
  CONSTRAINT `health_records_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=42 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `health_records`
--

LOCK TABLES `health_records` WRITE;
/*!40000 ALTER TABLE `health_records` DISABLE KEYS */;
INSERT INTO `health_records` VALUES (1,1,'2025-03-12 13:14:26'),(2,1,'2024-01-01 12:00:00'),(6,1,'2024-01-01 08:00:00'),(7,1,'2025-03-12 14:22:05'),(8,1,'2025-03-12 14:22:20'),(9,1,'2024-01-01 12:00:00'),(10,1,'2024-01-02 12:00:00'),(11,1,'2024-01-03 12:00:00'),(12,1,'2024-01-14 12:00:00'),(13,1,'2024-03-12 12:00:00'),(14,1,'2024-03-13 12:00:00'),(15,1,'2025-01-01 12:34:56'),(16,1,'2025-03-13 16:19:13'),(18,1,'2025-03-13 16:20:57'),(19,1,'2025-03-13 16:24:54'),(20,1,'2025-03-13 16:24:57'),(21,1,'2025-03-13 16:24:59'),(22,1,'2025-03-13 16:24:59'),(23,1,'2025-03-13 16:24:59'),(24,1,'2025-03-13 16:25:00'),(25,1,'2025-03-13 16:25:00'),(26,1,'2025-03-13 16:25:00'),(27,1,'2025-03-13 16:25:00'),(28,1,'2025-03-13 16:25:00'),(29,1,'2025-03-13 16:29:09'),(30,1,'2025-03-10 12:00:00'),(31,1,'2025-03-09 12:00:00'),(32,1,'2025-02-09 12:00:00'),(33,1,'2025-02-19 12:00:00'),(34,1,'2025-03-13 19:50:23'),(35,1,'2025-03-13 19:50:25'),(36,1,'2025-03-13 19:50:25'),(38,1,'2025-03-13 19:53:15'),(39,1,'2025-03-13 19:55:24'),(40,1,'2025-03-13 20:07:20'),(41,1,'2025-03-15 23:25:37');
/*!40000 ALTER TABLE `health_records` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `health_thresholds`
--

DROP TABLE IF EXISTS `health_thresholds`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `health_thresholds` (
  `threshold_id` int(11) NOT NULL AUTO_INCREMENT,
  `metric_type` enum('blood_pressure_systolic','heart_rate','bmi','temperature') COLLATE utf8mb4_unicode_ci NOT NULL,
  `min_value` decimal(10,2) DEFAULT NULL,
  `max_value` decimal(10,2) DEFAULT NULL,
  `alert_type` enum('warning','emergency') COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`threshold_id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `health_thresholds`
--

LOCK TABLES `health_thresholds` WRITE;
/*!40000 ALTER TABLE `health_thresholds` DISABLE KEYS */;
/*!40000 ALTER TABLE `health_thresholds` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `heart_rate`
--

DROP TABLE IF EXISTS `heart_rate`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `heart_rate` (
  `hr_id` int(11) NOT NULL AUTO_INCREMENT,
  `record_id` int(11) NOT NULL,
  `rate` int(11) DEFAULT NULL,
  PRIMARY KEY (`hr_id`) USING BTREE,
  KEY `record_id` (`record_id`) USING BTREE,
  CONSTRAINT `heart_rate_ibfk_1` FOREIGN KEY (`record_id`) REFERENCES `health_records` (`record_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `heart_rate`
--

LOCK TABLES `heart_rate` WRITE;
/*!40000 ALTER TABLE `heart_rate` DISABLE KEYS */;
/*!40000 ALTER TABLE `heart_rate` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `height_weight`
--

DROP TABLE IF EXISTS `height_weight`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `height_weight` (
  `hw_id` int(11) NOT NULL AUTO_INCREMENT,
  `record_id` int(11) NOT NULL,
  `height` decimal(5,2) DEFAULT NULL,
  `weight` decimal(5,2) DEFAULT NULL,
  `bmi` decimal(4,2) DEFAULT NULL,
  PRIMARY KEY (`hw_id`) USING BTREE,
  KEY `record_id` (`record_id`) USING BTREE,
  CONSTRAINT `height_weight_ibfk_1` FOREIGN KEY (`record_id`) REFERENCES `health_records` (`record_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=34 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `height_weight`
--

LOCK TABLES `height_weight` WRITE;
/*!40000 ALTER TABLE `height_weight` DISABLE KEYS */;
INSERT INTO `height_weight` VALUES (1,1,170.00,60.00,20.76),(2,2,170.00,60.00,20.76),(3,9,170.00,60.00,20.76),(4,10,170.00,60.00,20.76),(5,11,170.00,60.00,20.76),(6,12,170.00,60.00,20.76),(7,13,170.00,60.00,20.76),(8,14,170.00,60.00,20.76),(9,15,170.00,65.00,22.49),(10,16,121.00,12.00,8.20),(11,18,121.00,22.00,15.03),(12,19,121.00,12.00,8.20),(13,20,121.00,12.00,8.20),(14,21,121.00,12.00,8.20),(15,22,121.00,12.00,8.20),(16,23,121.00,12.00,8.20),(17,24,121.00,12.00,8.20),(18,25,121.00,12.00,8.20),(19,26,121.00,12.00,8.20),(20,27,121.00,12.00,8.20),(21,28,121.00,12.00,8.20),(22,29,122.00,22.00,14.78),(23,30,172.00,60.00,20.28),(24,31,172.00,63.00,21.30),(25,32,172.00,63.00,21.30),(26,33,172.00,63.00,21.30),(27,34,121.00,2.00,1.37),(28,35,121.00,22.00,15.03),(29,36,121.00,22.00,15.03),(30,38,123.00,33.00,21.81),(31,39,170.00,34.00,11.76),(32,40,178.00,50.00,15.78),(33,41,175.00,33.00,10.78);
/*!40000 ALTER TABLE `height_weight` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `notifications`
--

DROP TABLE IF EXISTS `notifications`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `notifications` (
  `notification_id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `record_id` int(11) DEFAULT NULL,
  `device_id` int(11) DEFAULT NULL,
  `message` varchar(255) NOT NULL,
  `sent_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `status` enum('sent','failed') NOT NULL DEFAULT 'sent',
  `type` enum('emergency','warning','info') NOT NULL,
  `detection_type` enum('Fall Detected','Walking','Sitting') NOT NULL,
  `is_read` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`notification_id`) USING BTREE,
  KEY `user_id` (`user_id`) USING BTREE,
  KEY `record_id` (`record_id`) USING BTREE,
  KEY `fk_notifications_device` (`device_id`) USING BTREE,
  CONSTRAINT `fk_notifications_device` FOREIGN KEY (`device_id`) REFERENCES `devices` (`device_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_notifications_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE,
  CONSTRAINT `notifications_ibfk_2` FOREIGN KEY (`record_id`) REFERENCES `fall_detection_records` (`record_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `notifications`
--

LOCK TABLES `notifications` WRITE;
/*!40000 ALTER TABLE `notifications` DISABLE KEYS */;
/*!40000 ALTER TABLE `notifications` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `temperature`
--

DROP TABLE IF EXISTS `temperature`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `temperature` (
  `temp_id` int(11) NOT NULL AUTO_INCREMENT,
  `record_id` int(11) NOT NULL,
  `value` decimal(4,1) DEFAULT NULL,
  PRIMARY KEY (`temp_id`) USING BTREE,
  KEY `record_id` (`record_id`) USING BTREE,
  CONSTRAINT `temperature_ibfk_1` FOREIGN KEY (`record_id`) REFERENCES `health_records` (`record_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `temperature`
--

LOCK TABLES `temperature` WRITE;
/*!40000 ALTER TABLE `temperature` DISABLE KEYS */;
/*!40000 ALTER TABLE `temperature` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `users` (
  `user_id` int(11) NOT NULL AUTO_INCREMENT COMMENT '用户id',
  `username` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `password` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `role` enum('elderly','family','admin') COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '用户权限',
  `name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `phone` varchar(15) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `address` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `family_id` int(11) DEFAULT NULL,
  `avatar` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`user_id`) USING BTREE,
  UNIQUE KEY `username` (`username`) USING BTREE,
  KEY `family_id` (`family_id`) USING BTREE,
  CONSTRAINT `family_id` FOREIGN KEY (`family_id`) REFERENCES `families` (`family_id`),
  CONSTRAINT `fk_users_family_id` FOREIGN KEY (`family_id`) REFERENCES `families` (`family_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `users_ibfk_1` FOREIGN KEY (`family_id`) REFERENCES `families` (`family_id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'zwd','scrypt:32768:8:1$OzLdr7LEjRnznA3p$973d512fa0a4bb9d23d28fdd39cc34b6f181c170cfc533686c8b967f926e4cc7931df5afc1c3ae67cee760eb16bab4886bef8addb7c47fcde62323d55b83ec41','admin','zwd','11221122111','zhangweidong0730@outlook.com','南新','2025-03-01 21:32:41',1,'/static/avatars/1.jpg'),(2,'zdl','scrypt:32768:8:1$5QISfHLanHLAH20V$9c6bbc7b670eef32e8356150bfbfb0f8686ab22a4f2a5678e651cad3a9578548a9c6ac5d9ff2d63ea590f3063404eaf3401929593aef0a08f08c083c197e0e0d','elderly','zdl','11111111111','111','南新','2025-03-08 20:27:07',1,'/static/avatars/2.jpg'),(3,'zcj','scrypt:32768:8:1$OJxV5j9XqxolEB8K$867fdc498e3bcf96fc89e070ec339f7e8c427a1b2a83dba34f856de0f30e978a3c437b98f4a6931e70201cf742b4bac803b33e780db1886ad4c99ae0b9dd4ff7','elderly','zcj','12111112222','','','2025-03-10 19:00:11',1,'/static/avatars/3.jpg'),(4,'primary_user','123456','admin','李四','13800138000',NULL,NULL,'2025-03-14 12:33:38',1,NULL),(5,'family_member_1','123456','family','张三','13800138001',NULL,NULL,'2025-03-14 12:33:38',1,NULL),(6,'family_member_2','123456','family','王五','13800138002',NULL,NULL,'2025-03-14 12:33:38',5,NULL),(7,'whn','scrypt:32768:8:1$7gEAr0Nwpu1AAEpm$c1debbc309a23fad646d2bceba26fa3013eef979d37ef1cf351bd261e5b1cf505365e522b484faaf9aeac1efccd81fba0c53f732ad48c37b52854e2eb93589d7','elderly','whn','11111111111','','','2025-03-15 23:28:22',5,NULL);
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-03-16 21:01:08
