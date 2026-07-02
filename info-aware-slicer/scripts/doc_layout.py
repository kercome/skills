#!/usr/bin/env python3
"""
doc_layout.py — 切片图片 → 排版文档生成器

读取 document_chain.json 的状态信息，将切片图片的 OCR 文本智能排版：
  - CONTINUOUS 帧 → 合并文本，去重滚动重叠
  - NEW_PAGE 帧   → 新章节
  - MISSING_GAP    → 警告标注

输出排版精美的 Markdown 文档（可直接在 Typora/Obsidian 中阅读）。

用法:
  python doc_layout.py -i "H:/AAA/切片测试文档" -o "H:/AAA/排版文档.md" --gpu
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

# --- 依赖检查 ---
def _check_deps() -> None:
    missing = []
    for pkg, mod in [("opencv-python", "cv2"), ("easyocr", "easyocr"), ("numpy", "numpy")]:
        try:
            __import__(mod)
        except ImportError:
            missing.append(pkg)
    if missing:
        print(f"缺少依赖，请安装: pip install {' '.join(missing)}")
        sys.exit(1)

_check_deps()

import cv2
import numpy as np
import easyocr

logger = logging.getLogger("doc_layout")


def _setup_logger(output_base: str) -> None:
    log_dir = os.path.join(os.path.dirname(output_base) or ".", "_logs")
    os.makedirs(log_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = os.path.join(log_dir, f"layout_{ts}.log")

    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler(log_path, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter("%(asctime)s | %(levelname)-7s | %(message)s"))
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(fh)
    logger.addHandler(ch)
    logger.info(f"日志: {log_path}")


# ============================================================
#  工具函数
# ============================================================

def _imread_cjk(file_path: str, flags: int = cv2.IMREAD_COLOR) -> Optional[np.ndarray]:
    """兼容 CJK 路径的图片读取."""
    try:
        with open(os.path.normpath(file_path), "rb") as f:
            buf = np.frombuffer(f.read(), np.uint8)
        return cv2.imdecode(buf, flags)
    except Exception:
        return None


def _extract_number(filename: str) -> int:
    m = re.search(r"\d+", os.path.basename(filename))
    return int(m.group()) if m else 0


def _lines_to_set(text: str) -> set[str]:
    """文本按行拆分为字符集合（去空格），用于快速去重比对."""
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    return {re.sub(r"\s+", "", l) for l in lines}


def _merge_texts(prev: str, curr: str) -> tuple[str, int]:
    """合并两个连续滚动帧的文本，自动定位重叠点并去重。

    算法：从 prev_text 尾部逐行向前查找，在 curr_text 头部匹配，
          找到重叠行后拼接去重部分。

    Returns:
        (合并后的文本, 找到的重叠行数)
    """
    prev_lines = [l.strip() for l in prev.split("\n") if l.strip()]
    curr_lines = [l.strip() for l in curr.split("\n") if l.strip()]

    if not prev_lines:
        return curr, 0
    if not curr_lines:
        return prev, 0

    # 从 prev 尾部取最多 8 行去 curr 头部匹配
    search_window = min(8, len(prev_lines), len(curr_lines))

    best_overlap = 0
    for n in range(search_window, 0, -1):
        tail = prev_lines[-n:]
        head = curr_lines[:n]
        # 宽松匹配：去除空格后比较
        tail_clean = [re.sub(r"\s+", "", l) for l in tail]
        head_clean = [re.sub(r"\s+", "", l) for l in head]
        if tail_clean == head_clean:
            best_overlap = n
            break

    if best_overlap > 0:
        merged = "\n".join(prev_lines + curr_lines[best_overlap:])
    else:
        merged = prev + "\n" + curr

    return merged, best_overlap


# ============================================================
#  主逻辑
# ============================================================

def layout(
    input_dir: str,
    output_path: str,
    use_gpu: bool,
    ocr_lang: list[str],
    chain_path: Optional[str],
) -> None:
    input_dir = os.path.normpath(input_dir)
    output_path = os.path.normpath(output_path)
    _setup_logger(output_path)

    # --- 1. 读取 document_chain.json ---
    if chain_path is None:
        chain_path = os.path.join(input_dir, "document_chain.json")

    chain: list[dict] = []
    chain_by_filename: dict[str, dict] = {}
    if os.path.exists(chain_path):
        with open(chain_path, "r", encoding="utf-8") as f:
            chain = json.load(f)
        for item in chain:
            chain_by_filename[item["filename"]] = item
        logger.info(f"已加载 document_chain.json: {len(chain)} 条记录")
    else:
        logger.warning("未找到 document_chain.json，将按纯图片顺序排版")

    # --- 2. 收集图片 ---
    exts = ["*.jpg", "*.jpeg", "*.png", "*.bmp", "*.tiff", "*.webp"]
    images: list[str] = []
    for ext in exts:
        for p in Path(input_dir).glob(ext):
            images.append(str(p))
        for p in Path(input_dir).glob(ext.upper()):
            images.append(str(p))
    images = sorted(set(images), key=_extract_number)

    if not images:
        logger.error(f"在 {input_dir} 中未找到图片！")
        return

    total = len(images)
    logger.info(f"图片总数: {total} 张")

    # --- 3. 按 chain 状态分组 ---
    # 结构: [(group_status, [image_paths])]
    groups: list[tuple[str, list[str]]] = []
    current_group: list[str] = []

    def _flush_group() -> None:
        nonlocal current_group
        if not current_group:
            return
        # 取组内第一帧的状态（CONTINUOUS 组的所有帧状态一致）
        fn = os.path.basename(current_group[0])
        info = chain_by_filename.get(fn, {})
        status = info.get("status", "NEW_PAGE")
        groups.append((status, current_group))
        current_group = []

    for img in images:
        fn = os.path.basename(img)
        info = chain_by_filename.get(fn, {})
        status = info.get("status", "NEW_PAGE")

        if status in ("NEW_PAGE", "FIRST_FRAME", "MISSING_GAP"):
            _flush_group()
            # 单帧独立组
            groups.append((status, [img]))
        else:  # CONTINUOUS
            # 和前一张是否同一段连续滚动？
            if current_group and chain_by_filename.get(
                os.path.basename(current_group[-1]), {}
            ).get("status") == "CONTINUOUS":
                current_group.append(img)
            else:
                _flush_group()
                current_group.append(img)

    _flush_group()

    logger.info(f"排版分组: {len(groups)} 组 ({len([g for g in groups if g[0]=='CONTINUOUS'])} 组连续滚动)")

    # --- 4. OCR + 排版输出 ---
    logger.info("加载 OCR 模型...")
    t0 = time.time()
    reader = easyocr.Reader(ocr_lang, gpu=use_gpu)
    logger.info(f"OCR 就绪, {time.time() - t0:.1f}s")

    stats = {"CONTINUOUS": 0, "NEW_PAGE": 0, "FIRST_FRAME": 0, "MISSING_GAP": 0}
    section_idx = 0
    merged_overlaps = 0
    ocr_total_time = 0.0

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("# 文档排版输出\n\n")
        f.write(f"> 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"> 来源目录: `{input_dir}`\n")
        f.write(f"> 图片总数: {total} 张 | 排版分组: {len(groups)} 组\n")
        f.write(f"> chain 状态: {json.dumps(stats, ensure_ascii=False)}\n\n")
        f.write("---\n\n")

        for gi, (status, group_imgs) in enumerate(groups):
            stats[status] = stats.get(status, 0) + 1

            # 取元数据
            first_fn = os.path.basename(group_imgs[0])
            info = chain_by_filename.get(first_fn, {})
            pts_start = info.get("pts_sec", 0)
            match_conf = info.get("match_confidence", 0.0)

            if len(group_imgs) > 1:
                last_fn = os.path.basename(group_imgs[-1])
                last_info = chain_by_filename.get(last_fn, {})
                pts_end = last_info.get("pts_sec", pts_start)
            else:
                pts_end = pts_start

            # --- 写章节标题 ---
            section_idx += 1

            if status == "FIRST_FRAME":
                f.write(f"## 📄 章节 {section_idx} — 视频起始\n\n")
            elif status == "CONTINUOUS":
                n = len(group_imgs)
                f.write(f"## 📜 章节 {section_idx} — 连续滚动 ({n} 帧, {pts_start:.1f}s ~ {pts_end:.1f}s)\n\n")
            elif status == "NEW_PAGE":
                f.write(f"## 📖 章节 {section_idx} — 新页面 ({pts_start:.1f}s)\n\n")
            elif status == "MISSING_GAP":
                f.write(f"## ⚠️ 缺失警告 — {pts_start:.1f}s\n\n")
                f.write(f"> **此处检测到物理断层**，匹配度 {match_conf:.3f}\n")
                f.write(f"> 建议回看原视频 {pts_start:.0f}s 附近补充切片\n\n")
                f.write("---\n\n")

            # --- OCR 并合并 ---
            group_texts: list[str] = []
            for j, img_path in enumerate(group_imgs):
                fn = os.path.basename(img_path)
                logger.info(f"  [{gi+1}/{len(groups)}] OCR: {fn}")
                t_ocr = time.time()
                try:
                    img = _imread_cjk(img_path)
                    if img is not None:
                        results = reader.readtext(img)
                        results.sort(key=lambda r: r[0][0][1])
                        text = " ".join([res[1] for res in results])
                    else:
                        text = ""
                except Exception as e:
                    logger.warning(f"    OCR 失败 {fn}: {e}")
                    text = ""
                ocr_total_time += time.time() - t_ocr
                group_texts.append(text)

            # 合并连续帧文本
            if status == "CONTINUOUS" and len(group_texts) > 1:
                merged = group_texts[0]
                for i in range(1, len(group_texts)):
                    merged, overlap = _merge_texts(merged, group_texts[i])
                    if overlap > 0:
                        merged_overlaps += 1
                final_text = merged
            else:
                final_text = group_texts[0] if group_texts else ""

            # --- 嵌入图片 ---
            if len(group_imgs) == 1:
                f.write(f"![{first_fn}]({group_imgs[0]})\n\n")
            else:
                # 多帧组：首帧 + 尾帧各一张缩略图
                f.write(f"![{first_fn}]({group_imgs[0]})\n\n")
                f.write(f"> 📎 本组共 {len(group_imgs)} 帧，仅展示首尾帧。")
                f.write(f" 末尾帧: `{os.path.basename(group_imgs[-1])}`\n\n")
                f.write(f"![{last_fn}]({group_imgs[-1]})\n\n")

            # --- 写入合并后的文本 ---
            f.write(f"**识别文本**：\n\n```text\n{final_text}\n```\n\n")
            f.write("---\n\n")

    # --- 统计 ---
    elapsed = time.time() - t0
    logger.info("\n" + "=" * 60)
    logger.info("  排版完成 — 统计")
    logger.info("=" * 60)
    logger.info(f"总图片:         {total} 张")
    logger.info(f"排版分组:       {len(groups)} 组")
    for s, c in sorted(stats.items()):
        logger.info(f"  {s:15s} {c} 组")
    logger.info(f"文本重叠去重:   {merged_overlaps} 处")
    logger.info(f"OCR 总耗时:     {ocr_total_time:.1f}s")
    logger.info(f"总耗时:         {elapsed:.1f}s")
    logger.info(f"输出:           {output_path}")
    logger.info("=" * 60)


# ============================================================
#  CLI
# ============================================================

def main() -> None:
    parser = argparse.ArgumentParser(
        description="切片图片 → 排版文档生成器（利用 document_chain.json 状态智能排版）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python doc_layout.py -i "H:\\\\AAA\\\\切片测试文档" -o "H:\\\\AAA\\\\排版文档.md" --gpu
  python doc_layout.py -i ./frames -o ./layout.md --gpu --chain ./frames/document_chain.json
        """,
    )
    parser.add_argument("-i", "--input", required=True, help="切片图片目录")
    parser.add_argument("-o", "--output", required=True, help="输出 Markdown 文件路径")
    parser.add_argument("--chain", default=None, help="document_chain.json 路径（默认在 input 目录下查找）")
    parser.add_argument("--gpu", action="store_true", help="启用 GPU 加速 OCR")
    parser.add_argument("--lang", nargs="+", default=["ch_sim", "en"], help="EasyOCR 语言，默认 ch_sim en")
    args = parser.parse_args()

    if not os.path.isdir(args.input):
        print(f"错误: 输入目录不存在: {args.input}")
        sys.exit(1)

    layout(
        input_dir=args.input,
        output_path=args.output,
        use_gpu=args.gpu,
        ocr_lang=args.lang,
        chain_path=args.chain,
    )


if __name__ == "__main__":
    main()
