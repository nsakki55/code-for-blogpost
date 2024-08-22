import controlflow as cf

docs_agent = cf.Agent(
    name="DocsBot",
    description="An agent that specializes in writing technical documentation",
    instructions=(
        "You are an expert in technical writing. You strive "
        "to condense complex subjects into clear, concise language."
        "Your goal is to provide the user with accurate, informative "
        "documentation that is easy to understand."
    ),
)

editor_agent = cf.Agent(
    name="EditorBot",
    description="An agent that specializes in editing technical documentation",
    instructions=(
        "You are an expert in grammar, style, and clarity. "
        "Your goal is to review the technical document created by DocsBot, "
        "ensuring that it is accurate, well-organized, and easy to read."
        "You should output notes rather than rewriting the document."
    ),
)

technical_document = cf.Task(
    "Write a technical document",
    agents=[docs_agent, editor_agent],
    instructions=(
        "Write a technical document that explains agentic workflows."
        "The docs agent should generate the document, "
        "after which the editor agent should review and "
        "edit it. Only the editor can mark the task as complete."
    ),
)

with cf.instructions("No more than 2 sentences per document"):
    technical_document.run()
