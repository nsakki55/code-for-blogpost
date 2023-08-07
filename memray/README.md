# how to use memray
## Command
### Run memory profile
```bash
$ memray run [options] {file.py} [args]
$ memray run [options] -m {module} [args]
```

### live report 
```bash
$ memray run --live {file.py}
```

### summary report
```bash
$ memray summary <results.bin>
```

### flame graph report
```bash
$ memray flamegraph <results.bin>
```

### table report
```bash
$ memray table <results.bin>
```

### tree report
```bash
$ memray tree <results.bin>
```

### stats report
```bash
$ memray stats <results.bin>
```

### transform report
```bash
$ memray transform <format> <results.bin>
```
