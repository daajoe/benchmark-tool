#!/bin/python
#hecher markus 7/2013
#helping stuff for grounded extension

from PredicateHandler import *
from DflatDecomposition import *

class DflatPredicateReader(PredicateReader):

	BAGINPUT = 0

	INTRO = False	#remove for -introduced

	def __init__(self):
		BI = DflatPredicateReader.BAGINPUT
		
		super(DflatPredicateReader, self).__init__({
			"currentNode" : BI, "childNode" : BI, "final" : BI, "current" : BI, "introduced" : BI,  "-introduced" : BI } )
			#, "childItem" : CT, "childCost" : CT, "sub" : CT, 
			#"childAnd" : CT, "childOr" : CT, "childAccept" : CT, "childReject" : CT, "childAuxItem" : CT,  
			#"itemTreeNodeHasAddress" : MD, "itemTreeNodeExtends" : MD })
		
		self._decompByID = {}	#whole decomposition
		self._decelem = None	#current node/element of the decomp

		#self._decroot = None	
	
		#self._node = None
		#self._bag = []		#bag contents
		#self._notintro = []		#bag contents
		#self._intro = []		#bag contents
		#self._childnodes = []	#child nodes
		self._root = False
		#self._superroot = None

	@staticmethod
	def unList(lst):
		if type(lst) is not list:
			return str(lst)
		indx = 0
		res = ""
		for i in lst:
			if indx == 1:
				res += "("
			elif indx > 1:
				res += ","
		#	if type(i) is list:
			res += DflatPredicateReader.unList(i)
		#	else:
		#		res += i
			indx += 1
		if indx > 1:
			res += ")"
		return res
		#print res

	def onMatch(self, inpt):
		#print inpt
		for i in inpt:
			if type(i) is list:
				typ = self._preds.get(i[0])
				if typ == DflatPredicateReader.BAGINPUT:
					#if not self._decelem is None: #clear
					#	self._decelem = None
					if i[0] == "currentNode":

						#if not self._node is None:
						#	self._makeDecompNode()
						#	self._decelem = None
						#print "CURRENT: ", i[1]
						#self._node = i[1]
						self._decelem = self.getElemById(i[1])
						if self._root:
							self._superroot = self._decelem
							self._root = False
					elif i[0] == "current":
						#self._bag.append(DflatPredicateReader.unList(i[1]))
						self._decelem.keys().append(DflatPredicateReader.unList(i[1]))
					elif i[0] == "introduced":
						#print "notintro ", i[1]
						DflatPredicateReader.INTRO = True
						self._decelem.setIntroPositive(DflatPredicateReader.INTRO)
						assert(DflatPredicateReader.INTRO)
						self._decelem.addIntro(DflatPredicateReader.unList(i[1]))
						#self._intro.append(DflatPredicateReader.unList(i[1]))
					elif i[0] == "-introduced":
						DflatPredicateReader.INTRO = False
						self._decelem.setIntroPositive(DflatPredicateReader.INTRO)
						assert(not DflatPredicateReader.INTRO)
						#print "notintro ", i[1]
						self._decelem.addIntro(DflatPredicateReader.unList(i[1]))
					#	self._notintro.append(DflatPredicateReader.unList(i[1]))
					elif i[0] == "childNode":
						elem = self.getElemById(i[1])
						#elem = self._decompByID.get(i[1])
						#print i[1]
						#assert (not elem is None)
						#if elem is None:
						#	elem = DflatDecomposition([])
						#	self._decompByID[i[1]] = elem
						self._decelem.addNext(elem)
						elem.addPrev(self._decelem)

						#self._childnodes.append(elem)
				#elif typ >= DflatPredicateReader.CHILDTAB:
				#	self._makeDecompNode()
			elif type(i) is str:
				typ = self._preds.get(i)
				if typ == DflatPredicateReader.BAGINPUT and i == "final":
					#	self._makeDecompNode()
					#	self._decroot = self._decelem
					#	print "ROOT!", self._decroot
					#if self._decelem is not None:
					#	self._superroot = self._decelem
					#else:
					if self._decelem is not None:
						self._superroot = self._decelem
					else:
						self._root = True

	def getElemById(self, eid):
		decelem = self._decompByID.get(eid)
		if decelem is None:
			decelem = DflatDecomposition([], DflatPredicateReader.INTRO)
			self._decompByID[eid] = decelem
			decelem.setNr(eid)
		return decelem
		#decelem.keys().append(content)

	#def _makeDecompNode(self):
		#if self._decelem is None:
		#assert(not self._node is None)
		#decelem = self.getElemById(self._node)
		#decelem.keys().append(self._bag)
		#print self._node
		#decelem = self._decompByID.get(self._node)
		#if decelem is None:
		#	decelem = DflatDecomposition(self._bag)
		#else:
		#decelem.keys().append(self._bag)

		#if self._root:
		#	self._superroot = decelem
			#print "ROOT", self._decroot
		#	self._root = False

		#assert(self._node != decelem.nr())		#already done

		#self._decelem.setIntro(set(self._bag) - set(self._notintro))
		#decelem.setIntro(self._intro)
		#decelem.setNr(self._node)
		#self._decompByID[self._node] = decelem
		#decelem.setNext(self._childnodes)
		#for k in self._childnodes:
		#	k.addPrev(decelem)
			#if not self._decompByID.get(k.nr()) is None:
			#	del self._decompByID[k.nr()]
			#clear
		#self._childnodes = []
		#self._bag = []
		#self._notintro = []
		#self._intro = []
		#self._node = None
		#if self._superroot is None:
		#	self._superroot = self._decelem


	def onFinish(self):
		pass
		#self._makeDecompNode()
		#assert(len(self._decompByID) == 1)
		#for k in self._decompByID:
		#	i = self._decompByID[k]
		#	self._childnodes.append(i) #for non-root tree case
	
		#if len(self._decompByID) > 1: #non-root tree
		#	self._node = -1
		#	self._bag.append("...")
		#	self._decelem = None
		#	self._makeDecompNode() #make inofficial super-root
		
	def getRoot(self):
		#return self._decroot #elem
		return self._superroot



