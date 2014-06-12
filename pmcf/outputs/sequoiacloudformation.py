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
..  module:: pmcf.outputs.sequoiacloudformation
    :platform: Unix
    :synopsis: module containing Sequoia output class for PMCF

..  moduleauthor:: Stephen Gran <stephen.gran@piksel.com>
"""

import logging

from pmcf.exceptions import ProvisionerException
from pmcf.outputs.cloudformation import AWSCFNOutput

LOG = logging.getLogger(__name__)


class SequoiaAWSCFNOutput(AWSCFNOutput):
    """
    Sequoia-specific output class.

    Subclasses the AWS output class, and overlays it with a Sequoia specific
    tagging policy.
    """

    def run(self, data, metadata={}):
        """
        Interfaces with public and private cloud providers.

        Sequoia-specific overlay.  Add Sequoia tags and invokes parent class
        method.

        :param data: Stack definition
        :type data: str.
        :param metadata: Additional information for stack launch (tags, etc).
        :type metadata: dict.
        :raises: :class:`pmcf.exceptions.ProvisionerException`
        :returns: boolean
        """

        try:
            metadata['tags'] = {
                'Stack': metadata['name'],
                'Stage': metadata['stage'],
            }
        except KeyError, e:
            raise ProvisionerException(str(e))

        metadata['name'] = "%s-%s" % (metadata['name'], metadata['stage'])

        return super(self.__class__, self).run(data, metadata)


__all__ = [
    SequoiaAWSCFNOutput,
]
