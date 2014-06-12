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

Policy
******

The policy classes in pmcf are responsible for providing defaults and
restrictions on resource usage in stack definitions.

The policy module is selected by adding this to your config file::

    policy = JSONPolicy


Available policy libraries
==========================


:mod:`pmcf.policy.base_policy`
------------------------------

.. automodule:: pmcf.policy.base_policy
    :noindex:
    :members: __all__
    :undoc-members:


.. autoclass:: BasePolicy
    :members:
    :undoc-members:
    :show-inheritance:


:mod:`pmcf.policy.json_policy`
------------------------------

.. automodule:: pmcf.policy.json_policy
    :noindex:
    :members: __all__
    :undoc-members:


.. autoclass:: JSONPolicy
    :members:
    :undoc-members:
    :show-inheritance:
