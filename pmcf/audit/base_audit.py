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
..  module:: pmcf.audit.base_audit
    :platform: Unix
    :synopsis: module containing abstract base audit classes

..  moduleauthor:: Stephen Gran <stephen.gran@piksel.com>
"""

import abc
import logging

LOG = logging.getLogger(__name__)


class BaseAudit(object):
    """
    Abstract base class for audit classes.

    The PMCF Audit classes are responsible for transparently logging an audit
    trail of stack updates and creations.

    Only provides an interface, and can not be used directly
    """

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def record_stack(self, stack, destination, credentials):
        """
        Abstract base method providing a signature.  Can not be used directly

        In implementation classes, this is the method that would record an
        audit log.

        :param stack: stack definition
        :type stack: str.
        :param destination: destination to copy stack to
        :type destination: str.
        :param credentials: credentials for copy command
        :type credentials: dict.
        :returns:  boolean
        :raises: :class:`NotImplementedError`
        """

        raise NotImplementedError


__all__ = [
    'BaseAudit',
]
