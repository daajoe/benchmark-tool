'''
Created on Jan 20, 2010
@author: Roland Kaminski

Modified on Mar 19, 2017
@author: Johannes K. Fichte
'''

import zipfile

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
        self.instSheet = ResultTable(benchmark, measures, "ta1")
        self.classSheet = ResultTable(benchmark, measures, "ta2", self.instSheet)

    def finish(self):
        # TODO:
        # self.summarySheet.finish()
        self.instSheet.finish()
        # TODO:
        # self.classSheet.finish()

    def printSheet(self, out):
        zipFile = zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED)
        out = StringIO()

        for sheet in [self.instSheet, self.classSheet]:
            for i in range(0, len(sheet.cowidth)):
                # sheet.name, i + 1, sheet.cowidth[i])
                pass

        self.instSheet.printSheet(out, "Instances")
        self.classSheet.printSheet(out, "Classes")

    def addRunspec(self, runspec):
        # TODO: remove duplicate data for runs
        # print xml_string
        # benchmark.class.instance contains all benchmarks (class = folder)
        # benchmark.class.instance.name/id
        # project.runspec.class=id
        # project.runspec.class.instance.id.run.number
        #

        benchmarks = {}  # FORMAT: benchmarks = {'class':
        #                            {'benchmark1': [run1, run2], 'benchmark2': [run1, run2]}}
        class_ids = {}  # FORMAT: instance_ids = {classid: instancename}
        instance_ids = {}  # FORMAT: instance_ids = {(classid,instanceid): instancename}
        # for element in root:
        #     if element.tag == 'benchmark':
        #         for element2 in element:
        #             if element2.tag == 'class':
        #                 class_ids[element2.attrib['id']] = element2.attrib['name']
        #                 for element3 in element2:
        #                     instance_ids[(element2.attrib['id'], element3.attrib['id'])] = element3.attrib['name']
        #     if element.tag == 'project':
        #         for element2 in element:
        #             if element2.tag == 'runspec':
        # USED FOR TXT SUMMARY FILE
        # self.summarySheet.addRunspec(runspec)
        # benchmark = runspec.benchmark.name
        # setting = runspec.setting.name
        # solver = runspec.system.name
        # solver_version = runspec.system.version
        # machine = runspec.machine.name
        self.instSheet.addRunspec(runspec)
        # TODO:
        # self.classSheet.addRunspec(runspec)
        return
        instance_id = element4.tag.attrib['id']
        for element5 in element4:
            if element4.tag == 'run':
                for element6 in element5:
                    if element4.tag == 'measure':
                        pass


class Cell:
    def __init__(self):
        self.style = None

    def protect(self, val):
        # TODO:
        return val
        # return val.replace("\"", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class StringCell(Cell):
    def __init__(self, val):
        Cell.__init__(self)
        if val == None:
            self.val = ""
        else:
            self.val = val

    def printSheet(self, out):
        out.write(self.protect(self.val))


class FloatCell(Cell):
    def __init__(self, val):
        Cell.__init__(self)
        self.val = val

    def printSheet(self, out):
        out.write('%s' % self.val)
        # TODO: style *val* or -val-


class FormulaCell(Cell):
    def __init__(self, val, arrayForm=False):
        Cell.__init__(self)
        self.val = val
        self.arrayForm = arrayForm

    def printSheet(self, out):
        out.write('%s' % self.protect(self.val))


