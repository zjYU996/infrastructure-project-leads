# Global Infrastructure Project Lead Collector

这个 Python 项目用于每天自动采集全球桥梁、铁路、公路、港口、码头和钢结构相关项目线索，并生成 Excel 与 Markdown 日报。

## 功能

- 从 `sources.csv` 读取网站名称、URL、国家、类别。
- 使用英文和中文关键词筛选项目线索。
- 输出字段包含：日期、国家、项目名称、项目类型、业主、承包商、摘要、来源网站、原文链接、相关性等级、跟进建议。
- 每次运行生成 `reports/project_leads_YYYY-MM-DD.xlsx` 和 `reports/project_leads_YYYY-MM-DD.md`。
- 对无法直接爬取的网站记录 URL 和错误原因，程序继续采集其他来源。
- 通过 `.github/workflows/daily-collector.yml` 每天北京时间 08:00 自动运行。

## 本地运行

```bash
python -m pip install -r requirements.txt
python main.py --sources sources.csv --output-dir reports
```

也可以指定超时和单个来源最多保留的线索数量：

```bash
python main.py --timeout 30 --max-items-per-source 100
```

## 配置 sources.csv

`sources.csv` 支持英文表头，也兼容中文表头。

```csv
website_name,url,country,category
World Bank Procurement,https://projects.worldbank.org/en/projects-operations/procurement,Global,procurement
```

兼容字段包括：

- 网站名称：`website_name`、`site`、`source`、`name`、`网站名称`、`来源网站`
- URL：`url`、`link`、`website`、`网址`、`链接`
- 国家：`country`、`region`、`market`、`国家`、`地区`
- 类别：`category`、`type`、`sector`、`类别`、`类型`

## 关键词

默认关键词包括：

- 英文：`bridge`、`steel bridge`、`viaduct`、`railway`、`highway`、`port`、`wharf`、`tender`、`procurement`、`EPC`
- 中文：`桥梁`、`钢桥`、`钢结构`、`铁路`、`公路`、`港口`、`码头`、`招标`、`采购`

可在 `src/project_leads/keywords.py` 中调整权重、类别和相关性规则。

## 新增网站爬虫

当前默认使用 `GenericCrawler` 采集公开 HTML 列表页。后续可以新增站点专用爬虫：

1. 在 `src/project_leads/crawlers/` 下新增一个爬虫类，实现 `crawl(source, run_date)`。
2. 在 `src/project_leads/crawlers/registry.py` 中注册域名匹配规则。
3. 保持返回 `CrawlResult(leads=[...], errors=[...])`，这样报表逻辑无需修改。

## GitHub Actions

工作流文件位于 `.github/workflows/daily-collector.yml`。GitHub Actions 的 cron 使用 UTC 时间，`0 0 * * *` 对应北京时间每天 08:00。

运行后会：

- 安装依赖；
- 执行采集；
- 上传当天 Excel 和 Markdown 报告为 artifact；
- 如 `reports/` 有更新，则自动提交到仓库。
