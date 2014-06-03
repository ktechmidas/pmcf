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

import difflib
import json
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


def sort_json(string_data):
    ret = ''
    data = json.loads(string_data)
    if isinstance(data, dict):
        ret += "{"
        for k in sorted(data.keys()):
            ret += json.dumps(k) + ": "
            ret += sort_json(json.dumps(data[k]))
            ret += ", "
        ret = ret[:-2]
        ret += "}"
    elif isinstance(data, list):
        ret += "["
        for k in data:
            ret += sort_json(json.dumps(k))
            ret += ", "
        ret = ret[:-2]
        ret += "]"
    else:
        ret += json.dumps(data)
    return ret


def make_diff(old, new):
    ret = ''
    old_data = json.loads(old)
    new_data = json.loads(new)
    if old_data == new_data:
        return ret

    COLORS = {
        'reset': '\x1b[0m',
        'red': '\x1b[31m',
        'green': '\x1b[32m',
    }

    def _colourise(start, line, end='reset'):
        return COLORS[start] + line + COLORS[end]

    old = sort_json(old)
    old = json.dumps(json.loads(old), indent=4)
    new = json.dumps(json.loads(new), indent=4)

    d = difflib.Differ()
    diff = list(d.compare(old.splitlines(1), new.splitlines(1)))
    for line in diff:
        if line.startswith('-'):
            ret += _colourise('red', line)
        elif line.startswith('+'):
            ret += _colourise('green', line)
        else:
            ret += line
    return ret


__all__ = [
    error,
    import_from_string,
    make_diff,
    sort_json,
]
