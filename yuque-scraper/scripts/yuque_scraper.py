#!/usr/bin/env python3
"""
Yuque Knowledge Base Scraper
拉取语雀公开知识库全部文档到本地，按目录层级保存为 Markdown。

用法:
    python yuque_scraper.py --url https://www.yuque.com/{user}/{book} [--output ./output]

依赖:
    pip install html2text
    系统需有 curl 命令
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.parse
import tempfile

try:
    import html2text
except ImportError:
    print("ERROR: html2text not installed. Run: pip install html2text")
    sys.exit(1)


# ============================================================
# HTML2Text 配置
# ============================================================
h2t = html2text.HTML2Text()
h2t.body_width = 0
h2t.ignore_images = False
h2t.ignore_links = False
h2t.protect_links = True
h2t.unicode_snob = True


# ============================================================
# 工具函数
# ============================================================
def sanitize_filename(name):
    """清理文件名中的非法字符"""
    name = re.sub(r'[<>:"/\\|?*]', '_', name)
    name = re.sub(r'\s+', ' ', name).strip().rstrip('.')
    return name[:100] if len(name) > 100 else name


def curl_fetch(url, output_file, timeout=60):
    """
    使用 curl 下载 URL 内容到文件。
    为什么不用 urllib: 语雀 TLS 握手与 Python SSL 不兼容，会偶发 SSLEOFError。
    为什么不用 subprocess capture_output: 对 >500KB 响应有缓冲区截断问题。
    curl -o file 直接写磁盘，最稳定。
    """
    result = subprocess.run(
        ['curl', '-s', '--max-time', str(timeout), '-o', output_file,
         '-H', 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
               'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
         '-H', 'Accept: text/html,*/*',
         '-H', 'Accept-Language: zh-CN,zh;q=0.9',
         '-H', f'Referer: https://www.yuque.com/',
         url],
        timeout=timeout + 10
    )
    return os.path.getsize(output_file) if os.path.exists(output_file) else 0


def extract_appdata(html):
    """
    从语雀页面 HTML 中提取 appData JSON 对象。
    语雀是 SPA，数据嵌在 <script> 标签中：
        window.appData = JSON.parse(decodeURIComponent("...URL-encoded JSON..."));
    """
    match = re.search(
        r'window\.appData\s*=\s*JSON\.parse\(decodeURIComponent\("(.+?)"\)\)',
        html, re.DOTALL
    )
    if not match:
        return None
    decoded = urllib.parse.unquote(match.group(1))
    try:
        return json.loads(decoded)
    except json.JSONDecodeError:
        return None


def extract_doc_content(app_data):
    """
    从 appData.doc._cachedContent 中提取文档正文。
    关键：不同文档的正文随机出现在不同字段，必须逐个尝试。
    详见 references/cachedContent_fields.md
    """
    if app_data.get('status') == 403:
        return 'FORBIDDEN'

    doc = app_data.get('doc', {})
    if not doc:
        return None

    cached = doc.get('_cachedContent', {})

    # 多字段 fallback（按优先级排序）
    body_fields = [
        'body', '_cache_decrypted_body',               # HTML 格式
        'body_draft', '_cache_decrypted_body_draft',   # 草稿 HTML
        'body_asl', '_cache_decrypted_body_asl',       # ASL/Lake 格式（多数文档正文在这）
        'body_draft_asl', '_cache_decrypted_body_draft_asl',
    ]

    body_html = ''
    for field in body_fields:
        val = cached.get(field, '')
        if val and len(val) > 50:
            body_html = val
            break

    # 也检查 doc 级别的字段
    if not body_html:
        for field in body_fields:
            val = doc.get(field, '')
            if val and len(val) > 50:
                body_html = val
                break

    if not body_html or len(body_html) < 50:
        return None

    # 清理 HTML → Markdown
    body_html = re.sub(r'<!doctype[^>]*>', '', body_html, flags=re.IGNORECASE)
    body_html = re.sub(r'<meta[^>]*>', '', body_html)
    md = h2t.handle(body_html)
    md = re.sub(r'\n{4,}', '\n\n\n', md)
    return md.strip()


# ============================================================
# TOC 提取
# ============================================================
def fetch_toc(yuque_url):
    """
    从语雀知识库主页提取目录结构 (TOC)。
    返回: (book_name, namespace, toc_list)
    """
    print(f"[1/4] 提取 TOC: {yuque_url}")

    tmp = tempfile.mktemp(suffix='.html')
    try:
        size = curl_fetch(yuque_url, tmp)
        if size < 1000:
            print(f"  ERROR: 主页下载失败 ({size} bytes)")
            return None, None, None

        with open(tmp, 'r', encoding='utf-8', errors='replace') as f:
            html = f.read()

        app_data = extract_appdata(html)
        if not app_data:
            print("  ERROR: 无法从页面提取 appData")
            return None, None, None

        book = app_data.get('book', {})
        book_name = book.get('name', 'unknown')
        namespace = book.get('namespace', '')
        toc = book.get('toc', [])

        doc_count = sum(1 for t in toc if t['type'] == 'DOC')
        print(f"  OK: 知识库「{book_name}」, {doc_count} 篇文档, {len(toc)} 条 TOC 记录")
        return book_name, namespace, toc
    finally:
        try:
            os.unlink(tmp)
        except OSError:
            pass


# ============================================================
# 目录树构建
# ============================================================
def build_path(item, toc_by_uuid, cache):
    """递归构建文件路径，基于 parent_uuid 链"""
    if item['uuid'] in cache:
        return cache[item['uuid']]
    puuid = item.get('parent_uuid', '')
    if puuid and puuid in toc_by_uuid:
        parent_path = build_path(toc_by_uuid[puuid], toc_by_uuid, cache)
        path = os.path.join(parent_path, sanitize_filename(item['title']))
    else:
        path = sanitize_filename(item['title'])
    cache[item['uuid']] = path
    return path


# ============================================================
# 文档下载
# ============================================================
def download_docs(namespace, toc, output_dir, delay=2):
    """
    逐篇下载文档正文。
    策略: 访问 /{namespace}/{slug}/markdown 页面，从 _cachedContent 提取正文。
    """
    toc_by_uuid = {item['uuid']: item for item in toc}
    paths_cache = {}

    doc_items = [item for item in toc if item['type'] == 'DOC']
    total = len(doc_items)

    print(f"\n[2/4] 下载 {total} 篇文档正文...")

    results = {'success': 0, 'empty': 0, 'forbidden': 0, 'error': 0}
    details = []

    for i, item in enumerate(doc_items):
        title = item['title']
        slug = item['url']
        source_url = f'https://www.yuque.com/{namespace}/{slug}'
        md_url = f'{source_url}/markdown'

        # 构建输出路径
        rel_path = build_path(item, toc_by_uuid, paths_cache)
        filepath = os.path.join(output_dir, rel_path)
        # rel_path 末尾是文件名（文档标题），需加 .md
        filepath = filepath + '.md'

        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        # 跳过已下载的（有实际内容的）
        if os.path.exists(filepath) and os.path.getsize(filepath) > 200:
            with open(filepath, 'r', encoding='utf-8') as f:
                existing = f.read()
            if '需登录' not in existing and '无法获取' not in existing:
                results['success'] += 1
                details.append(f"[{i+1}/{total}] SKIP: {title}")
                continue

        # 下载 markdown 页面
        tmp = tempfile.mktemp(suffix='.html')
        try:
            size = curl_fetch(md_url, tmp)

            content = None
            status = 'empty'

            if size > 30000:  # > 30KB 说明不是空壳
                with open(tmp, 'r', encoding='utf-8', errors='replace') as f:
                    html = f.read()
                app_data = extract_appdata(html)
                if app_data:
                    content = extract_doc_content(app_data)
                    if content == 'FORBIDDEN':
                        status = 'forbidden'
                        content = None

            # 写入文件
            header = f"# {title}\n\n> 来源: {source_url}\n\n"

            if content and len(content) > 20:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(header + content)
                results['success'] += 1
                details.append(f"[{i+1}/{total}] OK ({len(content)} chars): {title}")
            elif status == 'forbidden':
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(header + "⚠️ 该文档需登录后访问，请手动打开链接查看。\n")
                results['forbidden'] += 1
                details.append(f"[{i+1}/{total}] FORBIDDEN: {title}")
            else:
                # 尝试访问普通页面作为 fallback
                tmp2 = tempfile.mktemp(suffix='.html')
                try:
                    curl_fetch(source_url, tmp2)
                    with open(tmp2, 'r', encoding='utf-8', errors='replace') as f:
                        html2 = f.read()
                    app_data2 = extract_appdata(html2)
                    if app_data2:
                        content2 = extract_doc_content(app_data2)
                        if content2 and len(content2) > 20 and content2 != 'FORBIDDEN':
                            with open(filepath, 'w', encoding='utf-8') as f:
                                f.write(header + content2)
                            results['success'] += 1
                            details.append(f"[{i+1}/{total}] OK_via_regular ({len(content2)} chars): {title}")
                            continue

                    if app_data2 and extract_doc_content(app_data2) == 'FORBIDDEN':
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write(header + "⚠️ 该文档需登录后访问，请手动打开链接查看。\n")
                        results['forbidden'] += 1
                        details.append(f"[{i+1}/{total}] FORBIDDEN: {title}")
                        continue
                finally:
                    try:
                        os.unlink(tmp2)
                    except OSError:
                        pass

                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(header + "⚠️ 该文档无法通过公开 API 获取（可能需登录）。请手动访问原链接查看。\n")
                results['empty'] += 1
                details.append(f"[{i+1}/{total}] EMPTY: {title}")

        except Exception as e:
            header = f"# {title}\n\n> 来源: {source_url}\n\n"
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(header + f"⚠️ 下载失败: {str(e)[:200]}\n")
            results['error'] += 1
            details.append(f"[{i+1}/{total}] ERROR: {title} - {str(e)[:80]}")
        finally:
            try:
                os.unlink(tmp)
            except OSError:
                pass

        # 进度输出（每 10 篇）
        if (i + 1) % 10 == 0 or i == total - 1:
            print(f"  进度: {i+1}/{total} "
                  f"(成功:{results['success']} 空:{results['empty']} "
                  f"需登录:{results['forbidden']} 错误:{results['error']})")

        # 反爬限速
        time.sleep(delay)

    return results, details


# ============================================================
# 索引生成
# ============================================================
def generate_index(book_name, namespace, toc, output_dir, results):
    """生成 _索引.md 文件"""
    print(f"\n[3/4] 生成索引文件...")

    toc_by_uuid = {item['uuid']: item for item in toc}
    paths_cache = {}

    lines = []
    lines.append(f"# {book_name} - 本地索引")
    lines.append("")
    lines.append(f"> 来源: https://www.yuque.com/{namespace}")
    lines.append(f"> 拉取时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    doc_total = sum(1 for t in toc if t['type'] == 'DOC')
    lines.append(f"> 总文档数: {doc_total}")
    lines.append(f"> 成功: {results['success']} | 需登录: {results['forbidden']} | "
                 f"未获取: {results['empty']} | 错误: {results['error']}")
    lines.append("")

    has_content = 0
    no_content = 0

    for item in toc:
        level = item.get('level', 0)
        indent = "  " * level
        title = item['title']
        type_ = item['type']

        if type_ == 'TITLE':
            lines.append(f"{indent}## {title}")
        else:
            slug = item['url']
            rel_path = build_path(item, toc_by_uuid, paths_cache)
            filepath = os.path.join(output_dir, rel_path + '.md')
            source_url = f'https://www.yuque.com/{namespace}/{slug}'

            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                if '需登录' in content or '无法获取' in content or '下载失败' in content:
                    status = "⚠️ 需登录"
                    no_content += 1
                else:
                    size_kb = os.path.getsize(filepath) // 1024
                    status = f"✅ ({size_kb}KB)"
                    has_content += 1
            else:
                status = "❌ 缺失"
                no_content += 1

            lines.append(f"{indent}- {title} {status}")
            lines.append(f"{indent}  来源: {source_url}")

    lines.append("")
    lines.append("---")
    lines.append(f"已获取内容: {has_content} 篇 | 未获取: {no_content} 篇 | "
                 f"成功率: {has_content/(has_content+no_content)*100:.1f}%")

    index_path = os.path.join(output_dir, '_索引.md')
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f"  OK: {index_path}")


# ============================================================
# 主函数
# ============================================================
def main():
    parser = argparse.ArgumentParser(
        description='拉取语雀公开知识库全部文档到本地 Markdown'
    )
    parser.add_argument(
        '--url', required=True,
        help='语雀知识库 URL (如: https://www.yuque.com/user/book)'
    )
    parser.add_argument(
        '--output', default=None,
        help='输出目录 (默认: ./yuque-{book名})'
    )
    parser.add_argument(
        '--delay', type=float, default=2.0,
        help='每次请求间隔秒数 (默认: 2.0)'
    )
    args = parser.parse_args()

    # 验证 URL
    url = args.url.rstrip('/')
    if 'yuque.com' not in url:
        print("ERROR: URL 必须是语雀链接 (包含 yuque.com)")
        sys.exit(1)

    # Step 1: 提取 TOC
    book_name, namespace, toc = fetch_toc(url)
    if not toc:
        print("ERROR: 无法提取目录结构，请检查 URL 是否为公开知识库")
        sys.exit(1)

    # 确定输出目录
    output_dir = args.output or os.path.join(
        os.getcwd(), f'yuque-{sanitize_filename(book_name)}'
    )
    os.makedirs(output_dir, exist_ok=True)
    print(f"  输出目录: {output_dir}")

    # Step 2: 下载文档
    results, details = download_docs(namespace, toc, output_dir, args.delay)

    # Step 3: 生成索引
    generate_index(book_name, namespace, toc, output_dir, results)

    # Step 4: 输出报告
    print(f"\n[4/4] 完成！")
    print(f"  总计: {sum(results.values())} 篇")
    print(f"  ✅ 成功: {results['success']}")
    print(f"  ⚠️ 需登录: {results['forbidden']}")
    print(f"  ⚠️ 未获取: {results['empty']}")
    print(f"  ❌ 错误: {results['error']}")
    print(f"  📁 输出: {output_dir}")
    print(f"  📋 索引: {os.path.join(output_dir, '_索引.md')}")


if __name__ == '__main__':
    main()
