#!/bin/bash

# Usage: merge_request_response.sh [request (request_log.json)] [response (response_log.json)]
#
# Merge two JSON files that share a field named 'request_id' using that field's
# value as an index.

request=${1:-request_log.json}
response=${2:-response_log.json}

# jq -c -s '[.[0][], .[1][]]' "$request" "$response"
#jq -c -s 'reduce .[1][] as $item1 ({}; .[$item1."request_id"] = $item1) as $dict1 | .[0][] | $key="request_id" | if $dict1[.$key] then "barf" else . end' "$request" "$response"
#jq -c -s 'reduce .[1][] as $item1 ({}; .[$item1."request_id"] = $item1) as $dict1 | .[0][] | if $dict1[."request_id"] then "barf" else . end' "$request" "$response"
# jq -c -s 'reduce .[1][] as $item1 ({}; .[$item1."request_id"] = $item1) as $dict1 | .[0][] | if $dict1[."request_id"] then . + $dict1[."request_id"] else . end' "$request" "$response"
# 'reduce .[1][] as $item1 ({}; .[$item1."request_id"] = $item1) as $dict1 | .[0][] | if $dict1[."request_id"] then . + $dict1[."request_id"] else . end'

jq -s 'flatten | group_by(.request_id) | map(add)' "$request" "$response"
