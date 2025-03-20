-- 修改health_records表结构
ALTER TABLE `health_records` 
CHANGE COLUMN `elderly_id` `user_id` int(11) NOT NULL,
ADD CONSTRAINT `health_records_ibfk_1` 
FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`);

-- 修改health_thresholds表结构
ALTER TABLE `health_thresholds` 
CHANGE COLUMN `elderly_id` `user_id` int(11) NOT NULL COMMENT '用户ID',
ADD CONSTRAINT `health_thresholds_ibfk_1` 
FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`);

-- 为health_records表添加索引
ALTER TABLE `health_records` 
ADD INDEX `idx_user_time` (`user_id`, `recorded_at`);

-- 为health_thresholds表添加索引
ALTER TABLE `health_thresholds` 
ADD INDEX `idx_user_metric` (`user_id`, `metric_type`); 