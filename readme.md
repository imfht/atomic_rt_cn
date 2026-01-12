# Atomic Red Team CN

🛡️ 基于 [Atomic Red Team](https://github.com/redcanaryco/atomic-red-team) 的中文攻击技术数据库与智能分析平台

## 项目简介

Atomic Red Team CN 是一个 Web 应用程序，用于整合、存储和分析来自 Atomic Red Team 项目的网络攻击技术。该平台结合了数据库存储、REST API 和大语言模型（LLM）集成，提供中文化的攻击技术分析和展示。

## 主要功能

- 📊 **攻击技术数据库**: 使用 SQLAlchemy 存储和管理来自 Atomic Red Team 的攻击技术数据
- 🔄 **数据同步**: 从 Atomic Red Team 官方仓库获取最新的攻击技术数据
- 🤖 **AI 智能分析**: 集成 OpenAI API（或兼容接口）对攻击技术进行中文分析和总结
- 🔍 **搜索功能**: 按技术 ID、名称或描述快速搜索攻击技术
- 📈 **统计展示**: 可视化展示数据库统计信息和分析进度
- 🌐 **友好界面**: 现代化的 Web 界面，支持响应式设计

## 技术栈

- **后端**: Python Flask + SQLAlchemy
- **前端**: HTML + CSS + JavaScript
- **数据库**: SQLite
- **AI 集成**: OpenAI API（或兼容接口）
- **数据源**: Atomic Red Team GitHub 仓库

## 快速开始

### 环境要求

- Python 3.8+
- pip

### 安装步骤

1. 克隆仓库：

```bash
git clone https://github.com/imfht/atomic_rt_cn.git
cd atomic_rt_cn
```

2. 安装依赖：

```bash
pip install -r requirements.txt
```

3. 配置环境变量：

复制 `.env.example` 到 `.env` 并填写配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件，设置必要的配置项：

```
# Flask 配置
SECRET_KEY=your-secret-key-here

# OpenAI API 配置（可选，用于 AI 分析功能）
OPENAI_API_KEY=your-openai-api-key
OPENAI_API_BASE=https://api.openai.com/v1
OPENAI_MODEL=gpt-3.5-turbo
```

4. 初始化数据库：

```bash
flask init-db
```

5. （可选）添加示例数据：

```bash
flask seed-db
```

6. 启动应用：

```bash
python app.py
```

应用将在 `http://localhost:5000` 启动。

## 使用指南

### 1. 同步数据

首次使用时，需要从 Atomic Red Team 仓库同步攻击技术数据：

1. 访问 `http://localhost:5000`
2. 点击导航栏中的"数据同步"
3. 点击"同步数据"按钮

### 2. 浏览攻击技术

在"攻击技术"页面可以：
- 浏览所有已同步的攻击技术
- 使用搜索框查找特定技术
- 点击技术卡片查看详细信息
- 查看原子测试（Atomic Tests）

### 3. AI 分析

在技术详情页面：
1. 如果技术尚未分析，点击"开始分析"按钮
2. 系统将调用 LLM API 生成中文摘要和分析
3. 分析结果将自动保存到数据库

### 4. 查看统计

在"仪表盘"页面查看：
- 攻击技术总数
- 原子测试总数
- 已分析技术数量
- 分析完成率

## API 文档

### 获取所有技术

```
GET /api/techniques?page=1&per_page=20&search=T1003
```

### 获取单个技术

```
GET /api/techniques/<technique_id>
```

### 同步技术数据

```
POST /api/techniques/sync
Content-Type: application/json

{
  "technique_ids": ["T1003", "T1059"]  // 可选，留空则同步默认列表
}
```

### 分析技术

```
POST /api/techniques/<technique_id>/analyze
```

### 获取统计信息

```
GET /api/stats
```

## 项目结构

```
atomic_rt_cn/
├── app.py              # Flask 应用主文件
├── models.py           # 数据库模型
├── services.py         # 业务逻辑服务（数据同步、LLM 集成）
├── requirements.txt    # Python 依赖
├── .env.example       # 环境变量示例
├── .gitignore         # Git 忽略文件
├── readme.md          # 项目文档
├── templates/         # HTML 模板
│   └── index.html
└── static/            # 静态资源
    ├── css/
    │   └── style.css
    └── js/
        └── main.js
```

## 配置说明

### 数据库配置

默认使用 SQLite 数据库，文件位于 `atomic_rt.db`。可以通过环境变量更改：

```
DATABASE_URL=sqlite:///atomic_rt.db
```

支持其他数据库（需要安装相应驱动）：
- PostgreSQL: `postgresql://user:pass@localhost/dbname`
- MySQL: `mysql://user:pass@localhost/dbname`

### LLM API 配置

支持 OpenAI API 和兼容接口（如 Azure OpenAI、本地模型等）：

```
OPENAI_API_KEY=your-api-key
OPENAI_API_BASE=https://api.openai.com/v1  # 可选，使用兼容接口时修改
OPENAI_MODEL=gpt-3.5-turbo  # 使用的模型
```

注意：如果不配置 LLM API，AI 分析功能将返回模拟数据。

## 部署

### 使用 Gunicorn

```bash
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### 使用 Docker（示例）

创建 `Dockerfile`：

```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
```

构建和运行：

```bash
docker build -t atomic-rt-cn .
docker run -p 5000:5000 -v $(pwd)/.env:/app/.env atomic-rt-cn
```

## 开发

### 运行开发服务器

```bash
export FLASK_ENV=development
python app.py
```

### 数据库迁移

初始化数据库：
```bash
flask init-db
```

添加示例数据：
```bash
flask seed-db
```

## 许可证

MIT License

## 致谢

- [Atomic Red Team](https://github.com/redcanaryco/atomic-red-team) - 提供攻击技术数据
- [MITRE ATT&CK](https://attack.mitre.org/) - 攻击技术框架
- [Flask](https://flask.palletsprojects.com/) - Web 框架
- [OpenAI](https://openai.com/) - LLM API

## 贡献

欢迎提交 Issue 和 Pull Request！

## 联系方式

如有问题或建议，请提交 Issue。
