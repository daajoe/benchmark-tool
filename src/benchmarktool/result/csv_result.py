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
from itertools import izip, count, imap, cycle, ifilter
from operator import attrgetter, itemgetter
import time
import numpy as np
import pandas as pd
# without X
import matplotlib as mpl

mpl.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

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
                    row = {}
                    for name, value_type, value in run.iter(self.measures):
                        if value_type == 'int':
                            try:
                                row[name] = np.int(value)
                            except ValueError, e:
                                row[name] = np.nan
                        elif value_type == 'float':
                            row[name] = np.float(value)
                        else:
                            row[name] = value
                    runs[run.number] = row
                benchmarks[clazz_name][inst_result.instance.name] = runs
        d = OrderedDict()
        d['solver'] = runspec.setting.system.name
        d['solver_measure'] = runspec.setting.system.measures
        d['solver_version'] = runspec.setting.system.version
        d['solver_config'] = runspec.setting.name
        d['plot_type'] = runspec.setting.plot_type
        d['plot_color'] = runspec.setting.plot_color
        d['plot_name'] = runspec.setting.plot_name
        d['plot_show'] = runspec.setting.plot_show
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
                            'time', 'solver', 'solver_config', 'error_code']
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

    def output_cactus_plot(self, plots, filename, benchmark, mapping, indices=('time', 'memusage'), ignore_vbest=False,
                           limit=5):
        if 'vbest' not in mapping:
            mapping['vbest'] = (True, 'vbest', 'm', ':')
        for index in indices:
            configs = plots['solver_config'].unique()
            NUM_COLORS = len(configs) + 1
            # Latex Fonts
            # TODO: move to xml config
            plt.rc('font', family='serif')
            # plt.rc('text', usetex=True)
            plt.rcParams['text.usetex'] = True
            plt.rcParams['text.latex.preamble'] = [r'\usepackage{amsmath}\def\hy{\hbox{-}\nobreak\hskip0pt}']

            fig = plt.figure()
            ax = fig.add_subplot(111)

            lfont = lambda x: '$\mathtt{%s}$' % x.replace('-', '\hy')
            ignorelist = imap(lambda x: x[0], ifilter(lambda x: x[1], mapping))

            for key in configs:
                if key in ignorelist:
                    continue
                plot = plots[(plots['solver_config'] == key)]
                # ignore warning deliberately
                pd.options.mode.chained_assignment = None
                # sort by runtime/etc.
                plot.sort_values(by=[index], inplace=True)
                pd.options.mode.chained_assignment = 'warn'
                plot.reset_index(inplace=True)
                ts = pd.Series(plot[index])
                label = lfont(mapping[key][1]) if mapping.has_key(key) else key
                ax = ts.plot(markeredgecolor='none', label=label, color=mapping[key][2], linestyle=mapping[key][3])

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
            ax.legend(handles, labels, loc='best', prop={'size': 8}, frameon=False, mode='expand')

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
        return res_filename + ''.join(file_ext)

    # TODO: signature
    def printSheet(self, prefix, project_name, suffix, results, keys):
        def output_path(oparm, osuffix=suffix):
            return os.path.join(prefix, '%s-%s%s' % (project_name, oparm, osuffix))

        if any(k == 'pace_jkf' for k in results.iterkeys()):
            self.printSheetTrellis(prefix, project_name, suffix, results, keys)
            return

        # TODO: move properties to dedicated file class/property
        rows = []
        plot_mappings = {}

        output = defaultdict(list)
        for key, values in results.iteritems():
            benchmark_info = dict(izip(keys, key))
            benchmark_info['solver_config'] = '%s-%s' % (
            benchmark_info['solver_config'], benchmark_info['solver_version'])
            # gather additional plot infos
            pname = benchmark_info['plot_name'] if benchmark_info['plot_name'] else benchmark_info['solver_config']
            pcolor = benchmark_info['plot_color'] if benchmark_info['plot_color'] else 'm'
            ptype = benchmark_info['plot_type'] if benchmark_info['plot_type'] else ':'
            pshow = benchmark_info['plot_show'] if benchmark_info['plot_show'] else True
            plot_mappings[benchmark_info['solver_config']] = (pshow, pname, pcolor, ptype)
            del benchmark_info['plot_show']
            del benchmark_info['plot_name']
            del benchmark_info['plot_color']
            del benchmark_info['plot_type']

            for clazz, clazz_val in values.iteritems():
                for instance, runs in clazz_val.iteritems():
                    for run_id, res in runs.iteritems():
                        run_line = {}
                        for k, measure in res.iteritems():
                            if type(measure) == float:
                                measure = round(measure, 4)
                            run_line[k] = measure

                        run_line.update(benchmark_info)
                        run_line.update({'instance': instance, 'class': clazz})
                        rows.append(run_line)

        df = pd.DataFrame(rows)
        df.replace(to_replace='-1', value=np.nan, inplace=True)

        df = df[(df['error'] < 64)]

        # list of non-memedout instances
        nonmemout = df[(df['error'] < 2)][['full_path', 'instance']]
        def myfunc(x):
            ret = x.replace('./','').split('/')
            ret = '%s/%s' %(ret[4], '/'.join(ret[6:-2]))
            return ret
        nonmemout['full_path'] = df['full_path'].apply(myfunc)
        nonmemout.sort_values(by=['full_path', 'instance'], inplace=True)
        nonmemout.drop_duplicates().reset_index(drop=True).to_csv(output_path('nomemout'), index=False)

        # TODO: generalize to xml file
        df_mem_range = df.copy()
        df_mem_range['mem_range'] = df['memusage']
        df_mem_range['mem_range'] = pd.cut(df_mem_range['memusage'], np.arange(0, 10000, 250))
        output['by-mem'] = df_mem_range.groupby(
            ['benchmark_name', 'mem_range', 'solver_config', 'solver', 'solver_args']).agg(
            {'instance': 'count', 'time': [np.mean, np.max, np.min, np.std, np.sum], 'error': [np.mean, np.max],
             'memusage': [np.mean, np.max, np.min, np.std], 'solved': np.sum}).reset_index()

        df_time_range = df.copy()
        df_time_range['time_range'] = df['time']
        df_time_range['time_range'] = pd.cut(df_mem_range['time'], np.arange(0, 1800, 120))
        output['by-time'] = df_time_range.groupby(
            ['benchmark_name', 'time_range', 'solver_config', 'solver', 'solver_args']).agg(
            {'instance': 'count', 'time': [np.mean, np.max, np.min, np.std, np.sum], 'error': [np.mean, np.max],
             'memusage': [np.mean, np.max, np.min, np.std], 'solved': np.sum}).reset_index()

        output['by-run'] = df
        output['by-instance'] = df.groupby(['instance', 'benchmark_name', 'class', 'solver_config', 'solver',
                                            'solver_args', 'status', 'timelimit', 'memlimit', 'solved']).agg(
            {'run': 'count', 'time': [np.mean, np.max, np.min, np.std], 'error': [np.mean, np.max],
             'memusage': [np.mean, np.max, np.min, np.std]}).reset_index()

        output['by-class'] = df.groupby(
            ['benchmark_name', 'class', 'solver_config', 'solver', 'solver_args', 'status', 'timelimit',
             'memlimit']).agg(
            {'instance': 'count', 'time': [np.mean, np.max, np.min, np.std], 'error': [np.mean, np.max],
             'memusage': [np.mean, np.max, np.min, np.std]}).reset_index()

        output['by-benchmark'] = df.groupby(['benchmark_name', 'solver_config', 'status', 'timelimit', 'memlimit']).agg(
            {'instance': 'count', 'time': [np.mean, np.max, np.min, np.std], 'error': [np.mean, np.max],
             'memusage': [np.mean, np.max, np.min, np.std]}).reset_index()

        output['by-all'] = df.groupby(['solver_config']).agg(
            {'instance': 'count', 'time': [np.mean, np.max, np.min, np.std], 'error': [np.mean, np.max],
             'memusage': [np.mean, np.max, np.min, np.std]}).reset_index()

        for k in output.iterkeys():
            with open(os.path.join(prefix, '%s-%s%s' % (project_name, k, suffix)), 'w') as outfile:
                # order header
                col_ord = self.sort_order(list(output[k].columns))
                output[k] = output[k].reindex_axis(col_ord, axis=1)
                # order values
                if k == 'by-run':
                    output[k].sort_values(by=['instance', 'time'], inplace=True)
                elif k == 'by-instance':
                    output[k].sort_values(by=[('instance', ''), ('time', 'mean'), ('memusage', 'mean')], inplace=True)
                elif k == 'by-class':
                    output[k].sort_values(
                        by=['benchmark_name', 'class', ('time', 'mean'), ('memusage', 'mean')],
                        ascending=[True, True, True, True], inplace=True)
                    output[k].reset_index()
                elif k == 'by-time':
                    output[k].sort_values(
                        by=['benchmark_name', 'time_range', ('time', 'mean'), ('memusage', 'mean')],
                        ascending=[True, True, False, True], inplace=True)
                    output[k].reset_index()
                elif k == 'by-mem':
                    output[k].sort_values(
                        by=['benchmark_name', 'mem_range', ('time', 'mean'), ('memusage', 'mean')],
                        ascending=[True, True, True, True], inplace=True)
                    output[k].reset_index()
                elif k == 'by-benchmark':
                    output[k].sort_values(
                        by=['benchmark_name', ('instance', 'count'), ('time', 'mean'), ('memusage', 'mean')],
                        ascending=[True, False, True, True], inplace=True)
                elif k == 'by-all':
                    output[k].sort_values(
                        by=[('instance', 'count'), ('time', 'mean'), ('memusage', 'mean')],
                        ascending=[False, True, True], inplace=True)

                # vbest_all, vbest_improved_all = self.compute_vbest_solution_quality_all(df)
                # output csv
                # noinspection PyUnboundLocalVariable
                output[k].to_csv(outfile, index=False)

                # output a minimal attribute file
                max_cols = ['instance', 'benchmark_name', 'class', 'tw_range', 'abs_improvement', 'time', 'solved',
                            'solver_config']
                av_cols = map(lambda x: x[0] if isinstance(x, tuple) else x, list(output[k].columns.values))
                sel_cols = [item for item in max_cols if item in av_cols]

                output[k][sel_cols].to_csv(self.ext(outfile.name, 'short'), index=False)

        key1 = 'time'
        vbest, vbest_improved = self.compute_vbest(df, key1)
        vbest.to_csv(output_path('vbest'))
        vbest_improved.to_csv(output_path('vbest-improved'))
        vbest[['instance', 'solver_config', key1]].to_csv(output_path('vbest_short'))
        vbest_improved[['instance', 'solver_config', key1]].to_csv(output_path('vbest-improved_short'))

        short_df = self.compute_short_df(df, vbest)
        short_df_non_zero = short_df[(short_df[key1] > 0)]

        self.output_cactus_plot(short_df, output_path('cactus_plot', ''), project_name, plot_mappings)
        self.output_cactus_plot(short_df_non_zero, output_path('cactus_plot_improved', ''), project_name, plot_mappings)


    def compute_vbest_solution_quality_all(self, df):
        self.compute_vbest_solution_quality_all(df, 'abs_improvement')

    # def compute_vbest_solution_quality(self, df, key):
    #     max_improvements = df.reset_index()
    #     max_improvements.sort_values(by=['benchmark_name', 'class', 'instance', key],
    #                                  ascending=[True, True, True, False], inplace=True)
    #     vbest = max_improvements.groupby(['instance']).head(1)
    #     # order header
    #     col_ord = self.sort_order(list(vbest.columns))
    #     vbest = vbest.reindex_axis(col_ord, axis=1)
    #     vbest_improved = vbest[(vbest[key] > 0)]
    #     return vbest, vbest_improved

    def compute_short_df(self, df, vbest):
        # take short vbest
        vbest_short = vbest[['instance', 'solver_config', 'time', 'memusage']]
        # ignore warning deliberately
        pd.options.mode.chained_assignment = None
        vbest_short['solver_config'] = 'vbest'
        pd.options.mode.chained_assignment = 'warn'
        short_df = df[['instance', 'solver_config', 'time', 'memusage']]
        short_df = short_df.append(vbest_short)
        short_df = short_df.reindex_axis(['solver_config', 'instance', 'time', 'memusage'], axis=1)
        return short_df

    def compute_vbest_solution_quality(self, df):
        return self.compute_vbest(df, 'abs_improvement')

    def compute_vbest(self, df, key):
        max_improvements = df.reset_index()
        max_improvements.sort_values(by=['benchmark_name', 'class', 'instance', key],
                                     ascending=[True, True, True, False], inplace=True)
        vbest = max_improvements.groupby(['benchmark_name', 'class', 'instance']).head(1)
        # order header
        col_ord = self.sort_order(list(vbest.columns))
        vbest = vbest.reindex_axis(col_ord, axis=1)
        vbest_improved = vbest[(vbest[key] > 0)]
        return vbest, vbest_improved

    # TODO:
    # def compute_vbest_solution_quality_runtime(self, df):
    #     max_improvements = df.reset_index()
    #     max_improvements.sort_values(by=['benchmark_name', 'class', 'instance', 'abs_improvement'],
    #                                  ascending=[True, True, True, False], inplace=True)
    #     vbest = max_improvements.groupby(['benchmark_name', 'class', 'instance']).head(1)
    #     # order header
    #     col_ord = self.sort_order(list(vbest.columns))
    #     vbest = vbest.reindex_axis(col_ord, axis=1)
    #     vbest_improved = vbest[(vbest['abs_improvement'] > 0)]
    #     return vbest, vbest_improved


    # TODO: move to different sheet
    # TODO: move to pandas
    def print_error_sheets(self, prefix, project_name, suffix, results, keys):
        error_codes = {0: 'ok', 1: 'timeout', 2: 'memout', 4: 'presolver_timeout', 8: 'dnf',
                       16: 'invalid_decomposition', 32: 'invalid_input',
                       64: 'solver_runtime_error', 128: 'unknown_error'}
        errors = {i: [] for i in error_codes.iterkeys()}
        num_instances = 0
        output = []
        for key, values in results.iteritems():
            benchmark_info = dict(izip(keys, key))
            for clazz, clazz_val in values.iteritems():
                for instance, runs in clazz_val.iteritems():
                    for run_id, res in runs.iteritems():
                        run_line = {}
                        run_line.update(benchmark_info)
                        run_line.update(
                            {'instance': instance, 'class': clazz, 'error': res['error'], 'solved': res['solved'],
                             'full_path': res['full_path']})
                        for err_key in errors.iterkeys():
                            if err_key == 0:
                                if res['error'] == 0:
                                    errors[err_key].append({'instance': instance, 'full_path': res['full_path']})
                                continue
                            val = res['error'] // err_key
                            if val == 1:
                                errors[err_key].append({'instance': instance, 'full_path': res['full_path']})
                        num_instances += 1
                        output.append(run_line)

        # print single instance outputs
        for k, v in error_codes.iteritems():
            with open(os.path.join(prefix, '%s-error-%s%s' % (project_name, v, suffix)), 'w') as outfile:
                errors[k].sort(key=itemgetter('instance'))
                ResultTable.printSheet(self, out=outfile, results=errors[k])

        # print summary outputs
        summary = []
        for k, v in error_codes.iteritems():
            summary.append(
                {'error/ok': v, 'error_code': k, 'abs_num': len(errors[k]), 'rel_num': len(errors[k]) / num_instances})
        with open(os.path.join(prefix, '%s-%s%s' % (project_name, 'error-0summary', suffix)), 'w') as outfile:
            ResultTable.printSheet(self, out=outfile, results=summary)

    def printSheetTrellis(self, prefix, project_name, suffix, results, keys):
        def output_path(oparm, osuffix=suffix):
            return os.path.join(prefix, '%s-%s%s' % (project_name, oparm, osuffix))

        rows = []
        output = defaultdict(list)
        for key, values in results.iteritems():
            benchmark_info = dict(izip(keys, key))
            for clazz, clazz_val in values.iteritems():
                for instance, runs in clazz_val.iteritems():
                    for run_id, res in runs.iteritems():
                        run_line = {}
                        for k, measure in res.iteritems():
                            if type(measure) == float:
                                measure = round(measure, 4)
                            run_line[k] = measure

                        run_line.update(benchmark_info)
                        run_line.update({'instance': instance, 'class': clazz})
                        if res['width'] != -1 and res['ubound'] != -1:
                            abs_improvement = res['ubound'] - res['width']
                            try:
                                rel_improvement = round(abs_improvement / float(res['width']), 4)
                            except ZeroDivisionError:
                                rel_improvement = 0
                        else:
                            rel_improvement = abs_improvement = 0
                        run_line.update({'rel_improvement': rel_improvement, 'abs_improvement': abs_improvement})
                        rows.append(run_line)

        # TODO: generalize to xml file
        df = pd.DataFrame(rows)
        df.replace(to_replace='-1', value=np.nan, inplace=True)

        output['by-run'] = df
        output['by-instance'] = df.groupby(['instance', 'benchmark_name', 'class', 'solver_config', 'solver',
                                            'solver_args']).agg(
            {'run': 'count', 'width': [np.mean, np.max, np.min, np.std],
             'ubound': [np.mean, np.max, np.min, np.std], 'abs_improvement': [np.max, np.count_nonzero, np.sum],
             'wall': [np.mean, np.max, np.min, np.std], 'time': [np.mean, np.max, np.min, np.std],
             'error': [np.max]})

        output['by-instance'].reset_index(inplace=True)
        output['by-class'] = df.groupby(
            ['benchmark_name', 'class', 'solver_config', 'solver', 'solver_args']).agg(
            {'instance': 'count', 'width': [np.mean, np.max, np.min, np.std],
             'ubound': [np.mean, np.max, np.min, np.std], 'abs_improvement': [np.max, np.count_nonzero, np.sum],
             'wall': [np.mean, np.max, np.min, np.std], 'time': [np.mean, np.max, np.min, np.std]}).reset_index()

        # TODO: move ranges to xml file parameter
        # Group by treewidth/ubound ranges
        df_width = df.copy()
        df_width['tw_range'] = df['width']
        # pd.cut(df["B"], np.arange(0,1.0+0.155,0.155))
        df_width['tw_range'] = pd.cut(df_width['width'], np.arange(0, 500, 25))

        output['by-width'] = df_width.groupby(
            ['benchmark_name', 'tw_range', 'solver_config', 'solver', 'solver_args']).agg(
            {'instance': 'count', 'width': [np.mean, np.max, np.min, np.std],
             'ubound': [np.mean, np.max, np.min, np.std], 'abs_improvement': [np.max, np.count_nonzero, np.sum],
             'wall': [np.mean, np.max, np.min, np.std], 'time': [np.mean, np.max, np.min, np.std, np.sum],
             'solved': np.sum}).reset_index()

        output['by-benchmark'] = df.groupby(['benchmark_name', 'solver_config']).agg(
            {'instance': 'count', 'width': [np.mean, np.max, np.min, np.std],
             'ubound': [np.mean, np.max, np.min, np.std], 'abs_improvement': [np.max, np.count_nonzero, np.sum],
             'wall': [np.mean, np.max, np.min, np.std], 'time': [np.mean, np.max, np.min, np.std]}).reset_index()

        output['by-all'] = df.groupby(['solver_config']).agg(
            {'instance': 'count', 'width': [np.mean, np.max, np.min, np.std],
             'ubound': [np.mean, np.max, np.min, np.std], 'abs_improvement': [np.max, np.count_nonzero, np.sum],
             'wall': [np.mean, np.max, np.min, np.std], 'time': [np.mean, np.max, np.min, np.std]}).reset_index()

        for k in output.iterkeys():
            with open(os.path.join(prefix, '%s-%s%s' % (project_name, k, suffix)), 'w') as outfile:
                with open(os.path.join(prefix, '%s-improved-%s%s' % (project_name, k, suffix)), 'w') as outfile_filter:
                    # order header
                    col_ord = self.sort_order(list(output[k].columns))
                    output[k] = output[k].reindex_axis(col_ord, axis=1)
                    # order values
                    if k == 'by-run':
                        filter = 'abs_improvement'
                        output[k].sort_values(by=['instance', 'abs_improvement', 'time'], inplace=True)
                    elif k == 'by-instance':
                        filter = ('abs_improvement', 'amax')
                        output[k].sort_values(by=[('instance', ''), ('abs_improvement', 'amax'), ('time', 'mean')],
                                              inplace=True)
                    elif k == 'by-class':
                        filter = ('abs_improvement', 'amax')
                        # output[k].sort_values(by=['class', ('abs_improvement', 'amax'), ('time', 'mean')], inplace=True)
                        output[k].sort_values(
                            by=['benchmark_name', 'class', ('abs_improvement', 'sum'), ('time', 'mean')],
                            ascending=[True, True, False, True], inplace=True)
                        output[k].reset_index()
                    elif k == 'by-width':
                        filter = ('abs_improvement', 'amax')
                        # output[k].sort_values(by=['class', ('abs_improvement', 'amax'), ('time', 'mean')], inplace=True)
                        output[k].sort_values(
                            by=['benchmark_name', 'tw_range', ('abs_improvement', 'sum'), ('time', 'mean')],
                            ascending=[True, True, False, True], inplace=True)
                        output[k].reset_index()
                    elif k == 'by-benchmark':
                        filter = ('abs_improvement', 'amax')
                        # ('abs_improvement', 'amax')
                        output[k].sort_values(
                            by=['benchmark_name', ('abs_improvement', 'sum'), ('instance', 'count'), ('time', 'mean')],
                            ascending=[True, False, False, True], inplace=True)
                    elif k == 'by-all':
                        filter = ('abs_improvement', 'amax')
                        # ('abs_improvement', 'amax')
                        output[k].sort_values(
                            by=[('abs_improvement', 'sum'), ('instance', 'count'), ('time', 'mean')],
                            ascending=[False, False, True], inplace=True)

                        vbest_all, vbest_improved_all = self.compute_vbest_solution_quality_all(df)

                    # output csv
                    # noinspection PyUnboundLocalVariable
                    output[k][(output[k][filter] > 0)].to_csv(outfile_filter, index=False)
                    output[k].to_csv(outfile, index=False)

                    # output a minimal attribute file
                    max_cols = ['instance', 'benchmark_name', 'class', 'tw_range', 'abs_improvement', 'time', 'solved',
                                'solver_config']
                    av_cols = map(lambda x: x[0] if isinstance(x, tuple) else x, list(output[k].columns.values))
                    sel_cols = [item for item in max_cols if item in av_cols]

                    output[k][sel_cols][(output[k][sel_cols][filter] > 0)].to_csv(
                        self.ext(outfile_filter.name, 'short'), index=False)
                    output[k][sel_cols].to_csv(self.ext(outfile.name, 'short'), index=False)

        vbest, vbest_improved = self.compute_vbest_solution_quality(df)
        vbest.to_csv(output_path('vbest'))
        vbest_improved.to_csv(output_path('vbest-improved'))
        vbest[['instance', 'solver_config', 'abs_improvement']].to_csv(output_path('vbest_short'))
        vbest_improved[['instance', 'solver_config', 'abs_improvement']].to_csv(output_path('vbest-improved_short'))

        short_df = self.compute_short_df_trellis(df, vbest)
        short_df_non_zero = short_df[(short_df['abs_improvement'] > 0)]
        short_df2 = self.compute_cum_non_zero_trellis(df, vbest)

        self.output_cactus_plot(short_df, output_path('cactus_plot', ''), project_name)
        self.output_cactus_plot(short_df_non_zero, output_path('cactus_plot_improved', ''), project_name)
        self.output_cactus_plot(short_df2, output_path('cactus_plot_improved_cum', ''), project_name,
                                indices=('cum_sum_abs_improvement', 'time'))
        # print short_df2

    def output_cactus_plot_trellis(self, plots, filename, benchmark, indices=('abs_improvement', 'time'),
                                   ignore_vbest=False,
                                   limit=5):
        for index in indices:
            configs = plots['solver_config'].unique()
            NUM_COLORS = len(configs) + 1
            # Latex Fonts
            plt.rc('font', family='serif')
            # plt.rc('text', usetex=True)
            plt.rcParams['text.usetex'] = True
            plt.rcParams['text.latex.preamble'] = [r'\usepackage{amsmath}\def\hy{\hbox{-}\nobreak\hskip0pt}']

            cm = plt.get_cmap('gist_rainbow')
            fig = plt.figure()
            ax = fig.add_subplot(111)
            # ax.set_color_cycle([cm(1. * i / NUM_COLORS) for i in range(NUM_COLORS)])

            # TODO:
            # ax.set_prop_cycle([cm(1. * i / NUM_COLORS) for i in range(NUM_COLORS)])
            # marker = cycle(('.', 'p', '^', '*', 'd', 's', 'o'))  # (',', '+', '.', 'o', '*'))
            # marker = cycle(('.', 'p', '^'))  # (',', '+', '.', 'o', '*'))
            lstyle = cycle(['-', '--', '-.', ':'])

            # TODO: move and fix crappy relabeling
            mapping = {'jdrasil-b100-n1': 'sat-100-1800(900)',
                       'jdrasil-b75t1800-n1': 'sat-075-3600(1800)',
                       'jdrasil-b75t90r40-n1': 'sat-075-90-40',
                       'jdrasil-b75-n1': 'sat-075-1800(900)',
                       'jdrasil-b125-n1': 'sat-125-1800(900)',
                       'jdrasil-b150-n1': 'sat-150-1800(900)',
                       'htd-b75-n1': 'heur-075-1800',
                       'htd-b100-n1': 'heur-100-1800',
                       'htd-b125-n1': 'heur-125-1800',
                       'htd-b150-n1': 'heur-150-1800',
                       'tcs-b75-n1': 'bforce-075-1800',
                       'tcs-b100-n1': 'bforce-100-1800',
                       'tcs-b125-n1': 'bforce-125-1800',
                       'tcs-b150-n1': 'bforce-150-1800',
                       'vbest': 'vbest'}

            lfont = lambda x: '$\mathtt{%s}$' % x.replace('-', '\hy')
            # mapping = {}

            # b: blue
            # g: green
            # r: red
            # c: cyan
            # m: magenta
            # y: yellow
            # k: black
            # w: white
            # ['-', '--', '-.', ':'])
            # https://xkcd.com/color/rgb/

            # https://matplotlib.org/users/colormaps.html
            colors = defaultdict(lambda: ('m', ':'))
            colors.update(
                {'jdrasil-b100-n1': ('r', '-'),
                 'jdrasil-b75t1800-n1': ('r', '--'),
                 'jdrasil-b75t90r40-n1': ('r', '--'),
                 'jdrasil-b75-n1': ('r', '-.'),
                 'jdrasil-b125-n1': ('r', ':'),
                 'jdrasil-b150-n1': ('r', '-'),
                 'htd-b75-n1': ('c', '-'),
                 'htd-b100-n1': ('c', '-'),
                 'htd-b125-n1': ('c', '-'),
                 'htd-b150-n1': ('c', '-'),
                 # xkcd:lime
                 'tcs-b75-n1': ('xkcd:bright blue', '--'),
                 'tcs-b100-n1': ('xkcd:bright blue', '-'),
                 'tcs-b125-n1': ('xkcd:bright blue', ':'),
                 'tcs-b150-n1': ('xkcd:bright blue', '-.'),
                 'vbest': ('k', '-')})

            ignorelist = []
            # ignorelist = ['vbest']
            ignorelist = ['htd-b100-n1', 'jdrasil-b75-n1', 'jdrasil-b25-n1', 'jdrasil-b75t1800-n1',
                          'jdrasil-b50-n1', 'jdrasil-b150-n1',
                          'tcs-b150-n1', 'tcs-b75-n1', 'tcs-b50-n1', 'vbest']  # , 'jdrasil-b125-n1', , ] #, ]
            # 'jdrasil-b100-n1',
            # TODO: there is something broken with jdrasil-b75-n1

            #
            # print configs
            #
            # mapping = [('jdrasil', 'sat'), ('tcs', 'bruteforce'), ('htd', 'heuristic'), ('b', ''), ('n1', '1800-10'),
            #            ('t1800-1800', '-3600'), ('t90r40-1800-10', '-90-40')]
            # for i in xrange(len(configs)):
            #     for key, val in mapping:
            #         if configs[i] == 'vbest':
            #             continue
            #         configs[i] = configs[i].replace(key, val)

            # TODO: fix only best 'limit' configurations
            # patches = []
            for key in configs:
                if key in ignorelist:
                    continue
                plot = plots[(plots['solver_config'] == key)]
                # ignore warning deliberately
                pd.options.mode.chained_assignment = None
                # sort by runtime/etc.
                plot.sort_values(by=[index], inplace=True)
                pd.options.mode.chained_assignment = 'warn'
                plot.reset_index(inplace=True)
                # ts = pd.Series(plot['time'])
                ts = pd.Series(plot[index])
                # linestyle='', marker=marker.next()
                label = lfont(mapping[key]) if mapping.has_key(key) else key
                ax = ts.plot(markeredgecolor='none', label=label, linestyle=colors[key][1],  # lstyle.next(),
                             color=colors[key][0])  # , marker=marker.next())

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
            ax.legend(handles, labels, loc='best', prop={'size': 8}, frameon=False, mode='expand')

            # lgd = ax.legend(loc='best', prop={'size': 8}, frameon=False, mode='expand')
            # art.append(lgd)

            # plt.title('%s' % benchmark)
            plt.savefig('%s-%s.pdf' % (filename, index), bbox_inches="tight")  # , additional_artists=art)

            # fancybox=True, shadow=True, ncol=5)
            # ax.set_yscale("log", nonposx='clip')
            # plt.legend(handles=patches,loc=4)
            # plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)

    def compute_cum_non_zero_trellis(self, df, vbest):
        # take short vbest
        vbest_short = vbest[['instance', 'solver_config', 'abs_improvement', 'time']]
        # ignore warning deliberately
        pd.options.mode.chained_assignment = None
        vbest_short['solver_config'] = 'vbest'
        pd.options.mode.chained_assignment = 'warn'
        short_df = df[['instance', 'solver_config', 'abs_improvement', 'time']]
        short_df = short_df.append(vbest_short)
        short_df = short_df.reindex_axis(['solver_config', 'instance', 'abs_improvement', 'time'], axis=1)

        short_df = short_df[(short_df['abs_improvement'] > 0)]
        short_df.sort_values(by=['abs_improvement'], ascending=[True], inplace=True)

        # print short_df[['instance','solver_config','abs_improvement']]
        data2 = short_df.reset_index()
        data3 = data2.set_index(["solver_config", "index"])
        # print data2.groupby(['solver_config']).sum().groupby(['abs_improvement']).cumsum()
        res = data3.groupby(level=[0, 1]).sum().groupby(level=[0]).cumsum().reset_index()
        res['cum_sum_abs_improvement'] = res['abs_improvement']
        # res['abs_improvement']=short_df['abs_improvement']
        # print res
        # exit(1)
        return res
        # print short_df['abs_improvement'].cumsum()
        exit(1)
        short_df['cum_sum_abs_improvement'] = short_df['abs_improvement'].cumsum()
        # short_df.insert(1,'cum_abs_improvement', )

        return short_df

    def compute_short_df_trellis(self, df, vbest):
        # take short vbest
        vbest_short = vbest[['instance', 'solver_config', 'abs_improvement', 'time']]
        # ignore warning deliberately
        pd.options.mode.chained_assignment = None
        vbest_short['solver_config'] = 'vbest'
        pd.options.mode.chained_assignment = 'warn'
        short_df = df[['instance', 'solver_config', 'abs_improvement', 'time']]
        short_df = short_df.append(vbest_short)
        short_df = short_df.reindex_axis(['solver_config', 'instance', 'abs_improvement', 'time'], axis=1)
        return short_df


