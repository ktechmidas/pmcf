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

Outputs
*******

The output classes in pmcf are used to transform the internal data structure
into an interface with outside services.  Some, such as the JSONOutput class,
only prints the output, while others, such as the AWSCloudFormation class,
will provision or update a new stack in AWS.

The output module is selected by adding this to your config file::

    output = C4AWSCFNOutput


Available outputs libraries
==============================


:mod:`pmcf.outputs.base_output`
-------------------------------

.. automodule:: pmcf.outputs.base_output
    :noindex:
    :members: __all__
    :undoc-members:


.. autoclass:: BaseOutput
    :members:
    :undoc-members:
    :show-inheritance:


:mod:`pmcf.outputs.c4cloudformation`
------------------------------------

.. automodule:: pmcf.outputs.c4cloudformation
    :noindex:
    :members: __all__
    :undoc-members:


.. autoclass:: C4AWSCFNOutput
    :members:
    :undoc-members:
    :show-inheritance:


:mod:`pmcf.outputs.cloudformation`
----------------------------------

.. automodule:: pmcf.outputs.cloudformation
    :noindex:
    :members: __all__
    :undoc-members:


.. autoclass:: AWSCFNOutput
    :members:
    :undoc-members:
    :show-inheritance:


:mod:`pmcf.outputs.json_output`
-------------------------------

.. automodule:: pmcf.outputs.json_output
    :noindex:
    :members: __all__
    :undoc-members:


.. autoclass:: JSONOutput
    :members:
    :undoc-members:
    :show-inheritance:


:mod:`pmcf.outputs.sequoiacloudformation`
-----------------------------------------

.. automodule:: pmcf.outputs.sequoiacloudformation
    :noindex:
    :members: __all__
    :undoc-members:


.. autoclass:: SequoiaAWSCFNOutput
    :members:
    :undoc-members:
    :show-inheritance:
