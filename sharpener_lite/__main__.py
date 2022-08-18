import glob
import json
import argparse

from .Output import Output
from .Session import Session



parser = argparse.ArgumentParser(description='Handy benchmarking tool')
parser.add_argument(
	'-r',
	'--root',
	type=str,
	help='Root folder path',
	default='.',
	required=False
)
parser.add_argument(
	'-cp',
	'--config_prefix',
	type=str,
	help='Config file name prefix',
	default='benchmark_',
	required=False
)
parser.add_argument(
	'-c',
	'--config',
	type=str,
	help='Config name (file name is "<config prefix>_<config name>.json")',
	default='default',
	required=False
)
parser.add_argument(
	'-tp',
	'--test_prefix',
	type=str,
	help='Tests files names prefix',
	default='benchmark_',
	required=False
)
parser.add_argument(
	'-m',
	'--metrics',
	type=str,
	nargs='+',
	help='Metrics names to evaluate (all by default)',
	default=None,
	required=False
)
parser.add_argument(
	'-f',
	'--format',
	type=str,
	help='Output format',
	choices=Session.Report.formats(),
	default='table',
	required=False
)
parser.add_argument(
	'-o',
	'--output',
	type=str,
	help='Output target',
	default='stdout',
	required=False
)
parser.add_argument(
	'--progress',
	action=argparse.BooleanOptionalAction,
	default=True
)
args = parser.parse_args()



with open(
	glob.iglob(
		f'{args.root}/**/{args.config_prefix}{args.config}.json',
		recursive=True
	).__next__(),
	'rb'
) as f:
	config = json.loads(f.read())



Output(
	args.output
).write(
	Session(
		args.root,
		args.test_prefix,
		config
	)(
		args.metrics,
		args.progress
	).format(
		args.format
	)
)