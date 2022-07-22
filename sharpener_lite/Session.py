import os
import glob
import timeit
import functools
import importlib
import statistics
import dataclasses
from types import ModuleType

from .Benchmark import Benchmark



class Module(ModuleType):

	def __new__(_, file_path: str, file_prefix: str):

		spec = importlib.util.spec_from_file_location(
			Module.name(file_path, file_prefix),
			file_path
		)
		module = importlib.util.module_from_spec(spec)
		spec.loader.exec_module(module)

		return module

	def name(path, prefix):

		file_name = os.path.basename(path)
		without_ext = os.path.splitext(file_name)[0]

		return without_ext[len(prefix):]


class Benchmarks(dict):

	def __new__(_, module: Module, config):
		return {
			name: e(Benchmark.Config(config[name]))
			for name in dir(module)
			for e in [getattr(module, name)]
			if name in config and hasattr(e, '__bases__') and Benchmark in e.__bases__
		}


@dataclasses.dataclass
class Session:

	path: str
	file_prefix: str
	config: dict

	@property
	def paths(self):
		return filter(
			lambda path: Module.name(path, self.file_prefix) in self.config.keys(),
			glob.iglob(f'{self.path}/**/{self.file_prefix}*.py', recursive=True)
		)

	@functools.cached_property
	def modules(self):
		return {
			name: Benchmarks(
				Module(p, self.file_prefix),
				self.config[name]
			)
			for p in self.paths
			for name in [Module.name(p, self.file_prefix)]
		}

	def __call__(self):
		return {
			m_name: {
				b_name: Benchmark.Report(b)
				for b_name, b in m.items()
			}
			for m_name, m in self.modules.items()
		}