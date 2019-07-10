import sys
from collections import OrderedDict
import re
import os
from typing import Iterable


def parse_id(id: str):
	"""
	>>> print(parse_id('D3-S34-EV3'))
	OrderedDict([('D', '3'), ('S', '34'), ('EV', '3')])
	>>> print(parse_id('D3-S34-EV3')['EV'])
	3
	"""
	ids = []
	for item in id.split('-'):
		match = re.match(r"([a-z]+)([0-9]+)", item, re.I)
		if match:
			items = match.groups()
		ids.append(items)

	return OrderedDict(ids)


def lprint(*args, **kwargs):
	import inspect
	callerFrame = inspect.stack()[1]  # 0 represents this line
	myInfo = inspect.getframeinfo(callerFrame[0])
	myFilename = os.path.basename(myInfo.filename)
	print('{}({}):'.format(myFilename, myInfo.lineno), *args, flush=True, file=sys.stderr, **kwargs)


def concat_list(list_: Iterable, sep='-', exclude_none=True):
	"""
	>>> concat_list(["ABC", "123", None], sep='|', exclude_none=False)
	'ABC|123|None'
	>>> concat_list(["C", None, "D1", "S2", "T", 7], sep='-')
	'C-D1-S2-T-7
	>>> concat_list(None)
	Traceback (most recent call last):
	...
	TypeError: The first argument of the function concat_list must be an iterable object.
	"""
	try:
		if exclude_none:
			return sep.join([str(item) for item in list_ if item is not None])
		else:
			return sep.join([str(item) for item in list_])
	except TypeError:
		raise TypeError('The first argument of the function concat_list must be an iterable object.')


def id_incrementer():
	id_ = -1
	while True:
		yield id_
		id_ += 1
