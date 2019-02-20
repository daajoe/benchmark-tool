import os
from .base import Job, ScriptGen, SeqRun
import benchmarktool.tools as tools

class CondorScriptGen(ScriptGen):
    """
    A class that generates and evaluates start scripts for pbs runs.
    """

    class CondorScript:
        def __init__(self, runspec, path, queue):
            self.runspec = runspec
            self.path = path
            self.queue = queue
            self.num = 0
            self.time = None
            self.startscripts = None
            self.next()

        def write(self):
            if self.num > 0:
                self.num = 0
                template = open(self.runspec[2], "r").read()
                script = os.path.join(self.path, "start{0:04}.pbs".format(len(self.queue)))
                open(script, "w").write(
                    template.format(walltime=tools.pbsTime(self.runspec[3]), nodes=self.runspec[1], ppn=self.runspec[0],
                                    jobs=self.startscripts))
                self.queue.append(script)

        def next(self):
            self.write()
            self.startscripts = ""
            self.num = 0
            self.time = 0

        def append(self, startfile):
            self.num += 1
            self.startscripts += startfile + "\n"

    def __init__(self, seqJob):
        """
        Initializes the script generator.

        Keyword arguments:
        seqJob - A reference to the associated sequential job.
        """
        ScriptGen.__init__(self, seqJob)

    def addToScript(self, runspec, instance):
        skip = self.skip
        for run in range(1, self.job.runs + 1):
            path = self._path(runspec, instance, run)
            tools.mkdir_p(path)
            startpath = os.path.join(path, "start.py")
            finish = os.path.join(path, ".finished")
            if skip and os.path.isfile(finish):
                continue
            seq = SeqRun(path, run, self.job, runspec, instance)
            with open(startpath, "w") as startfile:
                with open(runspec.system.config.template) as templatefile:
                    template = templatefile.read()
                run = dotdict(seq.__dict__)
                run.instancebase = os.path.basename(run.instance.path())
                run.root = self.job.basedir.strip()
                run.instance = run.instance.path()
                run.memlimit = self.job.memout
                run.timelimit = self.job.timeout
                run.finished = finish
                startfile.write(template.format(run=run))
            os.chmod(startpath, 0o770)
            self.startfiles.append((runspec, path, "start.py"))
            tools.setExecutable(startpath)

        return

    def genStartScript(self, path):
        """
        Generates a condor submit script that can be used to start all scripts
        generated using addToScript().

        Keyword arguments:
        path - The target location for the script
        """
        tools.mkdir_p(path)

        instances = []
        initialdir = os.path.join(self.job.basedir.strip(), 'output')
        for (runspec, instpath, instname) in self.startfiles:
            instance = os.path.join(self.job.basedir.strip(), instpath, instname)
            outprefix = os.path.join(self.job.basedir.strip(), instpath)
            instances.append((instance, outprefix))

        for i, chunk in enumerate(chunks(instances, 5000)):
            startpath = os.path.join(self.job.basedir.strip(), path, "condor_%s.submit" %i)
            with open(startpath, "w") as condorsubmitfile:
                with open(self.job.condortemplate) as template:
                    t = Template(template.read())
                    condorsubmitfile.write(
                        t.render(instances=chunk, timeout=self.job.timeout,
                                 memout=self.job.memout, initialdir=initialdir))
        #tools.setExecutable(os.path.join(path, "condor_0.submit"))



class CondorJob(Job):
    """
    Describes a condor job.
    """

    def __init__(self, name, memout, timeout, runs, script_mode, walltime, condortemplate, basedir, *args, **kwargs):
        """
        Initializes a parallel job description.

        Keyword arguments:
        name        - A unique name for a job
        timeout     - A timeout in seconds for individual benchmark runs
        runs        - The number of runs per benchmark
        script_mode - Specifies the script generation mode
        walltime    - The walltime for a job submitted via PBS
        attr        - A dictionary of arbitrary attributes
        """
        Job.__init__(self, name, memout, timeout, runs, **kwargs)
        self.script_mode = script_mode
        self.walltime = walltime
        self.condortemplate = condortemplate
        self.basedir = basedir

    def toXml(self, out, indent):
        """
        Dump a (pretty-printed) XML-representation of the parallel job.

        Keyword arguments:
        out     - Output stream to write to
        indent  - Amount of indentation
        """
        extra = ' script_mode="{0.script_mode}" walltime="{0.walltime}"'.format(self)
        Job._toXml(self, out, indent, "pbsjob", extra)

    def scriptGen(self):
        """
        Returns a class that can generate start scripts and evaluate benchmark results.
        (see SeqScriptGen)
        """
        return CondorScriptGen(self)

