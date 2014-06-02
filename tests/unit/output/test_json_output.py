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

import json
import mock
from nose.tools import assert_equals, assert_raises

from pmcf.exceptions import ProvisionerException
from pmcf.outputs import JSONOutput
from pmcf.provisioners import AWSFWProvisioner


def _mock_ud(self, cfg, args):
    return ''


class TestJSONOutput(object):

    def test_lb_valid(self):
        out = JSONOutput()
        ret = {
            "AWSTemplateFormatVersion": "2010-09-09",
            "Description": "test test stack",
            "Outputs": {
                "ELBtestDNS": {
                    "Description": "Public DNSName of the ELBtest ELB",
                    "Value": {
                        "Fn::GetAtt": [
                            "ELBtest",
                            "DNSName"
                        ]
                    }
                }
            },
            "Resources": {
                "ELBtest": {
                    "Properties": {
                        "AvailabilityZones": {
                            "Fn::GetAZs": ""
                        },
                        "CrossZone": "true",
                        "HealthCheck": {
                            "HealthyThreshold": 3,
                            "Interval": 5,
                            "Target": "HTTP:80/healthcheck",
                            "Timeout": 2,
                            "UnhealthyThreshold": 3
                        },
                        "Listeners": [
                            {
                                "InstancePort": 80,
                                "InstanceProtocol": "HTTP",
                                "LoadBalancerPort": 80,
                                "Protocol": "HTTP"
                            }
                        ]
                    },
                    "Type": "AWS::ElasticLoadBalancing::LoadBalancer"
                }
            }
        }

        cfg = {
            'name': 'test',
            'stage': 'test'
        }
        res = {
            'instance': [],
            'secgroup': [],
            'load_balancer': [{
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
            }]
        }
        tmpl = out.add_resources(None, res, cfg)
        assert_equals(json.loads(tmpl), ret)

    def test_lb_valid_ssl(self):
        out = JSONOutput()
        ret = {
            "AWSTemplateFormatVersion": "2010-09-09",
            "Description": "test test stack",
            "Outputs": {
                "ELBtestDNS": {
                    "Description": "Public DNSName of the ELBtest ELB",
                    "Value": {
                        "Fn::GetAtt": [
                            "ELBtest",
                            "DNSName"
                        ]
                    }
                }
            },
            "Resources": {
                "ELBtest": {
                    "Properties": {
                        "AvailabilityZones": {
                            "Fn::GetAZs": ""
                        },
                        "CrossZone": "true",
                        "HealthCheck": {
                            "HealthyThreshold": 3,
                            "Interval": 5,
                            "Target": "HTTP:80/healthcheck",
                            "Timeout": 2,
                            "UnhealthyThreshold": 3
                        },
                        "Listeners": [
                            {
                                "InstancePort": 80,
                                "InstanceProtocol": "HTTP",
                                "LoadBalancerPort": 443,
                                "SSLCertificateId": "test",
                                "Protocol": "HTTPS"
                            }
                        ]
                    },
                    "Type": "AWS::ElasticLoadBalancing::LoadBalancer"
                }
            }
        }

        cfg = {
            'name': 'test',
            'stage': 'test'
        }
        res = {
            'instance': [],
            'secgroup': [],
            'load_balancer': [{
                'listener': [
                    {
                        'instance_port': 80,
                        'protocol': 'HTTPS',
                        'sslCert': 'test',
                        'lb_port': 443,
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
            }]
        }
        tmpl = out.add_resources(None, res, cfg)
        assert_equals(json.loads(tmpl), ret)

    def test_lb_valid_access_log_policy(self):
        out = JSONOutput()
        ret = {
            "AWSTemplateFormatVersion": "2010-09-09",
            "Description": "test test stack",
            "Outputs": {
                "ELBtestDNS": {
                    "Description": "Public DNSName of the ELBtest ELB",
                    "Value": {
                        "Fn::GetAtt": [
                            "ELBtest",
                            "DNSName"
                        ]
                    }
                }
            },
            "Resources": {
                "ELBtest": {
                    "Properties": {
                        "AccessLoggingPolicy": {
                            "EmitInterval": 60,
                            "Enabled": "true",
                            "S3BucketName": "c4-elb-logs",
                            "S3BucketPrefix": "stage/ais"
                        },
                        "AvailabilityZones": {
                            "Fn::GetAZs": ""
                        },
                        "CrossZone": "true",
                        "HealthCheck": {
                            "HealthyThreshold": 3,
                            "Interval": 5,
                            "Target": "HTTP:80/healthcheck",
                            "Timeout": 2,
                            "UnhealthyThreshold": 3
                        },
                        "Listeners": [
                            {
                                "InstancePort": 80,
                                "InstanceProtocol": "HTTP",
                                "LoadBalancerPort": 80,
                                "Protocol": "HTTP"
                            }
                        ]
                    },
                    "Type": "AWS::ElasticLoadBalancing::LoadBalancer"
                }
            }
        }

        cfg = {
            'name': 'test',
            'stage': 'test'
        }
        res = {
            'instance': [],
            'secgroup': [],
            'load_balancer': [{
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
                'policy': [{
                    'type': 'log_policy',
                    'policy': {
                        's3bucket': u'c4-elb-logs',
                        'emit_interval': 60,
                        'enabled': True,
                        's3prefix': u'stage/ais'
                    }
                }]
            }]
        }
        tmpl = out.add_resources(None, res, cfg)
        assert_equals(json.loads(tmpl), ret)

    def test_sg_valid(self):
        out = JSONOutput()
        ret = {
            "AWSTemplateFormatVersion": "2010-09-09",
            "Description": "test test stack",
            "Resources": {
                "sgtest": {
                    "Properties": {
                        "GroupDescription": "security group for test",
                        "SecurityGroupIngress": [
                            {
                                "FromPort": 22,
                                "IpProtocol": "tcp",
                                "SourceSecurityGroupName": "womble",
                                "ToPort": 22
                            },
                            {
                                "CidrIp": "10.1.2.0/24",
                                "FromPort": 80,
                                "IpProtocol": "tcp",
                                "ToPort": 80
                            }
                        ]
                    },
                    "Type": "AWS::EC2::SecurityGroup"
                }
            }
        }

        cfg = {
            'name': 'test',
            'stage': 'test'
        }
        res = {
            'instance': [],
            'load_balancer': [],
            'secgroup': [{
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
            }]
        }
        tmpl = out.add_resources(None, res, cfg)
        assert_equals(json.loads(tmpl), ret)

    def test_sg_valid_short_form(self):
        out = JSONOutput()
        ret = {
            "AWSTemplateFormatVersion": "2010-09-09",
            "Description": "test test stack",
            "Resources": {
                "sgtest": {
                    "Properties": {
                        "GroupDescription": "security group for test",
                        "SecurityGroupIngress": [
                            {
                                "CidrIp": "10.1.2.0/24",
                                "FromPort": 80,
                                "IpProtocol": "tcp",
                                "ToPort": 80
                            }
                        ]
                    },
                    "Type": "AWS::EC2::SecurityGroup"
                }
            }
        }

        cfg = {
            'name': 'test',
            'stage': 'test'
        }
        res = {
            'instance': [],
            'load_balancer': [],
            'secgroup': [{
                'name': 'test',
                'rules': [
                    {
                        'port': 80,
                        'protocol': 'tcp',
                        'source_cidr': '10.1.2.0/24'
                    }
                ]
            }]
        }
        tmpl = out.add_resources(None, res, cfg)
        assert_equals(json.loads(tmpl), ret)

    @mock.patch('pmcf.provisioners.AWSFWProvisioner.userdata', _mock_ud)
    def test_instance_valid_instance_secrets(self):
        out = JSONOutput()
        ret = {
            "AWSTemplateFormatVersion": "2010-09-09",
            "Description": "test test stack",
            "Resources": {
                "ASGapp": {
                    "Properties": {
                        "AvailabilityZones": {
                            "Fn::GetAZs": ""
                        },
                        "DesiredCapacity": 6,
                        "LaunchConfigurationName": {
                            "Ref": "LCapp"
                        },
                        "MaxSize": 6,
                        "MinSize": 6,
                        "Tags": [
                            {
                                "Key": "Name",
                                "PropagateAtLaunch": True,
                                "Value": "test::app"
                            }
                        ]
                    },
                    "Type": "AWS::AutoScaling::AutoScalingGroup"
                },
                "LCapp": {
                    "Properties": {
                        "ImageId": "ami-e97f849e",
                        "InstanceMonitoring": "false",
                        "InstanceType": "m1.large",
                        "KeyName": "bootstrap",
                        "SecurityGroups": [],
                        "UserData": {
                            "Fn::Base64": ""
                        }
                    },
                    "Type": "AWS::AutoScaling::LaunchConfiguration"
                }
            }
        }

        cfg = {
            'name': 'test',
            'stage': 'test',
            'instance_access': '1234',
            'instance_secret': '2345',
        }
        res = {
            'load_balancer': [],
            'secgroup': [],
            'instance': [{
                'block_device': [],
                'count': 6,
                'image': 'ami-e97f849e',
                'monitoring': False,
                'name': 'app',
                'provisioner': {
                    'args': {
                        'apps': ['ais-jetty/v2.54-02'],
                        'appBucket': 'test',
                        'roleBucket': 'test',
                        'roles': ['jetty']
                    },
                    'provider': 'awsfw_standalone'},
                'sg': [],
                'size': 'm1.large',
                'sshKey': 'bootstrap'
            }]
        }
        tmpl = out.add_resources(AWSFWProvisioner(), res, cfg)
        assert_equals(json.loads(tmpl), ret)

    @mock.patch('pmcf.provisioners.AWSFWProvisioner.userdata', _mock_ud)
    def test_instance_valid_elb(self):
        out = JSONOutput()
        ret = {
            "AWSTemplateFormatVersion": "2010-09-09",
            "Description": "test test stack",
            "Outputs": {
                "ELBtestDNS": {
                    "Description": "Public DNSName of the ELBtest ELB",
                    "Value": {
                        "Fn::GetAtt": [
                            "ELBtest",
                            "DNSName"
                        ]
                    }
                }
            },
            "Resources": {
                "ELBtest": {
                    "Properties": {
                        "AvailabilityZones": {
                            "Fn::GetAZs": ""
                        },
                        "CrossZone": "true",
                        "HealthCheck": {
                            "HealthyThreshold": 3,
                            "Interval": 5,
                            "Target": "HTTP:80/healthcheck",
                            "Timeout": 2,
                            "UnhealthyThreshold": 3
                        },
                        "Listeners": [
                            {
                                "InstancePort": 80,
                                "InstanceProtocol": "HTTP",
                                "LoadBalancerPort": 80,
                                "Protocol": "HTTP"
                            }
                        ]
                    },
                    "Type": "AWS::ElasticLoadBalancing::LoadBalancer"
                },
                "ASGapp": {
                    "Properties": {
                        "AvailabilityZones": {
                            "Fn::GetAZs": ""
                        },
                        "DesiredCapacity": 6,
                        "LaunchConfigurationName": {
                            "Ref": "LCapp"
                        },
                        "LoadBalancerNames": [
                            {"Ref": "ELBtest"},
                        ],
                        "MaxSize": 6,
                        "MinSize": 6,
                        "Tags": [
                            {
                                "Key": "Name",
                                "PropagateAtLaunch": True,
                                "Value": "test::app"
                            }
                        ]
                    },
                    "Type": "AWS::AutoScaling::AutoScalingGroup"
                },
                "LCapp": {
                    "Properties": {
                        "ImageId": "ami-e97f849e",
                        "InstanceMonitoring": "false",
                        "InstanceType": "m1.large",
                        "KeyName": "bootstrap",
                        "SecurityGroups": [],
                        "UserData": {
                            "Fn::Base64": ""
                        }
                    },
                    "Type": "AWS::AutoScaling::LaunchConfiguration"
                }
            }
        }

        cfg = {
            'name': 'test',
            'stage': 'test'
        }
        res = {
            'load_balancer': [{
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
            }],
            'secgroup': [],
            'instance': [{
                'block_device': [],
                'count': 6,
                'image': 'ami-e97f849e',
                'monitoring': False,
                'name': 'app',
                'lb': 'test',
                'provisioner': {
                    'args': {
                        'apps': ['ais-jetty/v2.54-02'],
                        'appBucket': 'test',
                        'roleBucket': 'test',
                        'roles': ['jetty']
                    },
                    'provider': 'awsfw_standalone'},
                'sg': [],
                'size': 'm1.large',
                'sshKey': 'bootstrap'
            }]
        }
        tmpl = out.add_resources(AWSFWProvisioner(), res, cfg)
        assert_equals(json.loads(tmpl), ret)

    @mock.patch('pmcf.provisioners.AWSFWProvisioner.userdata', _mock_ud)
    def test_instance_valid(self):
        out = JSONOutput()
        ret = {
            "AWSTemplateFormatVersion": "2010-09-09",
            "Description": "test test stack",
            "Resources": {
                "ASGapp": {
                    "Properties": {
                        "AvailabilityZones": {
                            "Fn::GetAZs": ""
                        },
                        "DesiredCapacity": 6,
                        "LaunchConfigurationName": {
                            "Ref": "LCapp"
                        },
                        "MaxSize": 6,
                        "MinSize": 6,
                        "Tags": [
                            {
                                "Key": "Name",
                                "PropagateAtLaunch": True,
                                "Value": "test::app"
                            }
                        ]
                    },
                    "Type": "AWS::AutoScaling::AutoScalingGroup"
                },
                "LCapp": {
                    "Properties": {
                        "ImageId": "ami-e97f849e",
                        "InstanceMonitoring": "false",
                        "InstanceType": "m1.large",
                        "KeyName": "bootstrap",
                        "SecurityGroups": [],
                        "UserData": {
                            "Fn::Base64": ""
                        }
                    },
                    "Type": "AWS::AutoScaling::LaunchConfiguration"
                }
            }
        }

        cfg = {
            'name': 'test',
            'stage': 'test'
        }
        res = {
            'load_balancer': [],
            'secgroup': [],
            'instance': [{
                'block_device': [],
                'count': 6,
                'image': 'ami-e97f849e',
                'monitoring': False,
                'name': 'app',
                'provisioner': {
                    'args': {
                        'apps': ['ais-jetty/v2.54-02'],
                        'appBucket': 'test',
                        'roleBucket': 'test',
                        'roles': ['jetty']
                    },
                    'provider': 'awsfw_standalone'},
                'sg': [],
                'size': 'm1.large',
                'sshKey': 'bootstrap'
            }]
        }
        tmpl = out.add_resources(AWSFWProvisioner(), res, cfg)
        assert_equals(json.loads(tmpl), ret)

    @mock.patch('pmcf.provisioners.AWSFWProvisioner.userdata', _mock_ud)
    def test_instance_invalid_bad_provisioner(self):
        out = JSONOutput()
        cfg = {
            'name': 'test',
            'stage': 'test'
        }
        res = {
            'load_balancer': [],
            'secgroup': [],
            'instance': [{
                'block_device': [],
                'count': 6,
                'image': 'ami-e97f849e',
                'monitoring': False,
                'name': 'app',
                'provisioner': {
                    'args': {
                        'apps': ['ais-jetty/v2.54-02'],
                        'appBucket': 'test',
                        'roleBucket': 'test',
                        'roles': ['jetty']
                    },
                    'provider': 'puppet'},
                'sg': [],
                'size': 'm1.large',
                'sshKey': 'bootstrap'
            }]
        }
        assert_raises(ProvisionerException, out.add_resources,
                      AWSFWProvisioner(), res, cfg)

    def test_run(self):
        assert_equals(True, JSONOutput().run('', {}))
