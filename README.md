# AI 项目每日看板

自动收集和展示 GitHub 上热门的 AI 相关项目。

## 功能特点

- 每日自动更新
- 展示热门 AI 项目
- 展示最新 AI 项目
- 记录项目 Star 增长趋势
- 保存历史数据供后续分析

## 本地开发

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 更新数据：
```bash
python scripts/update_data.py
```

3. 运行开发服务器：
```bash
python scripts/dev_server.py
```

4. 访问网站：
```
http://localhost:8080/frontend/index.html
```

## 技术栈

- 前端：纯 HTML/CSS/JavaScript
- 数据存储：SQLite + JSON
- 自动化：GitHub Actions
- 部署：GitHub Pages

## 数据更新

- 每天早上 8:00（北京时间）自动更新
- 使用 GitHub API 获取最新数据
- 保存到 SQLite 数据库用于历史记录
- 生成 JSON 文件用于前端展示

## 贡献

欢迎提交 Issue 和 Pull Request！ 