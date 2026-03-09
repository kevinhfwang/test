#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rss_fetcher.py - 从真实RSS源抓取西班牙新闻
输出: data/rss_articles.json
"""
import feedparser
import json
import re
import ssl
from datetime import datetime
from pathlib import Path

# 忽略SSL验证
ssl._create_default_https_context = ssl._create_unverified_context

# RSS源配置 (24个来源)
RSS_SOURCES = [
    {"name": "El País", "url": "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/portada"},
    {"name": "El País España", "url": "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/section/espana"},
    {"name": "El País Economía", "url": "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/section/economia"},
    {"name": "El Mundo", "url": "https://feeds.elmundo.es/rss/portada.xml"},
    {"name": "El Mundo España", "url": "https://feeds.elmundo.es/rss/espana.xml"},
    {"name": "ABC", "url": "https://feeds.abc.es/rss/feeds/abc_ultima.xml"},
    {"name": "ABC España", "url": "https://feeds.abc.es/rss/feeds/abc_Espana.xml"},
    {"name": "El Confidencial", "url": "https://www.elconfidencial.com/rss/ultimo-minuto/"},
    {"name": "El Confidencial España", "url": "https://www.elconfidencial.com/rss/espana/"},
    {"name": "El Confidencial Economía", "url": "https://www.elconfidencial.com/rss/economia/"},
    {"name": "La Vanguardia", "url": "https://www.lavanguardia.com/rss/home.xml"},
    {"name": "La Razón", "url": "https://www.larazon.es/rss/espana.xml"},
    {"name": "20 Minutos", "url": "https://www.20minutos.es/rss/actualidad/"},
    {"name": "Público", "url": "https://www.publico.es/rss/"},
    {"name": "elDiario", "url": "https://www.eldiario.es/rss/"},
    {"name": "InfoLibre", "url": "https://www.infolibre.es/rss/"},
    {"name": "Euronews ES", "url": "https://es.euronews.com/rss"},
    {"name": "RTVE", "url": "https://www.rtve.es/rss/noticias.xml"},
    {"name": "Cinco Días", "url": "https://cincodias.elpais.com/rss/feed.html?feedId=1022"},
    {"name": "Expansión", "url": "https://www.expansion.com/rss/portada.xml"},
    {"name": "Expansión Economía", "url": "https://www.expansion.com/rss/economia.xml"},
    {"name": "The Local ES", "url": "https://feeds.thelocal.com/rss/es"},
    {"name": "Idealista", "url": "https://www.idealista.com/news/rss/"},
    {"name": "Fotocasa", "url": "https://www.fotocasa.es/blog/rss.xml"},
]

# 关键词过滤
FILTER_KEYWORDS = [
    "visa", "student", "residency", "immigration", "tax", "education", "housing",
    "migración", "visado", "estudiante", "residencia", "impuesto", "educación",
    "vivienda", "permiso", "ley", "extranjería", "autónomo", "universidad",
    "ayuda", "subsidio", "beca", "matrícula", "nacionalidad", "ciudadanía",
    "tarjeta sanitaria", "seguridad social", "paro", "empleo", "trabajo"
]

def fetch_feed(source):
    """抓取单个RSS源"""
    try:
        print(f"📡 抓取: {source['name']}")
        feed = feedparser.parse(source['url'])
        articles = []
        
        for entry in feed.entries[:10]:  # 每个源最多10篇
            summary = entry.get('summary', '')
            # 清理HTML标签
            summary = re.sub(r'<[^>]+>', '', summary)
            
            articles.append({
                'title': entry.get('title', ''),
                'link': entry.get('link', ''),
                'summary': summary[:300],
                'published': entry.get('published', datetime.now().isoformat()),
                'source': source['name']
            })
        
        print(f"   ✓ 获取 {len(articles)} 篇")
        return articles
    except Exception as e:
        print(f"   ✗ 失败: {e}")
        return []

def score_article(article):
    """计算文章相关度分数"""
    text = f"{article['title']} {article['summary']}".lower()
    score = 0
    
    for keyword in FILTER_KEYWORDS:
        if keyword in text:
            score += 1
    
    # 额外加分：近期文章
    if '2026' in text or '2025' in text:
        score += 2
    
    return score

def main():
    print("=" * 60)
    print("🚀 RSS Fetcher - 从西班牙媒体抓取新闻")
    print("=" * 60)
    
    # 创建数据目录
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # 抓取所有源
    all_articles = []
    for source in RSS_SOURCES:
        articles = fetch_feed(source)
        all_articles.extend(articles)
    
    print(f"\n📊 总计抓取: {len(all_articles)} 篇文章")
    
    # 去重（基于链接）
    seen_links = set()
    unique_articles = []
    for art in all_articles:
        if art['link'] not in seen_links:
            seen_links.add(art['link'])
            unique_articles.append(art)
    
    print(f"📊 去重后: {len(unique_articles)} 篇")
    
    # 评分并排序
    for art in unique_articles:
        art['score'] = score_article(art)
    
    unique_articles.sort(key=lambda x: x['score'], reverse=True)
    
    # 保存到文件
    output_file = data_dir / "rss_articles.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(unique_articles, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 已保存: {output_file}")
    print(f"📈 前5篇高分文章:")
    for i, art in enumerate(unique_articles[:5], 1):
        print(f"   {i}. [{art['score']}分] {art['title'][:50]}...")

if __name__ == "__main__":
    main()
