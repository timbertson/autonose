#!/usr/bin/env python

from setuptools import *
setup(
	name='sniffles',
	version='0.0.1',
	author_email='tim3d.junk+sniffles@gmail.com',
	author='Tim Cuthbertson',
	url='http://github.com/gfxmonk/sniffles/tree',
	description="test tracker for nosetests",
	long_description="test tracker for nosetests",
	packages = find_packages(exclude=['test', 'test.*']),
	entry_points = {
		'nose.plugins.0.10': ['sniffles = sniffles:Watcher'],
		'console_scripts':   ['autonose = sniffles.main',
	},
	classifiers=[
		"License :: OSI Approved :: BSD License",
		"Programming Language :: Python",
		"Development Status :: 4 - Beta",
		"Intended Audience :: Developers",
		"Topic :: Software Development :: Libraries :: Python Modules",
		"Topic :: Software Development :: Testing",
	],
	keywords='test nosetests nose nosetest autotest auto runner',
	license='BSD',
	zip_safe=True,
	install_requires=[
		'setuptools',
		'nose',
		'mandy',
		'snakefood',
	],
)
