import controlflow as cf
from pydantic import BaseModel, Field


class ResearchReport(BaseModel):
    title: str
    summary: str
    key_findings: list[str] = Field(min_items=3, max_items=10)
    references: list[str]


task = cf.Task(
    "Generate a research report on quantum computing", result_type=ResearchReport
)

report = task.run()
print(f"Report title: {report.title}")
print(f"Number of key findings: {len(report.key_findings)}")
