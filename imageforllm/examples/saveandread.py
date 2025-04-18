"""
Simplified Example Script for imageforllm

This script demonstrates the basic workflow:
1. Hooking matplotlib's savefig.
2. Defining the plot source comment as a string.
3. Generating a matplotlib plot.
4. Saving the plot with the embedded source comment and auto-extracted properties.
5. Reading the metadata back from the saved image file.
6. Unhooking savefig (optional cleanup).

Assumes imageforllm, matplotlib, and Pillow are installed.
"""

import matplotlib.pyplot as plt
import numpy as np
import textwrap  # To easily manage multi-line string indentation
import json      # To pretty-print the extracted properties
import os        # To check if the file exists and for output filename
# --- Step 1: Import imageforllm ---
# This assumes the package is installed (e.g., via pip install imageforllm).
try:
    import imageforllm
    print(f"Successfully imported imageforllm package (Version: {imageforllm.__version__}).")
except ImportError:
    print("Error: imageforllm package not found.")
    print("Please install it using 'pip install imageforllm' (or from your local source).")
    exit(1) # Exit if the package is not importable

print("-" * 40)
print("Step 2: Hooking matplotlib.pyplot.savefig")

# --- Step 2: Activate the imageforllm hook ---
# Call this function once at the beginning of your script or session.
# It replaces the default plt.savefig with imageforllm's version.
imageforllm.hook_image_save()
print("matplotlib.pyplot.savefig is now hooked by imageforllm.")

print("-" * 40)


print("Step 3: Defining plot source comment as a string and generating the plot")

# --- Step 3a: Define the source comment for your plot as a string ---
# imageforllm requires you to provide the comment string. It cannot reliably
# and automatically determine the exact sequence of calls that created
# your plot from the execution history.
#
# Use textwrap.dedent() to handle indentation if you define the string
# directly in your code like this.
plot_source_create_comment = textwrap.dedent("""
# This is the source comment used to generate the plot below.
import matplotlib.pyplot as plt
import numpy as np

# Sample data
x = np.linspace(0, 10, 100)
y1 = np.sin(x)
y2 = np.cos(x) * np.exp(-x/5) # Damped cosine

# Create figure and axes
fig, ax = plt.subplots(figsize=(8, 5))

# Plot data
ax.plot(x, y1, label='Pure Sine wave', color='blue', linestyle='-')
ax.plot(x, y2, label='Damped Cosine wave', color='red', linestyle='--')

# Set titles and labels
ax.set_title('Sine and Damped Cosine Waves Example')
ax.set_xlabel('Time [s]')
ax.set_ylabel('Amplitude')

# Add grid and legend
ax.grid(True, which='both', linestyle=':', linewidth=0.5)
ax.legend(loc='upper right')

# Note: The savefig call itself is NOT part of the embedded comment string.
""").strip() # .strip() removes potential leading/trailing blank lines

print("Defined the plot source comment as a string.")

# --- Step 3b: Generate the actual plot using matplotlib ---
# You must run the plotting commands to create the Figure and Axes objects
# in memory before you can save them.
print("Generating the matplotlib plot objects...")

# Sample data (same as in the string above)
x = np.linspace(0, 10, 100)
y1 = np.sin(x)
y2 = np.cos(x) * np.exp(-x/5) # Damped cosine

# Create figure and axes (using the object-oriented API)
fig, ax = plt.subplots(figsize=(8, 5))

# Plot data
ax.plot(x, y1, label='Pure Sine wave', color='blue', linestyle='-')
ax.plot(x, y2, label='Damped Cosine wave', color='red', linestyle='--')

# Set titles and labels
ax.set_title('Sine and Damped Cosine Waves Example')
ax.set_xlabel('Time [s]')
ax.set_ylabel('Amplitude')

# Add grid and legend
ax.grid(True, which='both', linestyle=':', linewidth=0.5)
ax.legend(loc='upper right')

