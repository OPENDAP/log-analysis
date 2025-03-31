#!/bin/bash
#
# Usage: download_and_merge.sh [start time (2025-03-27T09:00:00)] [ end time (2025-03-27T10:00:00)]
start=${1:-2025-03-27T09:00:00}
end=${2:-2025-03-27T10:00:00}

download_logs.py -l hyrax-prod -o bes_log.json -s $start -e $end
download_logs.py -l hyrax_request_log -o request_log.json -s $start -e $end
download_logs.py -l hyrax_response_log -o response_log.json -s $start -e $end

# To merge the three logs - accepts names via options or uses defaults:
ngap-logs.py
