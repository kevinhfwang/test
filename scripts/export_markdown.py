#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
export_markdown.py - 将文章导出为Markdown文件
读取: data/articles.json
输出: content/*.md
"""
import json
import os
import re

def slugify(title):
    """将标题转换为文件名安全的slug"""
    # 移除特殊字符，替换空格为连字符
    slug = re.sub(r'[^\w\s-]', '', title)
    slug = re.sub(r'\s+', '-', slug)
    return slug[:50].lower()

def main():
    print("📄 Export Markdown - 导出文章为Markdown")
    
    # 读取文章
    try:
        with open("data/articles.json", "r", encoding="utf-8") as f:
            articles = json.load(f)
    except FileNotFoundError:
        print("❌ 未找到 data/articles.json")
        return
    
    # 创建输出目录
    os.makedirs("content", exist_ok=True)
    
    exported = 0
    for a in articles:
        title = a.get("title", "Untitled")
        content = a.get("content", "")
        date = a.get("date", "")
        category = a.get("category", "general")
        
        # 生成文件名
        slug = slugify(title)
        if not slug:
            slug = f"article-{exported+1}"
        
        filepath = f"content/{slug}.md"
        
        # 添加frontmatter
        frontmatter = f"""---
title: {title}
date: {date}
category: {category}
---

"""
        
        # 写入文件
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(frontmatter + content)
        
        exported += 1
        print(f"  ✓ 导出: {filepath}")
    
    print(f"\n✅ 已导出 {exported} 篇文章到 content/ 目录")

if __name__ == "__main__":
    main()
