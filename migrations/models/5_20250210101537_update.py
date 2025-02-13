from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `knowledge_bases` MODIFY COLUMN `type` INT NOT NULL  COMMENT '类型: 0-私有 1-公开' DEFAULT 0;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `knowledge_bases` MODIFY COLUMN `type` INT NOT NULL  COMMENT '类型: 0-免费 1-付费' DEFAULT 0;"""
