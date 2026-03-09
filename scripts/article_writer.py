#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
article_writer.py - 从生成的标题生成文章内容
输入: data/generated_titles.json
输出: data/articles.json
"""
import json
import random
from datetime import datetime
from pathlib import Path

# 内容模板库
CONTENT_TEMPLATES = {
    "签证": {
        "intro": [
            "最近西班牙签证政策的变化引起了很多华人的关注。",
            "西班牙签证申请有了新动向，对于计划前往西班牙的人来说是个重要消息。",
            "西班牙政府近期对签证政策进行了更新，值得申请者留意。"
        ],
        "key_points": [
            "签证申请条件可能发生调整，建议提前了解最新要求",
            "申请流程和时间可能有所变化，建议预留充足的准备时间",
            "所需材料清单可能更新，建议通过官方渠道确认",
        ],
        "analysis": "对于计划前往西班牙的华人，建议密切关注西班牙驻华使领馆的最新公告。签证政策的变化可能影响申请条件、审批时间和所需材料。建议提前准备，确保材料真实完整。",
    },
    "居留": {
        "intro": [
            "西班牙居留政策近期有新变化，引起在西班牙华人的广泛关注。",
            "对于在西班牙长期居住的华人来说，居留政策的调整是个重要消息。",
            "西班牙政府近期对居留政策进行了更新，值得留意。"
        ],
        "key_points": [
            "居留申请和续签条件可能有所调整",
            "审批流程和所需材料可能发生变化",
            "不同类型居留的规定可能有更新",
        ],
        "analysis": "对于在西班牙的华人，居留政策变化可能直接影响您的合法身份。建议及时了解最新规定，确保身份合法有效。建议保留好居住证明、工作合同等材料。",
    },
    "移民": {
        "intro": [
            "西班牙移民政策迎来重要调整，这一消息引起广泛关注。",
            "对于有意移民西班牙的华人来说，政策变化是个重要消息。",
            "西班牙政府近期推出了新的移民政策，值得留意。"
        ],
        "key_points": [
            "移民申请条件可能出现新的变化",
            "合法化途径和政策可能有所调整",
            "对特定群体的移民政策可能有优惠",
        ],
        "analysis": "西班牙移民政策的变化为有意移民者提供了新的机会。建议通过正规渠道申请，准备充分的材料。建议咨询专业移民律师，了解最新政策细节。",
    },
    "教育": {
        "intro": [
            "西班牙教育政策近期有重要更新，引起家长和学生的关注。",
            "对于在西班牙留学的学生和有学龄子女的家庭来说，这一消息值得关注。",
            "西班牙教育部近期推出了新的政策措施。"
        ],
        "key_points": [
            "教育费用和奖学金政策可能调整",
            "学生签证和居留政策可能有变化",
            "公立学校的入学政策可能有更新",
        ],
        "analysis": "对于在西班牙留学的华人学生，建议密切关注所在学校的官方通知。家长在为孩子规划教育路径时，应充分考虑这些政策因素。",
    },
    "租房": {
        "intro": [
            "西班牙租房市场近期出现重要变化，引起广泛关注。",
            "对于在西班牙租房的华人来说，这是一个需要关注的消息。",
            "西班牙租房政策近期有调整，值得留意。"
        ],
        "key_points": [
            "房租水平和租赁条款可能有所调整",
            "租客权益保护可能有新的规定",
            "租房合同和押金规定可能有变化",
        ],
        "analysis": "西班牙租房市场的变化直接影响在西班牙生活的华人。建议了解自身权益，签订正规合同，保留好租金支付凭证。",
    },
    "工作": {
        "intro": [
            "西班牙就业市场近期有新动态，对于求职者和在职人员来说都是重要消息。",
            "西班牙劳动市场政策近期有调整，值得关注。",
            "就业政策的变化可能影响在西班牙工作的华人。"
        ],
        "key_points": [
            "就业市场趋势和行业需求可能变化",
            "劳工合同和工作许可政策可能调整",
            "对自雇人士的政策可能有更新",
        ],
        "analysis": "西班牙就业市场的变化对华人求职者和创业者都有影响。建议关注行业发展趋势，提升语言能力和专业技能。",
    },
    "默认": {
        "intro": [
            "最近西班牙的一条新闻引起了很多关注。",
            "西班牙近期有重要政策变化，值得留意。",
            "对于在西班牙或计划前往西班牙的人来说，这是个重要消息。"
        ],
        "key_points": [
            "政策细节可能有所调整",
            "申请流程和条件可能变化",
            "建议通过官方渠道了解最新信息",
        ],
        "analysis": "对于在西班牙的华人社区，这一变化需要持续关注。建议通过官方渠道获取最新信息，必要时咨询专业人士。",
    }
}

def detect_category(title):
    """根据标题检测类别"""
    title_lower = title.lower()
    keywords = {
        "签证": ["visa", "visado", "签证"],
        "居留": ["residencia", "居留"],
        "移民": ["inmigrante", "immigration", "migración", "移民"],
        "税务": ["impuesto", "tax", "税务", "税收"],
        "教育": ["educación", "education", "estudiante", "教育", "留学"],
        "就业": ["empleo", "trabajo", "就业", "工作"],
        "租房": ["vivienda", "alquiler", "房产", "房价", "租房"],
    }
    for cat, words in keywords.items():
        if any(w in title_lower for w in words):
            return cat
    return "默认"

def generate_article(title, source_summary, category):
    """生成完整的文章"""
    template = CONTENT_TEMPLATES.get(category, CONTENT_TEMPLATES["默认"])
    
    # 随机选择模板
    intro = random.choice(template['intro'])
    key_points = template['key_points']
    analysis = template['analysis']
    
    # 构建文章内容
    article_content = f"""# {title}

