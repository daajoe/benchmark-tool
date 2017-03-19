'''
Created on Jan 20, 2010
@author: Roland Kaminski

Modified on Mar 19, 2017
@author: Johannes K. Fichte
'''

import zipfile
from itertools import izip

try:
    from cStringIO import StringIO
except:
    from io import StringIO
import math
import sys
from benchmarktool import tools
from benchmarktool.tools import Sortable, cmp


# Source SO: 1630320
def lookahead(iterable):
    """Pass through all values from the given iterable, augmented by the
    information if there are more values to come after the current one
    (True), or if it is the last value (False).
    """
    # Get an iterator and pull the first value.
    it = iter(iterable)
    last = next(it)
    # Run the iterator to exhaustion (starting from the second value).
    for val in it:
        # Report the *previous* value (more to come).
        yield last, False
        last = val
    # Report the last value.
    yield last, True


class CSV:
    def __init__(self, benchmark, measures):
        self.benchmark = benchmark
        self.measures = measures
        self.results = {}
        self.instSheet = ResultTable(benchmark, measures, "ta1")
        # self.classSheet = ResultTable(benchmark, measures, "ta2", self.instSheet)

    def finish(self):
        self.instSheet.finish(self.results)
        # TODO:
        # self.classSheet.finish()
        # TODO:
        # self.summarySheet.finish()

    def printSheet(self, out):
        # PACE INSTANCE SUMMARY
        # solution quality (improved)
        # num solved instances
        # warning if difference between multiple runs very high
        # solution time, min, max, std
        # worst instance
        # avg width
        # best configuration
        # BEST SOLVER: output cactus plot
        # for sat best sat solver + best encoder
        #  SUMMARIZE RUNS, DIFF FOR EACH RUN, STD
        # PACE SET SUMMARY
        #
        #"Instances"
        out = StringIO()
        self.instSheet.printSheet(out, self.results)
        exit(1)

        # TODO:
        zipFile = zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED)
        out = StringIO()

        for sheet in [self.instSheet, self.classSheet]:
            for i in range(0, len(sheet.cowidth)):
                # sheet.name, i + 1, sheet.cowidth[i])
                pass

        self.instSheet.printSheet(out, "Instances")
        self.classSheet.printSheet(out, "Classes")

    # def addRunspec(self, runspec):
    #     # TODO: remove duplicate data for runs
    #     # print xml_string
    #     # benchmark.class.instance contains all benchmarks (class = folder)
    #     # benchmark.class.instance.name/id
    #     # project.runspec.class=id
    #     # project.runspec.class.instance.id.run.number
    #     #
    #     # USED FOR TXT SUMMARY FILE
    #     # self.summarySheet.addRunspec(runspec)
    #     # benchmark = runspec.benchmark.name
    #     # setting = runspec.setting.name
    #     # solver = runspec.system.name
    #     # solver_version = runspec.system.version
    #     # machine = runspec.machine.name
    #     self.instSheet.addRunspec(runspec)


    def addRunspec(self, runspec):
        # prepare mapping lookup
        class_ids = {}  # FORMAT: instance_ids = {classid: instancename}
        for clazz in self.benchmark:
            class_ids[clazz.id] = clazz.name

        benchmarks = {}  # FORMAT: benchmarks = {'class':
        #                            {'benchmark1': [run1, run2], 'benchmark2': [run1, run2]}}
        # compute dicts
        for class_result in runspec:
            clazz_name = class_ids[class_result.benchclass.id]
            benchmarks[clazz_name] = {}
            for inst_result in class_result:
                runs = {}
                # runs = {'solver': runspec.setting.system.name,
                #         'solver_version': runspec.setting.system.version}
                for run in inst_result:
                    row = {}
                    for name, value_type, value in run.iter(self.measures):
                        if value_type == 'int':
                            row[name] = int(value)
                        elif value_type == 'float':
                            row[name] = float(value)
                        else:
                            row[name] = value
                    runs[run.number] = row
                benchmarks[clazz_name][inst_result.instance.name] = runs
        solver = runspec.setting.system.name
        solver_version = runspec.setting.system.version
        solver_config = runspec.setting.name
        solver_args = runspec.setting.cmdline
        benchmark_name = runspec.benchmark.name
        machine = runspec.machine.name
        self.results[(benchmark_name, machine, solver, solver_version, solver_config, solver_args)] = benchmarks


