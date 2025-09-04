# Log analysis for service-chain profiling

The scripts in this directory support analyzing and plotting profiling data collected via CloudWatch logs in the NGAP system. They were initially created to support ticket HYRAX-1835.

The scripts are relatively brittle, as they were written to support this specific and relatively-constrained profiling case.

The helper script `profile-last-hour.jl` has been added to enable a just-push-go analysis entrypoint. For custom log selection and filtering, or for locally generated logs, see the [Custom analysis](#custom-analysis) instructions.

## Default analysis

_Dependency: [Julia](https://julialang.org/install/) installed._

To be prompted for a time range, log group name, output directory, and (if needed) aws credentials, do:
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

To download the CloudWatch logs, after installing the AWS CLI, do

```bash
aws configure  # will prompt for aws credentials
aws configure set aws_session_token <SESSION_TOKEN>

aws logs filter-log-events \
--log-group-name <LOG_GROUP_NAME> \
--start-time 1756242340000 \
--end-time 1756244560000 \
--output json > output_log.json
```

For NGAP, `LOG_GROUP_NAME` is `hyrax-<DEPLOYMENT_ENV>` for each of the deployment environments.

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


