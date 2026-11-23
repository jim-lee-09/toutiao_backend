# 头条新闻系统 · 后端

基于 FastAPI + SQLAlchemy 的头条新闻系统后端，提供新闻分类、新闻详情、用户注册登录、收藏、浏览历史等接口。

## 技术栈

| 组件 | 用途 |
|---|---|
| FastAPI | Web 框架，自动生成接口文档 |
| SQLAlchemy (async) | ORM，异步访问数据库 |
| MySQL + aiomysql | 数据存储 |
| Redis | 缓存（新闻列表、分类） |
| Pydantic | 请求/响应数据校验 |

## 目录结构

```
toutiao_backend/
├── main.py              # 应用入口：创建 app、注册路由和异常处理
├── config/              # 配置：数据库连接、Redis 连接
├── models/              # 数据库模型（表结构）
├── schemas/             # Pydantic 请求/响应模型
├── crud/                # 数据访问层（封装数据库操作）
├── routers/             # 接口路由层
├── cache/               # 缓存相关逻辑
└── utils/               # 工具：鉴权、统一响应、异常处理
```

## 接口模块

| 模块 | 路径前缀 | 说明 |
|---|---|---|
| 新闻 | `/api/news` | 分类、列表、详情 |
| 用户 | `/api/users` | 注册、登录、信息、修改密码 |
| 收藏 | `/api/favorite` | 添加、列表、删除、清空 |
| 历史 | `/api/history` | 添加、列表、删除、清空 |

## 快速开始

```bash
# 1. 创建虚拟环境
python -m venv .venv
.venv\Scripts\activate

# 2. 安装依赖
pip install fastapi uvicorn sqlalchemy aiomysql redis pydantic passlib

# 3. 修改数据库配置（config/db_conf.py 中的 SYSTEM_URL）

# 4. 启动
uvicorn main:app --reload
```

启动后访问 `http://127.0.0.1:8000/docs` 查看自动生成的接口文档。

## 说明

- 数据库密码目前直接写在 `config/db_conf.py`，仅用于本地开发。
- 前端代码位于 `frontend/` 目录，首次使用先装依赖：`cd frontend` → `npm install` → `npm run dev`。
