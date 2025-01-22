from sqlalchemy import Column, Integer, String, DateTime, Float, create_engine
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Repository(Base):
    __tablename__ = "repositories"

    id = Column(Integer, primary_key=True)
    github_id = Column(Integer, unique=True)
    name = Column(String)
    full_name = Column(String)
    description = Column(String)
    url = Column(String)
    stars = Column(Integer)
    forks = Column(Integer)
    language = Column(String)
    topics = Column(String)  # 以逗号分隔的主题列表
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    last_fetched = Column(DateTime)
    daily_stars = Column(Integer, default=0)
    trending_score = Column(Float, default=0.0)

# 创建数据库引擎和表
engine = create_engine("sqlite:///data/ai_projects.db")
Base.metadata.create_all(engine) 