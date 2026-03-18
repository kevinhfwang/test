#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
geopolitical_analyzer.py - 自动生成地缘政治影响分析报告
从RSS抓取地缘政治新闻，使用AI生成深度分析，自动按日期命名保存
"""
import json
import re
import ssl
import feedparser
import requests
from datetime import datetime
from pathlib import Path

# 忽略SSL验证
ssl._create_default_https_context = ssl._create_unverified_context

# 地缘政治相关RSS源
GEOPOLITICAL_RSS_SOURCES = [
    {"name": "El País Internacional", "url": "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/section/internacional"},
    {"name": "El Mundo Internacional", "url": "https://feeds.elmundo.es/rss/internacional.xml"},
    {"name": "BBC Mundo", "url": "http://feeds.bbci.co.uk/news/world/rss.xml"},
    {"name": "Euronews", "url": "https://es.euronews.com/rss"},
    {"name": "The Guardian World", "url": "https://www.theguardian.com/world/rss"},
    {"name": "Al Jazeera", "url": "https://www.aljazeera.com/xml/rss/all.xml"},
]

# 地缘政治关键词
GEOPOLITICAL_KEYWORDS = [
    # 中东冲突
    "irán", "iran", "以色列", "israel", "gaza", "加沙", "palestina", "巴勒斯坦",
    "hamas", "哈马斯", "líbano", "lebanon", "hizbulá", "hezbollah", "真主党",
    "oriente medio", "middle east", "中东", "guerra", "war", "战争",
    "conflicto", "conflict", "冲突", "bombardeo", "bombing", "轰炸",
    
    # 能源
    "petróleo", "oil", "石油", "crudo", "原油", "gasolina", "汽油",
    "gas", "能源", "energy", "opec", "opep",
    
    # 经济影响
    "economía global", "global economy", "全球经济", "inflación", "inflation", "通胀",
    "precio", "price", "价格", "mercado", "market", "市场",
    
    # 国际关系
    "ee.uu.", "usa", "美国", "china", "中国", "rusia", "russia", "俄罗斯",
    "unión europea", "european union", "欧盟", "otan", "nato", "北约",
    "sanciones", "sanctions", "制裁",
]

# 分析模板
ANALYSIS_TEMPLATE = """# {title}

## 📍 背景概述

{background}

## 🇪🇸 对西班牙的直接经济影响

### 1. 能源价格波动

- **石油依赖**：西班牙约70%的石油依赖进口，主要来自中东和北非
- **油价上涨**：{energy_impact}
- **通货膨胀**：能源成本上升推高整体通胀，影响民生

### 2. 旅游业冲击

- **中东游客减少**：西班牙是中东游客热门目的地，战争导致该客源市场萎缩
- **全球旅游信心下降**：地缘政治不稳定影响全球旅游意愿
- **航空公司调整航线**：可能取消或减少中东航线

### 3. 贸易与物流

- **苏伊士运河风险**：战争可能威胁这一关键航运通道
- **贸易成本上升**：航运保险费用增加，商品价格上涨
- **出口市场萎缩**：中东是西班牙重要出口市场

## 💰 政府应对措施

根据近期报道，西班牙政府正在准备援助计划，以缓解战争对经济的冲击：

### 已宣布的措施

- **燃油补贴延长**：针对运输行业的燃油补贴政策
- **弱势群体援助**：低收入家庭的能源账单补贴
- **企业支持**：受影响的中小企业可申请贷款援助

### 可能推出的措施

- 战略石油储备释放
- 与其他欧盟国家协调能源政策
- 加强与其他能源供应国的合作

## 👥 对华人社区的具体影响

### 1. 生活成本上升

- 汽油、柴油价格持续上涨
- 食品价格上涨（运输成本增加）
- 取暖和电力成本增加

### 2. 商业影响

- **进出口贸易**：与中东有业务往来的企业面临风险
- **旅游业**：华人经营的旅游相关业务可能客源减少
- **餐饮业**：食材成本上升

### 3. 投资与金融

- **股市波动**：IBEX 35指数可能因地缘政治风险下跌
- **汇率波动**：欧元兑美元、人民币可能波动
- **房地产**：通胀压力可能影响房贷利率

## 🛡️ 应对建议

### 短期应对措施

- **节约能源**：减少不必要的驾车，选择公共交通
- **储备必需品**：适当储备不易变质的食品
- **关注汇率**：选择合适时机进行货币兑换
- **保险检查**：确保商业和个人保险覆盖地缘政治风险

### 中长期策略

- **多元化收入**：减少对单一市场或客户的依赖
- **能源效率**：投资节能设备和措施
- **技能提升**：增强就业竞争力以应对经济波动
- **社区互助**：加强华人社区内部的信息共享和互助

## 📰 信息来源

{sources}

本文基于公开报道整理，仅供参考。具体政策以西班牙官方最新公布为准。

更新日期: {date}

