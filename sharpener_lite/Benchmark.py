from __future__ import annotations

import re
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

	@functools.cached_property
	def metric_mean_time(self):

		n = self.config.special['n']

		return (
			timeit.timeit(
				'f()',
				setup=self.prepare,
				globals={'f': self.run},
				number=n
			) / n * units.seconds
		).to(units.milliseconds)

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

		def __new__(C, b: Benchmark, metrics):
			return {
				k: C.Value(v)
				for k, v in b.metrics.items()
				if (metrics is None) or (k in metrics)
			}

		class Value(str):

			def __new__(C, v: Any, precision: int=3):
				if isinstance(v, pint.quantity.Quantity):
					return re.sub(
						f'(\\.\\d{{{precision-1}}}) ',
						r'\g<1>0 ',
						str(C.Rounded(v.m, 3) * v.u)
					)
				elif isinstance(v, float):
					return str(C.Rounded(v))
				else:
					return str(v)

			class Rounded(float):

				def __new__(self, f: float, precision: int):
					if math.floor(f) != f:
						return round(f, precision)
					else:
						return f