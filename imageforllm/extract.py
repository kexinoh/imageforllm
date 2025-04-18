#!/usr/bin/env python3
"""
Command-line tool to extract comment and plot properties embedded in images created with imageforllm
"""

import argparse
import sys
import os
import json
from ._metadata import (
    get_image_info, get_all_metadata_json, extract_ai_metadata,
    METADATA_KEY_COMMENT, METADATA_KEY_PROPERTIES,
    METADATA_KEY_AI_MODEL, METADATA_KEY_PROMPT, METADATA_KEY_PARAMETERS
)

def main():
    """Main entry point for the command-line tool."""
    parser = argparse.ArgumentParser(
        description="Extract comment and plot properties embedded in images created with imageforllm"
    )
    parser.add_argument(
        "image_file", 
        help="Path to the image file containing embedded metadata"
    )
    parser.add_argument(
        "-o", "--output", 
        help="Output file to save the extracted comment (default: print to stdout)"
    )
    parser.add_argument(
        "-i", "--info", 
        action="store_true",
        help="Print all metadata, not just the comment"
    )
    parser.add_argument(
        "-p", "--properties",
        action="store_true",
        help="Print only the plot properties metadata"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output metadata in JSON format"
    )
    parser.add_argument(
        "--ai",
        action="store_true",
        help="Print only the AI generation metadata"
    )
    
    args = parser.parse_args()
    
    # Check if the file exists
    if not os.path.isfile(args.image_file):
        print(f"Error: File '{args.image_file}' does not exist", file=sys.stderr)
        sys.exit(1)
    
    # Get the metadata from the image
    info = get_image_info(args.image_file)
    
    if not info:
        print(f"No metadata found in '{args.image_file}'", file=sys.stderr)
        sys.exit(1)
    
    # Handle output based on flags
    if args.json:
        # JSON output format
        if args.info:
            output_data = get_all_metadata_json(args.image_file)
        elif args.properties:
            if 'plot_properties' in info or METADATA_KEY_PROPERTIES in info:
                output_data = info.get('plot_properties', info.get(METADATA_KEY_PROPERTIES, {}))
            else:
                print(f"No plot properties found in '{args.image_file}'", file=sys.stderr)
                sys.exit(1)
        elif args.ai:
            ai_data = extract_ai_metadata(args.image_file)
            if ai_data:
                output_data = ai_data
            else:
                print(f"No AI metadata found in '{args.image_file}'", file=sys.stderr)
                sys.exit(1)
        else:
            # Default is comment
            if 'source_comment' in info or METADATA_KEY_COMMENT in info:
                output_data = {'comment': info.get('source_comment', info.get(METADATA_KEY_COMMENT, ""))}
            else:
                print(f"No comment found in '{args.image_file}'", file=sys.stderr)
                sys.exit(1)
        
        # Format and output the JSON
        json_str = json.dumps(output_data, indent=2)
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(json_str)
        else:
            print(json_str)
    else:
        # Plain text output format
        if args.info:
            # Print all metadata
            if args.output:
                with open(args.output, "w", encoding="utf-8") as f:
                    for key, value in info.items():
                        if isinstance(value, dict):
                            f.write(f"{key}:\n{json.dumps(value, indent=2)}\n\n")
                        else:
                            f.write(f"{key}: {value}\n\n")
            else:
                for key, value in info.items():
                    if isinstance(value, dict):
                        print(f"{key}:")
                        print(json.dumps(value, indent=2))
                        print()
                    else:
                        print(f"{key}: {value}\n")
        elif args.properties:
            # Print just the plot properties
            properties = info.get('plot_properties', info.get(METADATA_KEY_PROPERTIES, None))
            if not properties:
                print(f"No plot properties found in '{args.image_file}'", file=sys.stderr)
                sys.exit(1)
                
            if args.output:
                with open(args.output, "w", encoding="utf-8") as f:
                    f.write(json.dumps(properties, indent=2))
            else:
                print(json.dumps(properties, indent=2))
        elif args.ai:
            # Print just the AI metadata
            ai_metadata = extract_ai_metadata(args.image_file)
            if not ai_metadata:
                print(f"No AI metadata found in '{args.image_file}'", file=sys.stderr)
                sys.exit(1)
                
            if args.output:
                with open(args.output, "w", encoding="utf-8") as f:
                    f.write(json.dumps(ai_metadata, indent=2))
            else:
                print(json.dumps(ai_metadata, indent=2))
        else:
            # Print just the comment (default)
            comment = info.get('source_comment', info.get(METADATA_KEY_COMMENT, None))
            if not comment:
                print(f"No comment found in '{args.image_file}'", file=sys.stderr)
                sys.exit(1)
                
            if args.output:
                with open(args.output, "w", encoding="utf-8") as f:
                    f.write(comment)
            else:
                print(comment)
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 