#!/usr/bin/env python3

import re
import csv


# Define a function to process the lines
def process_file(input_file, output_file):
    """
    After running a group of tests using hy500.py, process the 'combined timing' file. Build this
    file using cat like cat sit-efs-urls-*_timing.txt > sit-efs-urls-combined_timing.txt
    :param input_file: The combined timing file
    :param output_file: A csv file with timing information and some limited error information
    :return: Nothing
    """
    data = []
    pending_time = None

    with open(input_file, 'r') as file:
        for line in file:
            line = line.strip()
            
            # Match lines with response times
            match_time = re.match(r"Time to gather (\d+) responses: ([\d.]+) ms", line)
            if match_time:
                if pending_time:
                    # If there is a pending time, add it with status code 200
                    data.append([pending_time["responses"], pending_time["time"], 200])
                    pending_time = None

                responses = int(match_time.group(1))
                time = float(match_time.group(2))
                pending_time = {"responses": responses, "time": time}
                continue

            # Match lines with errors
            match_error = re.match(r"Error: (\d+); .+", line)
            if match_error:
                status_code = int(match_error.group(1))
                if pending_time:
                    # Add the pending time with the error code
                    data.append([pending_time["responses"], pending_time["time"], status_code])
                    pending_time = None

    # If there's any remaining pending time, add it as successful
    if pending_time:
        data.append([pending_time["responses"], pending_time["time"], 200])

    # Write the processed data to a CSV file
    with open(output_file, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        # Write the header
        csv_writer.writerow(["Number of Responses", "Time (ms)", "HTTP Status Code"])
        # Write the data rows
        csv_writer.writerows(data)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="After running a group of tests using hy500.py, process the "
                                                 "'combined timing' file. Build this file using 'cat' like "
                                                 "cat sit-efs-urls-*_timing.txt > sit-efs-urls-combined_timing.txt.")
    parser.add_argument("-v", "--verbose", help="Increase output verbosity.", action="store_true")
    parser.add_argument("-i", "--input", help=".", required=True)
    parser.add_argument("-o", "--output", help=".", default="output.csv")

    args = parser.parse_args()

    process_file(args.input, args.output)

    print(f"Data extracted and saved to {args.output}")


if __name__ == "__main__":
    main()