class Table:
    def __init__(self, name):
        self.content = []
        self.cowidth = []
        self.name = name

    def add(self, row, col, cell):
        # TODO:
        # estimate some "good" column width
        while len(self.cowidth) <= col + 1:
            self.cowidth.append(0.8925)
        if cell.__class__ == StringCell:
            self.cowidth[col] = max(self.cowidth[col], len(cell.val) * 0.069 + 0.1)
        while len(self.content) <= row:
            self.content.append([])
        rowRef = self.content[row]
        while len(rowRef) <= col:
            rowRef.append(None)
        rowRef[col] = cell

    def get(self, row, col):
        return self.content[row][col]

    def cellIndex(self, row, col, absCol=False, absRow=False):
        radix = ord("Z") - ord("A") + 1
        ret = ""
        while col >= 0:
            rem = col % radix
            ret = chr(rem + ord("A")) + ret
            col = col // radix - 1
        if absCol:
            preCol = "$"
        else:
            preCol = ""
        if absRow:
            preRow = "$"
        else:
            preRow = ""
        return preCol + ret + preRow + str(row + 1)

    def printSheet(self, out):
        print
        print 'CELL', dir(self.content[0])
        # exit(1)
        # TODO: write header
        for row in self.content:
            for cell, last in lookahead(row):
                if cell is None:
                    #TODO:
                    pass
                else:
                    cell.printSheet(out)
                    if not last:
                        out.write(',')
                    else:
                        out.write('\n')

class ValueRows:
    def __init__(self, highlight):
        self.highlight = highlight
        self.list = {}

    def __iter__(self):
        for name, valList in self.list.items():
            if name in self.highlight:
                func = self.highlight[name]
                for line in range(0, len(valList)):
                    row = sorted(valList[line])
                    if len(row) > 1:
                        minimum = row[0][0]
                        median = tools.medianSorted(list(map(lambda x: x[0], row)))
                        maximum = row[-1][0]
                        green = []
                        red = []
                        if func == "t":
                            if maximum - minimum > 2:
                                for value, col in row:
                                    if value <= minimum and value < median:
                                        green.append(col)
                                    else:
                                        break
                            if maximum - median > 2:
                                for value, col in reversed(row):
                                    if value >= maximum and value > median:
                                        red.append(col)
                                    else:
                                        break
                        elif func == "to":
                            if maximum - minimum > 0:
                                for value, col in row:
                                    if value <= minimum and value < median:
                                        green.append(col)
                                    else:
                                        break
                            for value, col in reversed(row):
                                if value > median and value >= maximum:
                                    red.append(col)
                                else:
                                    break
                        yield name, line, green, red

    def add(self, name, val, line, col):
        if not name in self.list: self.list[name] = []
        valList = self.list[name]
        while len(valList) <= line: valList.append([])
        valList[line].append((val, col))

    def map(self, name, line, func):
        if not name in self.list:
            return None
        if line >= len(self.list[name]):
            return None
        if len(self.list[name][line]) == 0:
            return None
        return func(list(map(lambda x: x[0], self.list[name][line])))


