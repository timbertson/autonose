# Autonose

Autonose is an autotest-like tool for python, using the excellent nosetest
library.

autotest tracks filesystem changes and automatically re-run
any changed tests or dependencies whenever a file is added, removed or
updated. A file counts as changed if it has iself been modified, or if any
file it `import`s has changed.

## Using it:

	$ easy_install autonose
	autonose

It's really that simple. try `autonose --help` for configuration options.

**note**: if you can't find the nosexml dependency, you may need to:

	svn checkout http://python-nosexml.googlecode.com/svn/trunk/ nosexml
	cd nosexml
	python setup.py develop

until nosexml 0.2 gets packaged properly


Autonose currently has a native GUI for OSX and GTK. If neither of those
are available to you, you can instead run the console version (with the
`--console` option).

Here's the obligatory screenshot of autonose in action:
![Autonose running on OSX](http://gfxmonk.net/upload/screenshot-autonose.png)

.. but the real magic happens when you have autonose running *while* modifying
your tests / code.


## Advanced use:

nosetests has a lot of options and plugins. autonose tries to work as best
it can with them, but be warned that some plugins will interfere with autonose
(particularly any that do their own output or manage test results).

However, you can pass any options you want to nose by prefixing them with `-x`,
or by using `--config=nose.cfg` if you have a config file.
(e.g. to turn on doctest, you should pass `-x--with-doctest` to autonose)

## Current Status

Autotest does not (currently):

 - understand dynamic imports (use of `__import__`)
 - track any file types other than `.py`
 - detect filesystem changes instantly (inotify-style). This is not an
   issue for small codebases, but could be for larger ones.

All of these points are at various stages of being worked on; see the github
issues page for the status on these (and many more!) enhancements.

