import os
import re
import sys
import codecs
from benchmarktool.tools import escape

runsolver_re = {
    "wall": ("float", re.compile(r"^Real time \(s\): (?P<val>[0-9]+(\.[0-9]+)?)$"), lambda x: x),
    "memerror": ("string", re.compile(r"^Maximum VSize (?P<val>exceeded): sending SIGTERM then SIGKILL"), lambda x: x),
    "segfault": ("string", re.compile(r"^\s*Child\s*ended\s*because\s*it\s*received\s*signal\s*11\s*\((?P<val>SIGSEGV)\)\s*"), lambda x: x),
    "time": ("float", re.compile(r"^Real time \(s\): (?P<val>[0-9]+(\.[0-9]+)?)$"), lambda x: x),
    "memusage": ("float", re.compile(r"^maximum resident set size= (?P<val>[0-9]+(\.[0-9]+)?)$"), lambda x: round(x / 1024, 2))
}


def clasp_gpusat(root, runspec, instance):
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
        'stderr': ('string', ""),
        'status': ("string", "NA"),
        'timeout': ('float', 0)
    }

    finished = True
    instance_str = instance.instance
    timeout = runspec.project.job.timeout

    # error codes: 0 = ok, 1 = timeout, 2 = memout, 4 = presolver timeout,
    #             8 = dnf, 16 = invalid decomposition, 32 = invalid input,
    #             64 = solver runtime error, 128 = unknown error

    f=""
    try:
        f = open(os.path.join(root, '%s.watcher' % instance_str)).read()
        for line in f.splitlines():
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

        errorFile = open(os.path.join(root, instance.instance + ".err"),"r").read()

        for line in content:
            for val, reg in clasp_gpusat_re.items():
                m = reg[1].match(line)
                if m: res[val] = (reg[0], float(m.group("val")) if reg[0] == "float" else m.group("val"))

        if res['wall'][1] >= timeout:
            res["timeout"] = ("float", 1)
            res["time"] = ('float', runspec.project.job.timeout)
        elif "segfault" in res:
            res["timeout"] = ("float", 1)
            res["time"] = ('float', runspec.project.job.timeout + 6)
        elif res['memerror'][1] != 'NA' or "Maximum VSize exceeded: sending SIGTERM then SIGKILL" in f:
            res["timeout"] = ("float", 1)
            res["time"] = ('float', runspec.project.job.timeout + 4)
        elif "std::bad_alloc" in content:
            res["timeout"] = ("float", 1)
            res["time"] = ('float', runspec.project.job.timeout + 4)
        elif "inf" in content:
            res["timeout"] = ("float", 1)
            res["time"] = ('float', runspec.project.job.timeout + 3)
        elif not '#models' in res:
            res["timeout"] = ("float", 1)
            res["time"] = ('float', runspec.project.job.timeout + 1)

        memout = "error" in res and res["error"][1] == "std::bad_alloc"
        timedout = memout or res['error'][1] != 0 or res['status'] == "NA" or res["wall"][1] >= timeout
        if timedout: res["timeout"] = ("float", 1)

        if res['error'][1] != 0:
            sys.stderr.write("*** ERROR: Run {0} failed with unrecognized status or error!\n".format(root))

    if not 'time' in res:
        res["timeout"] = ("float", 1)
        res["time"] = ('float', runspec.project.job.timeout + 5)

    return [(key, val[0], val[1]) for key, val in res.items()]
