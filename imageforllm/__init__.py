"""
ImageForLLM - A package to embed code and plot properties into matplotlib images for LLM context
"""

import warnings

# Optional: Add a simple check to recommend Pillow installation if not present
try:
    from PIL import Image  # noqa: F401
except ImportError:
    warnings.warn(
        "imageforllm requires Pillow for metadata embedding. "
        "Install it with: pip install Pillow",
        ImportWarning
    )

# Import using absolute imports to ensure we always import from the correct location
from ._hook import hook_image_save, unhook_image_save
from ._metadata import (
    get_image_info, get_image_info_from_bytes,
    get_all_metadata_json, get_all_metadata_json_from_bytes,
    add_ai_metadata, add_ai_metadata_to_bytes,
    extract_ai_metadata, extract_ai_metadata_from_bytes,
    METADATA_KEY_COMMENT, METADATA_KEY_PROPERTIES, 
    METADATA_KEY_AI_MODEL, METADATA_KEY_PROMPT, METADATA_KEY_PARAMETERS
)
from .extract import main as extract_main

__version__ = "0.4.0"  

__all__ = [
    "hook_image_save",
    "unhook_image_save",
    "get_image_info",
    "get_image_info_from_bytes",
    "get_all_metadata_json",
    "get_all_metadata_json_from_bytes",
    "add_ai_metadata",
    "add_ai_metadata_to_bytes",
    "extract_ai_metadata",
    "extract_ai_metadata_from_bytes",
    "extract_main",
    "__version__",
    "METADATA_KEY_COMMENT", 
    "METADATA_KEY_PROPERTIES",
    "METADATA_KEY_AI_MODEL",
    "METADATA_KEY_PROMPT",
    "METADATA_KEY_PARAMETERS",
] 