using Dates

include(joinpath(@__DIR__, "run-analysis.jl")) #TODO-H: turn run-analysis into a package

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

# TODO: support enormous logs....might not be grabbing all due to download size restrictions?!?
function main(; force_new_credentials::Bool=false, use_all_defaults::Bool=false)
    # Prompt for credentials 
    validate_or_prompt_aws_credentials(; force_new_credentials)

    # Set up log filter
    now = Dates.now()
    start_time = let
        default = string(now - Dates.Hour(1))
        t = use_all_defaults ? default :
            Base.prompt("Start time? (Default is an hour ago)"; default)
        datetime2epoch_ms(DateTime(t))
    end
    end_time = let
        default = string(now)
        t = use_all_defaults ? default : Base.prompt("End time? (Default is now)"; default)
        datetime2epoch_ms(DateTime(t))
    end

    log_group_name = let
        default = "hyrax-prod"
        use_all_defaults ? default : Base.prompt("Log group name?"; default)
    end

    # Get logs 
    outdir = let
        default = joinpath(homedir(), "Downloads")
        use_all_defaults ? default : Base.prompt("Output directory?"; default)
    end
    log_path = joinpath(outdir, string(Dates.today()),
                        "logs_$(start_time)-$(end_time)_$(log_group_name).json") #TODO prompt output dir
    mkpath(dirname(log_path))

    @info "Downloading logs to $log_path..."
    aws_cmd = `aws logs filter-log-events --log-group-name $log_group_name --start-time $start_time --end-time $end_time --output json`
    logs = read(aws_cmd, String)
    write(log_path, logs)

    # Generate results 
    title_prefix = uppercase(first(split(log_group_name, "hyrax-"; limit=1)))
    results = analyze_logs(; log_path, title_prefix)

    return results
end

# CLI entrypoint
if abspath(PROGRAM_FILE) == @__FILE__
    force_new_credentials = "-F" in ARGS
    use_all_defaults = "-y" in ARGS
    main(; force_new_credentials, use_all_defaults)
    return nothing
end
