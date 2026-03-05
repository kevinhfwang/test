#!/usr/bin/env python3
"""
Spain Identity Content System v3.0
西班牙身份内容系统 - 长期自动化内容引擎

功能：
1. 每日RSS抓取 → 爆款标题生成 → Obsidian存储
2. 每周主题分析 → 高频主题识别 → 内容策略调整
3. 城市数据库维护 → Navarra vs Madrid对比
4. 知识图谱构建 → 身份路径结构化
"""

import feedparser
import json
import os
import re
import hashlib
import random
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import urllib.request
import ssl
import shutil

ssl._create_default_https_context = ssl._create_unverified_context

# 路径配置
PROJECT_ROOT = Path(__file__).parent.parent
CONFIG_PATH = PROJECT_ROOT / "config" / "system_config.json"
OBSIDIAN_VAULT_PATH = PROJECT_ROOT / "obsidian_vault"  # Obsidian知识库路径
OUTPUT_PATH = PROJECT_ROOT / "output"

# 默认配置
DEFAULT_CONFIG = {
    "mission": "Build long-term Spain identity content engine",
    "daily_cycle": {
        "max_titles_per_day": 20,
        "titles_per_article": 3,
        "max_length": 28,
        "min_question_ratio": 0.4,
        "style_models": ["policy_alert", "information_gap", "city_comparison", "time_window_urgency"]
    },
    "rss_sources": [
        {"name": "El País", "url": "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/portada", "category": "general"},
        {"name": "El País España", "url": "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/section/espana", "category": "policy"},
        {"name": "El País Economía", "url": "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/section/economia", "category": "economy"},
        {"name": "The Local ES", "url": "https://feeds.thelocal.com/rss/es", "category": "expat"},
        {"name": "elDiario", "url": "https://www.eldiario.es/rss/", "category": "general"},
        {"name": "La Vanguardia", "url": "https://www.lavanguardia.com/rss/home.xml", "category": "general"}
    ],
    "filter_keywords": {
        "high_priority": ["visa", "residencia", "residency", "immigration", "migración", "extranjería"],
        "medium_priority": ["student", "estudiante", "education", "educación", "universidad", "master"],
        "low_priority": ["tax", "impuesto", "housing", "vivienda", "alquiler", "Navarra", "autónomo"],
        "contextual": ["permit", "permiso", "work", "trabajo", "law", "ley", "policy", "política"]
    },
    "obsidian": {
        "enabled": True,
        "vault_path": "obsidian_vault",
        "folders": [
            "01_Daily_News",
            "02_Viral_Titles",
            "03_Policy_Monitoring",
            "04_Identity_Pathways",
            "05_City_Database",
            "06_Cost_Database",
            "07_Weekly_Analysis",
            "08_Published_Articles",
            "09_Client_Questions"
        ]
    },
    "categories": [
        "Policy Change",
        "Student Visa Path",
        "Work Residency",
        "Permanent Residency",
        "City Comparison",
        "Cost of Living",
        "Tax & Finance",
        "Digital Nomad"
    ]
}

# 爆款标题模板（按风格分类）
TITLE_TEMPLATES = {
    "policy_alert": [
        "注意！西班牙{topic}{adj}了",
        "最新！{topic}调整影响{group}",
        "提醒：西班牙{topic}有新变化",
        "重要：{group}{topic}政策变了",
        "速看：西班牙{topic}最新动态",
        "紧急：{topic}政策有变动",
    ],
    "information_gap": [
        "原来西班牙{topic}可以这么{adj}！",
        "{group}不知道：{topic}还能这样",
        "揭秘：西班牙{topic}的{adj}真相",
        "很多人不知道：{topic}有变化",
        "{topic}的秘密：{group}必看",
        "西班牙{topic}：{adj}真相曝光",
    ],
    "city_comparison": [
        "{topic}：马德里和Navarra差多少？",
        "Navarra vs 马德里：{topic}哪个更{adj}",
        "小城市更{adj}？{topic}真相来了",
        "西班牙{topic}：大城市vs小城市",
        "Navarra{topic}：比马德里{adj}多少？",
        "为什么{group}选Navarra不选马德里？",
    ],
    "time_window_urgency": [
        "{topic}还能{adj}多久？快看",
        "2026西班牙{topic}新规：{group}注意",
        "{topic}窗口期：{group}抓紧了",
        "倒计时：{topic}政策即将{adj}",
        "今年{topic}变了：{group}速了解",
        "2026年{topic}：{adj}趋势来了",
    ],
    "question": [
        "{topic}到底怎么{adj}？{group}必看",
        "为什么西班牙{topic}越来越{adj}？",
        "{topic}变了？{group}注意",
        "西班牙{topic}{adj}？真相来了",
        "{group}注意：{topic}有新变化？",
        "{topic}还能{adj}吗？最新情况",
    ]
}