print("Matplotlib plot objects created.")

print("-" * 40)
print("Step 4: Saving the plot with embedded metadata")

# --- Step 4: Save the plot using the hooked savefig ---
output_image_filename = 'example_plot_with_metadata.png'

print(f"Saving plot to '{output_image_filename}'...")

# Call the savefig method on the figure object (or use plt.savefig if it's the current figure).
# The imageforllm hook intercepts this call.
# Pass the 'create_comment' keyword argument with your plot's source comment string.
# imageforllm will also automatically extract basic plot properties (titles, labels, etc.)
# and embed them alongside the comment string (primarily for PNG format when saving to a file path).
try:
    fig.savefig(output_image_filename,
                create_comment=plot_source_create_comment, # Embed the comment string
                bbox_inches='tight',                  # Optional: adjust layout
                format='png')                         # Optional: explicitly set format (PNG is recommended for metadata)

    print(f"Plot successfully saved to '{output_image_filename}' with embedded metadata.")

except Exception as e:
    print(f"Error during plot saving: {e}")
    print("Saving failed. No metadata was embedded.")
    # Note: In a real application, you might want more detailed error handling here.

print("-" * 40)
print("Step 5: Reading the metadata back from the image file")

# --- Step 5: Read metadata from the saved image file ---
print(f"Attempting to read metadata from '{output_image_filename}'...")

# Check if the file was actually created
if not os.path.exists(output_image_filename):
    print(f"Output file '{output_image_filename}' was not found. Cannot read metadata.")
else:
    try:
        # Use imageforllm.get_image_info to extract the embedded metadata.
        extracted_metadata = imageforllm.get_image_info(output_image_filename)

        if extracted_metadata:
            print("\n--- Successfully Extracted Metadata ---")

            # The metadata is returned as a dictionary.
            # The source comment is stored under imageforllm.METADATA_KEY_COMMENT.
            source_comment = extracted_metadata.get(imageforllm.METADATA_KEY_COMMENT)
            if source_comment:
                print(f"\nEmbedded Source Comment (Key: '{imageforllm.METADATA_KEY_COMMENT}'):")
                print(source_comment)
                print("-" * 20)
            else:
                print("\nNo source comment metadata found (was 'create_comment' provided during save?).")

            # Auto-extracted plot properties are stored under imageforllm.METADATA_KEY_PROPERTIES.
            plot_properties = extracted_metadata.get(imageforllm.METADATA_KEY_PROPERTIES)
            if plot_properties:
                print(f"\nAutomatically Extracted Plot Properties (Key: '{imageforllm.METADATA_KEY_PROPERTIES}'):")
                # Print the properties dictionary in a readable JSON format
                print(json.dumps(plot_properties, indent=2))
                print("-" * 20)
            else:
                 print("\nNo automatic plot properties metadata found (metadata embedding might have failed).")

            print("--- End of Extracted Metadata ---")

        else:
            print(f"No imageforllm metadata found in '{output_image_filename}'.")
            print("(This is expected if the file was not saved correctly with the hook/metadata enabled).")

    except Exception as e:
        print(f"Error during metadata extraction: {e}")
        # Note: get_image_info already includes basic internal error handling
        # and warnings, but this catches errors outside of that.

print("-" * 40)
print("Step 6: Cleaning up")

# --- Step 6: Unhook savefig and close the figure ---
# Good practice: restore the original savefig function if you're done.
# Close the figure to free up memory.
try:
    imageforllm.unhook_image_save()
    print("matplotlib.pyplot.savefig hook removed.")
except Exception:
     # Unhooking should generally not fail, but handle defensively
     print("Warning: Failed to unhook matplotlib.pyplot.savefig.")

try:
    plt.close(fig)
    print("Figure closed.")
except Exception:
    # Handle case where fig might not have been created if earlier steps failed
    pass

print("-" * 40)
print("Example script finished.")
print(f"Check the generated file: {output_image_filename}")