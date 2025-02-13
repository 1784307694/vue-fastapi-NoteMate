from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `account` (
    `id` BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `created_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `user_id` INT NOT NULL UNIQUE COMMENT '用户ID',
    `balance` DECIMAL(18,2) NOT NULL  COMMENT '账户余额' DEFAULT 0,
    `frozen_amount` DECIMAL(18,2) NOT NULL  COMMENT '冻结金额' DEFAULT 0,
    `status` VARCHAR(9) NOT NULL  COMMENT '账户状态' DEFAULT 'NORMAL',
    KEY `idx_account_created_028865` (`created_at`),
    KEY `idx_account_updated_63b235` (`updated_at`),
    KEY `idx_account_user_id_6b740d` (`user_id`),
    KEY `idx_account_status_d97dc0` (`status`)
) CHARACTER SET utf8mb4 COMMENT='账户表 - 用户资金账户';
CREATE TABLE IF NOT EXISTS `account_flow` (
    `id` BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `created_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `account_id` INT NOT NULL  COMMENT '账户ID',
    `user_id` INT NOT NULL  COMMENT '用户ID',
    `order_no` VARCHAR(32) NOT NULL  COMMENT '关联订单号',
    `amount` DECIMAL(18,2) NOT NULL  COMMENT '变动金额',
    `balance` DECIMAL(18,2) NOT NULL  COMMENT '变动后余额',
    `flow_type` VARCHAR(8) NOT NULL  COMMENT '流水类型',
    `direction` VARCHAR(3) NOT NULL  COMMENT '资金方向: IN-收入 OUT-支出',
    `remark` VARCHAR(255)   COMMENT '流水备注',
    KEY `idx_account_flo_created_0b0258` (`created_at`),
    KEY `idx_account_flo_updated_6b8bb7` (`updated_at`),
    KEY `idx_account_flo_account_21ba8c` (`account_id`),
    KEY `idx_account_flo_user_id_21a195` (`user_id`),
    KEY `idx_account_flo_order_n_885753` (`order_no`),
    KEY `idx_account_flo_flow_ty_e74f78` (`flow_type`),
    KEY `idx_account_flo_directi_0f39b9` (`direction`)
) CHARACTER SET utf8mb4 COMMENT='账户流水表';
CREATE TABLE IF NOT EXISTS `api` (
    `id` BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `created_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `path` VARCHAR(100) NOT NULL  COMMENT 'API路径',
    `method` VARCHAR(6) NOT NULL  COMMENT '请求方法',
    `summary` VARCHAR(500) NOT NULL  COMMENT '请求简介',
    `tags` VARCHAR(100) NOT NULL  COMMENT 'API标签',
    KEY `idx_api_created_78d19f` (`created_at`),
    KEY `idx_api_updated_643c8b` (`updated_at`),
    KEY `idx_api_path_9ed611` (`path`),
    KEY `idx_api_method_a46dfb` (`method`),
    KEY `idx_api_summary_400f73` (`summary`),
    KEY `idx_api_tags_04ae27` (`tags`)
) CHARACTER SET utf8mb4 COMMENT='API模型';
CREATE TABLE IF NOT EXISTS `auditlog` (
    `id` BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `created_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `ip` VARCHAR(64)   COMMENT 'IP地址',
    `user_id` INT NOT NULL  COMMENT '用户ID',
    `username` VARCHAR(64) NOT NULL  COMMENT '用户名称' DEFAULT '',
    `module` VARCHAR(64) NOT NULL  COMMENT '功能模块' DEFAULT '',
    `summary` VARCHAR(128) NOT NULL  COMMENT '请求描述' DEFAULT '',
    `method` VARCHAR(10) NOT NULL  COMMENT '请求方法' DEFAULT '',
    `path` VARCHAR(255) NOT NULL  COMMENT '请求路径' DEFAULT '',
    `status` INT NOT NULL  COMMENT '状态码' DEFAULT -1,
    `response_time` INT NOT NULL  COMMENT '响应时间(单位ms)' DEFAULT 0,
    KEY `idx_auditlog_created_cc33d0` (`created_at`),
    KEY `idx_auditlog_updated_2f871f` (`updated_at`),
    KEY `idx_auditlog_user_id_4b93fa` (`user_id`),
    KEY `idx_auditlog_usernam_b187b3` (`username`),
    KEY `idx_auditlog_module_04058b` (`module`),
    KEY `idx_auditlog_summary_3e27da` (`summary`),
    KEY `idx_auditlog_method_4270a2` (`method`),
    KEY `idx_auditlog_path_b99502` (`path`),
    KEY `idx_auditlog_status_2a72d2` (`status`),
    KEY `idx_auditlog_respons_8caa87` (`response_time`)
) CHARACTER SET utf8mb4 COMMENT='审计日志模型';
CREATE TABLE IF NOT EXISTS `comment` (
    `id` BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `created_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `note_id` INT NOT NULL  COMMENT '笔记ID',
    `user_id` INT NOT NULL  COMMENT '评论用户ID',
    `content` LONGTEXT NOT NULL  COMMENT '评论内容',
    `parent_id` INT   COMMENT '父评论ID',
    `like_count` INT NOT NULL  COMMENT '点赞数' DEFAULT 0,
    `root_id` INT   COMMENT '根评论ID',
    KEY `idx_comment_created_061f12` (`created_at`),
    KEY `idx_comment_updated_efaa22` (`updated_at`),
    KEY `idx_comment_note_id_70ee15` (`note_id`),
    KEY `idx_comment_user_id_059151` (`user_id`),
    KEY `idx_comment_parent__d09e62` (`parent_id`),
    KEY `idx_comment_root_id_6dfb38` (`root_id`)
) CHARACTER SET utf8mb4 COMMENT='评论表';
CREATE TABLE IF NOT EXISTS `menu` (
    `id` BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `created_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `name` VARCHAR(20) NOT NULL  COMMENT '菜单名称',
    `remark` JSON   COMMENT '保留字段',
    `menu_type` VARCHAR(7)   COMMENT '菜单类型',
    `icon` VARCHAR(100)   COMMENT '菜单图标',
    `path` VARCHAR(100) NOT NULL  COMMENT '菜单路径',
    `order` INT NOT NULL  COMMENT '排序' DEFAULT 0,
    `parent_id` INT NOT NULL  COMMENT '父菜单ID' DEFAULT 0,
    `is_hidden` BOOL NOT NULL  COMMENT '是否隐藏' DEFAULT 0,
    `component` VARCHAR(100) NOT NULL  COMMENT '组件',
    `keepalive` BOOL NOT NULL  COMMENT '存活' DEFAULT 1,
    `redirect` VARCHAR(100)   COMMENT '重定向',
    KEY `idx_menu_created_b6922b` (`created_at`),
    KEY `idx_menu_updated_e6b0a1` (`updated_at`),
    KEY `idx_menu_name_b9b853` (`name`),
    KEY `idx_menu_path_bf95b2` (`path`),
    KEY `idx_menu_order_606068` (`order`),
    KEY `idx_menu_parent__bebd15` (`parent_id`)
) CHARACTER SET utf8mb4 COMMENT='菜单模型';
CREATE TABLE IF NOT EXISTS `note` (
    `id` BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `created_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `user_id` INT NOT NULL  COMMENT '作者ID',
    `title` VARCHAR(200) NOT NULL  COMMENT '标题',
    `type` INT NOT NULL  COMMENT '类型: 0-免费 1-付费' DEFAULT 0,
    `price` DECIMAL(10,2) NOT NULL  COMMENT '价格' DEFAULT 0,
    `status` INT NOT NULL  COMMENT '状态: 0-私有 1-公开 2-审核中' DEFAULT 0,
    `view_count` INT NOT NULL  COMMENT '浏览次数' DEFAULT 0,
    `like_count` INT NOT NULL  COMMENT '点赞次数' DEFAULT 0,
    `buy_count` INT NOT NULL  COMMENT '购买次数' DEFAULT 0,
    KEY `idx_note_created_faed43` (`created_at`),
    KEY `idx_note_updated_b64cfc` (`updated_at`),
    KEY `idx_note_user_id_25080a` (`user_id`)
) CHARACTER SET utf8mb4 COMMENT='笔记表';
CREATE TABLE IF NOT EXISTS `note_collection` (
    `id` BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `created_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `user_id` INT NOT NULL  COMMENT '用户ID',
    `note_id` INT NOT NULL  COMMENT '笔记ID',
    UNIQUE KEY `uid_note_collec_user_id_7b0ce1` (`user_id`, `note_id`),
    KEY `idx_note_collec_created_921139` (`created_at`),
    KEY `idx_note_collec_updated_ac0b37` (`updated_at`),
    KEY `idx_note_collec_user_id_f5e2d9` (`user_id`),
    KEY `idx_note_collec_note_id_2a049e` (`note_id`)
) CHARACTER SET utf8mb4 COMMENT='笔记收藏表';
CREATE TABLE IF NOT EXISTS `pay_channel` (
    `id` BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `created_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `name` VARCHAR(50) NOT NULL  COMMENT '渠道名称',
    `code` VARCHAR(50) NOT NULL UNIQUE COMMENT '渠道编码',
    `channel_type` VARCHAR(6) NOT NULL  COMMENT '渠道类型',
    `config` JSON NOT NULL  COMMENT '渠道配置',
    `is_active` BOOL NOT NULL  COMMENT '是否启用' DEFAULT 1,
    KEY `idx_pay_channel_created_35fdbd` (`created_at`),
    KEY `idx_pay_channel_updated_91eb19` (`updated_at`),
    KEY `idx_pay_channel_channel_513e67` (`channel_type`)
) CHARACTER SET utf8mb4 COMMENT='支付渠道表';
CREATE TABLE IF NOT EXISTS `role` (
    `id` BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `created_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `name` VARCHAR(20) NOT NULL UNIQUE COMMENT '角色名称',
    `desc` VARCHAR(500)   COMMENT '角色描述',
    KEY `idx_role_created_7f5f71` (`created_at`),
    KEY `idx_role_updated_5dd337` (`updated_at`),
    KEY `idx_role_name_e5618b` (`name`)
) CHARACTER SET utf8mb4 COMMENT='角色模型';
CREATE TABLE IF NOT EXISTS `tradeorder` (
    `id` BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `created_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `order_no` VARCHAR(32) NOT NULL UNIQUE COMMENT '订单号',
    `user_id` INT NOT NULL  COMMENT '用户ID',
    `account_id` INT NOT NULL  COMMENT '账户ID',
    `target_user_id` INT   COMMENT '目标用户ID',
    `target_account_id` INT   COMMENT '目标账户ID',
    `amount` DECIMAL(18,2) NOT NULL  COMMENT '交易金额',
    `channel_id` INT NOT NULL  COMMENT '支付渠道ID',
    `trade_type` VARCHAR(8) NOT NULL  COMMENT '交易类型',
    `status` VARCHAR(9) NOT NULL  COMMENT '订单状态',
    `remark` VARCHAR(255)   COMMENT '交易备注',
    `complete_time` DATETIME(6)   COMMENT '完成时间',
    `product_id` INT   COMMENT '商品ID(笔记ID)',
    KEY `idx_tradeorder_created_0e87e9` (`created_at`),
    KEY `idx_tradeorder_updated_e9cc02` (`updated_at`),
    KEY `idx_tradeorder_user_id_984660` (`user_id`),
    KEY `idx_tradeorder_account_494bff` (`account_id`),
    KEY `idx_tradeorder_target__2c4b16` (`target_user_id`),
    KEY `idx_tradeorder_target__6a3f73` (`target_account_id`),
    KEY `idx_tradeorder_channel_dc0c2c` (`channel_id`),
    KEY `idx_tradeorder_trade_t_28a6c4` (`trade_type`),
    KEY `idx_tradeorder_status_b84652` (`status`),
    KEY `idx_tradeorder_product_e82732` (`product_id`)
) CHARACTER SET utf8mb4 COMMENT='交易订单表';
CREATE TABLE IF NOT EXISTS `user` (
    `id` BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `created_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `username` VARCHAR(20) NOT NULL UNIQUE COMMENT '用户名称',
    `alias` VARCHAR(30)   COMMENT '姓名',
    `email` VARCHAR(255)   COMMENT '邮箱',
    `phone` VARCHAR(20) NOT NULL UNIQUE COMMENT '电话',
    `password` VARCHAR(128)   COMMENT '密码',
    `avatar` VARCHAR(255)   COMMENT '头像',
    `bio` LONGTEXT   COMMENT '个人简介',
    `is_active` BOOL NOT NULL  COMMENT '是否激活' DEFAULT 1,
    `is_superuser` BOOL NOT NULL  COMMENT '是否为超级管理员' DEFAULT 0,
    `last_login` DATETIME(6)   COMMENT '最后登录时间',
    KEY `idx_user_created_b19d59` (`created_at`),
    KEY `idx_user_updated_dfdb43` (`updated_at`),
    KEY `idx_user_usernam_9987ab` (`username`),
    KEY `idx_user_alias_6f9868` (`alias`),
    KEY `idx_user_email_1b4f1c` (`email`),
    KEY `idx_user_phone_4e3ecc` (`phone`),
    KEY `idx_user_is_acti_83722a` (`is_active`),
    KEY `idx_user_is_supe_b8a218` (`is_superuser`),
    KEY `idx_user_last_lo_af118a` (`last_login`)
) CHARACTER SET utf8mb4 COMMENT='用户模型';
CREATE TABLE IF NOT EXISTS `user_follow` (
    `id` BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `created_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `user_id` INT NOT NULL  COMMENT '关注者ID',
    `followed_id` INT NOT NULL  COMMENT '被关注者ID',
    UNIQUE KEY `uid_user_follow_user_id_a1a867` (`user_id`, `followed_id`),
    KEY `idx_user_follow_created_ba844f` (`created_at`),
    KEY `idx_user_follow_updated_74a947` (`updated_at`),
    KEY `idx_user_follow_user_id_12533b` (`user_id`),
    KEY `idx_user_follow_followe_1656a1` (`followed_id`)
) CHARACTER SET utf8mb4 COMMENT='用户关注关系表';
CREATE TABLE IF NOT EXISTS `aerich` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `version` VARCHAR(255) NOT NULL,
    `app` VARCHAR(100) NOT NULL,
    `content` JSON NOT NULL
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `role_api` (
    `role_id` BIGINT NOT NULL,
    `api_id` BIGINT NOT NULL,
    FOREIGN KEY (`role_id`) REFERENCES `role` (`id`) ON DELETE CASCADE,
    FOREIGN KEY (`api_id`) REFERENCES `api` (`id`) ON DELETE CASCADE,
    UNIQUE KEY `uidx_role_api_role_id_ba4286` (`role_id`, `api_id`)
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `role_menu` (
    `role_id` BIGINT NOT NULL,
    `menu_id` BIGINT NOT NULL,
    FOREIGN KEY (`role_id`) REFERENCES `role` (`id`) ON DELETE CASCADE,
    FOREIGN KEY (`menu_id`) REFERENCES `menu` (`id`) ON DELETE CASCADE,
    UNIQUE KEY `uidx_role_menu_role_id_90801c` (`role_id`, `menu_id`)
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `user_role` (
    `user_id` BIGINT NOT NULL,
    `role_id` BIGINT NOT NULL,
    FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE,
    FOREIGN KEY (`role_id`) REFERENCES `role` (`id`) ON DELETE CASCADE,
    UNIQUE KEY `uidx_user_role_user_id_d0bad3` (`user_id`, `role_id`)
) CHARACTER SET utf8mb4;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
