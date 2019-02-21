import os
from .base import Job, ScriptGen
import benchmarktool.tools as tools


class PbsScriptGen(ScriptGen):
    """
    A class that generates and evaluates start scripts for pbs runs.
    """

    class PbsScript:
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

    def genStartScript(self, path):
        """
        Generates a start script that can be used to start all scripts 
        generated using addToScript().
        
        Keyword arguments:
        path - The target location for the script
        """
        tools.mkdir_p(path)
        startfile = open(os.path.join(path, "start.sh"), 'w')
        queue = []
        pbsScripts = {}
        for (runspec, instpath, instname) in self.startfiles:
            #TODO: move to xml file
            if instname.startswith('move.sh') or instname.startswith('results.txt'):
                continue
            relpath = os.path.relpath(instpath, path)
            jobScript = os.path.join(relpath, instname)
            pbsKey = (
                runspec.setting.ppn, runspec.setting.procs, runspec.setting.pbstemplate, runspec.project.job.walltime)

            if not pbsKey in pbsScripts:
                pbsScript = PbsScriptGen.PbsScript(pbsKey, path, queue)
                pbsScripts[pbsKey] = pbsScript
            else:
                pbsScript = pbsScripts[pbsKey]

            if self.job.script_mode == "multi":
                if pbsScript.num > 0: pbsScript.next()
                pbsScript.append(jobScript)
            elif self.job.script_mode == "timeout":
                if pbsScript.time + runspec.project.job.timeout + 300 >= runspec.project.job.walltime:
                    pbsScript.next()
                pbsScript.time += runspec.project.job.timeout + 300
                pbsScript.append(jobScript)

        for pbsScript in pbsScripts.values(): pbsScript.write()

        startfile.write("""#!/bin/bash\n\ncd "$(dirname $0)"\n""" + "\n".join(
            ['qsub "{0}"'.format(os.path.basename(x)) for x in queue]))
        startfile.close()
        tools.setExecutable(os.path.join(path, "start.sh"))


class PbsJob(Job):
    """
    Describes a pbs job.
    """

    def __init__(self, name, memout, timeout, runs, script_mode, walltime, **kwargs):
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
        return PbsScriptGen(self)