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

from pmcf.parsers import awsfw_parser
from pmcf.exceptions import ParserFailure


def _mock_validate(stack, schema):
    return None


def _mock_validate_raises(data, schema):
    raise jsonschema.exceptions.ValidationError('error')


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
            'port': 80,
            'path': '/healthcheck'
        }
        entry = 'HTTP:80/healthcheck'

        assert_equals(parser._build_hc(entry), data)

    def test_build_hc_tcp(self):
        parser = awsfw_parser.AWSFWParser()
        data = {
            'protocol': 'TCP',
            'port': 80,
        }
        entry = 'TCP:80'

        assert_equals(parser._build_hc(entry), data)

    def test_build_lbs_invalid_https_no_cert(self):
        parser = awsfw_parser.AWSFWParser()
        lbdata = [{
            'listener': {
                'healthCheck': 'HTTP:80/healthcheck',
                'protocol': 'HTTPS',
                'port': 443,
                'instance_protocol': u'HTTP',
                'instancePort': 80,
            }
        }]

        assert_raises(ParserFailure, parser.build_lbs, 'test', lbdata)

    def test_build_lbs_valid_http(self):
        parser = awsfw_parser.AWSFWParser()
        data = [
            {
                'listener': [
                    {
                        'instance_port': 80,
                        'protocol': 'HTTP',
                        'lb_port': 80,
                        'instance_protocol': 'HTTP',
                    }
                ],
                'healthcheck': {
                    'path': '/healthcheck',
                    'protocol': 'HTTP',
                    'port': 80
                },
                'name': 'test',
                'policy': [],
            }
        ]
        lbdata = [{
            'listener': {
                'healthCheck': 'HTTP:80/healthcheck',
                'protocol': 'HTTP',
                'port': 80,
                'instancePort': 80,
                'instance_protocol': 'HTTP',
            }
        }]
        parser.build_lbs('test', lbdata)
        assert_equals(parser.stack()['resources']['load_balancer'], data)

    def test_build_lbs_valid_https(self):
        parser = awsfw_parser.AWSFWParser()
        data = [
            {
                'listener': [
                    {
                        'instance_port': 80,
                        'sslCert': 'test',
                        'protocol': 'HTTPS',
                        'lb_port': 80,
                        'instance_protocol': 'HTTP',
                    }
                ],
                'name': 'test',
                'policy': [],
                'healthcheck': {
                    'path': '/healthcheck',
                    'protocol': 'HTTP',
                    'port': 80
                }
            }
        ]
        lbdata = [{
            'listener': {
                'healthCheck': 'HTTP:80/healthcheck',
                'protocol': 'HTTPS',
                'port': 80,
                'instancePort': 80,
                'sslCert': 'test',
                'instance_protocol': 'HTTP',
            }
        }]
        parser.build_lbs('test', lbdata)
        assert_equals(parser.stack()['resources']['load_balancer'], data)

    def test_build_lbs_valid_logging_policy(self):
        parser = awsfw_parser.AWSFWParser()
        data = [
            {
                'listener': [
                    {
                        'instance_port': 80,
                        'protocol': 'TCP',
                        'lb_port': 80
                    }
                ],
                'name': 'test',
                'policy': [],
                'healthcheck': {
                    'protocol': 'TCP',
                    'port': 80
                },
                'policy': [{
                    'type': 'log_policy',
                    'policy': {
                        's3bucket': u'c4-elb-logs',
                        'emit_interval': 60,
                        'enabled': True,
                        's3prefix': u'stage/ais'
                    }
                }]
            }
        ]
        lbdata = [{
            'listener': {
                'healthCheck': 'TCP:80',
                'protocol': 'TCP',
                'port': 80,
                'instancePort': 80,
            },
            'elb-logging': {
                'emitinterval': '60',
                's3bucket': 'c4-elb-logs',
                'prefix': 'stage%2Fais'
            }
        }]
        parser.build_lbs('test', lbdata)
        assert_equals(parser.stack()['resources']['load_balancer'], data)

    def test_build_lbs_valid_tcp(self):
        parser = awsfw_parser.AWSFWParser()
        data = [
            {
                'listener': [
                    {
                        'instance_port': 80,
                        'protocol': 'TCP',
                        'lb_port': 80
                    }
                ],
                'name': 'test',
                'policy': [],
                'healthcheck': {
                    'protocol': 'TCP',
                    'port': 80
                }
            }
        ]
        lbdata = [{
            'listener': {
                'healthCheck': 'TCP:80',
                'protocol': 'TCP',
                'port': 80,
                'instancePort': 80,
            }
        }]
        parser.build_lbs('test', lbdata)
        assert_equals(parser.stack()['resources']['load_balancer'], data)

    def test_build_lbs_valid_multiple(self):
        parser = awsfw_parser.AWSFWParser()
        data = [
            {
                'listener': [
                    {
                        'instance_port': 80,
                        'protocol': 'HTTP',
                        'lb_port': 80,
                        'instance_protocol': 'HTTP',
                    },
                    {
                        'instance_port': 80,
                        'protocol': 'HTTP',
                        'lb_port': 8080,
                        'instance_protocol': 'HTTP',
                    }
                ],
                'healthcheck': {
                    'path': '/healthcheck',
                    'protocol': 'HTTP',
                    'port': 80
                },
                'name': 'test',
                'policy': [],
            }
        ]
        lbdata = [{
            'listener': [
                {
                    'healthCheck': 'HTTP:80/healthcheck',
                    'protocol': 'HTTP',
                    'port': 80,
                    'instancePort': 80,
                    'instance_protocol': 'HTTP',
                },
                {
                    'protocol': 'HTTP',
                    'port': 8080,
                    'instancePort': 80,
                    'instance_protocol': 'HTTP',
                }
            ]
        }]
        parser.build_lbs('test', lbdata)
        assert_equals(parser.stack()['resources']['load_balancer'], data)

    def test_build_fw_valid(self):
        parser = awsfw_parser.AWSFWParser()
        rules = [
            {
                'name': 'test',
                'rules': [
                    {
                        'from_port': 22,
                        'to_port': 22,
                        'protocol': 'tcp',
                        'source_group': 'womble'
                    },
                    {
                        'from_port': 80,
                        'to_port': 80,
                        'protocol': 'tcp',
                        'source_cidr': '10.1.2.0/24'
                    }
                ]
            }
        ]
        rdata = [
            {
                'port': 22,
                'protocol': 'tcp',
                'source': 'womble',
            },
            {
                'port': 80,
                'protocol': 'tcp',
                'source': '10.1.2.0/24',
            }
        ]
        parser.build_fw('test', rdata)
        assert_equals(parser.stack()['resources']['secgroup'], rules)

    def test_build_instance_valid(self):
        data = [
            {
                'block_device': [],
                'count': 6,
                'image': 'ami-e97f849e',
                'lb': 'app',
                'name': 'app',
                'provisioner': {
                    'args': {
                        'apps': ['ais-jetty/v2.54-02'],
                        'roles': ['jetty']
                    },
                    'provider': 'AWSFWProvisioner'},
                'sg': [],
                'size': 'm1.large'
            }
        ]
        instances = [{
            'tier': 'app',
            'availabilityZone': ['eu-west-1a'],
            'role': ['jetty'],
            'cname': 'app',
            'count': '6',
            'amiId': 'ami-e97f849e',
            'size': 'm1.large',
            'app': ['ais-jetty/v2.54-02'],
            'elb': 'app',
        }]

        parser = awsfw_parser.AWSFWParser()
        parser._stack['resources']['load_balancer'].append({
            'listener': [
                {
                    'instance_port': 80,
                    'sslCert': 'test',
                    'protocol': 'HTTPS',
                    'lb_port': 80,
                    'instance_protocol': 'HTTP',
                }
            ],
            'name': 'app',
            'policy': [],
            'healthcheck': {
                'path': '/healthcheck',
                'protocol': 'HTTP',
                'port': 80
            }
        })
        parser.build_instances('test', instances)
        assert_equals(parser.stack()['resources']['instance'], data)

    def test_build_instance_valid_no_cname(self):
        data = [
            {
                'block_device': [],
                'count': 6,
                'image': 'ami-e97f849e',
                'name': 'app',
                'provisioner': {
                    'args': {
                        'apps': ['ais-jetty/v2.54-02'],
                        'roles': ['jetty']
                    },
                    'provider': 'AWSFWProvisioner'},
                'sg': [],
                'size': 'm1.large'
            }
        ]
        instances = [{
            'tier': 'app',
            'availabilityZone': ['eu-west-1a'],
            'role': ['jetty'],
            'count': '6',
            'amiId': 'ami-e97f849e',
            'size': 'm1.large',
            'app': ['ais-jetty/v2.54-02'],
        }]

        parser = awsfw_parser.AWSFWParser()
        parser.build_instances('test', instances)
        assert_equals(parser.stack()['resources']['instance'], data)

    def test_build_instance_valid_single_block_device(self):
        data = [
            {
                'block_device': [{
                    'size': 10,
                    'device': '/dev/sdh'
                }],
                'count': 6,
                'image': 'ami-e97f849e',
                'name': 'app',
                'provisioner': {
                    'args': {
                        'apps': ['ais-jetty/v2.54-02'],
                        'roles': ['jetty']
                    },
                    'provider': 'AWSFWProvisioner'
                },
                'sg': [],
                'size': 'm1.large'
            }
        ]
        instances = [{
            'tier': 'app',
            'availabilityZone': ['eu-west-1a'],
            'role': ['jetty'],
            'count': '6',
            'amiId': 'ami-e97f849e',
            'size': 'm1.large',
            'app': ['ais-jetty/v2.54-02'],
            'volume': {
                'volumeSize': '10',
                'volumeDevice': '/dev/sdh'
            }
        }]

        parser = awsfw_parser.AWSFWParser()
        parser.build_instances('test', instances)
        assert_equals(parser.stack()['resources']['instance'], data)

    def test_build_instance_valid_alternate_provisioner(self):
        data = [
            {
                'block_device': [],
                'count': 6,
                'image': 'ami-e97f849e',
                'name': 'app',
                'sg': [],
                'provisioner': {
                    'args': {
                        'apps': ['ais-jetty/v2.54-02'],
                        'roles': ['jetty']
                    },
                    'provider': 'puppet'
                },
                'size': 'm1.large'
            }
        ]
        instances = [{
            'tier': 'app',
            'availabilityZone': ['eu-west-1a'],
            'count': '6',
            'amiId': 'ami-e97f849e',
            'size': 'm1.large',
            'provisioner': {
                'provider': 'puppet',
                'args': {
                    'role': ['jetty'],
                    'app': ['ais-jetty/v2.54-02'],
                }
            }
        }]

        parser = awsfw_parser.AWSFWParser()
        parser.build_instances('test', instances)
        assert_equals(parser.stack()['resources']['instance'], data)

    def test_build_instance_valid_multiple_lb(self):
        data = [
            {
                'block_device': [],
                'count': 6,
                'image': 'ami-e97f849e',
                'lb': 'app',
                'name': 'app',
                'provisioner': {
                    'args': {
                        'apps': ['ais-jetty/v2.54-02'],
                        'roles': ['jetty']
                    },
                    'provider': 'AWSFWProvisioner'},
                'sg': [],
                'size': 'm1.large'
            }
        ]
        instances = [{
            'tier': 'app',
            'availabilityZone': ['eu-west-1a'],
            'role': ['jetty'],
            'cname': 'app',
            'count': '6',
            'amiId': 'ami-e97f849e',
            'size': 'm1.large',
            'app': ['ais-jetty/v2.54-02'],
            'elb': 'app',
        }]

        parser = awsfw_parser.AWSFWParser()
        parser._stack['resources']['load_balancer'].append({
            'listener': [
                {
                    'instance_port': 80,
                    'sslCert': 'test',
                    'protocol': 'HTTPS',
                    'lb_port': 80,
                    'instance_protocol': 'HTTP',
                }
            ],
            'name': 'app',
            'policy': [],
            'healthcheck': {
                'path': '/healthcheck',
                'protocol': 'HTTP',
                'port': 80
            }
        })
        parser._stack['resources']['load_balancer'].append({
            'listener': [
                {
                    'instance_port': 80,
                    'sslCert': 'test',
                    'protocol': 'HTTPS',
                    'lb_port': 80,
                    'instance_protocol': 'HTTP',
                }
            ],
            'name': 'app2',
            'policy': [],
            'healthcheck': {
                'path': '/healthcheck',
                'protocol': 'HTTP',
                'port': 80
            }
        })
        parser.build_instances('test', instances)
        assert_equals(parser.stack()['resources']['instance'], data)

    def test_build_instance_invalid_missing_lb(self):
        instances = [{
            'tier': 'app',
            'availabilityZone': ['eu-west-1a'],
            'role': ['jetty'],
            'count': '6',
            'amiId': 'ami-e97f849e',
            'size': 'm1.large',
            'app': ['ais-jetty/v2.54-02'],
            'elb': 'app',
        }]

        parser = awsfw_parser.AWSFWParser()
        assert_raises(ParserFailure, parser.build_instances, 'test', instances)

    def test_build_instance_invalid_multiple_lb(self):
        instances = [{
            'tier': 'app',
            'availabilityZone': ['eu-west-1a'],
            'role': ['jetty'],
            'cname': 'app',
            'count': '6',
            'amiId': 'ami-e97f849e',
            'size': 'm1.large',
            'app': ['ais-jetty/v2.54-02'],
            'elb': None,
        }]

        parser = awsfw_parser.AWSFWParser()
        parser._stack['resources']['load_balancer'].append({
            'listener': [
                {
                    'instance_port': 80,
                    'sslCert': 'test',
                    'protocol': 'HTTPS',
                    'lb_port': 80,
                    'instance_protocol': 'HTTP',
                }
            ],
            'name': 'app',
            'policy': [],
            'healthcheck': {
                'path': '/healthcheck',
                'protocol': 'HTTP',
                'port': 80
            }
        })
        parser._stack['resources']['load_balancer'].append({
            'listener': [
                {
                    'instance_port': 80,
                    'sslCert': 'test',
                    'protocol': 'HTTPS',
                    'lb_port': 80,
                    'instance_protocol': 'HTTP',
                }
            ],
            'name': 'app2',
            'policy': [],
            'healthcheck': {
                'path': '/healthcheck',
                'protocol': 'HTTP',
                'port': 80
            }
        })
        assert_raises(ParserFailure, parser.build_instances, 'test', instances)

    def test_build_ds_default_sg(self):
        ds = {
            'farmName': 'ais-stage-01',
            'farmOwner': 'gis-channel4@piksel.com',
            'key': 'test',
            'cloudwatch': 'true',
            'appBucket': 'testbucket',
            'roleBucket': 'testbucket',
            'instances': [{
                'tier': 'app',
                'availabilityZone': ['eu-west-1a'],
                'role': ['jetty'],
                'cname': 'app',
                'count': '6',
                'amiId': 'ami-e97f849e',
                'size': 'm1.large',
                'app': ['ais-jetty/v2.54-02'],
            }]
        }
        data = [
            {
                'block_device': [],
                'count': 6,
                'image': 'ami-e97f849e',
                'name': 'app',
                'sg': ['default'],
                'monitoring': True,
                'sshKey': 'test',
                'provisioner': {
                    'args': {
                        'apps': ['ais-jetty/v2.54-02'],
                        'roles': ['jetty'],
                        'appBucket': 'testbucket',
                        'roleBucket': 'testbucket',
                        'platform_environment': 'stage',
                    },
                    'provider': 'AWSFWProvisioner'
                },
                'size': 'm1.large'
            }
        ]

        parser = awsfw_parser.AWSFWParser()
        parser.build_ds(ds, {})
        assert_equals(parser._stack['resources']['instance'],  data)

    def test_build_ds_default_no_default_sg(self):
        ds = {
            'farmName': 'ais-stage-01',
            'farmOwner': 'gis-channel4@piksel.com',
            'key': 'test',
            'cloudwatch': 'true',
            'appBucket': 'testbucket',
            'roleBucket': 'testbucket',
            'noDefaultSG': None,
            'instances': [{
                'tier': 'app',
                'availabilityZone': ['eu-west-1a'],
                'role': ['jetty'],
                'cname': 'app',
                'count': '6',
                'amiId': 'ami-e97f849e',
                'size': 'm1.large',
                'app': ['ais-jetty/v2.54-02'],
            }]
        }
        data = [
            {
                'block_device': [],
                'count': 6,
                'image': 'ami-e97f849e',
                'name': 'app',
                'sg': [],
                'monitoring': True,
                'sshKey': 'test',
                'provisioner': {
                    'args': {
                        'apps': ['ais-jetty/v2.54-02'],
                        'roles': ['jetty'],
                        'appBucket': 'testbucket',
                        'roleBucket': 'testbucket',
                        'platform_environment': 'stage',
                    },
                    'provider': 'AWSFWProvisioner'
                },
                'size': 'm1.large'
            }
        ]

        parser = awsfw_parser.AWSFWParser()
        parser.build_ds(ds, {})
        assert_equals(parser._stack['resources']['instance'],  data)

    @mock.patch('jsonschema.validate', _mock_validate)
    def test_parse_invalid_xml_config_raises(self):
        parser = awsfw_parser.AWSFWParser()
        assert_raises(ParserFailure, parser.parse_file,
                      'tests/data/awsfw/ais-stage-farm-broken.xml')

    @mock.patch('jsonschema.validate', _mock_validate_raises)
    def test_schema_validation_failure_raises(self):
        parser = awsfw_parser.AWSFWParser()
        # Append empty instance
        parser._stack['resources']['instance'].append({})
        assert_raises(ParserFailure, parser.validate)


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
            'instance_secretkey': '23456'
        }
        parser = awsfw_parser.AWSFWParser()
        fname = 'tests/data/awsfw/ais-stage-farm.xml'
        self.data = parser.parse_file(fname, args)

    def test_parser_has_valid_keys(self):
        assert_equals(set(['config', 'resources']), set(self.data.keys()))

    def test_parser_config_has_valid_keys(self):
        keys = [
            'name',
            'environment',
            'access',
            'secret',
            'instance_accesskey',
            'instance_secretkey',
            'owner',
            'version',
            'strategy',
        ]
        assert_equals(set(keys), set(self.data['config'].keys()))

    def test_parser_resource_has_valid_keys(self):
        keys = [
            'instance',
            'load_balancer',
            'secgroup',
            'cdn',
            'db',
        ]
        assert_equals(set(keys), set(self.data['resources'].keys()))

    def test_parser_resource_has_valid_instance_count(self):
        assert_equals(1, len(self.data['resources']['instance']))

    def test_parser_resource_has_valid_lb_count(self):
        assert_equals(1, len(self.data['resources']['load_balancer']))

    def test_parser_resource_has_valid_secgroup_count(self):
        assert_equals(1, len(self.data['resources']['secgroup']))

    def test_parser_lb_has_valid_listener_count(self):
        assert_equals(2, len(
            self.data['resources']['load_balancer'][0]['listener']))

    def test_parser_sg_has_valid_rule_count(self):
        assert_equals(13, len(self.data['resources']['secgroup'][0]['rules']))
