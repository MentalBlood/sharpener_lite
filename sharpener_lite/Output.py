import io
import sys
from functools import partial



class Output:

	class File(io.IOBase):

		mapping = {
			'stderr': sys.stderr,
			'stdout': sys.stdout
		}

		def __new__(C, name: str):
			try:
				return partial(lambda x: x, C.mapping[name])
			except KeyError:
				return partial(open, name, 'w', encoding='utf8')

	def __init__(self, name: str):
		self.file = Output.File(name)

	def write(self, content: str) -> None:
		with self.file() as f:
			f.write(content)