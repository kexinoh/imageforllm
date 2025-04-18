#!/usr/bin/env python3
"""
Command-line tool to extract code embedded in images created with imageforllm
"""

import argparse
import sys
import os
import json
from ._metadata import get_image_info, METADATA_KEY_CODE, METADATA_KEY_PROPERTIES

def main():
    """Main entry point for the command-line tool."""
    parser = argparse.ArgumentParser(
        description="Extract code and plot properties embedded in images created with imageforllm"
    )
    parser.add_argument(
        "image_file", 
        help="Path to the image file containing embedded metadata"
    )
    parser.add_argument(
        "-o", "--output", 
        help="Output file to save the extracted code (default: print to stdout)"
    )
    parser.add_argument(
        "-i", "--info", 
        action="store_true",
        help="Print all metadata, not just the code"
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
            output_data = info
        elif args.properties:
            if 'plot_properties' in info or METADATA_KEY_PROPERTIES in info:
                output_data = info.get('plot_properties', info.get(METADATA_KEY_PROPERTIES, {}))
            else:
                print(f"No plot properties found in '{args.image_file}'", file=sys.stderr)
                sys.exit(1)
        else:
            # Default is code
            if 'source_code' in info or METADATA_KEY_CODE in info:
                output_data = {'code': info.get('source_code', info.get(METADATA_KEY_CODE, ""))}
            else:
                print(f"No code found in '{args.image_file}'", file=sys.stderr)
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
        else:
            # Print just the code (default)
            code = info.get('source_code', info.get(METADATA_KEY_CODE, None))
            if not code:
                print(f"No code found in '{args.image_file}'", file=sys.stderr)
                sys.exit(1)
                
            if args.output:
                with open(args.output, "w", encoding="utf-8") as f:
                    f.write(code)
            else:
                print(code)
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 