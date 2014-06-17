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
from nose.tools import assert_equals
import sys

from pmcf.outputs import JSONOutput


def _mock_ud(self, args):
    return ''


class TestJSONOutput(object):

    def test_role_valid(self):
        out = JSONOutput()
        ret = {
            "AWSTemplateFormatVersion": "2010-09-09",
            "Description": "test test stack",
            "Resources": {
                "Policytest": {
                    "Properties": {
                        "PolicyDocument": {
                            "Statement": [{
                                "Action": [
                                    "s3:GetObject"
                                ],
                                "Effect": "Allow",
                                "Resource": [
                                    "arn:aws:s3:::%s/%s/%s/%s/%s" % (
                                        "wibble",
                                        "infrastructure",
                                        "test",
                                        "test",
                                        "foo.zip"
                                    ),
                                    "arn:aws:s3:::%s/%s/%s/%s/%s" % (
                                        "wibble",
                                        "application",
                                        "test",
                                        "test",
                                        "bar.zip"
                                    )
                                ]
                            }],
                            "Version": "2012-10-17"
                        },
                        "PolicyName": "iam-test-test",
                        "Roles": [{"Ref": "Roletest"}]
                    },
                    "Type": "AWS::IAM::Policy"
                },
                "Profiletest": {
                    "Properties": {
                        "Path": "/test/test/",
                        "Roles": [{"Ref": "Roletest"}]
                    },
                    "Type": "AWS::IAM::InstanceProfile"
                },
                "Roletest": {
                    "Properties": {
                        "AssumeRolePolicyDocument": {
                            "Statement": [{
                                "Action": [
                                    "sts:AssumeRole"
                                ],
                                "Effect": "Allow",
                                "Principal": {
                                    "Service": ["ec2.amazonaws.com"]
                                }
                            }],
                            "Version": "2012-10-17"
                        },
                        "Path": "/test/test/"
                    },
                    "Type": "AWS::IAM::Role"
                }
            }
        }

        cfg = {
            'name': 'test',
            'environment': 'test',
            'artifact_bucket': 'wibble',
        }
        res = {
            'instance': [],
            'secgroup': [],
            'role': [{
                'name': 'test',
                'access': {
                    'infrastructure': 'foo.zip',
                    'application': 'bar.zip',
                }
            }],
            'load_balancer': []
        }
        tmpl = out.add_resources(res, cfg)
        assert_equals(json.loads(tmpl), ret)

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
            'environment': 'test'
        }
        res = {
            'instance': [],
            'secgroup': [],
            'role': [],
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
        tmpl = out.add_resources(res, cfg)
        assert_equals(json.loads(tmpl), ret)

    def test_lb_valid_internal(self):
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
                        "Subnets": [
                            "subnet-123"
                        ],
                        "Scheme": "internal",
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
            'environment': 'test',
        }
        res = {
            'instance': [],
            'secgroup': [],
            'role': [],
            'load_balancer': [{
                'listener': [
                    {
                        'instance_port': 80,
                        'protocol': 'HTTP',
                        'lb_port': 80,
                        'instance_protocol': 'HTTP',
                    }
                ],
                'internal': True,
                'subnets': ['subnet-123'],
                'healthcheck': {
                    'path': '/healthcheck',
                    'protocol': 'HTTP',
                    'port': 80
                },
                'name': 'test',
                'policy': [],
            }]
        }
        tmpl = out.add_resources(res, cfg)
        assert_equals(json.loads(tmpl), ret)

    def test_lb_valid_sg(self):
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
                "sgelb": {
                    "Properties": {
                        "GroupDescription": "security group for elb",
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
                },
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
                        ],
                        "SecurityGroups": [{"Ref": "sgelb"}],
                    },
                    "Type": "AWS::ElasticLoadBalancing::LoadBalancer"
                }
            }
        }

        cfg = {
            'name': 'test',
            'environment': 'test'
        }
        res = {
            'instance': [],
            'role': [],
            'secgroup': [{
                'name': 'elb',
                'rules': [
                    {
                        'port': 80,
                        'protocol': 'tcp',
                        'source_cidr': '10.1.2.0/24'
                    }
                ]
            }],
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
                'sg': ['elb'],
                'policy': [],
            }]
        }
        tmpl = out.add_resources(res, cfg)
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
            'environment': 'test'
        }
        res = {
            'instance': [],
            'secgroup': [],
            'role': [],
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
        tmpl = out.add_resources(res, cfg)
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
            'environment': 'test'
        }
        res = {
            'instance': [],
            'secgroup': [],
            'role': [],
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
        tmpl = out.add_resources(res, cfg)
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
            'environment': 'test'
        }
        res = {
            'instance': [],
            'load_balancer': [],
            'role': [],
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
        tmpl = out.add_resources(res, cfg)
        assert_equals(json.loads(tmpl), ret)

    def test_sg_valid_ref_vpc(self):
        out = JSONOutput()
        ret = {
            "AWSTemplateFormatVersion": "2010-09-09",
            "Description": "test test stack",
            "Resources": {
                "sgwomble": {
                    "Properties": {
                        "GroupDescription": "security group for womble",
                        "SecurityGroupIngress": [
                            {
                                "CidrIp": "10.0.0.0/8",
                                "FromPort": 80,
                                "IpProtocol": "tcp",
                                "ToPort": 80
                            }
                        ],
                        "VpcId": "vpc-123",
                    },
                    "Type": "AWS::EC2::SecurityGroup"
                },
                "sgtest": {
                    "Properties": {
                        "GroupDescription": "security group for test",
                        "SecurityGroupIngress": [
                            {
                                "SourceSecurityGroupId": {"Ref": "sgwomble"},
                                "FromPort": 80,
                                "IpProtocol": "tcp",
                                "ToPort": 80
                            }
                        ],
                        "VpcId": "vpc-123",
                    },
                    "Type": "AWS::EC2::SecurityGroup"
                }
            }
        }

        cfg = {
            'name': 'test',
            'environment': 'test',
            'vpcid': 'vpc-123',
        }
        res = {
            'instance': [],
            'load_balancer': [],
            'role': [],
            'secgroup': [
                {
                    'name': 'womble',
                    'rules': [
                        {
                            'port': 80,
                            'protocol': 'tcp',
                            'source_cidr': '10.0.0.0/8'
                        }
                    ]
                },
                {
                    'name': 'test',
                    'rules': [
                        {
                            'port': 80,
                            'protocol': 'tcp',
                            'source_group': '=womble'
                        }
                    ]
                }
            ]
        }
        tmpl = out.add_resources(res, cfg)
        assert_equals(json.loads(tmpl), ret)

    def test_sg_valid_ref(self):
        out = JSONOutput()
        ret = {
            "AWSTemplateFormatVersion": "2010-09-09",
            "Description": "test test stack",
            "Resources": {
                "sgwomble": {
                    "Properties": {
                        "GroupDescription": "security group for womble",
                        "SecurityGroupIngress": [
                            {
                                "CidrIp": "10.0.0.0/8",
                                "FromPort": 80,
                                "IpProtocol": "tcp",
                                "ToPort": 80
                            }
                        ]
                    },
                    "Type": "AWS::EC2::SecurityGroup"
                },
                "sgtest": {
                    "Properties": {
                        "GroupDescription": "security group for test",
                        "SecurityGroupIngress": [
                            {
                                "SourceSecurityGroupName": {"Ref": "sgwomble"},
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
            'environment': 'test'
        }
        res = {
            'instance': [],
            'load_balancer': [],
            'role': [],
            'secgroup': [
                {
                    'name': 'womble',
                    'rules': [
                        {
                            'port': 80,
                            'protocol': 'tcp',
                            'source_cidr': '10.0.0.0/8'
                        }
                    ]
                },
                {
                    'name': 'test',
                    'rules': [
                        {
                            'port': 80,
                            'protocol': 'tcp',
                            'source_group': '=womble'
                        }
                    ]
                }
            ]
        }
        tmpl = out.add_resources(res, cfg)
        assert_equals(json.loads(tmpl), ret)

    def test_sg_valid_owner_form(self):
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
                                "SourceSecurityGroupOwnerId": "wibble",
                                "SourceSecurityGroupName": "wobble",
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
            'environment': 'test'
        }
        res = {
            'instance': [],
            'load_balancer': [],
            'role': [],
            'secgroup': [{
                'name': 'test',
                'rules': [
                    {
                        'port': 80,
                        'protocol': 'tcp',
                        'source_group': 'wibble/wobble',
                    }
                ]
            }]
        }
        tmpl = out.add_resources(res, cfg)
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
            'environment': 'test'
        }
        res = {
            'instance': [],
            'load_balancer': [],
            'role': [],
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
        tmpl = out.add_resources(res, cfg)
        assert_equals(json.loads(tmpl), ret)

    def test_sg_valid_short_form_vpc(self):
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
                                "ToPort": 80,
                            }
                        ],
                        "VpcId": "vpc-123",
                    },
                    "Type": "AWS::EC2::SecurityGroup"
                }
            }
        }

        cfg = {
            'name': 'test',
            'environment': 'test',
            'vpcid': 'vpc-123',
        }
        res = {
            'instance': [],
            'load_balancer': [],
            'role': [],
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
        tmpl = out.add_resources(res, cfg)
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
                            },
                            {
                                "Key": "App",
                                "PropagateAtLaunch": True,
                                "Value": "app"
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
            'environment': 'test',
            'instance_accesskey': '1234',
            'instance_secretkey': '2345',
        }
        res = {
            'load_balancer': [],
            'secgroup': [],
            'role': [],
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
                    'provider': 'AWSFWProvisioner'},
                'sg': [],
                'size': 'm1.large',
                'sshKey': 'bootstrap'
            }]
        }
        tmpl = out.add_resources(res, cfg)
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
                            },
                            {
                                "Key": "App",
                                "PropagateAtLaunch": True,
                                "Value": "app"
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
            'environment': 'test'
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
            'role': [],
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
                    'provider': 'AWSFWProvisioner'},
                'sg': [],
                'size': 'm1.large',
                'sshKey': 'bootstrap'
            }]
        }
        tmpl = out.add_resources(res, cfg)
        assert_equals(json.loads(tmpl), ret)

    @mock.patch('pmcf.provisioners.AWSFWProvisioner.userdata', _mock_ud)
    def test_instance_valid_secgroup(self):
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
                            },
                            {
                                "Key": "App",
                                "PropagateAtLaunch": True,
                                "Value": "app"
                            }
                        ]
                    },
                    "Type": "AWS::AutoScaling::AutoScalingGroup"
                },
                "LCapp": {
                    "Properties": {
                        "IamInstanceProfile": "deploy-client",
                        "ImageId": "ami-e97f849e",
                        "InstanceMonitoring": "false",
                        "InstanceType": "m1.large",
                        "KeyName": "bootstrap",
                        "SecurityGroups": ["app"],
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
            'environment': 'test'
        }
        res = {
            'load_balancer': [],
            'secgroup': [],
            'role': [],
            'instance': [{
                'block_device': [],
                'count': 6,
                'image': 'ami-e97f849e',
                'monitoring': False,
                'name': 'app',
                'profile': 'deploy-client',
                'provisioner': {
                    'args': {
                        'apps': ['ais-jetty/v2.54-02'],
                        'appBucket': 'test',
                        'roleBucket': 'test',
                        'roles': ['jetty']
                    },
                    'provider': 'AWSFWProvisioner'},
                'sg': ['app'],
                'size': 'm1.large',
                'sshKey': 'bootstrap'
            }]
        }
        tmpl = out.add_resources(res, cfg)
        assert_equals(json.loads(tmpl), ret)

    @mock.patch('pmcf.provisioners.AWSFWProvisioner.userdata', _mock_ud)
    def test_instance_valid_ref_secgroup(self):
        out = JSONOutput()
        ret = {
            "AWSTemplateFormatVersion": "2010-09-09",
            "Description": "test test stack",
            "Resources": {
                "sgapp": {
                    "Properties": {
                        "GroupDescription": "security group for app",
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
                        "MaxSize": 6,
                        "MinSize": 6,
                        "Tags": [
                            {
                                "Key": "Name",
                                "PropagateAtLaunch": True,
                                "Value": "test::app"
                            },
                            {
                                "Key": "App",
                                "PropagateAtLaunch": True,
                                "Value": "app"
                            }
                        ]
                    },
                    "Type": "AWS::AutoScaling::AutoScalingGroup"
                },
                "LCapp": {
                    "Properties": {
                        "IamInstanceProfile": "deploy-client",
                        "ImageId": "ami-e97f849e",
                        "InstanceMonitoring": "false",
                        "InstanceType": "m1.large",
                        "KeyName": "bootstrap",
                        "SecurityGroups": [{"Ref": "sgapp"}],
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
            'environment': 'test'
        }
        res = {
            'load_balancer': [],
            'role': [],
            'secgroup': [
                {
                    'name': 'app',
                    'rules': [
                        {
                            'port': 80,
                            'protocol': 'tcp',
                            'source_cidr': '10.1.2.0/24'
                        }
                    ]
                }
            ],
            'instance': [{
                'block_device': [],
                'count': 6,
                'image': 'ami-e97f849e',
                'monitoring': False,
                'name': 'app',
                'profile': 'deploy-client',
                'provisioner': {
                    'args': {
                        'apps': ['ais-jetty/v2.54-02'],
                        'appBucket': 'test',
                        'roleBucket': 'test',
                        'roles': ['jetty']
                    },
                    'provider': 'AWSFWProvisioner'},
                'sg': ['app'],
                'size': 'm1.large',
                'sshKey': 'bootstrap'
            }]
        }
        tmpl = out.add_resources(res, cfg)
        assert_equals(json.loads(tmpl), ret)

    @mock.patch('pmcf.provisioners.AWSFWProvisioner.userdata', _mock_ud)
    def test_instance_valid_instance_profile(self):
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
                            },
                            {
                                "Key": "App",
                                "PropagateAtLaunch": True,
                                "Value": "app"
                            }
                        ]
                    },
                    "Type": "AWS::AutoScaling::AutoScalingGroup"
                },
                "LCapp": {
                    "Properties": {
                        "IamInstanceProfile": "deploy-client",
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
            'environment': 'test'
        }
        res = {
            'load_balancer': [],
            'secgroup': [],
            'role': [],
            'instance': [{
                'block_device': [],
                'count': 6,
                'image': 'ami-e97f849e',
                'monitoring': False,
                'name': 'app',
                'profile': 'deploy-client',
                'provisioner': {
                    'args': {
                        'apps': ['ais-jetty/v2.54-02'],
                        'appBucket': 'test',
                        'roleBucket': 'test',
                        'roles': ['jetty']
                    },
                    'provider': 'AWSFWProvisioner'},
                'sg': [],
                'size': 'm1.large',
                'sshKey': 'bootstrap'
            }]
        }
        tmpl = out.add_resources(res, cfg)
        assert_equals(json.loads(tmpl), ret)

    @mock.patch('pmcf.provisioners.PuppetProvisioner.cfn_init', _mock_ud)
    @mock.patch('pmcf.provisioners.PuppetProvisioner.userdata', _mock_ud)
    def test_instance_valid_puppet(self):
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
                            },
                            {
                                "Key": "App",
                                "PropagateAtLaunch": True,
                                "Value": "app"
                            }
                        ]
                    },
                    "Type": "AWS::AutoScaling::AutoScalingGroup"
                },
                "LCapp": {
                    "Metadata": "",
                    "Properties": {
                        "ImageId": "ami-e97f849e",
                        "InstanceMonitoring": "false",
                        "InstanceType": "m1.large",
                        "KeyName": "bootstrap",
                        "SecurityGroups": [],
                        "UserData": {
                            "Fn::Base64": ""
                        },
                    },
                    "Type": "AWS::AutoScaling::LaunchConfiguration"
                },
                "appHandle": {
                    "Type": "AWS::CloudFormation::WaitConditionHandle"
                },
                "appWait": {
                    "DependsOn": "ASGapp",
                    "Properties": {
                        "Handle": {
                            "Ref": "appHandle"
                        },
                        "Timeout": 3600,
                        "Count": 6,
                    },
                    "Type": "AWS::CloudFormation::WaitCondition"
                }
            }
        }

        cfg = {
            'name': 'test',
            'environment': 'test'
        }
        res = {
            'load_balancer': [],
            'secgroup': [],
            'role': [],
            'instance': [{
                'block_device': [],
                'count': 6,
                'image': 'ami-e97f849e',
                'monitoring': False,
                'name': 'app',
                'provisioner': {
                    'args': {},
                    'provider': 'PuppetProvisioner'},
                'sg': [],
                'size': 'm1.large',
                'sshKey': 'bootstrap'
            }]
        }
        tmpl = out.add_resources(res, cfg)
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
                            },
                            {
                                "Key": "App",
                                "PropagateAtLaunch": True,
                                "Value": "app"
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
            'environment': 'test'
        }
        res = {
            'load_balancer': [],
            'secgroup': [],
            'role': [],
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
                    'provider': 'AWSFWProvisioner'},
                'sg': [],
                'size': 'm1.large',
                'sshKey': 'bootstrap'
            }]
        }
        tmpl = out.add_resources(res, cfg)
        assert_equals(json.loads(tmpl), ret)

    def test_run(self):
        sys.stdout = open('/dev/null', 'w')
        assert_equals(True, JSONOutput().run('', {}))
