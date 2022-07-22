from __future__ import annotations

import re
import timeit
import statistics
from typing import Any
from functools import partial
from abc import ABC, abstractmethod

from .metric import metric



class Benchmark(ABC):

	def __init__(self, config: Benchmark.Config):

		self.config = config

		for method_name in ['prepare', 'run', 'clean']:
			method = getattr(self, method_name)
			new_method = partial(method, **config.kwargs)
			setattr(self, method_name, new_method)

	def prepare(self, *args, **kwargs):
		pass

	@abstractmethod
	def run(self, *args, **kwargs):
		pass

	def clean(self, *args, **kwargs):
		pass

	def __call__(self) -> float:

		self.prepare()
		result = timeit.timeit('f()', globals={'f': self.run}, number=1)
		self.clean()

		return result

	@property
	def metrics(self) -> list[metric]:
		return [
			e
			for name in set(dir(self)) - {'metrics'}
			for e in [getattr(self, name)]
			if type(e) == metric
		]

	class Config(dict):

		def isSpecial(name) -> bool:
			return re.match('__\w+__', name)

		@property
		def kwargs(self) -> dict[str, Any]:
			return {
				k: v
				for k, v in self.items()
				if not Benchmark.Config.isSpecial(k)
			}

		@property
		def special(self) -> dict[str, Any]:
			return {
				k[2:-2]: v
				for k, v in self.items()
				if Benchmark.Config.isSpecial(k)
			}

	class Report(dict):

		def __new__(_, b: Benchmark):

			t = statistics.mean(
				(
					b()
					for _ in range(b.config.special['n'])
				)
			)

			return {
				'time': t,
				'metrics': {
					m.name: m(b, t)
					for m in b.metrics
				}
			}