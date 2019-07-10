import glob
import xml.etree.ElementTree as ET
import re
from multi_doc_analyzer.reader.ace2005_reader import SgmDoc

def parse_sgm_to_SgmDoc(fh):
	tree = ET.parse(fh)
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


def parse_sgms(path):
	dicts = {}
	files = glob.glob(path + '*.sgm')
	for f in files:
		mySgmDoc = parse_sgm_to_SgmDoc(f)
		mySgmDoc.chinese_ssplit()
		dicts[mySgmDoc.doc_id] = mySgmDoc

	return dicts


if __name__ == '__main__':

	dicts = parse_sgms('/media/moju/data/work/ace05-parser/Data/LDC2006T06/data/Chinese/wl/adj/')
	print(dicts["DAVYZW_20041223.1020"].doc_chars[100:200])
	print(dicts["DAVYZW_20041223.1020"].sentence_list[0].start)
	print(dicts["DAVYZW_20041223.1020"].sentence_list[0].end)
	print(dicts["DAVYZW_20041223.1020"].sentence_list[0].string)

	# dicts = parse_sgms('/media/moju/data/work/ace05-parser/Data/LDC2006T06/data/Chinese/bn/adj/')
	# print(dicts["CBS20001001.1000.0041"].sentence_list[0].string)
