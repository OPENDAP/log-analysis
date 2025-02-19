#!/usr/bin/env python3

import json

verbose = False
max_records = 0

"""
Joins two JSON arrays into a single JSON array.
"""
def loggy(message: str):
    if verbose:
        print(f"# {message}")


def join_json_arrays(left_array: str, left_key: str, right_array: str, right_key: str, out_file: str):
    """
    For two arrays of JSON records, build an index from the 'right' array based on the
    JSON key 'key'. Then scan the records in 'left' for records using 'key' and join those
    with the matching records from 'right.'

    Assumptions: The 'left' array contains records that _always_ contains the 'key' and
    each instance is unique. Similarly, while not every record in 'right' has 'key,' the
    instances of 'key' are also unique in 'right.'

    :note: Make this return the merged document and let the caller decide if it should
    be written to a file or used differently.

    :param left_array: JSON array to merge
    :param left_key: The JSON key on which to form the index for the left array
    :param right_array: JSON array used to make the index on 'key'
    :param right_key: The JSON key on which to form the index for the right array
    :param out_file: Filename where the JSON should be written.
    :return: nothing
    """
    loggy(f"  left_array: {left_array}")
    loggy(f"    left_key: {left_key}")
    loggy(f"")
    loggy(f" right_array: {right_array}")
    loggy(f"   right_key: {right_key}")
    loggy(f"")
    loggy(f"    out_file: {out_file}")
    loggy(f"")

    # Load the left JSON array (e.g., job details)
    with open(left_array, 'r') as f:
        left_records = json.load(f)

    #loggy(f"left_records: {left_records}")


    # Load the right JSON array (e.g., user details)
    with open(right_array, 'r') as f:
        right_records = json.load(f)
    #loggy(f"right_records: {right_records}")

    # Build an index (a dictionary) from the right records using request_id as the key
    right_index = {record.get(right_key,""): record for record in right_records if record.get("hyrax-type","") == "request"}

    # For each record in the left array, merge it with the corresponding right record (if available)
    joined_records = []
    rec_num=0
    for left_record in left_records:
        rec_num+=1
        # Lookup the matching record; if none, use an empty dict
        left_key_val=left_record.get(left_key,{})
        if left_key_val:
            right_record = right_index.get(left_key_val, {})
            # Merge the two dictionaries (right_rec values will override left_rec on key collisions)
            joined = {**left_record, **right_record}
            joined_records.append(joined)
        else:
            joined_records.append(left_record)

        loggy(f"Completed Record {rec_num}")
        if max_records!=0 and rec_num >=max_records:
            break

    # Write the result to a new file or print it
    with open(out_file, 'w') as f:
        json.dump(joined_records, f, indent=2)

    print(f"Joined {len(joined_records)} records.")


def main():
    global verbose;
    import argparse
    parser = argparse.ArgumentParser(description="Given two json arrays, joi them using a common key and store them "
                                                 "in a file.")
    parser.add_argument("-v", "--verbose", help="Increase output verbosity.", action="store_true")
    parser.add_argument("-l", "--left", help="The 'left' json array (table)",
                        default="hyrax_request_log.json")
    parser.add_argument("-r", "--right", help="The 'right' json array (table)",
                        default="hyrax_response_log.json")
    parser.add_argument("-k", "--leftkey", help="Left array key for merge", default="request_id")
    parser.add_argument("-i", "--rightkey", help="Right array key for merge", default="hyrax-request-id")
    parser.add_argument("-o", "--output", help="Output file name.", default="merged.json")

    args = parser.parse_args()
    verbose=args.verbose
    loggy(f"verbose: {verbose}")
    loggy(f"args: {args}")

    join_json_arrays(args.right, args.rightkey, args.left, args.leftkey,  args.output)

    print(f"Data extracted and saved to {args.output}")


if __name__ == "__main__":
    main()
