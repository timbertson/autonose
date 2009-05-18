# Autonose - The Plan:

Autonose is to be a python autotest-like tool. pyautotest already exists, but
personally I've not had much luck with it, and by re-running everything all
the time, it doesn't really scale to larger projects.

The aim of autonose is to be trustable - aside from some well known shortcomings,
it should be able to give you high confidence that its cached test results
are in fact the current state of your test base. It will accomplish this by
runtime coverage checking, to determine all code files that could cause
the result of any given test to change.

Also, it should be quick. Ideally, it wouldn't have to poll for filesystem
changes, but until there is a reliable cross-platform solution for this it
can't be helped.

It will consist of a watcher, a runner, and a UI. There will be many UIs
possible, and I don't want to have to write them all. So the notification
system should be simple enough and well documented to enable others to
build on top of it.

It will depend on nosetests, because nosetests is awesome and ought to make
the watcher pretty simple.

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
        file to some file/named pipe which autonose is continually reading.
        Not that brilliant, but it allows for 3rd party os os-specififc
        extensions to easily inform autonose of changed files
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

1. [done] watcher: detect tests run and which files they touch
2. [done] runner: file modification tracking
3. [done] watcher: only rerun tests relevant to changed files
3. [done] runner: use watcher info to rerun tests
4. gui: basic terminal (curses) which basically just watches test run output,
   with a status line at the bottom
2. runner: *proper* file modification tracking (dynamic, instead of static)
5. runner: prioritising of tests-to-run
6. hooks for third parties
7. GUI: cocoa? wx? gtk? tk? a ruddy AJAX page? so many options :/
8. file system polling addons, prioritised

## Current limitations:

The watcher currently does not do any import detection. I tried it, but it seems very complicated
with lots of cases to cover. So for now, the scanner uses snakefood to statically determine
dependencies. Note that this will only cover "import blah" statements, it will *not* catch any uses
of the `__import__` function. Ultimately, I would like to use strace or something similar to determine
(at runtime) *every file* that is touched by the test process (and any subprocesses). This is
a big piece of work, so it will come after the rest of autonose has proven itself to be useful.
