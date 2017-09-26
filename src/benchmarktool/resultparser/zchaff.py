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
    "seed": ("int", re.compile(r"^Random Seed Used\s*(?P<val>[0-9]+)\s*$")),
    "max-decisions": ("int", re.compile(r"^Max Decision Level\s*(?P<val>[0-9]+)\s*$")),
    "decisions": ("int", re.compile(r"^Num. of Decisions\s*(?P<val>[0-9]+)\s*$")),
    "conflicts": ("int", re.compile(r"^\s*Added Conflict Clauses\s*(?P<val>[0-9]+)\s*$")),
    "shrinkings": ("int", re.compile(r"^\s*Num of Shrinkings\s*(?P<val>[0-9]+)\s*$")),
    "deletedconflictcls": ("int", re.compile(r"^\s*Deleted Conflict Clauses\s*(?P<val>[0-9]+)\s*$")),
    "deletedcls": ("int", re.compile(r"^\s*Deleted Clauses\s*(?P<val>[0-9]+)\s*$")),
    "conflictlits": ("int", re.compile(r"^\s*Added Conflict Literals\s*(?P<val>[0-9]+)\s*$")),
    "deletedlits": ("int", re.compile(r"^\s*Deleted \(Total\) Literals\s*(?P<val>[0-9]+)\s*$")),
    "implications": ("int", re.compile(r"^\s*Number of Implication\s*(?P<val>[0-9]+)\s*$")),
    "#vars": ("int", re.compile(r"^\s*Original Num Variables\s*(?P<val>[0-9]+)\s*$")),
    "#cls": ("int", re.compile(r"^\s*Original Num Clauses\s*(?P<val>[0-9]+)\s*$")),
    "#lits": ("int", re.compile(r"^\s*Original Num Literals\s*(?P<val>[0-9]+)\s*$"))
}


def zchaff(root, runspec, instance):
    """
    Extracts some sat statistics.
    """
    return parse_solver_output(root, runspec, instance, solver_re)
