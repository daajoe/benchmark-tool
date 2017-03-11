#/usr/bin/env python

#TODO: avoid runsolver if cluster configuration works well
request_cpus = 1
solver = htd-call-1.1
solver_args = -i 1000
Arguments = "-W $(timeout) -o $(sout) -e $(serr) -w $(watcher) -j $(Process) -d -s $(solver) $(benchmarkdir)/$(FILE) -a='$(solver_args)'"
#\"'$(solver_args)'\"

#TODO: replace json by yaml?
sout = $(FILE).$(RUN)._.out
serr = $(FILE).$(RUN)._.err
watcher = $(FILE).$(RUN).runsolver
#{run.path.benchmark.type}/{run.path.date}/$(IN_SHORT).out
