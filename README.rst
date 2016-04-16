Autonose
========

.. image:: http://gfxmonk.net/dist/status/project/autonose.png

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
watchdog using ``easy_install``, as it needs to compile a native extension which
isn't included in the 0install package.

Advanced use:
-------------

nosetests has a lot of options and plugins. autonose tries to work as best
it can with them, but be warned that some plugins will interfere with autonose
(particularly any that do their own output or manage test results).

However, you can pass any options you want to nose by prefixing them with ``-x``,
or by using ``--config=nose.cfg`` if you have a config file.
(e.g. to turn on doctest, you should pass ``-x--with-doctest`` to autonose)

Notes:
------

Autotest does not (currently):

- understand dynamic imports (use of ``__import__``)
- track any file types other than ``.py``

