from collections import OrderedDict
from typing import *

from corpus_reader.utils import concat_list


def pprint(cls):
	print(cls.pretty_str())


def set_parent(child, parent):
	child.parent = parent


def ids_to_full_id(ids: OrderedDict) -> str:
	"""
	>>> ids_to_full_id(OrderedDict({'D':1, 'S':2, 'E': None}))
	'D1-S2'
	"""
	return concat_list([str(key) + str(value) for key, value in ids.items() if value is not None])


class Hierarchy:

	def __init__(self, id, symbol):
		self.id: int = id
		self.ids: OrderedDict = OrderedDict({'C': None, 'D': None, 'S': None, 'EV': None, 'R': None, 'RM': None, 'E':None,
								 'M': None, 'T': None})  # TOOPTIMIZE
		self.ids[symbol] = id
		self.full_id = ids_to_full_id(self.ids)
		self.refs: Dict = {}

	def update_full_id(self, id, symbol):
		"""
		>>> token1 = Token(id=1, text='they')
		>>> token1.update_full_id(id=2, symbol='S')
		>>> token1.update_full_id(id=5, symbol='E')
		>>> token1.full_id
		'S2-E5-T1'
		"""
		self.ids[symbol] = id
		self.full_id = ids_to_full_id(self.ids)

	def set_referencer(self, referred: 'Hierarchy', symbol: str):
		"""
		Set a referencer (pointer) in "obj" that points to the "referred" instance. This referencer is stored
		>>> A = Token(1, 'Hi')
		>>> B = Token(2, 'NLP')
		>>> A.set_referencer(B, 'T')
		>>> A.refs['T']  # doctest: +ELLIPSIS
		<structure.Token object at ...>
		"""
		self.refs[symbol] = referred

	def set_ref_and_full_id(self, referred: 'Hierarchy', symbol: str):
		"""
		Set a referencer for self, and also create/update full_id, ids attribute
		>>> A = Token(1, 'Hi')
		>>> B = Token(2, 'NLP')
		>>> sen = Sentence(9, [A, B])
		>>> A.set_ref_and_full_id(sen, 'S')
		>>> A.refs['S']  # doctest: +ELLIPSIS
		<structure.Sentence object at ...>
		>>> A.full_id
		'S9-T1'
		"""
		self.set_referencer(referred, symbol)
		self.update_full_id(referred.id, symbol)


class ObjectList:

	def __init__(self, members):
		self.members = members

	def __iter__(self):
		return iter(self.members)

	def __len__(self):
		return len(self.members)

	def sep_str(self, sep='|'):
		return concat_list(self.members, sep=sep)

	def __str__(self):
		return self.sep_str(' ')


class Token(Hierarchy):
	"""
	>>> token1 = Token(id=1, text='Deep', char_b=2368, char_e=2371)
	>>> token2 = Token(id=2, text='Learning', char_b=2373, char_e=2380)
	>>> token1.full_id
	'T1'
	>>> sentence1 = Sentence(0, [token1, token2])
	>>> token1.set_sentence(sentence1)
	>>> token1.full_id
	'S0-T1'
	>>> token1.refs['S'].id, token1.ids['S']
	(0, 0)
	>>> doc1 = Document([sentence1], 0)
	>>> token1.set_document(doc1)
	>>> token1.full_id
	'D0-S0-T1'
	"""
	def __init__(self, id: int, text: str, char_b: int=None, char_e: int=None, pos: str=None, dep_type: str=None, dep_head: str=None):
		"""
		:param id: token id
		:param text: the string of the token
		:param char_b: the character begin position
		:param char_e: the character end position
		:param pos: pos tagging
		:param dep_type: dependency tagging
		:param dep_head: dependency head (which token this token points to)
		"""
		self.text = text

		self.char_b = char_b
		self.char_e = char_e
		self.pos = pos
		self.dep_type = dep_type
		self.dep_head = dep_head

		Hierarchy.__init__(self, id, 'T')

	def __str__(self):
		return self.text

	def set_sentence(self, sentence: 'Sentence'):
		self.set_ref_and_full_id(sentence, 'S')
		
	def set_document(self, document: 'Document'):
		self.set_ref_and_full_id(document, 'D')


class EntityMention(Hierarchy, ObjectList):
	"""
	>>> t1 = Token(1, '台積電')
	>>> t2 = Token(2, '集團')
	>>> e_mention = EntityMention(1, [t1, t2], 'ORGANIZATION')
	>>> str(e_mention), e_mention.sep_str("|")
	('台積電 集團', '台積電|集團')
	>>> e_mention.pretty_str()
	'text:台積電 集團 type:ORGANIZATION'
	>>> pprint(e_mention)
	text:台積電 集團 type:ORGANIZATION
	>>> e_mention.set_sentence(Sentence(2, [t1, t2]))
	"""
	def __init__(self, id: int, tokens: List[Token], type: str = None, char_b: int = None, char_e: int = None,
	             token_b: int = None, token_e: int = None, sentence = None, document = None):

		# required
		self.id = id
		self.tokens = tokens
		self.type = type
		self.text = ' '.join([str(token) for token in tokens])

		# position
		self.char_b = char_b
		self.char_e = char_e
		self.token_b = token_b
		self.token_e = token_e

		# optional
		self.sentence = self.set_sentence(sentence) if sentence else None
		self.sid = None
		self.document = self.set_document(document) if document else None
		self.did = None

		# might not be annotated yet
		self.entity = None
		self.entity_id = None
		self.cluster = None
		self.cid = None

		ObjectList.__init__(self, tokens)
		Hierarchy.__init__(self, id, 'M')

	def __str__(self):
		return ObjectList.sep_str(self, sep=' ')

	def pretty_str(self):
		return "text:{} ".format(self.text) + "type:{}".format(self.type)

	def set_sentence(self, sentence: 'Sentence'):
		self.set_ref_and_full_id(sentence, 'S')

	def set_entity(self, entity: 'Entity'):
		self.set_ref_and_full_id(entity, 'E')


