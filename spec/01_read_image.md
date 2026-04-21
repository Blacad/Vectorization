# 阶段二：图像读取与输入校验

## 目标

实现稳定的图像输入模块，支持读取常见位图格式并进行参数校验。

## 任务清单

-  实现读取 `jpg/png/jpeg` 图像文件
-  支持灰度图和彩色图读取
-  校验输入路径是否存在
-  校验文件格式是否合法
-  校验图像是否成功解码
-  提供统一的错误处理与异常提示
-  输出图像基本信息（宽、高、通道数）

## 建议函数

-  `load_image(path: str) -> np.ndarray`
-  `validate_image_file(path: str) -> None`
-  `get_image_info(image: np.ndarray) -> dict`

## 阶段验收标准

-  可读取示例 PNG/JPG 文件
-  对非法路径和损坏文件给出明确报错
-  能返回图像尺寸与通道信息