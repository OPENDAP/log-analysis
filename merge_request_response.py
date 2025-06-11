#!/usr/bin/env python3

"""
Merge two JSON files that share a field named 'request_id' using that field's
value as an index.
"""

import json

def merge_json_files(file1_path, file2_path, output_path):
    """
    Merges two JSON files based on the 'request_id' field.

    Args:
        file1_path (str): Path to the first JSON file.
        file2_path (str): Path to the second JSON file.
        output_path (str): Path to the output JSON file.
    """

    try:
        with open(file1_path, 'r') as f1, open(file2_path, 'r') as f2:
            data1 = json.load(f1)
            data2 = json.load(f2)

        # Create a dictionary for quick lookup from data2
        data2_dict = {item['request_id']: item for item in data2}

        merged_data = []
        for item1 in data1:
            request_id = item1['request_id']
            if request_id in data2_dict:
                # Merge the dictionaries
                merged_item = {**item1, **data2_dict[request_id]}
                merged_data.append(merged_item)
            else:
                merged_data.append(item1)  # Keep item1 if no match in data2

        with open(output_path, 'w') as output_file:
            json.dump(merged_data, output_file, indent=2)

        print(f"Merged data written to {output_path}")

    except FileNotFoundError:
        print("One or both input files not found.")
    except json.JSONDecodeError:
        print("Invalid JSON format in one or both input files.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage:
file1_path = 'request_log.json'  # Replace with your file paths
file2_path = 'response_log.json'
output_path = 'merged_request_response.json'

merge_json_files(file1_path, file2_path, output_path)
