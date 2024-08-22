import controlflow as cf

task = cf.Task(
    "Is this a book or a movie?",
    result_type=["book", "movie"],
    context=dict(title="Game of Thrones"),
)
result = task.run()

assert result == "book"
