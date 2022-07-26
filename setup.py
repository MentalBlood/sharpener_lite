import os
from setuptools import setup, find_packages



if __name__ == '__main__':

	long_description = ''
	if os.path.exists('README.md'):
		with open('README.md', encoding='utf-8') as f:
			long_description = f.read()

	setup(
		name='sharpener_lite',
		version='1.1.1',
		description='Handy profiling/benchmarking tool',
		long_description=long_description,
		long_description_content_type='text/markdown',
		author='mentalblood',
		install_requires=[
			# 'pint',
			# 'rich'
		],
		python_requires='>=3.9',
		packages=find_packages()
	)
