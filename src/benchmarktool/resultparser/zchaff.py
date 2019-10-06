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

result_map = {'SAT': 'SATISFIABLE', 'UNSAT': 'UNSATISFIABLE', 'UNKNOWN': 'UNKNOWN'}

solver_re = {
    "seed": ("int", re.compile(r"^Random Seed Used\s*(?P<val>[0-9]+)\s*$"), lambda x: x),
    "max-decisions": ("int", re.compile(r"^Max Decision Level\s*(?P<val>[0-9]+)\s*$"), lambda x: x),
    "decisions": ("int", re.compile(r"^Num. of Decisions\s*(?P<val>[0-9]+)\s*$"), lambda x: x),
    "conflicts": ("int", re.compile(r"^\s*Added Conflict Clauses\s*(?P<val>[0-9]+)\s*$"), lambda x: x),
    "shrinkings": ("int", re.compile(r"^\s*Num of Shrinkings\s*(?P<val>[0-9]+)\s*$"), lambda x: x),
    "deletedconflictcls": ("int", re.compile(r"^\s*Deleted Conflict Clauses\s*(?P<val>[0-9]+)\s*$"), lambda x: x),
    "deletedcls": ("int", re.compile(r"^\s*Deleted Clauses\s*(?P<val>[0-9]+)\s*$"), lambda x: x),
    "conflictlits": ("int", re.compile(r"^\s*Added Conflict Literals\s*(?P<val>[0-9]+)\s*$"), lambda x: x),
    "deletedlits": ("int", re.compile(r"^\s*Deleted \(Total\) Literals\s*(?P<val>[0-9]+)\s*$"), lambda x: x),
    "implications": ("int", re.compile(r"^\s*Number of Implication\s*(?P<val>[0-9]+)\s*$"), lambda x: x),
    "#vars": ("int", re.compile(r"^\s*Original Num Variables\s*(?P<val>[0-9]+)\s*$"), lambda x: x),
    "#cls": ("int", re.compile(r"^\s*Original Num Clauses\s*(?P<val>[0-9]+)\s*$"), lambda x: x),
    "#lits": ("int", re.compile(r"^\s*Original Num Literals\s*(?P<val>[0-9]+)\s*$"), lambda x: x),
    "status": ("string", re.compile(r"^RESULT:\s(?P<val>SAT|UNSAT|UNKNOWN)\s*$"), lambda x: result_map[x])
}


def zchaff(root, runspec, instance):
    """
    Extracts some sat statistics.
    """
    return parse_solver_output(root, runspec, instance, solver_re)