class Summary(ResultTable):
    pass
    # TODO: signature
    # def printSheet(self, prefix, project_name, suffix, results, keys):
    #     # inplace because output might be really large
    #     output = defaultdict(list)
    #     for key, values in results.iteritems():
    #         benchmark_info = dict(izip(keys, key))
    #         benchmark_lines = defaultdict(list)
    #         for clazz, clazz_val in values.iteritems():
    #             clazz_lines = defaultdict(list)
    #             for instance, runs in clazz_val.iteritems():
    #                 instance_lines = defaultdict(list)
    #                 for run_id, res in runs.iteritems():
    #                     run_line = {}
    #
    #
    #                     for k, measure in res.iteritems():
    #                         if type(measure) == float:
    #                             measure = round(measure, 4)
    #                         run_line[k] = measure
    #
    #                     run_line.update(benchmark_info)
    #                     run_line.update({'instance': instance, 'class': clazz, 'width': res['width'], 'ubound': res['ubound'], 'improvement': })
    #
    #                     output['by-run'].append(run_line)
    #                     for k, v in run_line.iteritems():
    #                         instance_lines[k].append(v)
    #
    #                 self.store_and_merge(clazz_lines, instance_lines, 'by-instance', output)
    #             self.store_and_merge(benchmark_lines, clazz_lines, 'by-class', output)
    #         self.store_and_merge(None, benchmark_lines, 'by-benchmark', output)
    #
    #     for k in output.iterkeys():
    #         with open(os.path.join(prefix, '%s-solution_quality-%s%s' % (project_name, k, suffix)), 'w') as outfile:
    #             if k in ('by-instance', 'by-run'):
    #                 output[k].sort(key=itemgetter('instance', 'time'))
    #             if k == 'by-class':
    #                 output[k].sort(key=itemgetter('class', 'time'))
    #             if k == 'by-benchmark':
    #                 output[k].sort(key=itemgetter('benchmark_name', 'number_of_instances', 'time'))
    #             ResultTable.printSheet(self, out=outfile, results=output[k])
    #
    #     #TODO: compute cactus plots
    #     pass


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
