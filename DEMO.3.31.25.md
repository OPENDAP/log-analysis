
cd to log-analysis

export PATH=$(pwd):$PATH

cd to data and mkdir prod-3-27-25 (or the equiv) and cd to that dir

aws configure to log into the correct account

time download_logs.py -l hyrax-prod -s 2025-03-27T00:00:00 -o hyrax-prod.json

How about one hour's worth of logs:

```shell
time download_logs.py -l hyrax-prod -o bes_log.json -s 2025-03-27T09:00:00 -e 2025-03-27T10:00:00
Fetching logs from 'hyrax-prod' starting at 2025-03-27T09:00:00...
Data extracted and saved to bes_log.json
download_logs.py -l hyrax-prod -o bes_log.json -s 2025-03-27T09:00:00 -e   1.94s user 0.98s system 2% cpu 1:47.43 total

time download_logs.py -l hyrax_request_log -o request_log.json -s 2025-03-27T09:00:00 -e 2025-03-27T10:00:00
Fetching logs from 'hyrax_request_log' starting at 2025-03-27T09:00:00...
Data extracted and saved to request_log.json
download_logs.py -l hyrax_request_log -o request_log.json -s  -e   0.31s user 0.15s system 4% cpu 11.138 total

time download_logs.py -l hyrax_response_log -o response_log.json -s 2025-03-27T09:00:00 -e 2025-03-27T10:00:00
Fetching logs from 'hyrax_response_log' starting at 2025-03-27T09:00:00...
Data extracted and saved to response_log.json
download_logs.py -l hyrax_response_log -o response_log.json -s  -e   0.30s user 0.14s system 4% cpu 10.726 total

```

```shell
time ngap-logs.py 
# Merged data extracted and saved to hyrax_combined_logs.json
ngap-logs.py  50.17s user 0.50s system 99% cpu 50.906 total
```