import controlflow as cf

task = cf.Task("Say hello in three languages", result_type=list[str])
result = task.run()

print(result)
assert isinstance(result, list)
assert len(result) == 3
