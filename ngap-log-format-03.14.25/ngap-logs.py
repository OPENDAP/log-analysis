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
    Prints a log message tpo stderr when verbose is enabled.
    """
    if verbose:
        print(f"# {message}",file=sys.stderr)

def stderr(message: str):
    """
    Prints a log message to stderr.
    """
    print(f"# {message}", file=sys.stderr)

def wrap_a_line(msg:str, count:int, width=80):
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
        dt = datetime.strptime(iso_string, time_format) #Handle Z timezones
        unix_timestamp = dt.timestamp()
        return int(unix_timestamp) #return as an integer.
    except ValueError as e:
        stderr(f"Error: Invalid ISO 8601 format: {e}")
        return None  # Or raise the exception, depending on your needs.
    except Exception as e:
        stderr(f"An unexpected error occurred: {e}")
        return None


application_log_request_type= "request"
application_log_info_type= "info"
application_log_error_type= "error"
application_log_verbose_type= "verbose"
application_log_timing_type= "timing"
request_id_key = "request_id"
bes_log_request_id_key = "request-id"
bes_log_type_key ="type"
bes_log_prefix=""


# TODO - Make this "peek" at the file ??
def get_records(source_file: str):
    """
    Reads JSON records from the supplied file into a list. First it tries to read the file as a collection of json
    objects without the delimiting json list syntax of commas and square brackets. If that fails, then it tries to
    read the file as a json list of objects with the attendant commas and enclosing square brackets: [{},{},{}]
    Args:
        source_file:

    Returns:
        The records as a list.

    """
    prolog = "get_records() - "
    failed = False
    loggy(f"{prolog}BEGIN")
    try:
        # Try as a raw json file.
        try:
            return get_raw_records(source_file)
        except json.JSONDecodeError:
            stderr(f"{prolog}WARNING: Fail to parse records as a raw json list (no enclosing square brackets, no commas between top level).")

        # Try as a list formatted json file.
        loggy(f"{prolog}Ingest as raw json records failed, trying as a list-o-json-records...")
        try:
            return get_list_records(source_file)
        except json.JSONDecodeError:
            stderr(f"{prolog}WARNING: Fail to parse records as a json list: '[{{}},{{}},{{}}]'.")

        failed = True
    finally:
        loggy(f"{prolog}END")

    # We can only get here if both ingest methods failed.
    stderr(f"{prolog}ERROR: File ingest for: '{source_file}' failed. Exiting...")

    if(failed):
        exit(400)
    else:
        return []

def get_list_records(source_file: str):
    """
    Reads a list of json records from source_file and returns a list.
    Args:
        source_file: The file containing a json list of records.

    Returns: The list of records.
    """
    prolog = "get_list_records() - "
    # Load the metrics log records. (e.g., job details)
    loggy(f"{prolog}Loading a list of json records from: '{source_file}'")
    try:
        with open(source_file, 'r') as f:
            records = json.load(f)
    except FileNotFoundError:
        stderr(f"{prolog}ERROR: File not found. path: '{source_file}'")
        exit(404)

    loggy(f"{prolog}Loaded {len(records)} records from '{source_file}'.")
    return records

def get_raw_records(source_file: str):
    """
    Reads a raw json records from source_file and returns a list.
    Args:
        source_file: The file containing the raw json objects.

    Returns: The list of records.
    """
    prolog = "get_raw_records() - "
    loggy(f"{prolog}Loading raw json records from: '{source_file}'")
    records = []
    line_num=0
    try:
        with open(source_file, 'r') as file:
            for line in file:
                line_num += 1
                json_object = json.loads(line.strip())
                records.append(json_object)

    except FileNotFoundError:
        stderr(f"{prolog}ERROR: File not found. path: '{source_file}'")
        exit(404)

    loggy(f"{prolog}END Loaded {len(records)} records in {line_num} lines from file: '{source_file}'")
    return records


def get_match(records:list, search_key:str, search_value:str, destination_name:str ):
    """
    Finds the first matching record in records.
    Args:
        records: The list of records to search
        search_key: The key name whose value must match the search_value
        search_value: The value search_key to match
        destination_name: The name of the object to be returned

    Returns: An object containing the matching record, or None if no match is found.

    """
    prolog = "get_match() - "
    loggy(f"{prolog}Checking records for : '{search_key}': {search_value}")
    matching_record = {
        destination_name: record
        for record in records
        if record.get(search_key, "") == search_value
    }
    loggy(f"{prolog}Found {len(matching_record)} record for '{search_key}': {search_value}")
    loggy(json.dumps(matching_record, indent=2))
    loggy("")
    return matching_record

def get_matches(records:list, search_key:str, search_value:str, destination_name:str ):
    """
    Finds all matching records in the records list
    Args:
        records: The list of records to search
        search_key: The key name whose value must match the search_value
        search_value: The value to match
        destination_name: The name of the object to be returned

    Returns: An object containing the matching records, or an empty object if no match is found.

    """
    prolog = "get_matches() - "
    # Build an index (a dictionary) the of the bes log records whose  request id matches the target value.
    loggy(f"{prolog}Checking records for '{search_key}': {search_value}")
    matching_records = [
            record
            for record in records
            if record.get(search_key, "") == search_value ]

    if len(matching_records) > 0:
        loggy(f"{prolog}--------------------------------------------------")

    loggy(f"{prolog}Found {len(matching_records)} records for '{search_key}': {search_value}")
    loggy(json.dumps(matching_records, indent=2))
    loggy("")
    return matching_records




def get_request_record(target_request_id:str,
                request_log_records: list,
                response_log_records: list,
                bes_log_records: list):
    """
    Builds the request lifecycle record for target_request_id.
    Args:
        target_request_id: The request_id whose lifecycle to locate.
        request_log_records: The request log records.
        response_log_records: The response log records.
        bes_log_records: The bes application log records.

    Returns: The complete lifecycle record for target_request_id.
    """
    prolog = "get_request_record() - "
    reqLog = "request_log"
    request_log = get_match(request_log_records, request_id_key, target_request_id, reqLog)

    respLog = "response_log"
    response_log = get_match(response_log_records, request_id_key, target_request_id, respLog)

    merged_olfs = {**request_log.get(reqLog), **response_log.get(respLog)}
    loggy(f"{prolog}Merged olfs log records for {request_id_key}: {target_request_id}")
    loggy(json.dumps(merged_olfs, indent=2))

    # Build an index (a dictionary) the of the bes log records whose  request id matches the target value.
    loggy(f"{prolog}Checking BES log for : {target_request_id}")
    bes_log_entries = get_matches(bes_log_records, bes_log_request_id_key, target_request_id, "")

    result_record = {**merged_olfs, "bes": bes_log_entries}
    loggy("# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # ")
    loggy(json.dumps(result_record, indent=2))
    loggy("")

    return result_record

def get_request(target_request_id:str,
                request_log_file: str,
                response_log_file: str,
                bes_log_file: str,
                out_file: str):
    """
    Search for the life of request_id in the various input files. Make unified json response.
    Args:
        target_request_id: The request_ir to investigate.
        request_log_file: The CloudWatch request_log for the hyrax log group.
        response_log_file: The CloudWatch response_log for the hyrax log group
        bes_log_file: The BES application log, encoded as json. from the same time period as the metrics log.
        out_file: Filename where the JSON should be written.

    Returns: nothing
    """
    prolog = "get_request() - "
    request_log_records = get_records(request_log_file)
    response_log_records = get_records(response_log_file)
    bes_log_records = get_records(bes_log_file)

    request_log_record = get_request_record(target_request_id,request_log_records,response_log_records, bes_log_records)

    # Write the results to the file
    with open(out_file, 'w') as fio:
        json.dump(request_log_record, fio, indent=2)

def get_merged( request_log_file: str,
                response_log_file: str,
                bes_log_file: str,
                out_file: str):
    """
    Merge the request life cycle data from the three logs: Cloudwatch request_log, Cloudwatch response_log and the
    BES application log (bes.log).
    Args:
        request_log_file: The CloudWatch request_log for the hyrax log group.
        response_log_file: The CloudWatch response_log for the hyrax log group
        bes_log_file: The BES application log, encoded as json. from the same time period as the metrics log.
        out_file: Filename where the JSON should be written.

    Returns: nothing
    """
    prolog = "get_merged() - "
    request_log_records = get_records(request_log_file)
    response_log_records = get_records(response_log_file)
    bes_log_records = get_records(bes_log_file)

    # Build an index (a dictionary) the all the bes records using bes_log_request_id_key as the key,
    # and include everything.
    bes_log_index = {
        record.get(bes_log_request_id_key,""): record
        for record in bes_log_records
        if record.get(bes_log_type_key,"") != ""
    }

    request_ids = request_log_records
    request_ids = {
        record.get(request_id_key,"")
        for record in request_log_records
        if record.get(request_id_key,"") != ""
    }
    merged_logs = {}
    for request_id in request_ids:
        merged_logs[request_id] = get_request_record(request_id,request_log_records,response_log_records,bes_log_records)

    # Write the results to the file
    with open(out_file, 'w') as fio:
        json.dump(merged_logs, fio, indent=2)



# ngap-logs.py -i request_id -r response_log.json -q request_log.json -b bes_log.json -o output_file
def main():
    global verbose
    global bes_log_prefix
    global bes_log_type_key
    global bes_log_request_id_key

    import argparse
    parser = argparse.ArgumentParser(description="This application can be used to located log entries for a specific "
                                                 "request_id, or it can be used to merge the three log streams: "
                                                 "Cloudwatch request_log, Cloudwatch response_log and the BES "
                                                 "application log into a single file using the request_id values as "
                                                 "the joining index.")
    parser.add_argument("-v", "--verbose",
                        help="Increase output verbosity.",
                        action="store_true")

    parser.add_argument("-i", "--request_id",
                        help="The request-id to find in the logs.",
                        default="")

    parser.add_argument("-r", "--response_log",
                        help="The CloudWatch Metrics response_log for the hyrax log group.",
                        default="response_log.json")

    parser.add_argument("-q", "--request_log",
                        help="The CloudWatch Metrics request_log for the hyrax log group.",
                        default="request_log.json")

    parser.add_argument("-b", "--bes_log",
                        help="The BES application log converted to JSON by beslog2json.py",
                        default="bes_log.json")

    parser.add_argument("-p", "--bes_prefix",
                        help="A prefix for all of the bes log keys. Check log file!",
                        default="hyrax-")

    parser.add_argument("-t", "--type",
                        help="Type of operation: R for find request record by request id, M for merge all records by request id.",
                        default="M")

    parser.add_argument("-o", "--output",
                        help="Output file name.",
                        default="hyrax_combined_logs.json")


    args = parser.parse_args()
    verbose=args.verbose

    loggy(f"verbose: {verbose}")
    loggy(f"args: {args}")
    if len(args.bes_prefix)!=0:
        bes_log_type_key = args.bes_prefix + bes_log_type_key
        bes_log_request_id_key = args.bes_prefix + bes_log_request_id_key
        bes_log_type_key = args.bes_prefix + bes_log_type_key
        bes_log_prefix = bes_log_prefix = args.bes_prefix


    loggy(f"bes_log_type_key: {bes_log_type_key}")

    if args.type == "R":
        get_request(args.request_id, args.request_log, args.response_log, args.bes_log, args.output)
        stderr(f"Request records extracted and saved to {args.output}")
    elif args.type == "M":
        get_merged(args.request_log, args.response_log, args.bes_log, args.output)
        stderr(f"Merged data extracted and saved to {args.output}")



if __name__ == "__main__":
    main()
