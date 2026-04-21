# 阶段七：SVG 导出模块

## 目标

统一管理 SVG 文件生成，保证输出结构规范、兼容性好、可读性高。

## 任务清单

-  封装 SVG 文档创建逻辑
-  支持设置宽高与 viewBox
-  支持写入单色 path
-  支持写入多色 path
-  支持填充色、描边色、描边宽度
-  支持保存到文件
-  保证编码与 XML 头正确

## 建议函数

-  `create_svg_document(width, height)`
-  `add_path(dwg, path_data, fill, stroke="none")`
-  `save_svg(dwg, output_path)`

## 阶段验收标准

-  生成的 SVG 可在浏览器和矢量工具中打开
-  SVG 文件结构规范
-  支持单色和多色输出