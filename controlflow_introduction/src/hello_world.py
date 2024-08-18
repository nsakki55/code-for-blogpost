import controlflow as cf

hello_task = cf.Task("say hello")
print(hello_task.run())
