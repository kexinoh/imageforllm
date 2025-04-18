# ImageForLLM

A package to embed code and plot properties into matplotlib images for LLM context.

## Overview

ImageForLLM enables embedding source code and plot properties into matplotlib images, particularly useful when sharing plots with Large Language Models (LLMs). This allows the LLM to understand how the plot was generated and what it represents.

## Installation

```bash
pip install imageforllm
```

The package requires Pillow for metadata embedding:

```bash
pip install Pillow
```

## Features

- Embed source code that generated a plot into the image metadata
- Automatically extract and embed plot properties (titles, labels, etc.)
- Extract embedded code and properties from images
- Command-line tool for extracting metadata from images

## Usage

### Basic Workflow

```python
import matplotlib.pyplot as plt
import numpy as np
import imageforllm

# 1. Hook matplotlib's savefig function
imageforllm.hook_image_save()

# 2. Define your plot code as a string
plot_source_code = """
It make work for a wave plot.
"""

# 3. Create your plot
x = np.linspace(0, 10, 100)
y = np.sin(x)
plt.plot(x, y)
plt.title('Sine Wave')
plt.xlabel('Time')
plt.ylabel('Amplitude')

# 4. Save with embedded code and auto-extracted properties
plt.savefig('sine_wave_plot.png', create_comment=plot_source_code)

# 5. (Optional) Unhook when done
imageforllm.unhook_image_save()
```

### Extracting Metadata

```python
import imageforllm

# Get metadata from an image
info = imageforllm.get_image_info('sine_wave_plot.png')

# Access embedded code
code = info.get(imageforllm.METADATA_KEY_CODE)
print(code)

# Access plot properties
properties = info.get(imageforllm.METADATA_KEY_PROPERTIES)
print(properties)
```

### Command-line Extraction

The package includes a command-line tool for extracting metadata:

```bash
# Extract and print code
python -m imageforllm.extract sine_wave_plot.png

# Extract and print all metadata
python -m imageforllm.extract sine_wave_plot.png --info

# Extract only plot properties
python -m imageforllm.extract sine_wave_plot.png --properties

# Output in JSON format
python -m imageforllm.extract sine_wave_plot.png --json

# Save extracted code to a file
python -m imageforllm.extract sine_wave_plot.png -o extracted_code.py
```

## Limitations

- Metadata embedding is primarily supported for PNG format
- When saving to file-like objects, metadata embedding is not supported
- The package cannot automatically determine the code that generated a plot; you must provide it as a string

## How It Works

1. The package hooks matplotlib's `savefig` function
2. When saving, it captures any provided source code and automatically extracts plot properties
3. It embeds this metadata into the PNG image using Pillow
4. Metadata can later be extracted from the image using the provided functions or command-line tool

## Example

See the included `examples/saveandread.py` for a complete example of saving and reading metadata.

## API Reference

### Main Functions

- `hook_image_save()`: Replaces matplotlib's savefig with a version that embeds metadata
- `unhook_image_save()`: Restores the original savefig function
- `get_image_info(image_path)`: Extracts metadata from an image file

### Constants

- `METADATA_KEY_CODE`: Key for source code in metadata dictionary
- `METADATA_KEY_PROPERTIES`: Key for plot properties in metadata dictionary

## License

[License information]