class ResultTable(Table):
    def __init__(self, benchmark, measures, name, instanceTable=None):
        Table.__init__(self, name)
        self.benchmark = benchmark
        self.systemColumns = {}
        self.results = {}
        self.measures = measures
        self.machines = set()
        self.instanceTable = instanceTable
        # TODO:
        if self.instanceTable is None:
            row = 1
            for benchclass in benchmark:
                for instance in benchclass:
                    self.add(row, 0, StringCell(instance.benchclass.name + "/" + instance.name))
                    row += instance.maxRuns
        else:
            row = 1
            for benchclass in benchmark:
                self.add(row, 0, StringCell(benchclass.name))
                row += 1

        self.resultOffset = row

    def getOffset(self, column, name):
        return self.systemColumns[(column.setting, column.machine)].columns[name].offset

    def finish(self):
        col = 1
        float_occur = {}
        value_rows = ValueRows(dict(self.measures))

        #TODO:
        #PACE INSTANCE SUMMARY
        # solution quality (improved)
        # num solved instances
        # warning if difference between multiple runs very high
        # solution time, min, max, std
        # worst instance
        # avg width
        # best configuration
        #BEST SOLVER: output cactus plot
        #for sat best sat solver + best encoder
        #  SUMMARIZE RUNS, DIFF FOR EACH RUN, STD
        #PACE SET SUMMARY
        #


        # generate all columns
        for systemColumn in sorted(self.systemColumns.values()):
            self.add(0, col, StringCell(systemColumn.genName(len(self.machines) > 1)))
            for column in systemColumn.iter(self.measures):
                name = column.name
                self.add(1, col, StringCell(name))
                #TODO: header offset
                #UP NEXT:::

                for line in range(0, len(column.content)):
                    value = column.content[line]
                    if value.__class__ == tuple:
                        column.content[line] = value[1]
                        value_rows.add(name, value[1], line, col)
                    elif value.__class__ == float:
                        self.add(2 + line, col, FloatCell(value))
                        value_rows.add(name, value, line, col)
                    else:
                        self.add(2 + line, col, StringCell(value))
                    # print line, name, value
                if column.type == "classresult":
                    if not name in float_occur:
                        float_occur[name] = set()
                    float_occur[name].add(col)
                elif column.type == "float":
                    if not name in float_occur:
                        float_occur[name] = set()
                    float_occur[name].add(col)
                col += 1
        output = StringIO()
        print '*'*30, 'SHEEET', '*'*30
        print dir(self), self.printSheet(output)
        print output.getvalue()
        # print self.instanceTable
        # print dir(value_rows), value_rows.list
        exit(1)
        resultColumns = []
        for colName in ["min", "median", "max"]:
            column = SystemColumn(None, None)
            column.offset = col
            self.add(0, col, StringCell(colName))
            resultColumns.append(column)
            if self.measures == "":
                measures = sorted(float_occur.keys())
            else:
                measures = map(lambda x: x[0], self.measures)
            for name in measures:
                if name in float_occur:
                    self.add(1, col, StringCell(name))
                    for row in range(2, self.resultOffset):
                        minRange = ""
                        for colRef in sorted(float_occur[name]):
                            if minRange != "":
                                minRange += ";"
                            minRange += "[.{0}]".format(self.cellIndex(row, colRef, True))
                        self.add(row, col, FormulaCell("of:={1}({0})".format(minRange, colName.upper())))
                        self.addFooter(col)
                        if colName == "min":
                            column.addCell(row - 2, name, "float", value_rows.map(name, row - 2, min))
                        elif colName == "median":
                            column.addCell(row - 2, name, "float", value_rows.map(name, row - 2, tools.median))
                        elif colName == "max":
                            column.addCell(row - 2, name, "float", value_rows.map(name, row - 2, max))
                    for colRef in sorted(float_occur[name]):
                        if colName == "min":
                            self.add(
                                self.resultOffset + 4,
                                colRef,
                                FormulaCell(
                                    "of:=SUM(([.{0}:.{1}]-[.{2}:.{3}])^2)^0.5".format(
                                        self.cellIndex(2, colRef),
                                        self.cellIndex(self.resultOffset - 1, colRef),
                                        self.cellIndex(2, col, True),
                                        self.cellIndex(self.resultOffset - 1, col, True)),
                                    True))
                            self.add(
                                self.resultOffset + 5,
                                colRef,
                                FormulaCell(
                                    "of:=SUM([.{0}:.{1}]=[.{2}:.{3}])".format(
                                        self.cellIndex(2, colRef),
                                        self.cellIndex(self.resultOffset - 1, colRef),
                                        self.cellIndex(2, col, True),
                                        self.cellIndex(self.resultOffset - 1, col, True)),
                                    True))
                        elif colName == "median":
                            self.add(
                                self.resultOffset + 6,
                                colRef,
                                FormulaCell(
                                    "of:=SUM([.{0}:.{1}]<[.{2}:.{3}])".format(
                                        self.cellIndex(2, colRef),
                                        self.cellIndex(self.resultOffset - 1, colRef),
                                        self.cellIndex(2, col, True),
                                        self.cellIndex(self.resultOffset - 1, col, True)),
                                    True))
                            self.add(
                                self.resultOffset + 7,
                                colRef,
                                FormulaCell(
                                    "of:=SUM([.{0}:.{1}]>[.{2}:.{3}])".format(
                                        self.cellIndex(2, colRef),
                                        self.cellIndex(self.resultOffset - 1, colRef),
                                        self.cellIndex(2, col, True),
                                        self.cellIndex(self.resultOffset - 1, col, True)),
                                    True))
                        elif colName == "max":
                            self.add(
                                self.resultOffset + 8,
                                colRef,
                                FormulaCell(
                                    "of:=SUM([.{0}:.{1}]=[.{2}:.{3}])".format(
                                        self.cellIndex(2, colRef),
                                        self.cellIndex(self.resultOffset - 1, colRef),
                                        self.cellIndex(2, col, True),
                                        self.cellIndex(self.resultOffset - 1, col, True)),
                                    True))
                    col += 1
            column.calcSummary(self.resultOffset - 2, [])

        # calc values for the footers
        for systemColumn in self.systemColumns.values():
            systemColumn.calcSummary(self.resultOffset - 2, resultColumns)
            for column in systemColumn.columns.values():
                value_rows.add(column.name, column.summary.sum, self.resultOffset - 2 + 1, column.offset)
                value_rows.add(column.name, column.summary.avg, self.resultOffset - 2 + 2, column.offset)
                value_rows.add(column.name, column.summary.dev, self.resultOffset - 2 + 3, column.offset)
                value_rows.add(column.name, column.summary.dst, self.resultOffset - 2 + 4, column.offset)
                value_rows.add(column.name, -column.summary.best, self.resultOffset - 2 + 5, column.offset)
                value_rows.add(column.name, -column.summary.better, self.resultOffset - 2 + 6, column.offset)
                value_rows.add(column.name, column.summary.worse, self.resultOffset - 2 + 7, column.offset)
                value_rows.add(column.name, column.summary.worst, self.resultOffset - 2 + 8, column.offset)

        # apply some styles to the instance sheet
        for name, line, red, green in value_rows:
            for i in red:
                cell = self.get(2 + line, i)
                cell.style = "cellBest"
            for i in green:
                cell = self.get(2 + line, i)
                cell.style = "cellWorst"

    def addRunspec(self, runspec):
        key = (runspec.setting, runspec.machine)
        if not key in self.systemColumns:
            self.systemColumns[key] = SystemColumn(runspec.setting, runspec.machine)
        column = self.systemColumns[key]
        self.machines.add(column.machine)
        for class_result in runspec:
            classSum = {}
            for inst_result in class_result:
                for run in inst_result:
                    for name, valueType, value in run.iter(self.measures):
                        # print name,valueType, value
                        if valueType != "float": valueType = "string"
                        if self.instanceTable is None:
                            column.addCell(inst_result.instance.line + run.number - 1, name, valueType, value)
                        elif valueType == "float":
                            if not name in classSum:
                                classSum[name] = (0.0, 0)
                            classSum[name] = (float(value) + classSum[name][0], 1 + classSum[name][1])

            if not self.instanceTable is None:
                for name, value in classSum.items():
                    resTemp = value[0] / value[1]
                    if name == "timeout": resTemp = value[0]
                    column.addCell(class_result.benchclass.line, name, "class_result",
                                   (class_result.benchclass, resTemp))


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
        if minmum != None:
            minmum.extend([None for _ in range(0, self.count - len(minmum))])
            sdsum = 0
            for a, b in zip(colA, minmum):
                if a != None:
                    if a <= b:
                        self.best += 1
                    sdsum += (a - b) * (a - b)
            self.dst = math.sqrt(sdsum)
        # better, worse
        if median != None:
            median.extend([None for _ in range(0, self.count - len(median))])
            for a, b in zip(colA, median):
                if a != None:
                    if a < b:
                        self.better += 1
                    elif a > b:
                        self.worse += 1
        # worst
        if maximum != None:
            maximum.extend([None for _ in range(0, self.count - len(maximum))])
            for a, b in zip(colA, maximum):
                if a != None and a >= b:
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
        elif self.type == "float" and value != None:
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

    def addCell(self, line, name, valueType, value):
        if not name in self.columns:
            self.columns[name] = ValueColumn(name, valueType)
        self.columns[name].addCell(line, value)
