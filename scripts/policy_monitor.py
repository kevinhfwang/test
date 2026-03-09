#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
policy_monitor.py - 检测政策相关新闻并生成更新建议
输入: https://kevinhfwang.github.io/test/spain-hot.xml
输出: obsidian_vault/03_Policy_Monitoring/*.md
"""
import feedparser
import datetime
import os
import re
from pathlib import Path

# RSS源
RSS_URL = "https://kevinhfwang.github.io/test/spain-hot.xml"

# 输出目录
OUTPUT_DIR = Path("obsidian_vault/03_Policy_Monitoring")

# 政策关键词（中英文）
POLICY_KEYWORDS = [
    # 移民/居留类
    "visa", "residency", "immigration", "residence permit", "work permit", 
    "citizenship", "digital nomad", "golden visa", 
    "migración", "visado", "residencia", "extranjería", "inmigrante",
    "permiso de residencia", "permiso de trabajo", "nacionalidad", "ciudadanía",
    # 教育类
    "student", "education", "university", "master", "beca", "matrícula",
    "estudiante", "educación", "universidad", "carrera",
    # 房产类
    "housing", "rent", "alquiler", "vivienda", "hipoteca", "compra",
    # 税务类
    "tax", "impuesto", "hacienda", "irpf", "iva", "deducción",
    # 就业类
    "employment", "work", "trabajo", "empleo", "autónomo", "paro",
    # 其他政策
    "law", "ley", "policy", "política", "decreto", "reforma",
    "normativa", "regulación", "legislación"
]

def is_policy_news(title, summary):
    """检测是否为政策相关新闻"""
    text = (title + " " + summary).lower()
    return any(k in text for k in POLICY_KEYWORDS)

def slugify(text):
    """生成文件名安全的slug"""
    slug = re.sub(r'[^\w\s-]', '', text)
    slug = re.sub(r'\s+', '-', slug)
    return slug[:30].lower()

def get_category(title, summary):
    """根据内容判断类别"""
    text = (title + " " + summary).lower()
    
    if any(k in text for k in ["visa", "visado", "residencia", "residency", "immigration", "migración"]):
        return "移民居留"
    elif any(k in text for k in ["student", "estudiante", "education", "educación", "universidad"]):
        return "教育留学"
    elif any(k in text for k in ["housing", "vivienda", "alquiler", "rent"]):
        return "房产租房"
    elif any(k in text for k in ["tax", "impuesto", "hacienda", "irpf"]):
        return "税务财务"
    elif any(k in text for k in ["work", "trabajo", "empleo", "autónomo"]):
        return "就业工作"
    else:
        return "其他政策"

def generate_update(entry, date):
    """生成政策更新建议文件"""
    title = entry.get('title', '')
    link = entry.get('link', '')
    summary = entry.get('summary', '')
    category = get_category(title, summary)
    
    # 生成文件名
    filename = f"{date}-{slugify(title)}.md"
    filepath = OUTPUT_DIR / filename
    
    # 构建内容
    content = f"""---
title: 政策变化检测 - {title[:50]}
date: {date}
category: {category}
source: {link}
tags: ["政策监控", "{category}", "{date}"]
---

# 📋 政策变化检测

## 来源新闻
- **原文链接**: {link}
- **标题**: {title}
- **摘要**: {summary[:200]}...

## 分类
`{category}`

## 可能影响
- [ ] 西班牙移民 / 居留政策
- [ ] 教育 / 留学政策
- [ ] 房产 / 租房市场
- [ ] 税务 / 财务规定
- [ ] 就业 / 工作许可

## 建议检查
根据此新闻，建议检查以下文件是否需要更新：

### 身份路径 (04_Identity_Pathways)
- [[04_Identity_Pathways/Identity_Pathways_Overview|身份路径概览]]

### 城市数据 (05_City_Database)
- [[05_City_Database/City_Database_Madrid|马德里城市数据]]
- [[05_City_Database/City_Database_Navarra|纳瓦拉城市数据]]

### 成本数据 (06_Cost_Database)
- [[06_Cost_Database/Cost_Database_2026|2026成本数据库]]

## 行动项
- [ ] 阅读原文确认政策细节
- [ ] 检查相关文件是否需要更新
- [ ] 如有重大变化，创建新的文章解读

---
*生成时间: {date}*  
*自动检测脚本: policy_monitor.py*
"""
    
    # 确保目录存在
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # 写入文件
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"  ✓ 生成政策更新建议: {filename}")
    return filename

def generate_daily_summary(detected_count, date):
    """生成每日政策监控摘要"""
    summary_file = OUTPUT_DIR / f"{date}_DAILY_SUMMARY.md"
    
    # 列出今天的所有政策文件
    policy_files = sorted([f for f in OUTPUT_DIR.glob(f"{date}-*.md") if not f.name.endswith("_SUMMARY.md")])
    
    content = f"""---
title: {date} 政策监控日报
date: {date}
category: 监控日报
tags: ["政策监控", "日报", "{date}"]
---

# 📊 {date} 政策监控日报

## 概览
- **检测时间**: {date}
- **检测到政策相关新闻**: {detected_count} 条

## 今日检测到的政策新闻

"""
    
    if policy_files:
        for i, f in enumerate(policy_files, 1):
            # 从文件名提取标题
            title_part = f.stem.replace(f"{date}-", "").replace("-", " ")
            content += f"{i}. [[{f.stem}|{title_part}]]\n"
    else:
        content += "_今日未检测到政策相关新闻_\n"
    
    content += f"""

## 待办事项
- [ ] 检查上述政策新闻的重要性
- [ ] 如有重大政策变化，更新相关数据库文件
- [ ] 在每周分析中汇总本周政策趋势

---
*自动生成于 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
    
    with open(summary_file, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"  ✓ 生成日报摘要: {summary_file.name}")

def main():
    print("=" * 60)
    print("🔍 Policy Monitor - 政策变化检测")
    print("=" * 60)
    
    today = datetime.date.today().isoformat()
    print(f"\n📅 检测日期: {today}")
    
    # 抓取RSS
    print(f"\n📡 从 RSS 源抓取: {RSS_URL}")
    feed = feedparser.parse(RSS_URL)
    
    if not feed.entries:
        print("⚠️ 未能获取 RSS 条目")
        return
    
    print(f"📊 获取 {len(feed.entries)} 条新闻")
    
    # 检测政策新闻
    detected = []
    for entry in feed.entries[:15]:  # 检查前15条
        title = entry.get('title', '')
        summary = entry.get('description', '') or entry.get('summary', '')
        
        if is_policy_news(title, summary):
            detected.append(entry)
            category = get_category(title, summary)
            print(f"  🔍 [{category}] {title[:50]}...")
    
    print(f"\n📋 检测到 {len(detected)} 条政策相关新闻")
    
    # 生成文件
    if detected:
        for entry in detected:
            generate_update(entry, today)
    
    # 生成日报摘要
    generate_daily_summary(len(detected), today)
    
    print(f"\n✅ 政策监控完成")
    print(f"📁 输出目录: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
