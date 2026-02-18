# AI Daily Brief

每日自动生成 AI 资讯与 GitHub 工具推荐，并推送到 Telegram / 企业微信。

## 功能（MVP）
- 聚合 AI 新闻（RSS）
- 聚合 GitHub AI 相关项目（关键词）
- 生成 Markdown 日报
- 推送到 Telegram / 企业微信
- GitHub Actions 每天 09:00 (Asia/Shanghai) 自动运行
- 支持手动触发（workflow_dispatch）

## 快速开始（本地）
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m app.main run-now
```

生成文件：`data/output/daily-brief-YYYY-MM-DD.md`

## 环境变量
见 `.env.example`。

常用配置：
- `RSS_FEEDS`：逗号分隔 RSS 列表
- `RSS_INCLUDE_KEYWORDS`：RSS 标题包含关键字（逗号分隔）
- `RSS_EXCLUDE_KEYWORDS`：RSS 标题排除关键字（逗号分隔）
- `RSS_REQUEST_TIMEOUT`：RSS 请求超时秒数
- `RSS_PER_FEED_LIMIT`：单个 RSS 抓取条数上限
- `GITHUB_SEARCH_QUERY`：GitHub 搜索关键词（示例：`llm OR ai`）
- `GITHUB_SEARCH_QUALIFIERS`：GitHub 限定条件（如 `language:Python topic:llm`）
- `GITHUB_SEARCH_DAYS`：抓取近 N 天创建的项目
- `GITHUB_SEARCH_PER_PAGE`：每次抓取条数（1-50）
- `GITHUB_MIN_STARS`：最小星标数过滤
- `GITHUB_EXCLUDE_KEYWORDS`：排除关键词（逗号分隔）
- `GITHUB_TOKEN`：可选，提高速率限制

## GitHub Actions 定时
工作流：`.github/workflows/daily.yml`
- 定时：每天 09:00（上海）
- 手动：Actions 页面点击 `Run workflow`

## Secrets 配置
在仓库 `Settings -> Secrets and variables -> Actions` 添加：
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`
- `WECOM_WEBHOOK_URL`
- 可选：`GITHUB_TOKEN_OVERRIDE`（默认可不填，使用内置 `GITHUB_TOKEN`）

## 目录结构（当前）
- `app/` 运行入口（`python -m app.main run-now`）
- `data/output/` 日报输出目录

## 下一步（计划）
- 引入更丰富的信息源与去重/排序策略
- 增强推送的重试与可观测性
