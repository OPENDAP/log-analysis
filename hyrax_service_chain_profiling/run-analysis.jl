using Pkg
Pkg.activate(@__DIR__)
Pkg.instantiate()
using DataFrames
using JSON3
using Statistics
using CairoMakie
using Dates

#####
##### Helper function
#####

function plot_profile_rainclouds(df; xlims=(nothing, nothing), title, savepath, metadata="")
    set_theme!(Theme(; fontsize=16))

    category_labels = df.action
    labels = unique!(select(df, :action)).action
    colors = Makie.distinguishable_colors(length(unique(df.action)))
    axis = (; xlabel="Duration [seconds]", title,
            xminorgridvisible=true,
            xminorgridcolor=RGBAf(0, 0, 0, 0.1),
            xgridcolor=RGBAf(0, 0, 0, 0.15),
            xminorticks=1:1000,
            yticks=(1:length(labels), labels),)
    p = rainclouds(category_labels, df.duration_sec;
                   axis,
                   figure=(size=(1200, 600),),
                   cloud_width=0.5,
                   clouds=hist,
                   orientation=:horizontal,
                   hist_bins=2000,
                   color=colors[indexin(category_labels, unique(category_labels))],)
    xlims!(xlims...)
    text!(p.figure.scene, Point3f(0, 0, 0); text=metadata, space=:relative)

    save(savepath, p)
    println("\t- Plot saved to $(basename(savepath))")
    return nothing
end

function print_log_examples(logs)
    println("Example of first entry from each log type:")
    for type in keys(logs)
        println("-> $(uppercase(type)):")
        row = first(logs[type])
        for k in names(logs[type])
            println("\t$k: \t$(row[k])")
        end
        println()
    end
end

function get_date_range_str(profiling_logs)
    return join(unix2datetime.(extrema(profiling_logs.time)), " to ")
end

function add_logs!(logs::Dict, df::DataFrame; key::String)
    # Clean-up column names to make more usable later
    rename!(s -> replace(s, "hyrax-" => "", "-" => "_"), df)

    if key in keys(logs)
        append!(logs[key], df)
    else
        logs[key] = df
    end
    return logs
end

# Extremely brittle....
function load_log_file!(logs::Dict, path)
    json = JSON3.read(path)
    if json isa JSON3.Object
        # Came from AWS, rather than locally!
        messages = [JSON3.parse(e.message) for e in json.events]
        if occursin("hyrax_request_log", path)
            add_logs!(logs, DataFrame(messages); key="hyrax_request_log")
        elseif occursin("hyrax_response_log", path)
            add_logs!(logs, DataFrame(messages); key="hyrax_response_log")
        elseif occursin("hyrax_edl_profiling", path)
            add_logs!(logs, DataFrame(messages); key="hyrax_edl_profiling")
        else
            for key in unique(m["hyrax-type"] for m in messages)
                df = DataFrame(filter(l -> l["hyrax-type"] == key, messages))
                add_logs!(logs, df; key)
            end
        end
    else
        # Local dev logs (maybe not worth supporting....)
        for key in unique(j["type"] for j in json)
            df = DataFrame(filter(l -> l["type"] == key, json))
            add_logs!(logs, df; key)
        end
    end
    return logs
end

function break_profiling_out_of_bes_timing_logs!(logs::Dict)
    "timing" in keys(logs) || return logs

    df_profiling = filter("timer_name" => startswith("Profile timing"), logs["timing"])
    logs["timing"] = filter("timer_name" => !startswith("Profile timing"), logs["timing"])
    if nrow(logs["timing"]) == 0
        delete!(logs, "timing")
    end

    parse_timer_name = str -> begin
        str = replace(str, "Profile timing: " => "")
        sp = split(str, " - "; limit=2)
        details = length(sp) == 2 ? last(sp) : ""
        return first(sp), details
    end
    transform!(df_profiling,
               :timer_name => ByRow(parse_timer_name) => [:action, :details])
    select!(df_profiling, Not(:timer_name))
    logs["profiling"] = df_profiling

    return logs
