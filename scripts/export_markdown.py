#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
export_markdown.py - 将文章导出为Markdown文件到Obsidian vault
输入: data/articles.json
输出: obsidian_vault/01_Daily_News/*.md
"""
import json
import os
import re
from datetime import datetime
from pathlib import Path

def slugify(title):
    """将标题转换为文件名"""
    slug = re.sub(r'[^\w\s-]', '', title)
    slug = re.sub(r'\s+', '-', slug)
    return slug[:30].lower() or f"article-{datetime.now().strftime('%m%d')}"

def main():
    print("=" * 60)
    print("📄 Export Markdown - 导出Obsidian笔记")
    print("=" * 60)
    
    # 读取文章
    data_dir = Path("data")
    try:
        with open(data_dir / "articles.json", 'r', encoding='utf-8') as f:
            articles = json.load(f)
    except FileNotFoundError:
        print("❌ 未找到 data/articles.json")
        return
    
    # 创建输出目录
    vault_dir = Path("obsidian_vault")
    news_dir = vault_dir / "01_Daily_News"
    news_dir.mkdir(parents=True, exist_ok=True)
    
    # 同时创建 content 目录
    content_dir = Path("content")
    content_dir.mkdir(exist_ok=True)
    
    today = datetime.now()
    date_str = today.strftime('%Y-%m-%d')
    
    exported = 0
    
    for i, art in enumerate(articles, 1):
        title = art.get("title", "Untitled")
        content = art.get("content", "")
        category = art.get("category", "general")
        source_name = art.get("source_name", "")
        source_url = art.get("source_url", "")
        
        # 生成文件名
        slug = slugify(title)
        filename = f"{date_str}_{i:02d}_{slug}.md"
        
        # 构建 frontmatter
        frontmatter = f"""---
title: {title}
date: {date_str}
category: {category}
source: {source_name}
source_url: {source_url}
tags: ["西班牙", "{category}", "{date_str}"]
---

"""
        
        # 写入 Obsidian vault
        filepath = news_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(frontmatter + content)
        
        # 同时写入 content 目录
        content_filepath = content_dir / filename
        with open(content_filepath, 'w', encoding='utf-8') as f:
            f.write(frontmatter + content)
        
        exported += 1
        print(f"  ✓ {filename}")
    
    # 创建每日索引文件
    index_content = f"""# {date_str} 西班牙新闻

## 今日文章 ({exported}篇)

"""
    for i, art in enumerate(articles, 1):
        index_content += f"{i}. [[{date_str}_{i:02d}_{slugify(art['title'])}|{art['title']}]] - {art.get('category', 'general')}\n"
    
    index_file = news_dir / f"{date_str}_index.md"
    with open(index_file, 'w', encoding='utf-8') as f:
        f.write(index_content)
    
    print(f"\n✅ 已导出 {exported} 篇文章")
    print(f"📁 Obsidian: {news_dir}/")
    print(f"📁 Content: {content_dir}/")
    print(f"📋 索引: {index_file.name}")

if __name__ == "__main__":
    main()
