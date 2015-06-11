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
..  module:: pmcf.audit.noop_audit
    :platform: Unix
    :synopsis: module containing noop audit class

..  moduleauthor:: Stephen Gran <stephen.gran@piksel.com>
"""

import logging

from pmcf.audit.base_audit import BaseAudit

LOG = logging.getLogger(__name__)


class NoopAudit(BaseAudit):
    """
    Noop audit class.  Does not perform any audit actions, only implements
    interface.
    """

    def record_stack(self, stack, destination, credentials):
        """
        Noop implementation of interface.  Does nothing successfully.

        :param stack: stack definition
        :type stack: str.
        :param destination: destination to copy stack to
        :type destination: str.
        :param credentials: credentials for copy command
        :type credentials: dict.
        :returns:  boolean
        """

        LOG.info('Not actually recording stack to %s', destination)
        return True


__all__ = [
    'NoopAudit',
]