end

# Brittle; multiple files of the same log type will overwrite each other
function load_raw_logs(log_path; verbose=true)
    logs = Dict()
    if isfile(log_path)
        logs = load_log_file!(logs, log_path)
    elseif isdir(log_path)
        for f in readdir(log_path; join=true)
            endswith(f, ".json") || continue
            @info f
            load_log_file!(logs, f)
        end
    else
        throw("Log path not found (`$log_path`)")
    end
    if verbose
        println("Number of log lines per type:")
        total = 0
        for k in keys(logs)
            str = lpad(k * ": ", 14)
            num = nrow(logs[k])
            println("\t$str$(num)")
            total += num
        end
        println("\t\tTotal: $total")
    end
    return logs
end

# Combine profiling logs from bes and olfs into single dataframe
function get_legible_profiling_logs(raw_logs)
    logs_olfs = let
        df = select(raw_logs["hyrax_edl_profiling"],
                    :request_id, :timer_name => :action,
                    :start_time_ms => ByRow(v -> parse(Int, v) / 1000) => :start_sec,
                    :duration_ms => ByRow(v -> parse(Int, v) / 1000) => :duration_sec,
                    :start_time_ms => ByRow(v -> parse(Int, v[1:(end - 3)])) => :time,
                    :duration_ms)

        # Clean up session-based logs!
        # In future, if request_id is stable across profiled checkpoints, we can
        # combine sets of checkpoints into single action. For now, we have to exclude them 😢. 
        # See README.md for example and better explanation of the following exclusions.
        df = filter(row -> !(row.action == "Validate token - Is valid? false" &&
                             row.duration_sec <= 1), df)
        df = filter(row -> !startswith(row.action, "Checkpoint:"), df)
        df = filter(row -> row.action !=
                           "Handle login operation - Login now concluded? false", df)

        # This duplicates "Request EDL user profile" (for curl) - if we do local validation, 
        # we aren't using a service so it doesn't matter that this value is excluded
        # (and it should be trivial compared to everything else, anyway...)
        df = filter(row -> !startswith(row.action, "Validate token - Is valid?"), df)

        # ...we need to do some extra math to support a call site we neglected to uniquely profile :D
        new_rows = DataFrame()
        for gdf in groupby(df, :request_id)
            nrow(gdf) == 2 || continue
            if issetequal(gdf.action,
                          ["Handle login operation - Login now concluded? true",
                           "Request token from EDL"])
                duration_sec = abs(-(gdf.duration_sec...))
                push!(new_rows,
                      (; request_id=gdf.request_id[1],
                       action="1c. Get ID (via User Profile) from EDL\n(Sessions only)",
                       start_sec=0,
                       duration_sec, time=0, duration_ms=0); promote=true)
            end
        end
        append!(df, new_rows; promote=true)

        # Now that we've done that math, we can remove the overarching profile statement
        df = filter(row -> !startswith(row.action,
                                       "Handle login operation - Login now concluded? true"),
                    df)

        _add_num_prefix = str -> begin
            if str == "Request EDL user profile"
                return "1a. Get token validation from EDL\n(Curl requests only)"
            elseif str == "Request token from EDL"
                return "1b. Get token in exchange for code from EDL\n(Sessions only)"
            elseif str == "1c. Get ID (via User Profile) from EDL\n(Sessions only)"
                return str 
            else
                @warn "Unexpected action type: `$str`"
            end
            return str
        end
        transform!(df, :action => ByRow(_add_num_prefix) => :action)
        df
    end

    logs_bes = let
        df = select(raw_logs["profiling"],
                    :request_id, :action,
                    :start_us => ByRow(v -> v / 1_000_000) => :start_sec,
                    :elapsed_us => ByRow(v -> v / 1_000_000) => :duration_sec,
                    :details, :time)
        # Rename the task actions from their logged text to make them more legible on the output plot
        transform!(df,
                   :action => ByRow(a -> replace(a, "Request redirect url" => "Get signed url from TEA",
                   "Request" => "Get",
                   "Handle" => "Process",
                   " unconstrained" => "")) => :action)

        _add_num_prefix = str -> begin
            if str == "Get granule record from CMR"
                return "2. " * str * "\n(Includes retries on failure)"
            elseif str == "Get DMRpp from DAAC bucket"
                return "3. Get DMR++ from S3\n(Includes implicit TEA redirect)"
            elseif str == "Get signed url from TEA"
                return "4. " * str
            elseif startswith(str, "Get SuperChunk data")
                return "5. Get SuperChunk data from S3"
            elseif startswith(str, "Process SuperChunk data")
                return "6. Process SuperChunk\n(In memory)"
            elseif startswith(str, "Validate token")
                return "??. Validate token"
            elseif startswith(str, "Get EDL user profile")
                return "??. Get EDL user profile"
            elseif startswith(str, "Process login operation")
                return "??. Process login operation"
            elseif startswith(str, "Checkpoint")
                return "??. Checkpoint"# TODO: process better
            elseif startswith(str, "Get token from EDL")
                return "??. Get token from EDL"
            else
                @warn "Unexpected action type: `$str`"
            end
            return str
        end
        transform!(df, :action => ByRow(_add_num_prefix) => :action)
    end

    profile_logs = vcat(logs_bes, logs_olfs; cols=:union)
    reverse!(sort!(profile_logs, :action))
    return profile_logs
