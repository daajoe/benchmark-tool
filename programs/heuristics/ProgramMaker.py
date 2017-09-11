#!/bin/python

import array
import re
import sys
from DflatPredicateHandler import *

class ProgramMaker:

	def startsIn(self, k):
		for l in self._preds:
			if k.startswith(l):
				return True
		return False

	def __init__(self):
		self._makeHeuristicProgram = True
		self._reorgTDNumberspace = True
		self._startReorg = 1
		#self._forbidParallelism = True
		self._useDynASP = False
		
		self._rootMode = False
		
		self._outputTDonly = False

		self._explicitStructure = True
		self._createChildInfo = False

		if self._outputTDonly:
			self._createChildInfo = True
			
		if self._createChildInfo:
			self._explicitStructure = False

	def make(self, root, code, preds, dyn):
		self._useDynASP = dyn
		self._code = code
		self._preds = preds
		self._superroot = root
		self._rootI = 0
		self._outp = array.array('B', "")
		self._roots = {}
		self._amounts = {}
		self._bag = {}
		if self._makeHeuristicProgram:
			self.heuristic(root)
			for k in self._roots:
				lst = self._bag.get(self._roots[k][1])
				if lst is None:
					lst = []
					self._bag[self._roots[k][1]] = lst
				lst.append(k)

			if self._reorgTDNumberspace:
				keys = self._bag.keys()
				keys.sort()
				i = self._startReorg
				for v in keys:
					for k in self._bag[v]:
						self._roots[k] = (self._roots[k][0], i)
					i += 1

			#print self._bag
			
			for k in self._roots:
				if self._useDynASP:
					if not self._reorgTDNumberspace or self.startsIn(k):
						if self._rootMode:
							self._outp += array.array('B', "_heuristic({},init,{}).\n".format(k, self._rootI - int(self._roots[k][1])))
						else:
							if self._roots[k][1] > 0:
								self._outp += array.array('B', "_heuristic({},init,{}).\n".format(k, self._roots[k][1]))

				else:
					if self._rootMode:
						self._outp += array.array('B', "_heuristic(" + self._preds[0] + "({}),init,{}).\n".format(k, self._rootI - int(self._roots[k][1])))
					else:
						if self._roots[k][1] > 0:
							self._outp += array.array('B', "_heuristic(" + self._preds[0] + "({}),init,{}).\n".format(k, int(self._roots[k][1] * 1.00)))
			
		else:
			if not self._outputTDonly:
				if not self._explicitStructure:
					self._outp += array.array('B', "#show item" + "/2. ")
					for p in self._preds:
						self._outp += array.array('B', "#show " + p + "/2. ")
					self._outp += array.array('B', "final ({}). ".format(root.nr()))
				else:
					self._outp += array.array('B', "final{}. ".format(root.nr()))
			self.facts(root)
			self._outp += array.array('B', "\n")
			if not self._outputTDonly:
				self.bottomUp(root)
		return self._outp.tostring() 

	def heuristic(self,root):
		i = root.nr()
		curr = (root,int(i))
		self._rootI = max(self._rootI, int(i))
		for c in root.next():
			self.heuristic(c)
		
		for k in root.keys():
			if not self._useDynASP or self.startsIn(k):
				p = self._amounts.get(k)
				v = 1
				if not p is None:
					v += int(p)
				self._amounts[k] = v

		for k in root.intro():
			if not self._useDynASP or self.startsIn(k):
				#print k,int(i)
				p = self._roots.get(k)
				choose = None
				if p is None:
					choose = lambda x, y: y
				else:
					if self._rootMode:
						choose = lambda x, y: x if x[1] <= y[1] else y
					else:
						choose = lambda x, y: y
						#choose = lambda x, y: x if x[1] >= y[1] else y
						#choose = lambda x, y: x if x[1] <= y[1] else y
				v = choose(p,curr)
				self._roots[k] = v

	def __replace(self, b, pos, end, nmb):
		for p in nmb: #range(match.end(4), match.end(4) + len(nmb)):
			if pos < end:
				b[pos] = p 
			else:
				b.insert(pos,p)
			pos += 1
		while pos < end - 1:
			b[pos] = ord(' ')
			pos += 1

		if self._explicitStructure:
			if b[pos] == ord(','):
				b[pos] = ord('(')
			else:
				b[pos] = ord(' ')

	def __replaceID(self, code, i, replStr):
		bf    = (lambda : "(" if not self._explicitStructure else "")
		#cf    = (lambda : "," if self._explicitStructure else "")
		nmb = array.array('B', bf() + str(i))
		b = array.array('B', code)
		assert len(b) == len(code)

		for match in re.finditer("([a-zA-Z_\-0-9]*)(\s*\(\s*)(@" + replStr + ")(\s*[,)])", code):
			self.__replace(b, match.end(2) - 1, match.end(4), nmb)
		
		return b

	def facts(self,root):
		i = root.nr()
		for c in root.next():
			self.facts(c)
			if self._createChildInfo:
				self._outp += array.array('B', "child (" + str(i) + "," + str(c.nr()) + "). ")
		
		for k in root.intro():
			if self._explicitStructure:
				self._outp += array.array('B', "intro" + str(i) + "(" + str(k) + "). ")
			else:
				self._outp += array.array('B', "intro (" + str(i) + "," + str(k) + "). ")

		for k in root.keys():
			if self._explicitStructure:
				self._outp += array.array('B', "bag" + str(i) + "(" + str(k) + "). ")
			else:
				self._outp += array.array('B', "bag (" + str(i) + "," + str(k) + "). ")

		if not self._outputTDonly and len(root.next()) == 0:
			if self._explicitStructure:
				self._outp += array.array('B', "initial{}. ".format(i))
			else:
				self._outp += array.array('B', "initial({}). ".format(i))

		if not self._outputTDonly and self._explicitStructure:
			self._outp += array.array('B', "#show item" + str(i) + "/1. ")
			for p in self._preds:
				self._outp += array.array('B', "#show " + p + str(i) + "/1. ")

	def __out(self, string, filt):
		self._outp += array.array('B', re.sub(".*(" + filt + ").*\.\s*(\[.*\])?", "", string))

	def __filter(self, code, filt):
		s = ""
		for m in re.finditer(".*(" + filt + ").*\.\s*(\[.*\])?", code):
			s += m.group(0)
		return s


	def bottomUp(self, root):
		lf    = (lambda : "final|" if root is self._superroot else "")
		invlf = (lambda : "final|" if root is not self._superroot else "")

		i = root.nr()
		for c in root.next():
			self.bottomUp(c)

		#replace and output @ID only
		b = self.__replaceID(self._code, i, "ID")
		self.__out(b.tostring(), "initial|final|@CID[01]")

		if len(root.next()) == 0:
			f = self.__filter(b.tostring(), lf() + "initial")
			self.__out(f, invlf() + "@CID[01]")			#no child nodes
		else:
			s = self.__filter(b.tostring(), lf() + "@CID[01]")
			for c in root.next():
				j = c.nr()
				b = self.__replaceID(s, j, "CID0")
				self.__out(b.tostring(), "@CID1")	#only one children first

				if len(root.next()) > 1:
					ss = self.__filter(b.tostring(), "@CID1")
					for c2 in root.next():
						k = c2.nr()
						if k != j:
							self._outp += self.__replaceID(ss, k, "CID1")

		self._outp += array.array('B', "\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n")	

