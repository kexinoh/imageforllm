"""
Bytes Object Example for imageforllm

This script demonstrates:
1. Working with image byte objects directly using the new bytes-specific functions
2. Compatibility with both path-based and bytes-based functions
3. Adding AI generation metadata to bytes
4. Reading back metadata from bytes
5. Converting between file paths and bytes

This is useful when working with images from APIs, URLs, or base64-encoded data.
"""

import os
import sys
import json
import base64
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
print("Step 1: Loading an image as bytes")

# Get the path to the example image file
current_dir = Path(__file__).parent
original_image_path = current_dir / 'aigirl.png'

if not original_image_path.exists():
    print(f"Error: Image file not found at {original_image_path}")
    exit(1)

print(f"Found image at: {original_image_path}")

# Read image file as bytes
with open(original_image_path, 'rb') as f:
    image_bytes = f.read()

print(f"Successfully loaded image as bytes ({len(image_bytes)} bytes)")

print("-" * 40)
print("Step 2: Adding AI metadata to image bytes using the new bytes-specific function")

# --- Step 2: Define the AI metadata ---
model = "stable-diffusion-xl-1.0"
prompt = "A digital painting of a futuristic cityscape at night with neon lights"
parameters = {
    "seed": 42,
    "guidance_scale": 7.5,
    "num_inference_steps": 50
}

# --- Step 3: Add the AI metadata directly to the bytes ---
print("Adding AI metadata to image bytes...")

# Use the bytes-specific function
result_buffer = imageforllm.add_ai_metadata_to_bytes(
    image_bytes,
    model=model,
    prompt=prompt,
    parameters=parameters
)

if result_buffer:
    modified_bytes = result_buffer.getvalue()
    print(f"Successfully added AI metadata, new size: {len(modified_bytes)} bytes")
    
    # Save to a file for later reference
    output_path_1 = current_dir / 'bytes_output_1.png'
    with open(output_path_1, 'wb') as f:
        f.write(modified_bytes)
    print(f"Saved bytes with metadata to: {output_path_1}")
else:
    print("Failed to add AI metadata to the image bytes.")
    exit(1)

# Use the file-based function with a direct path
output_path_2 = current_dir / 'bytes_output_2.png'
success = imageforllm.add_ai_metadata(
    str(output_path_2.with_suffix('.orig.png')), # use a different file to avoid overwriting
    model=model,
    prompt=prompt,
    parameters=parameters
)

print(f"Added metadata using file-based function: {'Success' if success else 'Failed'}")

print("-" * 40)
print("Step 3: Reading AI metadata directly from bytes using the bytes-specific function")

# --- Step 4: Read the AI metadata from the bytes ---
print(f"Reading AI metadata from the modified bytes...")

# Extract only the AI-specific metadata using the bytes-specific function
ai_metadata = imageforllm.extract_ai_metadata_from_bytes(modified_bytes)
if ai_metadata:
    print("\n--- AI Metadata Extracted from Bytes using bytes-specific function ---")
    print(json.dumps(ai_metadata, indent=2))
    print("--- End of AI Metadata ---")
else:
    print("No AI metadata found in the bytes.")

# Extract all metadata for comparison using the bytes-specific function
all_metadata = imageforllm.get_all_metadata_json_from_bytes(modified_bytes)
if all_metadata:
    print("\n--- All Metadata Extracted from Bytes using bytes-specific function ---")
    print(json.dumps(all_metadata, indent=2))
    print("--- End of All Metadata ---")
else:
    print("No metadata found in the bytes.")

print("-" * 40)
print("Step 4: Demonstrating function compatibility and interoperability")

# Save the bytes to a temp file
test_path = current_dir / 'temp_test.png'
with open(test_path, 'wb') as f:
    f.write(modified_bytes)

# Now read with file-based API
file_metadata = imageforllm.get_all_metadata_json(str(test_path))
print("\n--- Metadata read from file ---")
print(json.dumps(file_metadata, indent=2))
print("--- End of Metadata ---")

# Clean up temp file
if test_path.exists():
    os.remove(test_path)
    print(f"Removed temporary file: {test_path}")

print("-" * 40)
print("Step 5: Simulating base64 encoding/decoding workflow")

# This simulates what might happen in a web application
# The image is received as base64, processed, and then returned as base64
base64_encoded = base64.b64encode(image_bytes).decode('utf-8')
print(f"Base64 encoded image (first 50 chars): {base64_encoded[:50]}...")

# Decode the base64 data
decoded_bytes = base64.b64decode(base64_encoded)

# Add metadata to the decoded bytes using the bytes-specific function
result_buffer = imageforllm.add_ai_metadata_to_bytes(
    decoded_bytes,
    model="midjourney-v5",
    prompt="Sunset over mountains with lake reflections",
    parameters={"style": "realistic"},
)

# Extract metadata to verify it worked
metadata = imageforllm.extract_ai_metadata_from_bytes(result_buffer.getvalue())
print("\n--- Metadata from Base64 Workflow ---")
print(json.dumps(metadata, indent=2))
print("--- End of Metadata ---")

# Re-encode to base64 for sending back to client
processed_base64 = base64.b64encode(result_buffer.getvalue()).decode('utf-8')
print(f"Processed base64 encoded image (first 50 chars): {processed_base64[:50]}...")

print("-" * 40)
print("Example script finished.")

print("\nIn a real-world scenario, you might receive image bytes from:")
print("1. HTTP requests (requests.get('url').content)")
print("2. Base64-encoded data in JSON (base64.b64decode(data))")
print("3. File uploads in web applications")
print("4. In-memory image processing (PIL or OpenCV)")
print("\nWith the bytes-specific functions, you can work with these sources directly!") 