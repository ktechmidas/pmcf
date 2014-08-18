..
      Copyright 2014 Piksel Ltd.

      Licensed under the Apache License, Version 2.0 (the "License"); you may
      not use this file except in compliance with the License. You may obtain
      a copy of the License at

          http://www.apache.org/licenses/LICENSE-2.0

      Unless required by applicable law or agreed to in writing, software
      distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
      WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
      License for the specific language governing permissions and limitations
      under the License.

.. _cli:

Command line arguments
=======================

positional arguments::

    stackfile             path to stack (farm) definition file

optional arguments::

    -h, --help            show this help message and exit
    -v, --verbose         set loglevel to verbose
    -d, --debug           set loglevel to debug
    -q, --quiet           set loglevel to quiet
    -e ENVIRONMENT, --environment ENVIRONMENT
                          run config for this environment
    -p PROFILE, --profile PROFILE
                          use config profile
    -P POLICYFILE, --policyfile POLICYFILE
                          alternate policy file
    -c CONFIGFILE, --configfile CONFIGFILE
                          alternate config file
    -a ACTION, --action ACTION
                          action (one of create, update, trigger or delete)
    --poll                poll until completion

Sample usage::

    pmcf -d -p c4-pml -a create -e stage stacks/ais-stage-001.xml
