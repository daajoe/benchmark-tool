---
title: Quickstart
---

[TOC]

# Writing a runscript

A runscript is a yaml script that defines the benchmark. The runscript will be validated with [pykwalify](https://pykwalify.readthedocs.io/en/master/). The schema can be seen in `src/benchmarktool/runscript/schema.yml`. An example runscript can be seen in `benchmarks/examples/*/runscript.yml`. Here's an overview of the keys:

- **base_dir**
  The base directory of the benchmark. Example: `benchmarks/examples/clasp`.

- **output_dir**
  The directory to where the output (scripts and results) are generated. The path is relative to [base_dir](#base_dir). Example: `output`.

- **machines**
  Description such as CPU and memory capabilities of the machine used for the benchmarks. Currently not used.

- **configs**
  Description of the configuration to run the systems, i.e. template for the run script (might be shell scripts, etc).

- **systems**
  Description of the system (tools/solvers) on which the benchmark instances will be run against.

  - **system.measures**
    Module path to the python function of the [result parser](resultparser.md) that will be used to measure the result of this system, relative to [base_dir](#base_dir). For example, a value of `resultparser.sudokuresultparser` will use the function `sudokuresultparser` defined in `[base_dir]/resultparser.py`.

  - **system.settings**
    Description of the system's various settings, such as the `cmdline` options, `tag`, etc.

- **jobs**
  Description of various [jobs](jobs.md), including its type and resource limits.

- **benchmarks**
  Description of various benchmark instances through [specifications](instance-specs.md). Currently the specification type can be either `folder` or `doi`.

- **projects**
  Description of project, which can consists of many becnhmark runs by tags (runtags), or by manual specifications (runspecs).

---

# Generating Scripts

```sh
# pipenv shell
./bgen benchmarks/.../runscript.yml
```

After running the command, shortly the scripts will be generated in `$(base_dir)/$(output_dir)/$(project)/$(machine)` according to the runscript.

The structure of the scripts generated will depend on the job, but generally the structure will be like this:

```
[base_dir]/[output_dir]/[project]/[machine]/results/
└── start.py
└── $(benchmark)
    ├── $(system)-$(system)version]-$(system)setting]-n$(system)setting.proc]
    │   ├── $(instance_file_name)
    │   │   └── run$(run_number)
    │   │       └── start.sh
```

---

# Running the benchmark

Depending on the job, there should be a single entry point for running the benchmark in `$(base_dir)/$(output_dir)`. For example, there will be a `start.py` for a [Sequential Job](#). Just run this script to run the whole benchmark.

```sh
./benchmarks/.../output/.../start.py
```

---

# Evaluating the results

```sh
# pipenv shell
./beval benchmarks/.../runscript.yml > evaluation.xml
```

This script will collect statistics from the runs like its time and memory usage, errors etc according to the [result parser](resultparser.md) defined in the system measures.

---

# Summarizing evaluations

```
./bconv -c < evaluation.xml > result.csv
```
