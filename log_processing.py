#!/usr/bin/env python3
#
# Process log files from the BES. jhrg 12/06/24

import csv
import argparse
import os
from datetime import datetime
from collections import defaultdict


verbose = False


def split_csv_by_pid(input_file, field=2):
    """
    Spint the given CSV file into N files, one for each of the N PIDs in field 3
    of the CSV input file.
    :param input_file: CSV file of BES log data
    :param field: zero-based index of the field that holds the PID (this changed
    from 1 to 2 when instance IDs were addedd to the bes.log)
    :return: None; makes N files as a side effect
    """
    # Dictionary to store lines grouped by process ID
    pid_groups = defaultdict(list)

    # Read the input CSV file and group lines by PID
    with open(input_file, mode='r') as infile:
        reader = csv.reader(infile)
        for line in reader:
            if line:  # Skip empty lines
                pid = line[field]  # Assuming the PID is in the second column (index 2)
                pid_groups[pid].append(line)

    # Write output files for each unique PID
    base_filename = os.path.splitext(os.path.basename(input_file))[0]
    for pid, lines in pid_groups.items():
        output_filename = f"{base_filename}_pid_{pid}.csv"
        with open(output_filename, mode='w', newline='') as outfile:
            writer = csv.writer(outfile)
            writer.writerows(lines)
        print(f"Written {output_filename}")


def transform_logs_to_csv(input_file, output_file):
    """
    Transforms log lines from a custom format to CSV, converting Unix timestamps to ISO time strings
    and retaining microsecond values in 'timing' lines.

    Parameters:
    - input_file: Path to the input file containing log lines.
    - output_file: Path to the output CSV file.
    """
    def convert_to_iso(timestamp):
        """Converts Unix time in seconds to ISO 8601 format."""
        return datetime.utcfromtimestamp(int(timestamp)).isoformat() + "Z"

    line_count = 0
    info_count = 0
    timing_count = 0
    error_count = 0
    request_count = 0
    unknown_count = 0

    with open(input_file, 'r') as infile, open(output_file, 'w', newline='') as outfile:
        reader = infile.readlines()
        writer = csv.writer(outfile)

        for line in reader:
            line_count += 1
            # Split the log line by '|&|'
            fields = line.strip().split('|&|')

            if fields[2] == "info":
                info_count += 1
            elif fields[2] == "timing":
                timing_count += 1
            elif fields[2] == "request":
                request_count += 1
            elif fields[2] == "error":
                error_count += 1
            else:
                unknown_count += 1

            # Convert the first field (assumed to be Unix time) to ISO 8601
            try:
                fields[0] = convert_to_iso(fields[0])
            except ValueError:
                pass  # If conversion fails, keep the original value

            # Write the transformed line to the CSV file
            writer.writerow(fields)

    # sanity check; all lines accounted for?
    if line_count != info_count + timing_count + request_count + error_count:
        print(f"Error in the log file - some lines were not classified.")

    if verbose:
        print(f"Total line: {line_count}")
        print(f"Info: {info_count}")
        print(f"Timing: {timing_count}")
        print(f"Request: {request_count}")
        print(f"Error: {error_count}")
        print(f"Unknown: {unknown_count}")


def main():
    parser = argparse.ArgumentParser(description="Process raw BES log files, turning them into CSV files.")

    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    parser.add_argument("-s", "--split", help="split the csv file into N files, one for each PID",
                        action="store_true")

    parser.add_argument("-i", "--input", help="The log file (raw or CSV) to process.", required=True)

    # parser.add_argument("providers", nargs="*")

    args = parser.parse_args()
    global verbose
    verbose = args.verbose

    # This kludge means this can be called with a file that is already in CSV
    # form and have that file split up OR is can be called by a 'raw' log and
    # have that turned into CSV and, maybe, split.
    if args.split and os.path.splitext(args.input)[1] == ".csv":  # hack; look for csv file
        split_csv_by_pid(args.input)
    else:
        input_csv = f"{os.path.splitext(args.input)[0]}.csv"
        transform_logs_to_csv(args.input, input_csv)
        if args.split:
            split_csv_by_pid(input_csv)


if __name__ == "__main__":
    main()
