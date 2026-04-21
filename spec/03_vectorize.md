# 阶段四：黑白图像矢量化流程

## 目标

优先完成最小可用版本：将黑白/线稿/图标图像转换为 SVG 路径。

## 任务清单

### 4.1 轮廓提取

-  基于二值图提取外轮廓
-  支持提取孔洞/内部轮廓
-  支持按面积过滤小轮廓
-  支持选择不同轮廓检索模式

### 4.2 点集处理

-  将 OpenCV 轮廓转换为点集
-  去除重复点
-  保证轮廓闭合
-  统一轮廓方向（顺时针/逆时针）

### 4.3 折线路径生成

-  将轮廓点转换为 SVG path
-  支持 `M/L/Z` 命令输出
-  处理多轮廓场景

## 建议函数

-  `find_contours(binary_image, min_area=10, retrieve_holes=True) -> list`
-  `contour_to_points(contour) -> list[tuple[int, int]]`
-  `build_polygon_path(points) -> str`

## 阶段验收标准

-  黑白 logo 可成功输出 SVG
-  输出 SVG 可被浏览器正常打开
-  小面积噪点不会生成大量无用路径