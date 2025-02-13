from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `note` DROP INDEX `idx_note_knowled_720d49`;
        ALTER TABLE `note` DROP INDEX `idx_note_user_id_25080a`;
        ALTER TABLE `note` MODIFY COLUMN `user_id` BIGINT NOT NULL  COMMENT '作者';
        ALTER TABLE `note` MODIFY COLUMN `user_id` BIGINT NOT NULL  COMMENT '作者';
        ALTER TABLE `note` MODIFY COLUMN `knowledge_bases_id` BIGINT NOT NULL  COMMENT '所属知识库';
        ALTER TABLE `note` MODIFY COLUMN `knowledge_bases_id` BIGINT NOT NULL  COMMENT '所属知识库';
        ALTER TABLE `note` ADD CONSTRAINT `fk_note_user_00584777` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE;
        ALTER TABLE `note` ADD CONSTRAINT `fk_note_knowledg_03754426` FOREIGN KEY (`knowledge_bases_id`) REFERENCES `knowledge_bases` (`id`) ON DELETE CASCADE;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `note` DROP FOREIGN KEY `fk_note_knowledg_03754426`;
        ALTER TABLE `note` DROP FOREIGN KEY `fk_note_user_00584777`;
        ALTER TABLE `note` MODIFY COLUMN `user_id` INT NOT NULL  COMMENT '作者ID';
        ALTER TABLE `note` MODIFY COLUMN `user_id` INT NOT NULL  COMMENT '作者ID';
        ALTER TABLE `note` MODIFY COLUMN `knowledge_bases_id` INT NOT NULL  COMMENT '知识库ID';
        ALTER TABLE `note` MODIFY COLUMN `knowledge_bases_id` INT NOT NULL  COMMENT '知识库ID';
        ALTER TABLE `note` ADD INDEX `idx_note_user_id_25080a` (`user_id`);
        ALTER TABLE `note` ADD INDEX `idx_note_knowled_720d49` (`knowledge_bases_id`);"""
