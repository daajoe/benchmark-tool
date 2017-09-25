'''
Created on Sep 8, 2017

@author: Johannes K. Fichte
'''

import os
import re
import sys
import codecs
from benchmarktool.tools import escape

watcher_re = {
    "time": ("float", re.compile(r"^Real time \(s\): (?P<val>[0-9]+(\.[0-9]+)?)$"), lambda x: round(x,4)),
    "time_cpu": ("float", re.compile(r"^CPU time \(s\): (?P<val>[0-9]+(\.[0-9]+)?)$"), lambda x: x),
    "cpuusage": ("float", re.compile(r"^CPU usage \(%\): (?P<val>[0-9]+(\.[0-9]+)?)$"), lambda x: float(x)),
    "memerror": ("string", re.compile(r"^Maximum VSize (?P<val>exceeded): sending SIGTERM then SIGKILL"), lambda x: x),
    "memusage": ("float", re.compile(r"^maximum resident set size= (?P<val>[0-9]+(\.[0-9]+)?)$"), lambda x: round(x/1024, 2)),
    "memusage_vmem": ("float", re.compile(r"^Max\. virtual memory \(cumulated for all children\) \(KiB\):\s*(?P<val>[0-9]+(\.[0-9]+)?)$"), lambda x: round(x/1024,2)),
    "status_retcode": ("float", re.compile(r"^Child status: (?P<val>[0-9]+(\.[0-9]+)?)$"), lambda x: int(x)),
    "context_switches_involuntary":  ("int", re.compile(r"^involuntary context switches=\s*(?P<val>[0-9]+(\.[0-9]+)?)$"), lambda x: int(x)),
    "context_switches_voluntary":  ("int", re.compile(r"^voluntary context switches=\s*(?P<val>[0-9]+(\.[0-9]+)?)$"), lambda x: int(x)),                                      
}

solver_re = {
    "status": ("string", re.compile(r"^s\s*(?P<val>SATISFIABLE|UNSATISFIABLE|UNKNOWN)\s*$"), lambda x: x)
}


#see: http://www.satcompetition.org/2004/format-solvers2004.html
sat_return_codes = (10, 20)

def sat(root, runspec, instance):
    """
    Extracts some sat statistics.
    """

    res = {
        'instance': ('string', instance.instance),
        'setting': ('string', runspec.setting.name),
        'timelimit': ('int', runspec.project.job.timeout),
        'memlimit': ('int', runspec.project.job.memout),
        'solver': ('string', runspec.system.name),
        'solver_version': ('string', runspec.system.version),
        'solver_args': ('string', escape(runspec.setting.cmdline)),
        'full_call': ('string', None),
        'full_path': ('string', root),
        'hash': ('string', None),
        'solved': ('int', 0),
        'time': ('float', 0),
        'cpuusage': ('float', 0),
        'memusage': ('float', 0),
        'memusage_vmem': ('float', 0),
        'context_switches_involuntary': ('int', 0), 
        'context_switches_voluntary': ('int', 0),
        'run': ('int', 0),
        'error': ('int', 0),
        'error_str': ('string', ""),
        'stderr': ('string', ""),
        'status': ('string', "NA"),
        'status_retcode': ('int', 0)
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
                    #always take the max instead of the last value
                    if m:
                        m_value = (reg[0], reg[2](float(m.group("val"))) if reg[0] == "float" else m.group("val"))
                        if val in res:
                            res[val] = (m_value[0], max(res[val][1], m_value[1]))
                        else:
                            res[val] = m_value

        if "memerror" in res:
            res["error_str"] = ("string", "std::bad_alloc")
            res["error"] = ("int", res["error"] + 2)
            del res["memerror"]

    except IOError, e:
        finished = False
        res['error_str'] = ('string', 'Did not finish.')

    if finished:        
        content = codecs.open(os.path.join(root, '%s.txt' % instance_str), errors='ignore', encoding='utf-8').read()
        content = content.replace(",\n]", "\n]", 1)

        for line in content.split('\n'):
            for val, reg in solver_re.items():
                m = reg[1].match(line)
                #always take the max instead of the last value
                if m:
                    m_value = (reg[0], reg[2](float(m.group("val"))) if reg[0] == "float" else m.group("val"))
                    if val in res:
                        res[val] = (m_value[0], max(res[val][1], m_value[1]))
                    else:
                        res[val] = m_value

        res["solved"] = ("int", int(res["status_retcode"][1] in sat_return_codes))
        error_status = not "status" in res or res["status"][1] == -1
        memout = "error" in res and res["error"][1] == "std::bad_alloc"
        timedout = memout or error_status or not res["solved"] or  res["time"][1] >= timeout
        
        if timedout: res["istimeout"] = ("float", timeout)
        if error_status:
            sys.stderr.write("*** ERROR: Run {0} failed with unrecognized status or error!\n".format(root))
            sys.stderr.write(str(res))
            sys.stderr.write('\n')
            exit(1)

        if "interrupted" in res: del res["interrupted"]

    return [(key, val[0], val[1]) for key, val in res.items()]
