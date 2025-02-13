from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `note` ADD `introduction` LONGTEXT   COMMENT '简介';
        ALTER TABLE `note` ADD `cover` VARCHAR(255)   COMMENT '封面';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `note` DROP COLUMN `introduction`;
        ALTER TABLE `note` DROP COLUMN `cover`;"""
