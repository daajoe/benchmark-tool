'''
Created on Jan 19, 2010

@author: Roland Kaminski
'''

import heapq
import itertools
from zipfile import ZipFile
from StringIO import StringIO

import sys

class Spreadsheet:
    def __init__(self, benchmark, columns, measures):
        self.instSheet = InstanceTable(benchmark, columns, measures)
        
    def finish(self):
        self.instSheet.finish()
        
    def printSheet(self, out):
        zipFile = ZipFile(out, "w")
        out = StringIO()
        out.write('''<office:document-content xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0" xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0" xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0" xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:meta="urn:oasis:names:tc:opendocument:xmlns:meta:1.0" xmlns:number="urn:oasis:names:tc:opendocument:xmlns:datastyle:1.0" xmlns:presentation="urn:oasis:names:tc:opendocument:xmlns:presentation:1.0" xmlns:svg="urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0" xmlns:chart="urn:oasis:names:tc:opendocument:xmlns:chart:1.0" xmlns:dr3d="urn:oasis:names:tc:opendocument:xmlns:dr3d:1.0" xmlns:math="http://www.w3.org/1998/Math/MathML" xmlns:form="urn:oasis:names:tc:opendocument:xmlns:form:1.0" xmlns:script="urn:oasis:names:tc:opendocument:xmlns:script:1.0" xmlns:ooo="http://openoffice.org/2004/office" xmlns:ooow="http://openoffice.org/2004/writer" xmlns:oooc="http://openoffice.org/2004/calc" xmlns:dom="http://www.w3.org/2001/xml-events" xmlns:xforms="http://www.w3.org/2002/xforms" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:rpt="http://openoffice.org/2005/report" xmlns:of="urn:oasis:names:tc:opendocument:xmlns:of:1.2" xmlns:rdfa="http://docs.oasis-open.org/opendocument/meta/rdfa#" xmlns:field="urn:openoffice:names:experimental:ooxml-odf-interop:xmlns:field:1.0" xmlns:formx="urn:openoffice:names:experimental:ooxml-odf-interop:xmlns:form:1.0" office:version="1.2">''')
        out.write('''<office:scripts/>''')
        out.write('''<office:font-face-decls>''')
        out.write('''<style:font-face style:name="Liberation Sans" svg:font-family="'Liberation Sans'" style:font-family-generic="swiss" style:font-pitch="variable"/>''')
        out.write('''<style:font-face style:name="DejaVu Sans" svg:font-family="'DejaVu Sans'" style:font-family-generic="system" style:font-pitch="variable"/>''')
        out.write('''</office:font-face-decls>''')
        out.write('''<office:automatic-styles>''')
        out.write('''<style:style style:name="co1" style:family="table-column">''')
        out.write('''<style:table-column-properties fo:break-before="auto" style:column-width="0.8925in"/>''')
        out.write('''</style:style>''')
        out.write('''<style:style style:name="ro1" style:family="table-row">''')
        out.write('''<style:table-row-properties style:row-height="0.178in" fo:break-before="auto" style:use-optimal-row-height="true"/>''')
        out.write('''</style:style>''')
        out.write('''<style:style style:name="ta1" style:family="table" style:master-page-name="Default">''')
        out.write('''<style:table-properties table:display="true" style:writing-mode="lr-tb"/>''')
        out.write('''</style:style>''')
        out.write('''</office:automatic-styles>''')
        out.write('''<office:body>''')
        out.write('''<office:spreadsheet>''')
        self.instSheet.printSheet(out)
        out.write('''</office:spreadsheet></office:body></office:document-content>''')
        zipFile.writestr("mimetype", '''application/vnd.oasis.opendocument.spreadsheet''')
        zipFile.writestr("content.xml", out.getvalue())
        zipFile.writestr("META-INF/manifest.xml", '''<?xml version="1.0" encoding="UTF-8"?><manifest:manifest xmlns:manifest="urn:oasis:names:tc:opendocument:xmlns:manifest:1.0"><manifest:file-entry manifest:media-type="application/vnd.oasis.opendocument.spreadsheet" manifest:version="1.2" manifest:full-path="/"/><manifest:file-entry manifest:media-type="text/xml" manifest:full-path="content.xml"/></manifest:manifest>''')
        zipFile.close()
        
    def addRunspec(self, runspec):
        self.instSheet.addRunspec(runspec)
        
