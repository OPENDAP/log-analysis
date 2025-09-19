# Log analysis for service-chain profiling

The scripts in this directory support analyzing and plotting profiling data collected via CloudWatch logs in the NGAP system. They were initially created to support ticket HYRAX-1835.

The scripts are relatively brittle, as they were written to support this specific and relatively-constrained profiling case.

The helper script `profile-last-hour.jl` has been added to enable a just-push-go analysis entrypoint. For custom log selection and filtering, or for locally generated logs, see the [Custom analysis](#custom-analysis) instructions.

## Default analysis

_Dependency: [Julia](https://julialang.org/install/) installed._

To be prompted for a time range, environment name (sit/uat/prod), output directory, and (if needed) aws credentials, do:
```bash
julia path/to/profile.jl
```

To use all the defaults (namely, to grab the last hour's-worth of `hyrax-prod` logs), do
```bash
julia path/to/profile.jl -y
```
In this case, you will only be prompted if your aws credentials are stale.The path to your generated results will print to stdout on completion.

To force a credential update, e.g. in the case where you are switching between development environments even though your current credentials aren't stale, do 
```bash
julia path/to/profile.jl -F
```

To run on a pre-downloaded folder containing multiple logs, do
```bash
julia path/to/profile.jl <path-to-folder>
```

## Custom analysis

### 1. Collect log data to be analyzed

These script(s) can handle logs generated both locally during testing and pulled from CloudWatch.

#### Local logs

_Dependency: `jq` installed._

To format raw local logs as viable input for the analysis script, do
```bash
cat <PATH_TO_BES_LOG.log> | path/to/hyrax/bes/server/beslog2json.py | jq --slurp > bes_log.json
```

Raw `bes` logs will be found at path `~/hyrax/build/var/bes.log`, unless another location has been specifically configured.

#### CloudWatch logs

To download the two required log groups of CloudWatch logs, after installing the AWS CLI, do

```bash
aws configure  # will prompt for aws credentials
aws configure set aws_session_token <SESSION_TOKEN>

aws logs filter-log-events \
--log-group-name <LOG_GROUP_NAME> \
--start-time 1756242340000 \
--end-time 1756244560000 \
--output json > output_log.json
```

For NGAP, `LOG_GROUP_NAME`s are `hyrax-<DEPLOYMENT_ENV>`, `hyrax_edl_profiling_log`, `hyrax_request_log`, and `hyrax_response_log` for each of the deployment environments.

The start and end times are in miliseconds since the epoch. 
For ease of calculation, the current time can be determined via `echo $(($(date +%s%N)/1000000))`.
Alternatively, the `date` command can be used to get a time relative to the current time, e.g. for one day ago, `echo $(($(date -v -1d +%s%N)/1000000))`. Or just use https://currentmillis.com/ ! :)

### 2. Run Analysis

_Dependency: [Julia](https://julialang.org/install/) installed._

The first time this script runs, it will take some time to download and install the Julia dependencies. After that, it should run considerably faster!

```bash
cd <path/to/hyrax_profile_ngap> # this repo

julia run-analysis.jl <path/to/log.json> <PLOT_TITLE_PREFIX>
```
Some summary statistics will be printed to standard out. Plots will be saved next to the log file, using the input log file name with an additional plotting suffix: `<path/to/logs>_<plot_name>.png`. Any existing files of the same output plot name will be overwritten.

For example, 
```bash
julia run-analysis.jl ~Downloads/logs_2025-08-29_hyrax-foo.json "FOO "
```
will generate plots 
- `~Downloads/logs_2025-08-29_hyrax-foo_profile_raincloud.png` 
- `~Downloads/logs_2025-08-29_hyrax-foo_profile_raincloud_zoomed.png`

and the title on each plot will be prefixed with "FOO ". 

## Explanation of log parsing 

The OLFS logs return several types of profiling logs.  

For the curl-based authentication, two possible lines are logged, and we keep them both:
```
Request EDL user profile 
Validate token - Is valid? <true/false> 
```

Session authentication results in several additional logged messages. During analysis we exclude some of these lines, as the request_id parameter present in each log is not persistent across threads.

Here are the logs returned by an example (successful) browser request:
```
        { "request_id": "http-nio-8080-exec-5_41-b2468b37-cc86-41b9-a323-f28060d7d051", "hyrax-timer-name": "Validate token - Is valid? false", "hyrax-type": "timing", "start-time-ms": "1758227986408", "duration-ms": "0" }

        { "request_id": "http-nio-8080-exec-6_42-24dae409-8f6c-42da-99a3-58497f4b3194", "hyrax-timer-name": "Checkpoint: Redirect to EDL for authentication", "hyrax-type": "timing", "start-time-ms": "1758227986420", "duration-ms": "0" }
        { "request_id": "http-nio-8080-exec-6_42-24dae409-8f6c-42da-99a3-58497f4b3194", "hyrax-timer-name": "Handle login operation - Login now concluded? false", "hyrax-type": "timing", "start-time-ms": "1758227986415", "duration-ms": "5" }

        { "request_id": "http-nio-8080-exec-7_43-ab90555b-c81b-4467-b89c-ddb4e7c7ea38", "hyrax-timer-name": "Checkpoint: Client arrived from EDL with authentication code", "hyrax-type": "timing", "start-time-ms": "1758227986631", "duration-ms": "0" }
        { "request_id": "http-nio-8080-exec-7_43-ab90555b-c81b-4467-b89c-ddb4e7c7ea38", "hyrax-timer-name": "Request token from EDL", "hyrax-type": "timing", "start-time-ms": "1758227986632", "duration-ms": "228" }
        { "request_id": "http-nio-8080-exec-7_43-ab90555b-c81b-4467-b89c-ddb4e7c7ea38", "hyrax-timer-name": "Handle login operation - Login now concluded? true", "hyrax-type": "timing", "start-time-ms": "1758227986628", "duration-ms": "281" }
```

(The linebreaks have been artificially added to show the unique sets of request_ids.)

During analysis, we exclude both "Checkpoint: ..." logs (which will always have a "duration-ms=0", by definition).

We additionally throw out all instances of "Validate token - Is valid? false" where the "duration-ms" is 0, which happens only when validation is never even attempted---at the start of every browser session.

This leaves us with two types of relevant logged lines for the browser login path: "Request token from EDL" and "Handle login operation - Login now concluded? true". 

Hopefully we'll be able to set a persistent request_id in the future, and add those checkpoint lines back into our resultant analysis.