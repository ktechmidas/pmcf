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

Parsers
*******

The parsers classes in pmcf are responsible for reading stack definitions and
producing an internal data structure that can then be validated against the
schema classes.

The parser module is selected by adding this to your config file::

    parsers = AWSFWParser


Available parsers libraries
===========================


:mod:`pmcf.parsers.awsfw_parser`
--------------------------------

.. automodule:: pmcf.parsers.awsfw_parser
    :noindex:
    :members: __all__
    :undoc-members:


.. autoclass:: AWSFWParser
    :members:
    :undoc-members:
    :show-inheritance:


:mod:`pmcf.parsers.base_parser`
-------------------------------

.. automodule:: pmcf.parsers.base_parser
    :noindex:
    :members: __all__
    :undoc-members:


.. autoclass:: BaseParser
    :members:
    :undoc-members:
    :show-inheritance:


:mod:`pmcf.parsers.yaml_parser`
--------------------------------

.. automodule:: pmcf.parsers.yaml_parser
    :noindex:
    :members: __all__
    :undoc-members:


.. autoclass:: YamlParser
    :members:
    :undoc-members:
    :show-inheritance:
