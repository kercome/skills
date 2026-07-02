# _cachedContent 字段说明

## 概述

语雀文档正文存储在 `appData.doc._cachedContent` 对象中。该对象包含多个字段，不同文档的正文随机出现在不同字段里，必须逐个尝试。

## 字段优先级（按提取顺序）

| 优先级 | 字段名 | 格式 | 说明 |
|--------|--------|------|------|
| 1 | `body` | HTML | 正文 HTML，约 30% 文档有此字段 |
| 2 | `_cache_decrypted_body` | HTML | body 的解密版本，内容相同 |
| 3 | `body_draft` | HTML | 草稿版 HTML |
| 4 | `_cache_decrypted_body_draft` | HTML | 草稿解密版 |
| 5 | `body_asl` | ASL/Lake | **语雀自有格式**，约 60% 文档正文在此 |
| 6 | `_cache_decrypted_body_asl` | ASL/Lake | body_asl 的解密版本 |
| 7 | `body_draft_asl` | ASL/Lake | 草稿 ASL |
| 8 | `_cache_decrypted_body_draft_asl` | ASL/Lake | 草稿解密 ASL |

## 字段格式说明

### HTML 格式
```html
<!doctype html>
<div class="lake-content" typography="classic">
  <p class="ne-p"><span class="ne-text">正文内容</span></p>
  <pre><code>代码块</code></pre>
</div>
```
- 可直接用 `html2text` 转为 Markdown
- 需先移除 `<!doctype html>` 和 `<meta>` 标签

### ASL/Lake 格式
```html
<!doctype lake>
<meta name="doc-version" content="1" />
<p data-lake-id="xxx">正文内容</p>
```
- 语雀自有的 Lake 编辑器格式
- `html2text` 也能处理，但需先移除 `<!doctype lake>` 和 `<meta>` 标签
- 包含 `data-lake-id` 等属性，转换后无影响

## 空值判断

- 字段值为空字符串 `""` → 跳过
- 字段值长度 < 50 → 跳过（可能是无意义的占位）
- 字段值 > 50 字符 → 使用该字段

## 31KB 空壳页面

约 6-8% 的文档访问 `/markdown` 页面时返回固定 31KB 大小的空壳页面：
- `appData` 中无 `doc` 字段，或 `doc` 为空对象
- `_cachedContent` 不存在或所有字段为空
- `appData.status` 可能为 403

原因：语雀服务端缓存未命中，或文档设置了访问限制。

处理方式：写入占位符文件，标注 "⚠️ 需登录后访问"。
