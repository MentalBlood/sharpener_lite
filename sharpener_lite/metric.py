import dataclasses
from typing import Callable



@dataclasses.dataclass
class metric:

	f: Callable

	@property
	def name(self):
		return self.f.__name__

	def __call__(self, *args, **kwargs):
		return self.f(*args, **kwargs)