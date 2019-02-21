# Welcome to benchmark-tool

## Installation

Clone the repository:

```bash
git clone git@github.com:daajoe/benchmark-tool.git
```

Installing the dependencies can be done with [Pipenv](https://github.com/pypa/pipenv) (preferred)
or pip + virtualenv.

### Pipenv

```bash
pipenv install
```

### pip + virtualenv

```bash
python3 -m pip install -r requirements.txt
```

## How to use

1. [Writing a runscript](how-to/writing-runscript.md)
2. [Generate scripts with `./bgen`](how-to/generating-scripts.md)
3. [Running the benchmarks](how-to/running-benchmark.md)
4. [Evaluating the results with `./beval`](how-to/evaluating-results.md)

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
