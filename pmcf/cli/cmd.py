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

from pmcf.exceptions import ParserFailure, PMCFException
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
            self.parser.parse_file(self.args['stackfile'], self.args)
            for k, v in self.parser.stack()['resources'].iteritems():
                for idx, res in enumerate(v):
                    data = self.parser.stack()['resources'][k][idx]
                    self.policy.validate_resource(k, data)
            data = self.output.add_resources(self.provisioner,
                                             self.parser.stack()['resources'],
                                             self.parser.stack()['config'])

            try:
                metadata = {
                    'access': self.args['accesskey'],
                    'secret': self.args['secretkey'],
                    'region': self.args['region'],
                    'name': self.parser.stack()['config']['name'],
                    'owner': self.parser.stack()['config']['owner'],
                    'stage': self.parser.stack()['config']['stage'],
                    'version': self.parser.stack()['config']['version'],
                }
            except KeyError, e:
                raise ParserFailure(str(e))

            self.output.run(data, metadata)
            return False
        except PMCFException, e:
            LOG.error(e.message)
            return True


__all__ = [
    PMCFCLI,
]