# 主题映射
TOPIC_MAP = [
    (["visa", "visado", "签证"], "签证", "难办", "想来的"),
    (["student", "estudiante", "留学", "universidad"], "留学", "贵", "学生党"),
    (["residencia", "residency", "居留"], "居留", "严格", "想留下的"),
    (["immigration", "migración", "inmigrante"], "移民", "容易", "申请者"),
    (["housing", "vivienda", "alquiler", "房租"], "房租", "高", "租房族"),
    (["tax", "impuesto", "autónomo"], "税收", "复杂", "做生意的"),
    (["navarra", "pamplona", "tudela"], "Navarra", "特别", "住北部的"),
    (["madrid", "马德里"], "马德里", "贵", "住首都的"),
    (["work", "trabajo", "工作许可"], "工作", "难找", "求职者"),
    (["digital nomad", "nomada digital"], "数字游民签证", "热门", "远程办公的"),
    (["golden visa", "黄金签证"], "黄金签证", "收紧", "投资人"),
    (["sanidad", "healthcare", "医疗"], "医疗", "好", "新移民"),
    (["empadronamiento", "住家证明"], "住家证明", "重要", "刚搬来的"),
]

class SpainIdentitySystem:
    def __init__(self):
        self.config = self._load_config()
        self.articles = []
        self.titles = []
        self.today = datetime.now().strftime('%Y-%m-%d')
        random.seed()
        
        # 初始化Obsidian仓库
        if self.config.get('obsidian', {}).get('enabled'):
            self._init_obsidian_vault()

    def _load_config(self) -> Dict:
        """加载配置"""
        if CONFIG_PATH.exists():
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                return {**DEFAULT_CONFIG, **json.load(f)}
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(DEFAULT_CONFIG, f, indent=2, ensure_ascii=False)
        return DEFAULT_CONFIG

    def _init_obsidian_vault(self):
        """初始化Obsidian知识库文件夹结构"""
        vault_path = PROJECT_ROOT / self.config['obsidian']['vault_path']
        folders = self.config['obsidian']['folders']
        
        for folder in folders:
            (vault_path / folder).mkdir(parents=True, exist_ok=True)
        
        # 创建主索引文件
        index_path = vault_path / "🏠 Home.md"
        if not index_path.exists():
            self._create_home_index(index_path)

    def _create_home_index(self, path: Path):
        """创建Obsidian首页索引"""
        content = f"""# 🇪🇸 Spain Identity Content System

> 西班牙身份内容系统知识库
> 使命：{self.config['mission']}

## 📁 文件夹结构

| 文件夹 | 用途 |
|--------|------|
| `01_Daily_News` | 每日RSS原始新闻存档 |
| `02_Viral_Titles` | 生成的爆款标题库 |
| `03_Policy_Monitoring` | 政策变化追踪 |
| `04_Identity_Pathways` | 身份路径知识图谱 |
| `05_City_Database` | 城市数据库 |
| `06_Cost_Database` | 成本数据库 |
| `07_Weekly_Analysis` | 每周分析报告 |
| `08_Published_Articles` | 已发布文章存档 |
| `09_Client_Questions` | 客户常见问题 |

## 🎯 内容定位

- **Primary Focus**: 西班牙移民和留学路径
- **Differentiation**: 小城市定位 (Navarra vs Madrid)
- **Long-term Goal**: 建立西班牙身份知识图谱

## 📊 今日状态

- 最后更新: {self.today}
- 今日标题: [[{self.today} Viral Titles|查看今日标题]]

---

*自动生成于 {datetime.now().strftime('%Y-%m-%d %H:%M')}*
"""
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)

    # ==================== RSS抓取 ====================
    
    def fetch_rss(self, source: Dict) -> List[Dict]:
        """抓取单个RSS源"""
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (compatible; RSS Reader)'}
            request = urllib.request.Request(source['url'], headers=headers)
            
            with urllib.request.urlopen(request, timeout=15) as response:
                feed_data = response.read()
            
            feed = feedparser.parse(feed_data)
            articles = []
            
            for entry in feed.entries[:15]:
                summary = entry.get('summary', entry.get('description', ''))
                summary = re.sub(r'<[^>]+>', '', summary)
                
                articles.append({
                    'title': entry.get('title', ''),
                    'link': entry.get('link', ''),
                    'summary': summary[:800],
                    'published': entry.get('published', ''),
                    'source': source['name'],
                    'source_category': source.get('category', 'general')
                })
            
            print(f"  ✓ {source['name']}: {len(articles)}篇")
            return articles
            
        except Exception as e:
            print(f"  ✗ {source['name']}: {str(e)[:40]}")
            return []

    def fetch_all_rss(self) -> List[Dict]:
        """抓取所有RSS源"""
        print("\n📡 抓取RSS源...")
        all_articles = []
        
        for source in self.config['rss_sources']:
            articles = self.fetch_rss(source)
            all_articles.extend(articles)
        
        # 去重
        seen = set()
        unique = []
        for a in all_articles:
            if a['link'] not in seen and a['link']:
                seen.add(a['link'])
                unique.append(a)
        
        self.articles = unique
        print(f"📊 总计: {len(self.articles)}篇")
        return self.articles

    # ==================== 文章过滤与分类 ====================
    
    def score_article(self, article: Dict) -> Tuple[int, List[str]]:
        """为文章打分并识别类别"""
        text = f"{article['title']} {article['summary']}".lower()
        score = 0
        matched_categories = []
        
        keywords = self.config['filter_keywords']
        
        # 高优先级关键词 +3分
        for kw in keywords['high_priority']:
            if kw in text:
                score += 3
                if 'immigration' in kw or 'migración' in kw:
                    matched_categories.append('Policy Change')
                if 'residencia' in kw or 'residency' in kw:
                    matched_categories.append('Permanent Residency')
        
        # 中优先级关键词 +2分
        for kw in keywords['medium_priority']:
            if kw in text:
                score += 2
                if 'student' in kw or 'estudiante' in kw:
                    matched_categories.append('Student Visa Path')
        
        # 低优先级关键词 +1分
        for kw in keywords['low_priority']:
            if kw in text:
                score += 1
                if 'navarra' in kw:
                    matched_categories.append('City Comparison')
                if 'housing' in kw or 'vivienda' in kw:
                    matched_categories.append('Cost of Living')
        
        # 上下文关键词 +1分
        for kw in keywords['contextual']:
            if kw in text:
                score += 1
                if 'work' in kw or 'trabajo' in kw:
                    matched_categories.append('Work Residency')
        
        return score, list(set(matched_categories))

    def filter_and_categorize(self) -> List[Dict]:
        """过滤并分类文章"""
        print("\n🔍 过滤与分类...")
        
        scored_articles = []
        for article in self.articles:
            score, categories = self.score_article(article)
            if score >= 3:  # 至少匹配一个高优先级或组合
                article['relevance_score'] = score
                article['categories'] = categories
                scored_articles.append(article)
        
        # 按相关度排序
        scored_articles.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        # 限制数量
        max_articles = self.config['daily_cycle']['max_titles_per_day'] // self.config['daily_cycle']['titles_per_article']
        filtered = scored_articles[:max_articles]
        
        print(f"✓ 匹配: {len(filtered)}篇 (相关度≥3)")
        
        # 统计分类
        cat_counts = {}
        for a in filtered:
            for cat in a['categories']:
                cat_counts[cat] = cat_counts.get(cat, 0) + 1
        print(f"📊 分类分布: {cat_counts}")
        
        return filtered

    # ==================== 标题生成 ====================

    def detect_style(self, article: Dict) -> str:
        """检测文章适合的风格"""
        text = (article['title'] + " " + article['summary']).lower()
        categories = article.get('categories', [])
        
        # 城市对比类
        if 'City Comparison' in categories or 'navarra' in text or 'madrid' in text:
            return 'city_comparison'
        
        # 政策变化类
        if any(w in text for w in ['nuevo', 'new', 'cambia', 'change', 'alerta', 'urgente']):
            return 'policy_alert'
        
        # 时间窗口类
        if any(w in text for w in ['2026', '2025', 'plazo', 'deadline', 'window', 'countdown']):
            return 'time_window_urgency'
        
        # 信息差类（默认）
        return 'information_gap'

    def extract_topics(self, article: Dict) -> List[Tuple[str, str, str]]:
        """提取文章主题"""
        text = f"{article['title']} {article['summary']}".lower()
        matches = []
        
        for keywords, topic, adj, group in TOPIC_MAP:
            for kw in keywords:
                if kw.lower() in text:
                    matches.append((topic, adj, group))
                    break
        
        return matches if matches else [("居留政策", "重要", "华人")]

    def generate_title(self, article: Dict, style: str = None) -> Optional[str]:
        """为单篇文章生成标题"""
        if style is None:
            style = self.detect_style(article)
        
        templates = TITLE_TEMPLATES.get(style, TITLE_TEMPLATES['information_gap'])
        topics = self.extract_topics(article)
        
        for topic, adj, group in topics[:2]:
            template = random.choice(templates)
            title = template.format(topic=topic, adj=adj, group=group)
            
            if len(title) <= self.config['daily_cycle']['max_length']:
                return title
        
        return None

    def generate_titles_for_article(self, article: Dict) -> List[Dict]:
        """为单篇文章生成多个标题变体"""
        titles = []
        styles = self.config['daily_cycle']['style_models']
        
        # 根据文章类别选择风格
        primary_style = self.detect_style(article)
        
        # 先生成主风格标题
        title = self.generate_title(article, primary_style)
        if title:
            titles.append({
                'title': title,
                'style': primary_style,
                'source_article': article['title'],
                'source_link': article['link'],
                'source': article['source'],
                'categories': article.get('categories', []),
                'hash': hashlib.md5((title + article['link']).encode()).hexdigest()[:8]
            })
        
        # 再生成其他风格
        for style in random.sample(styles, min(2, len(styles))):
            if style != primary_style:
                title = self.generate_title(article, style)
                if title and title not in [t['title'] for t in titles]:
                    titles.append({
                        'title': title,
                        'style': style,
                        'source_article': article['title'],
                        'source_link': article['link'],
                        'source': article['source'],
                        'categories': article.get('categories', []),
                        'hash': hashlib.md5((title + article['link']).encode()).hexdigest()[:8]
                    })
        
        return titles[:self.config['daily_cycle']['titles_per_article']]

    def generate_all_titles(self, articles: List[Dict]) -> List[Dict]:
        """为所有文章生成标题"""
        print("\n✨ 生成爆款标题...")
        
        all_titles = []
        for article in articles:
            titles = self.generate_titles_for_article(article)
            all_titles.extend(titles)
        
        # 去重
        seen = set()
        unique = []
        for t in all_titles:
            if t['title'] not in seen:
                seen.add(t['title'])
                unique.append(t)
        
        max_titles = self.config['daily_cycle']['max_titles_per_day']
        self.titles = unique[:max_titles]
        
        print(f"✓ 生成: {len(self.titles)}个标题")
        return self.titles

    def add_fallback_titles(self):
        """添加备用标题（当新闻不足时）"""
        current_count = len(self.titles)
        min_required = 10
        
        if current_count < min_required:
            needed = min(min_required - current_count, 10)
            
            fallback_topics = [
                "西班牙留学真实一年花费？2026最新计算",
                "Navarra vs 马德里：生活成本到底差多少？",
                "学生签转工作居留：完整路径图解",
                "西班牙小城市更容易拿身份？真相来了",
                "非盈利居留DIY申请：这些坑千万别踩",
                "数字游民签证最新要求：你符合吗？",
                "黄金签证关停后：还有哪些Plan B？",
                "西班牙租房合同：这些隐藏条款要注意！",
                "首次申请居留被拒？最常见5个原因",
                "2026西班牙政策变了：影响哪些人？"
            ]
            
            import random
            selected = random.sample(fallback_topics, needed)
            
            for topic in selected:
                self.titles.append({
                    'title': topic,
                    'style': 'fallback',
                    'source_article': 'Fallback Topic',
                    'source_link': '',
                    'source': 'System',
                    'categories': ['General'],
                    'hash': __import__('hashlib').md5(topic.encode()).hexdigest()[:8]
                })
            
            print(f"📌 添加备用标题: {needed}个")

    def ensure_question_ratio(self):
        """确保疑问句比例"""
        question_markers = ['?', '？', '为什么', '怎么', '到底', '呢', '吗']
        total = len(self.titles)
        
        questions = sum(1 for t in self.titles if any(m in t['title'] for m in question_markers))
        ratio = questions / total if total > 0 else 0
        min_ratio = self.config['daily_cycle']['min_question_ratio']
        
        if ratio < min_ratio:
            needed = int(total * min_ratio) - questions
            for i, t in enumerate(self.titles):
                if needed <= 0:
                    break
                if not any(m in t['title'] for m in question_markers):
                    # 简单转换：加问号或替换关键词
                    if len(t['title']) < 27:
                        self.titles[i]['title'] = t['title'].replace('真相来了', '真相是？').replace('必看', '必看？') + '？'
                    needed -= 1
        
        final_ratio = sum(1 for t in self.titles if any(m in t['title'] for m in question_markers)) / total if total > 0 else 0
        print(f"📊 疑问句比例: {final_ratio:.0%}")

    # ==================== Obsidian集成 ====================

    def save_to_obsidian(self):
        """保存内容到Obsidian知识库"""
        if not self.config.get('obsidian', {}).get('enabled'):
            return
        
        vault_path = PROJECT_ROOT / self.config['obsidian']['vault_path']
        
        # 1. 保存每日新闻
        self._save_daily_news(vault_path)
        
        # 2. 保存生成的标题
        self._save_viral_titles(vault_path)
        
        # 3. 更新主题追踪
        self._update_theme_tracking(vault_path)
        
        print(f"✓ 已保存到Obsidian: {vault_path}")

    def _save_daily_news(self, vault_path: Path):
        """保存每日原始新闻"""
        folder = vault_path / "01_Daily_News"
        filepath = folder / f"{self.today} News.md"
        
        content = f"""# {self.today} 西班牙新闻日报

> 自动抓取: {len(self.articles)} 篇文章
> 相关匹配: {len([a for a in self.articles if hasattr(self, '_filtered_articles')])} 篇

## 抓取来源

"""
        for source in self.config['rss_sources']:
            source_articles = [a for a in self.articles if a['source'] == source['name']]
            content += f"- **{source['name']}**: {len(source_articles)} 篇\n"
        
        content += "\n## 相关文章详情\n\n"
        
        for article in getattr(self, '_filtered_articles', [])[:10]:
            content += f"""### {article['title']}

- **来源**: {article['source']}
- **链接**: {article['link']}
- **分类**: {', '.join(article.get('categories', []))}
- **相关度**: {article.get('relevance_score', 0)}

> {article['summary'][:200]}...

---

"""
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

    def _save_viral_titles(self, vault_path: Path):
        """保存生成的爆款标题"""
        folder = vault_path / "02_Viral_Titles"
        filepath = folder / f"{self.today} Viral Titles.md"
        
        content = f"""# {self.today} 爆款标题日报

> 生成数量: {len(self.titles)} 个
> 疑问句比例: 目标 ≥40%

## 今日标题

| # | 标题 | 风格 | 来源 | 分类 |
|---|------|------|------|------|
"""
        
        for i, t in enumerate(self.titles, 1):
            categories = ', '.join(t.get('categories', [])[:2])
            content += f"| {i} | {t['title']} | {t['style']} | {t['source']} | {categories} |\n"
        
        content += "\n## 按分类统计\n\n"
        
        # 统计每个分类的标题数
        cat_counts = {}
        for t in self.titles:
            for cat in t.get('categories', []):
                cat_counts[cat] = cat_counts.get(cat, 0) + 1
        
        for cat, count in sorted(cat_counts.items(), key=lambda x: -x[1]):
            content += f"- **{cat}**: {count} 个标题\n"
        
        content += f"""

## RSS订阅

```
标题RSS: output/spain-hot.xml
```

---

*生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

    def _update_theme_tracking(self, vault_path: Path):
        """更新主题追踪（用于周分析）"""
        tracking_file = vault_path / "07_Weekly_Analysis" / "theme_tracking.json"
        
        # 读取现有数据
        if tracking_file.exists():
            with open(tracking_file, 'r', encoding='utf-8') as f:
                tracking = json.load(f)
        else:
            tracking = {
                'daily_records': {},
                'theme_frequency': {},
                'last_updated': self.today
            }
        
        # 记录今日数据
        tracking['daily_records'][self.today] = {
            'title_count': len(self.titles),
            'categories': {}
        }
        
        for t in self.titles:
            for cat in t.get('categories', []):
                tracking['daily_records'][self.today]['categories'][cat] = \
                    tracking['daily_records'][self.today]['categories'].get(cat, 0) + 1
                tracking['theme_frequency'][cat] = tracking['theme_frequency'].get(cat, 0) + 1
        
        tracking['last_updated'] = self.today
        
        with open(tracking_file, 'w', encoding='utf-8') as f:
            json.dump(tracking, f, indent=2, ensure_ascii=False)

    # ==================== RSS输出 ====================

    def generate_rss_xml(self) -> str:
        """生成RSS XML"""
        now = datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')
        
        xml_parts = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">',
            '  <channel>',
            '    <title>🇪🇸 西班牙身份留学热点日报</title>',
            '    <link>https://yourdomain.com/</link>',
            '    <description>自动生成爆款标题库 - 聚焦西班牙移民、留学、Navarra小城市定位</description>',
            '    <language>zh-CN</language>',
            f'    <lastBuildDate>{now}</lastBuildDate>',
            '    <atom:link href="https://yourdomain.com/spain-hot.xml" rel="self" type="application/rss+xml"/>',
        ]
        
        for item in self.titles:
            pub_date = datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')
            categories = ', '.join(item.get('categories', []))
            description = f"来源: {item['source']} | 风格: {item['style']} | 分类: {categories}"
            
            xml_parts.append('    <item>')
            xml_parts.append(f'      <title><![CDATA[{item["title"]}]]></title>')
            xml_parts.append(f'      <description><![CDATA[{description}]]></description>')
            xml_parts.append(f'      <link>{item["source_link"] or "https://yourdomain.com/"}</link>')
            xml_parts.append(f'      <guid isPermaLink="false">{item["hash"]}</guid>')
            xml_parts.append(f'      <pubDate>{pub_date}</pubDate>')
            xml_parts.append('    </item>')
        
        xml_parts.extend([
            '  </channel>',
            '</rss>'
        ])
        
        return '\n'.join(xml_parts)

    def save_rss(self, xml_content: str):
        """保存RSS文件"""
        OUTPUT_PATH.mkdir(parents=True, exist_ok=True)
        filepath = OUTPUT_PATH / "spain-hot.xml"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        
        print(f"\n✅ RSS已保存: {filepath}")

    # ==================== 主流程 ====================

    def run_daily(self):
        """每日运行流程"""
        print("=" * 60)
        print("🇪🇸 Spain Identity Content System v3.0")
        print(f"⏰ {self.today}")
        print("=" * 60)
        
        # Step 1: 抓取新闻
        print("\n📰 Step 1: 收集新闻")
        self.fetch_all_rss()
        
        # Step 2: 过滤分类
        print("\n🎯 Step 2: 过滤与分类")
        filtered = self.filter_and_categorize()
        self._filtered_articles = filtered  # 保存供后续使用
        
        # Step 3: 生成标题
        print("\n✨ Step 3: 生成标题")
        if filtered:
            self.generate_all_titles(filtered)
        else:
            print("⚠️ 无匹配文章，将使用备用标题")
        
        # Step 3.5: 添加备用标题
        self.add_fallback_titles()
        
        # Step 4: 质量检查
        print("\n📊 Step 4: 质量检查")
        self.ensure_question_ratio()
        
        # Step 5: 保存到Obsidian
        print("\n📝 Step 5: 保存到Obsidian")
        self.save_to_obsidian()
        
        # Step 6: 生成RSS
        print("\n📡 Step 6: 生成RSS")
        xml = self.generate_rss_xml()
        self.save_rss(xml)
        
        # 显示结果
        print("\n" + "=" * 60)
        print("📋 今日标题预览 (前15条):")
        print("=" * 60)
        for i, t in enumerate(self.titles[:15], 1):
            marker = "❓" if any(m in t['title'] for m in ['?', '？', '为什么', '怎么', '到底']) else "📰"
            print(f"{i:2d}. {marker} {t['title'][:28]}")
        if len(self.titles) > 15:
            print(f"    ... 还有 {len(self.titles) - 15} 条")
        print("=" * 60)

if __name__ == '__main__':
    system = SpainIdentitySystem()
    system.run_daily()
