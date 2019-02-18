# sudoku-solver

Solve sudoku puzzles using python and a sat solver as fast as possible. The solver has a performance profiler builtin.

The python binding of [cryptominisat](https://github.com/msoos/cryptominisat) (named pycryptosat) is being used to solve the sudokus.

There are many example sudoku puzzles of various sizes in the `examples/sudokus` dir.

## Setup

* create virtualenv `virtualenv3 .env`
* activate virtualenv `source .env/bin/activate`
* install requirements `pip install -r .requirements`
* *optional:* leave virtualenv `deactivate`

## Usage

`main.py [-h] [--profiler] PATH`

##### positional arguments:
* `PATH` the sudoku puzzle to solve

##### optional arguments:
* `-h`, `--help` show this help message and exit
* `--profiler` run the performance profiler (this will slow down the solver significantly)

The solver will write some debug output to the `out` dir.

### Example

Run the parser and solver for a 9x9 sudoku without the profiler:

`python main.py examples/sudokus/table9-1.txt`
