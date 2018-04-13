#!/usr/bin/env python
#
# Copyright 2017
# Johannes K. Fichte, TU Wien, Austria
#
# runsolver_wrapper.py is free software: you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
# runsolver_wrapper.py is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.  You should have received a
# copy of the GNU General Public License along with
# runsolver_wrapper.py.  If not, see <http://www.gnu.org/licenses/>.
import argparse
from distutils.spawn import find_executable
import os
import signal
import socket
from subprocess import Popen, PIPE, call
import sys
import tempfile
import time

from os.path import dirname

import psutil


def handler(signum, frame):
  sys.stderr.write('SIGNAL received %s\n' %signum)
  current_process = psutil.Process()
  children = current_process.children(recursive=True)
  for child in children:
    sys.stderr.write('Child pid is %s\n' %(child.pid))
    sys.stderr.write('Killing child\n')
    os.kill(child.pid, 15)

signal.signal(signal.SIGTERM, handler)
signal.signal(signal.SIGINT, handler)


class dotdict(dict):
  """dot.notation access to dictionary attributes"""
  __getattr__ = dict.get
  __setattr__ = dict.__setitem__
  __delattr__ = dict.__delitem__

args=dotdict()
args.runsolver = '{run.root}/programs/runsolver-3.3.6'
args.memlimit = '{run.memlimit}'
args.timelimit = '{run.timeout}'
args.solver = '{run.root}/programs/{run.solver}'
args.watcher= '{run.root}/{run.path}/{run.instancebase}.watcher'
args.solver_args='{run.args}'
args.filename = ['{run.file}']
args.stdout='{run.root}/{run.path}/{run.instancebase}.txt'
#args.stdout='/dev/stdout'
args.stderr='{run.root}/{run.path}/{run.instancebase}.err'
#args.stderr='/dev/stderr'
args.finished = '{run.root}/{run.finished}'
# args.debug=True
args.run='{run.run}'

if os.path.isfile(args.finished):
  sys.stderr.write('INSTANCE RUN "%s" already exists. Exiting...\n' %args.finished)
  exit(2)


def main(args):
  def debug(value):
    if args.debug:
      sys.stderr.write('%s\n' %value)

  if not args.runsolver:
    sys.stderr.write('\nRunsolver not found. bin=%s\nExiting\n' %args.runsolver)
    exit(1)

  if not args.solver:
    sys.stderr.write('\nSolver not found. bin=%s\nExiting\n' %args.solver)


  try:
    if os.environ['BATCH_SYSTEM'] == 'HTCondor':
      condor = True
  except KeyError:
    condor = False

  #USE CONDOR SPECIFIC VARIABLES
  if condor:
    #tmp=os.environ['_CONDOR_SCRATCH_DIR']
    tmp='{run.root}/{run.path}'
  else:
    tmp=tempfile.gettempdir()
  
  debug(os.environ)
  debug('hostname = %s ' %socket.gethostname())
  sys.stderr.write('args=%s\n' %sys.argv[1:])
  sys.stderr.write(args.solver_args)
  sys.stderr.write('\n')

  dir_path = os.path.dirname(os.path.realpath(__file__))

  cmd = '%s -M %s -W %s -w %s %s %s -t %s --runid %s -f %s > %s 2>> %s' % (args.runsolver, args.memlimit, args.timelimit, args.watcher, args.solver, ''.join(args.solver_args), tmp, args.run, ' '.join(args.filename), args.stdout, args.stderr)
  sys.stderr.write('COMMAND=%s\n' %cmd)

  p_solver = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True, close_fds=True, cwd=dir_path)
  output, err = p_solver.communicate()
  sys.stdout.write('%s RETCODE %s\n' % ('*' * 40, '*' * 40))
  sys.stdout.write('ret=%s\n' %p_solver.returncode)
  sys.stdout.write('%s STDOUT %s\n' %('*'*40, '*'*40))
  sys.stdout.write(output)
  sys.stderr.write('%s STDERR %s\n' %('*'*40, '*'*40))
  sys.stderr.write(err)
  childreturncode=0
  with open(os.path.join(dir_path, args.watcher)) as f:
    for line in f:
      line=line.split()
      if line==[]:
        continue
      if line[0] == 'Child' and line[1] == 'status:':
        childreturncode=int(line[2])
  if int(p_solver.returncode) == 0 and childreturncode == 0:
    open(os.path.join(dir_path,args.finished),'a').close()


if __name__ == "__main__":
  main(args)
