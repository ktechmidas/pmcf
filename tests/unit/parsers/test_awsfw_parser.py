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
                'instance_protocol': u'HTTP',
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
                'instance_protocol': u'HTTP',
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
                    'instance_protocol': u'HTTP',
                }
            },
            {
                'listener': {
                    'protocol': 'HTTP',
                    'port': '8080',
                    'instancePort': 80,
                    'instance_protocol': u'HTTP',
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
                        'lb_port': '80',
                        'instance_protocol': 'HTTP',
                    }
                ],
                'healthcheck': {
                    'path': '/healthcheck',
                    'protocol': 'HTTP',
                    'port': '80'
                },
                'name': 'test',
            }
        ]
        lbdata = [{
            'listener': {
                'healthCheck': 'HTTP:80/healthcheck',
                'protocol': 'HTTP',
                'port': '80',
                'instancePort': 80,
                'instance_protocol': 'HTTP',
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
                        'lb_port': '80',
                        'instance_protocol': 'HTTP',
                    }
                ],
                'name': 'test',
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
                'instance_protocol': 'HTTP',
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
                'name': 'test',
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
                        'lb_port': '80',
                        'instance_protocol': 'HTTP',
                    },
                    {
                        'instance_port': 80,
                        'protocol': 'HTTP',
                        'lb_port': '8080',
                        'instance_protocol': 'HTTP',
                    }
                ],
                'healthcheck': {
                    'path': '/healthcheck',
                    'protocol': 'HTTP',
                    'port': '80'
                },
                'name': 'test'
            }
        ]
        lbdata = [{
            'listener': [
                {
                    'healthCheck': 'HTTP:80/healthcheck',
                    'protocol': 'HTTP',
                    'port': '80',
                    'instancePort': 80,
                    'instance_protocol': 'HTTP',
                },
                {
                    'protocol': 'HTTP',
                    'port': '8080',
                    'instancePort': 80,
                    'instance_protocol': 'HTTP',
                }
            ]
        }]
        parser.build_lbs('test', lbdata)
        assert_equals(parser._stack['resources']['load_balancer'], data)

    def test_build_fw_valid(self):
        parser = awsfw_parser.AWSFWParser()
        rules = [
            {
                'name': 'test',
                'rules': [
                    {
                        'from_port': '22',
                        'to_port': '22',
                        'protocol': 'tcp',
                        'source_group': 'womble'
                    },
                    {
                        'from_port': '80',
                        'to_port': '80',
                        'protocol': 'tcp',
                        'source_cidr': '10.1.2.0/24'
                    }
                ]
            }
        ]
        rdata = [
            {
                'port': '22',
                'protocol': 'tcp',
                'source': 'womble',
            },
            {
                'port': '80',
                'protocol': 'tcp',
                'source': '10.1.2.0/24',
            }
        ]
        parser.build_fw('test', rdata)
        assert_equals(parser._stack['resources']['secgroup'], rules)

    def test_parse_invalid_config_no_instances(self):
        parser = awsfw_parser.AWSFWParser()
        with open('tests/data/awsfw/ais-stage-farm-noinstances.xml') as fd:
            config = fd.read()
        assert_raises(ParserFailure, parser.parse, config)

    def test_parse_valid_config_provisioner_puppet(self):
        parser = awsfw_parser.AWSFWParser()
        struct = {
            'config': {
                'name': u'ais',
                'stage': u'stage',
                'strategy': 'BLUEGREEN',
                'version': u'v2p54',
                'owner': 'gis-channel4@piksel.com'
            },
            'resources': {
                'cdn': [],
                'db': [],
                'instance': [
                    {
                        'block_device': [],
                        'count': u'6',
                        'image': u'ami-e97f849e',
                        'monitoring': u'false',
                        'name': u'app',
                        'lb': u'app',
                        'provisioner': {
                            'args': {
                                'appBucket': u'aws-c4-003358414754',
                                'apps': ['ais'],
                                'roleBucket': u'aws-c4-003358414754',
                                'roles': ['app']
                            },
                            'type': u'puppet'
                        },
                        'sg': [u'app', 'default'],
                        'sshKey': u'ioko-pml',
                        'type': u'm1.large'
                    }
                ],
                'load_balancer': [
                    {
                        'healthcheck': {
                            'port': u'80',
                            'protocol': u'TCP'
                        },
                        'name': 'app',
                        'listener': [
                            {
                                'instance_port': u'80',
                                'lb_port': u'80',
                                'protocol': u'HTTP',
                                'instance_protocol': 'HTTP',
                            },
                            {
                                'instance_port': u'80',
                                'lb_port': u'443',
                                'protocol': u'HTTPS',
                                'sslCert': u'test',
                                'instance_protocol': 'HTTP',
                            }
                        ],
                        'logging': {
                            's3bucket': u'c4-elb-logs',
                            'emit_interval': u'60',
                            'enabled': True,
                            's3prefix': u'stage%2Fais'
                        }
                    }
                ],
                'secgroup': [
                    {
                        'name': u'app',
                        'rules': [
                            {
                                'from_port': u'22',
                                'protocol': u'tcp',
                                'source_cidr': u'54.246.118.174/32',
                                'to_port': u'22'
                            },
                            {
                                'from_port': u'22',
                                'protocol': u'tcp',
                                'source_cidr': u'62.82.81.73/32',
                                'to_port': u'22'
                            },
                            {
                                'from_port': u'22',
                                'protocol': u'tcp',
                                'source_cidr': u'83.244.197.164/32',
                                'to_port': u'22'
                            },
                            {
                                'from_port': u'22',
                                'protocol': u'tcp',
                                'source_cidr': u'83.244.197.190/32',
                                'to_port': u'22'
                            },
                            {
                                'from_port': u'22',
                                'protocol': u'tcp',
                                'source_cidr': u'83.98.0.0/17',
                                'to_port': u'22'
                            },
                            {
                                'from_port': u'22',
                                'protocol': u'tcp',
                                'source_group': u'jump-server-sg',
                                'to_port': u'22'
                            },
                            {
                                'from_port': u'5666',
                                'protocol': u'tcp',
                                'source_cidr': u'83.98.0.0/17',
                                'to_port': u'5666'
                            },
                            {
                                'from_port': u'161',
                                'protocol': u'tcp',
                                'source_cidr': u'83.98.0.0/17',
                                'to_port': u'161'
                            },
                            {
                                'from_port': u'161',
                                'protocol': u'udp',
                                'source_cidr': u'83.98.0.0/17',
                                'to_port': u'161'
                            },
                            {
                                'from_port': u'-1',
                                'protocol': u'icmp',
                                'source_cidr': u'83.98.0.0/17',
                                'to_port': u'-1'
                            },
                            {
                                'from_port': u'22',
                                'protocol': u'tcp',
                                'source_cidr': u'46.137.169.193/32',
                                'to_port': u'22'
                            },
                            {
                                'from_port': u'80',
                                'protocol': u'tcp',
                                'source_cidr': u'0.0.0.0/0',
                                'to_port': u'80'
                            },
                            {
                                'from_port': u'443',
                                'protocol': u'tcp',
                                'source_cidr': u'0.0.0.0/0',
                                'to_port': u'443'
                            }
                        ]
                    }
                ]
            }
        }

        with open('tests/data/awsfw/ais-stage-farm-puppet.xml') as fd:
            config = fd.read()

        data = parser.parse(config)
        assert_equals(data, struct)

    def test_parse_invalid_config_raises(self):
        parser = awsfw_parser.AWSFWParser()
        with open('tests/data/awsfw/ais-stage-farm-broken.xml') as fd:
            config = fd.read()

        assert_raises(ParserFailure, parser.parse, config)

    def test_parse_valid_config(self):
        parser = awsfw_parser.AWSFWParser()
        struct = {
            'config': {
                'name': u'ais',
                'stage': u'stage',
                'strategy': 'BLUEGREEN',
                'version': u'v2p54'},
            'resources': {
                'cdn': [],
                'db': [],
                'instance': [
                    {
                        'block_device': [],
                        'count': u'6',
                        'image': u'ami-e97f849e',
                        'monitoring': u'false',
                        'name': u'app',
                        'lb': u'app',
                        'provisioner': {
                            'args': {
                                'appBucket': u'aws-c4-003358414754',
                                'apps': [
                                    u'ais-jetty/v2.54-02',
                                    u'ais-nginx/v1.23',
                                    u'c4-devaccess'
                                ],
                                'roleBucket': u'aws-c4-003358414754',
                                'roles': [
                                    u'jetty',
                                    u'nginx-latest/v1.5',
                                    u'nagiosclient/v1.5',
                                    u'snmpd/v1.2',
                                    u'cloudwatch-monitoring/v1'
                                ]
                            },
                            'type': 'awsfw_standalone'
                        },
                        'sg': [u'app'],
                        'sshKey': u'ioko-pml',
                        'type': u'm1.large'
                    }
                ],
                'load_balancer': [
                    {
                        'healthcheck': {
                            'port': u'80',
                            'protocol': u'TCP'
                        },
                        'name': 'app',
                        'listener': [
                            {
                                'instance_port': u'80',
                                'lb_port': u'80',
                                'protocol': u'HTTP',
                                'instance_protocol': u'HTTP',
                            },
                            {
                                'instance_port': u'80',
                                'lb_port': u'443',
                                'protocol': u'HTTPS',
                                'sslCert': u'test',
                                'instance_protocol': u'HTTP',
                            }
                        ],
                        'logging': {
                            's3bucket': u'c4-elb-logs',
                            'emit_interval': u'60',
                            'enabled': True,
                            's3prefix': u'stage%2Fais'
                        }
                    }
                ],
                'secgroup': [
                    {
                        'name': u'app',
                        'rules': [
                            {
                                'from_port': u'22',
                                'protocol': u'tcp',
                                'source_cidr': u'54.246.118.174/32',
                                'to_port': u'22'
                            },
                            {
                                'from_port': u'22',
                                'protocol': u'tcp',
                                'source_cidr': u'62.82.81.73/32',
                                'to_port': u'22'
                            },
                            {
                                'from_port': u'22',
                                'protocol': u'tcp',
                                'source_cidr': u'83.244.197.164/32',
                                'to_port': u'22'
                            },
                            {
                                'from_port': u'22',
                                'protocol': u'tcp',
                                'source_cidr': u'83.244.197.190/32',
                                'to_port': u'22'
                            },
                            {
                                'from_port': u'22',
                                'protocol': u'tcp',
                                'source_cidr': u'83.98.0.0/17',
                                'to_port': u'22'
                            },
                            {
                                'from_port': u'22',
                                'protocol': u'tcp',
                                'source_group': u'jump-server-sg',
                                'to_port': u'22'
                            },
                            {
                                'from_port': u'5666',
                                'protocol': u'tcp',
                                'source_cidr': u'83.98.0.0/17',
                                'to_port': u'5666'
                            },
                            {
                                'from_port': u'161',
                                'protocol': u'tcp',
                                'source_cidr': u'83.98.0.0/17',
                                'to_port': u'161'
                            },
                            {
                                'from_port': u'161',
                                'protocol': u'udp',
                                'source_cidr': u'83.98.0.0/17',
                                'to_port': u'161'
                            },
                            {
                                'from_port': u'-1',
                                'protocol': u'icmp',
                                'source_cidr': u'83.98.0.0/17',
                                'to_port': u'-1'
                            },
                            {
                                'from_port': u'22',
                                'protocol': u'tcp',
                                'source_cidr': u'46.137.169.193/32',
                                'to_port': u'22'
                            },
                            {
                                'from_port': u'80',
                                'protocol': u'tcp',
                                'source_cidr': u'0.0.0.0/0',
                                'to_port': u'80'
                            },
                            {
                                'from_port': u'443',
                                'protocol': u'tcp',
                                'source_cidr': u'0.0.0.0/0',
                                'to_port': u'443'
                            }
                        ]
                    }
                ]
            }
        }

        with open('tests/data/awsfw/ais-stage-farm.xml') as fd:
            config = fd.read()

        data = parser.parse(config)
        assert_equals(data, struct)
