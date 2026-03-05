# 🇪🇸 Spain Identity Content System

**西班牙身份内容系统** - 长期自动化内容引擎

> 使命：聚焦西班牙移民、留学和Navarra小城市定位，将每日新闻转化为结构化流量资产，建立西班牙身份知识数据库。

## 🎯 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                    DAILY CYCLE (每日循环)                     │
├─────────────────────────────────────────────────────────────┤
│  Step 1: RSS抓取    →  西班牙政策/教育/移民新闻源             │
│  Step 2: 智能过滤   →  关键词匹配 + 分类                      │
│  Step 3: 标题生成   →  4种风格模型，20个标题/天              │
│  Step 4: Obsidian   →  知识库存储 + 结构化                   │
│  Step 5: RSS输出    →  spain-hot.xml                        │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                  WEEKLY OPTIMIZATION (每周优化)               │
├─────────────────────────────────────────────────────────────┤
│  • 分析生成标题的主题分布                                     │
│  • 识别高频主题 (Policy Change, City Comparison等)          │
│  • 生成洞察报告，调整内容策略                                 │
└─────────────────────────────────────────────────────────────┘
```

## 📁 Obsidian知识库结构

```
obsidian_vault/
├── 🏠 Home.md                    # 知识库首页
├── 01_Daily_News/                # 每日新闻存档
│   └── 2026-03-05 News.md
├── 02_Viral_Titles/              # 爆款标题库
│   └── 2026-03-05 Viral Titles.md
├── 03_Policy_Monitoring/         # 政策监控
├── 04_Identity_Pathways/         # 身份路径图谱
│   └── Identity_Pathways_Overview.md
├── 05_City_Database/             # 城市数据库
│   ├── City_Database_Navarra.md
│   └── City_Database_Madrid.md
├── 06_Cost_Database/             # 成本数据库
│   └── Cost_Database_2026.md
├── 07_Weekly_Analysis/           # 每周分析
│   ├── 📊 Weekly Reports Index.md
│   └── weekly_reports/
├── 08_Published_Articles/        # 已发布文章
└── 09_Client_Questions/          # 客户常见问题
```

## 🚀 快速开始

### 本地运行

```bash
# 克隆项目
git clone https://github.com/yourusername/spain-identity-system.git
cd spain-identity-system

# 安装依赖
pip install -r requirements.txt

# 运行每日内容生成
python scripts/content_engine.py

# 生成周分析报告 (周日运行)
python scripts/weekly_analyzer.py
```

### GitHub自动部署

1. **Fork/创建仓库** 并推送到GitHub
2. **启用GitHub Pages**: Settings → Pages → GitHub Actions
3. **自动运行**: 每天8:00 CET自动生成内容并部署

访问地址:
- 主页面: `https://yourusername.github.io/repo-name/`
- RSS订阅: `https://yourusername.github.io/repo-name/spain-hot.xml`

## 📊 内容生成规则

### 标题风格模型

| 风格 | 示例 | 用途 |
|------|------|------|
| **policy_alert** | 注意！西班牙居留政策变了 | 政策变化 |
| **information_gap** | 原来居留还能这样！ | 信息差 |
| **city_comparison** | Navarra vs马德里差多少？ | 城市对比 |
| **time_window_urgency** | 2026新规：抓紧了 | 时间窗口 |

### 内容分类

- **Policy Change** - 政策变化
- **Student Visa Path** - 学生签证路径
- **Work Residency** - 工作居留
- **Permanent Residency** - 长期居留
- **City Comparison** - 城市对比
- **Cost of Living** - 生活成本

## 🏛️ 核心差异化：Navarra定位

### 为什么选择Navarra？

| 维度 | Madrid | Navarra | 优势 |
|------|--------|---------|------|
| 租房成本 | €1000-1600 | €600-900 | **-40%** |
| 移民审批 | 3-6个月 | 1-3个月 | **更快** |
| 排队时间 | 长 | 短 | **更轻松** |
| 生活环境 | 繁忙 | 安静 | **宜居** |

### 适用人群
- 非盈利居留申请者
- 数字游民
- 留学生
- 退休移民

## 📈 长期发展路径

```
Phase 1: 流量积累 (当前)
    └── 每日爆款标题 → RSS订阅 → 社媒传播

Phase 2: 知识沉淀
    └── Obsidian知识图谱 → 身份路径指南 → 城市数据库

Phase 3: 变现转化
    └── 咨询服务 → 路径规划 → 社群运营
```

## 🛠️ 技术栈

- **Python 3.11+** - 核心脚本
- **feedparser** - RSS解析
- **GitHub Actions** - 自动化部署
- **Obsidian** - 知识管理
- **GitHub Pages** - 静态托管

## 📋 配置说明

编辑 `config/system_config.json`:

```json
{
  "daily_cycle": {
    "max_titles_per_day": 20,
    "titles_per_article": 3,
    "max_length": 28,
    "min_question_ratio": 0.4
  },
  "rss_sources": [
    {"name": "El País", "url": "...", "category": "general"}
  ],
  "filter_keywords": {
    "high_priority": ["visa", "residencia", ...],
    "medium_priority": ["student", "estudiante", ...]
  }
}
```

## 📚 模板文件

位于 `obsidian_templates/`:

- `City_Database_Navarra.md` - Navarra城市数据模板
- `City_Database_Madrid.md` - Madrid城市数据模板
- `Identity_Pathways_Overview.md` - 身份路径图谱模板
- `Cost_Database_2026.md` - 成本数据库模板

## 🤝 贡献

欢迎提交Issue和PR来完善:
- 新的RSS源
- 更多城市数据
- 标题模板优化
- 翻译改进

## 📄 License

MIT License

---

> Made with ❤️ for Spain identity seekers
