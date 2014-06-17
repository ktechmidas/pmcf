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
..  module:: pmcf.outputs.c4cloudformation
    :platform: Unix
    :synopsis: module containing Channel4 output class for PMCF

..  moduleauthor:: Stephen Gran <stephen.gran@piksel.com>
"""

import datetime
import logging

from pmcf.exceptions import ProvisionerException
from pmcf.outputs.cloudformation import AWSCFNOutput

LOG = logging.getLogger(__name__)


class C4AWSCFNOutput(AWSCFNOutput):
    """
    Channel4-specific output class.

    Subclasses the AWS output class, and overlays it with a Channel4 specific
    tagging policy.
    """

    def run(self, data, metadata={}, poll=False):
        """
        Interfaces with public and private cloud providers.

        Channel4-specific overlay.  Add Channel4 tags and invokes parent class
        method.

        :param data: Stack definition
        :type data: str.
        :param metadata: Additional information for stack launch (tags, etc).
        :type metadata: dict.
        :param poll: Whether to poll until completion
        :type poll: boolean.
        :raises: :class:`pmcf.exceptions.ProvisionerException`
        :returns: boolean
        """

        try:
            if metadata['environment'].lower() == 'prod':
                review_date = (datetime.date.today() +
                               datetime.timedelta(6*365/12)).isoformat()
            else:
                review_date = (datetime.date.today() +
                               datetime.timedelta(2*365/12)).isoformat()

            farmname = '-'.join(
                [metadata['name'],
                    metadata['environment'],
                    metadata['version']])

            metadata['tags'] = {
                'Project': metadata['name'],
                'Environment': metadata['environment'],
                'CodeVersion': metadata['version'],
                'Farm': farmname,
                'ReviewDate': review_date,
                'Owner': metadata['owner']
            }
        except KeyError, e:
            raise ProvisionerException(str(e))

        return super(self.__class__, self).run(data, metadata, poll)


__all__ = [
    C4AWSCFNOutput,
]
