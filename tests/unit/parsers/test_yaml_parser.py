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

import jsonschema
import mock
from nose.tools import assert_equals, assert_raises

from pmcf.parsers import yaml_parser
from pmcf.exceptions import ParserFailure


def _mock_validate(data, schema):
    return None


def _mock_validate_raises(data, schema):
    raise jsonschema.exceptions.ValidationError('error')


class TestParser(object):

    @mock.patch('jsonschema.validate', _mock_validate)
    def test_parse_invalid_args_raises(self):
        parser = yaml_parser.YamlParser()
        fname = 'tests/data/yaml/ais-test-farm.yaml'
        assert_raises(ParserFailure, parser.parse_file, fname, {})

    @mock.patch('jsonschema.validate', _mock_validate)
    def test_parser_raises_invalid_environment(self):
        args = {
            'environment': 'nosuchstage',
            'accesskey': '1234',
            'secretkey': '2345',
            'instance_accesskey': '12345',
            'instance_secretkey': '23456'
        }
        parser = yaml_parser.YamlParser()
        fname = 'tests/data/yaml/ais-test-farm.yaml'
        assert_raises(ParserFailure, parser.parse_file, fname, args)

    def test_parse_invalid_yaml_raises(self):
        config = """
            foo:
            - one
                bar:
                  - 1
                  - three
        """
        parser = yaml_parser.YamlParser()
        assert_raises(ParserFailure, parser.parse, config)

    @mock.patch('jsonschema.validate', _mock_validate_raises)
    def test_schema_validation_failure_raises(self):
        parser = yaml_parser.YamlParser()
        # Append empty instance
        parser._stack['resources']['instance'].append({})
        assert_raises(ParserFailure, parser.validate)

    @mock.patch('jsonschema.validate', _mock_validate)
    def test_instance_defaultsg(self):
        args = {
            'environment': 'stage',
            'accesskey': '1234',
            'secretkey': '2345',
            'instance_accesskey': '12345',
            'instance_secretkey': '23456'
        }
        parser = yaml_parser.YamlParser()
        fname = 'tests/data/yaml/ais-test-farm-defaultsg.yaml'
        data = parser.parse_file(fname, args)
        sgs = ['app', 'sg-123']
        assert_equals(data['resources']['instance'][0]['sg'], sgs)


class TestParserData(object):

    def __init__(self):
        self.data = {}

    @mock.patch('jsonschema.validate', _mock_validate)
    def setup(self):
        args = {
            'environment': 'stage',
            'accesskey': '1234',
            'secretkey': '2345',
            'instance_accesskey': '12345',
            'instance_secretkey': '23456',
            'audit_output': 'testbucket'
        }
        parser = yaml_parser.YamlParser()
        fname = 'tests/data/yaml/ais-test-farm.yaml'
        self.data = parser.parse_file(fname, args)

    def test_parser_has_valid_keys(self):
        assert_equals(set(['config', 'resources']), set(self.data.keys()))

    def test_parser_config_has_valid_keys(self):
        keys = [
            'audit_output',
            'name',
            'access',
            'secret',
            'environment',
            'instance_access',
            'instance_secret',
            'notify',
            'subnets',
            'provisioner',
            'profile',
        ]
        assert_equals(set(keys), set(self.data['config'].keys()))

    def test_parser_resource_has_valid_keys(self):
        keys = [
            'instance',
            'load_balancer',
            'secgroup',
            'cdn',
            'db',
            'role',
        ]
        assert_equals(set(keys), set(self.data['resources'].keys()))

    def test_parser_resource_first_instance_has_notify(self):
        assert_equals(
            True,
            'notify' in self.data['resources']['instance'][0].keys())

    def test_parser_resource_second_instance_has_notify(self):
        assert_equals(
            True,
            'notify' in self.data['resources']['instance'][1].keys())

    def test_parser_resource_has_valid_instance_count(self):
        assert_equals(2, len(self.data['resources']['instance']))

    def test_parser_resource_has_valid_lb_count(self):
        assert_equals(2, len(self.data['resources']['load_balancer']))

    def test_parser_resource_has_valid_secgroup_count(self):
        assert_equals(2, len(self.data['resources']['secgroup']))

    def test_parser_lb_has_valid_listener_count(self):
        assert_equals(2, len(
            self.data['resources']['load_balancer'][0]['listener']))

    def test_parser_sg_has_valid_rule_count_app(self):
        assert_equals(12, len(self.data['resources']['secgroup'][1]['rules']))

    def test_parser_sg_has_valid_rule_count_app2(self):
        assert_equals(0, len(self.data['resources']['secgroup'][0]['rules']))
