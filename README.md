# Log Processing 

Python code to process raw BES logs that use the |&| separators.

Now contains code to download Cloud Watch logs.

log_processing.py: Turn bes logs into CSV, fix the times and split the log up by PID.
download_logs.py: Download CloudWatch json for a given log group and date range.
response_times.py: Take many 'timing.txt' files made by the hyrax500-2 client and build
		   a single csv file that's easy to graph.

Using jq on the JSON downloaded by download_logs.py:

Here are some sample uses:
Get all the array elements where 'hyrax-type' is "start-up". Stamp and repeat for "error", "info" and "request"
    jq '[.[] | select(.["hyrax-type"] == "start-up")]' output.txt > start-up.json

How many elements in the array of records?
    jq 'length' info.json

Find all of the records where 'hyrax-type' is not equal to "error", ...
    jq '[ .[] | select((.["hyrax-type"] | IN("error", "info", "request", "start-up")) | not)]' output.txt > outliers.json

Print all of the vlaues of the 'hyrax-message' key for each record and write them out as a JSON array of values
jq '[ .[].["hyrax-message"]]' errors.json > error-messages.json

For example, this set of commands will deconstruct the bes log information read using download_logs.py:

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

Further refining:

(hyrax500) jgallag4@GSLAL2023031970 2-4-25-uat %  jq '[.[] | select(.["hyrax-message"] | contains("BESUtil.cc:298"))]' errors.json > errors-besutil.json
(hyrax500) jgallag4@GSLAL2023031970 2-4-25-uat % jq 'length' errors-besutil.json
51
