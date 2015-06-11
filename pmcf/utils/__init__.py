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
from netaddr import IPNetwork
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
    except AttributeError, exc:
        raise PropertyException(exc.message)


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


def do_init(obj, title, prop=False, template=None, **kwargs):
    """
    Wrapper for common init methods in helper classes

    :param obj: Object calling init method
    :type obj: object.
    :param title: Name of object resource
    :type title: string.
    :param kwargs: Arguments to pass to obj's init
    :type title: parameters.
    :raises: :class:`pmcf.exceptions.PropertyException`
    """

    try:
        if prop:
            super(obj.__class__, obj).__init__(title, **kwargs)
        else:
            super(obj.__class__, obj).__init__(title, template, **kwargs)
    except (TypeError, ValueError, AttributeError), exc:
        init_error(exc.message, obj.__class__.__name__, title)


def do_json(obj):
    """
    Wrapper for common calls to JSONrepr()

    :param obj: Object calling init method
    :type resource: object.
    :raises: :class:`pmcf.exceptions.PropertyException`
    """

    try:
        return super(obj.__class__, obj).JSONrepr()
    except ValueError, exc:
        error(obj, exc.message)


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


def is_term():
    """
    Wrapper method to determine if stdout looks like it is on a terminal

    :returns: bool.
    """

    if hasattr(sys.stdout, 'fileno'):
        return os.isatty(sys.stdout.fileno())
    return False


def colourise_output(start, line, end='reset'):
    """
    Wrapper method to return colourised output when running in a terminal.

    :param start: One of 'red', 'green', 'yellow' or 'cyan'
    :type start: str.
    :param line: Text to be colourised.
    :type line: str.
    :param end: Typically, 'reset' to clear the colourisation.
    :type end: str.
    :returns: str.
    """
    # Simple coloured output

    if not is_term():
        return line

    if colourise_output.init == 0:
        curses.setupterm()
        colourise_output.init = 1

    colours = {
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

    return colours[start] + line + colours[end]
colourise_output.init = 0


def get_changed_keys_from_templates(old, new):
    """
    Returns a list of changed keys in two templates

    :param old: String to diff from
    :type old: str.
    :param new: String to diff to
    :type new: str.
    :returns: list.
    """

    ret = []
    old_data = json.loads(old)
    new_data = json.loads(new)
    if old_data == new_data:
        return ret
    ret = valchange(old_data, new_data)
    ret.extend(valchange(new_data, old_data))
    return list(set(ret))


def valchange(old, new, parent=''):
    """
    Returns a list of changed keys in two dictionaries

    :param old: dict to diff from
    :type old: dict.
    :param new: dict to diff to
    :type new: dict.
    :returns: list.
    """

    changes = []
    for k in old.keys():
        if parent == '':
            display_key = k
        else:
            display_key = '%s.%s' % (parent, k)

        if k not in new.keys():
            changes.append(display_key)
            continue
        if isinstance(old[k], dict):
            changes.extend(valchange(old[k], new[k], display_key))
        else:
            if old[k] != new[k]:
                changes.append(display_key)

    return changes


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


def split_subnets(cidr, split):
    """
    Finds the nearest power of two to the number of desired subnets,
    Splits a CIDR into that many sub CIDRs, and returns the array.

    :param cidr: CIDR for entire range
    :type cidr: str.
    :param split: Number to split into
    :type split: int.
    :raises: :class:`pmcf.exceptions.PropertyException`
    :returns: list.
    """

    # Find the next closest power of two to a number
    # For 3, return 4, for 5 return 8

    if split == 1:
        return [cidr]

    power = 0
    while split > 0:
        split >>= 1
        power += 1

    try:
        ipaddr = IPNetwork(cidr)
        prefix = ipaddr.prefixlen
        newprefix = prefix + power
        return list(ipaddr.subnet(newprefix))
    except Exception, exc:
        raise PropertyException(str(exc))


__all__ = [
    'colourise_output',
    'error',
    'get_changed_keys_from_templates',
    'import_from_string',
    'init_error',
    'is_term',
    'make_diff',
    'split_subnets',
    'valchange',
]
