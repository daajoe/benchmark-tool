'''
Created on Mar 18, 2017

@author: Johannes K. Fichte
'''

import os
import re
import sys
import codecs
import json

dynasp_jkf_re = {
    "time": ("float", re.compile(r"^Real time \(s\): (?P<val>[0-9]+(\.[0-9]+)?)$")),
    "memerror": ("string", re.compile(r"^Maximum VSize (?P<val>exceeded): sending SIGTERM then SIGKILL")),
}


def dynasp_jkf(root, runspec, instance):
    """
    Extracts some clingo statistics.
    """
    #comma in instance name problems
    raise NotImplementedError('TODO')
    error = 0
    e_str = ''
    stderr = ''
    timeout = runspec.project.job.timeout
    res = {"time": ("float", timeout)}
    # {{{1 parse runsolver data
    for f in ['%s.watcher' % instance.instance]:
        for line in codecs.open(os.path.join(root, f), errors='ignore', encoding='utf-8'):
            for val, reg in pace_jkf_re.items():
                m = reg[1].match(line)
                if m: res[val] = (reg[0], float(m.group("val")) if reg[0] == "float" else m.group("val"))

    # {{{1 parse solver stdout
    # the runsolver combines both stderr and stdout
    # (should add an option to manually workaround this bizarre design decision)
    content = codecs.open(os.path.join(root, '%s.txt' % instance.instance), errors='ignore', encoding='utf-8').read()
    content = content.replace(",\n]", "\n]", 1)
    try:
        stats = json.loads(content)
    except ValueError, e:
        sys.stderr.write(str(e))
        sys.stderr.write('instance = %s\n' %instance.instance)
        error = 1
        e_str = str(e)
        with open(os.path.join(root,'%s.err' %instance.instance)) as fstderr:
            stderr=fstderr.read().replace('\n',' ').replace('  ','')
    accu = {
        'instance': ('string', instance.instance),
        'setting': ('string', runspec.setting.name),
        'timeout': ('int', runspec.project.job.timeout),
        'memout': ('int', runspec.project.job.memout),
        'solver': ('string', runspec.system.name),
        'solver_version': ('string', runspec.system.version),
        'solver_args': ('string', runspec.setting.cmdline),
        'full_call': ('string', None),
        'num_edges': ('int', None),
        'num_verts': ('int', None),
        'hash': ('string', None),
        'solved': ('int',-1),
        'wall': ('float', 0),
        'run': ('int', 0),
        'width': ('int',-1),
        'error': ('int', error),
        'error_str': ('string', e_str),
        'stderr': ('string', stderr)
    }
    #TODO: additional parameters
    if not error:
        try:
            accu['run'] = ('int', stats['run'])
            accu['full_call'] = ('string', stats['call'])
            accu['width'] = ('int', stats['width'])
            accu['solved'] = ('int', int(stats['solved']))
            accu['wall'] = ('float', stats['wall'])
            accu['hash'] = ('string', stats['hash'][0:16] + '*')
            accu['num_verts'] = ('int', stats['inputgraph_max_verts'])
            accu['num_egdes'] = ('int', stats['inputgraph_max_edges'])
            cut = os.path.join(*instance.location.split('/')[1:])
            index = stats['instance'].find(cut)
            if index != -1:
                accu['instance_path'] = ('string', stats['instance'][index+len(cut)+1:])
        except KeyError:
            sys.stderr.write("instance " + root + " did not finish properly\n")

    # {{{1 parse solver stdout
    content = open(os.path.join(root, "condor.log")).read()
    finished = content.find("Normal termination") >= 0
    if not finished:
        sys.stderr.write("instance " + root + " did not finish properly\n")

    # {{{1 output result
    memedout = False
    if "memerror" in res:
        memedout = True
        del res["memerror"]

    error = memedout or not finished
    timedout = res["time"][1] >= timeout or memedout or error
    res["timeout"] = ("float", int(timedout))
    res["memout"] = ("float", int(memedout))
    res["error"] = ("float", int(error))
    for key, val in accu.items():
        res[key] = val #("float", val)
    return [(key, val[0], val[1]) for key, val in res.items()]
