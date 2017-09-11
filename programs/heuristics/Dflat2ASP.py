#!/usr/bin/python

from pyparsing import *
import signal
import os
import io
import re
import sys
from DflatPredicateHandler import *
from ProgramMaker import *
#from DflatDecomposition import *

#def safeClose(f):
#	try:
#		f.close()
#	except IOError:
#		pass

class Dflat2ASP:
	def __init__(self):
		self._pr = DflatPredicateReader()
		self._ph = PredicateHandler(self._pr, self._pr)
		self._pm = ProgramMaker()

	def interrupt(self):
		return self._ph.interrupt()

	def predReader(self):
		return self._pr

	def makeProgram(self, root, code, preds, dyn = False):
		return self._pm.make(root, code, preds, dyn)
	
	def parse(self, inptf, outpf):
		try:
			self._ph.read(inptf)
			self._ph.write(outpf)
		except IOError as e:
			print e
		safeClose(inptf)
		#safeClose(outpf)
		
	

def signal_handler(signal, frame):
	if d.interrupt():
		sys.exit(0)

#debugger
d = None



if __name__ == "__main__":
	sys.setrecursionlimit(100000)
	d = Dflat2ASP()
	fi = sys.stdin
	#fo = sys.stdout
	#if len(sys.argv) > 1:
		#fo = file(sys.argv[1], "w")
		#if len(sys.argv) > 2:
	#		fi = file(sys.argv[2], "r")
	#		if len(sys.argv) > 1:
	#			print "usage: python " + __name__ + " <inputfile?>" + "<useDynasp?>"
	#			sys.exit(1)
	signal.signal(signal.SIGINT, signal_handler)
	
	d.parse(fi, sys.stdout)
	de = d.predReader().getRoot()
	#code = SatCode()
	print d.makeProgram(de, "", sys.argv[1].split(",")) #["vertex", "selectedEdge"])
	(

#"""
#-intro(@ID,A) :- bag(@ID,A), bag(@CID0,A).
#intro(@ID,A) :- not -intro(@ID,A), bag(@ID,A).
#
#:- item(@CID0,in(X)), not item(@CID1,in(X)).
#item(@ID,in(X)) :- item(@CID0,in(X)), bag(@ID,X).
#item(@ID,dom(X)) :- item(@CID0,dom(X)), bag(@ID,X).
#
#{ item(@ID,in(X)) : intro(@ID,X) }.
#:- not bag(@ID,X), bag(@CID0,X), not item(@CID0,in(X)), not item(@CID0,dom(X)).
#item(@ID,dom(X)) :- item(@ID,in(Y)), att(Y,X), bag(@ID,X).
#:- att(X,Y), item(@ID,in(X)), item(@ID,in(Y)).
#
#sol(in(X)) :- item(@ID,in(X)).
##minimize { 1,X : sol(in(X)) }.
#%:~ sol(in(X)). [1,X]
#"""
#)

##%cost(@ID,C) :- initial(@ID), C = #count { X : item(@ID,in(X)) }.
##%cost(@ID,CC+IC) :- cost(@CID0,CC), IC = #count { X : item(@ID,in(X)), intro(@ID,X) }.
##
##%:~ cost(@ID,C), final(@ID). [C]

#SATfastAlt
#(
#"""
#:- atom(A), item(@CID0,A), bag(@CID1,A), not item(@CID1,A).
#:- clause(C), not bag(@ID,C), bag(@CID0,C), not item(@CID0,C).
#
#item(@ID,X) :- item(@CID0,X), bag(@ID,X).
#{ item(@ID,A) : atom(A), intro(@ID,A) }.
#
#item(@ID,C) :- bag(@ID,C), bag(@ID,A), pos(C,A), item(@ID,A).
#item(@ID,C) :- bag(@ID,C), bag(@ID,A), neg(C,A), not item(@ID,A).
#""", []
#)


#PrimSATfastAlt
#(
#"""
#:- atom(A), item(@CID0,A), bag(@CID1,A), not item(@CID1,A).
#
#item(@ID,X) :- item(@CID0,X), bag(@ID,X).
#{ item(@ID,A) : intro(@ID,A) }.
#
#-curr(@ID,C) :- occursIn(A,C), not bag(@ID,A).
#curr(@ID,C) :- clause(C), not -curr(@ID,C).
#sat(@ID,C) :- pos(C,A), item(@ID,A).
#sat(@ID,C) :- neg(C,A), not item(@ID,A).
#:- curr(@ID,C), not sat(@ID,C).
#""", []
#)
#(
#dom set ultrafast
"""
:- in(@CID0,X), not in(@CID1,X), bag(@CID1,X).
in(@ID,X) :- in(@CID0,X), bag(@ID,X).
dom(@ID,X) :- dom(@CID0,X), bag(@ID,X).

{ in(@ID,X) : intro(@ID,X) }.
:- not bag(@ID,X), bag(@CID0,X), not in(@CID0,X), not dom(@CID0,X).
dom(@ID,X) :- in(@ID,Y), att(Y,X), bag(@ID,X).
:- att(X,Y), in(@ID,X), in(@ID,Y).

#minimize { 1,X : in(@ID,X) }.

""", 
["in", "dom"]
)

##minimize { 1,X : in(@ID,X), final(@ID) }.
#%cost(@ID,C) :- initial(@ID), C = #count { X : in(@ID,X) }.
#%cost(@ID,CC+IC) :- cost(@CID0,CC), IC = #count { X : in(@ID,X), intro(@ID,X) }.
#
#%:~ cost(@ID,C), final(@ID). [C]
#%:~ cost(@ID,C). [C, (@ID)]
#
##minimize { 1,X : in(@ID,X), final(@ID) }.
#
#%:~ D = #count { X : in(@ID,X) }. [D, (@ID)]


