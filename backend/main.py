from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import os
import aiohttp
from dotenv import load_dotenv
from typing import List
import asyncio
import schedule
import time
from models import Base, Repository
import ssl

load_dotenv()

app = FastAPI(title="AI Project Dashboard API")

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://rxxxxzz.github.io"],  # 替换为你的 GitHub Pages 域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据库配置
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ai_projects.db")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建数据库表
Base.metadata.create_all(bind=engine)

# GitHub API 配置
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_API_URL = "https://api.github.com"
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
}

async def fetch_github_data():
    """获取 GitHub 数据的异步函数"""
    print("开始获取 GitHub 数据...")
    # 创建 SSL 上下文
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    connector = aiohttp.TCPConnector(ssl=ssl_context)
    async with aiohttp.ClientSession(connector=connector) as session:
        # AI 相关的搜索查询
        queries = [
            "topic:artificial-intelligence",
            "topic:ai-agents",
            "topic:machine-learning",
            "topic:deep-learning",
            "topic:workflow"
        ]
        
        for query in queries:
            print(f"正在获取查询: {query}")
            search_url = f"{GITHUB_API_URL}/search/repositories"
            params = {
                "q": f"{query} created:>{(datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')}",
                "sort": "stars",
                "order": "desc",
                "per_page": 100
            }
            
            try:
                async with session.get(search_url, headers=HEADERS, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"成功获取数据，找到 {len(data.get('items', []))} 个仓库")
                        db = SessionLocal()
                        
                        for item in data.get("items", []):
                            repo = db.query(Repository).filter_by(github_id=item["id"]).first()
                            if not repo:
                                repo = Repository(
                                    github_id=item["id"],
                                    name=item["name"],
                                    full_name=item["full_name"],
                                    description=item.get("description", ""),
                                    url=item["html_url"],
                                    stars=item["stargazers_count"],
                                    forks=item["forks_count"],
                                    created_at=datetime.strptime(item["created_at"], "%Y-%m-%dT%H:%M:%SZ"),
                                    updated_at=datetime.strptime(item["updated_at"], "%Y-%m-%dT%H:%M:%SZ"),
                                    topics=",".join(item.get("topics", [])),
                                    language=item.get("language", "Unknown"),
                                    daily_stars=0,
                                    daily_views=0
                                )
                                db.add(repo)
                                print(f"添加新仓库: {repo.full_name}")
                            else:
                                # 更新每日数据
                                repo.daily_stars = item["stargazers_count"] - repo.stars
                                repo.stars = item["stargazers_count"]
                                repo.forks = item["forks_count"]
                                repo.updated_at = datetime.strptime(item["updated_at"], "%Y-%m-%dT%H:%M:%SZ")
                                repo.last_fetched = datetime.utcnow()
                                print(f"更新仓库: {repo.full_name}")
                            
                            # 计算趋势得分（确保使用默认值0）
                            daily_stars = repo.daily_stars or 0
                            daily_views = repo.daily_views or 0
                            repo.trending_score = float(daily_stars * 2 + daily_views)
                        
                        db.commit()
                        db.close()
                    else:
                        print(f"API 请求失败: {response.status}")
                        error_data = await response.text()
                        print(f"错误信息: {error_data}")
            except Exception as e:
                print(f"处理查询时出错: {str(e)}")
                import traceback
                print(traceback.format_exc())
            
            await asyncio.sleep(1)  # 避免触发 GitHub API 限制

@app.on_event("startup")
async def startup_event():
    """应用启动时的初始化"""
    print("应用启动，开始初始化...")
    try:
        await fetch_github_data()
        print("初始数据获取完成")
    except Exception as e:
        print(f"初始化时出错: {str(e)}")
    
    # 设置定时任务
    schedule.every().day.at("08:00").do(lambda: asyncio.run(fetch_github_data()))
    print("定时任务已设置为每天早上 8:00 更新")

@app.get("/trending", response_model=List[dict])
async def get_trending_repos():
    """获取趋势项目"""
    try:
        db = SessionLocal()
        repos = db.query(Repository)\
            .order_by(desc(Repository.trending_score))\
            .limit(10)\
            .all()
        
        result = [{
            "name": repo.name,
            "full_name": repo.full_name,
            "description": repo.description,
            "url": repo.url,
            "stars": repo.stars,
            "daily_stars": repo.daily_stars,
            "topics": repo.topics.split(",") if repo.topics else [],
            "language": repo.language,
            "trending_score": repo.trending_score
        } for repo in repos]
        
        db.close()
        return result
    except Exception as e:
        print(f"获取趋势项目时出错: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/new", response_model=List[dict])
async def get_new_repos():
    """获取新项目"""
    try:
        db = SessionLocal()
        one_week_ago = datetime.utcnow() - timedelta(days=7)
        
        repos = db.query(Repository)\
            .filter(Repository.created_at > one_week_ago)\
            .order_by(desc(Repository.stars))\
            .limit(10)\
            .all()
        
        result = [{
            "name": repo.name,
            "full_name": repo.full_name,
            "description": repo.description,
            "url": repo.url,
            "stars": repo.stars,
            "created_at": repo.created_at.strftime("%Y-%m-%d"),
            "topics": repo.topics.split(",") if repo.topics else [],
            "language": repo.language
        } for repo in repos]
        
        db.close()
        return result
    except Exception as e:
        print(f"获取新项目时出错: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    import threading
    
    # 创建一个后台线程来运行定时任务
    def run_schedule():
        while True:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次
    
    # 启动定时任务线程
    schedule_thread = threading.Thread(target=run_schedule, daemon=True)
    schedule_thread.start()
    
    # 运行 FastAPI 服务器
    uvicorn.run(app, host="0.0.0.0", port=8000) 