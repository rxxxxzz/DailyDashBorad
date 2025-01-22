from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Repository(Base):
    __tablename__ = "repositories"

    id = Column(Integer, primary_key=True)
    github_id = Column(Integer, unique=True)
    name = Column(String)
    full_name = Column(String)
    description = Column(String)
    url = Column(String)
    stars = Column(Integer, default=0)
    forks = Column(Integer, default=0)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    last_fetched = Column(DateTime, default=datetime.utcnow)
    daily_stars = Column(Integer, default=0)
    daily_views = Column(Integer, default=0)
    topics = Column(String)  # 存储为逗号分隔的字符串
    language = Column(String)
    trending_score = Column(Float, default=0.0)  # 用于计算热度 