# Log Processing 

## What's here
Python code to process raw BES logs that use the |&| separators.

Now contains code to download Cloud Watch logs.

log_processing.py: Turn bes logs into CSV, fix the times and split the log up by PID.
download_logs.py: Download CloudWatch json for a given log group and date range.
response_times.py: Take many 'timing.txt' files made by the hyrax500-2 client and build
		   a single csv file that's easy to graph.
ngap-logs.py:

## How to run the tests
Like this 
```bash
python -m unittest discover -p "test*.py" tests
```

## Usage info
Using jq on the JSON downloaded by download_logs.py:

Here are some sample uses:
Get all the array elements where 'hyrax-type' is "start-up". Stamp and repeat for "error", "info" and "request"
```bash
jq '[.[] | select(.["hyrax-type"] == "start-up")]' output.txt > start-up.json
```
How many elements in the array of records?
```bash
jq 'length' info.json
```
Find all the records where 'hyrax-type' is not equal to "error", ...
```bash
jq '[ .[] | select((.["hyrax-type"] | IN("error", "info", "request", "start-up")) | not)]' output.txt > outliers.json
```
Print all the values of the 'hyrax-message' key for each record and write them out as a JSON array of values
```bash
jq '[ .[].["hyrax-message"]]' errors.json > error-messages.json
```
For example, this set of commands will deconstruct the bes log information read using download_logs.py:
```bash
(hyrax500) jgallag4@GSLAL2023031970 2-4-25-uat % jq '[.[] | select(.["hyrax-type"] == "start-up")]' output.txt > start-up.json
(hyrax500) jgallag4@GSLAL2023031970 2-4-25-uat % jq '[.[] | select(.["hyrax-type"] == "error")]' output.txt > errors.json     
(hyrax500) jgallag4@GSLAL2023031970 2-4-25-uat % jq '[.[] | select(.["hyrax-type"] == "info")]' output.txt > infos.json
(hyrax500) jgallag4@GSLAL2023031970 2-4-25-uat % jq '[.[] | select(.["hyrax-type"] == "request")]' output.txt > requests.json
(hyrax500) jgallag4@GSLAL2023031970 2-4-25-uat % jq 'length' start-up.json 
424
(hyrax500) jgallag4@GSLAL2023031970 2-4-25-uat % jq 'length' errors.json  
58
(hyrax500) jgallag4@GSLAL2023031970 2-4-25-uat % jq 'length' infos.json 
1400
(hyrax500) jgallag4@GSLAL2023031970 2-4-25-uat % jq 'length' requests.json
335
(hyrax500) jgallag4@GSLAL2023031970 2-4-25-uat % jq 'length' output.txt   
2218
(hyrax500) jgallag4@GSLAL2023031970 2-4-25-uat % 
```
Further refining:
```bash
(hyrax500) jgallag4@GSLAL2023031970 2-4-25-uat %  jq '[.[] | select(.["hyrax-message"] | contains("BESUtil.cc:298"))]' errors.json > errors-besutil.json
(hyrax500) jgallag4@GSLAL2023031970 2-4-25-uat % jq 'length' errors-besutil.json
51
```
Here's more info about using jq to extract errors: Get all the records that do not contain... NB: 'contains' is a simple string search while 'test' is a 
regex match operator (not sure if they are called operators) and is more powerful but maybe slower.
```bash
jq '[.[] | select(.["hyrax-message"] | (contains("timeout_expired()") or contains("BESTimeoutError") or contains("NgapApi.cc:304")) | not)]' errors.json > other_errors.json
```
Here's how I split up all the errors for a 12-hour period from 00:00:00 to 12:00:00 on 2/12/25:

```bash
(hyrax500) jgallag4@GSLAL2023031970 2-12-25-prod % jq length errors.json CMR_not_found.json timeout_errors.json timeout_expired_errors.json other_errors.json 
867
504
131
131
101
```
Those numbers add up. 

In the other_errors.json there's a mix of things with a fair number of
bogus cache 'errors' that are actually (or should be) info messages.
This dump from cloud watch is from build 52 and I believe build 60 has
better treatment of those cache error/info messages.

I added a new command - join_json_arrays.py - that will join two json
arrays based on a key. Once done, we can get a CSV file of the response
codes and CCID using:

```bash
jq -r '.[] | "\(.http_response_code),\(.collectionId)"' merged.json > response_code_and_ccid.csv
```