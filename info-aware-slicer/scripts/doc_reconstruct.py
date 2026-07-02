#!/usr/bin/env python3
"""
doc_reconstruct.py — 去重切片 → 连续文档重建器

双检架构：页码连续性检测 + 帧时间差/Jaccard 兜底
将去重后的切片图片重建为带缺失标注的 Markdown 文档。

核心逻辑：
  1. 优先级 1 — 页码连续性：OCR 提取页码，相邻帧页码跳跃 > 1 → 标记缺失
  2. 优先级 2 — 帧时间差 + Jaccard 兜底：无页码时，帧间时间跨度超阈值
     且文本相似度极低 → 标记缺失 + 输出原视频时间点

用法：
  python doc_reconstruct.py -i ./deduped_frames -o document.md
  python doc_reconstruct.py -i ./deduped_frames -o document.md --gpu --slice-interval 1.0
"""

import os
import re
import sys
import time
import logging
import argparse
import difflib
from datetime import datetime
from pathlib import Path

# ============================================================
#  依赖检查
# ============================================================

def check_dependencies():
    missing = []
    try:
        import cv2
    except ImportError:
        missing.append("opencv-python")
    try:
        import easyocr
    except ImportError:
        missing.append("easyocr")
    try:
        from skimage.metrics import structural_similarity
    except ImportError:
        missing.append("scikit-image")

    if missing:
        print("=" * 60)
        print("缺少以下依赖，请先安装：\n")
        print("  pip install " + " ".join(missing))
        print("=" * 60)
        sys.exit(1)


check_dependencies()

import cv2
import numpy as np
import easyocr


# ============================================================
#  日志配置
# ============================================================

def setup_logger(output_dir: str) -> logging.Logger:
    os.makedirs(output_dir, exist_ok=True)
    log_file = os.path.join(output_dir, f"reconstruct_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

    logger = logging.getLogger("doc_reconstruct")
    logger.setLevel(logging.DEBUG)

    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter("%(asctime)s | %(levelname)-7s | %(message)s"))

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(logging.Formatter("%(message)s"))

    logger.addHandler(fh)
    logger.addHandler(ch)
    logger.info(f"日志文件: {log_file}")
    return logger


# ============================================================
#  核心函数
# ============================================================

def extract_number(file_path: str) -> int:
    """提取文件名中的数字，确保按序号排序"""
    match = re.search(r'\d+', os.path.basename(file_path))
    return int(match.group()) if match else 0


def imread_cjk(file_path: str, flags=cv2.IMREAD_COLOR):
    """安全读取图片，兼容含中文等非 ASCII 字符的路径"""
    file_path = os.path.normpath(file_path)
    try:
        with open(file_path, 'rb') as f:
            data = f.read()
        img = cv2.imdecode(np.frombuffer(data, np.uint8), flags)
        return img
    except Exception:
        return None


def extract_page_number(text: str) -> int | None:
    """
    正则提取页码（支持 '第X页' / 'Page X' / 尾部独立数字）
    返回页码整数或 None
    """
    # 策略 1: 匹配 "第 X 页" 或 "Page X"
    match = re.search(r'(?:第|Page)\s*(\d+)\s*(?:页)?', text, re.IGNORECASE)
    if match:
        return int(match.group(1))

    # 策略 2: 提取最后一行独立数字
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    if lines:
        last_line = lines[-1]
        # 允许 "- 14 -" 这种格式
        cleaned = re.sub(r'[-\s]', '', last_line)
        if re.match(r'^\d+$', cleaned):
            return int(cleaned)

    return None


def calculate_jaccard(text1: str, text2: str) -> float:
    """计算字符级 Jaccard 相似度（忽略空格和换行）"""
    set1 = set(text1.replace(" ", "").replace("\n", ""))
    set2 = set(text2.replace(" ", "").replace("\n", ""))

    if not set1 or not set2:
        return 0.0

    intersection = set1.intersection(set2)
    union = set1.union(set2)
    return len(intersection) / len(union)


def format_time(seconds: float) -> str:
    """将秒数格式化为 mm:ss 方便人工回溯"""
    m, s = divmod(int(seconds), 60)
    return f"{m:02d}:{s:02d}"


def extract_text(reader, img_path: str) -> str:
    """使用 EasyOCR 提取图片中的文字（兼容 CJK 路径）"""
    img = imread_cjk(img_path, cv2.IMREAD_COLOR)
    if img is None:
        return ""
    results = reader.readtext(img)
    # 按 Y 坐标排序，保持阅读顺序
    results.sort(key=lambda r: r[0][0][1] if r[0] else 0)
    return " ".join([res[1] for res in results])


# ============================================================
#  GPU 检测
# ============================================================

def detect_gpu() -> bool:
    try:
        import torch
        return torch.cuda.is_available()
    except ImportError:
        try:
            import subprocess
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
                capture_output=True, text=True, timeout=5
            )
            return result.returncode == 0 and bool(result.stdout.strip())
        except Exception:
            return False
    except Exception:
        return False


# ============================================================
#  主逻辑
# ============================================================

