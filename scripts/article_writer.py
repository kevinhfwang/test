#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
article_writer.py - 从生成的标题生成文章内容
读取: data/generated_titles.json
输出: data/articles.json
"""
import json
import datetime
import random

# 内容模板库 - 用于生成丰富的中文内容
CONTENT_TEMPLATES = {
    "签证": {
        "intro": [
            "最近西班牙签证政策的变化引起了很多华人的关注。",
            "西班牙签证申请有了新动向，对于计划前往西班牙的人来说是个重要消息。",
            "西班牙政府近期对签证政策进行了调整，值得申请者留意。"
        ],
        "implications": [
            "对于计划来西班牙留学、工作或定居的华人来说，这个变化需要特别关注。",
            "签证政策的变化可能影响申请流程和所需材料，建议提前了解。",
            "这一调整对有意前往西班牙的华人将产生直接影响。"
        ],
        "suggestions": [
            "建议持续关注西班牙驻华使领馆的最新公告，提前准备申请材料。",
            "如有疑问，建议咨询专业移民律师或签证代理机构。",
            "建议提前3-6个月准备签证申请，确保材料真实完整。"
        ],
        "closing": [
            "西班牙签证政策近年来变化较快，建议关注最新官方信息。",
            "及时了解政策变化，有助于顺利完成签证申请。",
            "保持对政策动态的关注，是成功申请签证的关键。"
        ]
    },
    "居留": {
        "intro": [
            "西班牙居留政策近期有新变化，引起在西班牙华人的广泛关注。",
            "对于在西班牙长期居住的华人来说，居留政策的调整是个重要消息。",
            "西班牙政府近期对居留政策进行了更新，值得留意。"
        ],
        "implications": [
            "对于在西班牙的华人来说，这个变化可能直接影响您的合法身份。",
            "居留政策的调整可能影响续签条件和申请流程。",
            "这一变化对在西班牙生活的华人社区有重要影响。"
        ],
        "suggestions": [
            "建议及时了解最新规定，确保身份合法有效。",
            "建议保留好居住证明、工作合同等材料，以备续签使用。",
            "如有疑问，建议咨询专业移民律师。"
        ],
        "closing": [
            "西班牙居留政策变化频繁，建议通过官方渠道保持信息更新。",
            "及时了解政策动态，有助于维护自身合法权益。",
            "关注政策变化，是在西班牙长期生活的重要一环。"
        ]
    },
    "移民": {
        "intro": [
            "西班牙移民政策迎来重要调整，这一消息引起广泛关注。",
            "对于有意移民西班牙的华人来说，政策变化是个重要消息。",
            "西班牙政府近期推出了新的移民政策，值得留意。"
        ],
        "implications": [
            "这一政策变化为有意移民西班牙的华人提供了新的机会。",
            "移民政策的调整可能影响申请条件和审批流程。",
            "对于有移民计划的人来说，这是一个需要关注的时机。"
        ],
        "suggestions": [
            "建议通过正规渠道申请，准备充分的材料。",
            "建议咨询专业移民律师，了解最新政策细节。",
            "建议提前规划，确保申请过程合法合规。"
        ],
        "closing": [
            "西班牙移民政策不断调整，建议关注最新官方信息。",
            "及时了解政策变化，有助于把握移民机会。",
            "保持对移民政策的关注，是成功移民的重要一步。"
        ]
    },
    "税务": {
        "intro": [
            "西班牙税务政策近期有调整，对于在西班牙工作和生活的华人来说值得关注。",
            "西班牙政府近期对税务政策进行了更新，可能影响纳税人。",
            "税务政策的变化是近期西班牙华人社区关注的热点。"
        ],
        "implications": [
            "这一变化可能影响在西班牙工作、生活和投资的华人。",
            "税务政策的调整可能改变个人和企业的税负。",
            "对于自雇人士和企业主来说，这一变化需要特别关注。"
        ],
        "suggestions": [
            "建议及时了解IRPF个人所得税、IVA增值税等相关规定。",
            "建议聘请专业税务顾问，确保合规纳税。",
            "建议保留好相关财务凭证，以备税务申报使用。"
        ],
        "closing": [
            "西班牙税务政策较为复杂，建议通过专业渠道获取信息。",
            "及时了解税务变化，有助于合理规划个人财务。",
            "遵守税务规定，是在西班牙长期生活的基础。"
        ]
    },
    "教育": {
        "intro": [
            "西班牙教育政策近期有重要更新，引起家长和学生的关注。",
            "对于在西班牙留学的学生和有学龄子女的家庭来说，这一消息值得关注。",
            "西班牙教育部近期推出了新的政策措施。"
        ],
        "implications": [
            "这一变化可能影响在西班牙的留学生和教育相关群体。",
            "教育政策的调整可能影响学费、入学条件等方面。",
            "对于华人家庭来说，这一变化需要特别关注。"
        ],
        "suggestions": [
            "建议密切关注所在学校的官方通知。",
            "建议提前了解入学政策和学费变化。",
            "建议通过官方渠道获取最新教育信息。"
        ],
        "closing": [
            "西班牙教育体系对国际学生相对友好，但政策变化频繁。",
            "及时了解教育政策，有助于做好学业规划。",
            "关注教育动态，是为孩子规划未来的重要一环。"
        ]
    },
    "就业": {
        "intro": [
            "西班牙就业市场近期有新动态，对于求职者和在职人员来说都是重要消息。",
            "西班牙劳动市场政策近期有调整，值得关注。",
            "就业政策的变化可能影响在西班牙工作的华人。"
        ],
        "implications": [
            "这一变化对在西班牙求职或工作的华人都有影响。",
            "就业政策的调整可能影响工作许可和劳工权益。",
            "对于自雇人士来说，这一变化需要特别关注。"
        ],
        "suggestions": [
            "建议关注行业发展趋势，提升专业技能。",
            "建议了解自身劳工权益，确保合法工作。",
            "建议通过正规渠道寻找工作机会。"
        ],
        "closing": [
            "西班牙就业市场持续改善，为求职者提供了更多机会。",
            "及时了解就业政策，有助于把握职业发展机遇。",
            "关注就业动态，是在西班牙事业发展的重要一环。"
        ]
    },
    "房产": {
        "intro": [
            "西班牙房地产市场近期出现重要变化，引起投资者和租户的关注。",
            "房产政策的调整是近期西班牙华人社区关注的热点。",
            "对于有意投资西班牙房产的华人来说，这一消息值得关注。"
        ],
        "implications": [
            "这一变化可能影响房产投资者和租房者的决策。",
            "房产政策的调整可能影响房价和租金走势。",
            "对于在西班牙居住的人来说，这一变化有直接影响。"
        ],
        "suggestions": [
            "建议关注房价走势和租金变化。",
            "建议了解购房和租房的相关政策。",
            "建议咨询专业机构，做出明智决策。"
        ],
        "closing": [
            "西班牙房产市场具有投资价值，但需要谨慎决策。",
            "及时了解房产政策，有助于做出明智选择。",
            "关注市场动态，是房产投资的重要一环。"
        ]
    },
    "default": {
        "intro": [
            "最近西班牙的一条新闻引起了很多关注。",
            "西班牙近期有重要政策变化，值得留意。",
            "对于在西班牙或计划前往西班牙的人来说，这是个重要消息。"
        ],
        "implications": [
            "对于计划来西班牙留学、移民或工作的华人来说，这个变化值得关注。",
            "这一政策调整可能影响在西班牙生活的方方面面。",
            "对于华人社区来说，了解这一变化很重要。"
        ],
        "suggestions": [
            "建议持续关注官方政策变化，并提前规划。",
            "建议通过官方渠道获取最新信息。",
            "如有疑问，建议咨询专业人士。"
        ],
        "closing": [
            "西班牙政策近年来变化较快，建议关注最新官方信息。",
            "及时了解政策动态，有助于更好地适应在西班牙的生活。",
            "保持信息更新，是在西班牙生活的重要一环。"
        ]
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
        "房产": ["vivienda", "alquiler", "房产", "房价", "租房"],
    }
    for cat, words in keywords.items():
        if any(w in title_lower for w in words):
            return cat
    return "default"

def generate_article(title, source_summary, category):
    """生成完整的文章"""
    template = CONTENT_TEMPLATES.get(category, CONTENT_TEMPLATES["default"])
    
    article = f"""# {title}

