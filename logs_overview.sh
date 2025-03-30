#!/bin/bash
#
# Usage: logs_overview [combined log json]

# TODO add json files record count as sanity check

combined_log_file=${1:-hyrax_combined_logs.json}

# To see the spread of response codes:
echo "Response codes:"
jq 'to_entries[] | .value | .http_response_code' $combined_log_file| sort -u

# Get the counts of all response types
echo "Located" $(jq 'to_entries[] | .value | .http_response_code' $combined_log_file | wc -l) "records"
echo "Located" $(jq 'to_entries[] | .value | if .http_response_code==200 then .http_response else "skippy" end ' $combined_log_file| grep -v skippy | wc -l)" (200 OK) response records"
echo "Located" $(jq 'to_entries[] | .value | if .http_response_code==400 then .http_response else "skippy" end ' $combined_log_file| grep -v skippy | wc -l)" (400 User Error) response records"
echo "Located" $(jq 'to_entries[] | .value | if .http_response_code==401 then .http_response else "skippy" end ' $combined_log_file| grep -v skippy | wc -l)" (401 Unauthorized) response records"
echo "Located" $(jq 'to_entries[] | .value | if .http_response_code==404 then .http_response else "skippy" end ' $combined_log_file| grep -v skippy | wc -l)" (404 Not Found) response records"
echo "Located" $(jq 'to_entries[] | .value | if .http_response_code==500 then .http_response else "skippy" end ' $combined_log_file| grep -v skippy | wc -l)" (500 Server Error) response records"
echo "Located" $(jq 'to_entries[] | .value | if .http_response_code==502 then .http_response else "skippy" end ' $combined_log_file| grep -v skippy | wc -l)" (502 Bad Gateway) response records"
