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
..  module:: pmcf.provisioners.block
    :platform: Unix
    :synopsis: module containing blocking provisioner class

..  moduleauthor:: Stephen Gran <stephen.gran@piksel.com>
"""

import logging
from troposphere import Join, Ref

from pmcf.provisioners.base_provisioner import BaseProvisioner

LOG = logging.getLogger(__name__)


class BlockingProvisioner(BaseProvisioner):

    def userdata(self, args):
        """
        Signals wait condition at end of boot cycle

        :param args: provisioner arguments
        :type args: dict.
        :returns: str.
        """

        script = [
            '#!/bin/bash\n',
            'apt-get -y install python-setuptools\n',
            'easy_install https://s3.amazonaws.com/cloudformation-examples/',
            'aws-cfn-bootstrap-latest.tar.gz\n',
            'cfn-signal -e 0 -r Success \'',
            Ref(args['WaitHandle']),
            '\'\n',
        ]

        return Join('', script)

    def wants_wait(self):
        """
        Whether a provisioner implementation wants a wait condition created

        :returns: boolean.
        """

        return True


__all__ = [
    BlockingProvisioner,
]