#SATfastAlt
(
"""
:- atom(A), item(@CID0,A), bag(@CID1,A), not item(@CID1,A).
:- clause(C), not bag(@ID,C), bag(@CID0,C), not item(@CID0,C).

item(@ID,X) :- item(@CID0,X), bag(@ID,X).
{ item(@ID,A) : atom(A), intro(@ID,A) }.

item(@ID,C) :- bag(@ID,C), bag(@ID,A), pos(C,A), item(@ID,A).
item(@ID,C) :- bag(@ID,C), bag(@ID,A), neg(C,A), not item(@ID,A).
""", []
)
#PrimSATfastAlt
(
"""
:- atom(A), item(@CID0,A), bag(@CID1,A), not item(@CID1,A).

item(@ID,X) :- item(@CID0,X), bag(@ID,X).
{ item(@ID,A) : intro(@ID,A) }.

-curr(@ID,C) :- occursIn(A,C), not bag(@ID,A).
curr(@ID,C) :- clause(C), not -curr(@ID,C).
sat(@ID,C) :- pos(C,A), item(@ID,A).
sat(@ID,C) :- neg(C,A), not item(@ID,A).
:- curr(@ID,C), not sat(@ID)
""", []
)
(
#dom set gringo child stuff
"""
:- child(@ID,C), child(@ID,C2), in(C,X), not in(C2,X), bag(C2,X).
in(@ID,X) :- in(@CID0,X), bag(@ID,X).
dom(@ID,X) :- dom(@CID0,X), bag(@ID,X).

{ in(@ID,X) : intro(@ID,X) }.
:- not bag(@ID,X), bag(C,X), child(@ID,C), not in(C,X), not dom(C,X).
dom(@ID,X) :- in(@ID,Y), att(Y,X), bag(@ID,X).
:- att(X,Y), in(@ID,X), in(@ID,Y).
""", 
["in", "dom"]
)
#yaind dom set
("""
-intro(@ID,A) :- bag(@ID,A), bag(@CID0,A).
intro(@ID,A) :- not -intro(@ID,A), bag(@ID,A).

:- item(@CID0,in(X)), not item(@CID1,in(X)), bag(@CID1,X).
item(@ID,in(X)) :- item(@CID0,in(X)), bag(@ID,X).
item(@ID,dom(X)) :- item(@CID0,dom(X)), bag(@ID,X).

{ item(@ID,in(X)) : intro(@ID,X) }.
:- not bag(@ID,X), bag(@CID0,X), not item(@CID0,in(X)), not item(@CID0,dom(X)).
item(@ID,dom(X)) :- item(@ID,in(Y)), att(Y,X), bag(@ID,X).
:- att(X,Y), item(@ID,in(X)), item(@ID,in(Y)).
"""
)

#min ind dom set
("""
-intro(@ID,A) :- bag(@ID,A), bag(@CID0,A).
intro(@ID,A) :- not -intro(@ID,A), bag(@ID,A).

:- item(@CID0,in(X)), not item(@CID1,in(X)).
item(@ID,in(X)) :- item(@CID0,in(X)), bag(@ID,X).
item(@ID,dom(X)) :- item(@CID0,dom(X)), bag(@ID,X).

{ item(@ID,in(X)) : intro(@ID,X) }.
:- not bag(@ID,X), bag(@CID0,X), not item(@CID0,in(X)), not item(@CID0,dom(X)).
item(@ID,dom(X)) :- item(@ID,in(Y)), att(Y,X), bag(@ID,X).
:- att(X,Y), item(@ID,in(X)), item(@ID,in(Y)).

sol(in(X)) :- item(@ID,in(X)).
#minimize { 1,X : sol(in(X)) }.
%:~ sol(in(X)). [1,X]
"""
)

##%cost(@ID,C) :- initial(@ID), C = #count { X : item(@ID,in(X)) }.
##%cost(@ID,CC+IC) :- cost(@CID0,CC), IC = #count { X : item(@ID,in(X)), intro(@ID,X) }.
##
##%:~ cost(@ID,C), final(@ID). [C]


#SATfast
(
"""
false(@CID0,X) :- bag(@CID0,X), not item(@CID0,X).
:- atom(A), item(@CID0,A), false(@CID1,A).
:- clause(C), not bag(@ID,C), false(@CID0,C).

item(@ID,X) :- item(@CID0,X), bag(@ID,X).
{ item(@ID,A) : atom(A), intro(@ID,A) }.

item(@ID,C) :- bag(@ID,C), bag(@ID,A), pos(C,A), item(@ID,A).
item(@ID,C) :- bag(@ID,C), bag(@ID,A), neg(C,A), not item(@ID,A).
"""
)


#MinSAT
(
"""
-intro(@ID,A) :- bag(@ID,A), bag(@CID0,A).
intro(@ID,A) :- not -intro(@ID,A), bag(@ID,A).

false(@CID0,X) :- bag(@CID0,X), not item(@CID0,X).
:- atom(A), item(@CID0,A), false(@CID1,A).
:- clause(C), not bag(@ID,C), false(@CID0,C).

item(@ID,X) :- item(@CID0,X), bag(@ID,X).
{ item(@ID,A) : atom(A), intro(@ID,A) }.

item(@ID,C) :- bag(@ID,C), bag(@ID,A), pos(C,A), item(@ID,A).
item(@ID,C) :- bag(@ID,C), bag(@ID,A), neg(C,A), not item(@ID,A).

:~ item(@ID,A), atom(A). [1,A]
"""
)


