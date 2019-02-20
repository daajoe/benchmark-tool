#!/usr/bin/python

import gringo, sys, json, signal, threading, argparse, StringIO

class Solver:
    def __init__(self, args):
        signal.signal(signal.SIGINT, self.__interrupt)
        signal.signal(signal.SIGTERM, self.__interrupt)
        self.__step = 0
        self.__condition = threading.Condition()
        self.__args = args
        self.__solving = False
        self.__interrupted = False
        self.__stats_interrupted = False

    def __interrupt(self, signum, frame):
        sys.stderr.write("INTERRUPTED\n")
        self.__interrupted = True
        if self.__solving:
            self.cancel()

    def on_finish(self, ret, interrupted):
        self.__condition.acquire()
        self.__solving = False
        self.__stats_interrupted = interrupted
        self.__condition.notify()
        self.__condition.release()

    def add_const(self, prg):
        if len(self.__args.const) > 0:
            const = ""
            for c in self.__args.const:
                const += "#const " + c + "."
            prg.add("base", [], const)

    def start(self, step):
        pass

    def get(self):
        pass

    def cancel(self):
        pass

    def stats(self):
        return {}

    def __continue(self, ret):
        if self.__interrupted:
            return False
        if self.__args.imax is not None and self.__step >= self.__args.imax:
            return False
        if self.__args.imin is not None and self.__step < self.__args.imin:
            return True
        return ret != gringo.SolveResult.SAT

    def solve(self):
        ret = gringo.SolveResult.UNKNOWN
        sys.stdout.write("[\n")
        sys.stdout.flush()
        while self.__continue(ret):
            self.start(self.__step)
            self.__solving = True
            if self.__interrupted: self.cancel()
            self.__condition.acquire()
            while self.__solving:
                # NOTE: we need a timeout to catch signals
                self.__condition.wait(float("inf"))
            self.__condition.release()
            self.__solving = False
            ret = self.get()
            self.__step += 1
            stats = self.stats()
            stats["interrupted"] = int(self.__stats_interrupted)
            json.dump(stats, sys.stdout)
            sys.stdout.write(",\n")
            sys.stdout.flush()
        sys.stdout.write("]\n")
        sys.stdout.flush()
        sys.stderr.write("FINISHED\n")


class MultiShot(Solver):
    def __init__(self, script_args, control_args):
        Solver.__init__(self, script_args)
        self.__prg = gringo.Control(control_args)
        self.add_const(self.__prg)
        for f in script_args.file:
           self.__prg.load(f)

        self.__prg.add("check", ["t"], "#external query(t).")
        self.__future = None

    def start(self, step):
        parts = []
        parts.append(("check", [step]))
        if step > 0:
            self.__prg.release_external(gringo.Fun("query", [step-1]))
            parts.append(("step", [step]))
            self.__prg.cleanup_domains()
        else:
            parts.append(("base", []))
        self.__prg.ground(parts)
        self.__prg.assign_external(gringo.Fun("query", [step]), True)
        self.__future = self.__prg.solve_async(on_finish=self.on_finish)

    def get(self):
        return self.__future.get()

    def cancel(self):
        self.__future.cancel()

    def stats(self):
        return self.__prg.stats

class SingleShot(Solver):
    def __init__(self, script_args, control_args):
        Solver.__init__(self, script_args)
        self.__script_args = script_args
        self.__control_args = control_args
        self.__prg = None
        self.__future = None
        self.__step = 0

    def start(self, step):
        self.__prg = gringo.Control(self.__control_args)
        self.add_const(self.__prg)
        for f in self.__script_args.file:
            self.__prg.load(f)
        self.__prg.add("base", [], "query({0}).".format(step))
        self.__step = step
        for i in range(0, step + 1):
            parts = []
            parts.append(("check", [i]))
            if i > 0:
                parts.append(("step", [i]))
                self.__prg.cleanup_domains()
            else:
                parts.append(("base", []))
            self.__prg.ground(parts)
        self.__future = self.__prg.solve_async(on_finish=self.on_finish)

    def get(self):
        return self.__future.get()

    def cancel(self):
        self.__future.cancel()

    def stats(self):
        stats = self.__prg.stats
        stats["step"] = self.__step
        return stats

# NOTES:
# - which statistics level?
# - should additional time measuring be done with python means?
# - should the interrupted flag be added to the json output?

if "--" in sys.argv:
    i = sys.argv.index("--")
    args_script = sys.argv[1:i]
    args_clingo = sys.argv[i+1:]
else:
    args_script = sys.argv[1:]
    args_clingo = []

file_parser = argparse.ArgumentParser(add_help=False, prog="problem file", description="""Problem files contain one option or argument per line.""")
file_parser.add_argument('file', nargs='+', default=[], help='gringo source file')
file_parser.add_argument('--imin', help="minimum number of incremental steps", type=int)
file_parser.add_argument('--imax', help="maximum number of incremental steps", type=int)
file_parser.add_argument('--const', help="set a constant", action="append", default=[])

file_help = StringIO.StringIO()
file_parser.print_help(file_help)
file_help = file_help.getvalue()
file_help = "problem file: " + file_help[20:]

parser = argparse.ArgumentParser(description="""
Script to solve incremental problems. Solver options can be appended to the
commandline following a double hyphen.
""", epilog=file_help, formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument("mode", help="select single- or multi-shot mode", choices=["multi", "single"])
parser.add_argument('file', help="the problem to run", type=file)

args = parser.parse_args(args_script)
file_args = file_parser.parse_args([line.rstrip() for line in args.file])

if file_args.imin is not None and file_args.imax is not None and file_args.imin > file_args.imax:
    file_parser.error("imin must be smaller or equal to imax")

solver = MultiShot(file_args, args_clingo) if args.mode == "multi" else SingleShot(file_args, args_clingo)
solver.solve()

