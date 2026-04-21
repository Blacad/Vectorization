# 阶段一：项目初始化与工程结构搭建

## 目标
建立标准 Python 工程结构，安装依赖，确保程序可以通过命令行运行。

## 任务清单

\- [ ] 创建项目目录结构
\- [ ] **创建虚拟环境与依赖文件** --- 虚拟环境名字为 `vector`
\- [ ] 选择并安装核心依赖
\- [ ] 配置基础代码风格工具
\- [ ] 配置测试框架
\- [ ] 创建程序入口文件
\- [ ] 创建示例资源目录
\- [ ] 创建输出目录

\## 建议依赖

\- `opencv-python`
\- `numpy`
\- `Pillow`
\- `svgwrite`
\- `scikit-learn`（用于彩色图像量化，可选但建议）
\- `pytest`

\## 建议目录结构

\```text
bitmap_to_vector/
├─ README.md
├─ requirements.txt
├─ pyproject.toml
├─ main.py
├─ vectorizer/
│  ├─ __init__.py
│  ├─ io.py
│  ├─ preprocess.py
│  ├─ contour.py
│  ├─ simplify.py
│  ├─ color_quantize.py
│  ├─ svg_export.py
│  ├─ pipeline.py
│  └─ cli.py
├─ tests/
│  ├─ test_io.py
│  ├─ test_preprocess.py
│  ├─ test_contour.py
│  ├─ test_svg_export.py
│  └─ test_pipeline.py
├─ examples/
│  ├─ input/
│  └─ output/
└─ docs/
   └─ design.md