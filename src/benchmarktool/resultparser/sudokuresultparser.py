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

pace_jkf_re = {
    "time": ("float", re.compile(r"^Real time \(s\): (?P<val>[0-9]+(\.[0-9]+)?)$")),
    "memerror": ("string", re.compile(r"^Maximum VSize (?P<val>exceeded): sending SIGTERM then SIGKILL")),
}


def sudokuresultparser(root, runspec, instance):
    """
    Extracts some clingo statistics.
    """

    # DEFAULT VALUES
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
        # 'num_verts': ('int', 'nan'),
        # 'num_hyperedges': ('int', 'nan'),
        'hash': ('string', None),  # TODO:
        'solved': ('int', 0),
        'wall': ('float', 0),
        'run': ('int', 0),
        # 'objective': ('float', 'nan'),
        'error': ('int', 0),
        # 'error_str': ('string', ''),
        # 'stderr': ('string', ''),
        # TODO: valid sudokuo
        'status': ('int', -1)
    }

    # to call this resultparser
    # ./beval runscripts/sudoku2019.xml

    # TODO:
    # 1) parse the output form the sudoku solver
    # 2) validate the output (valid sudoku or not) using programs/sudoku_validate-1.0  / Subprocess
    # 3) summarize the suff


    # boxing = lambda x: (type(x).__name__, x)
    # rval = lambda x: x[1]

    pbs_job = 'PbsJob' in repr(runspec.project.job)
    instance_str = instance.instance
    valid_solver_run = True
    signal_handling_error = False
    invalid_result = False
    cplex_license_issue = False
    grounding_error = False

    # ERROR HANDLING
    try:
        logfile = os.path.join(root, 'runsolver.err')
        err_content = codecs.open(logfile, errors='ignore', encoding='utf-8').read()
        err_content = err_content.replace(",\n]", "\n]", 1)

        if 'raise TimeoutException(\'signal\')' in err_content or 'SIGNAL received' in err_content:
            res['timeout'] = ('int', 1)
            signal_handling_error = True
        elif 'MemoryError: std::bad_alloc' in err_content or 'z3.z3types.Z3Exception: out of memory' in err_content:
            res['memout'] = ('int', 1)
            grounding_error = True
        elif 'ERROR in Tree Decomposition' in err_content:
            invalid_result = True
        elif 'cplex.exceptions.errors.CplexSolverError: CPLEX Error  1016: Promotional version. Problem size limits exceeded.' in err_content:
            cplex_license_issue = True
        elif 'Traceback (most recent call last):' in err_content:
            res['error_str'] = ('string', res['error_str'][1] + "Python Runtime error: check logfile %s\n" % logfile)
            valid_solver_run = False

    except IOError:
        sys.stderr.write('Missing Error file for instance %s.\n' % root)

    #full call
    #runsolver
    #command line: ../../../../../../../../programs/runsolver-3.3.6 -M 8192 -W 7200 -w ../../../../../../../../output/fhtd-hypergraphs/behemoth/results/hyperbench-csp_other/fhtd-0.7-default-n1/./2bitcomp_5.hg/run1/2bitcomp_5.hg.watcher ../../../../../../../../programs/fhtd-0.\
    #7 -t /tmp/3258669.1.all.q --runid 1 -f ../../../../../../../../benchmarks/hypergraphs/hyperbench/csp_other/2bitcomp_5.hg

    runsolver_error = False
    # WATCHER DATA HANDLING
    try:
        f = codecs.open(os.path.join(root, 'runsolver.watcher'), errors='ignore', encoding='utf-8').read()
        for line in f.splitlines():
            for val, reg in runsolver_re.items():
                m = reg[1].match(line)
                if m: res[val] = (reg[0], reg[2](float(m.group("val"))) if reg[0] == "float" else m.group("val"))
                
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
        except KeyError, e:
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

#    if not pbs_job:
#        log_content = open(os.path.join(root, "condor.log")).read()
#        # ret = 9: runsolver error (heavy process)
#        finished = log_content.find('Normal termination') >= 0 or log_content.find(
#            'Abnormal termination (signal 9)') >= 0
#        if not finished:
#            sys.stderr.write('instance %s did not finish properly\n' % root)
        

            

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
        validator = 'programs/sudoku_validate-1.0'
        validator_output = subprocess.check_output("./%s -f %s" % (validator, output_file), shell=True)
    except IOError:
        sys.stderr.write('Instance %s did not finish properly. Missing output file.\n' % root)
        cluster_error = True
    except subprocess.CalledProcessError:
        sys.stderr.write('Instance %s did not output anything. Empty output file.\n' % root)
        error += 64

    # error codes: 0 = ok, 1 = timeout, 2 = memout, 64 = invalid output, 128 = program runtime error,
    # 256 = runsolver error/glitch, 512 = error signal handling, 1024 = cluster run error
    # 2048 = invalid result, 4096 = cplex license issue
    error += int(res['timeout'][1])
    error += int(res['memout'][1]) * 2
   #  error += int(not valid_json) * 64
    error += int(not valid_solver_run) * 128
    error += int(runsolver_error) * 256
    error += int(signal_handling_error) * 512
    error += int(cluster_error) *1024
    error += int(invalid_result) * 2048
    error += int(cplex_license_issue) * 4096
    error += int(grounding_error) * 8192

    res['error'] = ('int', error)

    is_valid = True

    if validator_output is None or 'NOT CORRECT' in validator_output:
        is_valid = False

    def clean_empty_lines(inp):
        result = []
        for line in inp:
            if line != "":
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
    #except KeyError, e:
    #    pass

    #TODO: twins

    def nan_or_value(tpl, stats):
        try:
            return (tpl[0], stats[tpl[1]])
        except KeyError, e:
            return (tpl[0], 'nan')

    # PROBLEM/SOLVER SPECIFIC OUTPUT

    return [(key, val[0], val[1]) for key, val in res.items()]