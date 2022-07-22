import re
import abc
from typing import Iterable



class PatternEncoded(str):

	pattern: str

	def __new__(C, s: str):
		return re.match(C.pattern, s).groups()[0]

	@classmethod
	def match(C, s: str) -> bool:
		return re.match(C.pattern, s) is not None

	@classmethod
	def filter(C, i: Iterable):
		return filter(lambda e: C.match(e), i)

	@classmethod
	def unfilter(C, i: Iterable):
		return filter(lambda e: not C.match(e), i)