{intro}

## 政策要点

{chr(10).join(['• ' + point for point in key_points])}

## 详细解读

{source_summary[:200] if source_summary else '根据西班牙媒体报道，相关政策近期出现重要变化。'}

## 对华人社区的影响

{analysis}

## 实用建议

1. **及时关注**：通过官方渠道了解最新政策动态
2. **准备材料**：提前准备好相关证明文件
3. **专业咨询**：如有疑问，建议咨询专业律师或顾问
4. **保持更新**：定期查看政策变化，确保信息最新

---

*本文内容仅供参考，不构成任何投资或移民建议。政策信息可能随时变化，请以西班牙官方最新公布为准。*
"""
    return article_content

def main():
    print("=" * 60)
    print("📝 Article Writer - 生成文章内容")
    print("=" * 60)
    
    # 读取生成的标题
    data_dir = Path("data")
    try:
        with open(data_dir / "generated_titles.json", 'r', encoding='utf-8') as f:
            titles = json.load(f)
    except FileNotFoundError:
        print("❌ 未找到 data/generated_titles.json")
        return
    
    print(f"📊 读取 {len(titles)} 个标题")
    
    articles = []
    
    for t in titles[:5]:  # 只生成前5篇详细内容
        title = t.get('title', '')
        source = t.get('source', {})
        source_summary = source.get('summary', '')
        
        # 检测类别
        category = detect_category(title)
        
        # 生成文章
        content = generate_article(title, source_summary, category)
        
        articles.append({
            "title": title,
            "content": content,
            "category": category,
            "date": t.get('date', datetime.now().strftime('%Y-%m-%d')),
            "source_name": source.get('name', ''),
            "source_url": source.get('url', '')
        })
        
        print(f"  ✓ 生成: {title[:40]}...")
    
    # 保存
    output_file = data_dir / "articles.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 已生成 {len(articles)} 篇文章")
    print(f"📁 保存到: {output_file}")

if __name__ == "__main__":
    main()
