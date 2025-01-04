# Log Processing 

Python code to process raw BES logs that use the |&| separators.

Now contains code to download Cloud Watch logs.

log_processing.py: Turn bes logs into CSV, fix the times and split the log up by PID.
download_logs.py: Download CloudWatch json for a given log group and date range.
response_times.py: Take many 'timing.txt' files made by the hyrax500-2 client and build
		   a single csv file that's easy to graph.

