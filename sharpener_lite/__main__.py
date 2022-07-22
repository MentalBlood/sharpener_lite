import glob
import json
import pprint
import argparse

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
args = parser.parse_args()



with open(
	glob.iglob(
		f'{args.root}/**/{args.config_prefix}{args.config}.json',
		recursive=True
	).__next__(),
	'rb'
) as f:
	config = json.loads(f.read())


pprint.pprint(
	Session(args.root, args.test_prefix, config)()
)