# TeamWork6

## 项目概述
TeamWork6是一款智能日程协作平台，旨在解决团队协作中的日程安排痛点，提供智能日程调度、组织级日程可视化和标准化数据接入功能。本平台通过整合AI算法与直观的用户界面，帮助团队高效管理会议安排，提升协作效率。

## 产品特点
- **智能日程调度**：基于参与者日程自动推荐最佳会议时间
- **组织级日程可视化**：直观展示团队成员的日程安排和忙闲状态
- **标准化数据接入**：支持导入Excel日程表和集成第三方日历服务
- **角色权限管理**：灵活的组织和成员权限控制
- **会议生命周期管理**：从创建、参与到记录的全流程支持
- **大模型集成**：支持配置AI助手以提供智能会议建议

## 技术架构

### 前端技术栈
- **框架**：Vue 3 <mcfile name="package.json" path="TeamWork6\openSourceFront\package.json"></mcfile>
- **UI组件库**：Element Plus <mcfile name="package.json" path="TeamWork6\openSourceFront\package.json"></mcfile>
- **状态管理**：Pinia <mcfile name="package.json" path="TeamWork6\openSourceFront\package.json"></mcfile>
- **路由**：Vue Router <mcfile name="package.json" path="TeamWork6\openSourceFront\package.json"></mcfile>
- **HTTP客户端**：Axios <mcfile name="package.json" path="TeamWork6\openSourceFront\package.json"></mcfile>
- **构建工具**：Vite <mcfile name="package.json" path="TeamWork6\openSourceFront\package.json"></mcfile>

### 后端技术栈
- **语言**：Python
- **Web框架**：Flask <mcfile name="meeting.py" path="TeamWork6\schedule-planner\backend\app\routes\meeting.py"></mcfile>
- **数据库**：SQLite <mcfile name="meeting.py" path="TeamWork6\schedule-planner\backend\app\models\meeting.py"></mcfile>
- **认证**：JWT Token验证
- **密码加密**：Werkzeug安全工具 <mcfile name="user.py" path="TeamWork6\schedule-planner\backend\app\models\user.py"></mcfile>

## 项目结构

```
TeamWork6/
├── schedule-planner/          # 后端服务
│   ├── backend/               # 应用核心代码
│   │   ├── app/               # 应用主目录
│   │   │   ├── models/        # 数据模型
│   │   │   ├── routes/        # API路由
│   │   │   ├── services/      # 业务逻辑
│   │   │   ├── config.py      # 配置文件
│   │   ├── tests/             # 后端测试
│   │   ├── uploads/           # 文件上传目录
│   ├── docs/                  # 后端文档
│
├── openSourceFront/           # 前端应用
│   ├── src/                   # 源代码
│   │   ├── pages/             # 页面组件
│   │   ├── router/            # 路由配置
│   │   ├── components/        # UI组件
│   │   ├── store/             # 状态管理
│   │   ├── utils/             # 工具函数
│   ├── package.json           # 依赖配置
│
├── test/                      # 测试文档
│   ├── tool/                  # 测试工具
│   ├── 测试.md                # 测试用例
│
├── Technical architecture/    # 技术架构文档
│   ├── 接口文档.md            # API文档
│   ├── DB设计说明.md          # 数据库设计
│
├── product.md                 # 产品文档
├── team.md                    # 团队文档
└── README.md                  # 项目说明
```

## 功能模块

### 用户认证与管理
- **注册/登录**：支持手机号、邮箱登录与注册 <mcfile name="测试.md" path="TeamWork6\test\测试.md"></mcfile>
- **个人信息管理**：修改昵称、邮箱、手机号、密码 <mcfile name="测试.md" path="TeamWork6\test\测试.md"></mcfile>
- **头像上传**：支持图片上传和QQ头像链接 <mcfile name="测试.md" path="TeamWork6\test\测试.md"></mcfile>
- **权限控制**：基于角色的访问控制 <mcfile name="user.py" path="TeamWork6\schedule-planner\backend\app\models\user.py"></mcfile>

### 日程管理
- **日程查看**：个人日程列表与详情 <mcfile name="测试.md" path="TeamWork6\test\测试.md"></mcfile>
- **日程创建**：支持单次和重复日程 <mcfile name="测试.md" path="TeamWork6\test\测试.md"></mcfile>
- **日程导入**：Excel文件导入功能 <mcfile name="测试.md" path="TeamWork6\test\测试.md"></mcfile>
- **日程删除**：单个和批量删除功能 <mcfile name="测试.md" path="TeamWork6\test\测试.md"></mcfile>

