# Bitmap to SVG Vectorizer

一个用 Python 编写的位图转 SVG 命令行工具，支持 `jpg`、`jpeg`、`png` 输入。它优先服务黑白/高对比图像，也支持基础彩色图标和扁平插画的区域矢量化。

## 安装

```bash
python3 -m venv vector
source vector/bin/activate
pip install -r requirements.txt
```

## 使用

黑白/高对比图像：

```bash
python main.py --input examples/input/logo.png --output examples/output/logo.svg --mode binary
```

如果原图是白底黑色主体，通常需要反色：

```bash
python main.py --input examples/input/logo.png --output examples/output/logo.svg --mode binary --invert
```

彩色图像：

```bash
python main.py --input examples/input/icon.png --output examples/output/icon.svg --mode color --colors 8
```

## 参数

- `--input`：输入 `jpg/jpeg/png` 文件路径。
- `--output`：输出 SVG 文件路径。
- `--mode binary|color`：选择黑白或彩色矢量化流程。
- `--threshold`：固定二值化阈值；不传时使用 Otsu。
- `--min-area`：过滤小轮廓面积，默认 `10`。
- `--colors`：彩色模式 K-Means 聚类颜色数量，默认 `8`。
- `--epsilon-ratio`：Douglas-Peucker 轮廓简化强度，默认 `0.002`。
- `--invert`：反转黑白阈值结果。
- `--max-size`：处理前缩放最长边，但 SVG 输出尺寸仍匹配原图。
- `--smooth none|chaikin|bezier`：可选平滑策略。

## 测试

```bash
pytest
```

## 适用范围

适合：

- 黑白 logo
- 高对比线稿
- 图标
- 扁平插画
- 色块清晰的简单图像

不适合：

- 复杂照片
- 大面积渐变
- 纹理丰富的图像
- 对路径艺术质量要求很高的商业矢量重绘

