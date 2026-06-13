# Doc2MD - 文档转 Markdown

## 功能
将 DOCX、PDF、XLSX、PPTX 文件转换为 Markdown 格式，自动提取文档内嵌图片。

## 触发场景
当用户说以下任一指令时激活：
- "转成 md"
- "转为 Markdown"
- "提取内容"

## 支持格式
| 格式 | 扩展名 | 转换工具 | 图片提取 |
|------|--------|---------|---------|
| Word | .docx | Pandoc / python-docx | ✅ |
| PDF | .pdf | Marker / PyMuPDF | ✅ |
| Excel | .xlsx, .xls | Python + openpyxl | ✅ (嵌入图表) |
| PowerPoint | .pptx, .ppt | Python + python-pptx | ✅ |

## 输出结构

每次转换生成一个与源文件同名的目录，所有输出文件都在该目录内：

```
example/                    ← 与源文件同名（去掉扩展名）
├── example.md              ← 主 Markdown 内容（含内联图片引用）
└── images/                 ← 提取的图片统一存放
    ├── image_1.png
    ├── image_2.png
    └── ...
```

说明：
- 目录名 = 源文件名去掉扩展名（如 `report.pdf` → `report/`）
- Markdown 中的图片引用格式：`![描述](images/image_1.png)`
- 图片按页/幻灯片顺序编号：`image_N.ext`
- 图片保留原始格式（png/jpg/jpeg/gif/bmp）

## 工作原理
1. 识别文件扩展名
2. 创建与源文件同名的输出目录
3. 调用对应转换工具提取文本和图片
4. 图片存入 `images/`，Markdown 中插入内联引用
5. 返回输出目录路径

## AI 自动决策
- 未指定输出路径 → 在源文件同目录下创建同名输出目录
- 工具未安装 → 提示安装命令

## 故障排除
| 问题 | 原因 | 解决 |
|------|------|------|
| 输出为空 | PDF 是扫描版/加密文档 | 确保 PDF 为文本型 |
| 格式不支持 | 扩展名不在支持列表 | 仅支持 DOCX/PDF/XLSX/PPTX |
| 工具未找到 | Pandoc/Marker/PyMuPDF 未安装 | 按提示安装对应工具 |
| 图片缺失 | 源文档无内嵌图片 | 正常现象，images/ 目录为空 |

## 自定义
修改 `scripts/doc2md.py` 可添加新格式支持。