class Table:
    def __init__(self, name):
        self.content = []
        self.cowidth = []
        self.name = name

    def printSheet(self, out, results):

        for row in self.content:
            for cell, last in lookahead(row):
                if cell is not None:
                    cell.printSheet(out)
                    if not last:
                        out.write(',')
                    else:
                        out.write('\n')

class ResultTable(Table):
    def __init__(self, benchmark, measures, name, instance_table=None):
        Table.__init__(self, name)
        self.benchmark = benchmark
        self.results = {}
        self.measures = measures

    def finish(self, results):
        pass

class Summary:
    def __init__(self):
        self.sum = 0
        self.dev = 0
        self.sqsum = 0
        self.avg = 0
        self.dst = 0
        self.best = 0
        self.better = 0
        self.worse = 0
        self.worst = 0
        self.count = 0

    def calc(self, n, colA, minmum, median, maximum):
        self.avg = self.sum / self.count
        self.dev = math.sqrt(self.sqsum / self.count - self.avg * self.avg)
        colA.extend([None for _ in range(0, - len(colA))])
        # geometric distance, best
        if minmum is not None:
            minmum.extend([None for _ in range(0, self.count - len(minmum))])
            sdsum = 0
            for a, b in zip(colA, minmum):
                if a is not None:
                    if a <= b:
                        self.best += 1
                    sdsum += (a - b) * (a - b)
            self.dst = math.sqrt(sdsum)
        # better, worse
        if median is not None:
            median.extend([None for _ in range(0, self.count - len(median))])
            for a, b in zip(colA, median):
                if a != None:
                    if a < b:
                        self.better += 1
                    elif a > b:
                        self.worse += 1
        # worst
        if maximum is not None:
            maximum.extend([None for _ in range(0, self.count - len(maximum))])
            for a, b in zip(colA, maximum):
                if a is not None and a >= b:
                    self.worst += 1

    def add(self, val):
        self.sum += val
        self.sqsum += val * val
        self.count += 1


class ValueColumn:
    def __init__(self, name, valueType):
        self.offset = None
        self.content = []
        self.name = name
        self.type = valueType
        self.summary = Summary()

    def addCell(self, line, value):
        if self.type == "classresult":
            self.summary.add(float(value[1]))
        elif self.type == "float" and value is not None:
            value = float(value)
            self.summary.add(value)
        while len(self.content) <= line:
            self.content.append(None)
        self.content[line] = value


class SystemColumn(Sortable):
    def __init__(self, setting, machine):
        self.setting = setting
        self.machine = machine
        self.columns = {}
        self.offset = None

    def genName(self, addMachine):
        res = self.setting.system.name + "-" + self.setting.system.version + "/" + self.setting.name
        if addMachine:
            res += " ({0})".format(self.machine.name)
        return res

    def __cmp__(self, other):
        return cmp((self.setting.system.order, self.setting.order, self.machine.name),
                   (other.setting.system.order, other.setting.order, other.machine.name))

    def __hash__(self):
        return hash((self.setting, self.machine))

    def iter(self, measures):
        if measures == "":
            for column in sorted(self.columns, cmp=lambda x: x.name):
                yield column
        else:
            for name, _ in measures:
                if name in self.columns:
                    yield self.columns[name]

    # TODO:
    # def calcSummary(self, n, ref):
    #     for name, column in self.columns.items():
    #         minimum = maximum = median = None
    #         if len(ref) == 3:
    #             minimum = ref[0].columns[name].content
    #             maximum = ref[1].columns[name].content
    #             median = ref[2].columns[name].content
    #         column.summary.calc(n, column.content, minimum, maximum, median)

    def addCell(self, line, name, value_type, value):
        # print line,name,value_type, value
        if not name in self.columns:
            self.columns[name] = ValueColumn(name, value_type)
        self.columns[name].addCell(line, value)
