# TeamWork6

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
- [开发指南](#开发指南)
- [贡献指南](#贡献指南)
- [许可证](#许可证)

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

## 👨‍💻 开发指南

### 代码规范

- **前端**：使用 ESLint + Prettier 进行代码格式化
- **后端**：遵循 PEP 8 Python代码规范
- **提交信息**：使用 Conventional Commits 规范

### 测试

```bash
# 后端测试
cd schedule-planner/backend
pytest

# 前端测试
cd openSourceFront
pnpm test
```

### 开发流程

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 🤝 贡献指南

我们欢迎所有形式的贡献！请查看以下指南：

### 贡献类型

- 🐛 **Bug修复**：报告和修复bug
- ✨ **新功能**：添加新功能
- 📚 **文档改进**：改进文档
- 🎨 **UI/UX改进**：改进用户界面
- ⚡ **性能优化**：优化性能
- 🧪 **测试**：添加或改进测试

### 贡献步骤

1. Fork 项目
2. 创建你的功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交你的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开一个 Pull Request

### 问题反馈

如果你发现了bug或有功能建议，请：

1. 检查现有的 [Issues](../../issues)
2. 创建新的 Issue，并详细描述问题
3. 提供复现步骤和期望行为

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

感谢所有为这个项目做出贡献的开发者！

### 主要贡献者

- **唐震** - 项目架构师和主要开发者
- **WithLei** - 参考项目 [MeetingReservation](https://github.com/WithLei/MeetingReservation)
- **iwxyi** - 参考项目 [EasyMeeting_Android](https://github.com/iwxyi/EasyMeeting_Android)

### 技术栈致谢

- [Vue.js](https://vuejs.org/) - 渐进式JavaScript框架
- [Element Plus](https://element-plus.org/) - Vue 3 UI组件库
- [Flask](https://flask.palletsprojects.com/) - Python Web框架
- [OpenAI](https://openai.com/) - AI服务提供商

## 📞 联系我们

- **项目主页**：[https://github.com/your-username/EasyMeeting](https://github.com/your-username/EasyMeeting)
- **问题反馈**：[Issues](../../issues)
- **邮箱**：your-email@example.com

---

<div align="center">

**如果这个项目对你有帮助，请给它一个 ⭐️**

Made with ❤️ by the EasyMeeting Team

</div>

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

## 👨‍💻 开发指南

### 代码规范

- **前端**：使用 ESLint + Prettier 进行代码格式化
- **后端**：遵循 PEP 8 Python代码规范
- **提交信息**：使用 Conventional Commits 规范

### 测试

```bash
# 后端测试
cd schedule-planner/backend
pytest

# 前端测试
cd openSourceFront
pnpm test
```

### 开发流程

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 🤝 贡献指南

我们欢迎所有形式的贡献！请查看以下指南：

### 贡献类型

- 🐛 **Bug修复**：报告和修复bug
- ✨ **新功能**：添加新功能
- 📚 **文档改进**：改进文档
- 🎨 **UI/UX改进**：改进用户界面
- ⚡ **性能优化**：优化性能
- 🧪 **测试**：添加或改进测试

### 贡献步骤

1. Fork 项目
2. 创建你的功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交你的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开一个 Pull Request

### 问题反馈

如果你发现了bug或有功能建议，请：

1. 检查现有的 [Issues](../../issues)
2. 创建新的 Issue，并详细描述问题
3. 提供复现步骤和期望行为

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

感谢所有为这个项目做出贡献的开发者！

### 主要贡献者

- **唐震** - 项目架构师和主要开发者
- **WithLei** - 参考项目 [MeetingReservation](https://github.com/WithLei/MeetingReservation)
- **iwxyi** - 参考项目 [EasyMeeting_Android](https://github.com/iwxyi/EasyMeeting_Android)

### 技术栈致谢

- [Vue.js](https://vuejs.org/) - 渐进式JavaScript框架
- [Element Plus](https://element-plus.org/) - Vue 3 UI组件库
- [Flask](https://flask.palletsprojects.com/) - Python Web框架
- [OpenAI](https://openai.com/) - AI服务提供商

## 📞 联系我们

- **项目主页**：[https://github.com/your-username/EasyMeeting](https://github.com/your-username/EasyMeeting)
- **问题反馈**：[Issues](../../issues)
- **邮箱**：your-email@example.com

---

<div align="center">

**如果这个项目对你有帮助，请给它一个 ⭐️**

Made with ❤️ by the EasyMeeting Team

</div> 
