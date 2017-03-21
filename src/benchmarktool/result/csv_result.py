'''
Created on Jan 20, 2010
@author: Roland Kaminski

Modified on Mar 19, 2017
@author: Johannes K. Fichte
'''
import os
import zipfile
from collections import OrderedDict
from collections import defaultdict
from itertools import izip, count, imap
from operator import attrgetter, itemgetter

import numpy as np

try:
    from cStringIO import StringIO
except:
    from io import StringIO
from benchmarktool.tools import Sortable, cmp
from csv import DictWriter
import math


def all_same(iterable):
    return all(x == iterable[0] for x in iterable)


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
    def __init__(self, benchmark, measures, project_name):
        self.benchmark = benchmark
        self.measures = measures
        self.results = {}
        self.keys = []
        self.project_name = project_name
        self.instSheets = InstanceTable(benchmark, measures, "ta1")
        # self.classSheets = ClassTable(benchmark, measures, "ta1")

    def finish(self):
        self.instSheets.finish(self.results)
        # TODO:
        # self.classSheet.finish()
        # TODO:
        # self.summarySheet.finish()

    def printSheet(self, out):
        # tools have to run from benchmark-tool dir otherwise
        # /usr/bin/python: can't open file 'src/bconv.py'
        # hence it's safe to assume cwd here
        # TODO: replace by a clean way based on the output location;
        #       likely requires additional output from bconv
        output_dir = os.path.join(os.getcwd(), 'output', self.project_name)

        # zipFile = zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED)
        # TODO(1): solution quality (improved over upper bounds)
        # TODO(*): specify solution quality col in xml file
        # TODO(*): vbest solver configuration by configuration name
        # TODO(2): cactus plot runtime, cactus plot (best 5 configs)
        # TODO(3): cactus plot solution-quality, cactus plot (best 5 configs)
        self.instSheets.printSheet(prefix=output_dir, project_name=self.project_name, suffix='.csv',
                                   results=self.results, keys=self.keys)

        return

    # def addRunspec(self, runspec):



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
        d = OrderedDict()
        d['solver'] = runspec.setting.system.name
        d['solver_version'] = runspec.setting.system.version
        d['solver_config'] = runspec.setting.name
        d['solver_args'] = runspec.setting.cmdline
        d['benchmark_name'] = runspec.benchmark.name
        d['machine'] = runspec.machine.name
        self.keys = d.keys()
        self.results[tuple(d.values())] = benchmarks


class Table:
    def __init__(self, name):
        self.name = name

    def printSheet(self, out, results, keys=None):
        if len(results) == 0:
            return
        keys = results[0].keys()
        # TODO(1): move sort order to xml-file: use parameter keys
        # TODO(3): sort order depending on by-instance, by-whatever
        basic_sort_order = ['instance', 'benchmark_name', 'class', 'number_of_instances', 'width', 'solved', 'time',
                            'wall', 'solver', 'solver_config']
        sum_order = ['avg', 'min', 'max', 'stdev']
        sort_order = []
        for i in basic_sort_order:
            sort_order.append(i)
            for j in sum_order:
                sort_order.append('%s-%s' % (i, j))

        remaining = set(keys) - set(sort_order)
        sort_order.extend(remaining)
        sort_order = dict(imap(lambda x: (x[1], x[0]), enumerate(sort_order)))
        header = sorted(keys, key=lambda val: sort_order[val])
        writer = DictWriter(out, fieldnames=header)
        writer.writeheader()
        writer.writerows(results)


class ResultTable(Table):
    def __init__(self, benchmark, measures, name, instance_table=None):
        Table.__init__(self, name)
        self.benchmark = benchmark
        self.results = {}
        self.measures = measures

    def finish(self, results):
        pass


class InstanceTable(ResultTable):
    def __summarize(self, aggregated, instance_str):
        merged_results = {}
        additional_stats = {}
        for k, values in aggregated.iteritems():
            if len(values) > 0:
                if type(values[0]) in (float, int):
                    # TODO: move precision to xml file
                    additional_stats['%s-min' % k] = round(min(values), 4)
                    additional_stats['%s-max' % k] = round(max(values), 4)
                    # todo: move mean vs. sum parameters to xml file
                    if k != 'number_of_instances':
                        merged_results['%s' % k] = round(np.mean(values), 4)
                    else:
                        merged_results['%s' % k] = round(np.sum(values), 4)
                    additional_stats['%s-stdev' % k] = round(np.std(values), 4)
                if type(values[0]) in (str, unicode):
                    if all_same(values):
                        merged_results[k] = values[0]
                        # TODO: xml allow various as value instead of deleting cols
                        # else:
                        #     merged_results[k] = 'various'
        if 'number_of_instances' not in aggregated:
            merged_results['number_of_instances'] = 1
        return merged_results, additional_stats

    def store_and_merge(self, to_lines, from_lines, instance_str, output):
        avg_data, additional_stats = self.__summarize(from_lines, instance_str)
        if to_lines is not None:
            for k, v in avg_data.iteritems():
                to_lines[k].append(v)
        ret = {}
        ret.update(avg_data)
        ret.update(additional_stats)
        output[instance_str].append(ret)

    def printSheet(self, prefix, project_name, suffix, results, keys):
        # inplace because output might be really large
        # TODO: if really no need, then remove it here and put it in different functions
        output = defaultdict(list)
        for key, values in results.iteritems():
            benchmark_info = dict(izip(keys, key))
            benchmark_lines = defaultdict(list)
            for clazz, clazz_val in values.iteritems():
                clazz_lines = defaultdict(list)
                for instance, runs in clazz_val.iteritems():
                    instance_lines = defaultdict(list)
                    for run_id, res in runs.iteritems():
                        run_line = {}
                        for k, measure in res.iteritems():
                            if type(measure) == float:
                                measure = round(measure, 4)
                            run_line[k] = measure

                        run_line.update(benchmark_info)
                        run_line.update({'instance': instance, 'class': clazz})
                        output['by-run'].append(run_line)
                        for k, v in run_line.iteritems():
                            instance_lines[k].append(v)

                    self.store_and_merge(clazz_lines, instance_lines, 'by-instance', output)
                self.store_and_merge(benchmark_lines, clazz_lines, 'by-class', output)
            self.store_and_merge(None, benchmark_lines, 'by-benchmark', output)

        for k in output.iterkeys():
            with open(os.path.join(prefix, '%s-%s%s' % (project_name, k, suffix)), 'w') as outfile:
                if k in ('by-instance', 'by-run'):
                    output[k].sort(key=itemgetter('instance', 'time'))
                if k == 'by-class':
                    output[k].sort(key=itemgetter('class', 'time'))
                if k == 'by-benchmark':
                    output[k].sort(key=itemgetter('benchmark_name', 'number_of_instances', 'time'))
                ResultTable.printSheet(self, out=outfile, results=output[k])


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
        if not name in self.columns:
            self.columns[name] = ValueColumn(name, value_type)
        self.columns[name].addCell(line, value)
