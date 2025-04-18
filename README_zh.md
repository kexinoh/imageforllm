# ImageForLLM 🖼️

[English](README.md) | [中文](README_zh.md)

为LLM提供图像识别的免费午餐 🍱

[![Python 3](https://img.shields.io/badge/python-3+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 概述 🔍

ImageForLLM能够将源代码和图表属性嵌入到matplotlib图像中，特别适用于与大型语言模型（LLMs）共享图表。这使LLM能够理解图表是如何生成的以及它代表什么。

## 简易使用 ✨

只需**两行**代码，它就可以自动将生成图像的信息添加到matplotlib生成的图像元数据中，无需任何额外操作。

对于LLM或其他读者，可以通过这些信息快速理解图片的内容。

```python
import imageforllm
imageforllm.hook_image_save()
```

## 安装 📦

```bash
pip install imageforllm
```

该包需要Pillow来嵌入元数据：

```bash
pip install Pillow
```

## 功能特点 ✅

- 将生成图表的源代码嵌入到图像元数据中
- 自动提取并嵌入图表属性（标题、标签等）
- 从图像中提取嵌入的代码和属性
- 用于从图像提取元数据的命令行工具

## 使用方法 🚀

### 基本工作流程

```python
import matplotlib.pyplot as plt
import numpy as np
import imageforllm

# 1. 钩住matplotlib的savefig函数
imageforllm.hook_image_save()

# 2. 将你的图表代码定义为字符串
plot_source_code = """
它适用于波形图。
"""

# 3. 创建你的图表
x = np.linspace(0, 10, 100)
y = np.sin(x)
plt.plot(x, y)
plt.title('正弦波')
plt.xlabel('时间')
plt.ylabel('振幅')

# 4. 保存时嵌入代码和自动提取的属性
plt.savefig('sine_wave_plot.png', create_comment=plot_source_code)

# 5. (可选) 完成后取消钩子
imageforllm.unhook_image_save()
```

### 提取元数据 🔄

```python
import imageforllm

# 从图像获取元数据
info = imageforllm.get_image_info('sine_wave_plot.png')

# 访问嵌入的代码
code = info.get(imageforllm.METADATA_KEY_CODE)
print(code)

# 访问图表属性
properties = info.get(imageforllm.METADATA_KEY_PROPERTIES)
print(properties)
```

### 命令行提取 🖥️

该包包含一个用于提取元数据的命令行工具：

```bash
# 提取并打印代码
python -m imageforllm.extract sine_wave_plot.png

# 提取并打印所有元数据
python -m imageforllm.extract sine_wave_plot.png --info

# 仅提取图表属性
python -m imageforllm.extract sine_wave_plot.png --properties

# 以JSON格式输出
python -m imageforllm.extract sine_wave_plot.png --json

# 将提取的代码保存到文件
python -m imageforllm.extract sine_wave_plot.png -o extracted_code.py
```

## 局限性 ⚠️

- 元数据嵌入主要支持PNG格式
- 当保存到类文件对象时，不支持元数据嵌入
- 该包不能自动确定生成图表的代码；您必须以字符串形式提供

## 工作原理 🔧

1. 该包钩住matplotlib的`savefig`函数
2. 保存时，它捕获任何提供的源代码并自动提取图表属性
3. 它使用Pillow将这些元数据嵌入到PNG图像中
4. 稍后可以使用提供的函数或命令行工具从图像中提取元数据

## 示例 📝

请参见包含的`examples/saveandread.py`，了解保存和读取元数据的完整示例。

## API参考 📚

### 主要函数

- `hook_image_save()`：用嵌入元数据的版本替换matplotlib的savefig
- `unhook_image_save()`：恢复原始的savefig函数
- `get_image_info(image_path)`：从图像文件中提取元数据

### 常量

- `METADATA_KEY_CODE`：元数据字典中源代码的键
- `METADATA_KEY_PROPERTIES`：元数据字典中图表属性的键

## 许可证 📄

[许可证信息] 