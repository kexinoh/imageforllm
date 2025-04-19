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
METADATA_KEY_COMMENT = "imageforllm:source_comment"
METADATA_KEY_PROPERTIES = "imageforllm:plot_properties"
METADATA_KEY_AI_MODEL = "imageforllm:ai_model"
METADATA_KEY_PROMPT = "imageforllm:prompt"
METADATA_KEY_PARAMETERS = "imageforllm:parameters"

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
        The source code, if found, will be under the key 'source_comment'.
        Automatically extracted plot properties, if found, will be under
        the key 'plot_properties'.
        AI model information, if found, will be under keys 'ai_model', 'prompt', 
        and 'parameters'.
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
            if METADATA_KEY_COMMENT in img.info and 'source_comment' not in metadata:
                metadata['source_comment'] = img.info[METADATA_KEY_COMMENT]
                
            # For backwards compatibility, support the old 'code' key too
            if 'imageforllm' in img.info and 'source_comment' not in metadata:
                try:
                    legacy_info = json.loads(img.info['imageforllm'])
                    if 'comment' in legacy_info:
                        metadata['source_comment'] = legacy_info['comment']
                except (json.JSONDecodeError, TypeError):
                    pass

            if METADATA_KEY_PROPERTIES in img.info and 'plot_properties' not in metadata:
                try:
                    metadata['plot_properties'] = json.loads(img.info[METADATA_KEY_PROPERTIES])
                except (json.JSONDecodeError, TypeError):
                    metadata['plot_properties'] = img.info[METADATA_KEY_PROPERTIES]
                    
            # Check for AI-related metadata
            if METADATA_KEY_AI_MODEL in img.info and 'ai_model' not in metadata:
                metadata['ai_model'] = img.info[METADATA_KEY_AI_MODEL]
                
            if METADATA_KEY_PROMPT in img.info and 'prompt' not in metadata:
                metadata['prompt'] = img.info[METADATA_KEY_PROMPT]
                
            if METADATA_KEY_PARAMETERS in img.info and 'parameters' not in metadata:
                try:
                    metadata['parameters'] = json.loads(img.info[METADATA_KEY_PARAMETERS])
                except (json.JSONDecodeError, TypeError):
                    metadata['parameters'] = img.info[METADATA_KEY_PARAMETERS]

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

def add_ai_metadata(image_path, model, prompt, parameters=None):
    """
    Adds AI image generation metadata to an existing image file.
    
    Args:
        image_path: The path to the image file.
        model: The name/version of the AI model used to generate the image.
        prompt: The prompt text used to generate the image.
        parameters: Optional dictionary of additional generation parameters (e.g., seeds, styles).
        
    Returns:
        bool: True if metadata was successfully added, False otherwise.
    """
    img = None
    metadata_dict = {}
    try:
        if not os.path.exists(image_path):
            warnings.warn(f"Image file not found: {image_path}")
            return False
            
        img = Image.open(image_path)
        
        if img.format != 'PNG':
            warnings.warn(f"Metadata embedding is primarily supported for PNG format. The image format is {img.format}.")
            return False
            
        # Prepare metadata
        metadata_dict[METADATA_KEY_AI_MODEL] = model
        metadata_dict[METADATA_KEY_PROMPT] = prompt
        if parameters:
            metadata_dict[METADATA_KEY_PARAMETERS] = parameters
            
        # Save existing metadata if any
        existing_info = {}
        if "imageforllm:metadata" in img.info:
            try:
                existing_info = json.loads(img.info["imageforllm:metadata"])
            except json.JSONDecodeError:
                warnings.warn("Failed to decode existing metadata, will overwrite.")
            except Exception as e:
                warnings.warn(f"Error processing existing metadata: {e}, will overwrite.")
        
        # Update with AI metadata
        existing_info.update(metadata_dict)
        
        # Create temp buffer and save original image
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        
        # Embed updated metadata and save
        _embed_metadata_in_png(buffer, image_path, existing_info)
        
        return True
        
    except Exception as e:
        warnings.warn(f"Failed to add AI metadata to {image_path}: {e}")
        return False
    finally:
        if img:
            img.close()

def extract_ai_metadata(image_path):
    """
    Extracts AI-specific metadata from an image file.
    
    Args:
        image_path: The path to the image file.
        
    Returns:
        dict: A dictionary containing AI metadata (model, prompt, parameters).
              Returns an empty dictionary if no AI metadata is found.
    """
    all_info = get_image_info(image_path)
    ai_metadata = {}
    
    if 'ai_model' in all_info:
        ai_metadata['model'] = all_info['ai_model']
    
    if 'prompt' in all_info:
        ai_metadata['prompt'] = all_info['prompt']
        
    if 'parameters' in all_info:
        ai_metadata['parameters'] = all_info['parameters']
        
    return ai_metadata

def get_all_metadata_json(image_path):
    """
    Extracts all metadata from an image and returns it as a JSON-serializable dictionary.
    
    Args:
        image_path: The path to the image file.
        
    Returns:
        dict: A dictionary containing all metadata, suitable for JSON serialization.
              Returns an empty dictionary if no metadata is found.
    """
    metadata = get_image_info(image_path)
    
    # Convert any complex types to strings for JSON compatibility if needed
    for key, value in metadata.items():
        if not isinstance(value, (str, int, float, bool, dict, list, type(None))):
            metadata[key] = str(value)
            
    return metadata

# Expose public functions
__all__ = ['get_image_info', 'add_ai_metadata', 'extract_ai_metadata', 
           'get_all_metadata_json', 'METADATA_KEY_COMMENT', 
           'METADATA_KEY_PROPERTIES', 'METADATA_KEY_AI_MODEL',
           'METADATA_KEY_PROMPT', 'METADATA_KEY_PARAMETERS'] 