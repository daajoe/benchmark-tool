'''
Created on Sep 8, 2017

@author: Johannes K. Fichte
'''

import os
import re
import sys
import codecs
from benchmarktool.tools import escape
from benchmarktool.resultparser.sat import parse_solver_output

solver_re = {
    "status": ("string", re.compile(r"^s\s*(?P<val>SATISFIABLE|UNSATISFIABLE|UNKNOWN)\s*$"), lambda x: x),
    "restarts": ("int", re.compile(r"^restarts\s*:\s(?P<val>[0-9]+)\s*$")),
    "conflicts": ("int", re.compile(r"^conflicts\s*:\s(?P<val>[0-9]+)\s*$")),
    "decisions": ("int", re.compile(r"^decisions\s*:\s(?P<val>[0-9]+)\s*$")),
    "propagations": ("int", re.compile(r"^propagations\s*:\s(?P<val>[0-9]+)\s*$")),
    "conflict literals": ("int", re.compile(r"^conflict literals\s*:\s(?P<val>[0-9]+)\s*$")),
    "#vars": ("int", re.compile(r"^\|\s*Number of variables\s*:\s*(?P<val>[0-9]+)\s*\|$")),
    "#cls": ("int", re.compile(r"^\|\s*Number of clauses\s*:\s*(?P<val>[0-9]+)\s*\|$"))
}


def minisat(root, runspec, instance):
    """
    Extracts some sat statistics.
    """
    return parse_solver_output(root, runspec, instance, solver_re)
