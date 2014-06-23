Developing PMCF
---------------

Developers wishing to work on the Piksel Managed Cloud Framework
should always base their work on the latest code, available from
the master GIT repository at:

   http://gitlab.piksel.com/pmcf/python-pmcf

Creating Unit Tests
-------------------
For every new feature, unit tests should be created that both test and
(implicitly) document the usage of said feature. If submitting a patch for a
bug that had no unit test, a new passing unit test should be added. If a
submitted bug fix does have a unit test, be sure to add a new one that fails
without the patch and passes with the patch.

Running Tests
-------------
The test harness runs in a python virtual environment to avoid polluting
the normal python environment.  In order to install the python libraries in
the venv, it is necessary to install a few packages:
``apt-get install build-essential python-virtualenv python-tox python-dev libyaml-dev``

The testing system is based on python nosetools.  Simply run the command
``./run_tests.sh``
If you have not already created a venv, this script will do so on the first
run.

To create or update the virtual environment and populate it with the
dependencies necessary to run tests and builds of the software, run
``./tools/install_venv.sh -f``
This can be run independently of running the test suite to refresh the venv

To run the script without installing dependencies on your system (that is,
purely from the venv), do the following:

* Create a local config file (and optionally policy file):
  * cp tests/data/etc/pmcf.conf .local
  * $EDITOR .local/pmcf.conf - adjust to suit your needs
  * echo '{}' > .local/policy.json

* Run with your local config:
  * PYTHONNPATH=. tools/with_venv.sh python pmcf/cli/cli.py -v \
    -c .local/pmcf.conf -P .local/policy.json \
    -p sequoia -e infra --poll buildhelper.yaml
