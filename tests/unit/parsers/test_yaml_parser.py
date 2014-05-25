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
            'config': {
                'name': 'ais',
                'stage': 'stage',
                'access': '1234',
                'secret': '2345',
                'instance_access': '12345',
                'instance_secret': '23456'
            },
            'resources': {
                'instance': [
                    {
                        'count': 3,
                        'image': 'ami-0bceb93b',
                        'lb': 'app',
                        'monitoring': False,
                        'name': 'app',
                        'provisioner': {'provider': 'puppet'},
                        'sg': ['app'],
                        'size': 'm1.large',
                        'sshKey': 'bootstrap'
                    }
                ],
                'load_balancer': [
                    {
                        'healthcheck': {
                            'port': 80,
                            'protocol': 'TCP'
                        },
                        'listener': [
                            {
                                'instance_port': 80,
                                'instance_protocol': 'HTTP',
                                'lb_port': 80,
                                'protocol': 'HTTP'
                            },
                            {
                                'instance_port': 80,
                                'instance_protocol': 'HTTP',
                                'lb_port': 443,
                                'protocol': 'HTTPS',
                                'sslCert': 'test',
                            }
                        ],
                        'name': 'app'
                    }
                ],
                'secgroup': [
                    {
                        'name': 'app',
                        'rules': [
                            {
                                'port': 22,
                                'protocol': 'tcp',
                                'source_cidr': '54.246.118.174/32'
                            },
                            {
                                'port': 22,
                                'protocol': 'tcp',
                                'source_cidr': '62.82.81.73/32'
                            },
                            {
                                'port': 22,
                                'protocol': 'tcp',
                                'source_cidr': '83.244.197.164/32'
                            },
                            {
                                'port': 22,
                                'protocol': 'tcp',
                                'source_cidr': '83.244.197.190/32'
                            },
                            {
                                'port': 22,
                                'protocol': 'tcp',
                                'source_cidr': '83.98.0.0/17'
                            },
                            {
                                'port': 5666,
                                'protocol': 'tcp',
                                'source_cidr': '83.98.0.0/17'
                            },
                            {
                                'port': 161,
                                'protocol': 'tcp',
                                'source_cidr': '83.98.0.0/17'
                            },
                            {
                                'port': 161,
                                'protocol': 'udp',
                                'source_cidr': '83.98.0.0/17'
                            },
                            {
                                'port': -1,
                                'protocol': 'icmp',
                                'source_cidr': '83.98.0.0/17'
                            },
                            {
                                'port': 22,
                                'protocol': 'tcp',
                                'source_cidr': '46.137.169.193/32'
                            },
                            {
                                'port': 80,
                                'protocol': 'tcp',
                                'source_cidr': '0.0.0.0/0'
                            },
                            {
                                'port': 443,
                                'protocol': 'tcp',
                                'source_cidr': '0.0.0.0/0'
                            }
                        ]
                    }
                ]
            }
        }

        args = {
            'stage': 'stage',
            'accesskey': '1234',
            'secretkey': '2345',
            'instance_accesskey': '12345',
            'instance_secretkey': '23456'
        }
        parser = yaml_parser.YamlParser()
        with open('tests/data/yaml/ais-test-farm.yaml') as fd:
            data = parser.parse(fd.read(), args)
        assert_equals(data, struct)

    def test_parse_invalid_args_raises(self):
        parser = yaml_parser.YamlParser()
        with open('tests/data/yaml/ais-test-farm.yaml') as fd:
            assert_raises(ParserFailure, parser.parse, fd.read(), {})

    def test_parse_invalid_config_raises(self):
        parser = yaml_parser.YamlParser()
        with open('tests/data/yaml/ais-test-bad-farm.yaml') as fd:
            assert_raises(ParserFailure, parser.parse, fd.read(), {})

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
