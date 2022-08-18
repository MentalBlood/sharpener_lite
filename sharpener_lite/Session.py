import io
import os
import glob
import json
import functools
import importlib
import dataclasses
from rich.table import Table
from types import ModuleType
from rich.console import Console
from rich.progress import track, Progress

from .Benchmark import Benchmark
from .PatternEncoded import PatternEncoded



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

	@dataclasses.dataclass(frozen=True)
	class Report:

		as_dict: dict

		@functools.cached_property
		def as_json(self) -> str:
			return json.dumps(self.as_dict, indent=4)

		@functools.cached_property
		def as_table(self) -> str:

			t = Table(show_header=False, show_lines=True)

			for module_name, benchmarks in self.as_dict.items():

				benchmarks_table = Table(show_header=False, show_lines=True, pad_edge=False, show_edge=False)
				for b_name, b in benchmarks.items():

					metrics_table = Table(show_header=False, pad_edge=False, show_edge=False)
					for metric_name, metric_value in b.items():
						metrics_table.add_row(metric_name, metric_value)

					benchmarks_table.add_row(b_name, metrics_table)

				t.add_row(module_name, benchmarks_table)

			output = io.StringIO()
			Console(file=output).print(t)

			return output.getvalue()

		def format(self, name: str) -> str | dict:
			return getattr(self, f'as_{name}')

		class FormatName(PatternEncoded):
			pattern = 'as_((?:\w|_)+)'

		@classmethod
		def formats(C) -> list[str]:
			return [
				C.FormatName(name)
				for name in C.FormatName.filter(
					dir(C)
				)
			]

	def __call__(self, metrics, show_progress):

		result = {}

		with Progress(auto_refresh=False, disable=not show_progress) as p:

			benchmarks_task = p.add_task(f'[blue]Running benchmarks', total=sum((len(m) for m in self.modules.values())))

			for m_name, m in self.modules.items():

				module_task = p.add_task(f'[green]{m_name}', total=len(m))

				result[m_name] = {}
				for b_name, b in m.items():
					result[m_name][b_name] = Benchmark.Report(b, metrics)
					p.update(benchmarks_task, advance=1)
					p.update(module_task, advance=1)

		return self.__class__.Report(result)