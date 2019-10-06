'''
Created on Mar 18, 2017

@author: Johannes K. Fichte
'''

import codecs
import json
import os
import re
import sys
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

dpdb_re = {
    "time": ("float", re.compile(r"^Real time \(s\): (?P<val>[0-9]+(\.[0-9]+)?)$"), lambda x: x),
    "memerror": ("string", re.compile(r"^Maximum VSize (?P<val>exceeded): sending SIGTERM then SIGKILL"), lambda x: x),
    "models": ("float", re.compile(r"^\[INFO\] dpdb\.problems\.sharpsat: Problem has (?P<val>[0-9]+) models"), lambda x: x)
}

def dpdb(root, runspec, instance):
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
        'subsolver': ('string', 'nan'),  # TODO: z3
        'solver_version': ('string', runspec.system.version),  # TODO:
        'solver_args': ('string', escape(runspec.setting.cmdline)),
        'full_call': ('string', None),
        'full_path': ('string', root),
        'num_verts': ('int', 'nan'),
        'num_hyperedges': ('int', 'nan'),
        'hash': ('string', None),  # TODO:
        'solved': ('int', 0),
        'wall': ('float', 0),
        'run': ('int', 0),
        'objective': ('float', 'nan'),
        'error': ('int', 0),
        'error_str': ('string', ''),
        'stderr': ('string', ''),
        'status': ('int', -1)
    }

    # boxing = lambda x: (type(x).__name__, x)
    # rval = lambda x: x[1]

    pbs_job = 'PbsJob' in repr(runspec.project.job)
    instance_str = instance.instance
    valid_solver_run = True
    interrupt_err = False
    dbconn_warning = False
    thread_err = False

    #TODO: next

    # ERROR HANDLING
    try:
        logfile = os.path.join(root, '%s.err' % instance_str)
        err_content = codecs.open(logfile, errors='ignore', encoding='utf-8').read()
        err_content = err_content.replace(",\n]", "\n]", 1)
        for line in err_content.splitlines():
            if not interrupt_err and '[INFO] dpdb.problem' in err_content and 'interrupted' in line:
                valid_solver_run = False
                interrupt_err = True
                res['error_str'] = ('string', res['error_str'][1] + "Python Runtime error: check logfile %s\n" %
                                    "[INFO] dpdb.problem node ... interrupted")
            if not dbconn_warning and '[WARNING] dpdb: Killing all connections' in line:
                dbconn_warning = True
                res['error_str'] = ('string', res['error_str'][1] + "Python Runtime error: check logfile %s\n" %
                                    "[WARNING] dpdb: Killing all connections")
            if not thread_err and '[ERROR] dpdb.problem: Error in worker thread' in line:
                thread_err = True
                res['error_str'] = ('string', res['error_str'][1] + "Python Runtime error: check logfile %s\n" %
                                    "[ERROR] dpdb.problem: Error in worker thread")
            # noinspection DuplicatedCode
            for val, reg in dpdb_re.items():
                m = reg[1].match(line)
                if m: res[val] = (reg[0], reg[2](float(m.group("val"))) if reg[0] == "float" else m.group("val"))

    except IOError:
        sys.stderr.write('Missing Error file for instance %s.\n' % root)

    runsolver_error = False
    # WATCHER DATA HANDLING
    if pbs_job:
        try:
            f = codecs.open(os.path.join(root, '%s.watcher' % instance_str), errors='ignore', encoding='utf-8').read()
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

    else:
        log_content = open(os.path.join(root, "condor.log")).read()
        # ret = 9: runsolver error (heavy process)
        finished = log_content.find('Normal termination') >= 0 or log_content.find(
            'Abnormal termination (signal 9)') >= 0
        if not finished:
            sys.stderr.write('instance %s did not finish properly\n' % root)

    # READ RESULT OUTPUT FROM SOLVER
    stats = {}
    error = 0
    cluster_error = False

    # OUTPUT is not done properly
    # try:
    #     # errors='ignore',
    #     content = codecs.open(os.path.join(root, '%s.txt' % instance_str), encoding='utf-8').read()
    #     valid_json = True
    #
    #     try:
    #         stats = json.loads(content)
    #     except ValueError, e:
    #         sys.stderr.write('Error (invalid JSON): %s ("%s"); %s\n' % (instance.instance, root, str(e)))
    #         res['error_str'] = ('string', res['error_str'][1] + str(e))
    #         valid_json = False
    #
    # except IOError:
    #     sys.stderr.write('Instance %s did not finish properly. Missing output file.\n' % root)
    #     cluster_error = True

    # error codes: 0 = ok, 1 = timeout, 2 = memout, 64 = invalid output, 128 = program runtime error,
    # 256 = runsolver error/glitch, 512 = error signal handling, 1024 = cluster run error
    # 2048 = invalid result, 4096 = cplex license issue
    error += int(res['timeout'][1])
    error += int(res['memout'][1]) * 2
    # error += int(not valid_json) * 64
    error += int(not valid_solver_run) * 128
    error += int(runsolver_error) * 256
    error += int(interrupt_err) * 512
    error += int(dbconn_warning) *1024
    error += int(thread_err) * 2048

    res['error'] = ('int', error)

    try:
        res['wall'] = ('float', stats['wall'])
        res['solved'] = ('int', int(stats['solved']))
    except KeyError, e:
        pass

    #TODO: twins

    def nan_or_value(tpl, stats):
        try:
            return (tpl[0], stats[tpl[1]])
        except KeyError, e:
            return (tpl[0], 'nan')

    # PROBLEM/SOLVER SPECIFIC OUTPUT
    if error == 0:
        res['objective'] = nan_or_value(('float', 'width'), stats)

        try:
            res['hash'] = ('string', stats['hash'][0:16] + '*')
            cut = os.path.join(*instance.location.split('/')[1:])
            index = stats['instance'].find(cut)
            if index != -1:
                res['instance_path'] = ('string', stats['instance'][index + len(cut) + 1:])
        except KeyError, e:
            # sys.stderr.write('Missing attribute "%s" for instance "%s".\n' % (str(e), root))
            pass
        try:
            res['full_call'] = ('string', b64encode(stats['call']))
        except KeyError:
            res['full_call'] = ('string', 'nan')
            # sys.stderr.write('Could not find "call" in json values (instance = %s).\n' % root)

    return [(key, val[0], val[1]) for key, val in res.items()]