class RelationMention(Hierarchy):
	"""
	>>> arg1 = EntityMention(id=1,tokens=[Token(10, '台積電')],type='ORG')
	>>> arg2 = EntityMention(id=2,tokens=[Token(10, '劉德音'), Token(11, '董事長')],type='PER')
	>>> r_mention = RelationMention(id=1, type='ORG-AFF', arg1=arg1, arg2=arg2)
	>>> r_mention.type, r_mention.full_id
	('ORG-AFF', 'R1')
	>>> r_mention.get_left_right_args()
	"""
	def __init__(self, id: int, type: str, arg1: EntityMention, arg2: EntityMention):
		self.id = id
		self.type = type
		self.arg1 = arg1
		self.arg2 = arg2
		
		if arg1.sentence:
			if arg1.sentence is arg2.sentence:
				self.set_sentence(arg1.sentence)
			else:
				raise ValueError("arg1 and arg2 in a relation mention are not in the same sentence! ")
		
		if arg1.document:
			if arg1.document is arg2.document:
				self.set_document(arg1.document)
			else:
				raise ValueError("arg1 and arg2 in a relation mention are not in the same document! ")

		Hierarchy.__init__(self, id, 'R')

	def get_left_right_args(self):
		"""
		:return: left argument, right argument, relation type with direction, e.g.,PHYS-lr.
		"""
		if self.arg1.char_b < self.arg2.char_b:
			self.arg_l = self.arg1
			self.arg_r = self.arg2
			self.label = self.type + '-lr'
		elif self.arg1.char_b > self.arg2.char_b:
			self.arg_l = self.arg2
			self.arg_r = self.arg1
			self.label = self.type + '-rl'
		else:
			print("error! relation argument positions error!")
		return self.arg_l, self.arg_r, self.label

	def set_sentence(self, sentence: 'Sentence'):
		self.set_ref_and_full_id(sentence, 'S')

	
class Sentence(Hierarchy, ObjectList):
	"""
	Sentence contains the list of entity mention and list of relation mentions.
	>>> token1 = Token(id=1, text='Deep', char_b=2368, char_e=2371)
	>>> token2 = Token(id=2, text='Learning', char_b=2373, char_e=2380)
	>>> sentence1 = Sentence(0, [token1, token2])
	>>> print(sentence1)
	Deep Learning
	>>> token1.full_id, token2.full_id
	('S0-T1', 'S0-T2')
	"""
	def __init__(self, id: int, tokens: List[Token], char_b: int = None, char_e: int = None):

		self.tokens = tokens

		self.char_b = char_b
		self.char_e = char_e

		self.entity_mentions = []

		self.relation_mentions = []

		Hierarchy.__init__(self, id, 'S')
		ObjectList.__init__(self, tokens)

		# referencers
		self.set_to_tokens()

	def pprint(self):
		e_mentions_string = ''
		for e in self.entity_mentions:
			e_mentions_string += str(e) + '\t'
		return "sent_index:{}\n".format(self.id) + "text:{}\n".format(self.text) + \
		       "e_mentions:\n" + e_mentions_string

	def set_document(self, document: 'Document'):
		self.set_ref_and_full_id(document, 'D')

	def set_to_tokens(self):
		for token in self.tokens:
			token.set_sentence(self)


class Document(Hierarchy, ObjectList):
	"""
	A Document contains an id and a list of Sentence.
	>>> token1 = Token(id=1, text='Deep', char_b=2368, char_e=2371)
	>>> token2 = Token(id=2, text='Learning', char_b=2373, char_e=2380)
	>>> sentence1 = Sentence(0, [token1, token2])
	>>> token3 = Token(id=1, text='Machine')
	>>> token4 = Token(id=2, text='Reading')
	>>> sentence2 = Sentence(1, [token3, token4])
	>>> sentences = [sentence1,sentence2]
	>>> document = Document(sentences=sentences, id=20)
	>>> document.full_id, sentence1.full_id, token2.full_id
	('D20', 'D20-S0', 'D20-S0-T2')

	"""
	def __init__(self, id: int, sentences: List[Sentence]):

		self.sentences = sentences

		self.cluster = None

		Hierarchy.__init__(self, id, 'D')

		ObjectList.__init__(self, sentences)

		# referencers
		self.set_to_sentences()

	def set_to_sentences(self):
		for sentence in self.sentences:
			sentence.set_document(self)
			self.set_to_tokens(sentence)

	def set_to_tokens(self, sentence):
		for token in sentence:
			token.set_document(self)

	def set_cluster(self, cluster: 'Cluster'):
		self.set_ref_and_full_id(cluster, 'C')


class Cluster(ObjectList, Hierarchy):
	def __init__(self, id: int, documents: List[Document]):
		self.documents = documents

		ObjectList.__init__(self, documents)
		Hierarchy.__init__(self, id, 'C')

	def set_to_documents(self):
		for document in self.documents:
			document.set_cluster(self)


# after coreference
class Entity:
	def __init__(self, id: int, mentions: List[EntityMention]):
		self.id = id
		self.mentions = mentions
