'''
Created on Jan 20, 2010
@author: Roland Kaminski

Modified on Mar 19, 2017
@author: Johannes K. Fichte
'''
import os
from collections import OrderedDict
from collections import defaultdict
from itertools import izip, imap, cycle, ifilter, combinations
from operator import itemgetter

# without X
import matplotlib as mpl

mpl.use('TkAgg')

import numpy as np
import pandas as pd

pd.set_option('display.max_rows', 20)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

from matplotlib.backends.backend_pdf import PdfPages

import matplotlib.pyplot as plt

try:
    from cStringIO import StringIO
except:
    from io import StringIO
from benchmarktool.tools import Sortable, cmp
from csv import DictWriter


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
        # print dir(self.benchmark)
        self.instSheets.printSheet(prefix=output_dir, project_name=self.project_name, suffix='.csv',
                                   results=self.results, keys=self.keys)

        self.instSheets.print_error_sheets(prefix=output_dir, project_name=self.project_name, suffix='.csv',
                                           results=self.results, keys=self.keys)
        return

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
                    # ignore OSX finder files
                    if inst_result.instance.name == '.DS_Store':
                        continue
                    row = {}
                    for name, value_type, value in run.iter(self.measures):
                        if value_type == 'list':
                            row[name] = []
                            L = value[1:-1].split(',')
                            for l_value in L:
                                row[name].append(self.convert2datatype(l_value, value_type))
                        else:
                            row[name] = self.convert2datatype(value, value_type)
                    runs[run.number] = row
                benchmarks[clazz_name][inst_result.instance.name] = runs
        d = OrderedDict()
        d['solver'] = runspec.setting.system.name
        d['solver_measure'] = runspec.setting.system.measures
        d['solver_version'] = runspec.setting.system.version
        d['solver_config'] = runspec.setting.name
        d['plot_marker'] = runspec.setting.plot_marker
        d['plot_linestyle'] = runspec.setting.plot_linestyle
        d['plot_color'] = runspec.setting.plot_color
        d['plot_name'] = runspec.setting.plot_name
        d['plot_show'] = runspec.setting.plot_show
        d['solver_args'] = runspec.setting.cmdline
        d['benchmark_name'] = runspec.benchmark.name
        d['machine'] = runspec.machine.name
        self.keys = d.keys()
        self.results[tuple(d.values())] = benchmarks

    def convert2datatype(self, value, value_type):
        if value_type == 'int':
            if value == 'nan':
                return np.nan
            elif value.startswith('['):
                value = value[1:-1]
                if len(value) == 0:
                    return np.nan
                else:
                    return map(np.int, value.split(','))
            else:
                return np.int(value)
        elif value_type == 'float':
            if value == 'None':
                return np.nan
            elif value.startswith('['):
                value = value[1:-1]
                if len(value) == 0:
                    return np.nan
                else:
                    return map(np.float, value.split(','))
            else:
                return np.float(value)
        else:
            return value


