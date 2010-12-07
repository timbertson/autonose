#!/usr/bin/env python

## NOTE: ##
## setup.py is not maintained, and is only provided for convenience.
## please see http://gfxmonk.net/dist/0install/index/ for
## up-to-date installable packages.

from setuptools import *
setup(
	name='autonose',
	version='0.1.6',
	author_email='tim3d.junk+autonose@gmail.com',
	author='Tim Cuthbertson',
	url='http://gfxmonk.net/dist/0install/autonose.xml',
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
		'snakefood',
		'python-termstyle',
	],
)
