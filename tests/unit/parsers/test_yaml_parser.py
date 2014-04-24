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

from pmcf.parsers import yaml_parser
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

    def test_parse_valid_config(self):
        struct = {
            'foo': {
                'bar': [1, 'three'],
                'baz': True
            }
        }

        config = """
            foo:
                bar:
                  - 1
                  - three
                baz: true
        """
        parser = yaml_parser.YamlParser()
        data = parser.parse(config)
        assert_equals(data, struct)

    def test_parse_invalid_config(self):
        config = """
            foo:
            - one
                bar:
                  - 1
                  - three
        """
        parser = yaml_parser.YamlParser()
        assert_raises(ParserFailure, parser.parse, config)
