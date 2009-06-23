#!/usr/bin/env python

from setuptools import *
setup(
	name='autonose',
	version='0.1.0',
	author_email='tim3d.junk+autonose@gmail.com',
	author='Tim Cuthbertson',
	url='http://github.com/gfxmonk/autonose',
	description="continuous test tracker / runner for nosetests",
	long_description="continuous test tracker / runner for nosetests",
	packages = find_packages(exclude=['test', 'test.*']),
	entry_points = {
		'nose.plugins.0.11': ['autonose = autonose:Watcher'],
		'console_scripts':   ['autonose = autonose:main'],
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
		'nose>=0.11',
		'nosexml>=0.2', # see http://code.google.com/p/python-nosexml/ (svn checkout http://python-nosexml.googlecode.com/svn/trunk/ nosexml && cd nosexml && python setup.py develop)
		'mandy',
		'snakefood',
		'termstyle',
	],
)
