#!/usr/bin/env python3

import argparse

def add_commas_to_json(input_file, output_file):
    # Read the input file
    with open(input_file, 'r') as file:
        lines = file.readlines()

    # Add commas to lines ending with '}'
    updated_lines = []
    for i, line in enumerate(lines):
        stripped_line = line.strip()
        # Add a comma if the line ends with '}' and it's not the last line
        if stripped_line.endswith('}') and i < len(lines) - 1:
            updated_lines.append(line.rstrip() + ',\n')
        else:
            updated_lines.append(line)

    # Write the updated lines to the output file
    with open(output_file, 'w') as file:
        file.writelines(updated_lines)

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Add commas to JSON lines ending with '}'.")
    parser.add_argument("-i", "--input", required=True, help="Input JSON file")
    parser.add_argument("-o", "--output", default="updated_logs.json", help="Output JSON file (default: updated_logs.json)")

    # Parse arguments
    args = parser.parse_args()

    # Process the file
    add_commas_to_json(args.input, args.output)
    print(f"Updated file with commas saved to {args.output}")

if __name__ == "__main__":
    main()
