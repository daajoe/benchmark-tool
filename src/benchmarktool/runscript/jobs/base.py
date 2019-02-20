import os
import benchmarktool.tools as tools
from benchmarktool.tools import Sortable, cmp

class Job(Sortable):
    """
    Base class for all jobs. 
    """

    def __init__(self, name, memout, timeout, runs, **kwargs):
        """
        Initializes a job.
        
        Keyword arguments:
        name    - A unique name for a job
        timeout - A timeout in seconds for individual benchmark runs
        runs    - The number of runs per benchmark
        attr    - A dictionary of arbitrary attributes
        """
        self.name = name
        self.timeout = timeout
        self.runs = runs
        self.attr = kwargs
        self.memout = memout

    def _toXml(self, out, indent, xmltag, extra):
        """
        Helper function to dump a (pretty-printed) XML-representation of a job.
        
        Keyword arguments:
        out     - Output stream to write to
        indent  - Amount of indentation
        xmltag  - Tag name for the job
        extra   - Additional arguments for the job 
        """
        out.write(
            '{1}<{2} name="{0.name}" timeout="{0.timeout}" runs="{0.runs}"{3}'.format(self, indent, xmltag, extra))
        for key, val in self.attr.items():
            out.write(' {0}="{1}"'.format(key, val))
        out.write('/>\n')

    def __hash__(self):
        """
        Calculates a hash value for the job using its name. 
        """
        return hash(self.name)

    def __cmp__(self, job):
        """
        Compares two jobs using their names. 
        """
        return cmp(job.name, job.name)


class Run(Sortable):
    """
    Base class for all runs.
    
    Class members:
    path - Path that holds the target location for start scripts
    root - directory relative to the location of the run's path.
    """

    def __init__(self, path):
        """
        Initializes a run.
        
        Keyword arguments:
        path - A path that holds the location 
               where the individual start scripts for the job shall be generated 
        """
        self.path = path
        self.root = os.path.relpath(".", self.path)


class SeqRun(Run):
    """
    Describes a sequential run.
    
    Class members:
    run      - The number of the run
    job      - A reference to the job description
    runspec  - A reference to the run description
    instance - A reference to the instance to benchmark
    file     - A relative path to the instance
    args     - The command line arguments for this run
    solver   - The solver for this run
    timeout  - The timeout of this run
    """

    def __init__(self, path, run, job, runspec, instance):
        """
        Initializes a sequential run.
        
        Keyword arguments:
        path     - A path that holds the location 
                   where the individual start scripts for the job shall be generated
        run      - The number of the run
        job      - A reference to the job description
        runspec  - A reference to the run description
        instance - A reference to the instance to benchmark
        """
        Run.__init__(self, path)
        self.run = run
        self.job = job
        self.runspec = runspec
        self.instance = instance
        self.file = os.path.relpath(self.instance.path(), self.path)
        self.args = self.runspec.setting.cmdline
        self.solver = self.runspec.system.name + "-" + self.runspec.system.version
        self.timeout = self.job.timeout
        self.memlimit = self.job.memout
        self.instancebase = os.path.basename(instance.path())
        self.finished = os.path.join(path, ".finished")



class ScriptGen:
    """
    A class providing basic functionality to generate 
    start scripts for arbitrary jobs and evaluation of results.
    """

    def __init__(self, job):
        """
        Initializes the script generator.
        
        Keyword arguments:
        seqJob - A reference to the associated job.
        """
        self.skip = False
        self.job = job
        self.startfiles = []

    def setSkip(self, skip):
        self.skip = skip

    def _path(self, runspec, instance, run):
        """
        Returns the relative path to the start script location.
        
        Keyword arguments:
        runspec  - The run specification for the start script
        instance - The benchmark instance for the start script
        run      - The number of the run for the start script
        """
        return os.path.join(runspec.path(), instance.classname.name, instance.instance, "run%d" % run)

    def addToScript(self, runspec, instance):
        """
        Creates a new start script for the given instance.
        
        Keyword arguments:
        runspec  - The run specification for the start script
        instance - The benchmark instance for the start script
        """
        skip = self.skip
        for run in range(1, self.job.runs + 1):
            path = self._path(runspec, instance, run)
            tools.mkdir_p(path)
            startpath = os.path.join(path, "start.sh")
            finish = os.path.join(path, ".finished")
            if skip and os.path.isfile(finish):
                continue
            template = open(runspec.system.config.template).read()
            startfile = open(startpath, "w")
            startfile.write(template.format(run=SeqRun(path, run, self.job, runspec, instance)))

            startfile.close()
            self.startfiles.append((runspec, path, "start.sh"))
            tools.setExecutable(startpath)

    def evalResults(self, out, indent, runspec, instance):
        """
        Parses the results of a given benchmark instance and outputs them as XML.
        
        Keyword arguments:
        out     - Output stream to write to
        indent  - Amount of indentation
        runspec - The run specification of the benchmark
        runspec - The benchmark instance
        """
        for run in range(1, self.job.runs + 1):
            out.write('{0}<run number="{1}">\n'.format(indent, run))
            measure_function = tools.import_function(runspec.system.measures)
            result = measure_function(self._path(runspec, instance, run), runspec, instance)
            for key, valtype, val in sorted(result):
                out.write('{0}<measure name="{1}" type="{2}" val="{3}"/>\n'.format(indent + "\t", key, valtype, val))
            out.write('{0}</run>\n'.format(indent))

