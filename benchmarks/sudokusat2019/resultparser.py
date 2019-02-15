'''
Created on Mar 18, 2017
@author: Johannes K. Fichte
'''

import codecs
import json
import os
import re
import sys
import subprocess
from base64 import b64encode

from benchmarktool.tools import escape

runsolver_re = {
    "wall": ("float", re.compile(r"^Real time \(s\): (?P<val>[0-9]+(\.[0-9]+)?)$"), lambda x: x),
    "memerror": ("string", re.compile(r"^Maximum VSize (?P<val>exceeded): sending SIGTERM then SIGKILL"), lambda x: x),
    "segfault": (
        "string", re.compile(r"^\s*Child\s*ended\s*because\s*it\s*received\s*signal\s*11\s*\((?P<val>SIGSEGV)\)\s*"),
        lambda x: x),
    "time": ("float", re.compile(r"^Real time \(s\): (?P<val>[0-9]+(\.[0-9]+)?)$"), lambda x: x),
    "memusage": (
        "float", re.compile(r"^maximum resident set size= (?P<val>[0-9]+(\.[0-9]+)?)$"), lambda x: round(x / 1024, 2)),
    "status": ("int", re.compile(r"Child status: (?P<val>[0-9]+)"), lambda x: x),
    "cumcpu_time": (
    "float", re.compile("Current children cumulated CPU time \(s\)\s(?P<val>[0-9]+(\.[0-9]+)?)$"), lambda x: x)
}


def sudokuresultparser(root, runspec, instance):
    res = {
        'instance': ('string', instance.instance),
        'setting': ('string', runspec.setting.name),
        'timelimit': ('int', runspec.project.job.timeout),
        'memlimit': ('int', runspec.project.job.memout),
        'memerror': ('string', 'nan'),
        'timeout': ('int', -1),
        'memout': ('int', -1),
        'solver': ('string', runspec.system.name),
        'solver_args': ('string', escape(runspec.setting.cmdline)),
        'full_call': ('string', None),
        'full_path': ('string', root),
        'hash': ('string', None),  # TODO:
        'solved': ('int', 0),
        'wall': ('float', 0),
        'run': ('int', 0),
        'objective': ('int', 0),
        'error': ('int', 0),
        'status': ('int', -1)
    }

    instance_str = instance.instance
    valid_solver_run = True
    signal_handling_error = False

    # ERROR HANDLING
    try:
        logfile = os.path.join(root, 'runsolver.err')
        err_content = codecs.open(logfile, errors='ignore', encoding='utf-8').read()
        err_content = err_content.replace(",\n]", "\n]", 1)

        if 'raise TimeoutException(\'signal\')' in err_content or 'SIGNAL received' in err_content:
            res['timeout'] = ('int', 1)
            signal_handling_error = True
        elif 'Traceback (most recent call last):' in err_content:
            res['error_str'] = ('string', res['error_str'][1] + "Python Runtime error: check logfile %s\n" % logfile)
            valid_solver_run = False

    except IOError:
        sys.stderr.write('Missing Error file for instance %s.\n' % root)


    runsolver_error = False
    try:
        f = codecs.open(os.path.join(root, 'runsolver.watcher'), errors='ignore', encoding='utf-8').read()
        for line in f.splitlines():
            for val, reg in runsolver_re.items():
                m = reg[1].match(line)
                if m:
                    parser = str
                    if reg[0] == 'float': parser = float
                    elif reg[0] == 'int': parser = int

                    res[val] = (reg[0], reg[2](parser(m.group("val"))))
                
        if res['memerror'][1] != 'nan':
            res["error_str"] = ("string", "std::bad_alloc")
            res["error"] = ("int", 2)
            res['memout'] = ("int", 1)
        else:
            res['memout'] = ("int", 0)

        try:
            res['timeout'] = ('int', int(res["time"][1] >= res['timelimit'][1]))
            if 'cumcpu_time' in res:
                del res['cumcpu_time']
        except KeyError:
            # sometimes we obtain lost times during runs
            # we report them here but note that there was a runsolver error
            res['time'] = res['cumcpu_time']
            res['timeout'] = ('int', int(res["time"][1] >= res['timelimit']))
            runsolver_error = True
            
        res['finished'] = ('int', int(res['status'][1] >= 0))
        # to = log_content.find('Child ended because it received signal 15 (SIGTERM)') >=0
        if not res['finished']:
            sys.stderr.write('instance %s did not finish properly\n' % root)
    except IOError:
        res['error_str'] = ('string', 'Did not finish.')
        return [(key, val[0], val[1]) for key, val in res.items()]


    # READ RESULT OUTPUT FROM SOLVER
    validator_output = None
    content = None
    stats = {}
    error = 0
    cluster_error = False
    instance_output = None

    try:
        instance_output = codecs.open(os.path.join(root, 'runsolver.solver'), encoding='utf-8').read()
        output_file = os.path.join(root, 'runsolver.solver')
        validator = 'benchmarks/sudokusat2019/bin/sudoku_validate-1.0'
        validator_output = subprocess.check_output("./%s -f %s" % (validator, output_file), shell=True, encoding='utf-8')
    except IOError:
        sys.stderr.write('Instance %s did not finish properly. Missing output file.\n' % root)
        cluster_error = True
    except subprocess.CalledProcessError as e:
        sys.stderr.write('Instance %s did not output anything or output format is wrong.\n' % root)
        error += 64

    # error codes: 0 = ok, 1 = timeout, 2 = memout, 64 = invalid output, 128 = program runtime error,
    # 256 = runsolver error/glitch, 512 = error signal handling, 1024 = cluster run error
    # 2048 = invalid result, 4096 = cplex license issue
    error += int(res['timeout'][1])
    error += int(res['memout'][1]) * 2
    # error += int(not valid_json) * 64
    error += int(not valid_solver_run) * 128
    error += int(runsolver_error) * 256
    error += int(signal_handling_error) * 512
    error += int(cluster_error) * 1024

    res['error'] = ('int', error)

    is_valid = True

    if validator_output is None or 'NOT CORRECT' in validator_output:
        is_valid = False

    def clean_empty_lines(inp):
        result = []
        for line in inp:
            if line != "" and line != "\n":
                result.append(line)
        return result

    # Validate if output is consistent with input
    instance_input = codecs.open(os.path.join(instance.location, instance.instance), encoding='utf-8').read()

    instance_output = clean_empty_lines(instance_output.split('\n'))
    instance_input = clean_empty_lines(instance_input.split('\n'))

    if len(instance_output) < len(instance_input):
        is_valid = False
    else:
        for i in range(4,len(instance_input)):
            for j, char in enumerate(instance_input[i]):
                if char != '_' and instance_output[i][j] != char:
                    is_valid = False
                    break


    #try:
    # res['wall'] = ('float', stats['wall'])
    res['solved'] = ('int', int(is_valid))
    res['objective'] = ('int', int(is_valid))
    #except KeyError, e:
    #    pass


    def nan_or_value(tpl, stats):
        try:
            return (tpl[0], stats[tpl[1]])
        except KeyError:
            return (tpl[0], 'nan')

    # PROBLEM/SOLVER SPECIFIC OUTPUT

    return [(key, val[0], val[1]) for key, val in res.items()]
