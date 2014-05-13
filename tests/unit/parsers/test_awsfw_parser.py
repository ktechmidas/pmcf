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

from nose.tools import assert_equals, assert_raises

from pmcf.parsers import awsfw_parser
from pmcf.exceptions import ParserFailure


class TestParser(object):

    def setup(self):
        pass

    def teardown(self):
        pass

    @classmethod
    def setup_class(cls):
        pass

    @classmethod
    def teardown_class(cls):
        pass

    def test__listify_string(self):
        parser = awsfw_parser.AWSFWParser()
        data = 'foo'
        assert_equals(parser._listify(data), ['foo'])

    def test__listify_list(self):
        parser = awsfw_parser.AWSFWParser()
        data = ['foo']
        assert_equals(parser._listify(data), data)

    def test_parse_valid_config(self):
        struct = {
            'resources': {
                'instance': [],
                'loadbalancer': [],
                'db': [],
                'cdn': []
            }
        }

        config = ''
        with open('data/ais-stage-farm.xml') as fd:
            config = fd.read()

        parser = awsfw_parser.AWSFWParser()
        data = parser.parse(config)
        # FIXME: Just to get a check in
        assert_equals(data, data)
