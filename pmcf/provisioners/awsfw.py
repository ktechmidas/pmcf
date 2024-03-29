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
..  module:: pmcf.provisioners.awsfw
    :platform: Unix
    :synopsis: module containing AWSFW provisioner class

..  moduleauthor:: Stephen Gran <stephen.gran@piksel.com>
"""

import logging

from pmcf.provisioners.base_provisioner import BaseProvisioner

LOG = logging.getLogger(__name__)


class AWSFWProvisioner(BaseProvisioner):
    """
    AWSFW Provisioner class

    This class assembles userdata suitable for use by cloud-init, but in a
    backwards-compatible manner with the existing AWSFW standalone installer.
    """

    def userdata(self, args):
        """
        Validates resource against local policy.

        :param args: provisioner arguments
        :type args: dict.
        :raises: :class:`pmcf.exceptions.ProvisionerException`
        :returns: str.
        """

        userdata = self.make_skeleton()

        userdata = self.add_file(userdata, 'scripts/awsfw/part-handler',
                                 'part-handler', compress=False)
        userdata = self.add_file(userdata, 'scripts/awsfw/cloud-config',
                                 'cloud-config', compress=False)
        userdata = self.add_file(userdata, 'scripts/awsfw/s3curl.pl',
                                 'x-s3curl', compress=False)

        args['roles'] = ','.join(args['roles'])
        args['apps'] = ','.join(args['apps'])
        args['instantiatedby'] = 'create-farm'

        awsfw_data = ''
        for key, val in args.iteritems():
            awsfw_data += 'export %s=%s\n' % (key, val)

        userdata = self.add_data(userdata, awsfw_data, 'vars',
                                 'awsfw-data', compress=False)
        userdata = self.add_file(userdata, 'scripts/awsfw/bootstrap.sh',
                                 'x-shellscript', compress=False)

        return self.resize(userdata)


__all__ = [
    'AWSFWProvisioner',
]
