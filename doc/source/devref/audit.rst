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

Audit
*****

The audit classes in pmcf are called at the end of the output run, which in
cases where pmcf is interfacing with a public cloud, will be at the end of
provisioning or updating a stack.

The audit module is selected by adding this to your config file::

    audit = S3Audit


:mod:`pmcf.audit.base_audit`
============================


.. automodule:: pmcf.audit.base_audit
    :members: __all__
    :noindex:
    :undoc-members:

.. autoclass:: BaseAudit
    :members:
    :undoc-members:


:mod:`pmcf.audit.noop_audit`
============================


.. automodule:: pmcf.audit.noop_audit
    :members: __all__
    :noindex:
    :undoc-members:

.. autoclass:: NoopAudit
    :members:
    :undoc-members:
    :show-inheritance:


:mod:`pmcf.audit.s3_audit`
==========================


.. automodule:: pmcf.audit.s3_audit
    :members: __all__
    :noindex:
    :undoc-members:

.. autoclass:: S3Audit
    :members:
    :undoc-members:
    :show-inheritance:
