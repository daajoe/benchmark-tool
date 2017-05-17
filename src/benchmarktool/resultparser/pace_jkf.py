'''
Created on Mar 18, 2017

@author: Johannes K. Fichte
'''

import os
import re
import sys
import codecs
import json
from base64 import b64encode
from benchmarktool.tools import escape

pace_jkf_re = {
    "time": ("float", re.compile(r"^Real time \(s\): (?P<val>[0-9]+(\.[0-9]+)?)$")),
    "memerror": ("string", re.compile(r"^Maximum VSize (?P<val>exceeded): sending SIGTERM then SIGKILL")),
}


def pace_jkf(root, runspec, instance):
    """
    Extracts some clingo statistics.
    """
    error = 0
    e_str = ''
    stderr = ''
    timeout = runspec.project.job.timeout
    res = {"time": ("float", timeout)}

    pbs_job = 'PbsJob' in repr(runspec.project.job)

    # {{{1 parse runsolver data
    # pbs runs use currently different filename
    if pbs_job:
        instance_str = 'runsolver'
    else:
        instance_str = instance.instance

    accu = {
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
        'solved': ('int', -1),
        'wall': ('float', 0),
        'run': ('int', 0),
        'width': ('int', -1),
        'error': ('int', error),
        'error_str': ('string', e_str),
        'stderr': ('string', stderr),
        'ubound': ('int', -1),
        'last_improved_in_round': ('int', 0),
        'rounds': ('int', 0),
        'rounds_improved': ('int', 0),
    }

    try:
        for f in ['%s.watcher' % instance_str]:
            for line in codecs.open(os.path.join(root, f), errors='ignore', encoding='utf-8'):
                for val, reg in pace_jkf_re.items():
                    m = reg[1].match(line)
                    if m: res[val] = (reg[0], float(m.group("val")) if reg[0] == "float" else m.group("val"))

    except IOError, e:
        finished = False
        accu['error_str'] = ('string', 'Did not finish.')
        return [(key, val[0], val[1]) for key, val in accu.items()]

    # {{{1 parse solver stdout
    content = codecs.open(os.path.join(root, '%s.%s' % (instance_str, 'solver' if pbs_job else 'txt')), errors='ignore',
                          encoding='utf-8').read()
    content = content.replace(",\n]", "\n]", 1)

    # TD specific validations

    valid_td = int('invalid' not in content)
    valid_input = int('vertices missing:' not in content and 'edges missing:' not in content)

    memed_out = False
    if "memerror" in res:
        memed_out = True
        del res["memerror"]

    timed_out = res["time"][1] >= timeout

    err_content = codecs.open(os.path.join(root, '%s.err' % instance_str), errors='ignore',
                              encoding='utf-8').read()
    err_content = err_content.replace(",\n]", "\n]", 1)

    presolver_timed_out = False
    if 'htd returned "124"' in err_content:
        presolver_timed_out = True

    if 'UnboundLocalError: local variable \'fstream\' referenced before assignment' in err_content:
        valid_input = False

    if pbs_job:
        log_content = open(os.path.join(root, 'runsolver.watcher')).read()
        finished = log_content.find('Child status: 0') >= 0
        # to = log_content.find('Child ended because it received signal 15 (SIGTERM)') >=0
        if not finished and instance.instance not in ['move.sh', 'results.txt'] and not presolver_timed_out and \
                not timed_out and valid_input and valid_td:
            sys.stderr.write('instance %s did not finish properly\n' % root)
            # sys.stderr.write(log_content[log_content.find('Child status:'):log_content.find('Child status:') + 20])
            # sys.stderr.write('\n')
    else:
        log_content = open(os.path.join(root, "condor.log")).read()
        # ret = 9: runsolver error (heavy process)
        finished = log_content.find('Normal termination') >= 0 or log_content.find(
            'Abnormal termination (signal 9)') >= 0
        if not finished:
            sys.stderr.write('instance %s did not finish properly\n' % root)

    valid_solver_run = 'Traceback (most recent call last):' not in err_content

    # error codes: 0 = ok, 1 = timeout, 2 = memout, 4 = presolver timeout,
    #             8 = dnf, 16 = invalid decomposition, 32 = invalid input,
    #             64 = solver runtime error, 128 = unknown error
    error = 0
    error += int(timed_out)
    error += int(memed_out) * 2
    error += int(not finished) * 4
    error += int(presolver_timed_out) * 8
    error += int(not valid_td) * 16
    error += int(not valid_input) * 32
    # only if instance did not timed out or memed out
    error += int(not valid_solver_run and not 1 < error < 4) * 64

    try:
        stats = json.loads(content)
    except ValueError, e:
        stats = {}
        if error == 0:
            sys.stderr.write('Error: %s (%s); %s\n' % (instance.instance, root, str(e)))
            error = 64
            e_str = str(e)
            with open(os.path.join(root, '%s.err' % instance_str)) as fstderr:
                stderr = fstderr.read().replace('\n', ' ').replace('  ', '')

    # TODO: additional parameters
    try:
        accu['wall'] = ('float', stats['wall'])
        accu['solved'] = ('int', int(stats['solved']))
    except KeyError, e:
        pass

    if not error:
        try:
            accu['run'] = ('int', stats['run'])
            accu['width'] = ('int', stats['width'])
            accu['hash'] = ('string', stats['hash'][0:16] + '*')
            accu['ubound'] = ('int', stats['ubound'])
            accu['last_improved_in_round'] = ('int', stats['last_improved_in_round'])
            accu['rounds'] = ('int', stats['rounds'])
            accu['rounds_improved'] = ('int', stats['rounds_improved'])

            cut = os.path.join(*instance.location.split('/')[1:])
            index = stats['instance'].find(cut)
            if index != -1:
                accu['instance_path'] = ('string', stats['instance'][index + len(cut) + 1:])
        except KeyError, e:
            sys.stderr.write('Missing attribute "%s" for instance "%s".\n' % (str(e), root))
        try:
            accu['full_call'] = ('string', b64encode(stats['call']))
        except KeyError:
            accu['full_call'] = ('string', 'NA')
            # sys.stderr.write('Could not find "call" in json values (instance = %s).\n' % root)

    for key, val in accu.items():
        res[key] = val  # ("float", val)

    res['timeout'] = ("int", int(timed_out))
    res["memout"] = ("float", int(memed_out))
    res["error"] = ("int", error)
    res['td_validator'] = ('int', valid_td)
    res['valid_input'] = ('int', valid_input)

    # if instance.instance == 'timt4stic_20110831_0329.gml.lp.gr':
    #     sys.stderr.write('error = %s\n' % error)
    #     sys.stderr.write('error = %s\n' %res["error"][1])
    #     exit(1)

    return [(key, val[0], val[1]) for key, val in res.items()]
