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

from pmcf.provisioners.base_provisioner import BaseProvisioner

import logging

LOG = logging.getLogger(__name__)


class AWSFWProvisioner(BaseProvisioner):

    def userdata(self, config):
        ud = self.make_skeleton()

        with open('scripts/awsfw/part-handler') as fd:
            ud = self.add_data(ud, fd.read(),
                               'part-handler', 'part-handler')

        awsfw_data = ''
        for k, v in config.iteritems():
            awsfw_data += 'export %s=%s\n' % (k, v)

        ud = self.add_data(ud, awsfw_data, 'awsfw-data', 'vars')

        with open('scripts/awsfw/s3curl.pl') as fd:
            ud = self.add_data(ud, fd.read(),
                               'x-s3curl', 's3curl.pl')
        with open('scripts/awsfw/awsfw_standalone') as fd:
            ud = self.add_data(ud, fd.read(),
                               'x-shellscript', 'awsfw_standalone')

        return self.resize(ud)


__all__ = [
    AWSFWProvisioner,
]
