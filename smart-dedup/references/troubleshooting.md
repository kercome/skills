# 已知问题 & 解决方案

## 问题 1: 任务在 10 分钟时被超时砍掉

### 现象

日志显示只处理了 300/1199 张图片就停止了，输出目录为空。

### 原因

WorkBuddy 沙箱中的 Bash/PowerShell 工具有默认超时限制（约 10 分钟）。1199 张图片在 CPU 模式下需要约 2 小时，10 分钟只够处理 300 张。

### 解决方案

**在原生 Windows PowerShell（非沙箱）中运行**。原生终端没有超时限制，让脚本自然跑到结束。

```powershell
cd C:\Users\Kerco\WorkBuddy\2026-06-25-22-51-10
.\.venv\Scripts\Activate.ps1
python smart_dedup.py -i "H:\AAA\切片\串烧" -o "H:\AAA\切片\串烧_去重结果" --gpu
```

---

## 问题 2: GPU 不可用 (CUDA not available)

### 现象

```
>>> torch.cuda.is_available()
False
>>> torch.__version__
'2.12.1+cpu'
```

日志写着 `GPU 加速: 是`，但 EasyOCR 静默降级到 CPU，全程没有警告。

### 原因 (三层断链)

| 层 | 问题 | 详情 |
|----|------|------|
| L1 PyTorch | CPU 版本 | 安装的是 `torch-2.12.1+cpu`，不是 CUDA 版 |
| L2 CUDA Toolkit | 未安装 | 系统没有 CUDA Toolkit |
| L3 Sandbox 隔离 | 驱动访问被拦截 | sandbox 进程无法访问 NVIDIA 内核驱动 |

**第 3 层是根本瓶颈**——即便装了 GPU 版 PyTorch + CUDA Toolkit，在沙箱里也看不到 GPU。

### 解决方案

1. 在原生 PowerShell 运行（绕过沙箱）
2. 安装 GPU 版 PyTorch:

```powershell
pip uninstall torch torchvision -y
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124
```

> Python 3.13 只能用 cu124 (CUDA 12.4)，cu121 没有 3.13 的轮子。

---

## 问题 3: PyTorch CUDA 索引找不到对应版本

### 现象

```
Looking in indexes: https://download.pytorch.org/whl/cu121
ERROR: Could not find a version that satisfies the requirement torch
```

### 原因

Python 3.13 + CUDA 12.1 的 PyTorch 轮子不存在。最新支持的组合是 Python 3.13 + CUDA 12.4。

### 解决方案

将索引 URL 改为 `cu124`:

```powershell
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124
```

---

## 问题 4: 执行中断后输入目录文件不完整

### 现象

脚本被 kill 时正处于循环中，部分图片已被 `shutil.move` 到 `_duplicates` 目录。输入目录剩余 961 张，`_duplicates` 有 239 张。输出目录为空。

### 原因

脚本只有完整运行到循环结束后才执行文件导出。如果中途被中断，`shutil.move` 效果已生效但 `shutil.copy2` 导出未执行。

### 解决方案

运行前先把 `_duplicates` 中的文件移回输入目录：

```powershell
Get-ChildItem "H:\AAA\切片\串烧\_duplicates\*" -File | Move-Item -Destination "H:\AAA\切片\串烧\" -Force
```
