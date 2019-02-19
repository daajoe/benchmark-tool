'''
Created on Jan 17, 2010

@author: Roland Kaminski
'''

import os
import re
import sys
import codecs

clasp_re = {
    "models"      : ("float", re.compile(r"^(c )?Models[ ]*:[ ]*(?P<val>[0-9]+)\+?[ ]*$")),
    "choices"     : ("float", re.compile(r"^(c )?Choices[ ]*:[ ]*(?P<val>[0-9]+)\+?[ ]*$")),
    "time"        : ("float", re.compile(r"^Real time \(s\): (?P<val>[0-9]+(\.[0-9]+)?)$")),
    "conflicts"   : ("float", re.compile(r"^(c )?Conflicts[ ]*:[ ]*(?P<val>[0-9]+)\+?[ ]*\(Analyzed:[ ]*(\d+(\.\d+)?)\)")),
    "conflicts_analyzed"   : ("float", re.compile(r"^(c )?Conflicts[ ]*:[ ]*([0-9]+)\+?[ ]*\(Analyzed:[ ]*(?P<val>\d+(\.\d+)?)\)")),
    "conflict":  ("float", re.compile(r"^(c[ ]*)?Conflict[ ]*:[ ]*(?P<val>[0-9]+)\+?[ ]*\(Average[ ]Length:[ ]*(\d+(\.\d+)?)[ ]*Ratio:[ ]*(\d+(\.\d+)?)%[ ]*\)")),
    "conflict_avg_length":  ("float", re.compile(r"^(c[ ]*)?Conflict[ ]*:[ ]*([0-9]+)\+?[ ]*\(Average[ ]Length:[ ]*(?P<val>\d+(\.\d+)?)[ ]*Ratio:[ ]*(\d+(\.\d+)?)%[ ]*\)")),
    "conflict_ratio":  ("float", re.compile(r"^(c[ ]*)?Conflict[ ]*:[ ]*([0-9]+)\+?[ ]*\(Average[ ]Length:[ ]*(\d+(\.\d+)?)[ ]*Ratio:[ ]*(?P<val>\d+(\.\d+)?)%[ ]*\)")),
    "restarts"    : ("float", re.compile(r"^(c )?Restarts[ ]*:[ ]*(?P<val>[0-9]+)\+?[ ]*")),
    "restarts_avg"    : ("float", re.compile(r"^(c )?Restarts[ ]*:[ ]*([0-9]+)\+?[ ]*\(Average:[ ]*(?P<val>\d+(\.\d+)?)[ ]*Last:[ ]*\d+(\.\d+)?[ ]*\)")),
    "restarts_last"    : ("float", re.compile(r"^(c )?Restarts[ ]*:[ ]*([0-9]+)\+?[ ]*\(Average:[ ]*(\d+(\.\d+)?)[ ]*Last:[ ]*(?P<val>\d+(\.\d+))?[ ]*\)")),
    "optimum"     : ("string", re.compile(r"^(c )?Optimization[ ]*:[ ]*(?P<val>(-?[0-9]+)( -?[0-9]+)*)[ ]*$")),
    "status"      : ("string", re.compile(r"^(s )?(?P<val>SATISFIABLE|UNSATISFIABLE|UNKNOWN|OPTIMUM FOUND)[ ]*$")),
    "interrupted" : ("string", re.compile(r"(c )?(?P<val>INTERRUPTED!)")),
    "error"       : ("string", re.compile(r"^\*\*\* clasp ERROR: (?P<val>.*)$")),
    "memerror"    : ("string", re.compile(r"^Maximum VSize (?P<val>exceeded): sending SIGTERM then SIGKILL")),
    "lemmas_del"    : ("float", re.compile(r"^(c )?Lemmas[ ]*:[ ]*([0-9]+)\+?[ ]*\(Deleted:[ ]*(?P<val>\d+(\.\d+)?)\)")),
    "lemmas"    : ("float", re.compile(r"^(c )?Lemmas[ ]*:[ ]*(?P<val>[0-9]+)\+?[ ]*\(Deleted:[ ]*(\d+(\.\d+)?)\)")),
    "lemmas_binary" : ("float", re.compile(r"^(c[ ]*)?Binary[ ]*:[ ]*(?P<val>[0-9]+)\+?[ ]*\(Ratio:[ ]*(\d+(\.\d+)?)%\)")),
    "lemmas_binary_ratio" : ("float", re.compile(r"^(c[ ]*)?Binary[ ]*:[ ]*([0-9]+)\+?[ ]*\(Ratio:[ ]*(?P<val>\d+(\.\d+)?)%\)")),
    "lemmas_ternary" : ("float", re.compile(r"^(c[ ]*)?Ternary[ ]*:[ ]*(?P<val>[0-9]+)\+?[ ]*\(Ratio:[ ]*(\d+(\.\d+)?)%\)")),
    "lemmas_ternary_ratio" : ("float", re.compile(r"^(c[ ]*)?Ternary[ ]*:[ ]*([0-9]+)\+?[ ]*\(Ratio:[ ]*(?P<val>\d+(\.\d+)?)%\)")),
    "backjumps": ("float", re.compile(r"^(c[ ]*)?Backjumps[ ]*:[ ]*(?P<val>[0-9]+)\+?[ ]*\(Average:[ ]*(\d+(\.\d+)?)[ ]*Max:[ ]*(\d+(\.\d+)?)[ ]*Sum:[ ]*(\d+(\.\d+)?)\)")),
    "backjumps_avg": ("float", re.compile(r"^(c[ ]*)?Backjumps[ ]*:[ ]*([0-9]+)\+?[ ]*\(Average:[ ]*(?P<val>\d+(\.\d+)?)[ ]*Max:[ ]*(\d+(\.\d+)?)[ ]*Sum:[ ]*(\d+(\.\d+)?)\)")),
    "backjumps_max": ("float", re.compile(r"^(c[ ]*)?Backjumps[ ]*:[ ]*([0-9]+)\+?[ ]*\(Average:[ ]*(\d+(\.\d+)?)[ ]*Max:[ ]*(?P<val>\d+(\.\d+)?)[ ]*Sum:[ ]*(\d+(\.\d+)?)\)")),
    "backjumps_sum": ("float", re.compile(r"^(c[ ]*)?Backjumps[ ]*:[ ]*([0-9]+)\+?[ ]*\(Average:[ ]*(\d+(\.\d+)?)[ ]*Max:[ ]*(\d+(\.\d+)?)[ ]*Sum:[ ]*(?P<val>\d+(\.\d+)?)\)")),
    "variables": ("float", re.compile(r"^(c[ ]*)?Variables[ ]*:[ ]*(?P<val>[0-9]+)\+?[ ]*\(Eliminated:[ ]*(\d+(\.\d+)?)[ ]*Frozen:[ ]*(\d+(\.\d+)?)[ ]*\)")),
    "variables_eliminated": ("float", re.compile(r"^(c[ ]*)?Variables[ ]*:[ ]*([0-9]+)\+?[ ]*\(Eliminated:[ ]*(?P<val>\d+(\.\d+)?)[ ]*Frozen:[ ]*(\d+(\.\d+)?)[ ]*\)")),
    "variables_frozen": ("float", re.compile(r"^(c[ ]*)?Variables[ ]*:[ ]*([0-9]+)\+?[ ]*\(Eliminated:[ ]*(\d+(\.\d+)?)[ ]*Frozen:[ ]*(?P<val>\d+(\.\d+)?)[ ]*\)")),
    "constraints": ("float", re.compile(r"^(c[ ]*)?Constraints[ ]*:[ ]*(?P<val>[0-9]+)\+?[ ]*\(Binary:[ ]*(\d+(\.\d+)?)%[ ]*Ternary:[ ]*(\d+(\.\d+)?)%[ ]*Other:[ ]*(\d+(\.\d+)?)%[ ]*\)")),
    "constraints_binary": ("float", re.compile(r"^(c[ ]*)?Constraints[ ]*:[ ]*([0-9]+)\+?[ ]*\(Binary:[ ]*(?P<val>\d+(\.\d+)?)%[ ]*Ternary:[ ]*(\d+(\.\d+)?)%[ ]*Other:[ ]*(\d+(\.\d+)?)%[ ]*\)")),
    "constraints_ternary": ("float", re.compile(r"^(c[ ]*)?Constraints[ ]*:[ ]*([0-9]+)\+?[ ]*\(Binary:[ ]*(\d+(\.\d+)?)%[ ]*Ternary:[ ]*(?P<val>\d+(\.\d+)?)%[ ]*Other:[ ]*(\d+(\.\d+)?)%[ ]*\)")),
    "constraints_other": ("float", re.compile(r"^(c[ ]*)?Constraints[ ]*:[ ]*([0-9]+)\+?[ ]*\(Binary:[ ]*(\d+(\.\d+)?)%[ ]*Ternary:[ ]*(\d+(\.\d+)?)%[ ]*Other:[ ]*(?P<val>\d+(\.\d+)?)%[ ]*\)"))
}

def clasp(root, runspec, instance):
    """
    Extracts some clasp statistics.
    """

    timeout = runspec.project.job.timeout
    res     = { "time": ("float", timeout) }
    for f in [instance.instance + ".txt", instance.instance + ".watcher"]:
    #for f in [instance.instance"runsolver.solver", "runsolver.watcher"]:
        for line in codecs.open(os.path.join(root, f), errors='ignore', encoding='utf-8'):
            for val, reg in clasp_re.items():
                m = reg[1].match(line)
                if m: res[val] = (reg[0], float(m.group("val")) if reg[0] == "float" else m.group("val"))
        break

    #print res["time"][1]
    if "memerror" in res:
        res["error"]  = ("string", "std::bad_alloc")
        res["status"] = ("string", "UNKNOWN")
        del res["memerror"]
    if res["time"][1] >= timeout and not "status" in res:
        #res["error"] = ("string", "timeout")
        res["status"] = ("string", "UNKNOWN")
    result   = []
    error    = not "status" in res or ("error" in res and res["error"][1] != "std::bad_alloc")
    memout   = "error" in res and res["error"][1] == "std::bad_alloc"
    status   = res["status"][1] if "status" in res else None
    timedout = memout or error or status == "UNKNOWN" or (status == "SATISFIABLE" and "optimum" in res) or res["time"][1] >= timeout or "interrupted" in res;
    if timedout: res["time"] = ("float", timeout)
    if error: 
        sys.stderr.write("*** ERROR: Run {0} failed with unrecognized status or error!\n".format(root))
        exit(1)
    result.append(("error", "float", int(error)))
    result.append(("timeout", "float", int(timedout)))
    result.append(("memout", "float", int(memout)))

    if "optimum" in res and not " " in res["optimum"][1]:
        result.append(("optimum", "float", float(res["optimum"][1])))
        del res["optimum"]
    if "interrupted" in res: del res["interrupted"]
    if "error" in res: del res["error"]
    for key, val in res.items(): result.append((key, val[0], val[1]))
    return result
