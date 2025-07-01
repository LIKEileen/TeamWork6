/*
 Navicat Premium Dump SQL

 Source Server         : schedule_planner
 Source Server Type    : SQLite
 Source Server Version : 3045000 (3.45.0)
 Source Schema         : main

 Target Server Type    : SQLite
 Target Server Version : 3045000 (3.45.0)
 File Encoding         : 65001

 Date: 30/06/2025 20:48:33
*/

PRAGMA foreign_keys = false;

-- ----------------------------
-- Table structure for meeting_participants
-- ----------------------------
DROP TABLE IF EXISTS "meeting_participants";
CREATE TABLE "meeting_participants" (
  "id" INTEGER PRIMARY KEY AUTOINCREMENT,
  "meeting_id" INTEGER NOT NULL,
  "user_id" INTEGER NOT NULL,
  "status" TEXT DEFAULT 'pending',
  "is_key_member" BOOLEAN DEFAULT FALSE,
  FOREIGN KEY ("meeting_id") REFERENCES "meetings" ("id") ON DELETE CASCADE ON UPDATE NO ACTION,
  FOREIGN KEY ("user_id") REFERENCES "users" ("id") ON DELETE CASCADE ON UPDATE NO ACTION,
  UNIQUE ("meeting_id" ASC, "user_id" ASC)
);

-- ----------------------------
-- Records of meeting_participants
-- ----------------------------

-- ----------------------------
-- Table structure for meetings
-- ----------------------------
DROP TABLE IF EXISTS "meetings";
CREATE TABLE "meetings" (
  "id" INTEGER PRIMARY KEY AUTOINCREMENT,
  "title" TEXT NOT NULL,
  "description" TEXT,
  "start_time" TEXT NOT NULL,
  "end_time" TEXT NOT NULL,
  "creator_id" INTEGER NOT NULL,
  "min_participants" INTEGER DEFAULT 1,
  FOREIGN KEY ("creator_id") REFERENCES "users" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION
);

-- ----------------------------
-- Records of meetings
-- ----------------------------

-- ----------------------------
-- Table structure for recurring_events
-- ----------------------------
DROP TABLE IF EXISTS "recurring_events";
CREATE TABLE "recurring_events" (
  "id" INTEGER PRIMARY KEY AUTOINCREMENT,
  "user_id" INTEGER NOT NULL,
  "title" TEXT NOT NULL,
  "start_time" TEXT NOT NULL,
  "end_time" TEXT NOT NULL,
  "frequency" TEXT NOT NULL,
  "custom_dates" TEXT,
  "color" TEXT DEFAULT '#409EFF',
  "created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY ("user_id") REFERENCES "users" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION
);

-- ----------------------------
-- Records of recurring_events
-- ----------------------------

-- ----------------------------
-- Table structure for schedule_events
-- ----------------------------
DROP TABLE IF EXISTS "schedule_events";
CREATE TABLE "schedule_events" (
  "id" INTEGER PRIMARY KEY AUTOINCREMENT,
  "user_id" INTEGER NOT NULL,
  "title" TEXT NOT NULL,
  "day" TEXT NOT NULL,
  "start_time" TEXT NOT NULL,
  "end_time" TEXT NOT NULL,
  "color" TEXT DEFAULT '#409EFF',
  "event_type" TEXT DEFAULT 'single',
  "recurring_id" INTEGER,
  "created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  "updated_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY ("user_id") REFERENCES "users" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION,
  FOREIGN KEY ("recurring_id") REFERENCES "recurring_events" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION
);

-- ----------------------------
-- Records of schedule_events
-- ----------------------------

-- ----------------------------
-- Table structure for sqlite_sequence
-- ----------------------------
DROP TABLE IF EXISTS "sqlite_sequence";
CREATE TABLE "sqlite_sequence" (
  "name",
  "seq"
);

-- ----------------------------
-- Records of sqlite_sequence
-- ----------------------------
INSERT INTO "sqlite_sequence" VALUES ('users', 4);

-- ----------------------------
-- Table structure for token_blacklist
-- ----------------------------
DROP TABLE IF EXISTS "token_blacklist";
CREATE TABLE "token_blacklist" (
  "id" INTEGER PRIMARY KEY AUTOINCREMENT,
  "token" TEXT NOT NULL,
  "created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE ("token" ASC)
);

-- ----------------------------
-- Records of token_blacklist
-- ----------------------------

-- ----------------------------
-- Table structure for users
-- ----------------------------
DROP TABLE IF EXISTS "users";
CREATE TABLE "users" (
  "id" INTEGER PRIMARY KEY AUTOINCREMENT,
  "nickname" TEXT NOT NULL,
  "phone" TEXT,
  "email" TEXT NOT NULL,
  "password_hash" TEXT NOT NULL,
  "avatar" TEXT,
  "role" TEXT DEFAULT 'user',
  "created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  "updated_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE ("phone" ASC),
  UNIQUE ("email" ASC)
);

