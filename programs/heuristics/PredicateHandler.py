#!/bin/python

from pyparsing import *
import re

def safeClose(f):
       try:
               f.close()
       except IOError:
               pass



class PredicateHandler:
	def __init__(self, src, dest):
		self._dest = dest
		self._src = src
		#self._re = re.compile("(([^(:,. ]+)(\((([a-z0-9][^,. ]*)(,([a-z0-9][^,. ]*))*)\))?[. ])")
		self._re = re.compile("(([^(:,. ]+)(\((([^,. ]+)(,([^,. ]+))*)\))?([^. ]*)[. ])")
		#self._re = re.compile("(([A-Za-z_]+)(\((([a-z0-9][A-Za-z0-9_]+)(,([a-z0-9][A-za-z0-9_]+))*)\))?[. ])")
		#print self._re.match("childItem(n1_13,map(e,out)).")
		#print self._re.findall("asdf(df). asdf(er).")
		ParserElement.enablePackrat()
		LBRACK = Suppress("(") 
		RBRACK = Suppress(")") 
		COLON  = Suppress(".") 
		ALT_OP = Suppress(",") 
 
		# predicate/function grammar
		#print alphanums
		ident = Word(alphanums+"_"+"-")
		predElem = Forward() 
		predExpr = Group(ident + LBRACK + predElem + ZeroOrMore(ALT_OP + predElem) + RBRACK + \
				 Optional(COLON)) ^ ident #.setParseAction(self.__mkstr))
		predElem << predExpr 
		self._pred = OneOrMore(predExpr) 
		#.setParseAction(self.__mklist1))

	#def __mklist1(self, s,l,t):
        #    return list(t)

	#def __mklist(self, s,l,t):
	#	x = []
	#	for i in t:
	#		x.append(i)
		#print type(t), t
	#	return x

	#def __mkstr(self, s,l,t):
	#	return str(t[0])

	def interrupt(self):
		if not self._run:
			return True
		else:
			self._run = False
		return False

	def read(self, f):
		self._src.onRead()
		res = ""
		done = False
		self._run = True
		try:
			s = f.readline()
			while len(s) > 0 and self._run: #and not s.startswith("Solutions:"):
				#if s.find(":-") == -1:
					#for i in self._re.findall(s):
					#	card = self._src.predicates().get(i[1])
					#	if not card is None: #done or not card is None:
					#		res = res + i[0]
					#if len(res) > 0:
				#try:
					#vals = self._pred.parseString(res).asList()
				vals = self._pred.parseString(s).asList()
				#except (Exception):
				#	pass
				self._dest.onMatch(vals)
				#res = ""
				s = f.readline()
		except IOError as e:
			saveClose(f)
			raise e
		self._run = False
		self._dest.onFinish()
				
	def write(self, f):
		self._dest.onWrite()
		try:
			#for s in self._src.predicates():
				#f.write(s)
			f.write("\n")
		except IOError as e:
			saveClose(f)
			raise e

class PredicateReader(object):

	def __init__(self, preds):
		self._preds = preds
	
	def onRead(self):
		pass

	def predicates(self):
		return self._preds
	
	def onMatch(self, inpt):
		print inpt
			
	def onFinish(self):
		pass

	def onWrite(self):
		pass

