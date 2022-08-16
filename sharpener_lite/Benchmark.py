from __future__ import annotations

import pint
import math
import timeit
import functools
import statistics
from typing import Any
from abc import ABC, abstractmethod

from .units import units
from .PatternEncoded import PatternEncoded



class Benchmark(ABC):

	def __init__(self, config: Benchmark.Config):
		self.config = config

	def prepare(self):
		pass

	@abstractmethod
	def run(self):
		pass

	def clean(self):
		pass

	def __call__(self) -> float:

		self.prepare()
		result = timeit.timeit('f()', globals={'f': self.run}, number=1)
		self.clean()

		return result

	@functools.cached_property
	def metric_mean_time(self):
		return statistics.mean(
			(
				self()
				for _ in range(self.config.special['n'])
			)
		) * units.seconds

	@property
	def metrics(self) -> dict:
		return {
			Benchmark.MetricName(name): getattr(self, name)
			for name in Benchmark.MetricName.filter(dir(self))
		}

	class Config(dict):

		@property
		def kwargs(self) -> dict[str, Any]:
			return {
				k: self[k]
				for k in self.__class__.Special.unfilter(self)
			}

		@property
		def special(self) -> dict[str, Any]:
			return {
				self.__class__.Special(k): self[k]
				for k in self.__class__.Special.filter(self)
			}

		class Special(PatternEncoded):
			pattern = '__(\w+)__'

	class MetricName(PatternEncoded):
		pattern = 'metric_((\w|_)+)'

	class Report(dict):

		def __new__(C, b: Benchmark):
			return {
				k: C.Value(v)
				for k, v in b.metrics.items()
			}

		class Value(str):

			def __new__(C, v: Any):
				if isinstance(v, pint.quantity.Quantity):
					return str(C.Rounded(v.m, 3) * v.u)
				elif isinstance(v, float):
					return str(C.Rounded(v))
				else:
					return str(v)

			class Rounded(float):

				def __new__(self, f: float, precision: int):
					if math.floor(f) != f:
						return round(f, round(math.log(1 / (f - math.floor(f)), 10)) - 1 + precision)
					else:
						return f