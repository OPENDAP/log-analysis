#!/bin/bash
#
# Usage: all_x_responses [combined log json] [output json]


combined_log_file=${1:-hyrax_combined_logs.json}
all_401_file=${1:-all_401_records}

jq 'to_entries[] | .value | if .http_response_code==401 then . else "dropme" end' $combined_log_file | grep -v dropme > "$all_401_file"
echo "Located"$(cat "$all_401_file" | jq '.http_response_code' | wc -l)" (401 Unauthenticated) response records."
echo "Located"$(cat "$all_401_file" | jq 'if .collectionId!=null and (.collectionId | contains("login")) then . else "skippy" end' | grep -v skippy | jq '.collectionId' | wc -l)" (401 Unauthorized) response records from the login endpoint."
