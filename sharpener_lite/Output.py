import io
import sys
import functools
import dataclasses



@dataclasses.dataclass(frozen=True)
class Output:

	name: str

	class File(io.IOBase):

		mapping = {
			'stderr': sys.stderr,
			'stdout': sys.stdout
		}

		def __new__(C, name: str):
			try:
				return functools.partial(lambda x: x, C.mapping[name])
			except KeyError:
				return functools.partial(open, name, 'w', encoding='utf8')

	@functools.cached_property
	def file(self):
		return self.__class__.File(self.name)

	def write(self, content: str) -> None:
		with self.file() as f:
			f.write(content)