class Cell:
    def __init__(self):
        pass

class StringCell:
    def __init__(self, val):
        self.val = val
    
    def printSheet(self, out):
        out.write('<table:table-cell office:value-type="string"><text:p>{0}</text:p></table:table-cell>'.format(self.val))

class FloatCell:
    def __init__(self, val):
        self.val = val
    
    def printSheet(self, out):
        out.write('<table:table-cell office:value-type="float" office:value="{0}"></table:table-cell>'.format(self.val))

class Table:
    def __init__(self):
        self.rows    = 0
        self.rowSize = {}
        self.content = {}
    
    def add(self, row, col, cell):
        self.content[(row,col)] = cell
        self.rows         = max(self.rows, row+1)
        self.rowSize[row] = max(self.rowSize.get(row, 0), col + 1)
    
    def printSheet(self, out):
        row = 0
        col = 0
        out.write('<table:table table:name="Instances" table:style-name="ta1" table:print="false"><table:table-column table:style-name="co1" table:default-cell-style-name="Default"/>')
        for row in range(0, self.rows):
            out.write('<table:table-row table:style-name="ro1">')
            for col in range(0,  self.rowSize.get(row, 0)):
                cell = self.content.get((row, col), None)
                if cell == None:
                    out.write('<table:table-cell office:value-type="string"><text:p></text:p></table:table-cell>')
                else:
                    cell.printSheet(out)
            out.write('</table:table-row>')
        out.write('</table:table>')
    
class InstanceTable(Table):
    def __init__(self, benchmark, columns, measures):
        Table.__init__(self)
        self.benchmark = benchmark
        self.columns   = columns
        self.results   = {}
        self.measures  = measures
        self.lines     = 0
        row = 2
        for instance in self.benchmark.list:
            instance = instance.values()[0]
            self.add(row, 0, StringCell(instance.benchclass.name + "/" + instance.name))
            row += instance.maxRuns
            self.lines += instance.maxRuns
        
        self.add(row + 1, 0, StringCell("SUM"))
        self.add(row + 2, 0, StringCell("AVERAGE"))
        self.add(row + 3, 0, StringCell("STDDEV"))
        
    def finish(self):
        col = 1
        for column in sorted(self.columns.columns):
            column.offset = col
            if self.measures == "": measures = sorted(column.width)
            else: measures = self.measures
            add = 0
            for name in measures:
                self.add(1, column.offset + add, StringCell(name))
                for line in range(0, self.lines):
                    cell = column.getCell(name, line)
                    self.add(2 + line, column.offset + add, cell)
                add += 1
            if add == 0: add = 1    
            col+= add

    def addRunspec(self, runspec):
        column = self.columns.getColumn(runspec)
        for classresult in runspec.classresults:
            for instresult in classresult.instresults:
                for run in instresult.runs:
                    if self.measures == "": measures = sorted(run.measures.keys())
                    else: measures = self.measures
                    for name in measures:
                        if name in run.measures:
                            type, value = run.measures[name]
                            if type != "float": type = "string"
                            column.addCell(instresult.instance.line + run.number - 1, name, type, value)

class Result:
    def __init__(self):
        self.machines   = {}
        self.configs    = {}
        self.systems    = {}
        self.jobs       = {}
        self.benchmarks = {}
        self.projects   = {}
    
    def merge(self, projects):
        benchmarks = set()
        columns    = set()
        for project in self.projects.values():
            for runspec in project.runspecs:
                columns.add(Column(runspec.setting, runspec.machine))
                for classresult in runspec.classresults:
                    for instresult in classresult.instresults:
                        instresult.instance.maxRuns = max(instresult.instance.maxRuns, len(instresult.runs))
                benchmarks.add(runspec.benchmark)
        
        return BenchmarkMerge(benchmarks), ColumnMerge(columns)
        
    def genOffice(self, out, selProjects, measures):
        projects = [] 
        for project in self.projects.values():
            if selProjects == "" or projects.name in selProjects:
                projects.append(project)
        benchmarkMerge, columnMerge = self.merge(projects)
        
        sheet = Spreadsheet(benchmarkMerge, columnMerge, measures)
        for project in projects:
            for runspec in project.runspecs:
                sheet.addRunspec(runspec)
        sheet.finish()
        sheet.printSheet(out)

