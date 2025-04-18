"""
Hook functionality for ImageForLLM

This module provides functions for hooking and unhooking matplotlib's savefig function.
"""

import io
import os
import functools
import warnings
import matplotlib.pyplot as plt

# Import metadata functions
from ._metadata import _embed_metadata_in_png, _extract_plot_properties
from ._metadata import METADATA_KEY_COMMENT, METADATA_KEY_PROPERTIES

# Global variables to track the hook state
_original_savefig = None
_is_hooked = False

def _savefig_with_metadata(fig, fname, *args, create_comment=None, **kwargs):
    """
    Replacement for matplotlib.pyplot.savefig that embeds metadata.
    
    Args:
        fig: A matplotlib Figure object
        fname: The path or file-like object to save the figure to
        create_comment: Optional string containing the source code used to generate the plot
        *args, **kwargs: Other arguments to pass to the original savefig function
        
    Returns:
        The result of the original savefig function
    """
    global _original_savefig
    
    if not _original_savefig:
        warnings.warn("Original savefig function not found. Hook may not be properly installed.")
        return plt.gcf().savefig(fname, *args, **kwargs)
    
    # Remove create_comment parameter from kwargs to avoid passing it to the underlying function
    if 'create_comment' in kwargs:
        create_comment = kwargs.pop('create_comment')

    # Handle file-like objects
    if hasattr(fname, 'write'):
        warnings.warn("Metadata embedding is not supported for file-like objects. Falling back to original savefig.")
        return _original_savefig(fig, fname, *args, **kwargs)
    
    # Check if fname is empty
    if fname is None:
        warnings.warn("Missing filename (fname) for savefig. Cannot save image.")
        return _original_savefig(fig, fname, *args, **kwargs)
    
    # Determine output format
    format = kwargs.get('format', None)
    if format is None and isinstance(fname, str):
        # Try to infer format from filename
        _, ext = os.path.splitext(fname)
        if ext:
            format = ext[1:]  # Remove the dot
        else:
            format = 'png'  # Default to png
    
    if format and format.lower() != 'png':
        warnings.warn(f"Metadata embedding is only fully supported for PNG format, not {format}. Saving without metadata.")
        return _original_savefig(fig, fname, *args, **kwargs)
    
    # Prepare metadata dictionary
    metadata_to_embed = {}
    
    # 1. Add user-provided create_comment (if any)
    if create_comment is not None:
        metadata_to_embed[METADATA_KEY_COMMENT] = str(create_comment)
    
    # 2. Automatically extract plot properties
    try:
        plot_properties = _extract_plot_properties(fig)
        if plot_properties:
            metadata_to_embed[METADATA_KEY_PROPERTIES] = plot_properties
    except Exception as e:
        warnings.warn(f"Failed to extract plot properties: {e}")
    
    # If no metadata to embed, just call the original function
    if not metadata_to_embed:
        warnings.warn("No metadata to embed. Using original savefig.")
        return _original_savefig(fig, fname, *args, **kwargs)
    
    # Save to a buffer first
    buffer = io.BytesIO()
    result = _original_savefig(fig, buffer, *args, **kwargs)
    
    # Embed metadata and save to final destination
    try:
        _embed_metadata_in_png(buffer, fname, metadata_to_embed)
    except Exception as e:
        warnings.warn(f"Failed to embed metadata: {e}. Falling back to original savefig.")
        buffer.seek(0)
        with open(fname, 'wb') as f:
            f.write(buffer.read())
    finally:
        buffer.close()
    
    return result

