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

import boto
import logging

from pmcf.exceptions import ProvisionerException
from pmcf.outputs.json_output import JSONOutput

LOG = logging.getLogger(__name__)


class AWSCFNOutput(JSONOutput):

    def run(self, data, metadata={}):
        if metadata.get('region', None) is None:
            raise ProvisionerException('Need to supply region in metadata')

        cfn = None
        for region in boto.regioninfo.get_regions('cloudformation'):
            if region.name == metadata['region']:
                cfn = boto.connect_cloudformation(
                    aws_access_key_id=metadata['access'],
                    aws_secret_access_key=metadata['secret'],
                    region=region
                )
        if cfn is None:
            raise ProvisionerException("Can't find a valid region")

        tags = {}
        if metadata.get('tags'):
            tags = metadata['tags']

        try:
            cfn.create_stack(metadata['name'], data, tags=tags)
        except Exception, e:
            raise ProvisionerException(str(e))

        return True


__all__ = [
    AWSCFNOutput,
]
