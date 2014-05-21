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

import logging
import os
import sys

from pmcf.exceptions import PMCFException
from pmcf.utils import import_from_string

LOG = logging.getLogger(__name__)


class PMCFCLI(object):
    def __init__(self, args):

        self.parser = import_from_string('pmcf.parsers', args['parser'])()
        self.policy = import_from_string('pmcf.policy', args['policy'])(
            json_file=args['policyfile']
        )
        self.provisioner = import_from_string('pmcf.provisioners',
                                              args['provisioner'])()
        self.output = import_from_string('pmcf.outputs',
                                         args['output'])()
        self.args = args

    def run(self):
        try:
            self.parser.parse_file(self.args['stackfile'])
            for k, v in self.parser._stack['resources'].iteritems():
                for idx, res in enumerate(v):
                    data = self.parser._stack['resources'][k][idx]
                    self.policy.validate_resource(k, data)
            data = self.output.add_resources(self.provisioner,
                                             self.parser._stack['resources'],
                                             self.parser._stack['config'])

            metadata = {
                'access': os.environ['AWS_ACCESS_KEY_ID'],
                'secret': os.environ['AWS_SECRET_ACCESS_KEY'],
                'region': 'us-west-2',
                'name': self.parser._stack['config']['name']
            }
            self.output.run(data, metadata)
            return False
        except PMCFException, e:
            LOG.error(e.message)
            return True


__all__ = [
    PMCFCLI,
]
