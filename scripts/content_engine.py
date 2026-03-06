#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
content_engine.py - 内容引擎
生成内容并保存到本地，可选上传到微信
"""
import requests
import json
import re
import time
import feedparser
import ssl
from datetime import datetime
from pathlib import Path

ssl._create_default_https_context = ssl._create_default_https_context

WECHAT_APPID = 'wxc84159b815237de7'
WECHAT_APPSECRET = '15db1f3e77aedd8c13af291b36f45121'
GITHUB_RSS_URL = "https://kevinhfwang.github.io/test/spain-hot.xml"
BORDER_COLORS = ['#3498db', '#e74c3c', '#f39c12', '#27ae60', '#9b59b6']

VIRAL_TITLES_DB = {
    "签证": ["想来的不知道：签证还能这样", "揭秘：西班牙签证的难办真相", "提醒：西班牙签证有新变化", "签证窗口期：想来的抓紧了"],
    "居留": ["揭秘：西班牙居留的严格真相？", "提醒：西班牙居留有新变化？", "西班牙居留变了？真相来了"],
    "移民": ["原来西班牙移民可以这么容易！", "申请者不知道：移民还能这样", "2026年移民：容易趋势来了"],
    "税务": ["税收：马德里和Navarra差多少？", "揭秘：西班牙税收的复杂真相", "西班牙税务新规？纳税人必看"],
    "教育": ["揭秘：西班牙教育政策的变化真相？", "申请者不知道：西班牙教育还能这样？", "西班牙留学新政策？学生党必看"],
    "就业": ["2026年西班牙就业：容易趋势来了？", "西班牙就业市场变了？打工人必看", "西班牙自雇政策变了？老板们注意"],
    "房产": ["西班牙房价还能涨多久？投资者必看", "西班牙租金到底怎么变了？租客注意", "西班牙房产投资新规？投资者必看"],
}

CONTENT_TEMPLATES = {
    "签证": {"intro": "最近西班牙签证政策的变化引起了很多华人的关注。", "implications": "对于计划来西班牙留学、工作或定居的华人来说，这个变化需要特别关注。", "suggestions": "建议持续关注西班牙驻华使领馆的最新公告，提前准备申请材料。", "closing": "西班牙签证政策近年来变化较快，建议关注最新官方信息。", "analysis": "对于计划前往西班牙的华人，建议密切关注西班牙驻华使领馆的最新公告。签证政策的变化可能影响申请条件、审批时间和所需材料。建议提前准备，确保申请材料真实完整。"},
    "居留": {"intro": "西班牙居留政策近期有新变化，引起在西班牙华人的广泛关注。", "implications": "对于在西班牙的华人来说，这个变化可能直接影响您的合法身份。", "suggestions": "建议及时了解最新规定，确保身份合法有效。", "closing": "西班牙居留政策变化频繁，建议通过官方渠道保持信息更新。", "analysis": "对于在西班牙的华人，居留政策变化可能直接影响您的合法身份。建议及时了解最新规定，确保身份合法有效。已经在西班牙的华人应关注续签政策变化，保留好居住证明、工作合同等材料。"},
    "移民": {"intro": "西班牙移民政策迎来重要调整，这一消息对于有意移民西班牙的华人来说意义重大。", "implications": "这一政策变化为有意移民西班牙的华人提供了新的机会。", "suggestions": "建议通过正规渠道申请，准备充分的材料。", "closing": "西班牙移民政策不断调整，建议关注最新官方信息。", "analysis": "西班牙移民政策的变化为有意移民者提供了新的机会。建议通过正规渠道申请，准备充分的材料，确保申请过程合法合规。对于符合条件的申请人，这是一个难得的机会。建议咨询专业移民律师，了解最新政策细节。"},
    "教育": {"intro": "西班牙教育政策近期有重要更新，对于在西班牙留学的学生和有学龄子女的家庭来说，这一消息值得关注。", "implications": "这一变化可能影响在西班牙的留学生和教育相关群体。", "suggestions": "建议密切关注所在学校的官方通知。", "closing": "西班牙的教育体系对国际学生相对友好，但政策变化较为频繁。", "analysis": "对于在西班牙留学的华人学生，建议密切关注所在学校的官方通知。家长在为孩子规划教育路径时，应充分考虑这些政策因素。西班牙的教育体系对国际学生相对友好，建议通过官方渠道保持信息更新。"},
    "就业": {"intro": "西班牙就业市场近期有新动态，对于在西班牙求职或工作的华人来说，这是一个重要的消息。", "implications": "这一变化对在西班牙求职或工作的华人都有影响。", "suggestions": "建议关注行业发展趋势，提升语言能力和专业技能。", "closing": "西班牙就业市场持续改善，为求职者提供了更多机会。", "analysis": "西班牙就业市场的变化对华人求职者和创业者都有影响。建议关注失业率数据、行业发展趋势，以及针对外国人的工作许可政策变化。对于自雇人士，需特别关注社保和税务政策调整。华人社区在餐饮、零售、服务业等领域有一定优势，就业市场改善意味着更多机会。"},
    "税务": {"intro": "西班牙税务政策近期有调整，对于在西班牙工作和生活的华人来说，这一消息需要关注。", "implications": "这一变化可能影响在西班牙工作、生活和投资的华人。", "suggestions": "建议及时了解IRPF个人所得税、IVA增值税等相关规定。", "closing": "西班牙税务政策较为复杂，建议通过专业渠道获取信息。", "analysis": "税务政策的变化直接影响在西班牙工作、生活和投资的华人。建议及时了解IRPF个人所得税、IVA增值税等相关规定，确保合规纳税。对于自雇人士和企业主，建议聘请专业税务顾问，帮助处理复杂的税务申报事宜。"},
    "房产": {"intro": "西班牙房地产市场近期出现重要变化，对于有意投资房产或在西班牙租房的华人来说，这一消息值得关注。", "implications": "这一变化可能影响房产投资者和租房者的决策。", "suggestions": "建议关注房价走势和租金变化。", "closing": "西班牙房产市场具有投资价值，但需要谨慎决策。", "analysis": "对于有意在西班牙投资房产的华人，建议关注房价走势和租金收益率变化。不同城市和区域的房地产市场差异较大，建议实地考察或咨询当地专业机构。对于租房者，新政策提供了更多保护，建议了解自身权益。"},
}

class ContentEngine:
    def fetch_rss(self, url):
        try:
            feed = feedparser.parse(url)
            articles = []
            for entry in feed.entries[:8]:
                summary = re.sub(r'<[^>]+>', '', entry.get('summary', ''))
                articles.append({'title': entry.get('title', ''), 'link': entry.get('link', ''), 'summary': summary, 'published': entry.get('published', '')})
            return articles
        except Exception as e:
            print(f"  ✗ 失败: {e}")
            return []
    
    def fetch_original(self, url):
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            resp = requests.get(url, headers=headers, timeout=15)
            html = resp.text
            html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL|re.I)
            html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL|re.I)
            paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', html, flags=re.DOTALL)
            content_parts = []
            for p in paragraphs:
                text = re.sub(r'<[^>]+>', '', p).strip()
                if 50 < len(text) < 500:
                    content_parts.append(text)
            return ' '.join(content_parts)[:3000]
        except:
            return ""
    
    def detect_category(self, title, content):
        text = f"{title} {content}".lower()
        keywords = {"签证": ["visa", "visado"], "居留": ["residencia"], "移民": ["inmigrante", "immigration", "migración"], "教育": ["educación", "education", "estudiante"], "就业": ["empleo", "trabajo"], "税务": ["impuesto", "tax"], "房产": ["vivienda", "alquiler"]}
        for cat, words in keywords.items():
            if any(w in text for w in words):
                return cat
        return "签证"
    
    def match_viral_title(self, category, used_titles=None):
        if used_titles is None:
            used_titles = []
        titles = VIRAL_TITLES_DB.get(category, VIRAL_TITLES_DB["签证"])
        for title in titles:
            if title not in used_titles:
                return title
        return titles[0]
    
    def generate_chinese_content(self, category, original_text, source_name):
        template = CONTENT_TEMPLATES.get(category, CONTENT_TEMPLATES["签证"])
        sentences = re.split(r'(?<=[.!?])\s+', original_text[:1500])
        original_excerpts = [s.strip()[:150] + "..." for s in sentences[:3] if len(s.strip()) > 50]
        
        html_parts = []
        highlight_points = " | ".join([template["implications"], template["suggestions"]])
        html_parts.append(f'<p style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px; border-radius: 8px; font-size: 15px; line-height: 1.8; margin: 15px 0;"><strong>📢 核心看点：</strong><br/>{highlight_points}</p>')
        html_parts.append(f'<p style="padding-left: 2em; line-height: 1.8; color: #333; margin: 15px 0;">{template["intro"]}</p>')
        html_parts.append('<p style="padding-left: 2em; line-height: 1.8; color: #333; margin: 15px 0;"><strong>主要变化包括：</strong></p>')
        for point in [template["implications"], template["suggestions"], template["closing"]]:
            html_parts.append(f'<p style="padding-left: 2em; line-height: 1.8; color: #333; margin: 10px 0;">• {point}</p>')
        if original_excerpts:
            html_parts.append(f'<p style="background: #f5f5f5; padding: 15px; border-left: 4px solid #999; margin: 15px 0; font-size: 13px; color: #666;"><strong>📰 原文摘录（{source_name}）：</strong><br/>{original_excerpts[0]}</p>')
        html_parts.append(f'<p style="background: #e3f2fd; padding: 15px; border-left: 4px solid #2196f3; margin: 15px 0; font-size: 14px;"><strong>💡 提示：</strong>建议关注官方渠道发布的详细信息，以获取最新、最准确的政策内容。</p>')
        return '\n'.join(html_parts)
    
    def generate_analysis(self, category):
        template = CONTENT_TEMPLATES.get(category, CONTENT_TEMPLATES["签证"])
        return template["analysis"]


def generate_full_html(article, color_index):
    border_color = BORDER_COLORS[color_index % len(BORDER_COLORS)]
    h2 = f'<h2 style="color: #1a1a1a; border-left: 5px solid {border_color}; padding-left: 15px; margin-top: 30px;">{article["title"]}</h2>'
    source_info = f'<p style="background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 4px solid #6c757d; margin: 20px 0; font-size: 14px; color: #495057;"><strong>📰 原文信息</strong><br/><strong>来源：</strong>{article["source_name"]}<br/><strong>发布时间：</strong>{article["publish_date"]}<br/><strong>原文链接：</strong>{article["source_url"]}</p>'
    body_title = f'<h3 style="color: #2c3e50; margin-top: 25px; border-left: 4px solid {border_color}; padding-left: 12px;">📝 正文内容</h3>'
    chinese_title = f'<h3 style="color: #2c3e50; margin-top: 25px; border-left: 4px solid #e74c3c; padding-left: 12px;">👥 华人视角解读</h3>'
    chinese_view = f'<p style="padding-left: 2em; line-height: 1.8; color: #333; margin: 15px 0;">{article["chinese_analysis"]}</p>'
    disclaimer = '<p style="background: #fff3cd; padding: 15px; border-radius: 8px; border-left: 4px solid #ffc107; margin: 20px 0; font-size: 13px; color: #856404;"><strong>⚠️ 免责声明：</strong><br/>本文内容仅供参考，不构成任何投资或移民建议。政策信息可能随时变化，请以西班牙官方最新公布为准。</p>'
    signature = '<p style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 12px; font-size: 16px; line-height: 1.8; margin: 30px 0; text-align: center;"><strong style="font-size: 18px;">板鸭身边事</strong><br/><span style="opacity: 0.9;">带你第一时间掌握西班牙正在发生的事</span></p>'
    return f'<section style="max-width: 100%; padding: 10px;">{h2}{source_info}{body_title}{article["content"]}{chinese_title}{chinese_view}{disclaimer}{signature}</section>'


def get_wechat_token():
    url = 'https://api.weixin.qq.com/cgi-bin/token'
    params = {'grant_type': 'client_credential', 'appid': WECHAT_APPID, 'secret': WECHAT_APPSECRET}
    try:
        return requests.get(url, params=params, timeout=10).json().get('access_token')
    except:
        return None


def main():
    print("=" * 70)
    print("🚀 西班牙新闻内容引擎 (Content Engine)")
    print("=" * 70)
    
    engine = ContentEngine()
    
    rss_articles = engine.fetch_rss(GITHUB_RSS_URL)
    if not rss_articles:
        print("❌ 未能获取RSS话题")
        return
    
    print("\n📝 获取原文并生成中文内容...")
    selected_articles = []
    used_titles = []
    
    for i, rss_art in enumerate(rss_articles[:5]):
        print(f"  [{i+1}] {rss_art['title'][:40]}...")
        original = engine.fetch_original(rss_art['link'])
        time.sleep(0.5)
        category = engine.detect_category(rss_art['title'], original)
        viral_title = engine.match_viral_title(category, used_titles)
        used_titles.append(viral_title)
        chinese_content = engine.generate_chinese_content(category, original, rss_art.get('source', '西班牙媒体'))
        chinese_analysis = engine.generate_analysis(category)
        selected_articles.append({'title': viral_title, 'digest': f"西班牙{category}政策有新变化，点击查看详情", 'source_name': rss_art.get('source', '西班牙媒体'), 'source_url': rss_art['link'], 'publish_date': rss_art.get('published', datetime.now().strftime('%Y-%m-%d')), 'content': chinese_content, 'chinese_analysis': chinese_analysis, 'category': category})
        print(f"      → 类别: {category}")
        print(f"      → 标题: {viral_title}")
    
    print("\n💾 保存生成的内容...")
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    with open(output_dir / f"generated_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", 'w', encoding='utf-8') as f:
        json.dump({'timestamp': datetime.now().isoformat(), 'articles': selected_articles}, f, ensure_ascii=False, indent=2)
    print(f"  ✓ 内容已保存到 output/ 目录")
    
    print("\n🚀 尝试上传到微信公众号...")
    token = get_wechat_token()
    if not token:
        print("  ⚠️ 无法获取微信Token（这在CI环境中是正常的）")
        print("  ✓ 内容已生成本地文件，请手动运行上传到微信")
        return
    
    print("  ✅ 获取Token成功，开始上传...")
    thumb_ids = ['WfulcYFUbeMjJ_9fRU62R2VbfsoC3SXqnJaXRGzkMr6KeDCxS6KtRc5XibVkObtd', 'WfulcYFUbeMjJ_9fRU62R-83GnWuynLS4Aqvu3Rv_PJn1Qk3KTLqyldegX8Hd5t-', 'WfulcYFUbeMjJ_9fRU62R7fXg2D_tIIWtaSyoJDVH7CI3Y_polaJoCGDu4_k1OG4', 'WfulcYFUbeMjJ_9fRU62R2b9pkVKTttbKk7a3YfFvYC5Pm7GQ7h3ZOk_YyEyYvtC', 'WfulcYFUbeMjJ_9fRU62R9RN-j52MudMBWLXFyROKB3jvievpA6YK_jORmtUJOcF']
    
    news_items = []
    for i, art in enumerate(selected_articles):
        html = generate_full_html(art, i)
        news_items.append({'title': art['title'], 'author': '板鸭小西', 'digest': art['digest'], 'content': html, 'content_source_url': art['source_url'], 'thumb_media_id': thumb_ids[i] if i < len(thumb_ids) else thumb_ids[0], 'show_cover_pic': 0, 'need_open_comment': 1, 'only_fans_can_comment': 0})
    
    url = 'https://api.weixin.qq.com/cgi-bin/draft/add'
    payload = {'articles': news_items}
    json_str = json.dumps(payload, ensure_ascii=False)
    headers = {'Content-Type': 'application/json; charset=utf-8'}
    
    try:
        resp = requests.post(url, params={'access_token': token}, data=json_str.encode('utf-8'), headers=headers, timeout=30)
        result = resp.json()
        if 'media_id' in result:
            print("\n" + "=" * 70)
            print("✅ 多图文草稿创建成功！")
            print("=" * 70)
            print(f"📋 Media ID: {result['media_id']}")
            print(f"\n📋 文章清单:")
            for i, art in enumerate(selected_articles):
                print(f"  {i+1}. {art['title']} [{art['category']}]")
            with open(output_dir / f"draft_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", 'w', encoding='utf-8') as f:
                json.dump({'media_id': result['media_id'], 'articles': selected_articles}, f, ensure_ascii=False, indent=2)
        else:
            print(f"\n❌ 上传失败: {result}")
    except Exception as e:
        print(f"\n❌ 错误: {e}")


if __name__ == '__main__':
    main()
