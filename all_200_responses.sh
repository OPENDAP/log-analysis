#!/bin/bash
#
# Usage: all_x_responses [combined log json] [output json]

combined_log_file=${1:-hyrax_combined_logs.json}
all_200_file=${2:-all_200_records}

jq 'to_entries[] | select(.value.http_response_code == 200) | .value' $combined_log_file > "$all_200_file"
echo "Located"$(jq '.http_response_code' $all_200_file | wc -l)" HTTP 200 response records."

