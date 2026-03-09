#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rss_fetcher.py - 从真实RSS源抓取西班牙新闻
支持RSS抓取失败时使用浏览器fallback
输出: data/rss_articles.json
"""
import feedparser
import json
import re
import ssl
import subprocess
import sys
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
    # 原有移民居留类
    "visa", "student", "residency", "immigration", "tax", "education", "housing",
    "migración", "visado", "estudiante", "residencia", "impuesto", "educación",
    "vivienda", "permiso", "ley", "extranjería", "autónomo", "universidad",
    "ayuda", "subsidio", "beca", "matrícula", "nacionalidad", "ciudadanía",
    "tarjeta sanitaria", "seguridad social", "paro", "empleo", "trabajo",
    
    # 美伊战争地缘政治类 (高优先级)
    "Irán", "Iran", "Israel", "Gaza", "Palestina", "Palestine",
    "Oriente Medio", "Middle East", "guerra", "war", "conflicto", "conflict",
    "Hamas", "Líbano", "Lebanon", "Hizbulá", "Hezbollah",
    
    # 地缘政治对西班牙影响
    "gasolina", "gas", "petrol", "oil", "crudo", "barril",
    "economía", "economy", "inflación", "inflation", "precio", "price",
    "energía", "energy", "suministro", "supply",
    
    # 中小学教育类 (新增)
    "colegio", "escuela", "primaria", "secundaria", "bachillerato", "ESO",
    "educación infantil", "guardería", "preescolar",
    "ranking", "mejor colegio", "school ranking", "mejor escuela",
    "zona escolar", "concertado", "público", "privado", "semi-privado",
    "escuela para extranjeros", "school for immigrants",
    "integración escolar", "inmersión lingüística", "bilingüe", "bilingual",
    "elección de colegio", "cómo elegir colegio", "selección escolar",
    "matrícula escolar", "plaza escolar", "admisión escolar",
]

# 浏览器 fallback 网站 (当RSS失败时直接抓取)
BROWSER_FALLBACK_SITES = [
    {"name": "El País", "url": "https://elpais.com", "selector": "article h2 a"},
    {"name": "El Mundo", "url": "https://elmundo.es", "selector": "article h2 a, .ue-c-cover-content__link"},
    {"name": "ABC", "url": "https://abc.es", "selector": "article h2 a, .titular a"},
]

def fetch_feed(source):
    """抓取单个RSS源"""
    try:
        print(f"📡 抓取: {source['name']}")
        feed = feedparser.parse(source['url'])
        articles = []
        
        # 检查是否有bozo错误 (RSS解析错误)
        if hasattr(feed, 'bozo') and feed.bozo:
            print(f"   ⚠️ RSS解析警告: {feed.get('bozo_exception', 'Unknown')}")
        
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

def fetch_with_browser(site):
    """使用浏览器抓取网站"""
    try:
        print(f"🌐 浏览器抓取: {site['name']} ({site['url']})")
        
        # 使用 playwright 或直接 HTTP 请求
        import urllib.request
        import urllib.error
        
        req = urllib.request.Request(
            site['url'],
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
            }
        )
        
        with urllib.request.urlopen(req, timeout=15) as response:
            html = response.read().decode('utf-8', errors='ignore')
        
        # 提取标题和链接
        articles = []
        
        # 尝试多种模式匹配
        # 模式1: 常见的文章链接
        patterns = [
            r'<h[1-6][^>]*>.*?<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>.*?</h[1-6]>',
            r'<article[^>]*>.*?<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>.*?</article>',
            r'<a[^>]*href="([^"]+)"[^>]*class="[^"]*(?:titular|headline|title)[^"]*"[^>]*>(.*?)</a>',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, html, re.DOTALL | re.IGNORECASE)
            for link, title in matches[:5]:  # 每个模式最多5篇
                # 清理标题
                title = re.sub(r'<[^>]+>', '', title).strip()
                title = re.sub(r'\s+', ' ', title)
                
                # 处理相对链接
                if link.startswith('/'):
                    base_url = '/'.join(site['url'].split('/')[:3])
                    link = base_url + link
                elif not link.startswith('http'):
                    link = site['url'].rstrip('/') + '/' + link
                
                if title and len(title) > 10:
                    articles.append({
                        'title': title,
                        'link': link,
                        'summary': f'从 {site["name"]} 首页抓取',
                        'published': datetime.now().isoformat(),
                        'source': f"{site['name']} (Browser)"
                    })
        
        # 去重
        seen = set()
        unique = []
        for art in articles:
            if art['link'] not in seen:
                seen.add(art['link'])
                unique.append(art)
        
        print(f"   ✓ 浏览器获取 {len(unique)} 篇")
        return unique[:10]  # 最多返回10篇
        
    except Exception as e:
        print(f"   ✗ 浏览器抓取失败: {e}")
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
    
    # 抓取所有RSS源
    all_articles = []
    failed_sources = []
    
    for source in RSS_SOURCES:
        articles = fetch_feed(source)
        if articles:
            all_articles.extend(articles)
        else:
            failed_sources.append(source)
    
    print(f"\n📊 RSS总计抓取: {len(all_articles)} 篇文章")
    print(f"📊 失败源: {len(failed_sources)} 个")
    
    # 如果RSS抓取失败太多，使用浏览器fallback
    if len(all_articles) < 20:
        print(f"\n⚠️ RSS文章不足，启用浏览器fallback...")
        for site in BROWSER_FALLBACK_SITES:
            browser_articles = fetch_with_browser(site)
            all_articles.extend(browser_articles)
    
    # 去重（基于链接）
    seen_links = set()
    unique_articles = []
    for art in all_articles:
        if art['link'] not in seen_links:
            seen_links.add(art['link'])
            unique_articles.append(art)
    
    print(f"\n📊 去重后: {len(unique_articles)} 篇")
    
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
    
    # 如果文章太少，警告
    if len(unique_articles) < 5:
        print(f"\n⚠️ 警告: 只抓取到 {len(unique_articles)} 篇文章，可能RSS源有问题")
        print("   建议检查网络连接或RSS源可用性")

if __name__ == "__main__":
    main()
