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

    def test__listify_string(self):
        parser = awsfw_parser.AWSFWParser()
        data = 'foo'
        assert_equals(parser._listify(data), ['foo'])

    def test__listify_list(self):
        parser = awsfw_parser.AWSFWParser()
        data = ['foo']
        assert_equals(parser._listify(data), data)

    def test_build_hc_invalid(self):
        parser = awsfw_parser.AWSFWParser()
        hc = 'TCP'
        assert_raises(ParserFailure, parser._build_hc, hc)

    def test_build_hc_http(self):
        parser = awsfw_parser.AWSFWParser()
        data = {
            'protocol': 'HTTP',
            'port': '80',
            'path': '/healthcheck'
        }
        entry = 'HTTP:80/healthcheck'

        assert_equals(parser._build_hc(entry), data)

    def test_build_hc_tcp(self):
        parser = awsfw_parser.AWSFWParser()
        data = {
            'protocol': 'TCP',
            'port': '80',
        }
        entry = 'TCP:80'

        assert_equals(parser._build_hc(entry), data)

    def test_build_lbs_invalid_https_no_cert(self):
        parser = awsfw_parser.AWSFWParser()
        lbdata = [{
            'listener': {
                'healthCheck': 'HTTP:80/healthcheck',
                'protocol': 'HTTPS',
                'port': '443',
                'instancePort': 80,
            }
        }]

        assert_raises(ParserFailure, parser.build_lbs, 'test', lbdata)

    def test_build_lbs_invalid_no_healthcheck(self):
        parser = awsfw_parser.AWSFWParser()
        lbdata = [{
            'listener': {
                'protocol': 'HTTP',
                'port': '80',
                'instancePort': 80,
            }
        }]

        assert_raises(ParserFailure, parser.build_lbs, 'test', lbdata)

    def test_build_lbs_invalid_no_healthcheck_multi(self):
        parser = awsfw_parser.AWSFWParser()
        lbdata = [
            {
                'listener': {
                    'protocol': 'HTTP',
                    'port': '80',
                    'instancePort': 80,
                }
            },
            {
                'listener': {
                    'protocol': 'HTTP',
                    'port': '8080',
                    'instancePort': 80,
                }
            }
        ]

        assert_raises(ParserFailure, parser.build_lbs, 'test', lbdata)

    def test_build_lbs_valid_http(self):
        parser = awsfw_parser.AWSFWParser()
        data = [
            {
                'listener': [
                    {
                        'instance_port': 80,
                        'protocol': 'HTTP',
                        'lb_port': '80'
                    }
                ],
                'healthcheck': {
                    'path': '/healthcheck',
                    'protocol': 'HTTP',
                    'port': '80'
                }
            }
        ]
        lbdata = [{
            'listener': {
                'healthCheck': 'HTTP:80/healthcheck',
                'protocol': 'HTTP',
                'port': '80',
                'instancePort': 80,
            }
        }]
        parser.build_lbs('test', lbdata)
        assert_equals(parser._stack['resources']['load_balancer'], data)

    def test_build_lbs_valid_https(self):
        parser = awsfw_parser.AWSFWParser()
        data = [
            {
                'listener': [
                    {
                        'instance_port': 80,
                        'sslCert': 'test',
                        'protocol': 'HTTPS',
                        'lb_port': '80'
                    }
                ],
                'healthcheck': {
                    'path': '/healthcheck',
                    'protocol': 'HTTP',
                    'port': '80'
                }
            }
        ]
        lbdata = [{
            'listener': {
                'healthCheck': 'HTTP:80/healthcheck',
                'protocol': 'HTTPS',
                'port': '80',
                'instancePort': 80,
                'sslCert': 'test',
            }
        }]
        parser.build_lbs('test', lbdata)
        assert_equals(parser._stack['resources']['load_balancer'], data)

    def test_build_lbs_valid_tcp(self):
        parser = awsfw_parser.AWSFWParser()
        data = [
            {
                'listener': [
                    {
                        'instance_port': 80,
                        'protocol': 'TCP',
                        'lb_port': '80'
                    }
                ],
                'healthcheck': {
                    'protocol': 'TCP',
                    'port': '80'
                }
            }
        ]
        lbdata = [{
            'listener': {
                'healthCheck': 'TCP:80',
                'protocol': 'TCP',
                'port': '80',
                'instancePort': 80,
            }
        }]
        parser.build_lbs('test', lbdata)
        assert_equals(parser._stack['resources']['load_balancer'], data)

    def test_build_lbs_valid_multiple(self):
        parser = awsfw_parser.AWSFWParser()
        data = [
            {
                'listener': [
                    {
                        'instance_port': 80,
                        'protocol': 'HTTP',
                        'lb_port': '80'
                    },
                    {
                        'instance_port': 80,
                        'protocol': 'HTTP',
                        'lb_port': '8080'
                    }
                ],
                'healthcheck': {
                    'path': '/healthcheck',
                    'protocol': 'HTTP',
                    'port': '80'
                }
            }
        ]
        lbdata = [{
            'listener': [
                {
                    'healthCheck': 'HTTP:80/healthcheck',
                    'protocol': 'HTTP',
                    'port': '80',
                    'instancePort': 80,
                },
                {
                    'protocol': 'HTTP',
                    'port': '8080',
                    'instancePort': 80,
                }
            ]
        }]
        parser.build_lbs('test', lbdata)
        assert_equals(parser._stack['resources']['load_balancer'], data)

    def test_parse_valid_config(self):
        parser = awsfw_parser.AWSFWParser()
        struct = {
            'resources': {
                'instance': [],
                'load_balancer': [],
                'db': [],
                'cdn': []
            }
        }

        config = ''
        with open('data/ais-stage-farm.xml') as fd:
            config = fd.read()

        data = parser.parse(config)
        # FIXME: Just to get a check in
        assert_equals(data, data)
