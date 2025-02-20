#!/usr/bin/env python3

import json
import sys
from datetime import datetime

"""
Joins two JSON arrays into a single JSON array.
"""

verbose = False
max_records = 0

def loggy(message: str):
    """
    Prints a log message tpo stderr when verbose is enabled.
    """
    if verbose:
        print(f"# {message}",file=sys.stderr)

def join_json_arrays(left_array: str, right_array: str, key: str, result: str):
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
    :param right_array: JSON array used to make the index on 'key'
    :param key: The JSON key on which to form the index
    :param result: Filename where the JSON should be written.
    :return: nothing
    """

    loggy("-----------------------------------------------------------")
    loggy("join_json_arrays()")
    loggy("")

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

    print(f"Joined {len(joined_records)} records.",file=sys.stderr)



def convert_iso_to_unix(iso_string):
    """Converts an ISO 8601 formatted string to a Unix timestamp."""
    try:
        time_format = "%Y-%m-%dT%H:%M:%S%z"
        dt = datetime.strptime(iso_string, time_format) #Handle Z timezones
        unix_timestamp = dt.timestamp()
        return int(unix_timestamp) #return as an integer.
    except ValueError as e:
        print(f"Error: Invalid ISO 8601 format: {e}", file=sys.stderr)
        return None  # Or raise the exception, depending on your needs.
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        return None


request_type="request"
info_type="info"
error_type="error"
verbose_type="verbose"
timing_type="timing"

def join_olfs_metrics_log_with_bes_application_log_entries(
        olfs_metrics: str,
        bes_application_log: str,
        out_file: str):
    """
    For two arrays of JSON records, build an index from the 'right_array' based on the
    JSON key 'right_key'. Then scan the records in 'left_array' for records using 'key' and join those
    with the matching records from 'right.'

    Assumptions: The 'left' array contains records that _always_ contains the 'key' and
    each instance is unique. Similarly, while not every record in 'right' has 'key,' the
    instances of 'key' are also unique in 'right.'

    :note: Make this return the merged document and let the caller decide if it should
    be written to a file or used differently.

    :param bes_log_msg_type: The hyrax-type of log messages to join
    :param olfs_metrics: JSON array to merge
    :param left_key: The JSON key name on which to form the index for the left array
    :param right_array: JSON array used to make the index on 'key'
    :param right_key: The JSON key name on which to form the index for the right array
    :param out_file: Filename where the JSON should be written.
    :return: nothing
    """
    olfs_metrics_request_id_key = "request_id"
    bes_log_request_id_key = "hyrax-request-id"


    loggy("-----------------------------------------------------------")
    loggy("join_bes_json_log_entries()")
    loggy("")
    loggy(f"                  olfs_metrics: {olfs_metrics}")
    loggy(f"   olfs_metrics_request_id_key: {olfs_metrics_request_id_key}")
    loggy("")
    loggy(f"                       bes_log: {bes_application_log}")
    loggy(f"        bes_log_request_id_key: {bes_log_request_id_key}")
    loggy("")
    loggy(f"                      out_file: {out_file}")
    loggy("")

    # Load the OLFS Metrics JSON array (e.g., job details)
    with open(olfs_metrics, 'r') as f:
        olfs_metrics_records = json.load(f)
    #loggy(f"olfs_metrics_records: {olfs_metrics_records}")

    # Load the BES Application Log JSON array (e.g., user details)
    with open(bes_application_log, 'r') as f:
        bes_log_records = json.load(f)
    #loggy(f"bes_log_records: {bes_log_records}")

    # Build an index (a dictionary) from the BES Application Log  records using bes_log_request_id_key as the key
    bes_application_log_index = {record.get(bes_log_request_id_key,""): record for record in bes_log_records if record.get("hyrax-type","") == request_type}

    # Iterate over the records in olfs_metrics_records,
    # merge each with the corresponding bes_log_records record(s), a BES application
    # log record is found with a matching request id.
    joined_records = []
    rec_num=0
    matched_records=0
    for olfs_record in olfs_metrics_records:
        rec_num+=1
        loggy(f"-- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --")
        #loggy(f"olfs_record: {olfs_record}")
        # Lookup the matching record; if none, use an empty dict
        metrics_request_id = olfs_record.get(olfs_metrics_request_id_key, {})
        if metrics_request_id:
            loggy(f"olfs_record has \"{olfs_metrics_request_id_key}\": {metrics_request_id}")
            bes_log_record = bes_application_log_index.get(metrics_request_id, {})
            if len(bes_log_record) > 0:
                #loggy(f"bes_log_record: {bes_log_record}")
                pid = bes_log_record.get("hyrax-pid","")
                instance_id = bes_log_record.get("hyrax-instance-id","")
                bes_start_time = int(bes_log_record.get("hyrax-time",0))
                loggy(f"pid: {pid} instance_id: {instance_id} bes_start_time: {bes_start_time}")

                # What time was the request completed?
                # From the olfs_record we get the value of the "time_completed" key
                # The value is formatted as:  YYYY-MM-DDTHH:MM:SSZ ("2025-02-14T07:00:05+0000")
                end_time_str = olfs_record.get("time_completed","" )
                end_time = bes_start_time
                if end_time_str != "":
                    end_time = convert_iso_to_unix(end_time_str)

                related_bes_entries = [
                    record for record in bes_log_records
                    if record.get("hyrax-instance-id", "") == instance_id and
                       record.get("hyrax-pid", "") == pid and
                       record.get("hyrax-type", "") != request_type and
                       bes_start_time <= int(record.get("hyrax-time", bes_start_time))  <= end_time
                ]
                #loggy(f"Located {len(other_stuff)} other records for pid: {pid} on instance: {instance_id}")
                loggy(f"Found {len(related_bes_entries)} related_bes_entries for pid: {pid} on instance: {instance_id} .")

                joined = {**olfs_record, "bes": {request_type:{**bes_log_record}, "related_bes_entries": related_bes_entries }}
                joined_records.append(joined)
                matched_records +=1

            else:
                loggy(f"Failed to locate the bes_application_log_key: {bes_log_request_id_key} with value: {metrics_request_id} in the bes_application_log_index.")
                joined_records.append(olfs_record)
        else:
            loggy(f"Failed to locate key {olfs_metrics_request_id_key} in olfs_record: {olfs_record}")


        # loggy(f"Completed Record {rec_num}, matched: {matched_records}")
        if max_records!=0 and rec_num >=max_records:
            break

    # Write the result to a new file or print it
    with open(out_file, 'w') as f:
        json.dump(joined_records, f, indent=2)

    print(f"Processed {len(joined_records)} records. Joined {matched_records} records.",file=sys.stderr)


def main():
    global verbose;
    import argparse
    parser = argparse.ArgumentParser(description="Given two json arrays, joi them using a common key and store them "
                                                 "in a file.")
    parser.add_argument("-v", "--verbose",
                        help="Increase output verbosity.",
                        action="store_true")

    parser.add_argument("-l", "--left_array",
                        help="The 'left' json array (table)",
                        default="hyrax_request_log.json")

    parser.add_argument("-r", "--right_array",
                        help="The 'right' json array (table)",
                        default="hyrax_response_log.json")

    parser.add_argument("-k", "--left_key",
                        help="Left array key for merge",
                        default="request_id")

    parser.add_argument("-i", "--right_key",
                        help="Right array key for merge",
                        default="hyrax-request-id")

    parser.add_argument("-o", "--output",
                        help="Output file name.",
                        default="merged.json")


    args = parser.parse_args()
    verbose=args.verbose

    loggy(f"verbose: {verbose}")
    loggy(f"args: {args}")

    if args.left_key == args.right_key:
        join_json_arrays(args.left_array, args.right_array, args.left_key, args.output)
    else:
        join_olfs_metrics_log_with_bes_application_log_entries(args.left_array, args.left_key, args.right_array, args.right_key, args.output)

    print(f"Data extracted and saved to {args.output}",file=sys.stderr)


if __name__ == "__main__":
    main()
