#!/bin/bash

export combined_log_file="./hyrax_combined_logs.json"

# Find all the records in the $combined_log_file that do not have the BES record (aka unmatched records)
# using the presence of the key name "bes" as the indicator
export unmatched_records_file="./unmatched_records"
cat "$combined_log_file" | jq 'to_entries[] | .value | if has("bes") | not then . else "dropme" end' | grep -v dropme > "$unmatched_records_file"
echo "Located"$(cat "$unmatched_records_file" | jq '.http_response_code' | wc -l)" requests that lacked a BES component (aka unmatched requests)"


# All records requesting the CMR catalog service (124939 total records, all returned 404, all unmatched with a BES request)
export cmr_service_records_file="./cmr_records"
cat "$combined_log_file" | jq -r 'to_entries[] | .value | if .collectionId!=null and (.collectionId | contains("/hyrax/CMR"))  then . else "NO_CMR_PATH_FOUND" end' | grep -v NO_CMR_PATH_FOUND > "$cmr_service_records_file"
echo "Located"$(cat "$cmr_service_records_file" | jq '.request_id' | wc -l)" CMR catalog service requests"
echo "Located"$(cat "$cmr_service_records_file" | jq 'if .http_response_code==404 then . else "Skippy" end' | grep -v "Skippy" | jq '.request_id' | wc -l)" CMR catalog service requests that returned 404"
echo "Located"$(cat "$cmr_service_records_file" | jq 'if .bes==null then . else "Skippy" end' | grep -v "Skippy" | jq '.request_id' | wc -l)" CMR catalog service requests that lack a matching BES request expression."

# Get the all 404 response records (140994)
export all_404_response_records_file="./all_404_records"
cat "$combined_log_file" | jq 'to_entries[] | .value | if .http_response_code==404 then . else "not404."  end' | grep -v not404 | jq '.' > "$all_404_response_records_file"
echo "Located a total of "$(cat "$all_404_response_records_file" | jq '.http_response_code' | wc -l)" requests that returned 404"

# Get the all 404 response records for ngap service (15127)
export all_ngap_404_response_records_file="./all_ngap_404_records"
cat "$combined_log_file" | jq 'to_entries[] | .value | if .collectionId!=null and (.collectionId | startswith("/hyrax/ngap")) and .http_response_code==404  then . else "NoCollectionIdFound."  end' | grep -v NoCollectionIdFound | jq '.' > "$all_ngap_404_response_records_file"
echo "Located"$(cat "$all_ngap_404_response_records_file" | jq '.http_response_code' | wc -l)" ngap service requests that returned 404"

# Get the all 404 response records NOT for ngap service and NOT for CMR (928)
export other_404_responses_file="./other_404_records"
cat "$combined_log_file" | jq 'to_entries[] | .value | if .collectionId!=null and (.collectionId | startswith("/hyrax/ngap") | not) and (.collectionId | startswith("/hyrax/CMR") | not) and .http_response_code==404  then . else "NoCollectionIdFound."  end' | grep -v NoCollectionIdFound | jq '.' > "$other_404_responses_file"
echo "Located"$(cat "$other_404_responses_file" | jq '.http_response_code' | wc -l)" requests that returned 404 not for the ngap or CMR services. These are interesting..."

# Get the all 404 unmatched response records for ngap service(887) records
export unmatched_ngap_404_response_records_file="./unmatched_ngap_404_records"
cat "$combined_log_file" | jq 'to_entries[] | .value | if .bes==null and .collectionId!=null and (.collectionId | startswith("/hyrax/ngap")) and .http_response_code==404 then . else "NoCollectionIdFound."  end' | grep -v NoCollectionIdFound | jq '.' > "$unmatched_ngap_404_response_records_file"
echo "Located"$(cat "$unmatched_ngap_404_response_records_file" | jq '.http_response_code' | wc -l)" unmatched ngap service requests that returned 404"

# Get the all 404 response records directed at NSIDC_CPRD (14474) records
export nsidc_cprd_404_response_records_file="./nsidc_404_records"
cat "$combined_log_file" | jq 'to_entries[] | .value | if .collectionId!=null and (.collectionId | contains("-NSIDC_CPRD")) and .http_response_code==404 then . else "NoCollectionIdFound."  end' | grep -v NoCollectionIdFound | jq '.' > "$nsidc_cprd_404_response_records_file"
echo "Located"$(cat "$nsidc_cprd_404_response_records_file" | jq '.http_response_code' | wc -l)" NSIDC_CPRD requests that returned 404"


