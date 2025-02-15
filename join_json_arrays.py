#!/usr/bin/env python3

import json


"""
Joins two JSON arrays into a single JSON array.
"""


def join_json_arrays(left_array: str, right_array: str, key: str, result: str):
    # Load the left JSON array (e.g., job details)
    with open(left_array, 'r') as f:
        left_records = json.load(f)

    # Load the right JSON array (e.g., user details)
    with open(right_array, 'r') as f:
        right_records = json.load(f)

    # Build an index (a dictionary) from the right records using request_id as the key
    right_index = {record[key]: record for record in right_records}

    # For each record in the left array, merge it with the corresponding right record (if available)
    joined_records = []
    for left_rec in left_records:
        # Lookup the matching record; if none, use an empty dict
        right_rec = right_index.get(left_rec[key], {})
        # Merge the two dictionaries (right_rec values will override left_rec on key collisions)
        joined = {**left_rec, **right_rec}
        joined_records.append(joined)

    # Write the result to a new file or print it
    with open(result, 'w') as f:
        json.dump(joined_records, f, indent=2)

    print(f"Joined {len(joined_records)} records.")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Given two json arrays, joi them using a common key and store them "
                                                 "in a file.")
    parser.add_argument("-v", "--verbose", help="Increase output verbosity.", action="store_true")
    parser.add_argument("-l", "--left", help="The 'left' json array (table)",
                        default="hyrax_request_log.json")
    parser.add_argument("-r", "--right", help="The 'right' json array (table)",
                        default="hyrax_response_log.json")
    parser.add_argument("-k", "--key", help="Common key for merge", default="request_id")
    parser.add_argument("-o", "--output", help="Output file name.", default="merged.json")

    args = parser.parse_args()

    join_json_arrays(args.left, args.right, args.key, args.output)

    print(f"Data extracted and saved to {args.output}")


if __name__ == "__main__":
    main()
