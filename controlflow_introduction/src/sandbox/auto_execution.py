import controlflow as cf


@cf.flow
def research_flow():
    gather_sources = cf.Task("Gather research sources", result_type=list[str])

    analyze_sources = cf.Task(
        "Analyze gathered sources",
        result_type=dict,
        context={"sources": gather_sources},
    )

    write_report = cf.Task(
        "Write research report", result_type=str, depends_on=[analyze_sources]
    )

    # Only need to return or run the final task
    return write_report


result = research_flow()
print(result)
