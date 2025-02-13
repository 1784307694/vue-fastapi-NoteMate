from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `knowledgebases` (
    `id` BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `created_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `user_id` INT NOT NULL  COMMENT '用户ID',
    `name` VARCHAR(200) NOT NULL  COMMENT '标题',
    KEY `idx_knowledgeba_created_d333a6` (`created_at`),
    KEY `idx_knowledgeba_updated_ff0fa5` (`updated_at`),
    KEY `idx_knowledgeba_user_id_e3e589` (`user_id`)
) CHARACTER SET utf8mb4 COMMENT='知识库表';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS `knowledgebases`;"""
