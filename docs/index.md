# Welcome to benchmark-tool's documentation

- [Installation](installation.md)
- [Quickstart](quickstart.md)
- [Writing a Result Parser](resultparser.md)
- [Specifying Benchmark Jobs](jobs.md)
- [Specifying Benchmark Instances](instance-specs.md)
- [Importing/Exporting](export-import.md)

## Project layout

```
.
├── benchmarks/         # benchmark directory
│   └── examples/       # example benchmarks
├── docs/               # this documentation
├── external-tools/     # various third-party tools
├── src/                # main source code
│   ├── benchmarktool/  # main module
├── utils/              # general utilities
├── bgen*               # script generation
├── beval*              # evaluate benchmark results
├── bconv*              # summarize benchmark evaluation
├── bexport*            # export benchmarks
├── bimport*            # import benchmarks
```
