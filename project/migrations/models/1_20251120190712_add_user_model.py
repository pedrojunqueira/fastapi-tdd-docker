from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "textsummary" ADD "user_id" INT;
        CREATE TABLE IF NOT EXISTS "user" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "azure_oid" VARCHAR(255) UNIQUE,
    "email" VARCHAR(255) NOT NULL UNIQUE,
    "role" VARCHAR(6) NOT NULL DEFAULT 'reader',
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "last_login" TIMESTAMPTZ
);
COMMENT ON COLUMN "user"."role" IS 'ADMIN: admin\nWRITER: writer\nREADER: reader';
        ALTER TABLE "textsummary" ADD CONSTRAINT "fk_textsumm_user_5a73c430" FOREIGN KEY ("user_id") REFERENCES "user" ("id") ON DELETE CASCADE;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "textsummary" DROP CONSTRAINT IF EXISTS "fk_textsumm_user_5a73c430";
        ALTER TABLE "textsummary" DROP COLUMN "user_id";
        DROP TABLE IF EXISTS "user";"""
