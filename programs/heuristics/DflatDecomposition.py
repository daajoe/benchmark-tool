#!/bin/python

class DflatIdentifiable(object):

	def __init__(self, keys):
		self._keys = keys

	def add(self, val):
		self._keys.append(val)

	def __repr__(self):
		return self.__str__()

	def __str__(self):
		return str(self._keys)

	def id(self):
		return DflatIdentifiable.idstr(self._keys)

	def keys(self):
		return self._keys

	@staticmethod	
	def idstr(val):
		val.sort()
		return str(val)

	def content(self):
		self.id()
		return DflatIdentifiable.contentStr(self._keys, lambda _ : False) #DflatIdentifiable.SHOW_ALL)

	@staticmethod	
	def contentItemStr(val):
		if type(val) is list:
			res = ""
			i = 0
			for j in val:
				if i == 0:
					res += j + "("
				else: #if not exc(j):
					if i > 1:
						res += ", "
					res += DflatIdentifiable.contentItemStr(j)
				i += 1
			res += ")"
			return res
		else:
			return val

	@staticmethod	
	def contentStr(val, exc):
		res = "["
		for j in val:
			if not exc(j):
				if len(res) > 1:
					res += ", "
				res += DflatIdentifiable.contentItemStr(j)
		res += "]"
		return res

class DflatRowContainer(DflatIdentifiable):
	def __init__(self, keys):
		super(DflatRowContainer, self).__init__(keys)
		self._next = []
		self._prev = []
		self._node = None

	def setNode(self, n):
		self._node = n

	def node(self):
		return self._node

	def prev(self):
		return self._prev

	def next(self):
		return self._next

	def setPrev(self, child):
		self._prev = child

	def setNext(self, child):
		self._next = child

	def addPrev(self, child):
		self._prev.append(child)

	def addNext(self, child):
		self._next.append(child)

	def __str__(self):
		#return super(DflatDecomposition, self).__str__(self._keys) + str(self._next)
		return super(DflatRowContainer, self).__str__() + "@" #+ str(self.prev()) # + "->" + str(self._next)

class DflatDecomposition(DflatRowContainer):

	def __init__(self, keys, fullintro = True):
		super(DflatDecomposition, self).__init__(keys)
		self._nr = 0
		self._intro = []
		self._posIntro = fullintro
		self._introManaged = False

	def setNr(self, nr):	
		self._nr = nr

	def nr(self):
		return self._nr

	def addIntro(self, intro):
		self._intro.append(intro)

	def setIntroPositive(self, introP):
		self._posIntro = introP

	def setIntro(self, intro):
		self._intro = intro

	def intro(self):
		if not self._posIntro and not self._introManaged:
			self._intro = set(self._keys) - set(self._intro)
			self._introManaged = True
		return self._intro


	def content(self):
		return "n" + str(self._nr) + ": " + super(DflatDecomposition, self).content()

