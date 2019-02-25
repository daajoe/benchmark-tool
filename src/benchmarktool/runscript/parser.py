"""
This module contains an XML-parser for run script specifications. 
It reads and converts a given specification and returns its 
representation in form of python classes.
"""

__author__ = "Roland Kaminski"

import os
import yaml
from dotmap import DotMap
from pykwalify.core import Core as SchemaValidator
from benchmarktool.runscript.runscript import Runscript, Project, Benchmark, Config, System, Setting, CondorJob, PbsJob, SeqJob, Machine
from benchmarktool.runscript.benchmark.specs import FolderSpec, DOISpec
import benchmarktool.tools as tools
try: from StringIO import StringIO
except: from io import StringIO

class Parser:
    """
    A parser to parse xml runscript specifications.
    """   
    def __init__(self):
        """
        Initializes the parser.
        """
        pass
    
    def parse(self, file_name):
        """
        Parse a given runscript and return its representation 
        in form of an instance of class Runscript.
        
        Keyword arguments:
        file_name -- a string holding a path to a yaml file  
        """
        
        dirname = os.path.dirname(__file__)
        schema_file = os.path.join(dirname, "./schema.yml")
        validator = SchemaValidator(source_file=file_name, schema_files=[schema_file])
        validator.validate(raise_exception=True)
        
        runscript = DotMap(yaml.load(open(file_name)))
        run  = Runscript(os.path.join(runscript.base_dir, runscript.output_dir))
        
        for job_name, job_desc in runscript.jobs.items():
            if 'timeout' not in job_desc:
                job_desc.timeout = 0
            if 'memout' not in job_desc:
                job_desc.memout = 0

            if job_desc.type == "seq":
                job = SeqJob(job_name, **job_desc.toDict())
            elif job_desc.type == "pbs":
                job = PbsJob(job_name, **job_desc.toDict())
            elif job_desc.type == "condor":
                job = CondorJob(job_name, **job_desc.toDict())
            run.addJob(job)
        
        for machine_name, machine_desc in runscript.machines.items():
            machine = Machine(machine_name, **machine_desc.toDict())
            run.addMachine(machine)
        
        for config_name, config_desc in runscript.configs.items():
            template = os.path.join(runscript.base_dir, config_desc.template)
            config = Config(config_name, template)
            run.addConfig(config)
        
        settings = {}
        for system_idx, system_desc in enumerate(runscript.systems):
            system_desc.measures = "{base}.{measure}".format(
                base=os.path.normpath(runscript.base_dir).replace(os.sep, "."),
                measure=system_desc.measures
            )
            system = System(order=system_idx, **system_desc.toDict())
            for setting_idx, setting_desc in enumerate(system_desc.settings):
                settings[setting_desc.name] = []
                
                if "procs" in setting_desc and type(setting_desc.procs) is str:
                    procs = [int(proc) for proc in setting_desc.procs.split(None)]
                    del setting_desc.procs
                else:
                    procs = [setting_desc.get("procs")]
                
                if "tag" not in setting_desc:
                    setting_desc.tag = set()
                else:
                    setting_desc.tag = set(setting_desc.tag.split(None))
                
                if "pbstemplate" in setting_desc:
                    setting_desc.pbstemplate = os.path.join(runscript.base_dir, setting_desc.pbstemplate)
                
                if "condortemplate" in setting_desc:
                    setting_desc.condortemplate = os.path.join(runscript.base_dir, setting_desc.condortemplate)
                
                for proc in procs:
                    name = setting_desc.name
                    if proc is not None:
                        name += "-n{0}".format(proc)
                    settings[setting_desc.name].append(name)
                    params = { **setting_desc.toDict(), "name": name, "order": setting_idx, "procs": proc }
                    setting = Setting(**params)
                    system.addSetting(setting)
                
            run.addSystem(system, system_desc.config)
        
        for benchmark_name, benchmark_specs in runscript.benchmarks.items():
            benchmark = Benchmark(benchmark_name)
            for spec in benchmark_specs:
                spec.path = os.path.join(runscript.base_dir, spec.path)
                specification = None
                if spec.type == "folder":
                    specification = FolderSpec(**spec)
                elif spec.type == "doi":
                    specification = DOISpec(**spec)
                benchmark.addSpecification(specification)
            run.addBenchmark(benchmark)

        for project_name, project_desc in runscript.projects.items():
            project = Project(project_name)
            run.addProject(project, project_desc.job)
            for runspec in project_desc.get("runspecs", []):
                for setting in settings[runspec.setting]:
                    params = { **runspec.toDict(), "setting": setting }
                    project.addRunspec(**params)
            for runtag in project_desc.get("runtags", []):
                project.addRuntag(**runtag.toDict())
        
        return run
