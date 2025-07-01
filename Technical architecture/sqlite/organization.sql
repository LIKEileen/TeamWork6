/*
 Navicat Premium Dump SQL

 Source Server         : organization
 Source Server Type    : SQLite
 Source Server Version : 3045000 (3.45.0)
 Source Schema         : main

 Target Server Type    : SQLite
 Target Server Version : 3045000 (3.45.0)
 File Encoding         : 65001

 Date: 30/06/2025 20:48:06
*/

PRAGMA foreign_keys = false;

-- ----------------------------
-- Table structure for invitations
-- ----------------------------
DROP TABLE IF EXISTS "invitations";
CREATE TABLE "invitations" (
  "id" TEXT,
  "org_id" TEXT NOT NULL,
  "inviter_id" TEXT NOT NULL,
  "invitee_id" TEXT NOT NULL,
  "message" TEXT,
  "status" TEXT DEFAULT 'pending',
  "created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY ("id"),
  FOREIGN KEY ("org_id") REFERENCES "organizations" ("id") ON DELETE CASCADE ON UPDATE NO ACTION
);

-- ----------------------------
-- Records of invitations
-- ----------------------------
INSERT INTO "invitations" VALUES ('inv_c6da5e1f', 'org_f97ac339', '1', '2', NULL, 'accepted', '2025-06-14 16:41:22');

-- ----------------------------
-- Table structure for join_requests
-- ----------------------------
DROP TABLE IF EXISTS "join_requests";
CREATE TABLE "join_requests" (
  "id" TEXT,
  "org_id" TEXT NOT NULL,
  "user_id" TEXT NOT NULL,
  "message" TEXT,
  "status" TEXT DEFAULT 'pending',
  "created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY ("id"),
  FOREIGN KEY ("org_id") REFERENCES "organizations" ("id") ON DELETE CASCADE ON UPDATE NO ACTION
);

-- ----------------------------
-- Records of join_requests
-- ----------------------------
INSERT INTO "join_requests" VALUES ('req_204f3b3e', 'org_f97ac339', '4', '我是人工智能专业的学生，希望能够加入贵组织学习交流', 'accepted', '2025-06-14 16:46:38');

-- ----------------------------
-- Table structure for organization_members
-- ----------------------------
DROP TABLE IF EXISTS "organization_members";
CREATE TABLE "organization_members" (
  "id" INTEGER PRIMARY KEY AUTOINCREMENT,
  "org_id" TEXT NOT NULL,
  "user_id" TEXT NOT NULL,
  "role" TEXT DEFAULT '',
  "joined_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY ("org_id") REFERENCES "organizations" ("id") ON DELETE CASCADE ON UPDATE NO ACTION,
  UNIQUE ("org_id" ASC, "user_id" ASC)
);

-- ----------------------------
-- Records of organization_members
-- ----------------------------
INSERT INTO "organization_members" VALUES (1, 'org_f97ac339', '1', 'creator', '2025-06-14 16:39:54');
INSERT INTO "organization_members" VALUES (2, 'org_f97ac339', '2', 'admin', '2025-06-14 16:51:54');
INSERT INTO "organization_members" VALUES (3, 'org_f97ac339', '4', '', '2025-06-14 17:13:25');

-- ----------------------------
-- Table structure for organizations
-- ----------------------------
DROP TABLE IF EXISTS "organizations";
CREATE TABLE "organizations" (
  "id" TEXT,
  "name" TEXT NOT NULL,
  "creator_id" TEXT NOT NULL,
  "created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY ("id")
);

-- ----------------------------
-- Records of organizations
-- ----------------------------
INSERT INTO "organizations" VALUES ('org_f97ac339', '高级数据科学研究组', '1', '2025-06-14 16:39:54');

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
INSERT INTO "sqlite_sequence" VALUES ('organization_members', 3);

-- ----------------------------
-- Auto increment value for organization_members
-- ----------------------------
UPDATE "sqlite_sequence" SET seq = 3 WHERE name = 'organization_members';

PRAGMA foreign_keys = true;
