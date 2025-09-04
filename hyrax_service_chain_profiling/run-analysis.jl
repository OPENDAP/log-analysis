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

    category_labels = df.source
    labels = unique!(select(df, :source)).source
    colors = Makie.wong_colors()
    axis = (; xlabel="Duration [seconds]", title,
            xminorgridvisible=true,
            xminorgridcolor=RGBAf(0, 0, 0, 0.1),
            xgridcolor=RGBAf(0, 0, 0, 0.15),
            xminorticks=1:1000,
            yticks=(1:length(labels), labels),)
    p = rainclouds(category_labels, df.values;
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
    println("\t- Plot saved to $savepath")
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

#####
##### Main entrypoint
#####

function analyze_logs(; log_path, title_prefix="", verbose=false, max_zoom_x=20)
    isfile(log_path) || throw("Input log file not found: `$(log_path)`")

    @info "Loading data from $log_path..."
    plot_prefix = replace(log_path, ".json" => "")
    json = JSON3.read(log_path)
    logs = Dict()
    if json isa JSON3.Object
        # Came from AWS, rather than locally!
        messages = [JSON3.parse(e.message) for e in json.events]
        for t in unique(j["hyrax-type"] for j in messages)
            logs[t] = DataFrame(filter(l -> l["hyrax-type"] == t, messages))
        end
    else
        for t in unique(j["type"] for j in json)
            logs[t] = DataFrame(filter(l -> l["type"] == t, json))
        end
    end

    # Clean-up column names to make more usable later
    for k in keys(logs)
        rename!(s -> replace(s, "hyrax-" => "", "-" => "_"), logs[k])
    end

    @info "Processing profiling logs..."
    if "timing" in keys(logs)
        df_profiling = filter("timer_name" => startswith("Profile timing"), logs["timing"])
        logs["timing"] = filter("timer_name" => !startswith("Profile timing"),
                                logs["timing"])
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
    end

    @info "Number of log lines per type:"
    for k in keys(logs)
        str = lpad(k * ": ", 14)
        println("\t$str$(nrow(logs[k]))")
    end

    verbose && print_log_examples(logs)

    request_ids = []
    for k in keys(logs)
        k == "start-up" && continue
        k == "error" && continue
        append!(request_ids, unique(logs[k].request_id))
    end
    @info "Total number of request ids: $(length(unique(request_ids)))"

    # Let's do some exploring!
    profile_logs = logs["profiling"]
    transform!(profile_logs,
               :action => ByRow(a -> replace(a, "Request redirect url" => "Get signed url from TEA", "Request" => "Get", "Handle" => "Process", " unconstrained" => "")) => :action)
    _add_num_prefix = str -> begin
        str == "Get granule record from CMR" &&
            (return "1. " * str * "\n(Includes retries on failure)")
        str == "Get DMRpp from DAAC bucket" &&
            (return "2. Get DMR++ from S3\n(Includes TEA redirect)")
        str == "Get signed url from TEA" && (return "3. " * str)
        startswith(str, "Get SuperChunk data") && (return "4. Get SuperChunk data from S3")
        startswith(str, "Process SuperChunk data") &&
            (return "5. Process SuperChunk\n(In memory)")
        @warn "Unexpected action type: `$str`"
        return str
    end
    transform!(profile_logs, :action => ByRow(_add_num_prefix) => :action)
    reverse!(sort!(profile_logs, :action))

    date_range = get_date_range_str(profile_logs)

    @info "Profile logs summary:" date_range num_unique_requests = length(unique(profile_logs.request_id)) total_log_lines = nrow(profile_logs)

    gdf = combine(groupby(profile_logs, :action), nrow => "log count",
                  :elapsed_us => (arr -> median(arr) / 1_000_000) => "median duration [s]",
                  :elapsed_us => (arr -> maximum(arr) / 1_000_000) => "max duration [s]")
    display(reverse(gdf))

    @info "Generating summary plots..."
    df_actions = select(profile_logs, :action => :source,
                        :elapsed_us => ByRow(v -> v / 1_000_000) => :values)
    plot_profile_rainclouds(df_actions; title=title_prefix * "service chain profiling",
                            savepath=plot_prefix * "_profile_raincloud.png",
                            xlims=(nothing, nothing), metadata=date_range)

    max_duration_zoom = min(Int(ceil(maximum(df_actions.values))), max_zoom_x)
    for s in 2:2:max_duration_zoom
        plot_profile_rainclouds(df_actions;
                                title=title_prefix * "service chain profiling (zoomed)",
                                savepath=plot_prefix *
                                         "_profile_raincloud_zoomed_max$(s)sec.png",
                                xlims=(-.2, s),
                                metadata=date_range)
    end

    return (; logs, df_actions)
end

# CLI entrypoint
if abspath(PROGRAM_FILE) == @__FILE__
    analyze_logs(; log_path=ARGS[1], title_prefix=length(ARGS) > 1 ? ARGS[2] : "")
end
