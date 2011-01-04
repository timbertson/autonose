# Autonose

Autonose is an autotest-like tool for python, using the excellent nosetest
library.

Features:

 - Re-run tests instantly when you save a file
 - Re-runs only tests that have failed or depend on changed files
 - GTK GUI (console fallback for other platforms or by passing in --console)
 - focus mode: keep running a single test (GUI only)

To activate focus mode, click the large grey circle next to the test result.
To go back to normal mode, click the "#" in the status bar (next to the
number of tests run).

Note: on a Mac, to get immediate filesystem notification you may need to install
watchdog using `easy_install`, as it needs to compile a native extension which
isn't included in the 0install package.

## Installation:

The officially supported installation mechanism is zero install. You will
need the zeroinstall-injector package (from apt, yum, macports, etc.) or
[your platform's equivalent](http://zero-install.sourceforge.net/injector.html).

To launch it, simply run:

	$ 0launch http://gfxmonk.net/dist/0install/autonose.xml

You can also use 0alias to make a short name for it:

	$ 0alias http://gfxmonk.net/dist/0install/autonose.xml autonose
	$ autonose

If you have modified the code, you will want to create a local feed to run:

	$ 0launch http://gfxmonk.net/dist/0install/0local.xml autonose.xml
	$ 0launch autonose-local.xml

See http://gfxmonk.net/dist/0install/autonose.xml for further deatils.

## Advanced use:

nosetests has a lot of options and plugins. autonose tries to work as best
it can with them, but be warned that some plugins will interfere with autonose
(particularly any that do their own output or manage test results).

However, you can pass any options you want to nose by prefixing them with `-x`,
or by using `--config=nose.cfg` if you have a config file.
(e.g. to turn on doctest, you should pass `-x--with-doctest` to autonose)

## Notes:

Autotest does not (currently):

 - understand dynamic imports (use of `__import__`)
 - track any file types other than `.py`

