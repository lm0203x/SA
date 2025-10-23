-- ========================================
-- 预警系统数据表创建脚本
-- 作者: Claude AI Assistant  
-- 创建时间: 2025-10-21
-- 说明: 创建预警规则和预警记录相关数据表
-- ========================================

-- 使用数据库（请根据实际情况修改数据库名）
-- USE your_database_name;

-- ========================================
-- 1. 创建预警规则表 (alert_rules)
-- ========================================

CREATE TABLE IF NOT EXISTS `alert_rules` (
    -- 基础字段
    `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '规则ID',
    `rule_name` VARCHAR(100) NOT NULL COMMENT '规则名称',
    `ts_code` VARCHAR(20) NOT NULL COMMENT '股票代码',
    
    -- 规则配置
    `rule_type` VARCHAR(50) NOT NULL COMMENT '规则类型',
    `condition_type` VARCHAR(20) NOT NULL COMMENT '条件类型', 
    `threshold_value` DECIMAL(15,4) NOT NULL COMMENT '阈值',
    `comparison_operator` VARCHAR(10) NOT NULL COMMENT '比较运算符',
    
    -- 预警设置
    `alert_level` VARCHAR(20) DEFAULT 'medium' COMMENT '预警级别',
    `alert_message_template` TEXT COMMENT '预警消息模板',
    
    -- 状态管理
    `is_enabled` BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    `is_active` BOOLEAN DEFAULT TRUE COMMENT '是否活跃',
    
    -- 统计信息
    `trigger_count` INT DEFAULT 0 COMMENT '触发次数',
    `last_triggered_at` DATETIME NULL COMMENT '最后触发时间',
    
    -- 时间戳
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    -- 扩展配置
    `extra_config` TEXT COMMENT '扩展配置JSON'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='预警规则表';

-- ========================================
-- 2. 创建预警记录表 (risk_alerts) 
-- ========================================

CREATE TABLE IF NOT EXISTS `risk_alerts` (
    -- 基础字段
    `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '预警ID',
    `ts_code` VARCHAR(20) NOT NULL COMMENT '股票代码',
    
    -- 预警信息
    `alert_type` VARCHAR(50) NOT NULL COMMENT '预警类型',
    `alert_level` VARCHAR(20) NOT NULL COMMENT '预警级别',
    `alert_message` TEXT COMMENT '预警消息',
    
    -- 数值信息
    `risk_value` DECIMAL(15,4) NULL COMMENT '风险值',
    `threshold_value` DECIMAL(15,4) NULL COMMENT '阈值',
    `current_price` DECIMAL(10,2) NULL COMMENT '当前价格',
    
    -- 持仓信息
    `position_size` DECIMAL(15,2) NULL COMMENT '持仓数量',
    `portfolio_weight` DECIMAL(8,4) NULL COMMENT '组合权重',
    
    -- 状态管理
    `is_active` BOOLEAN DEFAULT TRUE COMMENT '是否活跃',
    `is_resolved` BOOLEAN DEFAULT FALSE COMMENT '是否已解决',
    
    -- 时间戳
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `resolved_at` DATETIME NULL COMMENT '解决时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='风险预警记录表';

-- ========================================
-- 3. 创建索引 - 预警规则表
-- ========================================

-- 股票代码索引
CREATE INDEX `idx_alert_rules_ts_code` ON `alert_rules` (`ts_code`);

-- 规则类型和启用状态复合索引
CREATE INDEX `idx_alert_rules_type_enabled` ON `alert_rules` (`rule_type`, `is_enabled`);

-- 活跃状态索引
CREATE INDEX `idx_alert_rules_active` ON `alert_rules` (`is_active`);

-- 创建时间索引
CREATE INDEX `idx_alert_rules_created_at` ON `alert_rules` (`created_at`);

-- ========================================
-- 4. 创建索引 - 预警记录表
-- ========================================

-- 股票代码和预警类型复合索引
CREATE INDEX `idx_risk_alerts_ts_code_type` ON `risk_alerts` (`ts_code`, `alert_type`);

-- 预警级别和活跃状态复合索引  
CREATE INDEX `idx_risk_alerts_level_active` ON `risk_alerts` (`alert_level`, `is_active`);

-- 创建时间索引
CREATE INDEX `idx_risk_alerts_created_at` ON `risk_alerts` (`created_at`);

-- ========================================
-- 5. 插入预警规则类型字典数据（可选）
-- ========================================

-- 插入一些示例预警规则，方便测试
INSERT IGNORE INTO `alert_rules` (
    `rule_name`, `ts_code`, `rule_type`, `condition_type`, 
    `threshold_value`, `comparison_operator`, `alert_level`, 
    `alert_message_template`
) VALUES 
(
    '平安银行涨幅超5%预警', 
    '000001.SZ', 
    'price_change_pct', 
    'daily_change', 
    5.0, 
    'gte', 
    'medium',
    '涨跌幅大于等于5.0%，当前涨跌幅：{current_value}%'
),
(
    '平安银行跌幅超3%预警', 
    '000001.SZ', 
    'price_change_pct', 
    'daily_change', 
    -3.0, 
    'lte', 
    'high',
    '涨跌幅小于等于-3.0%，当前涨跌幅：{current_value}%'
),
(
    '平安银行换手率异常预警', 
    '000001.SZ', 
    'turnover_rate', 
    'daily_turnover', 
    10.0, 
    'gt', 
    'medium',
    '换手率大于10.0%，当前换手率：{current_value}%'
);

-- ========================================
-- 6. 查看创建结果
-- ========================================

-- 查看表结构
DESCRIBE `alert_rules`;
DESCRIBE `risk_alerts`;

-- 查看索引
SHOW INDEX FROM `alert_rules`;
SHOW INDEX FROM `risk_alerts`;

-- 查看示例数据
SELECT * FROM `alert_rules` LIMIT 5;
SELECT COUNT(*) as total_rules FROM `alert_rules`;
SELECT COUNT(*) as total_alerts FROM `risk_alerts`;

-- ========================================
-- 7. 权限设置（根据需要）
-- ========================================

-- 如果需要为特定用户授权，请取消注释并修改用户名
-- GRANT SELECT, INSERT, UPDATE, DELETE ON your_database.alert_rules TO 'your_user'@'%';
-- GRANT SELECT, INSERT, UPDATE, DELETE ON your_database.risk_alerts TO 'your_user'@'%';
-- FLUSH PRIVILEGES;

-- ========================================
-- 脚本执行完成
-- ========================================

SELECT 
    'Alert system tables created successfully!' as message,
    NOW() as created_at;
