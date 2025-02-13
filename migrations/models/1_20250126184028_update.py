from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `user` MODIFY COLUMN `phone` VARCHAR(20)   COMMENT '电话';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `user` MODIFY COLUMN `phone` VARCHAR(20) NOT NULL  COMMENT '电话';"""
