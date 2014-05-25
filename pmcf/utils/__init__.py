# Copyright (c) 2014 Piksel
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import logging

from pmcf.exceptions import PropertyException

LOG = logging.getLogger(__name__)


def import_from_string(module, klass):
    try:
        mod = __import__(module, fromlist=[klass])
        return getattr(mod, klass)
    except AttributeError, e:
        raise PropertyException(e.message)


def error(resource, msg):
    res_type = getattr(resource, 'type', '<unknown type>')
    msg += ' in type %s' % res_type
    res_title = getattr(resource, 'title', None)
    if res_title:
        msg += ' (%s)' % res_title

    raise PropertyException(msg)


__all__ = [
    error,
    import_from_string,
]
