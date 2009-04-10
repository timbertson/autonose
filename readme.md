# sniffer - 'ze great plan:

Sniffer is to be a python autotest-like tool. pyautotest already exists, but
personally I've not had much luck with it, and by re-running everything all
the time, it doesn't really scale to larger projects.

The aim of sniffer is to be trustable - aside from some well known shortcomings,
it should be able to give you 100% confidence that its cached test results
are in fact the current state of your test base. It will accomplish this by
runtime coverage checking, to determine all possible files that could cause
the result of any given test to change.

Also, it should be quick. Ideally, it wouldn't have to poll for filesystem
changes, but until there is a reliable cross-platform solution for this it
can't be helped.

It will consist of a watcher, a runner, and a UI. There will be many UIs
possible, and I don't want to have to write them all. So the notification
system should be simple enough and well documented to enable others to
build on top of it.

It will depend on nosetests, because nosetests is awesome and ought to make
the watcher pretty simple. Also, it would be silly if to have `sniffer`
without a `nose` ;)

Here is the component breakdown:

### watcher (Nose plugin)

as every test file is run, capture

  - the code files touched (filter to within the current
    working directory, for simplicity)
  - the modification dates / fingerprint of all involved files
  - the number of passes/fails for this test file
  - the time taken for the test file
  - the reason (Exception class) and full report text for every non-success

These stats are to be kept up to date, and pickled whenever they change.
On startup run, the first priority is to determine the staleness of these
stats by checking file timestamps (or potentially checksums/hashes).

## Runner

behaviour:

  - poll for filesystem changes. this can be optimised by:
    - checking most recently modified files first
    - user input? This should force a re-test, not just a modtime check
      - maybe a user could even append the location of a modified
        file to some file/named pipe which sniffer is continually reading.
        Not that brilliant, but it allows for 3rd party os os-specififc
        extensions to easily inform sniffer of changed files
        (i.e a simple spotlight or inotify script)

  - when a file modification or deletion is detected:
    - if it's a test file, re-run it (ask nose for this;
      i.e see if it matches nose's regex for test file names)
    - re-run all tests that use this file (as tracked by the watcher).
      the order of tests run should be:
      - any test whose filename contains the modified filename base as a substring
        (i.e for `some_module.py`, `test_some_module.py` should run first).
        Shortest test filename wins
      - the test with the most failures
      - then sorted by time; shortest running tests first

  - when an additional file is detected:
    - run it (if it's a test)
    - run all tests that errored with an ImportError
    - (is there anything else to do?)

## UI:

  - At all times, current total test stats should be displayed (taken from the watcher).
    This means total number of tests, and total passes/failures/errors
  - When a rerun is in progess, the following information should be displayed:
    - a list of test files to be re-run (sorted by priority, and optionally truncated) - with total
    - the output of the current test run
    - names and details of failed tests
  - When no tests are currently being run, the output should show the full results of all failures.
    Full output of failed tests from the most-recently-run-files should be displayed first
    (or potentially last, depending on how the thing scrolls).

Perhaps this needs to be a real GUI, as the amount of information
required is beyond my feeble ncurses skills.

More than likely, this display should simply feed off the third party hooks below:

## Third party hooks:

 - nofication:
   - When a test is run on any file which previously had (or now has) errors
     (include the number of current vs previous failures)
   - When the number of failures reaches zero. (Fanfare?)

 - Current stats
   - Global: `(successes, errors, failures, skipped, to_be_run)`
     (`to_be_run` corresponds to files that have been modified but not yet tested)
   - Individual: `((file, test), report_text)` for all tests.
     Most likely `report_text` can be `None` for successful tests.
     The first tuple makes a unique key, so UI updates are made simple.
   - On initialisation, individual results should only be sent once files have been
     checked (i.e. once we know the files are as old as their corresponding results)

----

## Priorities:

1. watcher: plug into coverage module to detect tests run and which files they touch
2. runner: file modification tracking
3. runner: use watcher info to rerun tests
4. gui: basic terminal (curses) which basically just watches test run output,
   with a status line at the bottom
5. runner: prioritising of tests-to-run
6. hooks for third parties
7. GUI: cocoa? wx? gtk? tk? a ruddy AJAX page? so many options :/
8. file system polling addons, prioritised

## questions:

With the current setup, is there any way tests can slip through without being re-tested?

 - as long as the coverage stuff is solid and modules are simply included,
   it shouldn't be able to.
 - integration tests that run shell scripts, multiple processes,
   etc. are likely to slip through.
   - is there any point trying to watch for things like
     os.system or subprocess.Popen? probably not...

picking and de-pickling: as long as it's just data objects, it should be immune to code
changes. Should it all be just dicts and arrays, or is pickling rich object trees fine?

How should the third part notifications work? Should they be in-memory python modules,
or a file / named pipe? Maybe even a socket? The data doesn't need to be that rich, although
some abstraction for colours may be necessary in report outputs. Kinda sounds like a
html-or-xml format might be the best way for language neutrality.
Or maybe just html snippets within yaml ;)
