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
    :synopsis: module containing AWSFW implementation of provisioner class

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

    _provides = 'awsfw_standalone'

    def userdata(self, config, args):
        """
        Validates resource against local policy.

        :param config: Config items for userdata
        :type config: dict.
        :param args: instance definition
        :type args: dict.
        :raises: :class:`pmcf.exceptions.ProvisionerException`
        :returns: str.
        """

        ud = self.make_skeleton()

        ud = self.add_file(ud, 'scripts/awsfw/part-handler')
        ud = self.add_file(ud, 'scripts/awsfw/s3curl.pl', 'x-s3curl', False)

        config['roles'] = ','.join(args['roles'])
        config['rolebucket'] = args['roleBucket']
        config['apps'] = ','.join(args['apps'])
        config['appbucket'] = args['appBucket']
        config['instantiatedby'] = 'create-farm'

        awsfw_data = ''
        for k, v in config.iteritems():
            awsfw_data += 'export %s=%s\n' % (k, v)

        ud = self.add_data(ud, awsfw_data, 'vars')
        ud = self.add_file(ud, 'scripts/awsfw/bootstrap.sh', compress=True)

        return self.resize(ud)


__all__ = [
    AWSFWProvisioner,
]