# Get the all response records from NSIDC_CPRD (18644 records total)
export nsidc_cprd_records_file="./nsidc_cprd_records"
cat "$combined_log_file" | jq 'to_entries[] | .value | if .collectionId!=null and (.collectionId | contains("NSIDC_CPRD")) then . else "skippy"  end' | grep -v skippy | jq '.' > "$nsidc_cprd_records_file"
echo "Located"$(cat "$nsidc_cprd_records_file" | jq '.http_response_code' | wc -l)" records for NSIDC_CPRD"
echo "Located"$(cat "$nsidc_cprd_records_file" | jq 'if .http_response_code==200 then .http_response else "skippy" end '| grep -v skippy | wc -l)" (200 OK) response records for NSIDC_CPRD"
echo "Located"$(cat "$nsidc_cprd_records_file" | jq 'if .http_response_code==400 then .http_response else "skippy" end '| grep -v skippy | wc -l)" (400 User Error) response records for NSIDC_CPRD"
echo "Located"$(cat "$nsidc_cprd_records_file" | jq 'if .http_response_code==404 then .http_response else "skippy" end '| grep -v skippy | wc -l)" (404 Not Found) response records for NSIDC_CPRD"
echo "Located"$(cat "$nsidc_cprd_records_file" | jq 'if .http_response_code==500 then .http_response else "skippy" end '| grep -v skippy | wc -l)" (500 Server Error) response records for NSIDC_CPRD"
echo "Located"$(cat "$nsidc_cprd_records_file" | jq 'if .http_response_code==502 then .http_response else "skippy" end '| grep -v skippy | wc -l)" (502 Bad Gateway) response records for NSIDC_CPRD"

# Get the all response records from POCLOUD (18644 records total)
export pocloud_records_file="./pocloud_records"
cat "$combined_log_file" | jq 'to_entries[] | .value | if .collectionId!=null and (.collectionId | contains("POCLOUD")) then . else "skippy"  end' | grep -v skippy | jq '.' > "$pocloud_records_file"
echo "Located"$(cat "$pocloud_records_file" | jq '.http_response_code' | wc -l)" records for POCLOUD"
echo "Located"$(cat "$pocloud_records_file" | jq 'if .http_response_code==200 then .http_response else "skippy" end '| grep -v skippy | wc -l)" (200 OK) response records for POCLOUD"
echo "Located"$(cat "$pocloud_records_file" | jq 'if .http_response_code==400 then .http_response else "skippy" end '| grep -v skippy | wc -l)" (400 User Error) response records for POCLOUD"
echo "Located"$(cat "$pocloud_records_file" | jq 'if .http_response_code==404 then .http_response else "skippy" end '| grep -v skippy | wc -l)" (404 Not Found) response records for POCLOUD"
echo "Located"$(cat "$pocloud_records_file" | jq 'if .http_response_code==500 then .http_response else "skippy" end '| grep -v skippy | wc -l)" (500 Server Error) response records for POCLOUD"
echo "Located"$(cat "$pocloud_records_file" | jq 'if .http_response_code==502 then .http_response else "skippy" end '| grep -v skippy | wc -l)" (502 Bad Gateway) response records for POCLOUD"


# all 400 errors
export all_400_response_records_file="./all_400_records"
cat "$combined_log_file" | jq 'to_entries[] | .value | if .http_response_code==400 then . else "dropme" end' | grep -v dropme > "$all_400_response_records_file"
echo "Located"$(cat "$all_400_response_records_file" | jq '.http_response_code' | wc -l)" (400 User Error) response records."
echo "Located"$(cat "$all_400_response_records_file" | jq 'if .collectionId!=null and (.collectionId | contains("login")) then . else "skippy" end' | grep -v skippy | jq '.collectionId' | wc -l)" (400 User Error) response records from the login endpoint."

# To see the spread of response codes:
cat "$combined_log_file" | jq 'to_entries[] | .value | .http_response_code' | sort -u

# Get the all response records from POCLOUD (18644 records total)
echo "Located"$(cat "$combined_log_file" | jq 'to_entries[] | .value | .http_response_code' | wc -l)" records"
echo "Located"$(cat "$combined_log_file" | jq 'to_entries[] | .value | if .http_response_code==200 then .http_response else "skippy" end '| grep -v skippy | wc -l)" (200 OK) response records"
echo "Located"$(cat "$combined_log_file" | jq 'to_entries[] | .value | if .http_response_code==400 then .http_response else "skippy" end '| grep -v skippy | wc -l)" (400 User Error) response records"
echo "Located"$(cat "$combined_log_file" | jq 'to_entries[] | .value | if .http_response_code==401 then .http_response else "skippy" end '| grep -v skippy | wc -l)" (401 Unauthorized) response records"
echo "Located"$(cat "$combined_log_file" | jq 'to_entries[] | .value | if .http_response_code==404 then .http_response else "skippy" end '| grep -v skippy | wc -l)" (404 Not Found) response records"
echo "Located"$(cat "$combined_log_file" | jq 'to_entries[] | .value | if .http_response_code==500 then .http_response else "skippy" end '| grep -v skippy | wc -l)" (500 Server Error) response records"
echo "Located"$(cat "$combined_log_file" | jq 'to_entries[] | .value | if .http_response_code==502 then .http_response else "skippy" end '| grep -v skippy | wc -l)" (502 Bad Gateway) response records"

export all_401_response_records_file="./all_401_records"
cat "$combined_log_file" | jq 'to_entries[] | .value | if .http_response_code==401 then . else "dropme" end' | grep -v dropme > "$all_401_response_records_file"
echo "Located"$(cat "$all_401_response_records_file" | jq '.http_response_code' | wc -l)" (401 Unauthenticated) response records."
echo "Located"$(cat "$all_401_response_records_file" | jq 'if .collectionId!=null and (.collectionId | contains("login")) then . else "skippy" end' | grep -v skippy | jq '.collectionId' | wc -l)" (401 Unauthorized) response records from the login endpoint."

# Take a look at the 401 error records.

jq '.user_id' all_401_records | sort -u
























