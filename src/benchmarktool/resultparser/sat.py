'''
Created on Sep 8, 2017

@author: Johannes K. Fichte
'''

import os
import re
import sys
import codecs
from benchmarktool.tools import escape

sat_re = {
    "wall": ("float", re.compile(r"^Real time \(s\): (?P<val>[0-9]+(\.[0-9]+)?)$"), lambda x: x),
    "memerror": ("string", re.compile(r"^Maximum VSize (?P<val>exceeded): sending SIGTERM then SIGKILL"), lambda x: x),
    "memusage": ("float", re.compile(r"^maximum resident set size= (?P<val>[0-9]+(\.[0-9]+)?)$"), lambda x: round(x / 1024,2))
}


def sat(root, runspec, instance):
    """
    Extracts some sat statistics.
    """

    res = {
        'instance': ('string', instance.instance),
        'setting': ('string', runspec.setting.name),
        'timelimit': ('int', runspec.project.job.timeout),
        'memlimit': ('int', runspec.project.job.memout),
        'memerror': ('string', 'NA'),
        'solver': ('string', runspec.system.name),
        'solver_version': ('string', runspec.system.version),
        'solver_args': ('string', escape(runspec.setting.cmdline)),
        'full_call': ('string', None),
        'full_path': ('string', root),
        'hash': ('string', None),
        'solved': ('int', -1),
        'wall': ('float', 0),
        'memusage': ('float', 0),
        'run': ('int', 0),
        'error': ('int', 0),
        'error_str': ('string', ""),
        'stderr': ('string', "")
    }

    finished = True
    instance_str = instance.instance
    timeout = runspec.project.job.timeout

    # error codes: 0 = ok, 1 = timeout, 2 = memout, 4 = presolver timeout,
    #             8 = dnf, 16 = invalid decomposition, 32 = invalid input,
    #             64 = solver runtime error, 128 = unknown error

    try:
        for f in ['%s.watcher' % instance_str]:
            for line in codecs.open(os.path.join(root, f), encoding='utf-8'):
                for val, reg in sat_re.items():
                    m = reg[1].match(line)
                    if m: res[val] = (reg[0], res[2](float(m.group("val"))) if reg[0] == "float" else m.group("val"))

        if "memerror" in res and res['memerror'] != 'NA':
            res["error_str"] = ("string", "std::bad_alloc")
            res["error"] = ("int", 2)
            res["status"] = ("string", "UNKNOWN")
            del res["memerror"]

    except IOError, e:
        finished = False
        res['error_str'] = ('string', 'Did not finish.')

    if finished:
        content = codecs.open(os.path.join(root, '%s.txt' % instance_str), errors='ignore', encoding='utf-8').read()
        content = content.replace(",\n]", "\n]", 1)



        result = []
        error = not "status" in res or ("error" in res and res["error"][1] != "std::bad_alloc")
        memout = "error" in res and res["error"][1] == "std::bad_alloc"
        status = res["status"][1] if "status" in res else None

        timedout = memout or error or status == "UNKNOWN" or (status == "SATISFIABLE" and "optimum" in res) or \
                   res["time"][
                       1] >= timeout or "interrupted" in res;
        if timedout: res["istimeout"] = ("float", timeout)
        if error: sys.stderr.write("*** ERROR: Run {0} failed with unrecognized status or error!\n".format(root))

        if "optimum" in res and not " " in res["optimum"][1]:
            result.append(("optimum", "float", float(res["optimum"][1])))
            del res["optimum"]
        if "interrupted" in res: del res["interrupted"]
        if "error" in res: del res["error"]
        for key, val in res.items(): result.append((key, val[0], val[1]))

    return [(key, val[0], val[1]) for key, val in res.items()]
