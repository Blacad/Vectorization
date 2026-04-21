# 阶段八：总流程整合与命令行接口

## 目标

将所有模块串联为完整工具，支持用户通过命令行直接执行转换。

## 任务清单

### 8.1 CLI 设计

-  支持输入文件路径参数
-  支持输出文件路径参数
-  支持模式选择：`binary` / `color`
-  支持阈值参数
-  支持最小面积参数
-  支持颜色数量参数
-  支持简化强度参数
-  支持是否反色参数

### 8.2 流程调度

-  根据模式调用黑白或彩色管线
-  统一日志输出
-  统一异常处理
-  命令执行结束后输出结果摘要

## 建议命令示例

```
python main.py --input examples/input/logo.png --output examples/output/logo.svg --mode binary
python main.py --input examples/input/icon.png --output examples/output/icon.svg --mode color --colors 8
```

## 阶段验收标准

-  一条命令可完成完整转换
-  参数错误时有明确提示
-  正常执行后输出 SVG 文件