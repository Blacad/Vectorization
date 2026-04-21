# 阶段五：轮廓简化与平滑优化

## 目标

减少路径节点数量，改善边缘锯齿感，让输出更接近真实矢量图。

## 任务清单

### 5.1 折线简化

-  使用 Douglas-Peucker 算法简化轮廓
-  支持按轮廓长度动态计算 epsilon
-  提供简化强度参数

### 5.2 平滑策略

-  为点集添加可选平滑
-  研究并实现基础 Bézier 曲线拟合
-  若完整拟合较复杂，先实现“简化折线版本 + 预留平滑接口”

### 5.3 路径质量控制

-  限制最大节点数
-  过滤异常尖角
-  处理过短线段

## 建议函数

-  `simplify_contour(contour, epsilon_ratio=0.002) -> np.ndarray`
-  `smooth_points(points, method="none") -> list`
-  `build_bezier_path(points) -> str`（可先占位实现）

## 阶段验收标准

-  输出路径点数量明显减少
-  轮廓形状基本保持不失真
-  相比原始轮廓，SVG 文件体积更小