def hook_image_save():
    """
    Hooks matplotlib's savefig function to embed code metadata.

    The hooked savefig function accepts all original arguments plus an
    additional optional keyword argument:
    create_comment: A string containing the source code used to generate the plot.
                 If provided, this code will be embedded in the image metadata.

    Automatically extracts basic plot properties and embeds them if possible.
    Metadata embedding currently works reliably only for PNG files when saving to a file path.

    Requires Pillow to be installed.
    """
    global _original_savefig, _is_hooked
    
    if _is_hooked:
        warnings.warn("matplotlib.pyplot.savefig is already hooked by imageforllm.")
        return
    
    try:
        from PIL import Image  # noqa: F401
    except ImportError:
        raise ImportError(
            "Pillow is required for imageforllm metadata embedding. "
            "Please install it (`pip install Pillow`)."
        )
    
    # Store the original function
    _original_savefig = plt.Figure.savefig
    
    # Create a wrapper function to capture and handle the create_comment parameter
    @functools.wraps(_original_savefig)
    def wrapper(self, *args, **kwargs):
        """Modified savefig method that supports the create_comment parameter"""
        # Extract create_comment parameter if present
        create_comment = kwargs.pop('create_comment', None)
        
        # Ensure there is at least one argument (filename)
        if not args and 'fname' not in kwargs:
            warnings.warn("savefig() called without a filename. Cannot embed metadata.")
            return _original_savefig(self, *args, **kwargs)
            
        # Process arguments
        if args:
            fname = args[0]
            new_args = args[1:]
        elif 'fname' in kwargs:
            fname = kwargs.pop('fname')
            new_args = ()
        else:
            # This shouldn't happen, but just in case
            return _original_savefig(self, *args, **kwargs)
            
        # Call our metadata embedding function without passing create_comment as kwargs
        return _savefig_with_metadata(self, fname, *new_args, create_comment=create_comment, **kwargs)
    
    # Replace plt.Figure.savefig
    plt.Figure.savefig = wrapper
    
    # Wrap plt.savefig
    plt_savefig_original = plt.savefig
    
    @functools.wraps(plt_savefig_original)
    def plt_savefig_wrapper(*args, **kwargs):
        """Modified plt.savefig function that supports the create_comment parameter"""
        # Extract create_comment parameter
        create_comment = kwargs.pop('create_comment', None)
        
        # Get current figure
        fig = plt.gcf()
        
        # Ensure there is at least one argument (filename)
        if not args and 'fname' not in kwargs:
            warnings.warn("plt.savefig() called without a filename. Cannot embed metadata.")
            return plt_savefig_original(*args, **kwargs)
            
        # Process arguments
        if args:
            fname = args[0]
            new_args = args[1:]
        elif 'fname' in kwargs:
            fname = kwargs.pop('fname')
            new_args = ()
        else:
            # This shouldn't happen, but just in case
            return plt_savefig_original(*args, **kwargs)
            
        # Call the figure object's savefig method which has now been replaced by our wrapper
        return fig.savefig(fname, *new_args, create_comment=create_comment, **kwargs)
    
    # Replace plt.savefig
    plt.savefig = plt_savefig_wrapper
    
    _is_hooked = True
    
    print("Successfully hooked matplotlib's savefig function.")

def unhook_image_save():
    """
    Restores the original matplotlib.pyplot.savefig function.
    """
    global _original_savefig, _is_hooked
    
    if not _is_hooked:
        warnings.warn("imageforllm hook is not active.")
        return
    
    if _original_savefig is not None:
        # Restore Figure.savefig
        plt.Figure.savefig = _original_savefig
        
        # Try to restore plt.savefig
        try:
            # Create a function using Figure.savefig to replace plt.savefig
            @functools.wraps(_original_savefig)
            def restored_plt_savefig(*args, **kwargs):
                fig = plt.gcf()
                return fig.savefig(*args, **kwargs)
            
            plt.savefig = restored_plt_savefig
        except Exception as e:
            warnings.warn(f"Failed to restore plt.savefig: {e}")
        
        _original_savefig = None
        _is_hooked = False
        
        print("Successfully unhooked matplotlib's savefig function.")

# Expose public functions
__all__ = ['hook_image_save', 'unhook_image_save'] 