-- ----------------------------
-- Records of users
-- ----------------------------
INSERT INTO "users" VALUES (1, '张教授', '13812345678', 'zhangprofessor@example.com', 'scrypt:32768:8:1$fmLIx99d0SdEHu17$b3ee29887fa50f6ee561e4e97103567cc0ff1c8b87b79df34b0deaff757e8fde401d946f2a75a1673fef420e806cddd3280809fdfca3ee85d49cabc4861997f1', 'https://imgheybox.max-c.com/bbs/2024/09/19/1dc7d8a7978e8e9be26498747ef493ce/thumb.png', 'user', '2025-06-14 16:38:50', '2025-06-14 16:38:50');
INSERT INTO "users" VALUES (2, '李研究员', '13887654321', 'liresearcher@example.com', 'scrypt:32768:8:1$g0jZTMyFzDKee0DH$45e5bb824685b44291efdc54431abd45b7424d0625e25a5b55bfff35aeb62453a7337989919a063785d16940f68dd8a67fe7d43aa09935be111ec49e7efab222', 'https://imgheybox.max-c.com/bbs/2024/09/19/1dc7d8a7978e8e9be26498747ef493ce/thumb.png', 'user', '2025-06-14 16:38:57', '2025-06-14 16:38:57');
INSERT INTO "users" VALUES (3, '王博士', '13999888777', 'wangdoctor@example.com', 'scrypt:32768:8:1$eb03JvdYsOiGYtFu$f9aae646f56e7962346ec26c5bc9f00bf46b20db14ee87991cb45eab51c6af59a44f11be22db474707cc61b722c3c9753e9b19aad74d561c9d198caa5f25f081', 'https://imgheybox.max-c.com/bbs/2024/09/19/1dc7d8a7978e8e9be26498747ef493ce/thumb.png', 'user', '2025-06-14 16:39:04', '2025-06-14 16:39:04');
INSERT INTO "users" VALUES (4, '陈同学', '13666555444', 'chenstudent@example.com', 'scrypt:32768:8:1$3wSOXluTql6ODvJU$a312f4cdfd6c24be7c4fecfb4511395a81e7f7c2b30d5590c20d1d90f30fc786825fc8daf23203c2302a4f9b31c5dd3d12cd4f4c23f36987b8c6768071ad3308', 'https://imgheybox.max-c.com/bbs/2024/09/19/1dc7d8a7978e8e9be26498747ef493ce/thumb.png', 'user', '2025-06-14 16:39:12', '2025-06-14 16:39:12');

-- ----------------------------
-- Table structure for verification_codes
-- ----------------------------
DROP TABLE IF EXISTS "verification_codes";
CREATE TABLE "verification_codes" (
  "id" INTEGER PRIMARY KEY AUTOINCREMENT,
  "email" TEXT NOT NULL,
  "code" TEXT NOT NULL,
  "created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  "expires_at" TIMESTAMP NOT NULL
);

-- ----------------------------
-- Records of verification_codes
-- ----------------------------

-- ----------------------------
-- Indexes structure for table meeting_participants
-- ----------------------------
CREATE INDEX "idx_participant_meeting"
ON "meeting_participants" (
  "meeting_id" ASC
);
CREATE INDEX "idx_participant_user"
ON "meeting_participants" (
  "user_id" ASC
);

-- ----------------------------
-- Indexes structure for table meetings
-- ----------------------------
CREATE INDEX "idx_meeting_creator"
ON "meetings" (
  "creator_id" ASC
);

-- ----------------------------
-- Indexes structure for table recurring_events
-- ----------------------------
CREATE INDEX "idx_recurring_user_id"
ON "recurring_events" (
  "user_id" ASC
);

-- ----------------------------
-- Indexes structure for table schedule_events
-- ----------------------------
CREATE INDEX "idx_schedule_day"
ON "schedule_events" (
  "day" ASC
);
CREATE INDEX "idx_schedule_user_id"
ON "schedule_events" (
  "user_id" ASC
);

-- ----------------------------
-- Indexes structure for table token_blacklist
-- ----------------------------
CREATE INDEX "idx_token_blacklist"
ON "token_blacklist" (
  "token" ASC
);

-- ----------------------------
-- Auto increment value for users
-- ----------------------------
UPDATE "sqlite_sequence" SET seq = 4 WHERE name = 'users';

-- ----------------------------
-- Indexes structure for table users
-- ----------------------------
CREATE INDEX "idx_users_email"
ON "users" (
  "email" ASC
);
CREATE INDEX "idx_users_phone"
ON "users" (
  "phone" ASC
);

-- ----------------------------
-- Indexes structure for table verification_codes
-- ----------------------------
CREATE INDEX "idx_verification_email"
ON "verification_codes" (
  "email" ASC
);

PRAGMA foreign_keys = true;
