# TeamWork6

## 前言

- 产品服务器地址：47.99.171.202
- 使用方式：
访问网址
http://47.99.171.202:5173/login
- 测试账号：
手机号：13111111114
密码：qwerty
组织：数据研2024
也可以注册新账号进行体验～


## 注意事项
导入的Excel表格应以如下的形式组织: 
| 标题   | 日期         | 开始时间  | 结束时间  | 颜色      |
| ---- | ---------- | ----- | ----- | ------- |
| 高等数学 | 2025-06-17 | 08:00 | 09:30 | #409EFF |
| 大学物理 | 2025-06-17 | 10:00 | 11:30 | #67C23A |
| 程序设计 | 2025-06-17 | 14:00 | 15:30 | #E6A23C |
| 英语听说 | 2025-06-18 | 08:00 | 09:30 | #F56C6C |
| 数据结构 | 2025-06-18 | 10:00 | 11:30 | #909399 |


每一行表示一门课程或活动的时间安排，具体字段说明如下：

- 标题：活动或课程的名称

- 日期：安排的日期

- 开始时间 / 结束时间：该项的起止时间

- 颜色：用于表示该项的标识颜色



# EasyMeeting - 智能会议预约与日程管理系统

<div align="center">

![EasyMeeting Logo](https://img.shields.io/badge/EasyMeeting-智能会议预约-blue?style=for-the-badge&logo=calendar)
![Vue.js](https://img.shields.io/badge/Vue.js-3.5.13-4FC08D?style=flat-square&logo=vue.js)
![Flask](https://img.shields.io/badge/Flask-2.0+-000000?style=flat-square&logo=flask)
![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat-square&logo=python)
![Element Plus](https://img.shields.io/badge/Element%20Plus-2.9.8-409EFF?style=flat-square)

**一个现代化的智能会议预约与日程管理系统，支持AI助手、组织管理、智能时间推荐等功能**
</div>

## 📋 目录

- [项目简介](#项目简介)
- [功能特性](#功能特性)
- [技术架构](#技术架构)
- [项目结构](#项目结构)
- [快速开始](#快速开始)
- [API文档](#api文档)
- [部署指南](#部署指南)

## 🎯 项目简介

EasyMeeting 是一个基于 Vue.js 3 + Flask 的现代化智能会议预约与日程管理系统。该系统集成了AI助手、组织管理、智能时间推荐等先进功能，旨在为企业、团队和个人提供高效便捷的会议管理和日程安排解决方案。

### 核心价值

- **智能化**：集成AI助手，支持自然语言交互和智能时间推荐
- **协作性**：完善的组织管理功能，支持团队协作
- **可视化**：直观的热力图展示和日程管理界面
- **易用性**：现代化的UI设计，操作简单直观
- **扩展性**：模块化架构，易于扩展和维护

## ✨ 功能特性

### 🔐 用户认证系统
- **多方式登录**：支持手机号、邮箱登录
- **安全认证**：JWT Token认证机制
- **密码管理**：密码重置、手机号绑定
- **用户信息管理**：头像上传、个人信息编辑

### 📅 智能日程管理
- **可视化日程**：热力图展示，直观查看时间安排
- **事件管理**：添加、编辑、删除日程事件
- **时间冲突检测**：自动检测并提醒时间冲突
- **Excel导入**：支持Excel文件批量导入日程
- **颜色分类**：自定义事件颜色，便于分类管理

### 🤝 会议预约系统
- **智能时间推荐**：基于参与者空闲时间自动推荐最佳会议时间
- **会议创建**：支持创建单次和重复会议
- **参与者管理**：邀请、移除会议参与者
- **会议详情**：完整的会议信息管理

### 🏢 组织管理
- **组织创建**：创建和管理多个组织
- **成员管理**：邀请、移除组织成员
- **权限控制**：创建者、管理员、普通成员三级权限
- **组织邀请**：支持邀请码和直接邀请

### 🤖 AI智能助手
- **自然语言交互**：支持中文自然语言查询
- **智能查询**：查询会议安排、空闲时间
- **智能推荐**：基于历史数据推荐最佳时间
- **函数调用**：支持工具函数调用，执行具体任务

### 📱 现代化界面
- **响应式设计**：适配各种设备屏幕
- **主题切换**：支持明暗主题切换
- **组件化设计**：基于Element Plus组件库
- **用户体验优化**：流畅的交互体验

## 🏗️ 技术架构

### 前端技术栈
- **框架**：Vue.js 3.5.13
- **构建工具**：Vite 6.2.0
- **UI组件库**：Element Plus 2.9.8
- **状态管理**：Pinia 3.0.2
- **路由管理**：Vue Router 4.5.0
- **HTTP客户端**：Axios 1.8.4
- **日期处理**：Day.js 1.11.13
- **图片裁剪**：Cropper.js 1.6.2
- **Markdown渲染**：Marked 15.0.11
- **AI集成**：OpenAI 4.96.0

### 后端技术栈
- **框架**：Flask 2.0+
- **数据库**：SQLite (轻量级部署)
- **认证**：JWT (JSON Web Token)
- **密码加密**：Passlib + bcrypt
- **文件处理**：Pillow (图像处理)
- **数据处理**：Pandas + OpenPyXL
- **AI服务**：OpenAI API
- **邮件服务**：SMTP (QQ邮箱)
- **跨域处理**：Flask-CORS

### 开发工具
- **包管理**：pnpm (前端) / pip (后端)
- **代码格式化**：ESLint + Prettier
- **测试框架**：pytest (后端)
- **版本控制**：Git

## 📁 项目结构

```
EasyMeeting/
├── openSourceFront/          # 前端项目
│   ├── src/
│   │   ├── components/       # Vue组件
│   │   │   ├── Sidebar.vue           # 侧边栏组件
│   │   │   ├── ChatAssistant.vue     # AI助手组件
│   │   │   ├── HeatmapGrid.vue       # 热力图组件
│   │   │   ├── EventModal.vue        # 事件弹窗组件
│   │   │   ├── AvatarCropper.vue     # 头像裁剪组件
│   │   │   └── ...
│   │   ├── pages/           # 页面组件
│   │   │   ├── Schedule.vue          # 日程管理页面
│   │   │   ├── MyOrganization.vue    # 组织管理页面
│   │   │   ├── CreateMeeting.vue     # 创建会议页面
│   │   │   ├── LoginPage.vue         # 登录页面
│   │   │   └── ...
│   │   ├── api/             # API接口
│   │   ├── store/           # 状态管理
│   │   ├── router/          # 路由配置
│   │   ├── utils/           # 工具函数
│   │   └── assets/          # 静态资源
│   ├── public/              # 公共资源
│   ├── package.json         # 前端依赖配置
│   ├── vite.config.js       # Vite配置
│   └── 接口.md              # 接口文档
│
├── schedule-planner/         # 后端项目
│   ├── backend/
│   │   ├── app/
│   │   │   ├── models/      # 数据模型
│   │   │   │   ├── user.py          # 用户模型
│   │   │   │   ├── organization.py  # 组织模型
│   │   │   │   ├── meeting.py       # 会议模型
│   │   │   │   └── schedule.py      # 日程模型
│   │   │   ├── routes/      # 路由控制器
│   │   │   │   ├── auth.py          # 认证路由
│   │   │   │   ├── user.py          # 用户路由
│   │   │   │   ├── meeting.py       # 会议路由
│   │   │   │   ├── organization.py  # 组织路由
│   │   │   │   ├── schedule.py      # 日程路由
│   │   │   │   ├── chat.py          # AI聊天路由
│   │   │   │   └── upload.py        # 文件上传路由
│   │   │   ├── services/    # 业务逻辑
│   │   │   ├── __init__.py  # 应用初始化
│   │   │   └── config.py    # 配置文件
│   │   ├── tests/           # 测试文件
│   │   ├── docs/            # 文档
│   │   ├── uploads/         # 上传文件目录
│   │   ├── requirements.txt # Python依赖
│   │   └── run.py          # 启动文件
│   └── README.md
│
└── README.md                # 项目主文档
```

## 🚀 快速开始

### 环境要求

- **Node.js** >= 16.0.0
- **Python** >= 3.8
- **pnpm** >= 7.0.0 (推荐) 或 npm >= 8.0.0

### 1. 克隆项目

```bash
git clone https://github.com/your-username/EasyMeeting.git
cd EasyMeeting
```

### 2. 后端环境配置

```bash
# 进入后端目录
cd schedule-planner/backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
export SECRET_KEY="your-secret-key"
export OPENAI_API_KEY="your-openai-api-key"

# 启动后端服务
python run.py
```

后端服务将在 `http://localhost:5000` 启动

### 3. 前端环境配置

```bash
# 进入前端目录
cd openSourceFront

# 安装依赖
pnpm install
# 或使用 npm
npm install

# 配置环境变量
cp .env.example .env.local
# 编辑 .env.local 文件，配置后端API地址

# 启动开发服务器
pnpm dev
# 或使用 npm
npm run dev
```

前端服务将在 `http://localhost:5173` 启动

### 4. 访问应用

打开浏览器访问 `http://localhost:5173` 即可使用应用。

## 📚 API文档

### 认证相关接口

#### 用户登录
```http
POST /api/login
Content-Type: application/json

{
  "phone": "13812345678",
  "password": "123456"
}
```

#### 用户注册
```http
POST /api/register
Content-Type: application/json

{
  "nickname": "张三",
  "phone": "13812345678",
  "email": "zhangsan@example.com",
  "password": "123456"
}
```

### 会议管理接口

#### 查找可用会议时间
```http
POST /api/meeting/find-time
Content-Type: application/json

{
  "token": "your-auth-token",
  "participant_ids": ["user1_id", "user2_id"],
  "duration": 60,
  "start_date": "2024-08-01",
  "end_date": "2024-08-10"
}
```

#### 创建会议
```http
POST /api/meeting/create
Content-Type: application/json

{
  "token": "your-auth-token",
  "title": "项目启动会",
  "start_time": "2024-08-01 10:00:00",
  "end_time": "2024-08-01 11:00:00",
  "participant_ids": ["user1_id", "user2_id"]
}
```

### 组织管理接口

#### 创建组织
```http
POST /api/organization/create
Content-Type: application/json

{
  "token": "your-auth-token",
  "name": "技术部",
  "member_ids": ["user1_id", "user2_id"]
}
```

### AI助手接口

#### 聊天对话
```http
POST /api/chat
Content-Type: application/json
Authorization: Bearer your-openai-api-key

{
  "model": "gpt-4",
  "messages": [
    {
      "role": "user",
      "content": "明天有什么会议安排？"
    }
  ]
}
```

更多详细的API文档请参考：
- [接口文档](./openSourceFront/接口.md)
- [后端文档](./schedule-planner/backend/docs/)

## 🚀 部署指南

### Docker部署

#### 1. 构建镜像

```bash
# 构建后端镜像
docker build -t easymeeting-backend ./schedule-planner/backend

# 构建前端镜像
docker build -t easymeeting-frontend ./openSourceFront
```

#### 2. 运行容器

```bash
# 运行后端容器
docker run -d -p 5000:5000 --name easymeeting-backend easymeeting-backend

# 运行前端容器
docker run -d -p 80:80 --name easymeeting-frontend easymeeting-frontend
```

### 生产环境部署

#### 1. 后端部署

```bash
# 使用 Gunicorn 部署
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 run:app

# 使用 Nginx 反向代理
# 配置 nginx.conf
```

#### 2. 前端部署

```bash
# 构建生产版本
pnpm build

# 部署到 Nginx
# 将 dist 目录内容复制到 Nginx 静态文件目录
```

## 🙏 致谢

感谢所有为这个项目做出贡献的开发者！

## 效果展示
登录注册: 账号登录或快速注册，一步完成身份验证。

<img width="369" height="371" alt="605aca43249a820ce970076835d94a6" src="https://github.com/user-attachments/assets/91a14568-20db-48a4-abd4-335582e544b8" />
<img width="400" height="486" alt="3a3cbcd1679a4df975be485e0e5f5af" src="https://github.com/user-attachments/assets/4d96879a-af83-4d0c-84b7-008a27700a8e" />

组织热力图: 切换组织和颜色，深色块代表该时段成员忙碌度高。

<img width="2037" height="1266" alt="image" src="https://github.com/user-attachments/assets/72121e50-9b7e-4667-9d5b-2c3899ce3bc3" />

创建会议: 选日期范围→查可用时间→确认起止→生成会议。

<img width="640" height="280" alt="718357911aa84de0ec4082523ba7184" src="https://github.com/user-attachments/assets/5617a69c-82f7-4552-9445-e53645183878" />
<img width="641" height="178" alt="c2c6ec2f38e680797cefd6a92968d4b" src="https://github.com/user-attachments/assets/60f6d8d5-9ba7-4d13-bb89-0eb2154cfdbe" />
<img width="1032" height="662" alt="6e33fee7cff553af2c72950b55b45e5" src="https://github.com/user-attachments/assets/a7642548-6a8c-4021-8b79-cf2b8d245ee1" />
<img width="1034" height="599" alt="15826312173b70728b3a424ac1249dc" src="https://github.com/user-attachments/assets/64446c15-2d4d-4b0e-96f7-d3b52dc27b7e" />

我的日程: 手动或 Excel 导入事件，以半小时为粒度，自定义颜色。

<img width="2044" height="1321" alt="image" src="https://github.com/user-attachments/assets/9ade00f8-8ced-46fd-8394-6d3a44a4d475" />

我的组织: 查看成员列表，右上角处理待审邀请，一键发邀请给新人。

<img width="2463" height="1410" alt="image" src="https://github.com/user-attachments/assets/7bb9fdac-2223-49be-8b07-acedcaf847ca" />

大模型聊天: 配置 API 后即可与模型对话。













<div align="center">

**如果这个项目对你有帮助，请给它一个 ⭐️**

Made with ❤️ by the EasyMeeting Team

</div>
