import os
import json
import aiohttp
import asyncio
from datetime import datetime, timedelta
import ssl
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker
from models import Base, Repository, engine
from datetime import timezone
from zoneinfo import ZoneInfo

load_dotenv()

# 创建数据库会话
SessionLocal = sessionmaker(bind=engine)

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
    
    db = SessionLocal()
    trending_repos = []
    new_repos = []
    
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
                        
                        for item in data.get("items", []):
                            # 更新数据库
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
                                    language=item.get("language", "Unknown"),
                                    topics=",".join(item.get("topics", [])),
                                    created_at=datetime.strptime(item["created_at"], "%Y-%m-%dT%H:%M:%SZ"),
                                    updated_at=datetime.strptime(item["updated_at"], "%Y-%m-%dT%H:%M:%SZ"),
                                    last_fetched=datetime.utcnow(),
                                    daily_stars=0
                                )
                                db.add(repo)
                                print(f"添加新仓库: {repo.full_name}")
                            else:
                                # 计算每日新增 star 数
                                repo.daily_stars = item["stargazers_count"] - repo.stars
                                repo.stars = item["stargazers_count"]
                                repo.forks = item["forks_count"]
                                repo.updated_at = datetime.strptime(item["updated_at"], "%Y-%m-%dT%H:%M:%SZ")
                                repo.last_fetched = datetime.utcnow()
                                print(f"更新仓库: {repo.full_name}")
                            
                            # 计算趋势得分
                            repo.trending_score = float(repo.daily_stars * 2)
                            
                            # 准备 JSON 数据
                            repo_data = {
                                "name": repo.name,
                                "full_name": repo.full_name,
                                "description": repo.description,
                                "url": repo.url,
                                "stars": repo.stars,
                                "daily_stars": repo.daily_stars,
                                "language": repo.language,
                                "topics": repo.topics.split(",") if repo.topics else [],
                                "created_at": repo.created_at.isoformat(),
                                "updated_at": repo.updated_at.isoformat()
                            }
                            
                            # 添加到相应的列表
                            if (datetime.now() - repo.created_at).days <= 7:
                                new_repos.append(repo_data)
                            trending_repos.append(repo_data)
                            
                    else:
                        print(f"API 请求失败: {response.status}")
                        error_data = await response.text()
                        print(f"错误信息: {error_data}")
            except Exception as e:
                print(f"处理查询时出错: {str(e)}")
                import traceback
                print(traceback.format_exc())
            
            await asyncio.sleep(1)  # 避免触发 GitHub API 限制
    
    try:
        # 提交数据库更改
        db.commit()
        print("数据库更新完成")
        
        # 按分数排序
        trending_repos.sort(key=lambda x: x["daily_stars"], reverse=True)
        new_repos.sort(key=lambda x: x["stars"], reverse=True)
        
        # 只保留前 10 个仓库
        trending_repos = trending_repos[:10]
        new_repos = new_repos[:10]
        
        # 确保 data 目录存在
        os.makedirs("data", exist_ok=True)
        
        # 保存数据到 JSON 文件
        with open("data/trending.json", "w", encoding="utf-8") as f:
            json.dump(trending_repos, f, ensure_ascii=False, indent=2)
        
        with open("data/new.json", "w", encoding="utf-8") as f:
            json.dump(new_repos, f, ensure_ascii=False, indent=2)
        
        # 保存更新时间
        with open("data/last_update.json", "w", encoding="utf-8") as f:
            # 使用上海时区
            current_time = datetime.now(ZoneInfo("Asia/Shanghai"))
            json.dump({"last_update": current_time.isoformat()}, f, ensure_ascii=False, indent=2)
        
        print("JSON 文件更新完成")
    except Exception as e:
        print(f"保存数据时出错: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(fetch_github_data()) 