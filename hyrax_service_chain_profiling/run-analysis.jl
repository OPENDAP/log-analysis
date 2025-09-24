using Pkg
Pkg.activate(@__DIR__)
Pkg.instantiate()

using HyraxLogAnalysis

# CLI entrypoint
if abspath(PROGRAM_FILE) == @__FILE__
    return analyze_profile_logs(; log_path=ARGS[1],
                                title_prefix=length(ARGS) > 1 ? ARGS[2] : "")
end
