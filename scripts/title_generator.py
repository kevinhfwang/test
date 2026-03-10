#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
title_generator.py - 从RSS文章生成爆款中文标题
输入: data/rss_articles.json
输出: data/generated_titles.json
"""
import json
import random
from datetime import datetime
from pathlib import Path

# 爆款标题模板
TITLE_TEMPLATES = {
    "question": [
        "{topic}到底怎么{adj}？{group}必看",
        "为什么西班牙{topic}越来越{adj}？",
        "{topic}变了？{group}注意",
        "西班牙{topic}{adj}？真相来了",
        "{group}注意：{topic}有新变化？",
        "{topic}还能{adj}吗？最新情况",
        "2026西班牙{topic}新规：{group}必看",
    ],
    "alert": [
        "注意！西班牙{topic}{adj}了",
        "最新！{topic}调整影响{group}",
        "提醒：西班牙{topic}有新变化",
        "重要：{group}{topic}有变动",
        "速看：西班牙{topic}最新动态",
    ],
    "information_gap": [
        "原来西班牙{topic}可以这么{adj}！",
        "{group}不知道：{topic}还能这样",
        "揭秘：西班牙{topic}的{adj}真相",
        "很多人不知道：{topic}有变化",
        "想来的不知道：{topic}还能这样",
    ],
    # 地缘政治/战争专用模板
    "geopolitical": [
        "突发！{topic}，{group}必看",
        "{topic}，对西班牙{adj}影响有多大？",
        "欧洲力挺以色列？{topic}解读",
        "{topic}，华人{group}要注意",
        "中东局势{adj}，西班牙华人如何应对？",
    ]
}

# 主题映射
TOPIC_MAP = [
    (["visa", "visado", "签证"], "签证", "难办", "准备来西班牙的"),
    (["student", "estudiante", "estudio", "留学", "universidad", "master"], "留学", "贵", "想留学的"),
    (["residency", "residencia", "居留"], "居留", "严格", "想拿身份的"),
    (["immigration", "migración", "inmigrante", "移民"], "移民", "容易", "想移民的"),
    (["tax", "impuesto", "税务"], "税务", "复杂", "在西班牙的"),
    (["education", "educación", "教育"], "教育", "变", "有孩子的"),
    (["housing", "vivienda", "alquiler", "房租"], "租房", "涨", "要租房的"),
    (["work", "empleo", "trabajo", "工作"], "工作", "难找", "找工作的"),
    (["health", "sanidad", "salud", "医疗"], "医疗", "变", "需要医保的"),
    # 美伊战争/地缘政治 (高优先级)
    (["irán", "iran", "伊朗"], "伊朗局势", "紧张", "关注国际的"),
    (["israel", "以色列", "gaza", "加沙"], "中东冲突", "升级", "关注国际的"),
    (["guerra", "war", "战争", "conflicto", "冲突"], "战争风险", "上升", "在西班牙的"),
    (["oriente medio", "middle east", "中东"], "中东局势", "动荡", "关注国际的"),
    (["petróleo", "oil", "crudo", "barril", "汽油", "gasolina"], "油价", "涨", "开车的"),
    (["economía global", "global economy", "全球经济"], "全球经济", "波动", "做生意的"),
]

def detect_topic(title, summary):
    """检测文章主题"""
    text = f"{title} {summary}".lower()
    
    for keywords, topic, adj, group in TOPIC_MAP:
        if any(kw in text for kw in keywords):
            return topic, adj, group
    
    return "政策", "变", "在西班牙的"

def generate_title(article, used_titles):
    """生成爆款标题"""
    topic, adj, group = detect_topic(article['title'], article['summary'])
    
    # 地缘政治文章使用专用模板
    if topic in ["伊朗局势", "中东冲突", "战争风险", "油价上涨", "全球经济"]:
        template_type = random.choice(["alert", "geopolitical"])
    else:
        template_type = random.choice(["question", "alert", "information_gap"])
    
    templates = TITLE_TEMPLATES[template_type]
    
    # 生成标题
    for template in templates:
        title = template.format(topic=topic, adj=adj, group=group)
        if title not in used_titles:
            return title
    
    # 如果都重复了，添加日期
    return f"2026西班牙{topic}最新：{adj}趋势来了"

def main():
    print("=" * 60)
    print("✨ Title Generator - 生成爆款中文标题")
    print("=" * 60)
    
    # 读取RSS文章
    data_dir = Path("data")
    try:
        with open(data_dir / "rss_articles.json", 'r', encoding='utf-8') as f:
            articles = json.load(f)
    except FileNotFoundError:
        print("❌ 未找到 data/rss_articles.json，请先运行 rss_fetcher.py")
        return
    
    print(f"📊 读取 {len(articles)} 篇文章")
    
    # 选择高分文章生成标题
    selected = [a for a in articles if a.get('score', 0) >= 1][:15]
    
    # 生成标题
    generated = []
    used_titles = set()
    
    for art in selected:
        title = generate_title(art, used_titles)
        used_titles.add(title)
        
        generated.append({
            "title": title,
            "original_title": art['title'],
            "source": {
                "name": art['source'],
                "url": art['link'],
                "summary": art['summary'][:200]
            },
            "category": detect_topic(art['title'], art['summary'])[0],
            "date": datetime.now().strftime('%Y-%m-%d')
        })
    
    print(f"\n✅ 生成 {len(generated)} 个爆款标题")
    print("\n📋 标题列表:")
    for i, g in enumerate(generated[:10], 1):
        print(f"   {i}. {g['title']}")
    
    # 保存
    output_file = data_dir / "generated_titles.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(generated, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 已保存: {output_file}")

if __name__ == "__main__":
    main()
