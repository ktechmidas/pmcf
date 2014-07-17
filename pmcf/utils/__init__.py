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

"""
..  module:: pmcf.utils
    :platform: Unix
    :synopsis: module containing utility functions

..  moduleauthor:: Stephen Gran <stephen.gran@piksel.com>
"""

import curses
import difflib
import json
import logging
import os
import sys

from pmcf.exceptions import PropertyException

LOG = logging.getLogger(__name__)


def import_from_string(module, klass):
    """
    Imports a class from the string representation.  Used to autoload
    implementation classes based on configuration parameters.

    :param module: Name of module
    :type module: str.
    :param klass: Name of class
    :type klass: str.
    :raises: :class:`pmcf.exceptions.PropertyException`
    :returns: object
    """

    try:
        mod = __import__(module, fromlist=[klass])
        return getattr(mod, klass)
    except AttributeError, e:
        raise PropertyException(e.message)


def init_error(msg, res_type, res_title):
    """
    Wrapper for common resource error messages

    :param resource: Resource raising exception
    :type resource: object.
    :param msg: Error message
    :type msg: str.
    :raises: :class:`pmcf.exceptions.PropertyException`
    """

    msg += ' in type %s' % res_type
    if res_title:
        msg += ' (%s)' % res_title
    raise PropertyException(msg)


def error(resource, msg):
    """
    Wrapper for common resource error messages

    :param resource: Resource raising exception
    :type resource: object.
    :param msg: Error message
    :type msg: str.
    :raises: :class:`pmcf.exceptions.PropertyException`
    """

    res_type = getattr(resource, 'type', '<unknown type>')
    res_title = getattr(resource, 'title', None)
    init_error(msg, res_type, res_title)


def colourise_output(start, line, end='reset'):
    # Simple coloured output

    if isinstance(sys.stdout, file):
        if not os.isatty(sys.stdout.fileno()):
            return line

    if colourise_output.init == 0:
        curses.setupterm()
        colourise_output.init = 1

    COLOURS = {
        'reset': curses.tparm(curses.tigetstr('op')),
        'red': curses.tparm(curses.tigetstr('setaf'),
                            curses.COLOR_RED),
        'green': curses.tparm(curses.tigetstr('setaf'),
                              curses.COLOR_GREEN),
        'yellow': curses.tparm(curses.tigetstr('setaf'),
                               curses.COLOR_YELLOW),
        'cyan': curses.tparm(curses.tigetstr('setaf'),
                             curses.COLOR_CYAN),
    }

    return COLOURS[start] + line + COLOURS[end]
colourise_output.init = 0


def make_diff(old, new):
    """
    Creates coloured diff output from 2 strings.

    :param old: String to diff from
    :type old: str.
    :param new: String to diff to
    :type new: str.
    :returns: str.
    """

    ret = ''
    old_data = json.loads(old)
    new_data = json.loads(new)
    if old_data == new_data:
        return ret

    old = json.dumps(old_data, indent=4, sort_keys=True)
    new = json.dumps(new_data, indent=4, sort_keys=True)

    diff = list(difflib.unified_diff(old.splitlines(1),
                                     new.splitlines(1),
                                     fromfile='LiveTemplate',
                                     tofile='NewTemplate',
                                     n=100000))
    for line in diff:
        if line.startswith('-'):
            ret += colourise_output('red', line)
        elif line.startswith('+'):
            ret += colourise_output('green', line)
        else:
            ret += line
    return ret


__all__ = [
    colourise_output,
    error,
    init_error,
    import_from_string,
    make_diff,
]
