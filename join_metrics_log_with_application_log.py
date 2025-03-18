#!/usr/bin/env python3

import json
import sys
from datetime import datetime

"""
Joins our merged CloudWatch Metrics logs (hyrax_request_log and hyrax_response_log), with the 
json encoded BES application logs for the same time period.
"""

verbose = False
max_records = 0


def loggy(message: str):
    """
    Prints a log message to stderr when verbose is enabled.
    """
    if verbose:
        print(f"# {message}", file=sys.stderr)


def stderr(message: str):
    """
    Prints a log message to stderr.
    """
    print(f"# {message}", file=sys.stderr)


def wrap_a_line(msg: str, count: int, width=80):
    """
    A progress bar which will inject a newline when count % width is zero.
    """
    print(msg, end='', file=sys.stderr)
    if not count % width:
        print("", file=sys.stderr)


def convert_iso_to_unix(iso_string):
    """
    Converts an ISO 8601 formatted string to a Unix timestamp.
    """
    try:
        time_format = "%Y-%m-%dT%H:%M:%S%z"
        dt = datetime.strptime(iso_string, time_format)  # Handle Z timezones
        unix_timestamp = dt.timestamp()
        return int(unix_timestamp)  # return as an integer.
    except ValueError as e:
        stderr(f"Error: Invalid ISO 8601 format: {e}")
        return None  # Or raise the exception, depending on your needs.
    except Exception as e:
        stderr(f"An unexpected error occurred: {e}")
        return None


application_log_request_type = "request"
application_log_info_type = "info"
application_log_error_type = "error"
application_log_verbose_type = "verbose"
application_log_timing_type = "timing"


def join_metrics_log_with_application_log_entries(
        metrics_log: str,
        application_log: str,
        out_file: str):
    """
    Joins our merged CloudWatch Metrics logs (hyrax_request_log and hyrax_response_log), with the
    json encoded BES application logs for the same time period.

    :param metrics_log: The merged entries from our CloudWatch hyrax_request_log and hyrax_response_log streams
    :param application_log: The BES application log, encoded as json. from the same time period as the metrics log.
    :param out_file: Filename where the JSON should be written.
    :return: nothing
    """
    metrics_request_id_key = "request_id"
    application_log_request_id_key = "hyrax-request-id"

    loggy("---------------------------------------------------------------------------------------------------------")
    loggy("join_olfs_metrics_log_with_bes_application_log_entries()")
    loggy("")
    loggy(f"                      metrics_log: {metrics_log}")
    loggy(f"           metrics_request_id_key: {metrics_request_id_key}")
    loggy("")
    loggy(f"                  application_log: {application_log}")
    loggy(f"   application_log_request_id_key: {application_log_request_id_key}")
    loggy("")
    loggy(f"                         out_file: {out_file}")
    loggy("")

    # Load the metrics log records. (e.g., job details)
    with open(metrics_log, 'r') as f:
        metrics_log_records = json.load(f)

    # Load the application log records. (e.g., user details)
    with open(application_log, 'r') as f:
        application_log_records = json.load(f)

    # Build an index (a dictionary) the application records using application_log_request_id_key as the key,
    # only including the application_log_request_type entries.
    application_log_index = {
        record.get(application_log_request_id_key, ""): record
        for record in application_log_records
        if record.get("hyrax-type", "") == application_log_request_type
    }

    # Iterate over the records in metrics_log_records,
    # merge each with the corresponding application_log_records record(s). A BES application log records are located
    # by matching the values of the metrics_request_id_key and the application_log_request_id_key in the teo records.
    joined_records = []
    rec_num = 0
    matched_records = 0
    for metrics_log_record in metrics_log_records:
        rec_num += 1

        # Progress Bar :)
        if not verbose:
            wrap_a_line(".", rec_num, 100)

        loggy(f"-- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --")

        # Grab the value of metrics_request_id_key for the current metrics_log_record
        metrics_request_id = metrics_log_record.get(metrics_request_id_key, {})
        if metrics_request_id:
            loggy(f"metrics_log_record has \"{metrics_request_id_key}\": {metrics_request_id}")
            # Lookup the matching application log record; if none, return an empty dict
            application_log_record = application_log_index.get(metrics_request_id, {})
            if len(application_log_record) > 0:
                # Find the things we need- instance-id, pid, start and end times so we can mine
                # the application-log for messages.
                pid = application_log_record.get("hyrax-pid", "")
                instance_id = application_log_record.get("hyrax-instance-id", "")
                bes_start_time = int(application_log_record.get("hyrax-time", 0))
                loggy(f"pid: {pid} instance_id: {instance_id} bes_start_time: {bes_start_time}")

                # What time was the request completed?
                # From the metrics_log_record we get the value of the "time_completed" key
                # The value is formatted as:  YYYY-MM-DDTHH:MM:SSZ ("2025-02-14T07:00:05+0000")
                end_time_str = metrics_log_record.get("time_completed", "")
                end_time = bes_start_time
                if end_time_str != "":
                    end_time = convert_iso_to_unix(end_time_str)

                # Locate all the application log records for the request by matching instance-id, pid, and time range
                related_application_log_entries = [
                    record for record in application_log_records
                    if record.get("hyrax-instance-id", "") == instance_id and
                       record.get("hyrax-pid", "") == pid and
                       record.get("hyrax-type", "") != application_log_request_type and
                       bes_start_time <= int(record.get("hyrax-time", bes_start_time)) <= end_time
                ]
                loggy(
                    f"Found {len(related_application_log_entries)} related_application_log_entries for pid: {pid} on instance: {instance_id} .")

                # Join the things
                joined = {**metrics_log_record, "bes": {application_log_request_type: {**application_log_record},
                                                        "related_entries": related_application_log_entries}}
                joined_records.append(joined)
                matched_records += 1 + len(related_application_log_entries)

            else:
                loggy(
                    f"Failed to locate the application_log_request_id_key: {application_log_request_id_key} with value: {metrics_request_id} in the application_log_index.")
                joined_records.append(metrics_log_record)
        else:
            loggy(f"Failed to locate key {metrics_request_id_key} in metrics_log_record: {metrics_log_record}")

        if max_records != 0 and rec_num >= max_records:
            break

    # Write the results to the file
    with open(out_file, 'w') as f:
        json.dump(joined_records, f, indent=2)

    stderr(f"\nProcessed {len(joined_records)} metrics_log records. Joined {matched_records} application_log records.")


def main():
    global verbose;
    import argparse
    parser = argparse.ArgumentParser(description="Joins the merged CloudWatch Metrics logs, hyrax_request_log "
                                                 "and hyrax_response_log sent from the OLFS, With the json encoded "
                                                 "BES application logs for the same time period.")
    parser.add_argument("-v", "--verbose",
                        help="Increase output verbosity.",
                        action="store_true")

    parser.add_argument("-m", "--metrics_log",
                        help="The merged CloudWatch Metrics logs from the OLFS (hyrax_request_log "
                             "and hyrax_response_log",
                        default="metrics-log.json")

    parser.add_argument("-a", "--application_log",
                        help="The 'right' json array (table)",
                        default="application-log.json")

    parser.add_argument("-o", "--output",
                        help="Output file name.",
                        default="hyrax-combined-logs.json")

    args = parser.parse_args()
    verbose = args.verbose

    loggy(f"verbose: {verbose}")
    loggy(f"args: {args}")

    join_metrics_log_with_application_log_entries(args.metrics_log, args.application_log, args.output)

    stderr(f"Data extracted and saved to {args.output}")


if __name__ == "__main__":
    main()
