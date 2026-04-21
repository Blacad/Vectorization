# 阶段三：图像预处理模块

## 目标

实现矢量化前的预处理流程，为轮廓提取提供更干净的输入。

## 任务清单

### 3.1 黑白图预处理

-  实现灰度化
-  实现高斯去噪
-  实现中值滤波
-  实现固定阈值二值化
-  实现 Otsu 自适应阈值二值化
-  支持黑底白字/白底黑字反转

### 3.2 形态学处理

-  实现腐蚀
-  实现膨胀
-  实现开运算
-  实现闭运算
-  允许通过参数控制核大小

### 3.3 彩色图预处理

-  实现颜色空间转换（BGR/RGB/HSV）
-  实现可选缩放
-  为后续颜色量化准备输入

## 建议函数

-  `to_grayscale(image) -> np.ndarray`
-  `denoise_image(image, method="gaussian") -> np.ndarray`
-  `binarize_image(image, method="otsu", invert=False) -> np.ndarray`
-  `morphology_process(image, op="open", kernel_size=3) -> np.ndarray`
-  `resize_if_needed(image, max_size=None) -> np.ndarray`

## 阶段验收标准

-  对高对比图像可输出干净二值图
-  小噪点明显减少
-  预处理参数可配置