"""
AI Metadata Example for imageforllm

This script demonstrates:
1. Adding AI generation metadata to an existing image
2. Reading back that metadata from the image

This is useful for AI-generated images where you want to record the model,
prompt, and generation parameters in the image itself.
"""

import os
import json
from pathlib import Path

# --- Step 1: Import imageforllm ---
try:
    import imageforllm
    print(f"Successfully imported imageforllm package (Version: {imageforllm.__version__}).")
except ImportError:
    print("Error: imageforllm package not found.")
    print("Please install it using 'pip install imageforllm'.")
    exit(1)

print("-" * 40)
print("Step 1: Locating the AI-generated image")

# Get the path to the example image file
current_dir = Path(__file__).parent
original_image_path = current_dir / 'aigirl.png'

if not original_image_path.exists():
    print(f"Error: Image file not found at {original_image_path}")
    exit(1)

print(f"Found image at: {original_image_path}")

# Create a new file path for the version with metadata
output_image_path = current_dir / 'aigirl_with_metadata.png'

# Import shutil for file operations
import shutil

# Create a copy of the original image to work with
shutil.copy2(original_image_path, output_image_path)
print(f"Created copy for adding metadata at: {output_image_path}")

print("-" * 40)
print("Step 2: Adding AI metadata to the image")

# --- Step 2: Define the AI metadata ---
model = "gemini-2.0-flash-exp-image-generation"
prompt = "A long-haired Latin woman is looking back at the camera. There is a mirror in front of her. Similar to Lena Sjoberg."
parameters = {
    "temperature": 0.8,
    "max_output_tokens": 4096,
    "top_p": 0.95
}

# --- Step 3: Add the AI metadata to the image ---
print("Adding AI metadata to the image...")
success = imageforllm.add_ai_metadata(
    str(output_image_path),
    model=model,
    prompt=prompt,
    parameters=parameters
)

if success:
    print("Successfully added AI metadata to the image.")
else:
    print("Failed to add AI metadata to the image.")
    exit(1)

print("-" * 40)
print("Step 3: Reading the AI metadata back from the image")

# --- Step 4: Read the AI metadata from the image ---
print(f"Reading AI metadata from {output_image_path}...")

# Extract only the AI-specific metadata
ai_metadata = imageforllm.extract_ai_metadata(str(output_image_path))
if ai_metadata:
    print("\n--- AI Metadata Extracted ---")
    print(json.dumps(ai_metadata, indent=2))
    print("--- End of AI Metadata ---")
else:
    print("No AI metadata found in the image.")

# Extract all metadata for comparison
all_metadata = imageforllm.get_all_metadata_json(str(output_image_path))
if all_metadata:
    print("\n--- All Metadata Extracted ---")
    print(json.dumps(all_metadata, indent=2))
    print("--- End of All Metadata ---")
else:
    print("No metadata found in the image.")

print("-" * 40)
print("Example script finished.")

print("You can also extract metadata using the command line:")
print(f"python -m imageforllm.extract \"{output_image_path}\" --ai")
print("or")
print(f"python -m imageforllm.extract \"{output_image_path}\" --info")

print("\nThe original image remains unchanged at:")
print(f"{original_image_path}")
print("\nThe image with metadata is saved at:")
print(f"{output_image_path}") 