### 会议管理
- **智能会议时间推荐**：基于参与者日程自动推荐最佳时间 <mcfile name="meeting_service.py" path="TeamWork6\schedule-planner\backend\app\services\meeting_service.py"></mcfile>
- **会议创建**：设置标题、描述、时间、参与者 <mcfile name="meeting.py" path="TeamWork6\schedule-planner\backend\app\routes\meeting.py"></mcfile>
- **会议参与者管理**：添加/移除参与者，标记关键成员 <mcfile name="meeting.py" path="TeamWork6\schedule-planner\backend\app\models\meeting.py"></mcfile>
- **会议列表**：按日期筛选个人会议 <mcfile name="meeting.py" path="TeamWork6\schedule-planner\backend\app\routes\meeting.py"></mcfile>

### 组织管理
- **组织列表**：查看用户所属组织 <mcfile name="测试.md" path="TeamWork6\test\测试.md"></mcfile>
- **组织热力图**：可视化组织成员活动分布 <mcfile name="测试.md" path="TeamWork6\test\测试.md"></mcfile>

### 大模型集成
- **配置管理**：设置大模型API、密钥和系统提示词 <mcfile name="测试.md" path="TeamWork6\test\测试.md"></mcfile>

## 前端页面结构
- **认证页面**：登录、注册、忘记密码、绑定手机 <mcfile name="index.js" path="TeamWork6\openSourceFront\src\router\index.js"></mcfile>
- **仪表盘**：
  - 组织看板
  - 个人日程
  - 创建会议
  - 组织管理
  - 个人设置 <mcfile name="index.js" path="TeamWork6\openSourceFront\src\router\index.js"></mcfile>

## 后端API接口

### 认证接口
- 登录/注册
- 验证码发送与验证
- Token验证

### 会议接口
- `POST /meeting/find-time` - 查找可用会议时间 <mcfile name="meeting.py" path="TeamWork6\schedule-planner\backend\app\routes\meeting.py"></mcfile>
- `POST /meeting/create` - 创建会议 <mcfile name="meeting.py" path="TeamWork6\schedule-planner\backend\app\routes\meeting.py"></mcfile>
- `POST /meeting/list` - 获取会议列表 <mcfile name="meeting.py" path="TeamWork6\schedule-planner\backend\app\routes\meeting.py"></mcfile>

### 用户接口
- 用户信息管理
- 密码修改
- 头像上传

### 组织接口
- 组织列表
- 组织热力图

## 数据库设计
- **数据库范式**：遵循1NF到5NF及BCNF规范 <mcfile name="DB设计说明.md" path="TeamWork6\Technical architecture\DB设计说明.md"></mcfile>
- **主要表结构**：
  - `users` - 用户信息
  - `meetings` - 会议信息
  - `meeting_participants` - 会议参与者
  - `verification_codes` - 验证码
  - `token_blacklist` - Token黑名单 <mcfile name="user.py" path="TeamWork6\schedule-planner\backend\app\models\user.py"></mcfile>

## 测试用例
系统包含全面的测试用例，覆盖以下功能：
- 登录/注册功能测试
- 日程管理测试
- 用户信息管理测试
- 组织功能测试
- 大模型配置测试 <mcfile name="测试.md" path="TeamWork6\test\测试.md"></mcfile>

## 安装与运行

### 前端
```bash
# 进入前端目录
cd openSourceFront

# 安装依赖
npm install

# 开发模式运行
npm run dev

# 构建生产版本
npm run build

# 预览构建结果
npm run preview
```

### 后端
```bash
# 进入后端目录
cd schedule-planner/backend

# 安装依赖
pip install -r requirements.txt

# 初始化数据库
python -c "from app.models import init_db; init_db()"

# 运行开发服务器
python run.py
```

## 项目团队
| 角色                        | 成员人数 | 姓名                       |
| --------------------------- | -------- | -------------------------- |
| **CEO（项目总负责人）**     | 1人      | 王毓祥                     |
| **CPO（产品负责人）**       | 1人      | 廖炳衡                     |
| **CTO（技术负责人）**       | 1人      | 张旭                       |
| **CKO（知识与成长负责人）** | 1人      | 金建新                     |
| **前端工程师**              | 2人      | 李博洋，虞果               |
| **后端工程师**              | 4人      | 张旭，李正宇，钱睿澄，唐震 |
| **测试工程师**              | 1人      | 夏意晨                     |

### 项目主计划
- 需求分析与规划阶段（2周）
- 架构设计与技术选型阶段（1周）
- 迭代开发阶段（8周）
- 测试与优化阶段（2周）
- 部署与上线阶段（1周）

### 协同工作制度
- 每日站会：早上10点简短同步进度与问题
- 代码审查：所有代码需通过PR提交并经至少1名团队成员审查
- 文档先行：核心功能实现前需完成设计文档
- 迭代周期：2周一个迭代，周末进行迭代回顾
