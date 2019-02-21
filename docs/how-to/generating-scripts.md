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