def reconstruct(
    input_dir: str,
    output_md: str,
    slice_interval: float,
    time_gap_threshold: float,
    jaccard_threshold: float,
    use_gpu: bool,
    ocr_lang: list,
    embed_images: bool,
    logger: logging.Logger,
):
    """双检架构主逻辑"""

    input_dir = os.path.normpath(input_dir)
    output_md = os.path.normpath(output_md)
    output_dir = os.path.dirname(output_md) or "."
    os.makedirs(output_dir, exist_ok=True)

    start_time = time.time()

    # 收集并排序图片
    extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.tiff', '*.webp']
    image_files = []
    for ext in extensions:
        image_files.extend([str(p) for p in Path(input_dir).glob(ext)])
        image_files.extend([str(p) for p in Path(input_dir).glob(ext.upper())])
    image_files = list(set(image_files))
    image_files = sorted(image_files, key=extract_number)

    if not image_files:
        logger.error(f"在目录 {input_dir} 中未找到任何图片！")
        return

    total = len(image_files)

    logger.info("=" * 60)
    logger.info("  去重切片 → 连续文档重建器 v1.0")
    logger.info("  双检架构: 页码连续性 + 帧时间差/Jaccard 兜底")
    logger.info("=" * 60)
    logger.info(f"输入目录:       {input_dir}")
    logger.info(f"输出文件:       {output_md}")
    logger.info(f"图片总数:       {total} 张")
    logger.info(f"切片间隔:       {slice_interval}s/帧")
    logger.info(f"时间报警阈值:   {time_gap_threshold}s")
    logger.info(f"Jaccard 阈值:   {jaccard_threshold}")
    logger.info(f"GPU 加速:       {'是' if use_gpu else '否'}")
    logger.info(f"OCR 语言:       {ocr_lang}")
    logger.info(f"内嵌图片引用:   {'是' if embed_images else '否'}")
    logger.info("=" * 60)

    # 初始化 EasyOCR
    logger.info("正在加载 OCR 模型...")
    ocr_load_start = time.time()
    reader = easyocr.Reader(ocr_lang, gpu=use_gpu)
    logger.info(f"OCR 模型加载完成，耗时 {time.time() - ocr_load_start:.1f}s")

    # 统计
    missing_count = 0
    page_jumps = 0
    time_gaps = 0

    logger.info(f"\n开始处理 {total} 张图片...")
    logger.info("-" * 60)

    with open(output_md, 'w', encoding='utf-8') as md_file:
        md_file.write("# 视频文档提取笔记\n\n")
        md_file.write(f"> 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        md_file.write(f"> 来源目录: `{input_dir}`\n")
        md_file.write(f"> 图片总数: {total} 张\n\n")
        md_file.write("---\n\n")

        last_frame_num = -1
        last_page_num = None
        last_text = ""

        for i, img_path in enumerate(image_files):
            filename = os.path.basename(img_path)
            progress = f"[{i+1}/{total}]"

            # --- 1. OCR 提取文本 ---
            ocr_start = time.time()
            try:
                raw_text = extract_text(reader, img_path)
                curr_text = '\n'.join([line.strip() for line in raw_text.split('\n') if line.strip()])
            except Exception as e:
                logger.warning(f"{progress} OCR 失败 {filename}: {e}")
                curr_text = ""
            ocr_time = time.time() - ocr_start

            curr_frame_num = extract_number(filename)
            curr_page_num = extract_page_number(curr_text)

            # --- 2. 双检逻辑判定断层 ---
            is_missing = False
            missing_reason = ""

            if last_frame_num != -1:
                # 优先级 1: 页码连续性检测
                if curr_page_num is not None and last_page_num is not None:
                    page_diff = curr_page_num - last_page_num
                    if page_diff > 1:
                        is_missing = True
                        page_jumps += 1
                        if page_diff == 2:
                            missing_reason = f"页码跳跃: {last_page_num} → {curr_page_num} (缺失第 {last_page_num + 1} 页)"
                        else:
                            missing_reason = f"页码跳跃: {last_page_num} → {curr_page_num} (缺失第 {last_page_num + 1}~{curr_page_num - 1} 页)"

                # 兜底检测: 页码提取失败时，用帧时间差 + Jaccard
                else:
                    frame_diff = curr_frame_num - last_frame_num
                    time_diff = frame_diff * slice_interval
                    if time_diff > time_gap_threshold:
                        jaccard = calculate_jaccard(last_text, curr_text)
                        if jaccard < jaccard_threshold:
                            is_missing = True
                            time_gaps += 1
                            start_time_str = format_time(last_frame_num * slice_interval)
                            end_time_str = format_time(curr_frame_num * slice_interval)
                            missing_reason = (
                                f"时间跨度 {time_diff:.1f}s (帧 {last_frame_num}→{curr_frame_num}), "
                                f"原视频 {start_time_str}~{end_time_str}, "
                                f"文本相似度 {jaccard:.3f}"
                            )

            # --- 3. 写入 Markdown ---
            if is_missing:
                missing_count += 1
                md_file.write(f"\n> ⚠️ **缺失警告 #{missing_count}**\n")
                md_file.write(f"> **原因**: {missing_reason}\n")
                md_file.write(f"> **排查建议**: 回看原视频对应时间段补充切片\n\n")
                md_file.write("---\n\n")
                logger.warning(
                    f"{progress} ⚠️ 缺失检测 | {filename} | {missing_reason}"
                )

            md_file.write(f"### `{filename}`")
            if curr_page_num is not None:
                md_file.write(f" (第 {curr_page_num} 页)")
            md_file.write("\n\n")

            if embed_images:
                # 使用相对路径或绝对路径
                md_file.write(f"![{filename}]({img_path})\n\n")

            md_file.write(f"**识别文本**：\n\n```text\n{curr_text}\n```\n\n")
            md_file.write("---\n\n")

            # --- 4. 更新状态 ---
            last_frame_num = curr_frame_num
            if curr_page_num is not None:
                last_page_num = curr_page_num
            last_text = curr_text

            if not is_missing:
                logger.info(
                    f"{progress} ✅ {filename} | "
                    f"OCR: {ocr_time:.2f}s | "
                    f"{'页码:' + str(curr_page_num) if curr_page_num else '无页码'}"
                )

    # === 统计报告 ===
    elapsed = time.time() - start_time
    logger.info("\n" + "=" * 60)
    logger.info("  文档重建完成 — 统计报告")
    logger.info("=" * 60)
    logger.info(f"总处理图片:     {total} 张")
    logger.info(f"检测到缺失:     {missing_count} 处")
    logger.info(f"  - 页码跳跃:   {page_jumps} 处")
    logger.info(f"  - 时间跨度:   {time_gaps} 处")
    logger.info(f"输出文件:       {output_md}")
    logger.info(f"总耗时:         {elapsed:.1f}s")
    if total > 0:
        logger.info(f"平均速度:       {elapsed / total:.3f}s/张")
    logger.info("=" * 60)


# ============================================================
#  CLI 入口
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="去重切片 → 连续文档重建器 (双检架构: 页码连续性 + 帧时间差/Jaccard 兜底)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 基本用法
  python doc_reconstruct.py -i ./deduped_frames -o document.md

  # 启用 GPU 加速
  python doc_reconstruct.py -i ./deduped_frames -o document.md --gpu

  # 自定义参数
  python doc_reconstruct.py -i ./deduped_frames -o document.md --gpu --slice-interval 2.0 --time-gap 5.0

  # 不内嵌图片引用 (纯文本输出更轻量)
  python doc_reconstruct.py -i ./deduped_frames -o document.md --no-images

参数调优指南:
  --slice-interval   1.0  原始切片的时间间隔(秒/帧)，需与抽帧脚本一致
  --time-gap         3.0  时间跨度报警阈值。切片间隔2s时可调至5.0
  --jaccard          0.05 文本相似度兜底阈值。内容差异大的文档可调至0.03
        """,
    )

    parser.add_argument("-i", "--input", required=True, help="去重后保留的切片图片目录")
    parser.add_argument("-o", "--output", required=True, help="输出的 Markdown 文件路径")

    parser.add_argument("--slice-interval", type=float, default=1.0, help="原始切片的时间间隔(秒/帧)，默认 1.0")
    parser.add_argument("--time-gap", type=float, default=3.0, help="时间跨度报警阈值(秒)，默认 3.0")
    parser.add_argument("--jaccard", type=float, default=0.05, help="Jaccard 文本相似度兜底阈值，默认 0.05")

    parser.add_argument("--gpu", action="store_true", default=False, help="启用 GPU 加速")
    parser.add_argument("--auto-gpu", action="store_true", default=False, help="自动检测 GPU 并启用")
    parser.add_argument("--lang", nargs="+", default=["ch_sim", "en"], help="EasyOCR 识别语言，默认 ch_sim en")

    parser.add_argument("--no-images", action="store_true", default=False, help="不在 Markdown 中内嵌图片引用 (纯文本输出)")

    args = parser.parse_args()

    if not os.path.isdir(args.input):
        print(f"错误: 输入目录不存在: {args.input}")
        sys.exit(1)

    use_gpu = args.gpu
    if args.auto_gpu and not use_gpu:
        if detect_gpu():
            use_gpu = True
            print("检测到 NVIDIA GPU，已自动启用 GPU 加速")
        else:
            print("未检测到 GPU，使用 CPU 模式")

    log_dir = os.path.join(os.path.dirname(args.output) or ".", "_logs")
    logger = setup_logger(log_dir)

    try:
        reconstruct(
            input_dir=args.input,
            output_md=args.output,
            slice_interval=args.slice_interval,
            time_gap_threshold=args.time_gap,
            jaccard_threshold=args.jaccard,
            use_gpu=use_gpu,
            ocr_lang=args.lang,
            embed_images=not args.no_images,
            logger=logger,
        )
    except KeyboardInterrupt:
        logger.info("\n用户中断，已处理的内容保留在输出文件中。")
        sys.exit(130)
    except Exception as e:
        logger.error(f"运行出错: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
