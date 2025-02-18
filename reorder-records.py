#!/usr/bin/env python3
#
# reorder-records.py: Reorder fields in JSON records

import json
import argparse

def reorder_json_fields(input_file, output_file):
    # Specify the fields to reorder
    priority_fields = ["hyrax-time", "hyrax-instance-id", "hyrax-pid", "hyrax-type"]

    # Load the JSON log file
    with open(input_file, 'r') as file:
        records = json.load(file)

    # Reorder fields in each record
    reordered_records = []
    for record in records:
        reordered_record = {field: record[field] for field in priority_fields if field in record}
        reordered_record.update({k: v for k, v in record.items() if k not in priority_fields})
        reordered_records.append(reordered_record)

    # Write the reordered JSON records back to a file
    with open(output_file, 'w') as file:
        json.dump(reordered_records, file, indent=4)

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Reorder JSON log fields.")
    parser.add_argument("-i", "--input", required=True, help="Input JSON file")
    parser.add_argument("-o", "--output", default="reordered_logs.json", help="Output JSON file (default: reordered_logs.json)")

    # Parse arguments
    args = parser.parse_args()

    # Reorder the JSON fields
    reorder_json_fields(args.input, args.output)
    print(f"Reordered logs saved to {args.output}")

if __name__ == "__main__":
    main()