class Column:
    def __init__(self, setting, machine):
        self.setting  = setting
        self.machine  = machine
        self.measures = {}
        self.width    = set()
    
    def __cmp__(self, other):
        return cmp((self.setting.system.name, self.setting.system.version, self.machine.name), (other.setting.system.name, other.setting.system.version, other.machine.name))
    
    def __hash__(self):
        return hash((self.setting, self.machine))
    
    def addCell(self, line, name, type, value):
        if type == "float": cell = FloatCell(float(value))
        else: cell = StringCell(value)
        self.measures[(name, line)] = cell 
        self.width.add(name)
    
    def getWidth(self):
        return len(self.width)
    
    def getCell(self, name, line):
        return self.measures.get((name, line), None) 

class ColumnMerge:
    def __init__(self, columns):
        self.machines = set()
        self.columns  = {}
        for column in columns:
            self.columns[column] = column
            self.machines.add(column.machine)

    def getColumn(self, runspec):
        return self.columns[Column(runspec.setting, runspec.machine)]
    
class BenchmarkMerge:
    def __init__(self, benchmarks):
        start = []
        for benchmark in benchmarks:
            start = heapq.merge(start, benchmark)
        self.list = []
        num = 0
        for key, instances in itertools.groupby(start, lambda instance: (instance.benchclass.id, instance.id)):
            maxRuns = 1
            line = {}
            for instance in instances:
                line[instance.benchclass.benchmark] = instance
                instance.line = num
                maxRuns = max(instance.maxRuns, maxRuns)
            self.list.append(line)
            num = num + maxRuns 

class Machine:
    def __init__(self, name, cpu, memory):
        self.name   = name
        self.cpu    = cpu
        self.memory = memory 

class Config:
    def __init__(self, name, template):
        self.name     = name
        self.template = template

class System:
    def __init__(self, name, version, config, measures):
        self.name     = name
        self.version  = version
        self.config   = config
        self.measures = measures
        self.settings = {}

class Setting:
    def __init__(self, system, name, cmdline, tag, attr):
        self.system  = system
        self.name    = name
        self.cmdline = cmdline
        self.tag     = tag
        self.attr    = attr

class Job:
    def __init__(self, name, timeout, runs, attrib):
        self.name    = name
        self.timeout = timeout
        self.runs    = runs
        self.attrib  = attrib

class SeqJob(Job):
    def __init__(self, name, timeout, runs, parallel, attrib):
        Job.__init__(self, name, timeout, runs, attrib)
        self.parallel = parallel

class Benchmark:
    class Iterator:
        def __init__(self, benchmark):
            self.posclass = iter(sorted(benchmark.classes.values()))
            self.posinst  = None
            
        def next(self):
            while True:
                if self.posinst == None:
                    nextclass    = self.posclass.next()
                    self.posinst = iter(sorted(nextclass.instances.values()))
                try:
                    return self.posinst.next()
                except StopIteration:
                    self.posinst = None

    def __init__(self, name):
        self.name    = name
        self.classes = {}
        
    def __iter__(self):
        return Benchmark.Iterator(self)
    
class Class:
    def __init__(self, benchmark, name, id):
        self.benchmark = benchmark
        self.name      = name
        self.id        = id
        self.instances = {}

class Instance:
    def __init__(self, benchclass, name, id):
        self.benchclass = benchclass
        self.name       = name
        self.id         = id
        self.line       = None
        self.maxRuns    = 0
    
    def __cmp__(self, other):
        return cmp((self.benchclass.name, self.name, self.benchclass.benchmark.name), (other.benchclass.name, other.name, other.benchclass.benchmark.name))  

class Project:
    def __init__(self, name, job):
        self.name     = name
        self.job      = job
        self.runspecs = [] 

class Runspec():
    def __init__(self, system, machine, benchmark, setting):
        self.system       = system
        self.machine      = machine
        self.benchmark    = benchmark
        self.setting      = setting
        self.classresults = []

class ClassResult:
    def __init__(self, benchclass):
        self.benchclass  = benchclass
        self.instresults = []

class InstanceResult:
    def __init__(self, instance):
        self.instance = instance
        self.runs     = []

class Run:
    def __init__(self, instresult, number):
        self.instresult = instresult
        self.number     = number
        self.measures   = {}
