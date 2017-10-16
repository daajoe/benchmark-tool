import os
import re
import sys
import codecs
from benchmarktool.tools import escape

runsolver_re = {
    "wall": ("float", re.compile(r"^Real time \(s\): (?P<val>[0-9]+(\.[0-9]+)?)$"), lambda x: x),
    "memerror": ("string", re.compile(r"^Maximum VSize (?P<val>exceeded): sending SIGTERM then SIGKILL"), lambda x: x),
    "time": ("float", re.compile(r"^Real time \(s\): (?P<val>[0-9]+\.[0-9]+)$"), lambda x: x),
    "memusage": ("float", re.compile(r"^maximum resident set size= (?P<val>[0-9]+(\.[0-9]+)?)$"), lambda x: round(x, 2))
}

cachet_re = {
    "#models": ("float", re.compile(r"^\s*Number of solutions\s*(?P<val>\d*\.\d+|\d+|\d*\.\d+e[-+]\d+)\s*$")),
    "#lit": ("float", re.compile(r"^\s*Original Num Literals\s*(?P<val>\d*\.\d+|\d+|\d*\.\d+e[-+]\d+)\s*$")),
    "#clauses": ("float", re.compile(r"^\s*Original Num Clauses\s*(?P<val>\d*\.\d+|\d+|\d*\.\d+e[-+]\d+)\s*$")),
    "#var": ("float", re.compile(r"^\s*Number of Variables\s*(?P<val>\d*\.\d+|\d+|\d*\.\d+e[-+]\d+)\s*$")),
    "#desicions": ("float", re.compile(r"^\s*Number of Decisions\s*(?P<val>\d*\.\d+|\d+|\d*\.\d+e[-+]\d+)\s*$"))
}


def cachet(root, runspec, instance):
    """
    Extracts some sat statistics.
    """
    #TODO: merge with regular sat
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
        'stderr': ('string', ""),
        'status': ("string", "NA"),
        'istimeout': ('int', 0)
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
                for val, reg in runsolver_re.items():
                    m = reg[1].match(line)
                    if m: res[val] = (reg[0], reg[2](float(m.group("val"))) if reg[0] == "float" else m.group("val"))

        if res['memerror'][1] != 'NA':
            res["error_str"] = ("string", "std::bad_alloc")
            res["error"] = ("int", 2)

    except IOError, e:
        finished = False
        res['error_str'] = ('string', 'Did not finish.')

    if finished:
        # errors='ignore',
        content = codecs.open(os.path.join(root, '%s.txt' % instance_str), encoding='utf-8')

        for line in content:
            for val, reg in cachet_re.items():
                m = reg[1].match(line)
                if m: res[val] = (reg[0], float(m.group("val")) if reg[0] == "float" else m.group("val"))

        if res['#models'] > 0:
            res["status"] = ("string", "SAT")
        elif res['#models'] == 0:
            res["status"] = ("string", "UNSAT")

        memout = "error" in res and res["error"][1] == "std::bad_alloc"
        timedout = memout or res['error'][1] != 0 or res['status'] == "NA" or res["wall"][1] >= timeout
        if timedout: res["istimeout"] = ("int", 1)

        if res['error'][1] != 0:
            sys.stderr.write("*** ERROR: Run {0} failed with unrecognized status or error!\n".format(root))

    return [(key, val[0], val[1]) for key, val in res.items()]