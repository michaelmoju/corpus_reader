import re
import json
from multi_doc_analyzer.structure.structure import Token


class Word:
	def __init__(self, string, start, end):
		self.string = string
		self.start = start
		self.end = end


class SgmSentence:
	def __init__(self, string, start, end):
		self.string = string
		self.start = start
		self.end = end
		self.words = []
		self.tokens = []

	def to_words(self, t):
		self.words.append(Word(t['word'], t['characterOffsetBegin'], t['characterOffsetEnd']-1))

	def clean_first_sentence(self):
		if "\n\n" in self.string:
			o_len = len(self.string)
			self.string = re.sub('.*\n\n?', '', self.string)
			redun_len = o_len - len(self.string)
			self.start += redun_len
		if re.match('.* \n?', self.string):
			o_len = len(self.string)
			self.string = re.sub('.* \n?', '', self.string)
			redun_len = o_len - len(self.string)
			self.start += redun_len


class SgmDoc:
	def __init__(self, docid, doc_chars):
		self.doc_id = docid
		self.doc_chars = doc_chars
		self.sentence_list = []
		self.text = ""
		for t in self.doc_chars:
			self.text += t

	def chinese_ssplit(self):
		string = ''
		for index, t in enumerate(self.doc_chars):
			string += t
			# sentence segmentation
			if t == '。':
				mySentence = SgmSentence(string=string, start=index - (len(string) - 1), end=index)
				self.sentence_list.append(mySentence)
				string = ''
				
	def english_ssplit(self, nlp):
		props = {'annotators': 'ssplit, pos', 'outputFormat': 'json', 'pipelineLanguage': 'en'}

		offset = 0
		for c in self.doc_chars:
			if c not in ['\n', ' ', '\t', '.']:
				break
			else:
				offset += 1

		doc = json.loads(nlp.annotate(self.text, properties=props))

		for s in doc['sentences']:
			tokens = []
			text = ''

			start = s['tokens'][0]['characterOffsetBegin'] + offset
			for t in s['tokens'][:-1]:
				text += t['originalText'] + t['after']
				tokens.append(Token(t['index'], t['originalText'], t['characterOffsetBegin'] + offset,
				                    t['characterOffsetEnd'] + offset, t['pos']))

			text += s['tokens'][-1]['originalText']
			end = s['tokens'][-1]['characterOffsetEnd'] + offset

			mySentence = SgmSentence(string=text, start=start, end=end)
			mySentence.tokens = tokens

			self.sentence_list.append(mySentence)
