from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `note` ADD `content` LONGTEXT   COMMENT '内容';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `note` DROP COLUMN `content`;"""