end

#####
##### Main entrypoint
#####

function analyze_profile_logs(; log_path, title_prefix="", verbose=false, max_zoom_x=20)
    ispath(log_path) || throw("Input log(s) not found: `$(log_path)`")

    @info "Loading log data..."
    plot_prefix = isfile(log_path) ? replace(log_path, ".json" => "") : log_path * "//"
    raw_logs = load_raw_logs(log_path; verbose)
    break_profiling_out_of_bes_timing_logs!(raw_logs)

    verbose && print_log_examples(raw_logs)
    request_ids = []
    for k in keys(raw_logs)
        k == "start-up" && continue
        k == "error" && continue
        append!(request_ids, unique(raw_logs[k].request_id))
    end
    @info "Total unique request ids: $(length(unique(request_ids)))"

    df_profiling = get_legible_profiling_logs(raw_logs)
    date_range = get_date_range_str(df_profiling)
    @info "Total unique request ids in profiling logs: $(length(unique(df_profiling.request_id)))"
    @info "Profile logs summary:" date_range total_log_lines = nrow(df_profiling)
    println()
    gdf = combine(groupby(df_profiling, :action), nrow => "log count",
                  :duration_sec => median => "median duration [s]",
                  :duration_sec => maximum => "max duration [s]")
    display(reverse(gdf))

    @info "Generating summary plots in $(dirname(plot_prefix))..."
    plot_profile_rainclouds(df_profiling; title=title_prefix * "Service-chain profiling",
                            savepath=plot_prefix * "_profile_raincloud.png",
                            xlims=(nothing, nothing),
                            metadata=date_range * " " * title_prefix)

    max_duration_zoom = min(Int(ceil(maximum(df_profiling.duration_sec))), max_zoom_x)
    for s in 2:2:max_duration_zoom
        plot_profile_rainclouds(df_profiling;
                                title=title_prefix * "Service-chain profiling (zoomed)",
                                savepath=plot_prefix *
                                         "_profile_raincloud_zoomed_max$(s)sec.png",
                                xlims=(-0.2, s),
                                metadata=date_range)
    end

    return (; raw_logs, df_profiling)
end

# CLI entrypoint
if abspath(PROGRAM_FILE) == @__FILE__
    return analyze_profile_logs(; log_path=ARGS[1],
                                title_prefix=length(ARGS) > 1 ? ARGS[2] : "")
end
