using Dates
using HyraxLogAnalysis

#####
##### Helper function
#####

# Intentionally shelling out to the AWS CLI instead of using aws julia wrapper
function aws_set_temporary_credentials()
    run(`aws configure`)
    token = Base.prompt("AWS Session token?")
    return run(`aws configure set aws_session_token $token`)
end

function validate_or_prompt_aws_credentials(; force_new_credentials::Bool)
    if force_new_credentials
        aws_set_temporary_credentials()
    else
        try
            read(`aws sts get-caller-identity`, String)
        catch
            aws_set_temporary_credentials()
        end
    end

    try
        read(`aws sts get-caller-identity`, String)
    catch e
        print("AWS credentials are not set! Error: $e")
        rethrow()
    end
    return nothing
end

datetime2epoch_ms(x::DateTime) = (Dates.value(x) - Dates.UNIXEPOCH)

#####
##### Main entrypoint
#####

# TODO-future: support enormous logs....might not be grabbing all due to download size restrictions?!?
function main(; force_new_credentials::Bool=false, use_all_defaults::Bool=false)
    # Prompt for credentials 
    validate_or_prompt_aws_credentials(; force_new_credentials)

    # Get user inputs for log filter request
    time_now = Dates.now(UTC)
    start_time = let
        default = string(time_now - Dates.Hour(1))
        t = use_all_defaults ? default :
            Base.prompt("Start time? (Default is an hour ago)"; default)
        datetime2epoch_ms(DateTime(t))
    end
    end_time = let
        default = string(time_now)
        t = use_all_defaults ? default : Base.prompt("End time? (Default is now)"; default)
        datetime2epoch_ms(DateTime(t))
    end
    environment_name = let
        default = "prod"
        n = use_all_defaults ? default : lowercase(Base.prompt("Log group name (sit/uat/prod)?"; default))
        while !(n in ["sit", "uat", "prod"])
            n = lowercase(Base.prompt("Log group name (sit/uat/prod)?"; default))
        end
        n
    end
    outdir = let
        default = joinpath(homedir(), "Downloads")
        use_all_defaults ? default : Base.prompt("Output directory?"; default)
    end
    date_str = "$start_time-$end_time"

    log_dir = joinpath(outdir, string(Date(time_now)) * "_$(date_str)_" * environment_name)
    for log_group_name in ["hyrax_edl_profiling_log", "hyrax-$(environment_name)", "hyrax_response_log", "hyrax_request_log"]
        log_path = joinpath(log_dir, "logs-$(date_str)-$(log_group_name).json")

        aws_cmd = `aws logs filter-log-events --log-group-name $log_group_name --start-time $start_time --end-time $end_time --output json`
        @info "Making AWS download request..." start_time end_time log_group_name log_path command=aws_cmd

        logs = read(aws_cmd, String)
        mkpath(dirname(log_path))
        write(log_path, logs)
        println("...saved to $log_path")
    end
    @info "Log download complete"

    # Generate results  
    title_prefix = uppercase(environment_name) * " "
    results = analyze_profile_logs(; log_path=log_dir, title_prefix)

    return results
end

# CLI entrypoint
if abspath(PROGRAM_FILE) == @__FILE__
    force_new_credentials = "-F" in ARGS
    use_all_defaults = "-y" in ARGS
    main(; force_new_credentials, use_all_defaults)
    return nothing
end
