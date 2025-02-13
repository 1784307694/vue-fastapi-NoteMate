from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `knowledgebases` RENAME TO `knowledge_bases`;
        ALTER TABLE `knowledge_bases` ADD `type` INT NOT NULL  COMMENT '类型: 0-免费 1-付费' DEFAULT 0;
        ALTER TABLE `note` ADD `knowledge_bases_id` INT NOT NULL  COMMENT '知识库ID';
        ALTER TABLE `note` ADD INDEX `idx_note_knowled_720d49` (`knowledge_bases_id`);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `note` DROP INDEX `idx_note_knowled_720d49`;
        ALTER TABLE `note` DROP COLUMN `knowledge_bases_id`;
        ALTER TABLE `knowledge_bases` RENAME TO `knowledgebases`;
        ALTER TABLE `knowledge_bases` DROP COLUMN `type`;"""
