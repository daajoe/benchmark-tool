'''
Created on Jan 17, 2010

@author: Roland Kaminski
'''

import os
import re
import sys
import codecs

# noinspection PyUnresolvedReferences
from benchmarktool.resultparser.claspar import claspar
# noinspection PyUnresolvedReferences
from benchmarktool.resultparser.cudf import cudf
# noinspection PyUnresolvedReferences
from benchmarktool.resultparser.clasp import clasp
# noinspection PyUnresolvedReferences
from benchmarktool.resultparser.claspD import claspD
# noinspection PyUnresolvedReferences
from benchmarktool.resultparser.clingo import clingo
# noinspection PyUnresolvedReferences
from benchmarktool.resultparser.pace_jkf import pace_jkf
# noinspection PyUnresolvedReferences
from benchmarktool.resultparser.dynasp_jkf import dynasp_jkf
# noinspection PyUnresolvedReferences
from benchmarktool.resultparser.sat import sat
# noinspection PyUnresolvedReferences
from benchmarktool.resultparser.minisat import minisat
# noinspection PyUnresolvedReferences
from benchmarktool.resultparser.zchaff import zchaff
# noinspection PyUnresolvedReferences
from benchmarktool.resultparser.cachet import cachet
# noinspection PyUnresolvedReferences
from benchmarktool.resultparser.dsharp import dsharp
# noinspection PyUnresolvedReferences
from benchmarktool.resultparser.sharpsat import sharpsat
# noinspection PyUnresolvedReferences
from benchmarktool.resultparser.gpusat import gpusat
# noinspection PyUnresolvedReferences
from benchmarktool.resultparser.lingeling import lingeling
# noinspection PyUnresolvedReferences
from benchmarktool.resultparser.minisat_gpusat import minisat_gpusat
# noinspection PyUnresolvedReferences
from benchmarktool.resultparser.picosat import picosat
# noinspection PyUnresolvedReferences
from benchmarktool.resultparser.approxmc import approxmc
# noinspection PyUnresolvedReferences
from benchmarktool.resultparser.sat_gpusat import sat_gpusat
# noinspection PyUnresolvedReferences
from benchmarktool.resultparser.clasp_gpusat import clasp_gpusat
# noinspection PyUnresolvedReferences
from benchmarktool.resultparser.dynasp import dynasp
# noinspection PyUnresolvedReferences
from benchmarktool.resultparser.claspmcasp import claspmcasp
# noinspection PyUnresolvedReferences
from benchmarktool.resultparser.claspmcsat import claspmcsat
# noinspection PyUnresolvedReferences
from benchmarktool.resultparser.dynqbf import dynqbf
# noinspection PyUnresolvedReferences
from benchmarktool.resultparser.sharpCDCL import sharpCDCL
# noinspection PyUnresolvedReferences
from benchmarktool.resultparser.gpusat_htd import gpusat_htd
# noinspection PyUnresolvedReferences
from benchmarktool.resultparser.weightmc import weightmc
# noinspection PyUnresolvedReferences
from benchmarktool.resultparser.d4 import d4
# noinspection PyUnresolvedReferences
from benchmarktool.resultparser.c2d import c2d
# noinspection PyUnresolvedReferences
from benchmarktool.resultparser.cachet_wmc import cachet_wmc


claspre_features 	= re.compile(r"^Features[ ]*:[ ]*(([0-9]+\.?[0-9]*)([,](.+\.?.*))*)\+?[ ]*$")
claspre_conf = re.compile(r"^Chosen configuration:[ ]*(.*)\+?[ ]*$")

def claspre(root, runspec, instance):
	result = clasp(root, runspec, instance)
	for line in open(os.path.join(root, "runsolver.solver")):
		m = claspre_features.match(line)
		if m: result.append(("features", "list float", m.group(1)))
		m = claspre_conf.match(line)
		if m: result.append(("configuration", "string", m.group(1)))
	return result

smodels_status  = re.compile(r"^(True|False)")
smodels_choices = re.compile(r"^Number of choice points: ([0-9]+)")
smodels_time	= re.compile(r"^Real time \(s\): ([0-9]+\.[0-9]+)$")

def smodels(root, runspec, instance):
	"""
	Extracts some smodels statistics.
	(This function was tested with smodels-2.33.)
	"""
	result  = []
	status  = None
	timeout = time = runspec.project.job.timeout

	# parse smodels output
	for line in open(os.path.join(root, "runsolver.solver")):
		m = smodels_status.match(line)
		if m: status = m.group(1)
		m = smodels_choices.match(line)
		if m: result.append(("choices", "float", float(m.group(1))))

	# parse runsolver output
	for line in open(os.path.join(root, "runsolver.watcher")):
		m = smodels_time.match(line)
		if m: time = float(m.group(1))

	if status == None or time >= timeout:
		time = timeout
		result.append(("timeout", "float", 1))
	else:
		result.append(("timeout", "float", 0))

	if status == "True": status = "SATISFIABLE"
	elif status == "False": status = "UNSATISFIABLE"
	else: status = "UNKNOWN"

	result.append(("status", "string", status))
	result.append(("time", "float", time))

	return result