{random.choice(template['intro'])}

## 原始新闻摘要

{source_summary[:200] if source_summary else "根据西班牙媒体报道，相关政策近期出现重要变化。"}

## 这意味着什么？

{random.choice(template['implications'])}

## 建议

{random.choice(template['suggestions'])}

## 总结

{random.choice(template['closing'])}

---

*本文内容仅供参考，不构成任何投资或移民建议。政策信息可能随时变化，请以西班牙官方最新公布为准。*
"""
    return article

def main():
    print("📝 Article Writer - 生成文章内容")
    
    # 读取生成的标题
    try:
        with open("data/generated_titles.json", "r", encoding="utf-8") as f:
            titles = json.load(f)
    except FileNotFoundError:
        print("❌ 未找到 data/generated_titles.json")
        return
    
    articles = []
    
    for t in titles[:5]:
        title = t.get('title', '西班牙政策变化')
        source_summary = t.get('source', {}).get('summary', '')
        
        # 检测类别
        category = detect_category(title)
        
        # 生成文章
        content = generate_article(title, source_summary, category)
        
        articles.append({
            "title": title,
            "content": content,
            "category": category,
            "date": str(datetime.date.today())
        })
        
        print(f"  ✓ 生成: {title[:40]}...")
    
    # 保存文章
    with open("data/articles.json", "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 已生成 {len(articles)} 篇文章")
    print("📁 保存到: data/articles.json")

if __name__ == "__main__":
    main()
