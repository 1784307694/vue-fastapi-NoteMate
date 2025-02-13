from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `auditlog` ADD `host` VARCHAR(255) NOT NULL  COMMENT '请求ip' DEFAULT '';
        ALTER TABLE `auditlog` ADD INDEX `idx_auditlog_host_1fce2e` (`host`);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `auditlog` DROP INDEX `idx_auditlog_host_1fce2e`;
        ALTER TABLE `auditlog` DROP COLUMN `host`;"""
