---
name: yuque-scraper
description: 拉用语雀公开知识库全部文档到本地 Markdown。适用于用户要求"拉取语雀知识库""下载语雀文档""备份语雀知识库""导出语雀内容"等场景。支持任意公开语雀知识库 URL，自动提取目录结构、批量下载正文、转换为 Markdown 并按原文档层级保存。
agent_created: true
---

# Yuque Scraper - 语雀知识库批量拉取

## Overview

拉取语雀（yuque.com）公开知识库的全部文档到本地，按原文档目录层级保存为 Markdown 文件。核心脚本 `scripts/yuque_scraper.py` 一键完成 TOC 提取、正文下载、HTML→Markdown 转换、目录树构建、索引生成。

## When to Use

触发条件（满足任一即可）：
- 用户说"拉取语雀知识库""下载语雀文档""备份语雀知识库"
- 用户提供语雀 URL 并要求保存内容到本地
- 用户要求"把语雀上的文档导出""把语雀知识库爬下来"

不适用场景：
- 私有知识库（需登录 token，脚本不支持）
- 非语雀平台的内容拉取
- 只需查看单篇文档（直接 WebFetch 即可）

## Quick Start

### 一键拉取

```bash
# 安装依赖
pip install html2text

# 执行拉取
python scripts/yuque_scraper.py --url https://www.yuque.com/{user}/{book} --output {输出目录}
```

### 参数说明

| 参数 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `--url` | 是 | — | 语雀知识库 URL |
| `--output` | 否 | `./yuque-{知识库名}` | 输出目录 |
| `--delay` | 否 | `2.0` | 每次请求间隔秒数（反爬限速） |

### 执行流程

脚本自动完成 4 个阶段：

1. **TOC 提取**：访问知识库主页，从 `window.appData` 中解析目录结构
2. **正文下载**：逐篇访问 `/{slug}/markdown` 页面，从 `_cachedContent` 提取正文
3. **索引生成**：生成 `_索引.md` 文件，列出所有文档状态和源链接
4. **输出报告**：打印成功/失败/需登录统计

## How It Works

### 数据提取原理

语雀是 SPA 前端渲染，文档数据嵌在页面 HTML 的 `<script>` 标签中：

```javascript
window.appData = JSON.parse(decodeURIComponent("URL编码的JSON"));
```

提取三步：
1. 正则匹配 `decodeURIComponent("...")` 中的编码字符串
2. URL decode 解码
3. `json.loads()` 解析为 Python dict

### 正文字段 fallback

不同文档的正文随机出现在 `_cachedContent` 的不同字段中。脚本按优先级逐个尝试 8 个字段，详见 `references/cachedContent_fields.md`。

### 为什么用 curl 而非 urllib

- Python `urllib` 与语雀 TLS 握手不兼容，偶发 `SSLEOFError`
- `subprocess.run(capture_output=True)` 对 >500KB 响应有缓冲区截断
- `curl -o file` 直接写磁盘，最稳定

## Known Limitations

| 限制 | 原因 | 处理方式 |
|------|------|----------|
| 约 6-8% 文档无法获取 | 语雀服务端缓存未命中，返回 31KB 空壳 | 写入 "⚠️ 需登录" 占位符 + 源链接 |
| 图片保留 CDN 链接 | 不下载图片到本地 | Markdown 中保留原始 `![](https://cdn.nlark.com/...)` |
| 不支持私有知识库 | API v2 需登录 token | 脚本检测 403 并提示用户 |
| 语雀改版可能导致失效 | 依赖 `appData` 正则匹配 | 若失效需更新正则模式 |

## Resources

### scripts/
- `yuque_scraper.py` — 一体化拉取脚本，支持 `--url` / `--output` / `--delay` 参数

### references/
- `cachedContent_fields.md` — `_cachedContent` 8 个字段的优先级、格式说明、空值判断规则
