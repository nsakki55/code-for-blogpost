import controlflow as cf

task = cf.Task("Get the user's name", user_access=True)

with cf.instructions("Talk like a pirate"):
    task.run()
