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

import sys

from pmcf.exceptions import PMCFException
from pmcf.utils import import_from_string


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
            with open(self.args['stackfile']) as fd:
                self.parser.parse(fd.read())
            for k, v in self.parser._stack['resources'].iteritems():
                for idx, res in enumerate(v):
                    data = self.parser._stack['resources'][k][idx]
                    self.policy.validate_resource(k, data)
            data = self.output.add_resources(self.provisioner,
                                             self.parser._stack['resources'],
                                             self.parser._stack['config'])
            self.output.run(data)
            return False
        except PMCFException, e:
            print >> sys.stderr, e.message
            return True


__all__ = [
    PMCFCLI,
]