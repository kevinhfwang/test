#!/usr/bin/env python3
"""
Weekly Analysis Module
每周分析模块 - 分析生成的标题，识别高频主题，调整内容策略
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from collections import Counter
from typing import Dict, List

PROJECT_ROOT = Path(__file__).parent.parent
VAULT_PATH = PROJECT_ROOT / "obsidian_vault"
ANALYSIS_PATH = VAULT_PATH / "07_Weekly_Analysis"

class WeeklyAnalyzer:
    def __init__(self):
        self.tracking_file = ANALYSIS_PATH / "theme_tracking.json"
        self.weekly_report_path = ANALYSIS_PATH / "weekly_reports"
        self.weekly_report_path.mkdir(parents=True, exist_ok=True)
    
    def load_tracking_data(self) -> Dict:
        """加载追踪数据"""
        if self.tracking_file.exists():
            with open(self.tracking_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {'daily_records': {}, 'theme_frequency': {}, 'last_updated': ''}
    
    def analyze_last_7_days(self) -> Dict:
        """分析最近7天的数据"""
        data = self.load_tracking_data()
        
        # 获取最近7天的日期
        today = datetime.now()
        last_7_days = [(today - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)]
        
        # 收集数据
        weekly_stats = {
            'total_titles': 0,
            'category_counts': Counter(),
            'daily_breakdown': {}
        }
        
        for day in last_7_days:
            if day in data['daily_records']:
                record = data['daily_records'][day]
                weekly_stats['total_titles'] += record['title_count']
                weekly_stats['daily_breakdown'][day] = record['title_count']
                
                for cat, count in record['categories'].items():
                    weekly_stats['category_counts'][cat] += count
        
        return weekly_stats
    
    def generate_insights(self, stats: Dict) -> List[str]:
        """生成洞察建议"""
        insights = []
        
        # 分析高频主题
        top_categories = stats['category_counts'].most_common(3)
        
        if top_categories:
            insights.append(f"📈 本周最热门主题: {top_categories[0][0]} ({top_categories[0][1]}次)")
            
            # 建议增加其他主题
            all_categories = ['Policy Change', 'Student Visa Path', 'Work Residency', 
                            'Permanent Residency', 'City Comparison', 'Cost of Living']
            missing = set(all_categories) - set([c[0] for c in top_categories])
            if missing:
                insights.append(f"💡 建议增加内容: {', '.join(list(missing)[:2])}")
        
        # 产量分析
        avg_daily = stats['total_titles'] / 7
        if avg_daily < 10:
            insights.append(f"⚠️ 日均产量偏低 ({avg_daily:.1f}/天)，建议检查RSS源")
        else:
            insights.append(f"✅ 日均产量正常 ({avg_daily:.1f}/天)")
        
        return insights
    
    def generate_weekly_report(self):
        """生成周分析报告"""
        print("📊 生成周分析报告...")
        
        stats = self.analyze_last_7_days()
        insights = self.generate_insights(stats)
        
        # 本周日期范围
        today = datetime.now()
        week_start = (today - timedelta(days=6)).strftime('%Y-%m-%d')
        week_end = today.strftime('%Y-%m-%d')
        report_date = today.strftime('%Y-%m-%d')
        
        # 生成Markdown报告
        content = f"""# 周分析报告: {week_start} ~ {week_end}

## 📊 数据概览

- **分析周期**: {week_start} ~ {week_end}
- **总标题数**: {stats['total_titles']} 个
- **日均产量**: {stats['total_titles'] / 7:.1f} 个

## 🏆 主题分布

| 排名 | 主题 | 数量 | 占比 |
|------|------|------|------|
"""
        
        total = sum(stats['category_counts'].values())
        for i, (cat, count) in enumerate(stats['category_counts'].most_common(), 1):
            pct = count / total * 100 if total > 0 else 0
            content += f"| {i} | {cat} | {count} | {pct:.1f}% |\n"
        
        content += f"""

## 📅 每日产量

| 日期 | 标题数 |
|------|--------|
"""
        
        for day, count in sorted(stats['daily_breakdown'].items()):
            content += f"| {day} | {count} |\n"
        
        content += f"""

## 💡 洞察与建议

"""
        for insight in insights:
            content += f"- {insight}\n"
        
        content += f"""

## 🎯 下周策略建议

基于本周数据分析，建议下周重点关注：

1. **内容平衡**: 确保各主题类别均匀分布
2. **城市对比**: 增加Navarra vs Madrid对比内容
3. **政策追踪**: 关注移民/留学政策变化

---

*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        # 保存报告
        report_file = self.weekly_report_path / f"Weekly_Report_{week_start}_to_{week_end}.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✓ 报告已保存: {report_file}")
        
        # 更新主索引
        self._update_index()
        
        return report_file
    
    def _update_index(self):
        """更新周分析报告索引"""
        index_file = ANALYSIS_PATH / "📊 Weekly Reports Index.md"
        
        reports = sorted(self.weekly_report_path.glob("Weekly_Report_*.md"), reverse=True)
        
        content = "# 📊 周分析报告索引\n\n"
        content += "> 自动生成的每周内容分析报告\n\n"
        
        for report in reports[:10]:  # 最近10份
            date_range = report.stem.replace("Weekly_Report_", "").replace("_to_", " ~ ")
            content += f"- [[{report.stem}|{date_range}]]\n"
        
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(content)

if __name__ == '__main__':
    analyzer = WeeklyAnalyzer()
    analyzer.generate_weekly_report()
