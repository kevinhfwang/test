#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rss_builder.py - 从生成的标题构建RSS feed
输入: data/generated_titles.json
输出: output/spain-hot.xml
"""
import json
from datetime import datetime
from pathlib import Path

def main():
    print("=" * 60)
    print("📡 RSS Builder - 构建RSS feed")
    print("=" * 60)
    
    # 读取生成的标题
    data_dir = Path("data")
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    try:
        with open(data_dir / "generated_titles.json", 'r', encoding='utf-8') as f:
            titles = json.load(f)
    except FileNotFoundError:
        print("❌ 未找到 data/generated_titles.json")
        return
    
    print(f"📊 读取 {len(titles)} 个标题")
    
    # 构建RSS items
    items = []
    for t in titles[:10]:  # 最多10篇
        title = t.get('title', '')
        source = t.get('source', {})
        url = source.get('url', '')
        summary = source.get('summary', '')[:150]
        date = t.get('date', datetime.now().strftime('%Y-%m-%d'))
        category = t.get('category', 'general')
        
        item = f"""    <item>
      <title><![CDATA[{title}]]></title>
      <link>{url}</link>
      <description><![CDATA[来源: {source.get('name', '西班牙媒体')} | 分类: {category} | {summary}...]]></description>
      <pubDate>{date}</pubDate>
      <guid isPermaLink="false">{hash(title) & 0xFFFFFFFF}</guid>
    </item>"""
        items.append(item)
    
    # 构建完整RSS
    now = datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")
    
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
    output_file = output_dir / "spain-hot.xml"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(rss)
    
    print(f"\n✅ RSS构建完成")
    print(f"📁 保存到: {output_file}")
    print(f"📊 包含 {len(items)} 篇文章")
    print(f"⏰ 最后更新: {now}")

if __name__ == "__main__":
    main()
