from multi_doc_analyzer.structure.structure import *
from multi_doc_analyzer.reader.ace2005_reader import chinese_parser
from multi_doc_analyzer.reader.ace2005_reader import english_parser

class ACE05Reader:
	"""
	Read and parse ACE-2005 source file (*.sgm) and annotation file (*.xml).
	
	"""
	def __init__(self, lang: str):
		"""
		:param lang: the language which is read_file {en:english, zh:chinese}
		"""
		self.lang = lang
	
	def read(self, fp) -> Dict[str, Document]:
		"""
		:param fp: file path of ACE-2005 (LDC2006T06), e.g., '~/work/data/LDC2006T06/'
		:return: Dict[documentID, Document]
		"""
		fp = fp + 'data/'
		if self.lang == 'en':
			data_path = fp + 'English/'
			doc_dicts = english_parser.parse_source(data_path)
			return doc_dicts
		elif self.lang == 'zh':
			data_path = fp + 'Chinese/'
			doc_dicts = chinese_parser.parse_source(data_path)
			return doc_dicts


if __name__=='__main__':
	reader = ACE05Reader('en')
	doc_dicts = reader.read('/media/moju/data/work/resource/data/LDC2006T06/')