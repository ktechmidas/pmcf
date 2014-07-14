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

Strategy
********

The strategy classes in pmcf are responsible for instrumenting the output
layers by responding to method calls with an answer about whether to proceed,
prompt, or abort when faced with decisions about updates and deletes to
stacks.

The strategy module is selected by adding this to your stack definition::

    strategy: PromptInPlace


:mod:`pmcf.strategy.base_strategy`
==================================

.. automodule:: pmcf.strategy.base_strategy
    :noindex:
    :members: __all__
    :undoc-members:


.. autoclass:: BaseStrategy
    :members:
    :undoc-members:


:mod:`pmcf.strategy.bluegreen`
==============================

.. automodule:: pmcf.strategy.bluegreen
    :noindex:
    :members: __all__
    :undoc-members:


.. autoclass:: BlueGreen
    :members:
    :undoc-members:
    :show-inheritance:

:mod:`pmcf.strategy.inplace`
============================

.. automodule:: pmcf.strategy.inplace
    :noindex:
    :members: __all__
    :undoc-members:


.. autoclass:: InPlace
    :members:
    :undoc-members:
    :show-inheritance:

:mod:`pmcf.strategy.prompt_inplace`
===================================

.. automodule:: pmcf.strategy.prompt_inplace
    :noindex:
    :members: __all__
    :undoc-members:


.. autoclass:: PromptInPlace
    :members:
    :undoc-members:
    :show-inheritance:

