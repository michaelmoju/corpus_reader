from corpus_reader.structure.structure import *
from corpus_reader.utils import *
import re
import glob

special_tokens = {"-DQS-": "``", "-DQE-": "''", "-LRB-": "(", "-RRB-": ")", "-COMMA-": ",", "-COLON-": ":",
				  "-SEMICOLON-": ";", "-PERIOD-": ".", "-DOLLAR-": "$", "-PERCENT-": "%"}


class MiwaReader:
	"""
	Read and parse Miwa source file (*.split.stanford.so) and annotation file (*.split.ann).
	"""
	def read(self, fp) -> Dict[str, Document]:
		"""
		>>> read_so("/media/moju/data/work/resource/data/ace-2005/miwa2016/corpus/dev/AFP_ENG_20030327.0224.split.stanford.so")
		'<>'
		:param fp:
		:return:
		"""
		out_dicts = {}
		
		rgx_so = re.compile('(.*).split.stanford.so')
		so_files = glob.glob(fp + '*.split.stanford.so')
		for doc_idx, f in enumerate(so_files):
			docID, *_ = rgx_so.match(os.path.basename(f)).groups()
			sentences = read_so(f)
			
			doc_path_ann = fp + docID + '.split.ann'
			entity_mentions, relation_mentions = read_annot(doc_path_ann)
			
			doc = merge_so_annot(sentences, entity_mentions, relation_mentions, doc_idx)
			out_dicts[docID] = doc
			
		return out_dicts
		


def merge_so_annot(sentences: List[Sentence], e_mentions: Dict[str, EntityMention],
                  r_mentions: Dict[str, RelationMention], doc_idx: int) -> Document:
	"""
	:param sentences:
	:param e_mentions:
	:param r_mentions:
	:return:
	>>> merge_so_annot([], )
	"""
	
	for em_id, e_mention in e_mentions.items():
		for sentence in sentences:
			if sentence.char_b <= e_mention.char_b <= sentence.char_e:
				if e_mention.char_e > sentence.char_e:
					lprint('e_mention cross sentence')
				else:
					sentence.entity_mentions.append(e_mention)
	
	for rm_id, r_mention in r_mentions.items():
		for sentence in sentences:
			if sentence.char_b <= r_mention.arg1.char_b <= sentence.char_e:
				if r_mention.arg1.char_e > sentence.char_e:
					lprint('arg1 cross sentence')
				else:
					if r_mention.arg2.char_b < sentence.char_b or r_mention.arg2.char_e > sentence.char_e:
						lprint('args cross sentence')
					else:
						sentence.relation_mentions.append(r_mention)
	my_doc = Document(id=doc_idx, sentences=sentences)
	my_doc.name = sentences[0].doc_name
	return my_doc


def read_so(fh):
	rgx_file_name = re.compile('(.*).split.stanford.so')
	rgx_dep = re.compile('(.*)="(.*)"')
	out_sents = []
	with open(fh, 'r') as f:
		docID, *_ = rgx_file_name.match(os.path.basename(f.name)).groups()
		mySent = []
		tokens = []
		for line in f:
			if line is '\n': continue  # ignore blank lines
			else:
				data = line.rstrip().split()
			if len(data) == 5:
				if tokens:
					mySent = Sentence(id=sent_id, tokens=tokens, char_b=int(sent_start), char_e=int(sent_end))
					mySent.doc_name = docID
					out_sents.append(mySent)
					tokens = []
				sent_start, sent_end, _, id, parse_status = data
				sent_id = int(id[5:-1])
				if parse_status[14:-1] != 'success':
					lprint(parse_status[14:-1])
					lprint("parse not success!!")
			elif len(data) == 7:
				start, end, _, id, word, pos, dep = data
				word = word[6:-1]
				dep_type, dep_head = rgx_dep.match(dep).groups()
				
				for special_token in special_tokens.keys():
					if special_token in word:
						word = re.sub(special_token, special_tokens[special_token], word)
				myToken = Token(id[4:-1], word, start, end, pos[5:-1], dep_type, dep_head)
				tokens.append(myToken)
			else:
				lprint("len(data):{}".format(len(data)))
				lprint("read_so error!")
		if mySent:
			out_sents.append(mySent)
			del mySent
	return out_sents


def read_annot(fh):
	entity_mentions = {}
	relation_mentions = {}
	
	e_ind = 0
	r_ind = 0

	with open(fh, 'r') as f:
		for line in f:
			if line is '\n': continue # ignore blank lines
			data = line.rstrip().split()
			rgx_entity = re.compile('(.*)-(E[0-9]+)-([0-9]+)')
			rgx_relation = re.compile('(.*)-(R[0-9]+)-([0-9]+)')

			if rgx_entity.search(data[0]): #entity
				docID, *_ = rgx_entity.match(data[0]).groups()
				my_em = EntityMention(id=e_ind, tokens=[], type=data[1], char_b=int(data[2]), char_e=int(data[3]))
				my_em.string = ' '.join(data[4:])
				entity_mentions[data[0]] = my_em
				e_ind += 1
			elif rgx_relation.search(data[0]): #relation
				# split = lambda arg: arg.split(":")
				# arg1 = split(data[2])[1]
				# arg2 = split(data[3])[1]
				arg1 = data[2].split(":")[1]
				arg2 = data[3].split(":")[1]
				
				arg1 = entity_mentions[arg1]
				arg2 = entity_mentions[arg2]
				
				relation_mentions[data[0]] = RelationMention(id=r_ind, type=data[1], arg1=arg1, arg2=arg2)
				r_ind += 1
			else:
				lprint("read_annot error!")
				
	return entity_mentions, relation_mentions


def check_no_nested_entity_mentions(entity_mentions: Dict[str, EntityMention], docID):
	def nested(m, start, end):
		for i in range(start, end + 1):
			if i in range(m.char_b, m.char_e + 1):
				return True

	span_list = []

	for m in entity_mentions.values():
		for (start, end) in span_list:
			if not nested(m, start, end): continue
			else: lprint("nested entities found in {}!".format(docID) + " mentionID:{}".format(m.id) + '\n')
		span_list.append((m.char_b, m.char_e))


if __name__ == '__main__':
	reader = MiwaReader()
	
	sents = read_so('/media/moju/data/work/resource/data/ace-2005/miwa2016/corpus/dev/AFP_ENG_20030327.0224.split.stanford.so')
	
	entity_mentions, relation_mentions = read_annot('/media/moju/data/work/resource/data/ace-2005/miwa2016/corpus/dev/AFP_ENG_20030327.0224.split.ann')
	
	print(len(entity_mentions))
	print(len(relation_mentions))
	
	doc = merge_so_annot(sentences=sents, e_mentions=entity_mentions, r_mentions=relation_mentions, doc_idx=0)
	
	print(len(doc.sentences[10].entity_mentions))
	
	# reader.read('/media/moju/data/work/resource/data/ace-2005/miwa2016/corpus/dev/')
	

