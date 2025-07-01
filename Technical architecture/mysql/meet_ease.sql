/*
 Navicat Premium Dump SQL

 Source Server         : localhost_3306
 Source Server Type    : MySQL
 Source Server Version : 80013 (8.0.13)
 Source Host           : localhost:3306
 Source Schema         : meet_ease

 Target Server Type    : MySQL
 Target Server Version : 80013 (8.0.13)
 File Encoding         : 65001

 Date: 24/06/2025 17:53:12
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for event
-- ----------------------------
DROP TABLE IF EXISTS `event`;
CREATE TABLE `event`  (
  `event_id` varchar(10) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT '事项',
  `event_name` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '具体细节',
  PRIMARY KEY (`event_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of event
-- ----------------------------

-- ----------------------------
-- Table structure for event_schedule
-- ----------------------------
DROP TABLE IF EXISTS `event_schedule`;
CREATE TABLE `event_schedule`  (
  `schedule_id` varchar(10) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT '事项时间安排',
  `event_id` varchar(10) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '外键约束',
  `weekday` tinyint(4) NULL DEFAULT NULL COMMENT '1 == 周一, ...， 7 == 周日',
  PRIMARY KEY (`schedule_id`) USING BTREE,
  INDEX `matter_foreign_key`(`event_id` ASC) USING BTREE,
  CONSTRAINT `matter_foreign_key` FOREIGN KEY (`event_id`) REFERENCES `event` (`event_id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of event_schedule
-- ----------------------------

-- ----------------------------
-- Table structure for invitations
-- ----------------------------
DROP TABLE IF EXISTS `invitations`;
CREATE TABLE `invitations`  (
  `invitation_id` varchar(5) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `org_id` varchar(5) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `inviter_id` varchar(11) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `invitee_id` varchar(11) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `status` int(11) NULL DEFAULT NULL,
  `create_at` date NULL DEFAULT NULL,
  PRIMARY KEY (`invitation_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of invitations
-- ----------------------------

-- ----------------------------
-- Table structure for meeting_member
-- ----------------------------
DROP TABLE IF EXISTS `meeting_member`;
CREATE TABLE `meeting_member`  (
  `meeting_id` varchar(5) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `user_id` varchar(11) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `role` int(11) NULL DEFAULT NULL,
  PRIMARY KEY (`meeting_id`) USING BTREE,
  INDEX `meeting_user_id`(`user_id` ASC) USING BTREE,
  CONSTRAINT `meeting_id` FOREIGN KEY (`meeting_id`) REFERENCES `meetings` (`meeting_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `meeting_user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of meeting_member
-- ----------------------------

-- ----------------------------
-- Table structure for meetings
-- ----------------------------
DROP TABLE IF EXISTS `meetings`;
CREATE TABLE `meetings`  (
  `meeting_id` varchar(5) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `meeting_time` datetime NULL DEFAULT NULL,
  `org_id` varchar(5) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `status` int(11) NULL DEFAULT NULL,
  `creator` varchar(11) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  PRIMARY KEY (`meeting_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of meetings
-- ----------------------------

-- ----------------------------
-- Table structure for organization_memebers
-- ----------------------------
DROP TABLE IF EXISTS `organization_memebers`;
CREATE TABLE `organization_memebers`  (
  `org_id` varchar(5) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT '组织ID',
  `user_id` varchar(11) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '组织成员',
  `join_at` date NULL DEFAULT NULL,
  `role` enum('owner','member') CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  PRIMARY KEY (`org_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of organization_memebers
-- ----------------------------

-- ----------------------------
-- Table structure for organizations
-- ----------------------------
DROP TABLE IF EXISTS `organizations`;
CREATE TABLE `organizations`  (
  `org_id` varchar(5) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT '组织ID',
  `org_name` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '组织名',
  `owner_id` varchar(11) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '组织创建者',
  `create_at` date NULL DEFAULT NULL COMMENT '创建日期',
  `status` int(11) NULL DEFAULT NULL COMMENT '组织的状态',
  PRIMARY KEY (`org_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of organizations
-- ----------------------------

-- ----------------------------
-- Table structure for user_event
-- ----------------------------
DROP TABLE IF EXISTS `user_event`;
CREATE TABLE `user_event`  (
  `id` varchar(10) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT '用户对应的事项',
  `user_id` varchar(10) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '用户id',
  `event_id` varchar(10) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `user_matter_userId_foreign_key`(`user_id` ASC) USING BTREE,
  INDEX `user_matter_matterId_foreign_key`(`event_id` ASC) USING BTREE,
  CONSTRAINT `user_matter_matterId_foreign_key` FOREIGN KEY (`event_id`) REFERENCES `event` (`event_id`) ON DELETE SET NULL ON UPDATE SET NULL,
  CONSTRAINT `user_matter_userId_foreign_key` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE SET NULL ON UPDATE SET NULL
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of user_event
-- ----------------------------

-- ----------------------------
-- Table structure for users
-- ----------------------------
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users`  (
  `user_id` varchar(11) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT '用户手机号',
  `name` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `password` varchar(100) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  PRIMARY KEY (`user_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of users
-- ----------------------------

SET FOREIGN_KEY_CHECKS = 1;
