#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rss_builder.py - 构建RSS feed
读取: data/articles.json
输出: spain-hot.xml
生成链接指向 content/*.md
"""
import json
import datetime
import urllib.parse

def main():
    print("📡 RSS Builder - 构建RSS feed")
    
    # 读取文章
    try:
        with open("data/articles.json", "r", encoding="utf-8") as f:
            articles = json.load(f)
    except FileNotFoundError:
        print("❌ 未找到 data/articles.json")
        return
    
    # 构建RSS items
    items = []
    for a in articles[:10]:  # 最多10篇
        title = a.get('title', '')
        content = a.get('content', '')
        date = a.get('date', str(datetime.datetime.now()))
        
        # 提取摘要
        description = content[:150] + "..." if len(content) > 150 else content
        description = description.replace('#', '').replace('*', '').strip()
        
        # 生成 URL 安全 slug（兼容中文和空格）
        slug = urllib.parse.quote(title.replace(" ", "-")[:50])
        
        # 构建RSS item
        item = f"""    <item>
      <title><![CDATA[{title}]]></title>
      <link>https://kevinhfwang.github.io/test/content/{slug}.md</link>
      <description><![CDATA[{description}]]></description>
      <pubDate>{date}</pubDate>
      <guid isPermaLink="false">{hash(title) & 0xFFFFFFFF}</guid>
    </item>"""
        items.append(item)
    
    # 构建完整RSS
    now = datetime.datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")
    
    rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title><![CDATA[🇪🇸 西班牙身份留学热点日报]]></title>
    <link>https://kevinhfwang.github.io/test/</link>
    <description><![CDATA[聚焦西班牙移民、留学、生活政策变化 - 为华人社区提供最新资讯]]></description>
    <language>zh-CN</language>
    <lastBuildDate>{now}</lastBuildDate>
    <atom:link href="https://kevinhfwang.github.io/test/spain-hot.xml" rel="self" type="application/rss+xml"/>
{chr(10).join(items)}
  </channel>
</rss>"""
    
    # 保存RSS
    with open("spain-hot.xml", "w", encoding="utf-8") as f:
        f.write(rss)
    
    print(f"\n✅ 已构建RSS feed")
    print(f"📁 保存到: spain-hot.xml")
    print(f"📊 包含 {len(items)} 篇文章")

if __name__ == "__main__":
    main()