class Table:
    def __init__(self, name):
        self.name = name

    def printSheet(self, out, results, keys=None):
        if len(results) == 0:
            return
        keys = results[0].keys()
        # TODO(1): move sort order to xml-file: use parameter keys
        # TODO(3): sort order depending on by-instance, by-whatever
        basic_sort_order = ['instance', 'benchmark_name', 'class', 'number_of_instances', 'width', 'ubound',
                            'abs_improvement', 'rel_improvement', 'solved', 'time',
                            'time', 'solver', 'solver_config', 'error_code']
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

    def get_measures_from_first_item(self, results, keys):
        measures = [('instance', str), ('class', str), ('rel_improvement', float), ('abs_improvement', float)]
        for key, values in results.iteritems():
            benchmark_info = dict(izip(keys, key))
            measures.extend(map(lambda x: (x, str), benchmark_info.keys()))

            for clazz, clazz_val in values.iteritems():
                for instance, runs in clazz_val.iteritems():
                    for run_id, res in runs.iteritems():
                        for k, v in res.iteritems():
                            measures.append((k, type(v)))
                        return measures
        return measures

    def sort_order(self, columns):
        if len(columns) == 0:
            return
        # TODO(1): move sort order to xml-file: use parameter keys
        basic_sort_order = ['instance', 'benchmark_name', 'class', 'number_of_instances', 'width', 'ubound',
                            'abs_improvement', 'rel_improvement', 'solved', 'time',
                            'time', 'solver', 'solver_config', 'error_code', 'objective']
        sum_order = ['', 'mean', 'count', 'count_nonzero', 'sum', 'amin', 'amax', 'std']
        sort_order = []
        for i in basic_sort_order:
            sort_order.append(i)
            for j in sum_order:
                sort_order.append((i, j))

        remaining = set(columns) - set(sort_order)
        sort_order.extend(remaining)
        sort_order = dict(imap(lambda x: (x[1], x[0]), enumerate(sort_order)))
        header = sorted(columns, key=lambda val: sort_order[val])
        return header

    def output_cactus_plot(self, df_plot, filename, benchmark, mapping, indices=('time', 'memusage'),
                           ignore_vbest=False,
                           limit=5):
        # set unsolved instances to timeout
        df_solved = df_plot.copy().reset_index()
        # print df_solved[(df_solved.solved != 0)][['solver', 'time', 'solved', 'error']]
        df_solved.loc[(df_solved.solved == 0), 'time'] = df_solved.timelimit

        # TODO: fix vbest
        if 'vbest' not in mapping:
            # TODO: move vbest color to XML file
            mapping['vbest'] = (True, 'vbest', '#ece7f2', '.', ':')
        for index in indices:
            configs = df_solved['solver_config'].unique()
            NUM_COLORS = len(configs) + 1
            # Latex Fonts
            # TODO: move to xml config
            plt.rc('font', family='serif')
            plt.rc('text', usetex=True)
            plt.rcParams['text.usetex'] = True
            plt.rcParams['text.latex.preamble'] = [r'\usepackage{amsmath}\def\hy{\hbox{-}\nobreak\hskip0pt}']

            fig = plt.figure()
            ax = fig.add_subplot(111)

            # lfont = lambda x: '$\mathtt{%s}$' % x.replace('-', '\hy')
            lfont = lambda x: x  # lambda x: '$\mathtt{%s}$' % x.replace('-', '\hy')
            ignorelist = imap(lambda x: x[0], ifilter(lambda x: x[1], mapping))

            num_solved = {}
            for key in configs:
                if key in ignorelist:
                    continue
                plot = df_solved[(df_solved['solver_config'] == key)]
                # ignore warning deliberately
                pd.options.mode.chained_assignment = None
                # sort by runtime/etc.
                plot.sort_values(by=[index], inplace=True)
                pd.options.mode.chained_assignment = 'warn'
                plot.reset_index(inplace=True)
                ts = pd.Series(plot[index])
                label = lfont(mapping[key][1]) if mapping.has_key(key) else key
                num_solved[label] = df_solved[(df_solved['solver_config'] == key) & (df_solved['solved'] == 1)][
                    'solved'].count()
                try:
                    # TODO: move dot size ms to central place
                    # linestyle=mapping[key][4]
                    # ax = ts.plot(markeredgecolor='none', label=label, color=mapping[key][2],
                    #              marker=mapping[key][3], linestyle=' ', markersize=3)
                    ax = ts.plot(markeredgecolor='none', label=label, color=mapping[key][2],
                                 marker=mapping[key][3], linestyle=' ')
                except ValueError, e:
                    print e
                    print 'marker=', mapping[key][3], 'line=', mapping[key][4]
                    print "For configuration %s" % key

            # sort labels in decreasing order from best configuration
            num_solved = sorted(num_solved.iterkeys(), key=lambda k: num_solved[k], reverse=True)
            # print num_solved
            handles, labels = ax.get_legend_handles_labels()

            # or sort them by labels
            # print handles, labels
            def mycomp(i, j):
                if num_solved.index(i) < num_solved.index(j):
                    return -1
                else:
                    return 1

            import operator
            hl = sorted(zip(handles, labels), key=operator.itemgetter(1), cmp=mycomp)
            handles2, labels2 = zip(*hl)
            # print handles2, labels2

            fig.subplots_adjust(bottom=0.3, left=0.1)
            # box = ax.get_position()
            # ax.set_position([box.x0, box.y0 + box.height * 0.1,
            #                  box.width, box.height * 0.9])

            # Put a legend below current axis
            # ax.legend(loc='upper center', bbox_to_anchor=(0.18, 0.9), prop={'size': 8}, frameon=False)  # ,
            # ax.legend(loc='upper center', bbox_to_anchor=(0.18, 0.9), prop={'size': 8}, frameon=False)  # ,
            art = []
            # lgd = ax.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0., frameon=False, mode='expand')
            # lgd = ax.legend(loc='lower right', bbox_to_anchor=(0.2, 0.2), prop={'size': 8}, frameon=False, mode='expand')

            # sort both labels and handles by labels
            handles, labels = ax.get_legend_handles_labels()
            labels, handles = zip(*sorted(zip(labels, handles), key=lambda t: t[0]))
            # print labels
            # ax.legend(handles, labels, loc='best', prop={'size': 12}, frameon=False, mode='expand')
            ax.legend(handles2, labels2, loc='best', prop={'size': 12}, frameon=False, mode='expand')

            # lgd = ax.legend(loc='best', prop={'size': 8}, frameon=False, mode='expand')
            # art.append(lgd)

            # plt.title('%s' % benchmark)
            plt.savefig('%s-%s.pdf' % (filename, index), bbox_inches="tight")  # , additional_artists=art)

            # fancybox=True, shadow=True, ncol=5)
            # ax.set_yscale("log", nonposx='clip')
            # plt.legend(handles=patches,loc=4)
            # plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)

    # TODO: cleanup and move config to xml

    def ext(self, filename, extend_by):
        name, file_ext = os.path.splitext(filename)
        res_filename = '%s_%s' % (name, extend_by)