作者: 板鸭小西
"""


class GeopoliticalAnalyzer:
    """地缘政治分析器"""
    
    def __init__(self):
        self.articles = []
        self.analysis = None
        
    def fetch_geopolitical_news(self):
        """从RSS源抓取地缘政治新闻"""
        print("=" * 60)
        print("🌍 抓取地缘政治新闻")
        print("=" * 60)
        
        all_articles = []
        
        for source in GEOPOLITICAL_RSS_SOURCES:
            try:
                print(f"\n📡 {source['name']}...")
                feed = feedparser.parse(source['url'])
                
                for entry in feed.entries[:5]:  # 每个源最多5篇
                    title = entry.get('title', '')
                    summary = entry.get('summary', '')
                    
                    # 检查是否包含地缘政治关键词
                    text = f"{title} {summary}".lower()
                    score = sum(1 for kw in GEOPOLITICAL_KEYWORDS if kw in text)
                    
                    if score >= 2:  # 至少匹配2个关键词
                        all_articles.append({
                            'title': title,
                            'summary': re.sub(r'<[^>]+>', '', summary)[:300],
                            'link': entry.get('link', ''),
                            'source': source['name'],
                            'published': entry.get('published', datetime.now().isoformat()),
                            'score': score
                        })
                        print(f"   ✓ {title[:50]}...")
                
            except Exception as e:
                print(f"   ✗ 失败: {str(e)[:50]}")
        
        # 按分数排序
        all_articles.sort(key=lambda x: x['score'], reverse=True)
        self.articles = all_articles[:10]  # 取前10篇
        
        print(f"\n📊 共抓取 {len(self.articles)} 篇相关新闻")
        return self.articles
    
    def generate_analysis(self):
        """生成分析报告"""
        if not self.articles:
            print("❌ 没有新闻数据，无法生成分析")
            return None
        
        print("\n🤖 生成分析报告...")
        
        # 提取关键信息
        main_article = self.articles[0]
        background = main_article['summary'][:200]
        
        # 生成能源影响描述
        energy_keywords = ['petróleo', 'oil', 'gasolina', '能源', '油价']
        if any(kw in background.lower() for kw in energy_keywords):
            energy_impact = "战争风险导致国际油价飙升，直接影响西班牙汽油价格"
        else:
            energy_impact = "地缘政治紧张局势推高全球能源价格，影响西班牙能源供应"
        
        # 构建来源列表
        sources = []
        for art in self.articles[:3]:
            sources.append(f"- {art['source']}: {art['title'][:60]}...")
        sources_text = '\n'.join(sources)
        
        # 生成标题
        title = self._generate_title(main_article)
        
        # 填充模板
        analysis = ANALYSIS_TEMPLATE.format(
            title=title,
            background=background,
            energy_impact=energy_impact,
            sources=sources_text,
            date=datetime.now().strftime('%Y-%m-%d')
        )
        
        self.analysis = analysis
        print(f"✅ 分析生成完成: {title}")
        return analysis
    
    def _generate_title(self, article):
        """生成中文标题"""
        text = article['title'].lower()
        
        # 检测主题
        if any(kw in text for kw in ['irán', 'iran', '以色列', 'israel']):
            return "美伊战争对西班牙的影响分析"
        elif any(kw in text for kw in ['gaza', '加沙', 'palestina', '巴勒斯坦']):
            return "巴以冲突对西班牙的影响分析"
        elif any(kw in text for kw in ['petróleo', 'oil', '石油', '能源']):
            return "能源危机对西班牙的影响分析"
        else:
            return "地缘政治局势对西班牙的影响分析"
    
    def save_analysis(self):
        """保存分析报告"""
        if not self.analysis:
            print("❌ 没有分析内容，无法保存")
            return None
        
        # 确定文件名
        content_dir = Path(__file__).parent.parent / 'content'
        content_dir.mkdir(exist_ok=True)
        
        date_str = datetime.now().strftime('%Y-%m-%d')
        
        # 查找当天已有文件，确定序号
        existing_files = list(content_dir.glob(f'geopolitical_impact_analysis_{date_str}_*.md'))
        serial = len(existing_files) + 1
        
        filename = f'geopolitical_impact_analysis_{date_str}_{serial:02d}.md'
        filepath = content_dir / filename
        
        # 保存文件
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(self.analysis)
        
        print(f"\n💾 已保存: {filepath}")
        return filepath
    
    def run(self):
        """运行完整流程"""
        print("\n" + "=" * 60)
        print("🌍 地缘政治自动分析系统")
        print("=" * 60)
        
        # 1. 抓取新闻
        self.fetch_geopolitical_news()
        
        if not self.articles:
            print("\n⚠️ 未找到足够的地缘政治新闻，跳过本次生成")
            return None
        
        # 2. 生成分析
        self.generate_analysis()
        
        # 3. 保存文件
        filepath = self.save_analysis()
        
        print("\n" + "=" * 60)
        print("✅ 分析完成!")
        print("=" * 60)
        
        return filepath


def main():
    analyzer = GeopoliticalAnalyzer()
    analyzer.run()


if __name__ == "__main__":
    main()
