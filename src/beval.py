'''
Created on Jan 13, 2010

@author: Roland Kaminski
'''
import argparse
from benchmarktool.runscript.parser import Parser
import sys


def parse_args():
    parser = argparse.ArgumentParser(description='%s files')
    parser.add_argument('infile', nargs=1, type=str)
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = parse_args()
    filename = args.infile[0]

    # TODO: performance:: replace xml serialization by python data structure?
    p = Parser()
    run = p.parse(filename)
    run.evalResults(sys.stdout)
