import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [trendingRepos, setTrendingRepos] = useState([]);
  const [newRepos, setNewRepos] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [trendingResponse, newResponse] = await Promise.all([
          fetch('http://localhost:8000/trending'),
          fetch('http://localhost:8000/new')
        ]);

        const trendingData = await trendingResponse.json();
        const newData = await newResponse.json();

        setTrendingRepos(trendingData);
        setNewRepos(newData);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching data:', error);
        setLoading(false);
      }
    };

    fetchData();
    // 每5分钟刷新一次数据
    const interval = setInterval(fetchData, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  const RepoCard = ({ repo }) => (
    <div className="repo-card">
      <h3>
        <a href={repo.url} target="_blank" rel="noopener noreferrer">
          {repo.full_name}
        </a>
      </h3>
      <p className="description">{repo.description}</p>
      <div className="stats">
        <span>⭐ {repo.stars}</span>
        {repo.daily_stars && <span>今日: +{repo.daily_stars}</span>}
        <span>语言: {repo.language || 'N/A'}</span>
      </div>
      <div className="topics">
        {repo.topics.map(topic => (
          <span key={topic} className="topic-tag">{topic}</span>
        ))}
      </div>
    </div>
  );

  if (loading) {
    return <div className="loading">加载中...</div>;
  }

  return (
    <div className="app">
      <header>
        <h1>AI 项目每日看板</h1>
        <p className="update-time">
          最后更新时间: {new Date().toLocaleString()}
        </p>
      </header>

      <main>
        <section>
          <h2>🔥 热门项目</h2>
          <div className="repo-grid">
            {trendingRepos.map(repo => (
              <RepoCard key={repo.full_name} repo={repo} />
            ))}
          </div>
        </section>

        <section>
          <h2>✨ 新项目</h2>
          <div className="repo-grid">
            {newRepos.map(repo => (
              <RepoCard key={repo.full_name} repo={repo} />
            ))}
          </div>
        </section>
      </main>
    </div>
  );
}

export default App; 