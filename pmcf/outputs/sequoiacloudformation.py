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
    :synopsis: module containing Sequoia output class

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

    def run(self, data, metadata=None, poll=False,
            action='create', upload=True):
        """
        Interfaces with public and private cloud providers.

        Sequoia-specific overlay.  Add Sequoia tags and invokes parent class
        method.

        :param data: Stack definition
        :type data: str.
        :param metadata: Additional information for stack launch (tags, etc).
        :type metadata: dict.
        :param poll: Whether to poll until completion
        :type poll: boolean.
        :param action: Action to take on the stack
        :type action: str.
        :param upload: Whether to upload stack definition to s3 before launch
        :type upload: bool.
        :raises: :class:`pmcf.exceptions.ProvisionerException`
        :returns: boolean
        """

        metadata = metadata or {}
        try:
            metadata['tags'] = {
                'Stack': metadata['name'],
                'Stage': metadata['environment'],
            }
        except KeyError, exc:
            raise ProvisionerException(str(exc))

        metadata['name'] = "%s-%s" % (metadata['name'],
                                      metadata['environment'])

        return super(self.__class__, self).run(data, metadata, poll,
                                               action, upload)


__all__ = [
    'SequoiaAWSCFNOutput',
]
