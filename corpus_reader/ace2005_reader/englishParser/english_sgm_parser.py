import glob
import re
from multi_doc_analyzer.reader.ace2005_reader import SgmDoc
from lxml import etree
from stanfordcorenlp import StanfordCoreNLP
import json

def parse_sgm_to_SgmDoc(fh):
	parser = etree.XMLParser(recover=True)
	tree = etree.parse(fh, parser=parser)
	root = tree.getroot()
	assert root.tag == 'DOC'

	doc_id = ''
	for child in root:
		if child.tag == 'DOCID':
			doc_id = child.text.strip()

	doc_chars = []
	with open(fh) as f:
		for l in f:
			l = re.sub('<.*?>', '', l)
			for c in l:
				doc_chars.append(c)

	return SgmDoc(doc_id, doc_chars)


def parse_sgms(path, nlp):
	dicts = {}
	files = glob.glob(path + '*.sgm')
	for f in files:
		mySgmDoc = parse_sgm_to_SgmDoc(f)
		mySgmDoc.english_ssplit(nlp)
		dicts[mySgmDoc.doc_id] = mySgmDoc

	return dicts


if __name__ == '__main__':
	
	nlp = StanfordCoreNLP('http://140.109.19.190', port=9000, lang='en')
	
	dicts = parse_sgms('/Users/moju/work/resource/data/LDC2006T06/data/English/wl/adj/', nlp)
	
	# print(dicts["AGGRESSIVEVOICEDAILY_20041101.1144"].doc_id)
	# print(dicts["AGGRESSIVEVOICEDAILY_20041101.1144"].doc_chars)
	# print(dicts["AGGRESSIVEVOICEDAILY_20041101.1144"].sentence_list[1])

