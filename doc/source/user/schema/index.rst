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


Schema for stacks
=================

The internal schema validation in PMCF relies on the `Draft 4 JSON Schema
<http://json-schema.org/>`_.

The top level schema is composed of two keys:

:config:
        This is a dictionary of key-value information that applies to the
        stack as a whole

:resources:
        These are the instances, security groups, load balancers, and so on
        that comprise the stack.

**Example minimum valid config**

::

  ---
  config: {}
  resources:
    cdn: []
    db: []
    instance: []
    loadbalancer: []
    secgroup: []


Schemas for individual resources
--------------------------------
.. toctree::
   :maxdepth: 1

   instance
   loadbalancer
   network
   secgroup
   queue
