#!/usr/bin/env python3
"""
Command-line tool to add AI generation metadata to image files
"""

import argparse
import sys
import os
import json
from ._metadata import add_ai_metadata

def main():
    """Main entry point for the AI metadata command-line tool."""
    parser = argparse.ArgumentParser(
        description="Add AI generation metadata to image files"
    )
    parser.add_argument(
        "image_file", 
        help="Path to the image file to add metadata to"
    )
    parser.add_argument(
        "--model", 
        required=True,
        help="Name or version of the AI model used to generate the image"
    )
    parser.add_argument(
        "--prompt",
        required=True,
        help="Text prompt used to generate the image"
    )
    parser.add_argument(
        "--parameters",
        help="JSON string of additional parameters used for generation (e.g., seeds, styles)"
    )
    
    args = parser.parse_args()
    
    # Check if the file exists
    if not os.path.isfile(args.image_file):
        print(f"Error: File '{args.image_file}' does not exist", file=sys.stderr)
        sys.exit(1)
    
    # Parse parameters if provided
    parameters = None
    if args.parameters:
        try:
            parameters = json.loads(args.parameters)
        except json.JSONDecodeError:
            print(f"Error: Parameters must be a valid JSON string", file=sys.stderr)
            sys.exit(1)
    
    # Add metadata
    success = add_ai_metadata(args.image_file, args.model, args.prompt, parameters)
    
    if success:
        print(f"Successfully added AI metadata to '{args.image_file}'")
        return 0
    else:
        print(f"Failed to add AI metadata to '{args.image_file}'", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main()) 