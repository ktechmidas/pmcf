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

Queue Schema
============

The schema for queues is, like the other parts of the schema,
composed from smaller building blocks to make a larger whole.

The basic format of a security group is:

:name:
        The name of the queue

:retention:
        Default message retention period for the queue

**Example**

::

  ---
  config: {}
  resources:
    queue:
      - name: test
        retention: 60
