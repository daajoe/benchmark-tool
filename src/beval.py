'''
Created on Jan 13, 2010

@author: Roland Kaminski
'''
import argparse
from benchmarktool.runscript.parser import Parser
from cStringIO import StringIO
from lxml import etree
import sys


def parse_args():
    parser = argparse.ArgumentParser(description='%s files')
    parser.add_argument('infile', nargs=1, type=str)
    parser.add_argument('-c', '--csv', dest='csv', action='store_true',
                        help='output a csv file', default=False)
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = parse_args()
    filename = args.infile[0]
    csv = args.csv

    p = Parser()
    run = p.parse(filename)
    if not csv:
        run.evalResults(sys.stdout)
    else:
        output = StringIO()
        run.evalResults(output)
        # TODO: convert xml to csv
        root = etree.fromstring(output.getvalue())
        raise NotImplementedError('TODO:')
