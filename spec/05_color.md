# 阶段六：彩色图像矢量化流程

## 目标

支持基础彩色图像的分区域矢量化，适用于扁平插画、图标、简化色块图像。

## 任务清单

### 6.1 颜色量化

-  使用 K-Means 对颜色进行聚类
-  支持设置颜色数量 `k`
-  生成量化后的彩色图
-  保留每个颜色簇的代表色

### 6.2 分颜色区域提取

-  为每种量化颜色生成 mask
-  对每个 mask 单独提取轮廓
-  过滤小区域
-  支持多个同色区域分别生成路径

### 6.3 彩色 SVG 生成

-  为每个颜色区域生成 `fill`
-  控制图层顺序
-  避免区域间出现明显缝隙

## 建议函数

-  `quantize_colors(image, k=8) -> tuple[np.ndarray, list]`
-  `extract_color_regions(quantized_image, colors) -> list`
-  `build_colored_paths(regions) -> list[dict]`

## 阶段验收标准

-  彩色图标可输出多色 SVG
-  每个主要色块都能被识别
-  输出 SVG 颜色接近原图主要色彩