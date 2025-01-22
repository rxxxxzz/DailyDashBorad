# AI Project Dashboard (AI项目每日看板)

这是一个展示 GitHub 上热门 AI 相关项目的看板应用。

## 功能特点

- 实时抓取 GitHub 上的 AI 相关项目
- 展示今日最受欢迎的前 10 个项目（按星标和访问量排序）
- 展示新涌现的 AI 相关项目
- 自动更新数据

## 技术栈

- 后端：Python FastAPI
- 前端：React
- 数据库：SQLite
- 定时任务：Python Schedule

## 安装和运行

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 设置环境变量：
创建 `.env` 文件并添加 GitHub Token：
```
GITHUB_TOKEN=your_token_here
```

3. 运行应用：
```bash
uvicorn main:app --reload
```

## 项目结构

```
.
├── backend/           # 后端代码
│   ├── main.py       # FastAPI 应用
│   ├── models.py     # 数据模型
│   └── services/     # 服务层
├── frontend/         # 前端代码
│   ├── src/         
│   └── public/      
└── requirements.txt  # Python 依赖
``` 