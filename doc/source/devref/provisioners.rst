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

Provisioners
************

The provisioners classes in pmcf provide config management hooks when used in
combination with outputs that run against public clouds implementing a
metadata endpoint suitable for consumption by
`cloud-init <http://cloudinit.readthedocs.org/en/latest/>`_.


Available provisioners libraries
================================


:mod:`pmcf.provisioners.awsfw`
------------------------------

.. automodule:: pmcf.provisioners.awsfw
    :noindex:
    :members: __all__
    :undoc-members:


.. autoclass:: AWSFWProvisioner
    :members:
    :undoc-members:
    :show-inheritance:


:mod:`pmcf.provisioners.base_provisioner`
-----------------------------------------

.. automodule:: pmcf.provisioners.base_provisioner
    :noindex:
    :members: __all__
    :undoc-members:


.. autoclass:: BaseProvisioner
    :members:
    :undoc-members:
    :show-inheritance:


:mod:`pmcf.provisioners.puppet`
-------------------------------

.. automodule:: pmcf.provisioners.puppet
    :noindex:
    :members: __all__
    :undoc-members:


.. autoclass:: PuppetProvisioner
    :members:
    :undoc-members:
    :show-inheritance:
