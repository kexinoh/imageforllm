"""
Metadata handling for ImageForLLM

This module provides functions for embedding and extracting metadata from images.
"""

import io
import os
import json
import warnings
from PIL import Image, PngImagePlugin

# Define unique keys for our metadata
METADATA_KEY_CODE = "imageforllm:source_code"
METADATA_KEY_PROPERTIES = "imageforllm:plot_properties"

def _embed_metadata_in_png(image_bytes_io, output_path, metadata_dict):
    """
    Internal function to embed a dictionary of metadata into a PNG image.
    
    Args:
        image_bytes_io (io.BytesIO): BytesIO object containing the image data
        output_path (str): Path where the image with metadata will be saved
        metadata_dict (dict): Dictionary with metadata to embed
    """
    try:
        image_bytes_io.seek(0)
        img = Image.open(image_bytes_io)

        if img.format != 'PNG':
            warnings.warn(
                f"Metadata embedding is primarily supported for PNG format. "
                f"The image format is {img.format}. Metadata will not be embedded."
            )
            image_bytes_io.seek(0)
            with open(output_path, 'wb') as f:
                f.write(image_bytes_io.read())
            return

        # Create PNG info object with existing metadata if present
        pnginfo = PngImagePlugin.PngInfo()
        
        # Convert all metadata values to strings for compatibility
        stringified_metadata = {str(k): str(v) if not isinstance(v, dict) else json.dumps(v) 
                               for k, v in metadata_dict.items()}

        try:
            # Store as JSON string under a single key
            pnginfo.add_text("imageforllm:metadata", json.dumps(stringified_metadata))
            
            # For backwards compatibility, also store individual keys
            for k, v in stringified_metadata.items():
                pnginfo.add_text(k, v)
                
        except Exception as json_e:
            warnings.warn(f"Failed to encode metadata as JSON: {json_e}. Attempting to embed as simple strings.")
            for k, v in stringified_metadata.items():
                try:
                    pnginfo.add_text(k, v)
                except Exception as e:
                    warnings.warn(f"Failed to embed metadata key {k}: {e}")

        # Save the image with metadata
        img.save(output_path, format='PNG', pnginfo=pnginfo)

    except Exception as e:
        warnings.warn(f"Failed to embed metadata into {output_path}: {e}. Saving image without metadata.")
        try:
            image_bytes_io.seek(0)
            with open(output_path, 'wb') as f:
                f.write(image_bytes_io.read())
        except Exception as e_fallback:
            warnings.warn(f"Fallback saving also failed for {output_path}: {e_fallback}")
    finally:
        if 'img' in locals() and img:
            img.close()

def _extract_plot_properties(fig):
    """
    Extract basic properties from a matplotlib Figure object.
    
    Args:
        fig: A matplotlib Figure object
        
    Returns:
        dict: A dictionary of plot properties
    """
    properties = {}
    try:
        # Import matplotlib here to avoid circular imports
        import matplotlib
        
        # Figure level properties - Fix suptitle handling method
        # In some cases, fig.suptitle may be a method rather than an object, so it needs to be handled safely
        if hasattr(fig, '_suptitle') and fig._suptitle is not None:
            # Use _suptitle attribute (internal attribute) to directly get the title object
            if hasattr(fig._suptitle, 'get_text'):
                properties['figure_title'] = fig._suptitle.get_text()
            elif hasattr(fig._suptitle, 'get_label'):
                properties['figure_title'] = fig._suptitle.get_label()
        elif hasattr(fig, 'get_suptitle'):
            # Use get_suptitle method to get the title text
            suptitle_text = fig.get_suptitle()
            if suptitle_text:
                properties['figure_title'] = suptitle_text

        # Axis level properties
        axes_properties = []
        for i, ax in enumerate(fig.get_axes()):
            ax_props = {
                'index': i,
                'title': ax.get_title(),
                'xlabel': ax.get_xlabel(),
                'ylabel': ax.get_ylabel(),
                'type': type(ax).__name__,  # e.g., 'Axes', 'Axes3D'
                'xlim': str(ax.get_xlim()),
                'ylim': str(ax.get_ylim()),
                'has_grid': bool(ax.get_xgridlines() or ax.get_ygridlines()),
                'has_legend': ax.get_legend() is not None,
            }

            # Extract info about artists (lines, patches, etc.)
            artists_info = []
            
            # Process Line2D objects (regular plots)
            for line in ax.get_lines():
                artist_info = {
                    'type': 'Line2D',
                    'label': line.get_label(),
                    'color': str(line.get_color()),
                    'linestyle': line.get_linestyle(),
                    'marker': line.get_marker()
                }
                # Don't include actual data points to keep metadata manageable
                artists_info.append(artist_info)
                
            # Process other common artist types
            for artist in ax.get_children():
                # Skip Line2D objects already processed
                if isinstance(artist, matplotlib.lines.Line2D):
                    continue
                    
                if isinstance(artist, matplotlib.collections.PathCollection):  # scatter plots
                    artists_info.append({
                        'type': 'PathCollection', 
                        'label': artist.get_label() if hasattr(artist, 'get_label') else None
                    })
                elif isinstance(artist, matplotlib.patches.Rectangle):  # bars, hist bars
                    artists_info.append({
                        'type': 'Rectangle', 
                        'label': artist.get_label() if hasattr(artist, 'get_label') else None
                    })
                elif isinstance(artist, matplotlib.collections.QuadMesh):  # heatmaps, imshow
                    artists_info.append({
                        'type': 'QuadMesh',
                        'label': 'heatmap/image'
                    })

            if artists_info:
                ax_props['artists'] = artists_info

            axes_properties.append(ax_props)

        if axes_properties:
            properties['axes'] = axes_properties

    except Exception as e:
        warnings.warn(f"Failed to automatically extract plot properties: {e}")
        properties = {}  # Return empty properties if extraction fails

    return properties

def get_image_info(image_path):
    """
    Extracts metadata embedded by imageforllm from an image file.

    Args:
        image_path: The path to the image file.

    Returns:
        A dictionary containing extracted metadata. Returns an empty
        dictionary if the file is not found, not an image, or contains
        no imageforllm metadata.
        The source code, if found, will be under the key 'source_code'.
        Automatically extracted plot properties, if found, will be under
        the key 'plot_properties'.
    """
    metadata = {}
    img = None
    try:
        if not os.path.exists(image_path):
            warnings.warn(f"Image file not found: {image_path}")
            return metadata

        img = Image.open(image_path)

        if img.format == 'PNG' and img.info:
            # Try to load the combined JSON metadata first
            if "imageforllm:metadata" in img.info:
                try:
                    loaded_metadata = json.loads(img.info["imageforllm:metadata"])
                    # Update the main metadata dictionary with loaded data
                    metadata.update(loaded_metadata)
                except json.JSONDecodeError:
                    warnings.warn(f"Failed to decode JSON metadata from {image_path}.")
                except Exception as e_load:
                    warnings.warn(f"Error processing JSON metadata from {image_path}: {e_load}")

            # Fallback/Compatibility: Check for old simple keys
            if METADATA_KEY_CODE in img.info and 'source_code' not in metadata:
                metadata['source_code'] = img.info[METADATA_KEY_CODE]
                
            # For backwards compatibility, support the old 'code' key too
            if 'imageforllm' in img.info and 'source_code' not in metadata:
                try:
                    legacy_info = json.loads(img.info['imageforllm'])
                    if 'code' in legacy_info:
                        metadata['source_code'] = legacy_info['code']
                except (json.JSONDecodeError, TypeError):
                    pass

            if METADATA_KEY_PROPERTIES in img.info and 'plot_properties' not in metadata:
                try:
                    metadata['plot_properties'] = json.loads(img.info[METADATA_KEY_PROPERTIES])
                except (json.JSONDecodeError, TypeError):
                    metadata['plot_properties'] = img.info[METADATA_KEY_PROPERTIES]

        else:
            warnings.warn(f"Metadata extraction currently fully supported only for PNG with embedded info. Image format is {img.format}.")

    except FileNotFoundError:
        warnings.warn(f"Image file not found during metadata extraction: {image_path}")
    except Exception as e:
        warnings.warn(f"Error opening or reading metadata from image {image_path}: {e}")
    finally:
        if img:
            img.close()

    return metadata

# Expose public functions
__all__ = ['get_image_info', 'METADATA_KEY_CODE', 'METADATA_KEY_PROPERTIES'] 