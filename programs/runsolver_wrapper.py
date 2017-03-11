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
import socket
from subprocess import Popen, PIPE, call
import sys
import tempfile
import time

from os.path import dirname

def parse_args(runsolver):
  parser = argparse.ArgumentParser(description='%s -f instance')
  parser.add_argument('-M', '--mem-soft-limit', dest='memlimit', action='store', type=int, help='mem-limit', default=2000)
  parser.add_argument('-W', '--wall-clock-limit', dest='timelimit', action='store', type=int, help='time-limit', default=900)
  parser.add_argument('-s', '--solver', dest='solver', action='store', type=str, help='filename', default=[], required=True)
  parser.add_argument('-a', '--solver--args', dest='solver_args', action='store', type=str, help='solver args', default=[])
  parser.add_argument('-w', '--watcher-data', dest='watcher', action='store', type=lambda x: os.path.abspath(x), help='watcher filename', default='runsolver.watcher')
  parser.add_argument('-o', '--stdout', dest='stdout', action='store', type=lambda x: os.path.abspath(x), help='stdout redirect filename', default='/dev/stdout') #default='runsolver.solver')
  parser.add_argument('-e', '--stderr', dest='stderr', action='store', type=lambda x: os.path.abspath(x), help='stderr redirect filename', default='/dev/stderr') #default='runsolver.err')
  parser.add_argument('-r', '--runsolver', dest='runsolver', action='store', type=lambda x: find_executable(x), help='filename', default=runsolver)
  parser.add_argument('-d', '--debug', dest='debug', action='store_true', help='debug', default=False)
  parser.add_argument('-t', '--tmp', dest='tmp', action='store', type=str, help='tmp folder', default=tempfile.tempdir)
  parser.add_argument('-j', '--jobid', dest='jobid', action='store', type=str, help='jobid for parallel runs', default='')
  parser.add_argument('filename', type=str, nargs=1, help='filename')
  return parser.parse_args()

def main():
  def debug(value):
    if args.debug:
      sys.stderr.write('%s\n' %value)
  
  runsolver = "runsolver-3.3.5"
  args = parse_args(runsolver=runsolver)
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
    tmp=os.environ['_CONDOR_SCRATCH_DIR']
  else:
    tmp=args.tmp
  
  debug(os.environ)
  debug('hostname = %s ' %socket.gethostname())
  sys.stderr.write('args=%s\n' %sys.argv[1:])
  sys.stderr.write(args.solver_args)
  sys.stderr.write('\n')

  cmd = '%s -M %s -W %s -w %s %s %s -t %s -f %s > %s 2>> %s' % (args.runsolver, args.memlimit, args.timelimit, args.watcher, args.solver, ''.join(args.solver_args), tmp, ' '.join(args.filename), args.stdout, args.stderr)
  sys.stderr.write('COMMAND=%s\n' %cmd)

  p_solver = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True, close_fds=True)
  output, err = p_solver.communicate()
  if args.stdout == '/dev/stdout':
    sys.stdout.write('%s STDOUT %s\n' %('*'*40, '*'*40))
    sys.stdout.write(output)
  if args.stderr == '/dev/stderr':
    sys.stderr.write('%s STDERR %s\n' %('*'*40, '*'*40))
    sys.stderr.write(err)

if __name__ == "__main__":
  main()
