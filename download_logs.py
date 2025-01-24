#!/usr/bin/env python3

import boto3
import json
from datetime import datetime

"""
The response from boto3.client.filter_log_events has the form:
{
    'events': [
        {
            'logStreamName': 'instance-1-log-stream',
            'timestamp': 1672531200000,
            'message': '{"key": "value"}',
            'ingestionTime': 1672531234567
        },
        {
            'logStreamName': 'instance-2-log-stream',
            'timestamp': 1672531260000,
            'message': '{"key": "another-value"}',
            'ingestionTime': 1672531298765
        }
    ],
    'nextToken': 'eyJ2IjoiMSJ9...'  # A token for fetching the next page of results
}
"""


def download_logs(log_group_name, start_time, end_time = "", output_file = "output.txt"):
    """
    Download logs from an AWS CloudWatch Log Group.

    Parameters:
    - log_group_name: Name of the CloudWatch Log Group
    - start_time: Start time for log filtering in ISO 8601 format
    - output_file: Filepath to save the logs in JSON format
    """
    # Convert start_time to milliseconds since epoch
    start_timestamp = int(datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%S").timestamp() * 1000)

    # Initialize boto3 client
    client = boto3.client('logs')

    # Paginate through log events
    next_token = None
    all_events = []

    print(f"Fetching logs from '{log_group_name}' starting at {start_time}...")

    while True:
        params = {
            'logGroupName': log_group_name,
            'startTime': start_timestamp
        }
        if next_token:
            params['nextToken'] = next_token
        if end_time:
            # Convert start_time to milliseconds since epoch
            end_timestamp = int(datetime.strptime(end_time, "%Y-%m-%dT%H:%M:%S").timestamp() * 1000)
            params['endTime'] = end_timestamp

        response = client.filter_log_events(**params)

        # Collect events
        events = response.get('events', [])
        all_events.extend(events)

        # Check if more results are available
        next_token = response.get('nextToken')
        if not next_token:
            break

    # Write events to JSON file
    with open(output_file, 'w') as f:
        print("[", file=f)
        all_messages = [event['message'] for event in all_events]

        for message in all_messages:
            if message.startswith("{"):
                print(message, file=f, end="")
                print(',', file=f)

        # cheat - instead of splitting the messages up to get the last json object printed without an
        # ending comma, just write a placeholder line. jhrg 1/24/25
        print('{"placeholder-record": "placeholder-value"}', file=f)
        print("]", file=f)

    print(f"Logs saved to {output_file}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Download JSON formatted data from a CloudWatch Log Group. You must "
                                                 "set the Key ID and Secret key as environment variables (using 'aws "
                                                 "configure'.")
    parser.add_argument("-v", "--verbose", help="Increase output verbosity.", action="store_true")
    parser.add_argument("-l", "--log-group", help="The AWS log group name", default="hyrax-sit")
    parser.add_argument("-s", "--start", help="ISO 8601 timestamp, e.g., 2024-12-18T12:15:00",
                        required=True)
    parser.add_argument("-e", "--stop", help="ISO 8601 timestamp", default="")
    parser.add_argument("-o", "--output", help="Output file name.", default="output.txt")

    args = parser.parse_args()

    download_logs(args.log_group, args.start, args.stop, args.output)

    print(f"Data extracted and saved to {args.output}")


if __name__ == "__main__":
    main()

