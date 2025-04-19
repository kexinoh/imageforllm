# ImageForLLM 🖼️

[English](README.md) | [中文](README_zh.md)

为LLM提供图像识别的免费午餐 🍱

[![Python 3](https://img.shields.io/badge/python-3+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 概述 🔍

ImageForLLM能够将源注释和图表属性嵌入到matplotlib图像中，特别适用于与大型语言模型（LLMs）共享图表。这使LLM能够理解图表是如何生成的以及它代表什么。现在它还支持为AI生成的图像添加元数据，以提供更好的上下文。

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

- 将生成图表的源注释嵌入到图像元数据中
- 自动提取并嵌入图表属性（标题、标签等）
- 为AI生成的图像添加元数据（模型、提示、参数）
- 从图像中提取嵌入的注释、属性和AI元数据
- 用于从图像提取元数据和添加AI元数据的命令行工具
- 以JSON格式获取所有元数据，便于与其他工具集成

## 使用方法 🚀

### 基本Matplotlib工作流程

```python
import matplotlib.pyplot as plt
import numpy as np
import imageforllm

# 1. 钩住matplotlib的savefig函数
imageforllm.hook_image_save()

# 2. 将你的图表注释定义为字符串
plot_source_comment = """
它适用于波形图。
"""

# 3. 创建你的图表
x = np.linspace(0, 10, 100)
y = np.sin(x)
plt.plot(x, y)
plt.title('正弦波')
plt.xlabel('时间')
plt.ylabel('振幅')

# 4. 保存时嵌入注释和自动提取的属性
plt.savefig('sine_wave_plot.png', create_comment=plot_source_comment)

# 5. (可选) 完成后取消钩子
imageforllm.unhook_image_save()
```

### 为图像添加AI元数据

```python
import imageforllm

# 为现有图像添加AI生成元数据
model = "stable-diffusion-xl-1.0"
prompt = "一个宁静的山水景观，湖面倒映着夕阳"
parameters = {
    "seed": 42,
    "guidance_scale": 7.5,
    "num_inference_steps": 50
}

imageforllm.add_ai_metadata('ai_generated_image.png', model, prompt, parameters)
```

### 提取元数据 🔄

```python
import imageforllm

# 从图像获取所有元数据作为可JSON序列化的字典
all_info = imageforllm.get_all_metadata_json('image.png')

# 访问嵌入的注释
comment = all_info.get('source_comment')
print(comment)

# 访问图表属性
properties = all_info.get('plot_properties')
print(properties)

# 访问AI元数据
ai_model = all_info.get('ai_model')
prompt = all_info.get('prompt')
parameters = all_info.get('parameters')
print(f"模型: {ai_model}, 提示词: {prompt}")

# 仅提取AI特定元数据
ai_metadata = imageforllm.extract_ai_metadata('ai_generated_image.png')
print(ai_metadata)
```

### 命令行提取 🖥️

该包包含用于处理元数据的命令行工具：

```bash
# 提取并打印注释
python -m imageforllm.extract image.png

# 提取并打印所有元数据
python -m imageforllm.extract image.png --info

# 仅提取图表属性
python -m imageforllm.extract image.png --properties

# 仅提取AI元数据
python -m imageforllm.extract image.png --ai

# 以JSON格式输出
python -m imageforllm.extract image.png --json

# 将提取的注释保存到文件
python -m imageforllm.extract image.png -o extracted_comment.py
```

### 通过命令行添加AI元数据

```bash
# 为图像添加AI元数据
python -m imageforllm.ai_metadata image.png --model "stable-diffusion" --prompt "山水景观" --parameters '{"seed": 42}'
```

## 局限性 ⚠️

- 元数据嵌入主要支持PNG格式
- 当保存到类文件对象时，不支持元数据嵌入
- 该包不能自动确定生成图表的注释；您必须以字符串形式提供

## 工作原理 🔧

1. 该包钩住matplotlib的`savefig`函数
2. 保存时，它捕获任何提供的源注释并自动提取图表属性
3. 它使用Pillow将这些元数据嵌入到PNG图像中
4. 对于AI生成的图像，您可以添加模型、提示词和参数信息
5. 稍后可以使用提供的函数或命令行工具从图像中提取元数据

## 示例 📝

请参见包含的`examples/saveandread.py`，了解保存和读取元数据的示例，以及`examples/ai_metadata_example.py`，了解如何处理AI生成的图像。

## API参考 📚

### 主要函数

- `hook_image_save()`：用嵌入元数据的版本替换matplotlib的savefig
- `unhook_image_save()`：恢复原始的savefig函数
- `get_image_info(image_path)`：从图像文件中提取元数据
- `get_all_metadata_json(image_path)`：获取所有ImageForLLM特定的元数据（源注释、图表属性和AI元数据）作为可JSON序列化的字典。仅返回本库定义的元数据，不包含图像的其他数据。
- `add_ai_metadata(image_path, model, prompt, parameters=None)`：为图像添加AI生成元数据
- `extract_ai_metadata(image_path)`：仅从图像中提取AI特定元数据

### 常量

- `METADATA_KEY_COMMENT`：元数据字典中源注释的键
- `METADATA_KEY_PROPERTIES`：元数据字典中图表属性的键
- `METADATA_KEY_AI_MODEL`：AI模型信息的键
- `METADATA_KEY_PROMPT`：生成提示词的键
- `METADATA_KEY_PARAMETERS`：额外参数的键

## 许可证 📄

MIT