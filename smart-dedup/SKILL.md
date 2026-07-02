---
name: smart-dedup
description: 文档类视频切片智能去重工具。组合 SSIM 结构相似度三层分流 + EasyOCR 灰色地带裁决，自动识别并移除 PPT 录屏、代码演示、网页滚动等场景下的重复帧。适用于 10 分钟级视频切片（约 600-1200 张图片）的去重处理。当用户需要对视频抽帧后的图片序列去除重复画面、提取关键帧、压缩视频切片存储时触发本技能。
agent_created: true
---

# 文档切片智能去重工具

## 概述

对视频切片图片做 SSIM 结构相似度比对，分三档处理：
- SSIM ≥ 0.98 → 直接删（绝对重复：静止画面/光标闪烁/压缩噪点）
- SSIM < 0.70 → 直接留（翻页新画面）
- 0.70 ~ 0.98 → 再用 OCR 提取文字，文字一样就删，文字变了就留

比较基准是**上一个被保留的图片**，不是紧挨着的前一张，防止"慢漂移"误判。

## 使用场景

- PPT 录屏切片去重
- 代码演示视频抽帧去重
- 网页滚动/文档展示类视频去重
- 任何"画面大部分静止，偶尔有文字/内容更新"的视频切片

## 运行环境要求

### 关键限制：不能在 WorkBuddy 沙箱中运行

WorkBuddy 的 Bash/PowerShell 工具运行在沙箱环境中，进程被隔离，无法访问 NVIDIA 内核驱动。即使装了 GPU 版 PyTorch，`torch.cuda.is_available()` 也会返回 `False`。

**必须在原生 Windows PowerShell (非 sandbox) 中运行。**

### 依赖安装

```powershell
cd <项目目录>
.\.venv\Scripts\Activate.ps1

# 安装核心依赖
pip install opencv-python scikit-image easyocr

# 安装 GPU 版 PyTorch (Python 3.13 只能用 cu124)
pip uninstall torch torchvision -y
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124

# 验证 GPU
python -c "import torch; print('CUDA available:', torch.cuda.is_available())"
```

详细环境信息见 `references/environment.md`。

## 运行流程

### 1. 准备输入

确保输入目录中只有图片文件（jpg/jpeg/png/bmp/tiff/webp），文件名包含数字序号以保证顺序。

### 2. 执行去重

```powershell
python scripts/smart_dedup.py -i "输入目录" -o "输出目录" --gpu
```

可选参数：
- `--strict-ssim 0.98` — 绝对重复阈值，翻页带平滑动画可调低至 0.95
- `--loose-ssim 0.70` — 新页面阈值，柔和过渡可调至 0.60
- `--text-thresh 0.90` — 文本重复阈值，代码演示调低至 0.80，PPT小字变化调高至 0.95
- `--lang ch_sim en` — OCR 识别语言，纯中文可用 `ch_sim`
- `--auto-gpu` — 自动检测 GPU

### 3. 输出结构

```
输出目录/
├── slide_001.jpg      # 保留的去重图片 (按 slide_NNN 重命名)
├── slide_002.jpg
└── _logs/
    └── dedup_YYYYMMDD_HHMMSS.log

输入目录/_duplicates/    # 被剔除的重复图片 (从输入目录 move 过来)
```

### 4. 中断恢复

如果脚本被意外中断，输入目录会缺少被 move 走的图片。运行前先把 `_duplicates` 中的文件移回：

```powershell
Get-ChildItem "输入目录\_duplicates\*" -File | Move-Item -Destination "输入目录\" -Force
```

## 算法详解

完整算法说明、三层分流逻辑、关键设计决策见 `references/ssim-algorithm.md`。

## 排错指南

已知问题及解决方案见 `references/troubleshooting.md`，包括：
- 沙箱超时砍断
- GPU 不可用
- PyTorch CUDA 版本不匹配
- 中断后文件不完整

## 资源清单

| 文件 | 用途 |
|------|------|
| `scripts/smart_dedup.py` | 核心去重脚本，可直接执行 |
| `references/ssim-algorithm.md` | SSIM 三层分流算法详解 + 设计决策 |
| `references/troubleshooting.md` | 已知问题 & 解决方案 |
| `references/environment.md` | 硬件、软件、路径环境信息 |
