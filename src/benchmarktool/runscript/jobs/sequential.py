import os
from .base import Job, ScriptGen
import benchmarktool.tools as tools

class SeqScriptGen(ScriptGen):
    """
    A class that generates and evaluates start scripts for sequential runs.
    """

    def __init__(self, seqJob):
        """
        Initializes the script generator.
        
        Keyword arguments:
        seqJob - A reference to the associated sequential job.
        """
        ScriptGen.__init__(self, seqJob)

    def genStartScript(self, path):
        """
        Generates a start script that can be used to start all scripts 
        generated using addToScript().
        
        Keyword arguments:
        path - The target location for the script
        """
        tools.mkdir_p(path)
        startfile = open(os.path.join(path, "start.py"), 'w')
        queue = ""
        comma = False
        for (_, instpath, instname) in self.startfiles:
            relpath = os.path.relpath(instpath, path)
            if comma:
                queue += ","
            else:
                comma = True
            queue += repr(os.path.join(relpath, instname))
        startfile.write("""\
#!/usr/bin/python -u

import optparse
import threading
import subprocess
import os
import sys
import signal
import time

queue = [{0}]

class Main:
    def __init__(self):
        self.running  = set()
        self.cores    = set()
        self.started  = 0
        self.total    = None
        self.finished = threading.Condition()
        self.coreLock = threading.Lock()
        c = 0
        while len(self.cores) < {1}:
            self.cores.add(c)
            c += 1
    
    def finish(self, thread):
        self.finished.acquire()
        self.running.remove(thread)
        with self.coreLock:
            self.cores.add(thread.core)
        self.finished.notify()
        self.finished.release()
   
    def start(self, cmd):
        core     = 0
        with self.coreLock:
            core = self.cores.pop()
        thread = Run(cmd, self, core)
        self.started += 1
        self.running.add(thread)
        print("({{0}}/{{1}}/{{2}}/{{4}}) {{3}}".format(len(self.running), self.started, self.total, cmd, core))
        thread.start()
    
    def run(self, queue):
        signal.signal(signal.SIGTERM, self.exit)
        signal.signal(signal.SIGINT, self.exit)
        signal.signal(signal.SIGHUP, signal.SIG_IGN)
        self.finished.acquire()
        self.total = len(queue)
        for cmd in queue:
            while len(self.running) >= {1}:
                self.finished.wait()
            self.start(cmd)
        while len(self.running) != 0:
            self.finished.wait()
        self.finished.release()

    def exit(self, *args):
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        signal.signal(signal.SIGTERM, signal.SIG_IGN)
        print "WARNING: it is not guaranteed that all processes will be terminated!"
        print "sending sigterm ..."
        os.killpg(os.getpgid(0), signal.SIGTERM)
        print "waiting 10s..."
        time.sleep(10)
        print "sending sigkill ..."
        os.killpg(os.getpgid(0), signal.SIGKILL)

class Run(threading.Thread):
    def __init__(self, cmd, main, core):
        threading.Thread.__init__(self)
        self.cmd  = cmd
        self.main = main
        self.core = core
        self.proc = None
    
    def run(self):
        path, script = os.path.split(self.cmd)
        self.proc = subprocess.Popen(["bash", script, str(self.core)], cwd=path)
        self.proc.wait()
        self.main.finish(self)

def gui():
    import Tkinter
    class App:
        def __init__(self):
            root    = Tkinter.Tk()
            frame   = Tkinter.Frame(root)
            scrollx = Tkinter.Scrollbar(frame, orient=Tkinter.HORIZONTAL)
            scrolly = Tkinter.Scrollbar(frame)
            list    = Tkinter.Listbox(frame, selectmode=Tkinter.MULTIPLE)
            
            for script in queue:
                list.insert(Tkinter.END, script)
            
            scrolly.config(command=list.yview)
            scrollx.config(command=list.xview)
            list.config(yscrollcommand=scrolly.set)
            list.config(xscrollcommand=scrollx.set)
                
            scrolly.pack(side=Tkinter.RIGHT, fill=Tkinter.Y)
            scrollx.pack(side=Tkinter.BOTTOM, fill=Tkinter.X)
            list.pack(fill=Tkinter.BOTH, expand=1)
            
            button = Tkinter.Button(root, text='Run', command=self.pressed)
            
            frame.pack(fill=Tkinter.BOTH, expand=1)
            button.pack(side=Tkinter.BOTTOM, fill=Tkinter.X)

            self.root  = root
            self.list  = list
            self.run   = False
            self.queue = [] 
        
        def pressed(self):
            sel = self.list.curselection()
            for index in sel:
                global queue
                self.queue.append(queue[int(index)])
            self.root.destroy()

        def start(self):
            self.root.mainloop()
            return self.queue

    global queue
    queue.sort()
    queue = App().start()

if __name__ == '__main__':
    usage  = "usage: %prog [options] <runscript>"
    parser = optparse.OptionParser(usage=usage)
    parser.add_option("-g", "--gui", action="store_true", dest="gui", default=False, help="start gui to selectively start benchmarks") 

    opts, args = parser.parse_args(sys.argv[1:])
    if len(args) > 0: parser.error("no arguments expected")
    
    os.chdir(os.path.dirname(sys.argv[0]))
    if opts.gui: gui()

    m = Main()
    m.run(queue)
""".format(queue, self.job.parallel))
        startfile.close()
        tools.setExecutable(os.path.join(path, "start.py"))


class SeqJob(Job):
    """
    Describes a sequential job.
    """

    def __init__(self, name, memout, timeout, runs, parallel, **kwargs):
        """
        Initializes a sequential job description.  
        
        Keyword arguments:
        name     - A unique name for a job
        timeout  - A timeout in seconds for individual benchmark runs
        runs     - The number of runs per benchmark
        parallel - The number of runs that can be started in parallel
        attr     - A dictionary of arbitrary attributes
        """
        Job.__init__(self, name, memout, timeout, runs, **kwargs)
        self.parallel = parallel

    def scriptGen(self):
        """
        Returns a class that can generate start scripts and evaluate benchmark results.
        (see SeqScriptGen) 
        """
        return SeqScriptGen(self)

    def toXml(self, out, indent):
        """
        Dump a (pretty-printed) XML-representation of the sequential job.
        
        Keyword arguments:
        out     - Output stream to write to
        indent  - Amount of indentation
        """
        extra = ' parallel="{0.parallel}"'.format(self)
        Job._toXml(self, out, indent, "seqjob", extra)

