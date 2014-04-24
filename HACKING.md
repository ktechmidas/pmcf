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
To create virtual environments and populate them with the dependencies
necessary to run tests and builds of the software, run
``./tools/install_venv.sh``

The testing system is based on python nosetools.  Once you have a virtualenv
created,The approach to running tests is to simply run the command
``./run_tests.sh``

