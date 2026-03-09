#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
export_viral_titles.py - 将生成的标题导出为Markdown到Obsidian vault
输入: data/generated_titles.json
输出: obsidian_vault/02_Viral_Titles/*.md
"""
import json
from datetime import datetime
from pathlib import Path

def main():
    print("=" * 60)
    print("🔥 Export Viral Titles - 导出爆款标题")
    print("=" * 60)
    
    # 读取生成的标题
    data_dir = Path("data")
    try:
        with open(data_dir / "generated_titles.json", 'r', encoding='utf-8') as f:
            titles = json.load(f)
    except FileNotFoundError:
        print("❌ 未找到 data/generated_titles.json")
        return
    
    if not titles:
        print("⚠️ 没有标题数据")
        return
    
    # 创建输出目录
    vault_dir = Path("obsidian_vault")
    titles_dir = vault_dir / "02_Viral_Titles"
    titles_dir.mkdir(parents=True, exist_ok=True)
    
    today = datetime.now()
    date_str = today.strftime('%Y-%m-%d')
    
    # 构建 Markdown 内容
    md_content = f"""# {date_str} 爆款标题

> 自动生成于 {today.strftime('%Y-%m-%d %H:%M')}
> 来源：24个西班牙媒体RSS源

## 今日热门标题 ({len(titles)}个)

"""
    
    for i, t in enumerate(titles, 1):
        title = t.get('title', '')
        original = t.get('original_title', '')
        category = t.get('category', 'general')
        source = t.get('source', {})
        source_name = source.get('name', '')
        source_url = source.get('url', '')
        
        md_content += f"""### {i}. {title}

- **中文标题**：{title}
- **原文标题**：{original}
- **分类**：{category}
- **来源**：{source_name}
- **链接**：{source_url}

---

"""
    
    # 写入文件
    filename = f"{date_str} Viral Titles.md"
    filepath = titles_dir / filename
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    print(f"✅ 已导出 {len(titles)} 个标题")
    print(f"📁 保存到: {filepath}")
    
    # 同时更新 README 或索引
    readme_content = f"""# 02_Viral_Titles

爆款标题库 - 每日从西班牙媒体自动生成

## 最新文件

- [[{date_str} Viral Titles|{date_str} 爆款标题]]

## 历史记录

"""
    
    # 列出历史文件
    existing_files = sorted([f for f in titles_dir.glob("*.md") if f.name != "README.md"], reverse=True)
    for f in existing_files[:10]:  # 最近10个
        date_part = f.stem.replace(' Viral Titles', '')
        readme_content += f"- [[{f.stem}|{date_part} 爆款标题]]\n"
    
    readme_path = titles_dir / "README.md"
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"📋 索引: {readme_path.name}")

if __name__ == "__main__":
    main()
