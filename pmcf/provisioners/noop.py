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
..  module:: pmcf.provisioners.noop
    :platform: Unix
    :synopsis: module containing noop provisioner class

..  moduleauthor:: Stephen Gran <stephen.gran@piksel.com>
"""

import logging

from pmcf.provisioners.base_provisioner import BaseProvisioner

LOG = logging.getLogger(__name__)


class NoopProvisioner(BaseProvisioner):
    """
    Noop Provisioner class

    This class assembles userdata suitable for use by cloud-init, but does
    nothing.
    """

    def userdata(self, args):
        """
        Returns no userdata.

        :param args: provisioner arguments
        :type args: dict.
        :returns: None.
        """

        return None


__all__ = [
    'NoopProvisioner',
]
