import os
import json
from datetime import datetime, timedelta
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from models import Repository
import os

# 数据库配置
engine = create_engine("sqlite:///backend/ai_projects.db")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def generate_api_data():
    """从数据库生成 API 数据文件"""
    try:
        db = SessionLocal()
        
        # 获取趋势项目
        trending_repos = db.query(Repository)\
            .order_by(desc(Repository.trending_score))\
            .limit(10)\
            .all()
        
        trending_data = [{
            "name": repo.name,
            "full_name": repo.full_name,
            "description": repo.description,
            "url": repo.url,
            "stars": repo.stars,
            "daily_stars": repo.daily_stars,
            "topics": repo.topics.split(",") if repo.topics else [],
            "language": repo.language,
            "trending_score": repo.trending_score
        } for repo in trending_repos]
        
        # 获取新项目
        one_week_ago = datetime.utcnow() - timedelta(days=7)
        new_repos = db.query(Repository)\
            .filter(Repository.created_at > one_week_ago)\
            .order_by(desc(Repository.stars))\
            .limit(10)\
            .all()
        
        new_data = [{
            "name": repo.name,
            "full_name": repo.full_name,
            "description": repo.description,
            "url": repo.url,
            "stars": repo.stars,
            "created_at": repo.created_at.strftime("%Y-%m-%d"),
            "topics": repo.topics.split(",") if repo.topics else [],
            "language": repo.language
        } for repo in new_repos]
        
        # 确保 data 目录存在
        os.makedirs("data", exist_ok=True)
        
        # 保存数据到 JSON 文件
        with open("data/trending.json", "w", encoding="utf-8") as f:
            json.dump(trending_data, f, ensure_ascii=False, indent=2)
        
        with open("data/new.json", "w", encoding="utf-8") as f:
            json.dump(new_data, f, ensure_ascii=False, indent=2)
        
        # 保存更新时间
        with open("data/last_update.json", "w", encoding="utf-8") as f:
            json.dump({"last_update": datetime.now().isoformat()}, f, ensure_ascii=False, indent=2)
            
        db.close()
        print("API 数据生成完成")
        
    except Exception as e:
        print(f"生成 API 数据时出错: {str(e)}")
        raise

if __name__ == "__main__":
    generate_api_data() 