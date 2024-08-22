import controlflow as cf
from langchain_anthropic import ChatAnthropic


model = ChatAnthropic(model="claude-3-opus-20240229")

# Create three agents
writer = cf.Agent(
    name="Writer",
    description="An AI agent that writes paragraphs",
    model=model,
)

editor = cf.Agent(
    name="Editor",
    description="An AI agent that edits paragraphs for clarity and coherence",
    model=model,
)

manager = cf.Agent(
    name="Manager",
    description="An AI agent that manages the writing process",
    instructions="""
        Your goal is to ensure the final paragraph meets high standards 
        of quality, clarity, and coherence. You should be strict in your 
        assessments and only approve the paragraph if it fully meets 
        these criteria.
        """,
    model=model,
)


@cf.flow
def writing_flow():
    print("start writer task")
    draft_task = cf.Task(
        "Write a paragraph about the importance of AI safety",
        agents=[writer],
    )
    print("finished writer task")

    # we will continue editing until the manager approves the paragraph
    approved = False
    while not approved:

        print("start editor task")
        edit_task = cf.Task(
            "Edit the paragraph for clarity and coherence",
            context=dict(draft=draft_task),
            agents=[editor],
        )
        print("finished editor task")

        print("start managaer task")
        approval_task = cf.Task(
            "Review the edited paragraph to see if it meets the quality standards",
            result_type=bool,
            context=dict(edit=edit_task),
            agents=[manager],
        )
        print("finished managaer task")

        # eagerly run the approval task to see if the paragraph is approved
        approved = approval_task.run()
        approved = True

    return approved, edit_task.result


approved, draft = writing_flow()
print(f'{"Approved" if approved else "Rejected"} paragraph:\n{draft}')
