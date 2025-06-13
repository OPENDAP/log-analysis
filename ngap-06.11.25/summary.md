= Overview

In these logs there are:
* 10471 merged records.
* 3160 404 responses
* 3669 500 responses
* 41 request_log entries with no matching response log entries. (Http response code is unknown)
* 22 of the unmatched request_log records have bes log entries.

There are 2320 entries with complete request and response logs, but missing BES entries.
Of those:
* 789 http 200 OK
* 820 http 500 Internal Server Error
* 711 http 404 Not Found

In order to locate all of the complete records in the combined file I used the follow `jq` expression:
```
   cat hyrax_combined_logs.json | jq '.[] | select(.ERROR==null and .bes != [])' > complete_records.json 
```
* `.ERROR==null` The ERROR property is only set when the `response_log` does not contain a record that matches one found in the `request_log`.
* `.bes != []` Sometimes, the bes array is empty. 

There are 8110 complete records in this log sample.
```
cat complete_records.json | jq '.user_id' | wc
    8110    8110   97155
```

* 2449 HTTP 200 OK responses
```
cat complete_records.json | jq '.http_response_code' | grep 200 | wc
    2812    2812   11248
```

* 2449 HTTP 404 Not Found responses
```
cat complete_records.json | jq '.http_response_code' | grep 404 | wc
    2449    2449    9796
```

* 2449 HTTP 500 Internal Server Error responses
```    
cat complete_records.json | jq '.http_response_code' | grep 500 | wc
    2849    2849   11396
```

## HTTP 404 Not Found
```
cat complete_records.json | jq 'select(.http_response_code == 404)' > complete_404.json
```

There are 2449 records.
```
cat complete_404.json | jq '.user_id' | wc
    2449    2449   29318
```
Of these, there are 2440 "failed attempt 1, will retry" messages for CMR

```
cat complete_404.json | grep "attempt: 1" | grep "cmr.earthdata" | wc
    2440   43920  926986
```
And those spawned an additional 993 "failed attempt 2, will retry" messages for CMR

```
cat complete_404.json | grep "attempt: 2" | grep "cmr.earthdata" | wc
     993   17874  377252
```

Punting on the 9 non CMR 404s for now...


## HTTP 404 500 Internal Server Error

```
cat complete_records.json | jq 'select(.http_response_code == 500)' > complete_500.json
```
2849 Records
```
cat complete_500.json | jq '.user_id' | wc
    2849    2849   34111
```
Of these, there are 2849 "failed attempt 1, will retry" messages for CMR

```
cat complete_500.json | grep "attempt: 1" | grep "cmr.earthdata" | wc
    2849   51282 1082394
```
And those spawned an additional 2849 "failed attempt 2, will retry" messages for CMR

```
cat complete_500.json | grep "attempt: 2" | grep "cmr.earthdata" | wc
    2849   51282 1082394
```

CMR consistently returned an HTTP 500 status for every single request:
```
cat complete_500.json | grep "Returned HTTP_STATUS: 500"  | grep "cmr.earthdata" | wc
    8547  247863 3971051
```
Note that's `8547 = 2849 * 3`, one for each failed attempt.
