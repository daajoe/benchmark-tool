'''
Created on Jan 13, 2010

@author: Roland Kaminski
'''
import argparse
import sys

from benchmarktool.result.parser import Parser


def parse_args():
    parser = argparse.ArgumentParser(description='%s files')
    parser.add_argument('infile', nargs='?', type=argparse.FileType('r'),
                        default=sys.stdin)
    parser.add_argument("-p", "--projects", dest="projects", default="",
                        help="projects to display (by default all projects are shown)")
    parser.add_argument("-m", "--measures", dest="measures", default="time:t,timeout:to",
                        type=str, help="comma separated list of measures of form name[:{t,to,-}] to "
                                       "include in table (optional argument determines coloring)")
    parser.add_argument('-c', '--csv', dest='csv', action='store_true',
                        help='output a csv file', default=False)
    #TODO: ?
    # parser.add_argument("-o", "--output-folder", dest="output_folder", default="",
    #                     help="output folder")

    args = parser.parse_args()
    if args.csv:
        #TODO: summary
        #memout:t,timeout:t
        args.measures = 'wall:t,time:t,width:t,error:t,error_str:t,run:t,solved:t,stderr:t,full_path:t,ubound:t'
    return args


if __name__ == '__main__':
    opts = parse_args()
    inFile = opts.infile

    if opts.projects != "":  opts.projects = set(opts.projects.split(","))
    if opts.measures != "":
        measures = []
        for t in opts.measures.split(","):
            x = t.split(":", 1)
            if len(x) == 1:
                measures.append((x[0], None))
            else:
                measures.append(tuple(x))
        opts.measures = measures
    p = Parser()
    res = p.parse(inFile)

    try:
        out = sys.stdout.buffer
    except AttributeError:
        out = sys.stdout
    if not opts.csv:
        res.genOffice(out, opts.projects, opts.measures)
    else:
        res.genCSV(out, opts.projects, opts.measures)

