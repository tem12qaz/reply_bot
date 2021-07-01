-- upgrade --
CREATE TABLE IF NOT EXISTS "chat" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "telegram_id" BIGINT NOT NULL UNIQUE
);
CREATE INDEX IF NOT EXISTS "idx_chat_telegra_9bf690" ON "chat" ("telegram_id");
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(20) NOT NULL,
    "content" JSONB NOT NULL
);
