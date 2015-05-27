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


def _mock_tp(self):
    return ['OldestInstance']


class TestJSONOutput(object):

    def test_cache_valid(self):
        out = JSONOutput()
        ret = {
            "AWSTemplateFormatVersion": "2010-09-09", 
            "Description": "test test stack", 
            "Resources": {
                "CacheSubnetGrouptest": {
                    "Properties": {
                        "SubnetIds": [
                            "a", 
                            "b", 
                            "c"
                        ], 
                        "Description": "Subnet Group for test"
                    }, 
                    "Type": "AWS::ElastiCache::SubnetGroup"
                }, 
                "Cachetest": {
                    "Properties": {
                        "Engine": "redis", 
                        "VpcSecurityGroupIds": [
                            "sg-1234"
                        ], 
                        "NumCacheNodes": 1, 
                        "CacheSubnetGroupName": {
                            "Ref": "CacheSubnetGrouptest"
                        }, 
                        "ClusterName": "testtest", 
                        "CacheParameterGroupName": "default.redis2.8", 
                        "CacheNodeType": "cache.t2.micro"
                    }, 
                    "Type": "AWS::ElastiCache::CacheCluster"
                }
            }
        }

        cfg = {
            'name': 'test',
            'environment': 'test',
            'subnets': ['a','b','c'],
        }
        res = {
            'instance': [],
            'secgroup': [],
            'role': [],
            'load_balancer': [],
            'cache': [{
                'name': 'test',
                'params': {
                    'name': 'default.redis2.8',
                },
                'size': 'cache.t2.micro',
                'type': 'redis',
                'count': 1,
                'sg': ['sg-1234'],
            }]
        }
        tmpl = out.add_resources(res, cfg)
        assert_equals(json.loads(tmpl), ret)

    def test_cache_valid_sg_ref(self):
        out = JSONOutput()
        ret = {
            "AWSTemplateFormatVersion": "2010-09-09", 
            "Description": "test test stack", 
            "Resources": {
                "CacheSubnetGrouptest": {
                    "Properties": {
                        "SubnetIds": [
                            "a", 
                            "b", 
                            "c"
                        ], 
                        "Description": "Subnet Group for test"
                    }, 
                    "Type": "AWS::ElastiCache::SubnetGroup"
                }, 
                "Cachetest": {
                    "Properties": {
                        "Engine": "redis", 
                        "VpcSecurityGroupIds": [
                            {
                                "Ref": "sgredis"
                            }
                        ], 
                        "NumCacheNodes": 1, 
                        "CacheSubnetGroupName": {
                            "Ref": "CacheSubnetGrouptest"
                        }, 
                        "ClusterName": "testtest", 
                        "CacheParameterGroupName": "default.redis2.8", 
                        "CacheNodeType": "cache.t2.micro"
                    }, 
                    "Type": "AWS::ElastiCache::CacheCluster"
                }, 
                "sgredis": {
                    "Properties": {
                        "SecurityGroupIngress": [], 
                        "GroupDescription": "security group for redis"
                    }, 
                    "Type": "AWS::EC2::SecurityGroup"
                }
            }
        }

        cfg = {
            'name': 'test',
            'environment': 'test',
            'subnets': ['a','b','c'],
        }
        res = {
            'instance': [],
            'secgroup': [{
                'name': 'redis',
                'rules': []
            }],
            'role': [],
            'load_balancer': [],
            'cache': [{
                'name': 'test',
                'params': {
                    'name': 'default.redis2.8',
                },
                'size': 'cache.t2.micro',
                'type': 'redis',
                'count': 1,
                'sg': ['redis'],
            }]
        }
        tmpl = out.add_resources(res, cfg)
        assert_equals(json.loads(tmpl), ret)

    def test_cache_valid_cache_params(self):
        out = JSONOutput()
        ret = {
            "AWSTemplateFormatVersion": "2010-09-09", 
            "Description": "test test stack", 
            "Resources": {
                "CacheSubnetGrouptest": {
                    "Properties": {
                        "SubnetIds": [
                            "a", 
                            "b", 
                            "c"
                        ], 
                        "Description": "Subnet Group for test"
                    }, 
                    "Type": "AWS::ElastiCache::SubnetGroup"
                }, 
                "CacheParamstest": {
                    "Properties": {
                        "CacheParameterGroupFamily": "test", 
                        "Properties": {
                            "a": "b"
                        }, 
                        "Description": "Cache ParameterGroup for test"
                    }, 
                    "Type": "AWS::ElastiCache::ParameterGroup"
                }, 
                "Cachetest": {
                    "Properties": {
                        "Engine": "redis", 
                        "VpcSecurityGroupIds": [
                            "sg-1234"
                        ], 
                        "NumCacheNodes": 1, 
                        "CacheSubnetGroupName": {
                            "Ref": "CacheSubnetGrouptest"
                        }, 
                        "ClusterName": "testtest", 
                        "CacheParameterGroupName": {
                            "Ref": "CacheParamstest"
                        }, 
                        "CacheNodeType": "cache.t2.micro"
                    }, 
                    "Type": "AWS::ElastiCache::CacheCluster"
                }
            }
        }

        cfg = {
            'name': 'test',
            'environment': 'test',
            'subnets': ['a','b','c'],
        }
        res = {
            'instance': [],
            'secgroup': [],
            'role': [],
            'load_balancer': [],
            'cache': [{
                'name': 'test',
                'params': {
                    'name': 'test',
                    'params': {
                        "a": "b",
                    },
                },
                'size': 'cache.t2.micro',
                'type': 'redis',
                'count': 1,
                'sg': ['sg-1234'],
            }]
        }
        tmpl = out.add_resources(res, cfg)
        assert_equals(json.loads(tmpl), ret)

    def test_queue_valid(self):
        out = JSONOutput()
        ret = {
            'AWSTemplateFormatVersion': '2010-09-09',
            'Description': 'test test stack',
            'Resources': {
                'SQStest': {
                    'Properties': {
                        'MessageRetentionPeriod': 60,
                        'QueueName': 'test'
                    },
                    'Type': 'AWS::SQS::Queue'
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
            'load_balancer': [],
            'queue': [
                {
                    'name': 'test'
                }
            ]
        }
        tmpl = out.add_resources(res, cfg)
        assert_equals(json.loads(tmpl), ret)

    def test_network_valid(self):
        out = JSONOutput()
        ret = {
            "AWSTemplateFormatVersion": "2010-09-09",
            "Description": "test test stack",
            "Resources": {
                "RTtest": {
                    "Properties": {
                        "Tags": [{"Key": "Name", "Value": "test"}],
                        "VpcId": {"Ref": "VPCtest"}
                    },
                    "Type": "AWS::EC2::RouteTable"
                },
                "VPCtest": {
                    "Properties": {
                        "CidrBlock": "10.0.0.0/8",
                        "EnableDnsHostnames": "true",
                        "EnableDnsSupport": "true",
                        "Tags": [{"Key": "Name", "Value": "test"}]},
                    "Type": "AWS::EC2::VPC"
                },
                "testSRTA0": {
                    "Properties": {
                        "RouteTableId": {"Ref": "RTtest"},
                        "SubnetId": {"Ref": "testSubnet0"}
                    },
                    "Type": "AWS::EC2::SubnetRouteTableAssociation"
                },
                "testSRTA1": {
                    "Properties": {
                        "RouteTableId": {"Ref": "RTtest"},
                        "SubnetId": {"Ref": "testSubnet1"}
                    },
                    "Type": "AWS::EC2::SubnetRouteTableAssociation"
                },
                "testSubnet0": {
                    "Properties": {
                        "AvailabilityZone": "a",
                        "CidrBlock": "10.0.0.0/9",
                        "Tags": [
                            {"Key": "Name", "Value": "test-a"},
                            {"Key": "Public", "Value": False}
                        ],
                        "VpcId": {"Ref": "VPCtest"}
                    },
                    "Type": "AWS::EC2::Subnet"
                },
                "testSubnet1": {
                    "Properties": {
                        "AvailabilityZone": "b",
                        "CidrBlock": "10.128.0.0/9",
                        "Tags": [
                            {"Key": "Name", "Value": "test-b"},
                            {"Key": "Public", "Value": False}
                        ],
                        "VpcId": {"Ref": "VPCtest"}
                    },
                    "Type": "AWS::EC2::Subnet"
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
            'load_balancer': [],
            'network': [
                {
                    'name': 'test',
                    'netrange': '10.0.0.0/8',
                    'public': False,
                    'subnets': [
                        {
                            'name': 'test-a',
                            'cidr': '10.0.0.0/9',
                            'zone': 'a',
                            'public': False,
                        },
                        {
                            'name': 'test-b',
                            'cidr': '10.128.0.0/9',
                            'zone': 'b',
                            'public': False,
                        },
                    ],
                    'zones': ['a', 'b']
                }
            ]
        }
        tmpl = out.add_resources(res, cfg)
        assert_equals(json.loads(tmpl), ret)

    def test_network_valid_sg_ref(self):
        out = JSONOutput()
        ret = {
            "AWSTemplateFormatVersion": "2010-09-09",
            "Description": "test test stack",
            "Resources": {
                "RTtest": {
                    "Properties": {
                        "Tags": [{"Key": "Name", "Value": "test"}],
                        "VpcId": {"Ref": "VPCtest"}
                    },
                    "Type": "AWS::EC2::RouteTable"
                },
                "VPCtest": {
                    "Properties": {
                        "CidrBlock": "10.0.0.0/8",
                        "EnableDnsHostnames": "true",
                        "EnableDnsSupport": "true",
                        "Tags": [{"Key": "Name", "Value": "test"}]},
                    "Type": "AWS::EC2::VPC"
                },
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
                        ],
                        "VpcId": {
                            "Ref": "VPCtest"
                        }
                    },
                    "Type": "AWS::EC2::SecurityGroup"
                },
                "testSRTA0": {
                    "Properties": {
                        "RouteTableId": {"Ref": "RTtest"},
                        "SubnetId": {"Ref": "testSubnet0"}
                    },
                    "Type": "AWS::EC2::SubnetRouteTableAssociation"
                },
                "testSRTA1": {
                    "Properties": {
                        "RouteTableId": {"Ref": "RTtest"},
                        "SubnetId": {"Ref": "testSubnet1"}
                    },
                    "Type": "AWS::EC2::SubnetRouteTableAssociation"
                },
                "testSubnet0": {
                    "Properties": {
                        "AvailabilityZone": "a",
                        "CidrBlock": "10.0.0.0/9",
                        "Tags": [
                            {"Key": "Name", "Value": "test-a"},
                            {"Key": "Public", "Value": False}
                        ],
                        "VpcId": {"Ref": "VPCtest"}
                    },
                    "Type": "AWS::EC2::Subnet"
                },
                "testSubnet1": {
                    "Properties": {
                        "AvailabilityZone": "b",
                        "CidrBlock": "10.128.0.0/9",
                        "Tags": [
                            {"Key": "Name", "Value": "test-b"},
                            {"Key": "Public", "Value": False}
                        ],
                        "VpcId": {"Ref": "VPCtest"}
                    },
                    "Type": "AWS::EC2::Subnet"
                }
            }
        }
        cfg = {
            'name': 'test',
            'environment': 'test'
        }
        res = {
            'instance': [],
            'secgroup': [{
                'name': 'test',
                'vpcid': '=test',
                'rules': [
                    {
                        'port': 80,
                        'protocol': 'tcp',
                        'source_cidr': '10.1.2.0/24'
                    }
                ]
            }],
            'role': [],
            'load_balancer': [],
            'network': [
                {
                    'name': 'test',
                    'netrange': '10.0.0.0/8',
                    'public': False,
                    'subnets': [
                        {
                            'name': 'test-a',
                            'cidr': '10.0.0.0/9',
                            'zone': 'a',
                            'public': False,
                        },
                        {
                            'name': 'test-b',
                            'cidr': '10.128.0.0/9',
                            'zone': 'b',
                            'public': False,
                        },
                    ],
                    'zones': ['a', 'b']
                }
            ]
        }
        tmpl = out.add_resources(res, cfg)
        assert_equals(json.loads(tmpl), ret)

    def test_network_valid_public(self):
        out = JSONOutput()
        ret = {
            "AWSTemplateFormatVersion": "2010-09-09",
            "Description": "test test stack",
            "Resources": {
                "RTtest": {
                    "Type": "AWS::EC2::RouteTable",
                    "Properties": {
                        "Tags": [
                            {
                                "Key": "Name",
                                "Value": "test"
                            }
                        ],
                        "VpcId": {
                            "Ref": "VPCtest"
                        }
                    }
                },
                "testSRTA1": {
                    "Type": "AWS::EC2::SubnetRouteTableAssociation",
                    "Properties": {
                        "SubnetId": {
                            "Ref": "testSubnet1"
                        },
                        "RouteTableId": {
                            "Ref": "RTtest"
                        }
                    }
                },
                "testSRTA0": {
                    "Type": "AWS::EC2::SubnetRouteTableAssociation",
                    "Properties": {
                        "SubnetId": {
                            "Ref": "testSubnet0"
                        },
                        "RouteTableId": {
                            "Ref": "RTtest"
                        }
                    }
                },
                "testSubnet0": {
                    "Type": "AWS::EC2::Subnet",
                    "Properties": {
                        "AvailabilityZone": "a",
                        "CidrBlock": "10.0.0.0/9",
                        "Tags": [
                            {
                                "Key": "Name",
                                "Value": "test-a"
                            },
                            {
                                "Key": "Public",
                                "Value": True,
                            }
                        ],
                        "VpcId": {
                            "Ref": "VPCtest"
                        }
                    }
                },
                "IGtest": {
                    "Type": "AWS::EC2::InternetGateway",
                    "Properties": {
                        "Tags": [
                            {
                                "Key": "Name",
                                "Value": "test"
                            }
                        ]
                    }
                },
                "VPCIGtest": {
                    "Type": "AWS::EC2::VPCGatewayAttachment",
                    "Properties": {
                        "InternetGatewayId": {
                            "Ref": "IGtest"
                        },
                        "VpcId": {
                            "Ref": "VPCtest"
                        }
                    }
                },
                "VPCtest": {
                    "Type": "AWS::EC2::VPC",
                    "Properties": {
                        "CidrBlock": "10.0.0.0/8",
                        "EnableDnsHostnames": "true",
                        "Tags": [
                            {
                                "Key": "Name",
                                "Value": "test"
                            }
                        ],
                        "EnableDnsSupport": "true"
                    }
                },
                "DefaultRoutetest": {
                    "Type": "AWS::EC2::Route",
                    "Properties": {
                        "GatewayId": {
                            "Ref": "IGtest"
                        },
                        "DestinationCidrBlock": "0.0.0.0/0",
                        "RouteTableId": {
                            "Ref": "RTtest"
                        }
                    },
                    "DependsOn": "VPCIGtest"
                },
                "testSubnet1": {
                    "Type": "AWS::EC2::Subnet",
                    "Properties": {
                        "AvailabilityZone": "b",
                        "CidrBlock": "10.128.0.0/9",
                        "Tags": [
                            {
                                "Key": "Name",
                                "Value": "test-b"
                            },
                            {
                                "Key": "Public",
                                "Value": True,
                            }
                        ],
                        "VpcId": {
                            "Ref": "VPCtest"
                        }
                    }
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
            'load_balancer': [],
            'network': [
                {
                    'name': 'test',
                    'netrange': '10.0.0.0/8',
                    'public': True,
                    'subnets': [
                        {
                            'name': 'test-a',
                            'cidr': '10.0.0.0/9',
                            'zone': 'a',
                            'public': True,
                        },
                        {
                            'name': 'test-b',
                            'cidr': '10.128.0.0/9',
                            'zone': 'b',
                            'public': True,
                        },
                    ],
                    'zones': ['a', 'b']
                }
            ]
        }
        tmpl = out.add_resources(res, cfg)
        assert_equals(json.loads(tmpl), ret)

    def test_network_valid_public_and_private(self):
        out = JSONOutput()
        ret = {
            "AWSTemplateFormatVersion": "2010-09-09", 
            "Description": "test test stack", 
            "Resources": {
                "VPCIGtest": {
                    "Properties": {
                        "VpcId": {
                            "Ref": "VPCtest"
                        }, 
                        "InternetGatewayId": {
                            "Ref": "IGtest"
                        }
                    }, 
                    "Type": "AWS::EC2::VPCGatewayAttachment"
                }, 
                "testSubnet1": {
                    "Properties": {
                        "AvailabilityZone": "b", 
                        "VpcId": {
                            "Ref": "VPCtest"
                        }, 
                        "CidrBlock": "10.128.0.0/9", 
                        "Tags": [
                            {
                                "Value": "test-b", 
                                "Key": "Name"
                            }, 
                            {
                                "Value": False, 
                                "Key": "Public"
                            }
                        ]
                    }, 
                    "Type": "AWS::EC2::Subnet"
                }, 
                "testSubnet0": {
                    "Properties": {
                        "AvailabilityZone": "a", 
                        "VpcId": {
                            "Ref": "VPCtest"
                        }, 
                        "CidrBlock": "10.0.0.0/9", 
                        "Tags": [
                            {
                                "Value": "test-a", 
                                "Key": "Name"
                            }, 
                            {
                                "Value": True, 
                                "Key": "Public"
                            }
                        ]
                    }, 
                    "Type": "AWS::EC2::Subnet"
                }, 
                "testSRTA0": {
                    "Properties": {
                        "SubnetId": {
                            "Ref": "testSubnet0"
                        }, 
                        "RouteTableId": {
                            "Ref": "RTtestpublic"
                        }
                    }, 
                    "Type": "AWS::EC2::SubnetRouteTableAssociation"
                }, 
                "testSRTA1": {
                    "Properties": {
                        "SubnetId": {
                            "Ref": "testSubnet1"
                        }, 
                        "RouteTableId": {
                            "Ref": "RTtest"
                        }
                    }, 
                    "Type": "AWS::EC2::SubnetRouteTableAssociation"
                }, 
                "RTtestpublic": {
                    "Properties": {
                        "VpcId": {
                            "Ref": "VPCtest"
                        }, 
                        "Tags": [
                            {
                                "Value": "testpublic", 
                                "Key": "Name"
                            }
                        ]
                    }, 
                    "Type": "AWS::EC2::RouteTable"
                }, 
                "IGtest": {
                    "Properties": {
                        "Tags": [
                            {
                                "Value": "test", 
                                "Key": "Name"
                            }
                        ]
                    }, 
                    "Type": "AWS::EC2::InternetGateway"
                }, 
                "DefaultRoutetestpublic": {
                    "Properties": {
                        "DestinationCidrBlock": "0.0.0.0/0", 
                        "GatewayId": {
                            "Ref": "IGtest"
                        }, 
                        "RouteTableId": {
                            "Ref": "RTtestpublic"
                        }
                    }, 
                    "Type": "AWS::EC2::Route", 
                    "DependsOn": "VPCIGtest"
                }, 
                "RTtest": {
                    "Properties": {
                        "VpcId": {
                            "Ref": "VPCtest"
                        }, 
                        "Tags": [
                            {
                                "Value": "test", 
                                "Key": "Name"
                            }
                        ]
                    }, 
                    "Type": "AWS::EC2::RouteTable"
                }, 
                "VPCtest": {
                    "Properties": {
                        "EnableDnsSupport": "true", 
                        "CidrBlock": "10.0.0.0/8", 
                        "Tags": [
                            {
                                "Value": "test", 
                                "Key": "Name"
                            }
                        ], 
                        "EnableDnsHostnames": "true"
                    }, 
                    "Type": "AWS::EC2::VPC"
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
            'load_balancer': [],
            'network': [
                {
                    'name': 'test',
                    'netrange': '10.0.0.0/8',
                    'public': True,
                    'subnets': [
                        {
                            'name': 'test-a',
                            'cidr': '10.0.0.0/9',
                            'zone': 'a',
                            'public': True,
                        },
                        {
                            'name': 'test-b',
                            'cidr': '10.128.0.0/9',
                            'zone': 'b',
                            'public': False,
                        },
                    ],
                    'zones': ['a', 'b']
                }
            ]
        }
        tmpl = out.add_resources(res, cfg)
        assert_equals(json.loads(tmpl), ret)

    def test_network_valid_vpn(self):
        out = JSONOutput()
        ret = {
            "AWSTemplateFormatVersion": "2010-09-09",
            "Description": "test test stack",
            "Resources": {
                "RTtest": {
                    "Properties": {
                        "VpcId": {
                            "Ref": "VPCtest"
                        },
                        "Tags": [
                            {
                                "Value": "test",
                                "Key": "Name"
                            }
                        ]
                    },
                    "Type": "AWS::EC2::RouteTable"
                },
                "testCG0": {
                    "Properties": {
                        "Tags": [
                            {
                                "Value": "test",
                                "Key": "Name"
                            }
                        ],
                        "IpAddress": "1.2.3.4",
                        "BgpAsn": 65000,
                        "Type": "ipsec.1"
                    },
                    "Type": "AWS::EC2::CustomerGateway"
                },
                "VPCIGtest": {
                    "Properties": {
                        "VpcId": {
                            "Ref": "VPCtest"
                        },
                        "InternetGatewayId": {
                            "Ref": "IGtest"
                        }
                    },
                    "Type": "AWS::EC2::VPCGatewayAttachment"
                },
                "VPCVPNGWtest": {
                    "Properties": {
                        "VpcId": {
                            "Ref": "VPCtest"
                        },
                        "VpnGatewayId": {
                            "Ref": "testVPNGW"
                        }
                    },
                    "Type": "AWS::EC2::VPCGatewayAttachment"
                },
                "DefaultRoutetest": {
                    "DependsOn": "VPCIGtest",
                    "Properties": {
                        "GatewayId": {
                            "Ref": "IGtest"
                        },
                        "DestinationCidrBlock": "0.0.0.0/0",
                        "RouteTableId": {
                            "Ref": "RTtest"
                        }
                    },
                    "Type": "AWS::EC2::Route"
                },
                "testVPNGW": {
                    "Properties": {
                        "Tags": [
                            {
                                "Value": "test",
                                "Key": "Name"
                            }
                        ],
                        "Type": "ipsec.1"
                    },
                    "Type": "AWS::EC2::VPNGateway"
                },
                "VPCtest": {
                    "Properties": {
                        "EnableDnsSupport": "true",
                        "Tags": [
                            {
                                "Value": "test",
                                "Key": "Name"
                            }
                        ],
                        "CidrBlock": "10.0.0.0/8",
                        "EnableDnsHostnames": "true"
                    },
                    "Type": "AWS::EC2::VPC"
                },
                "IGtest": {
                    "Properties": {
                        "Tags": [
                            {
                                "Value": "test",
                                "Key": "Name"
                            }
                        ]
                    },
                    "Type": "AWS::EC2::InternetGateway"
                },
                "VGRPtest": {
                    "DependsOn": "VPCVPNGWtest",
                    "Properties": {
                        "RouteTableIds": [
                            {
                                "Ref": "RTtest"
                            }
                        ],
                        "VpnGatewayId": {
                            "Ref": "testVPNGW"
                        }
                    },
                    "Type": "AWS::EC2::VPNGatewayRoutePropagation"
                },
                "testSubnet1": {
                    "Properties": {
                        "AvailabilityZone": "b",
                        "VpcId": {
                            "Ref": "VPCtest"
                        },
                        "Tags": [
                            {
                                "Value": "test-b",
                                "Key": "Name"
                            },
                            {
                                "Value": True,
                                "Key": "Public"
                            }
                        ],
                        "CidrBlock": "10.128.0.0/9"
                    },
                    "Type": "AWS::EC2::Subnet"
                },
                "testSubnet0": {
                    "Properties": {
                        "AvailabilityZone": "a",
                        "VpcId": {
                            "Ref": "VPCtest"
                        },
                        "Tags": [
                            {
                                "Value": "test-a",
                                "Key": "Name"
                            },
                            {
                                "Value": True,
                                "Key": "Public"
                            }
                        ],
                        "CidrBlock": "10.0.0.0/9"
                    },
                    "Type": "AWS::EC2::Subnet"
                },
                "testSRTA0": {
                    "Properties": {
                        "RouteTableId": {
                            "Ref": "RTtest"
                        },
                        "SubnetId": {
                            "Ref": "testSubnet0"
                        }
                    },
                    "Type": "AWS::EC2::SubnetRouteTableAssociation"
                },
                "testSRTA1": {
                    "Properties": {
                        "RouteTableId": {
                            "Ref": "RTtest"
                        },
                        "SubnetId": {
                            "Ref": "testSubnet1"
                        }
                    },
                    "Type": "AWS::EC2::SubnetRouteTableAssociation"
                },
                "testVPNC0": {
                    "DependsOn": "VPCVPNGWtest",
                    "Properties": {
                        "CustomerGatewayId": {
                            "Ref": "testCG0"
                        },
                        "VpnGatewayId": {
                            "Ref": "testVPNGW"
                        },
                        "Type": "ipsec.1"
                    },
                    "Type": "AWS::EC2::VPNConnection"
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
            'load_balancer': [],
            'network': [
                {
                    'name': 'test',
                    'netrange': '10.0.0.0/8',
                    'public': True,
                    'subnets': [
                        {
                            'name': 'test-a',
                            'cidr': '10.0.0.0/9',
                            'zone': 'a',
                            'public': True,
                        },
                        {
                            'name': 'test-b',
                            'cidr': '10.128.0.0/9',
                            'zone': 'b',
                            'public': True,
                        },
                    ],
                    'vpn': [
                        {'asn': 65000, 'ip': '1.2.3.4'},
                    ],
                    'zones': ['a', 'b']
                }
            ]
        }
        tmpl = out.add_resources(res, cfg)
        assert_equals(json.loads(tmpl), ret)

    def test_network_valid_vpn_two_tiers(self):
        out = JSONOutput()
        ret = {
            "Resources": {
                "VGRPtest": {
                    "DependsOn": "VPCVPNGWtest", 
                    "Type": "AWS::EC2::VPNGatewayRoutePropagation", 
                    "Properties": {
                        "RouteTableIds": [
                            {
                                "Ref": "RTtest"
                            }
                        ], 
                        "VpnGatewayId": {
                            "Ref": "testVPNGW"
                        }
                    }
                }, 
                "RTtest": {
                    "Type": "AWS::EC2::RouteTable", 
                    "Properties": {
                        "Tags": [
                            {
                                "Key": "Name", 
                                "Value": "test"
                            }
                        ], 
                        "VpcId": {
                            "Ref": "VPCtest"
                        }
                    }
                }, 
                "DefaultRoutetestpublic": {
                    "DependsOn": "VPCIGtest", 
                    "Type": "AWS::EC2::Route", 
                    "Properties": {
                        "RouteTableId": {
                            "Ref": "RTtestpublic"
                        }, 
                        "GatewayId": {
                            "Ref": "IGtest"
                        }, 
                        "DestinationCidrBlock": "0.0.0.0/0"
                    }
                }, 
                "VPCtest": {
                    "Type": "AWS::EC2::VPC", 
                    "Properties": {
                        "EnableDnsHostnames": "true", 
                        "Tags": [
                            {
                                "Key": "Name", 
                                "Value": "test"
                            }
                        ], 
                        "CidrBlock": "10.0.0.0/8", 
                        "EnableDnsSupport": "true"
                    }
                }, 
                "testSRTA0": {
                    "Type": "AWS::EC2::SubnetRouteTableAssociation", 
                    "Properties": {
                        "RouteTableId": {
                            "Ref": "RTtestpublic"
                        }, 
                        "SubnetId": {
                            "Ref": "testSubnet0"
                        }
                    }
                }, 
                "testVPNC0": {
                    "DependsOn": "VPCVPNGWtest", 
                    "Type": "AWS::EC2::VPNConnection", 
                    "Properties": {
                        "Type": "ipsec.1", 
                        "VpnGatewayId": {
                            "Ref": "testVPNGW"
                        }, 
                        "CustomerGatewayId": {
                            "Ref": "testCG0"
                        }
                    }
                }, 
                "testVPNGW": {
                    "Type": "AWS::EC2::VPNGateway", 
                    "Properties": {
                        "Tags": [
                            {
                                "Key": "Name", 
                                "Value": "test"
                            }
                        ], 
                        "Type": "ipsec.1"
                    }
                }, 
                "VPCVPNGWtest": {
                    "Type": "AWS::EC2::VPCGatewayAttachment", 
                    "Properties": {
                        "VpnGatewayId": {
                            "Ref": "testVPNGW"
                        }, 
                        "VpcId": {
                            "Ref": "VPCtest"
                        }
                    }
                }, 
                "testSRTA1": {
                    "Type": "AWS::EC2::SubnetRouteTableAssociation", 
                    "Properties": {
                        "RouteTableId": {
                            "Ref": "RTtest"
                        }, 
                        "SubnetId": {
                            "Ref": "testSubnet1"
                        }
                    }
                }, 
                "VGRPtestpublic": {
                    "DependsOn": "VPCVPNGWtest", 
                    "Type": "AWS::EC2::VPNGatewayRoutePropagation", 
                    "Properties": {
                        "RouteTableIds": [
                            {
                                "Ref": "RTtestpublic"
                            }
                        ], 
                        "VpnGatewayId": {
                            "Ref": "testVPNGW"
                        }
                    }
                }, 
                "RTtestpublic": {
                    "Type": "AWS::EC2::RouteTable", 
                    "Properties": {
                        "Tags": [
                            {
                                "Key": "Name", 
                                "Value": "testpublic"
                            }
                        ], 
                        "VpcId": {
                            "Ref": "VPCtest"
                        }
                    }
                }, 
                "IGtest": {
                    "Type": "AWS::EC2::InternetGateway", 
                    "Properties": {
                        "Tags": [
                            {
                                "Key": "Name", 
                                "Value": "test"
                            }
                        ]
                    }
                }, 
                "testCG0": {
                    "Type": "AWS::EC2::CustomerGateway", 
                    "Properties": {
                        "Tags": [
                            {
                                "Key": "Name", 
                                "Value": "test"
                            }
                        ], 
                        "IpAddress": "1.2.3.4", 
                        "Type": "ipsec.1", 
                        "BgpAsn": 65000
                    }
                }, 
                "testSubnet0": {
                    "Type": "AWS::EC2::Subnet", 
                    "Properties": {
                        "Tags": [
                            {
                                "Key": "Name", 
                                "Value": "test-a"
                            }, 
                            {
                                "Key": "Public", 
                                "Value": True
                            }
                        ], 
                        "CidrBlock": "10.0.0.0/9", 
                        "AvailabilityZone": "a", 
                        "VpcId": {
                            "Ref": "VPCtest"
                        }
                    }
                }, 
                "testSubnet1": {
                    "Type": "AWS::EC2::Subnet", 
                    "Properties": {
                        "Tags": [
                            {
                                "Key": "Name", 
                                "Value": "test-b"
                            }, 
                            {
                                "Key": "Public", 
                                "Value": False
                            }
                        ], 
                        "CidrBlock": "10.128.0.0/9", 
                        "AvailabilityZone": "b", 
                        "VpcId": {
                            "Ref": "VPCtest"
                        }
                    }
                }, 
                "VPCIGtest": {
                    "Type": "AWS::EC2::VPCGatewayAttachment", 
                    "Properties": {
                        "InternetGatewayId": {
                            "Ref": "IGtest"
                        }, 
                        "VpcId": {
                            "Ref": "VPCtest"
                        }
                    }
                }
            }, 
            "Description": "test test stack", 
            "AWSTemplateFormatVersion": "2010-09-09"
        }

        cfg = {
            'name': 'test',
            'environment': 'test'
        }
        res = {
            'instance': [],
            'secgroup': [],
            'role': [],
            'load_balancer': [],
            'network': [
                {
                    'name': 'test',
                    'netrange': '10.0.0.0/8',
                    'public': True,
                    'subnets': [
                        {
                            'name': 'test-a',
                            'cidr': '10.0.0.0/9',
                            'zone': 'a',
                            'public': True,
                        },
                        {
                            'name': 'test-b',
                            'cidr': '10.128.0.0/9',
                            'zone': 'b',
                            'public': False,
                        },
                    ],
                    'vpn': [
                        {'asn': 65000, 'ip': '1.2.3.4'},
                    ],
                    'zones': ['a', 'b']
                }
            ]
        }
        tmpl = out.add_resources(res, cfg)
        assert_equals(json.loads(tmpl), ret)

    def test_network_valid_peer_two_tiers(self):
        out = JSONOutput()
        ret = {
            "Resources": {
                "DefaultRoutetestpublic": {
                    "Properties": {
                        "GatewayId": {
                            "Ref": "IGtest"
                        }, 
                        "DestinationCidrBlock": "0.0.0.0/0", 
                        "RouteTableId": {
                            "Ref": "RTtestpublic"
                        }
                    }, 
                    "DependsOn": "VPCIGtest", 
                    "Type": "AWS::EC2::Route"
                }, 
                "testSubnet1": {
                    "Properties": {
                        "Tags": [
                            {
                                "Key": "Name", 
                                "Value": "test-b"
                            }, 
                            {
                                "Key": "Public", 
                                "Value": False
                            }
                        ], 
                        "AvailabilityZone": "b", 
                        "CidrBlock": "10.128.0.0/9", 
                        "VpcId": {
                            "Ref": "VPCtest"
                        }
                    }, 
                    "Type": "AWS::EC2::Subnet"
                }, 
                "testSubnet0": {
                    "Properties": {
                        "Tags": [
                            {
                                "Key": "Name", 
                                "Value": "test-a"
                            }, 
                            {
                                "Key": "Public", 
                                "Value": True
                            }
                        ], 
                        "AvailabilityZone": "a", 
                        "CidrBlock": "10.0.0.0/9", 
                        "VpcId": {
                            "Ref": "VPCtest"
                        }
                    }, 
                    "Type": "AWS::EC2::Subnet"
                }, 
                "RTtest2public": {
                    "Properties": {
                        "Tags": [
                            {
                                "Key": "Name", 
                                "Value": "test2public"
                            }
                        ], 
                        "VpcId": {
                            "Ref": "VPCtest2"
                        }
                    }, 
                    "Type": "AWS::EC2::RouteTable"
                }, 
                "test2SRTA1": {
                    "Properties": {
                        "SubnetId": {
                            "Ref": "test2Subnet1"
                        }, 
                        "RouteTableId": {
                            "Ref": "RTtest2"
                        }
                    }, 
                    "Type": "AWS::EC2::SubnetRouteTableAssociation"
                }, 
                "test2SRTA0": {
                    "Properties": {
                        "SubnetId": {
                            "Ref": "test2Subnet0"
                        }, 
                        "RouteTableId": {
                            "Ref": "RTtest2public"
                        }
                    }, 
                    "Type": "AWS::EC2::SubnetRouteTableAssociation"
                }, 
                "RTtestpublic": {
                    "Properties": {
                        "Tags": [
                            {
                                "Key": "Name", 
                                "Value": "testpublic"
                            }
                        ], 
                        "VpcId": {
                            "Ref": "VPCtest"
                        }
                    }, 
                    "Type": "AWS::EC2::RouteTable"
                }, 
                "test2Subnet1": {
                    "Properties": {
                        "Tags": [
                            {
                                "Key": "Name", 
                                "Value": "test-b"
                            }, 
                            {
                                "Key": "Public", 
                                "Value": False
                            }
                        ], 
                        "AvailabilityZone": "b", 
                        "CidrBlock": "11.128.0.0/9", 
                        "VpcId": {
                            "Ref": "VPCtest2"
                        }
                    }, 
                    "Type": "AWS::EC2::Subnet"
                }, 
                "IGtest2": {
                    "Properties": {
                        "Tags": [
                            {
                                "Key": "Name", 
                                "Value": "test2"
                            }
                        ]
                    }, 
                    "Type": "AWS::EC2::InternetGateway"
                }, 
                "Routetesttest2": {
                    "Properties": {
                        "VpcPeeringConnectionId": {
                            "Ref": "testtest2Peering"
                        }, 
                        "DestinationCidrBlock": "10.0.0.0/8", 
                        "RouteTableId": {
                            "Ref": "RTtest2"
                        }
                    }, 
                    "Type": "AWS::EC2::Route"
                }, 
                "Routetest2test": {
                    "Properties": {
                        "VpcPeeringConnectionId": {
                            "Ref": "testtest2Peering"
                        }, 
                        "DestinationCidrBlock": "11.0.0.0/8", 
                        "RouteTableId": {
                            "Ref": "RTtest"
                        }
                    }, 
                    "Type": "AWS::EC2::Route"
                }, 
                "RTtest2": {
                    "Properties": {
                        "Tags": [
                            {
                                "Key": "Name", 
                                "Value": "test2"
                            }
                        ], 
                        "VpcId": {
                            "Ref": "VPCtest2"
                        }
                    }, 
                    "Type": "AWS::EC2::RouteTable"
                }, 
                "test2Subnet0": {
                    "Properties": {
                        "Tags": [
                            {
                                "Key": "Name", 
                                "Value": "test-a"
                            }, 
                            {
                                "Key": "Public", 
                                "Value": True
                            }
                        ], 
                        "AvailabilityZone": "a", 
                        "CidrBlock": "11.0.0.0/9", 
                        "VpcId": {
                            "Ref": "VPCtest2"
                        }
                    }, 
                    "Type": "AWS::EC2::Subnet"
                }, 
                "DefaultRoutetest2public": {
                    "Properties": {
                        "GatewayId": {
                            "Ref": "IGtest2"
                        }, 
                        "DestinationCidrBlock": "0.0.0.0/0", 
                        "RouteTableId": {
                            "Ref": "RTtest2public"
                        }
                    }, 
                    "DependsOn": "VPCIGtest2", 
                    "Type": "AWS::EC2::Route"
                }, 
                "VPCtest2": {
                    "Properties": {
                        "EnableDnsSupport": "true", 
                        "Tags": [
                            {
                                "Key": "Name", 
                                "Value": "test2"
                            }
                        ], 
                        "CidrBlock": "11.0.0.0/8", 
                        "EnableDnsHostnames": "true"
                    }, 
                    "Type": "AWS::EC2::VPC"
                }, 
                "Routetesttest2public": {
                    "Properties": {
                        "VpcPeeringConnectionId": {
                            "Ref": "testtest2Peering"
                        }, 
                        "DestinationCidrBlock": "11.0.0.0/8", 
                        "RouteTableId": {
                            "Ref": "RTtestpublic"
                        }
                    }, 
                    "Type": "AWS::EC2::Route"
                }, 
                "testtest2Peering": {
                    "Properties": {
                        "VpcId": {
                            "Ref": "VPCtest2"
                        }, 
                        "PeerVpcId": {
                            "Ref": "VPCtest"
                        }
                    }, 
                    "Type": "AWS::EC2::VPCPeeringConnection"
                }, 
                "RTtest": {
                    "Properties": {
                        "Tags": [
                            {
                                "Key": "Name", 
                                "Value": "test"
                            }
                        ], 
                        "VpcId": {
                            "Ref": "VPCtest"
                        }
                    }, 
                    "Type": "AWS::EC2::RouteTable"
                }, 
                "IGtest": {
                    "Properties": {
                        "Tags": [
                            {
                                "Key": "Name", 
                                "Value": "test"
                            }
                        ]
                    }, 
                    "Type": "AWS::EC2::InternetGateway"
                }, 
                "VPCIGtest2": {
                    "Properties": {
                        "InternetGatewayId": {
                            "Ref": "IGtest2"
                        }, 
                        "VpcId": {
                            "Ref": "VPCtest2"
                        }
                    }, 
                    "Type": "AWS::EC2::VPCGatewayAttachment"
                }, 
                "VPCIGtest": {
                    "Properties": {
                        "InternetGatewayId": {
                            "Ref": "IGtest"
                        }, 
                        "VpcId": {
                            "Ref": "VPCtest"
                        }
                    }, 
                    "Type": "AWS::EC2::VPCGatewayAttachment"
                }, 
                "VPCtest": {
                    "Properties": {
                        "EnableDnsSupport": "true", 
                        "Tags": [
                            {
                                "Key": "Name", 
                                "Value": "test"
                            }
                        ], 
                        "CidrBlock": "10.0.0.0/8", 
                        "EnableDnsHostnames": "true"
                    }, 
                    "Type": "AWS::EC2::VPC"
                }, 
                "testSRTA0": {
                    "Properties": {
                        "SubnetId": {
                            "Ref": "testSubnet0"
                        }, 
                        "RouteTableId": {
                            "Ref": "RTtestpublic"
                        }
                    }, 
                    "Type": "AWS::EC2::SubnetRouteTableAssociation"
                }, 
                "testSRTA1": {
                    "Properties": {
                        "SubnetId": {
                            "Ref": "testSubnet1"
                        }, 
                        "RouteTableId": {
                            "Ref": "RTtest"
                        }
                    }, 
                    "Type": "AWS::EC2::SubnetRouteTableAssociation"
                }
            }, 
            "AWSTemplateFormatVersion": "2010-09-09", 
            "Description": "test test stack"
        }

        cfg = {
            'name': 'test',
            'environment': 'test'
        }
        res = {
            'instance': [],
            'secgroup': [],
            'role': [],
            'load_balancer': [],
            'network': [
                {
                    'name': 'test',
                    'netrange': '10.0.0.0/8',
                    'public': True,
                    'subnets': [
                        {
                            'name': 'test-a',
                            'cidr': '10.0.0.0/9',
                            'zone': 'a',
                            'public': True,
                        },
                        {
                            'name': 'test-b',
                            'cidr': '10.128.0.0/9',
                            'zone': 'b',
                            'public': False,
                        },
                    ],
                    'zones': ['a', 'b']
                },
                {
                    'name': 'test2',
                    'netrange': '11.0.0.0/8',
                    'public': True,
                    'subnets': [
                        {
                            'name': 'test-a',
                            'cidr': '11.0.0.0/9',
                            'zone': 'a',
                            'public': True,
                        },
                        {
                            'name': 'test-b',
                            'cidr': '11.128.0.0/9',
                            'zone': 'b',
                            'public': False,
                        },
                    ],
                    'peers': [
                        {'peerid': '=test'},
                    ],
                    'zones': ['a', 'b']
                },
            ]
        }
        tmpl = out.add_resources(res, cfg)
        assert_equals(json.loads(tmpl), ret)

    def test_network_valid_peer(self):
        out = JSONOutput()
        ret = {
            "Description": "test test stack",
            "AWSTemplateFormatVersion": "2010-09-09",
            "Resources": {
                "RTtest2": {
                    "Type": "AWS::EC2::RouteTable",
                    "Properties": {
                        "VpcId": {
                            "Ref": "VPCtest2"
                        },
                        "Tags": [
                            {
                                "Value": "test2",
                                "Key": "Name"
                            }
                        ]
                    }
                },
                "VPCIGtest": {
                    "Type": "AWS::EC2::VPCGatewayAttachment",
                    "Properties": {
                        "VpcId": {
                            "Ref": "VPCtest"
                        },
                        "InternetGatewayId": {
                            "Ref": "IGtest"
                        }
                    }
                },
                "testSubnet0": {
                    "Type": "AWS::EC2::Subnet",
                    "Properties": {
                        "AvailabilityZone": "a",
                        "VpcId": {
                            "Ref": "VPCtest"
                        },
                        "CidrBlock": "10.0.0.0/9",
                        "Tags": [
                            {
                                "Value": "test-a",
                                "Key": "Name"
                            },
                            {
                                "Value": True,
                                "Key": "Public"
                            }
                        ]
                    }
                },
                "Routetest2test": {
                    "Type": "AWS::EC2::Route",
                    "Properties": {
                        "RouteTableId": {
                            "Ref": "RTtest"
                        },
                        "DestinationCidrBlock": "11.0.0.0/8",
                        "VpcPeeringConnectionId": {
                            "Ref": "testtest2Peering"
                        }
                    }
                },
                "test2Subnet1": {
                    "Type": "AWS::EC2::Subnet",
                    "Properties": {
                        "AvailabilityZone": "b",
                        "VpcId": {
                            "Ref": "VPCtest2"
                        },
                        "CidrBlock": "11.128.0.0/9",
                        "Tags": [
                            {
                                "Value": "test-b",
                                "Key": "Name"
                            },
                            {
                                "Value": True,
                                "Key": "Public"
                            }
                        ]
                    }
                },
                "test2Subnet0": {
                    "Type": "AWS::EC2::Subnet",
                    "Properties": {
                        "AvailabilityZone": "a",
                        "VpcId": {
                            "Ref": "VPCtest2"
                        },
                        "CidrBlock": "11.0.0.0/9",
                        "Tags": [
                            {
                                "Value": "test-a",
                                "Key": "Name"
                            },
                            {
                                "Value": True,
                                "Key": "Public"
                            }
                        ]
                    }
                },
                "testSRTA1": {
                    "Type": "AWS::EC2::SubnetRouteTableAssociation",
                    "Properties": {
                        "RouteTableId": {
                            "Ref": "RTtest"
                        },
                        "SubnetId": {
                            "Ref": "testSubnet1"
                        }
                    }
                },
                "testSRTA0": {
                    "Type": "AWS::EC2::SubnetRouteTableAssociation",
                    "Properties": {
                        "RouteTableId": {
                            "Ref": "RTtest"
                        },
                        "SubnetId": {
                            "Ref": "testSubnet0"
                        }
                    }
                },
                "IGtest": {
                    "Type": "AWS::EC2::InternetGateway",
                    "Properties": {
                        "Tags": [
                            {
                                "Value": "test",
                                "Key": "Name"
                            }
                        ]
                    }
                },
                "test2SRTA1": {
                    "Type": "AWS::EC2::SubnetRouteTableAssociation",
                    "Properties": {
                        "RouteTableId": {
                            "Ref": "RTtest2"
                        },
                        "SubnetId": {
                            "Ref": "test2Subnet1"
                        }
                    }
                },
                "VPCtest": {
                    "Type": "AWS::EC2::VPC",
                    "Properties": {
                        "CidrBlock": "10.0.0.0/8",
                        "Tags": [
                            {
                                "Value": "test",
                                "Key": "Name"
                            }
                        ],
                        "EnableDnsHostnames": "true",
                        "EnableDnsSupport": "true"
                    }
                },
                "Routetesttest2": {
                    "Type": "AWS::EC2::Route",
                    "Properties": {
                        "RouteTableId": {
                            "Ref": "RTtest2"
                        },
                        "DestinationCidrBlock": "10.0.0.0/8",
                        "VpcPeeringConnectionId": {
                            "Ref": "testtest2Peering"
                        }
                    }
                },
                "DefaultRoutetest": {
                    "Type": "AWS::EC2::Route",
                    "DependsOn": "VPCIGtest",
                    "Properties": {
                        "RouteTableId": {
                            "Ref": "RTtest"
                        },
                        "DestinationCidrBlock": "0.0.0.0/0",
                        "GatewayId": {
                            "Ref": "IGtest"
                        }
                    }
                },
                "DefaultRoutetest2": {
                    "Type": "AWS::EC2::Route",
                    "DependsOn": "VPCIGtest2",
                    "Properties": {
                        "RouteTableId": {
                            "Ref": "RTtest2"
                        },
                        "DestinationCidrBlock": "0.0.0.0/0",
                        "GatewayId": {
                            "Ref": "IGtest2"
                        }
                    }
                },
                "testtest2Peering": {
                    "Type": "AWS::EC2::VPCPeeringConnection",
                    "Properties": {
                        "PeerVpcId": {
                            "Ref": "VPCtest"
                        },
                        "VpcId": {
                            "Ref": "VPCtest2"
                        }
                    }
                },
                "IGtest2": {
                    "Type": "AWS::EC2::InternetGateway",
                    "Properties": {
                        "Tags": [
                            {
                                "Value": "test2",
                                "Key": "Name"
                            }
                        ]
                    }
                },
                "RTtest": {
                    "Type": "AWS::EC2::RouteTable",
                    "Properties": {
                        "VpcId": {
                            "Ref": "VPCtest"
                        },
                        "Tags": [
                            {
                                "Value": "test",
                                "Key": "Name"
                            }
                        ]
                    }
                },
                "VPCIGtest2": {
                    "Type": "AWS::EC2::VPCGatewayAttachment",
                    "Properties": {
                        "VpcId": {
                            "Ref": "VPCtest2"
                        },
                        "InternetGatewayId": {
                            "Ref": "IGtest2"
                        }
                    }
                },
                "testSubnet1": {
                    "Type": "AWS::EC2::Subnet",
                    "Properties": {
                        "AvailabilityZone": "b",
                        "VpcId": {
                            "Ref": "VPCtest"
                        },
                        "CidrBlock": "10.128.0.0/9",
                        "Tags": [
                            {
                                "Value": "test-b",
                                "Key": "Name"
                            },
                            {
                                "Value": True,
                                "Key": "Public"
                            }
                        ]
                    }
                },
                "test2SRTA0": {
                    "Type": "AWS::EC2::SubnetRouteTableAssociation",
                    "Properties": {
                        "RouteTableId": {
                            "Ref": "RTtest2"
                        },
                        "SubnetId": {
                            "Ref": "test2Subnet0"
                        }
                    }
                },
                "VPCtest2": {
                    "Type": "AWS::EC2::VPC",
                    "Properties": {
                        "CidrBlock": "11.0.0.0/8",
                        "Tags": [
                            {
                                "Value": "test2",
                                "Key": "Name"
                            }
                        ],
                        "EnableDnsHostnames": "true",
                        "EnableDnsSupport": "true"
                    }
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
            'load_balancer': [],
            'network': [
                {
                    'name': 'test',
                    'netrange': '10.0.0.0/8',
                    'public': True,
                    'subnets': [
                        {
                            'name': 'test-a',
                            'cidr': '10.0.0.0/9',
                            'zone': 'a',
                            'public': True,
                        },
                        {
                            'name': 'test-b',
                            'cidr': '10.128.0.0/9',
                            'zone': 'b',
                            'public': True,
                        },
                    ],
                    'zones': ['a', 'b']
                },
                {
                    'name': 'test2',
                    'netrange': '11.0.0.0/8',
                    'public': True,
                    'subnets': [
                        {
                            'name': 'test-a',
                            'cidr': '11.0.0.0/9',
                            'zone': 'a',
                            'public': True,
                        },
                        {
                            'name': 'test-b',
                            'cidr': '11.128.0.0/9',
                            'zone': 'b',
                            'public': True,
                        },
                    ],
                    'peers': [
                        {'peerid': '=test'},
                    ],
                    'zones': ['a', 'b']
                },
            ]
        }
        tmpl = out.add_resources(res, cfg)
        assert_equals(json.loads(tmpl), ret)

    def test_network_valid_routes(self):
        out = JSONOutput()
        ret = {
            "AWSTemplateFormatVersion": "2010-09-09", 
            "Resources": {
                "VPCtest": {
                    "Properties": {
                        "Tags": [
                            {
                                "Key": "Name", 
                                "Value": "test"
                            }
                        ], 
                        "EnableDnsSupport": "true", 
                        "EnableDnsHostnames": "true", 
                        "CidrBlock": "10.0.0.0/8"
                    }, 
                    "Type": "AWS::EC2::VPC"
                }, 
                "testSubnet1": {
                    "Properties": {
                        "Tags": [
                            {
                                "Key": "Name", 
                                "Value": "test-b"
                            }, 
                            {
                                "Key": "Public", 
                                "Value": True
                            }
                        ], 
                        "VpcId": {
                            "Ref": "VPCtest"
                        }, 
                        "CidrBlock": "10.128.0.0/9", 
                        "AvailabilityZone": "b"
                    }, 
                    "Type": "AWS::EC2::Subnet"
                }, 
                "VPCIGtest": {
                    "Properties": {
                        "InternetGatewayId": {
                            "Ref": "IGtest"
                        }, 
                        "VpcId": {
                            "Ref": "VPCtest"
                        }
                    }, 
                    "Type": "AWS::EC2::VPCGatewayAttachment"
                }, 
                "Route1122024test": {
                    "Properties": {
                        "DestinationCidrBlock": "11.2.2.0/24", 
                        "GatewayId": "10.0.0.2", 
                        "RouteTableId": {
                            "Ref": "RTtest"
                        }
                    }, 
                    "Type": "AWS::EC2::Route"
                }, 
                "DefaultRoutetest": {
                    "Properties": {
                        "DestinationCidrBlock": "0.0.0.0/0", 
                        "GatewayId": {
                            "Ref": "IGtest"
                        }, 
                        "RouteTableId": {
                            "Ref": "RTtest"
                        }
                    }, 
                    "Type": "AWS::EC2::Route", 
                    "DependsOn": "VPCIGtest"
                }, 
                "testSubnet0": {
                    "Properties": {
                        "Tags": [
                            {
                                "Key": "Name", 
                                "Value": "test-a"
                            }, 
                            {
                                "Key": "Public", 
                                "Value": True
                            }
                        ], 
                        "VpcId": {
                            "Ref": "VPCtest"
                        }, 
                        "CidrBlock": "10.0.0.0/9", 
                        "AvailabilityZone": "a"
                    }, 
                    "Type": "AWS::EC2::Subnet"
                }, 
                "RTtest": {
                    "Properties": {
                        "Tags": [
                            {
                                "Key": "Name", 
                                "Value": "test"
                            }
                        ], 
                        "VpcId": {
                            "Ref": "VPCtest"
                        }
                    }, 
                    "Type": "AWS::EC2::RouteTable"
                }, 
                "testSRTA1": {
                    "Properties": {
                        "SubnetId": {
                            "Ref": "testSubnet1"
                        }, 
                        "RouteTableId": {
                            "Ref": "RTtest"
                        }
                    }, 
                    "Type": "AWS::EC2::SubnetRouteTableAssociation"
                }, 
                "testSRTA0": {
                    "Properties": {
                        "SubnetId": {
                            "Ref": "testSubnet0"
                        }, 
                        "RouteTableId": {
                            "Ref": "RTtest"
                        }
                    }, 
                    "Type": "AWS::EC2::SubnetRouteTableAssociation"
                }, 
                "IGtest": {
                    "Properties": {
                        "Tags": [
                            {
                                "Key": "Name", 
                                "Value": "test"
                            }
                        ]
                    }, 
                    "Type": "AWS::EC2::InternetGateway"
                }
            }, 
            "Description": "test test stack"
        }

        cfg = {
            'name': 'test',
            'environment': 'test'
        }
        res = {
            'instance': [],
            'secgroup': [],
            'role': [],
            'load_balancer': [],
            'network': [
                {
                    'name': 'test',
                    'netrange': '10.0.0.0/8',
                    'public': True,
                    'subnets': [
                        {
                            'name': 'test-a',
                            'cidr': '10.0.0.0/9',
                            'zone': 'a',
                            'public': True,
                        },
                        {
                            'name': 'test-b',
                            'cidr': '10.128.0.0/9',
                            'zone': 'b',
                            'public': True,
                        },
                    ],
                    'routes': [
                        {
                            'cidr': '11.2.2.0/24',
                            'gateway': '10.0.0.2',
                        }
                    ],
                    'zones': ['a', 'b']
                },
            ]
        }
        tmpl = out.add_resources(res, cfg)
        assert_equals(json.loads(tmpl), ret)

    def test_network_valid_routes_two_tiers(self):
        out = JSONOutput()
        ret = {
            "AWSTemplateFormatVersion": "2010-09-09", 
            "Resources": {
                "DefaultRoutetestpublic": {
                    "Properties": {
                        "DestinationCidrBlock": "0.0.0.0/0", 
                        "GatewayId": {
                            "Ref": "IGtest"
                        }, 
                        "RouteTableId": {
                            "Ref": "RTtestpublic"
                        }
                    }, 
                    "Type": "AWS::EC2::Route", 
                    "DependsOn": "VPCIGtest"
                }, 
                "VPCtest": {
                    "Properties": {
                        "Tags": [
                            {
                                "Key": "Name", 
                                "Value": "test"
                            }
                        ], 
                        "EnableDnsSupport": "true", 
                        "EnableDnsHostnames": "true", 
                        "CidrBlock": "10.0.0.0/8"
                    }, 
                    "Type": "AWS::EC2::VPC"
                }, 
                "testSubnet1": {
                    "Properties": {
                        "Tags": [
                            {
                                "Key": "Name", 
                                "Value": "test-b"
                            }, 
                            {
                                "Key": "Public", 
                                "Value": False
                            }
                        ], 
                        "VpcId": {
                            "Ref": "VPCtest"
                        }, 
                        "CidrBlock": "10.128.0.0/9", 
                        "AvailabilityZone": "b"
                    }, 
                    "Type": "AWS::EC2::Subnet"
                }, 
                "VPCIGtest": {
                    "Properties": {
                        "InternetGatewayId": {
                            "Ref": "IGtest"
                        }, 
                        "VpcId": {
                            "Ref": "VPCtest"
                        }
                    }, 
                    "Type": "AWS::EC2::VPCGatewayAttachment"
                }, 
                "Route1122024test": {
                    "Properties": {
                        "DestinationCidrBlock": "11.2.2.0/24", 
                        "GatewayId": "10.0.0.2", 
                        "RouteTableId": {
                            "Ref": "RTtest"
                        }
                    }, 
                    "Type": "AWS::EC2::Route"
                }, 
                "testSubnet0": {
                    "Properties": {
                        "Tags": [
                            {
                                "Key": "Name", 
                                "Value": "test-a"
                            }, 
                            {
                                "Key": "Public", 
                                "Value": True
                            }
                        ], 
                        "VpcId": {
                            "Ref": "VPCtest"
                        }, 
                        "CidrBlock": "10.0.0.0/9", 
                        "AvailabilityZone": "a"
                    }, 
                    "Type": "AWS::EC2::Subnet"
                }, 
                "Route1122024testpublic": {
                    "Properties": {
                        "DestinationCidrBlock": "11.2.2.0/24", 
                        "GatewayId": "10.0.0.2", 
                        "RouteTableId": {
                            "Ref": "RTtestpublic"
                        }
                    }, 
                    "Type": "AWS::EC2::Route"
                }, 
                "RTtestpublic": {
                    "Properties": {
                        "Tags": [
                            {
                                "Key": "Name", 
                                "Value": "testpublic"
                            }
                        ], 
                        "VpcId": {
                            "Ref": "VPCtest"
                        }
                    }, 
                    "Type": "AWS::EC2::RouteTable"
                }, 
                "testSRTA0": {
                    "Properties": {
                        "SubnetId": {
                            "Ref": "testSubnet0"
                        }, 
                        "RouteTableId": {
                            "Ref": "RTtestpublic"
                        }
                    }, 
                    "Type": "AWS::EC2::SubnetRouteTableAssociation"
                }, 
                "testSRTA1": {
                    "Properties": {
                        "SubnetId": {
                            "Ref": "testSubnet1"
                        }, 
                        "RouteTableId": {
                            "Ref": "RTtest"
                        }
                    }, 
                    "Type": "AWS::EC2::SubnetRouteTableAssociation"
                }, 
                "RTtest": {
                    "Properties": {
                        "Tags": [
                            {
                                "Key": "Name", 
                                "Value": "test"
                            }
                        ], 
                        "VpcId": {
                            "Ref": "VPCtest"
                        }
                    }, 
                    "Type": "AWS::EC2::RouteTable"
                }, 
                "IGtest": {
                    "Properties": {
                        "Tags": [
                            {
                                "Key": "Name", 
                                "Value": "test"
                            }
                        ]
                    }, 
                    "Type": "AWS::EC2::InternetGateway"
                }
            }, 
            "Description": "test test stack"
        }

        cfg = {
            'name': 'test',
            'environment': 'test'
        }
        res = {
            'instance': [],
            'secgroup': [],
            'role': [],
            'load_balancer': [],
            'network': [
                {
                    'name': 'test',
                    'netrange': '10.0.0.0/8',
                    'public': True,
                    'subnets': [
                        {
                            'name': 'test-a',
                            'cidr': '10.0.0.0/9',
                            'zone': 'a',
                            'public': True,
                        },
                        {
                            'name': 'test-b',
                            'cidr': '10.128.0.0/9',
                            'zone': 'b',
                            'public': False,
                        },
                    ],
                    'routes': [
                        {
                            'cidr': '11.2.2.0/24',
                            'gateway': '10.0.0.2',
                        }
                    ],
                    'zones': ['a', 'b']
                },
            ]
        }
        tmpl = out.add_resources(res, cfg)
        assert_equals(json.loads(tmpl), ret)

    def test_network_valid_routes_peers(self):
        out = JSONOutput()
        ret = {
            "AWSTemplateFormatVersion": "2010-09-09", 
            "Description": "test test stack", 
            "Resources": {
                "DefaultRoutetest": {
                    "DependsOn": "VPCIGtest", 
                    "Properties": {
                        "DestinationCidrBlock": "0.0.0.0/0", 
                        "GatewayId": {
                            "Ref": "IGtest"
                        }, 
                        "RouteTableId": {
                            "Ref": "RTtest"
                        }
                    }, 
                    "Type": "AWS::EC2::Route"
                }, 
                "DefaultRoutetest2public": {
                    "DependsOn": "VPCIGtest2", 
                    "Properties": {
                        "DestinationCidrBlock": "0.0.0.0/0", 
                        "GatewayId": {
                            "Ref": "IGtest2"
                        }, 
                        "RouteTableId": {
                            "Ref": "RTtest2public"
                        }
                    }, 
                    "Type": "AWS::EC2::Route"
                }, 
                "IGtest": {
                    "Properties": {
                        "Tags": [
                            {
                                "Key": "Name", 
                                "Value": "test"
                            }
                        ]
                    }, 
                    "Type": "AWS::EC2::InternetGateway"
                }, 
                "IGtest2": {
                    "Properties": {
                        "Tags": [
                            {
                                "Key": "Name", 
                                "Value": "test2"
                            }
                        ]
                    }, 
                    "Type": "AWS::EC2::InternetGateway"
                }, 
                "RTtest": {
                    "Properties": {
                        "Tags": [
                            {
                                "Key": "Name", 
                                "Value": "test"
                            }
                        ], 
                        "VpcId": {
                            "Ref": "VPCtest"
                        }
                    }, 
                    "Type": "AWS::EC2::RouteTable"
                }, 
                "RTtest2": {
                    "Properties": {
                        "Tags": [
                            {
                                "Key": "Name", 
                                "Value": "test2"
                            }
                        ], 
                        "VpcId": {
                            "Ref": "VPCtest2"
                        }
                    }, 
                    "Type": "AWS::EC2::RouteTable"
                }, 
                "RTtest2public": {
                    "Properties": {
                        "Tags": [
                            {
                                "Key": "Name", 
                                "Value": "test2public"
                            }
                        ], 
                        "VpcId": {
                            "Ref": "VPCtest2"
                        }
                    }, 
                    "Type": "AWS::EC2::RouteTable"
                }, 
                "Route1122024test2": {
                    "Properties": {
                        "DestinationCidrBlock": "11.2.2.0/24", 
                        "RouteTableId": {
                            "Ref": "RTtest2"
                        }, 
                        "VpcPeeringConnectionId": {
                            "Ref": "test2testPeering"
                        }
                    }, 
                    "Type": "AWS::EC2::Route"
                }, 
                "Route1122024test2public": {
                    "Properties": {
                        "DestinationCidrBlock": "11.2.2.0/24", 
                        "RouteTableId": {
                            "Ref": "RTtest2public"
                        }, 
                        "VpcPeeringConnectionId": {
                            "Ref": "test2testPeering"
                        }
                    }, 
                    "Type": "AWS::EC2::Route"
                }, 
                "Routetest2test": {
                    "Properties": {
                        "DestinationCidrBlock": "11.0.0.0/8", 
                        "RouteTableId": {
                            "Ref": "RTtest"
                        }, 
                        "VpcPeeringConnectionId": {
                            "Ref": "testtest2Peering"
                        }
                    }, 
                    "Type": "AWS::EC2::Route"
                }, 
                "Routetesttest2": {
                    "Properties": {
                        "DestinationCidrBlock": "10.0.0.0/8", 
                        "RouteTableId": {
                            "Ref": "RTtest2"
                        }, 
                        "VpcPeeringConnectionId": {
                            "Ref": "testtest2Peering"
                        }
                    }, 
                    "Type": "AWS::EC2::Route"
                }, 
                "VPCIGtest": {
                    "Properties": {
                        "InternetGatewayId": {
                            "Ref": "IGtest"
                        }, 
                        "VpcId": {
                            "Ref": "VPCtest"
                        }
                    }, 
                    "Type": "AWS::EC2::VPCGatewayAttachment"
                }, 
                "VPCIGtest2": {
                    "Properties": {
                        "InternetGatewayId": {
                            "Ref": "IGtest2"
                        }, 
                        "VpcId": {
                            "Ref": "VPCtest2"
                        }
                    }, 
                    "Type": "AWS::EC2::VPCGatewayAttachment"
                }, 
                "VPCtest": {
                    "Properties": {
                        "CidrBlock": "10.0.0.0/8", 
                        "EnableDnsHostnames": "true", 
                        "EnableDnsSupport": "true", 
                        "Tags": [
                            {
                                "Key": "Name", 
                                "Value": "test"
                            }
                        ]
                    }, 
                    "Type": "AWS::EC2::VPC"
                }, 
                "VPCtest2": {
                    "Properties": {
                        "CidrBlock": "11.0.0.0/8", 
                        "EnableDnsHostnames": "true", 
                        "EnableDnsSupport": "true", 
                        "Tags": [
                            {
                                "Key": "Name", 
                                "Value": "test2"
                            }
                        ]
                    }, 
                    "Type": "AWS::EC2::VPC"
                }, 
                "test2SRTA0": {
                    "Properties": {
                        "RouteTableId": {
                            "Ref": "RTtest2public"
                        }, 
                        "SubnetId": {
                            "Ref": "test2Subnet0"
                        }
                    }, 
                    "Type": "AWS::EC2::SubnetRouteTableAssociation"
                }, 
                "test2SRTA1": {
                    "Properties": {
                        "RouteTableId": {
                            "Ref": "RTtest2"
                        }, 
                        "SubnetId": {
                            "Ref": "test2Subnet1"
                        }
                    }, 
                    "Type": "AWS::EC2::SubnetRouteTableAssociation"
                }, 
                "test2Subnet0": {
                    "Properties": {
                        "AvailabilityZone": "a", 
                        "CidrBlock": "11.0.0.0/9", 
                        "Tags": [
                            {
                                "Key": "Name", 
                                "Value": "test-a"
                            }, 
                            {
                                "Key": "Public", 
                                "Value": True
                            }
                        ], 
                        "VpcId": {
                            "Ref": "VPCtest2"
                        }
                    }, 
                    "Type": "AWS::EC2::Subnet"
                }, 
                "test2Subnet1": {
                    "Properties": {
                        "AvailabilityZone": "b", 
                        "CidrBlock": "11.128.0.0/9", 
                        "Tags": [
                            {
                                "Key": "Name", 
                                "Value": "test-b"
                            }, 
                            {
                                "Key": "Public", 
                                "Value": False
                            }
                        ], 
                        "VpcId": {
                            "Ref": "VPCtest2"
                        }
                    }, 
                    "Type": "AWS::EC2::Subnet"
                }, 
                "testSRTA0": {
                    "Properties": {
                        "RouteTableId": {
                            "Ref": "RTtest"
                        }, 
                        "SubnetId": {
                            "Ref": "testSubnet0"
                        }
                    }, 
                    "Type": "AWS::EC2::SubnetRouteTableAssociation"
                }, 
                "testSRTA1": {
                    "Properties": {
                        "RouteTableId": {
                            "Ref": "RTtest"
                        }, 
                        "SubnetId": {
                            "Ref": "testSubnet1"
                        }
                    }, 
                    "Type": "AWS::EC2::SubnetRouteTableAssociation"
                }, 
                "testSubnet0": {
                    "Properties": {
                        "AvailabilityZone": "a", 
                        "CidrBlock": "10.0.0.0/9", 
                        "Tags": [
                            {
                                "Key": "Name", 
                                "Value": "test-a"
                            }, 
                            {
                                "Key": "Public", 
                                "Value": True
                            }
                        ], 
                        "VpcId": {
                            "Ref": "VPCtest"
                        }
                    }, 
                    "Type": "AWS::EC2::Subnet"
                }, 
                "testSubnet1": {
                    "Properties": {
                        "AvailabilityZone": "b", 
                        "CidrBlock": "10.128.0.0/9", 
                        "Tags": [
                            {
                                "Key": "Name", 
                                "Value": "test-b"
                            }, 
                            {
                                "Key": "Public", 
                                "Value": True
                            }
                        ], 
                        "VpcId": {
                            "Ref": "VPCtest"
                        }
                    }, 
                    "Type": "AWS::EC2::Subnet"
                }, 
                "testtest2Peering": {
                    "Properties": {
                        "PeerVpcId": {
                            "Ref": "VPCtest"
                        }, 
                        "VpcId": {
                            "Ref": "VPCtest2"
                        }
                    }, 
                    "Type": "AWS::EC2::VPCPeeringConnection"
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
            'load_balancer': [],
            'network': [
                {
                    'name': 'test',
                    'netrange': '10.0.0.0/8',
                    'public': True,
                    'subnets': [
                        {
                            'name': 'test-a',
                            'cidr': '10.0.0.0/9',
                            'zone': 'a',
                            'public': True,
                        },
                        {
                            'name': 'test-b',
                            'cidr': '10.128.0.0/9',
                            'zone': 'b',
                            'public': True,
                        },
                    ],
                    'zones': ['a', 'b']
                },
                {
                    'name': 'test2',
                    'netrange': '11.0.0.0/8',
                    'public': True,
                    'subnets': [
                        {
                            'name': 'test-a',
                            'cidr': '11.0.0.0/9',
                            'zone': 'a',
                            'public': True,
                        },
                        {
                            'name': 'test-b',
                            'cidr': '11.128.0.0/9',
                            'zone': 'b',
                            'public': False,
                        },
                    ],
                    'routes': [
                        {
                            'cidr': '11.2.2.0/24',
                            'gateway': '=test',
                        }
                    ],
                    'peers': [
                        {'peerid': '=test'},
                    ],
                    'zones': ['a', 'b']
                },
            ]
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
                        "ConnectionDrainingPolicy": {
                            "Enabled": True,
                            "Timeout": 10,
                        },
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
                        "Tags": [{"Key": "Name", "Value": "test::test"}],
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

    def test_lb_valid_dns(self):
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
                "DNSELBtest": {
                    "Type": "AWS::Route53::RecordSet",
                    "Properties": {
                        "Comment": "ELB for test in test",
                        "HostedZoneName": "test.example.com",
                        "AliasTarget": {
                            "HostedZoneId": {
                                "Fn::GetAtt": [
                                    "ELBtest",
                                    "CanonicalHostedZoneNameID"
                                ]
                            },
                            "DNSName": {
                                "Fn::GetAtt": [
                                    "ELBtest",
                                    "CanonicalHostedZoneName"
                                ]
                            }
                        },
                        "Name": "test.test.example.com",
                        "Type": "A"
                    }
                },
                "ELBtest": {
                    "Properties": {
                        "AvailabilityZones": {
                            "Fn::GetAZs": ""
                        },
                        "CrossZone": "true",
                        "ConnectionDrainingPolicy": {
                            "Enabled": True,
                            "Timeout": 10,
                        },
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
                        "Tags": [{"Key": "Name", "Value": "test::test"}],
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
                'dns': 'example.com',
                'name': 'test',
                'policy': [],
            }]
        }
        tmpl = out.add_resources(res, cfg)
        assert_equals(json.loads(tmpl), ret)

    def test_lb_valid_dns_internal(self):
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
                "DNSELBtest": {
                    "Type": "AWS::Route53::RecordSet",
                    "Properties": {
                        "Comment": "ELB for test in test",
                        "HostedZoneName": "test.example.com",
                        "AliasTarget": {
                            "HostedZoneId": {
                                "Fn::GetAtt": [
                                    "ELBtest",
                                    "CanonicalHostedZoneNameID"
                                ]
                            },
                            "DNSName": {
                                "Fn::GetAtt": [
                                    "ELBtest",
                                    "DNSName"
                                ]
                            }
                        },
                        "Name": "test.test.example.com",
                        "Type": "A"
                    }
                },
                "ELBtest": {
                    "Properties": {
                        "CrossZone": "true",
                        "ConnectionDrainingPolicy": {
                            "Enabled": True,
                            "Timeout": 10,
                        },
                        "HealthCheck": {
                            "HealthyThreshold": 3,
                            "Interval": 5,
                            "Target": "HTTP:80/healthcheck",
                            "Timeout": 2,
                            "UnhealthyThreshold": 3
                        },
                        "Scheme": "internal",
                        "Subnets": [
                            "subnet-123"
                        ],
                        "Listeners": [
                            {
                                "InstancePort": 80,
                                "InstanceProtocol": "HTTP",
                                "LoadBalancerPort": 80,
                                "Protocol": "HTTP"
                            }
                        ],
                        "Tags": [{"Key": "Name", "Value": "test::test"}],
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
                'internal': True,
                'subnets': ['subnet-123'],
                'dns': 'example.com',
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
                        "ConnectionDrainingPolicy": {
                            "Enabled": True,
                            "Timeout": 10,
                        },
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
                        "Tags": [{"Key": "Name", "Value": "test::test"}],
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
                        "ConnectionDrainingPolicy": {
                            "Enabled": True,
                            "Timeout": 10,
                        },
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
                        "Tags": [{"Key": "Name", "Value": "test::test"}],
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
                        "ConnectionDrainingPolicy": {
                            "Enabled": True,
                            "Timeout": 10,
                        },
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
                        ],
                        "Tags": [{"Key": "Name", "Value": "test::test"}],
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
                            "Enabled": True,
                            "S3BucketName": "c4-elb-logs",
                            "S3BucketPrefix": "stage/ais"
                        },
                        "AvailabilityZones": {
                            "Fn::GetAZs": ""
                        },
                        "CrossZone": "true",
                        "ConnectionDrainingPolicy": {
                            "Enabled": True,
                            "Timeout": 10,
                        },
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
                        "Tags": [
                            {
                                "Key": "Name",
                                "Value": "test::test"
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

    def test_sg_valid_vpc(self):
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
                                "SourceSecurityGroupId": "womble",
                                "ToPort": 22
                            },
                            {
                                "CidrIp": "10.1.2.0/24",
                                "FromPort": 80,
                                "IpProtocol": "tcp",
                                "ToPort": 80
                            }
                        ],
                        "VpcId": "test",
                    },
                    "Type": "AWS::EC2::SecurityGroup"
                }
            }
        }

        cfg = {
            'name': 'test',
            'environment': 'test',
        }
        res = {
            'instance': [],
            'load_balancer': [],
            'role': [],
            'secgroup': [{
                'name': 'test',
                'vpcid': 'test',
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
        }
        res = {
            'instance': [],
            'load_balancer': [],
            'role': [],
            'secgroup': [
                {
                    'name': 'womble',
                    'vpcid': 'vpc-123',
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
                    'vpcid': 'vpc-123',
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
        }
        res = {
            'instance': [],
            'load_balancer': [],
            'role': [],
            'secgroup': [{
                'name': 'test',
                'vpcid': 'vpc-123',
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
                        "HealthCheckType": "EC2",
                        "HealthCheckGracePeriod": 600,
                        "LaunchConfigurationName": {
                            "Ref": "LCapp"
                        },
                        "MaxSize": 6,
                        "MinSize": 6,
                        "Tags": [
                            {
                                "Key": "Name",
                                "PropagateAtLaunch": True,
                                "Value": "test::app::test"
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
                        "BlockDeviceMappings": [
                            {
                                "DeviceName": "/dev/xvdb",
                                "VirtualName": "ephemeral0"
                            },
                            {
                                "DeviceName": "/dev/xvdc",
                                "VirtualName": "ephemeral1"
                            }
                        ],
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
            'version': 'v1',
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
                'public': False,
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
                        "ConnectionDrainingPolicy": {
                            "Enabled": True,
                            "Timeout": 10,
                        },
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
                        "Tags": [
                            {
                                "Key": "Name",
                                "Value": "test::test"
                            },
                            {
                                "Key": "App",
                                "Value": "app"
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
                        "HealthCheckType": "EC2",
                        "HealthCheckGracePeriod": 600,
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
                                "Value": "test::app::test"
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
                        "BlockDeviceMappings": [
                            {
                                "DeviceName": "/dev/xvdb",
                                "VirtualName": "ephemeral0"
                            },
                            {
                                "DeviceName": "/dev/xvdc",
                                "VirtualName": "ephemeral1"
                            }
                        ],
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
                'lb': ['test'],
                'provisioner': {
                    'args': {
                        'apps': ['ais-jetty/v2.54-02'],
                        'appBucket': 'test',
                        'roleBucket': 'test',
                        'roles': ['jetty']
                    },
                    'provider': 'AWSFWProvisioner'},
                'public': False,
                'sg': [],
                'size': 'm1.large',
                'sshKey': 'bootstrap'
            }]
        }
        tmpl = out.add_resources(res, cfg)
        assert_equals(json.loads(tmpl), ret)

    @mock.patch('pmcf.provisioners.AWSFWProvisioner.userdata', _mock_ud)
    def test_instance_valid_block_device(self):
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
                        "HealthCheckType": "EC2",
                        "HealthCheckGracePeriod": 600,
                        "LaunchConfigurationName": {
                            "Ref": "LCapp"
                        },
                        "MaxSize": 6,
                        "MinSize": 6,
                        "Tags": [
                            {
                                "Key": "Name",
                                "PropagateAtLaunch": True,
                                "Value": "test::app::test"
                            },
                            {
                                "Key": "App",
                                "PropagateAtLaunch": True,
                                "Value": "app"
                            }
                        ],
                    },
                    "Type": "AWS::AutoScaling::AutoScalingGroup"
                },
                "LCapp": {
                    "Properties": {
                        "BlockDeviceMappings": [
                            {
                                "DeviceName": "/dev/xvdb",
                                "VirtualName": "ephemeral0"
                            },
                            {
                                "DeviceName": "/dev/xvdc",
                                "VirtualName": "ephemeral1"
                            },
                            {
                                "Ebs": {
                                    "VolumeSize": "10",
                                    "VolumeType": "gp2",
                                },
                                "DeviceName": "/dev/xvdd"
                            },
                        ],
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
                'block_device': [
                    {
                        'size': '10',
                        'type': 'gp2',
                        'device': '/dev/xvdd',
                    },
                ],
                'count': 6,
                'image': 'ami-e97f849e',
                'monitoring': False,
                'name': 'app',
                'provisioner': {
                    'args': {
                        'apps': ['ais-jetty/v2.54-02'],
                        'appBucket': 'test',
                        'roleBucket': 'test',
                        'roles': ['jetty'],
                        'profile': 'deploy-client',
                    },
                    'provider': 'AWSFWProvisioner'},
                'public': False,
                'sg': ['app'],
                'size': 'm1.large',
                'sshKey': 'bootstrap'
            }]
        }
        tmpl = out.add_resources(res, cfg)
        assert_equals(json.loads(tmpl), ret)

    @mock.patch('pmcf.strategy.bluegreen.BlueGreen.termination_policy',
                _mock_tp)
    @mock.patch('pmcf.provisioners.AWSFWProvisioner.userdata', _mock_ud)
    def test_instance_valid_termination_policy(self):
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
                        "HealthCheckType": "EC2",
                        "HealthCheckGracePeriod": 600,
                        "LaunchConfigurationName": {
                            "Ref": "LCapp"
                        },
                        "MaxSize": 6,
                        "MinSize": 6,
                        "Tags": [
                            {
                                "Key": "Name",
                                "PropagateAtLaunch": True,
                                "Value": "test::app::test"
                            },
                            {
                                "Key": "App",
                                "PropagateAtLaunch": True,
                                "Value": "app"
                            }
                        ],
                        "TerminationPolicies": ["OldestInstance"],
                    },
                    "Type": "AWS::AutoScaling::AutoScalingGroup"
                },
                "LCapp": {
                    "Properties": {
                        "BlockDeviceMappings": [
                            {
                                "DeviceName": "/dev/xvdb",
                                "VirtualName": "ephemeral0"
                            },
                            {
                                "DeviceName": "/dev/xvdc",
                                "VirtualName": "ephemeral1"
                            }
                        ],
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
                'provisioner': {
                    'args': {
                        'apps': ['ais-jetty/v2.54-02'],
                        'appBucket': 'test',
                        'roleBucket': 'test',
                        'roles': ['jetty'],
                        'profile': 'deploy-client',
                    },
                    'provider': 'AWSFWProvisioner'},
                'public': False,
                'sg': ['app'],
                'size': 'm1.large',
                'sshKey': 'bootstrap'
            }]
        }
        tmpl = out.add_resources(res, cfg)
        assert_equals(json.loads(tmpl), ret)

    @mock.patch('pmcf.provisioners.AWSFWProvisioner.userdata', _mock_ud)
    def test_instance_valid_notify(self):
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
                        "HealthCheckType": "EC2",
                        "HealthCheckGracePeriod": 600,
                        "LaunchConfigurationName": {
                            "Ref": "LCapp"
                        },
                        "MaxSize": 6,
                        "MinSize": 6,
                        "Tags": [
                            {
                                "Key": "Name",
                                "PropagateAtLaunch": True,
                                "Value": "test::app::test"
                            },
                            {
                                "Key": "App",
                                "PropagateAtLaunch": True,
                                "Value": "app"
                            }
                        ],
                        "NotificationConfiguration": {
                            "TopicARN": "test",
                            "NotificationTypes": [
                                "autoscaling:EC2_INSTANCE_LAUNCH",
                                "autoscaling:EC2_INSTANCE_LAUNCH_ERROR",
                                "autoscaling:EC2_INSTANCE_TERMINATE",
                                "autoscaling:EC2_INSTANCE_TERMINATE_ERROR"
                            ]
                        }
                    },
                    "Type": "AWS::AutoScaling::AutoScalingGroup"
                },
                "LCapp": {
                    "Properties": {
                        "BlockDeviceMappings": [
                            {
                                "DeviceName": "/dev/xvdb",
                                "VirtualName": "ephemeral0"
                            },
                            {
                                "DeviceName": "/dev/xvdc",
                                "VirtualName": "ephemeral1"
                            }
                        ],
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
                'notify': 'test',
                'provisioner': {
                    'args': {
                        'apps': ['ais-jetty/v2.54-02'],
                        'appBucket': 'test',
                        'roleBucket': 'test',
                        'roles': ['jetty'],
                        'profile': 'deploy-client',
                    },
                    'provider': 'AWSFWProvisioner'},
                'public': False,
                'sg': ['app'],
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
                        "HealthCheckType": "EC2",
                        "HealthCheckGracePeriod": 600,
                        "LaunchConfigurationName": {
                            "Ref": "LCapp"
                        },
                        "MaxSize": 6,
                        "MinSize": 6,
                        "Tags": [
                            {
                                "Key": "Name",
                                "PropagateAtLaunch": True,
                                "Value": "test::app::test"
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
                        "BlockDeviceMappings": [
                            {
                                "DeviceName": "/dev/xvdb",
                                "VirtualName": "ephemeral0"
                            },
                            {
                                "DeviceName": "/dev/xvdc",
                                "VirtualName": "ephemeral1"
                            }
                        ],
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
                'provisioner': {
                    'args': {
                        'apps': ['ais-jetty/v2.54-02'],
                        'appBucket': 'test',
                        'roleBucket': 'test',
                        'roles': ['jetty'],
                        'profile': 'deploy-client',
                    },
                    'provider': 'AWSFWProvisioner'},
                'public': False,
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
                        "HealthCheckType": "EC2",
                        "HealthCheckGracePeriod": 600,
                        "LaunchConfigurationName": {
                            "Ref": "LCapp"
                        },
                        "MaxSize": 6,
                        "MinSize": 6,
                        "Tags": [
                            {
                                "Key": "Name",
                                "PropagateAtLaunch": True,
                                "Value": "test::app::test"
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
                        "BlockDeviceMappings": [
                            {
                                "DeviceName": "/dev/xvdb",
                                "VirtualName": "ephemeral0"
                            },
                            {
                                "DeviceName": "/dev/xvdc",
                                "VirtualName": "ephemeral1"
                            }
                        ],
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
                'provisioner': {
                    'args': {
                        'apps': ['ais-jetty/v2.54-02'],
                        'appBucket': 'test',
                        'roleBucket': 'test',
                        'roles': ['jetty'],
                        'profile': 'deploy-client',
                    },
                    'provider': 'AWSFWProvisioner'},
                'public': False,
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
                        "HealthCheckType": "EC2",
                        "HealthCheckGracePeriod": 600,
                        "LaunchConfigurationName": {
                            "Ref": "LCapp"
                        },
                        "MaxSize": 6,
                        "MinSize": 6,
                        "Tags": [
                            {
                                "Key": "Name",
                                "PropagateAtLaunch": True,
                                "Value": "test::app::test"
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
                        "BlockDeviceMappings": [
                            {
                                "DeviceName": "/dev/xvdb",
                                "VirtualName": "ephemeral0"
                            },
                            {
                                "DeviceName": "/dev/xvdc",
                                "VirtualName": "ephemeral1"
                            }
                        ],
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
                'provisioner': {
                    'args': {
                        'apps': ['ais-jetty/v2.54-02'],
                        'appBucket': 'test',
                        'roleBucket': 'test',
                        'roles': ['jetty'],
                        'profile': 'deploy-client',
                    },
                    'provider': 'AWSFWProvisioner'},
                'public': False,
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
        b = 'arn:aws:s3:::test/artifacts/'
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
                        "HealthCheckType": "EC2",
                        "HealthCheckGracePeriod": 600,
                        "LaunchConfigurationName": {
                            "Ref": "LCapp"
                        },
                        "MaxSize": 6,
                        "MinSize": 6,
                        "Tags": [
                            {
                                "Key": "Name",
                                "PropagateAtLaunch": True,
                                "Value": "test::app::test"
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
                        "BlockDeviceMappings": [
                            {
                                "DeviceName": "/dev/xvdb",
                                "VirtualName": "ephemeral0"
                            },
                            {
                                "DeviceName": "/dev/xvdc",
                                "VirtualName": "ephemeral1"
                            }
                        ],
                        "IamInstanceProfile": {
                            "Ref": "Profileapp"
                        },
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
                'Policyapp': {
                    'Properties': {
                        'PolicyDocument': {
                            'Statement': [{
                                'Action': ['s3:GetObject'],
                                'Effect': 'Allow',
                                'Resource': [
                                    b + 'infrastructure/test/test/foo.zip',
                                    b + 'infrastructure/hiera.tar.gz',
                                    b + 'application/test/test/bar.zip'
                                ]
                            }],
                            'Version': '2012-10-17'
                        },
                        'PolicyName': 'iam-app-test',
                        'Roles': [{'Ref': 'Roleapp'}]
                    },
                    'Type': 'AWS::IAM::Policy'
                },
                "Profileapp": {
                    "Properties": {
                        "Path": "/app/test/",
                        "Roles": [
                            {
                                "Ref": "Roleapp"
                            }
                        ]
                    },
                    "Type": "AWS::IAM::InstanceProfile"
                },
                "Roleapp": {
                    "Properties": {
                        "AssumeRolePolicyDocument": {
                            "Statement": [
                                {
                                    "Action": [
                                        "sts:AssumeRole"
                                    ],
                                    "Effect": "Allow",
                                    "Principal": {
                                        "Service": [
                                            "ec2.amazonaws.com"
                                        ]
                                    }
                                }
                            ],
                            "Version": "2012-10-17"
                        },
                        "Path": "/app/test/"
                    },
                    "Type": "AWS::IAM::Role"
                },
                "Handleapp": {
                    "Type": "AWS::CloudFormation::WaitConditionHandle"
                },
                "Waitapp": {
                    "DependsOn": "ASGapp",
                    "Properties": {
                        "Handle": {
                            "Ref": "Handleapp"
                        },
                        "Timeout": 3600,
                        "Count": 1,
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
                    'args': {
                        'infrastructure': 'foo.zip',
                        'application': 'bar.zip',
                        'bucket': 'test',
                    },
                    'provider': 'PuppetProvisioner',
                },
                'public': False,
                'sg': [],
                'size': 'm1.large',
                'sshKey': 'bootstrap'
            }]
        }
        tmpl = out.add_resources(res, cfg)
        assert_equals(json.loads(tmpl), ret)

    @mock.patch('pmcf.provisioners.AWSFWProvisioner.userdata', _mock_ud)
    def test_instance_valid_depends_on(self):
        out = JSONOutput()
        ret = {
            "AWSTemplateFormatVersion": "2010-09-09",
            "Description": "test test stack",
            "Resources": {
                "LCapp2": {
                    "Type": "AWS::AutoScaling::LaunchConfiguration",
                    "Properties": {
                        "BlockDeviceMappings": [
                            {
                                "DeviceName": "/dev/xvdb",
                                "VirtualName": "ephemeral0"
                            },
                            {
                                "DeviceName": "/dev/xvdc",
                                "VirtualName": "ephemeral1"
                            }
                        ],
                        "UserData": {
                            "Fn::Base64": ""
                        },
                        "InstanceMonitoring": "false",
                        "ImageId": "ami-e97f849e",
                        "KeyName": "bootstrap",
                        "SecurityGroups": [],
                        "InstanceType": "m1.large"
                    }
                },
                "ASGapp2": {
                    "Type": "AWS::AutoScaling::AutoScalingGroup",
                    "Properties": {
                        "DesiredCapacity": 6,
                        "HealthCheckType": "EC2",
                        "HealthCheckGracePeriod": 600,
                        "Tags": [
                            {
                                "Value": "test::app2::test",
                                "PropagateAtLaunch": True,
                                "Key": "Name"
                            },
                            {
                                "Value": "app2",
                                "PropagateAtLaunch": True,
                                "Key": "App"
                            }
                        ],
                        "MinSize": 6,
                        "MaxSize": 6,
                        "LaunchConfigurationName": {
                            "Ref": "LCapp2"
                        },
                        "AvailabilityZones": {
                            "Fn::GetAZs": ""
                        }
                    },
                    "DependsOn": "ASGapp"
                },
                "ASGapp": {
                    "Type": "AWS::AutoScaling::AutoScalingGroup",
                    "Properties": {
                        "DesiredCapacity": 6,
                        "HealthCheckType": "EC2",
                        "HealthCheckGracePeriod": 600,
                        "Tags": [
                            {
                                "Value": "test::app::test",
                                "PropagateAtLaunch": True,
                                "Key": "Name"
                            },
                            {
                                "Value": "app",
                                "PropagateAtLaunch": True,
                                "Key": "App"
                            }
                        ],
                        "MinSize": 6,
                        "MaxSize": 6,
                        "LaunchConfigurationName": {
                            "Ref": "LCapp"
                        },
                        "AvailabilityZones": {
                            "Fn::GetAZs": ""
                        }
                    }
                },
                "LCapp": {
                    "Type": "AWS::AutoScaling::LaunchConfiguration",
                    "Properties": {
                        "BlockDeviceMappings": [
                            {
                                "DeviceName": "/dev/xvdb",
                                "VirtualName": "ephemeral0"
                            },
                            {
                                "DeviceName": "/dev/xvdc",
                                "VirtualName": "ephemeral1"
                            }
                        ],
                        "UserData": {
                            "Fn::Base64": ""
                        },
                        "InstanceMonitoring": "false",
                        "ImageId": "ami-e97f849e",
                        "KeyName": "bootstrap",
                        "SecurityGroups": [],
                        "InstanceType": "m1.large"
                    }
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
            'instance': [
                {
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
                    'public': False,
                    'sg': [],
                    'size': 'm1.large',
                    'sshKey': 'bootstrap'
                },
                {
                    'block_device': [],
                    'count': 6,
                    'depends': 'ASGapp',
                    'image': 'ami-e97f849e',
                    'monitoring': False,
                    'name': 'app2',
                    'provisioner': {
                        'args': {
                            'apps': ['ais-jetty/v2.54-02'],
                            'appBucket': 'test',
                            'roleBucket': 'test',
                            'roles': ['jetty']
                        },
                        'provider': 'AWSFWProvisioner'},
                    'public': False,
                    'sg': [],
                    'size': 'm1.large',
                    'sshKey': 'bootstrap'
                }
            ]
        }
        tmpl = out.add_resources(res, cfg)
        assert_equals(json.loads(tmpl), ret)

    @mock.patch('pmcf.provisioners.AWSFWProvisioner.userdata', _mock_ud)
    def test_instance_valid_subnets_vpcid(self):
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
                        "HealthCheckType": "EC2",
                        "HealthCheckGracePeriod": 600,
                        "LaunchConfigurationName": {
                            "Ref": "LCapp"
                        },
                        "MaxSize": 6,
                        "MinSize": 6,
                        "Tags": [
                            {
                                "Key": "Name",
                                "PropagateAtLaunch": True,
                                "Value": "test::app::test"
                            },
                            {
                                "Key": "App",
                                "PropagateAtLaunch": True,
                                "Value": "app"
                            }
                        ],
                        "VPCZoneIdentifier": ["test-123"],
                    },
                    "Type": "AWS::AutoScaling::AutoScalingGroup"
                },
                "LCapp": {
                    "Properties": {
                        "BlockDeviceMappings": [
                            {
                                "DeviceName": "/dev/xvdb",
                                "VirtualName": "ephemeral0"
                            },
                            {
                                "DeviceName": "/dev/xvdc",
                                "VirtualName": "ephemeral1"
                            }
                        ],
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
            'subnets': ['test-123'],
            'vpcid': 'vpc-123'
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
                'public': False,
                'sg': [],
                'size': 'm1.large',
                'sshKey': 'bootstrap',
                'subnets': ['test-123'],
            }]
        }
        tmpl = out.add_resources(res, cfg)
        assert_equals(json.loads(tmpl), ret)

    def test_instance_valid_dns(self):
        out = JSONOutput()
        ret = {
            "AWSTemplateFormatVersion": "2010-09-09",
            "Description": "test test stack",
            "Resources": {
                "ASGapp": {
                    "Properties": {
                        "AvailabilityZones": {"Fn::GetAZs": ""},
                        "DesiredCapacity": 6,
                        "HealthCheckType": "EC2",
                        "HealthCheckGracePeriod": 600,
                        "LaunchConfigurationName": {"Ref": "LCapp"},
                        "MaxSize": 6,
                        "MinSize": 6,
                        "Tags": [
                            {
                                "Key": "Name",
                                "PropagateAtLaunch": True,
                                "Value": "test::app::test"
                            },
                            {
                                "Key": "App",
                                "PropagateAtLaunch": True,
                                "Value": "app"
                            },
                            {
                                "Key": "DNS",
                                "PropagateAtLaunch": True,
                                "Value":
                                    '{"r": "app", ' +
                                    '"t": "per-instance-public", ' +
                                    '"z": "test.aws.sequoia.piksel.com."}'
                            }
                        ]
                    },
                    "Type": "AWS::AutoScaling::AutoScalingGroup"
                },
                "LCapp": {
                    "Properties": {
                        "BlockDeviceMappings": [
                            {
                                "DeviceName": "/dev/xvdb",
                                "VirtualName": "ephemeral0"
                            },
                            {
                                "DeviceName": "/dev/xvdc",
                                "VirtualName": "ephemeral1"
                            }
                        ],
                        "ImageId": "ami-e97f849e",
                        "InstanceMonitoring": "false",
                        "InstanceType": "m1.large",
                        "KeyName": "bootstrap",
                        "SecurityGroups": []
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
                'dns': {
                    'type': 'per-instance-public',
                    'zone': 'aws.sequoia.piksel.com.',
                },
                'image': 'ami-e97f849e',
                'monitoring': False,
                'name': 'app',
                'provisioner': {
                    'args': {},
                    'provider': 'NoopProvisioner'},
                'public': False,
                'sg': [],
                'size': 'm1.large',
                'sshKey': 'bootstrap'
            }]
        }
        tmpl = out.add_resources(res, cfg)
        assert_equals(json.loads(tmpl), ret)

    @mock.patch('pmcf.provisioners.AWSFWProvisioner.userdata', _mock_ud)
    def test_instance_valid_public(self):
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
                        "HealthCheckType": "EC2",
                        "HealthCheckGracePeriod": 600,
                        "LaunchConfigurationName": {
                            "Ref": "LCapp"
                        },
                        "MaxSize": 6,
                        "MinSize": 6,
                        "Tags": [
                            {
                                "Key": "Name",
                                "PropagateAtLaunch": True,
                                "Value": "test::app::test"
                            },
                            {
                                "Key": "App",
                                "PropagateAtLaunch": True,
                                "Value": "app"
                            }
                        ],
                    },
                    "Type": "AWS::AutoScaling::AutoScalingGroup"
                },
                "LCapp": {
                    "Properties": {
                        "BlockDeviceMappings": [
                            {
                                "DeviceName": "/dev/xvdb",
                                "VirtualName": "ephemeral0"
                            },
                            {
                                "DeviceName": "/dev/xvdc",
                                "VirtualName": "ephemeral1"
                            }
                        ],
                        "AssociatePublicIpAddress": "true",
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
                'public': True,
                'sg': [],
                'size': 'm1.large',
                'sshKey': 'bootstrap'
            }]
        }
        tmpl = out.add_resources(res, cfg)
        assert_equals(json.loads(tmpl), ret)

    @mock.patch('pmcf.provisioners.AWSFWProvisioner.userdata', _mock_ud)
    def test_instance_valid_scaling_policy(self):
        out = JSONOutput()
        ret = {
            "AWSTemplateFormatVersion": "2010-09-09",
            "Description": "test test stack",
            "Resources": {
                "ASGScaleUpapp": {
                    "Properties": {
                        "AutoScalingGroupName": {
                            "Ref": "ASGapp"
                        },
                        "AdjustmentType": "ChangeInCapacity",
                        "ScalingAdjustment": "1",
                        "Cooldown": 300
                    },
                    "Type": "AWS::AutoScaling::ScalingPolicy"
                },
                "ASGScaleDownapp": {
                    "Properties": {
                        "AutoScalingGroupName": {
                            "Ref": "ASGapp"
                        },
                        "AdjustmentType": "ChangeInCapacity",
                        "ScalingAdjustment": "-1",
                        "Cooldown": 300
                    },
                    "Type": "AWS::AutoScaling::ScalingPolicy"
                },
                "CloudwatchDownapp": {
                    "Properties": {
                        "Statistic": "Average",
                        "EvaluationPeriods": 5,
                        "OKActions": [
                            {
                                "Ref": "ASGScaleDownapp"
                            }
                        ],
                        "MetricName": "nodejs_concurrents",
                        "ActionsEnabled": "true",
                        "Threshold": "35",
                        "Period": 300,
                        "ComparisonOperator": "GreaterThanThreshold",
                        "Unit": "Count",
                        "Namespace": "Piksel/sequoiaidentity",
                        "Dimensions": [
                            {
                                "Name": "AutoScalingGroupName",
                                "Value": {
                                    "Ref": "ASGapp"
                                }
                            }
                        ]
                    },
                    "Type": "AWS::CloudWatch::Alarm"
                },
                "CloudwatchUpapp": {
                    "Properties": {
                        "Statistic": "Average",
                        "EvaluationPeriods": 5,
                        "MetricName": "nodejs_concurrents",
                        "AlarmActions": [
                            {
                                "Ref": "ASGScaleUpapp"
                            }
                        ],
                        "ActionsEnabled": "true",
                        "Threshold": "50",
                        "Period": 300,
                        "ComparisonOperator": "GreaterThanThreshold",
                        "Unit": "Count",
                        "Namespace": "Piksel/sequoiaidentity",
                        "Dimensions": [
                            {
                                "Name": "AutoScalingGroupName",
                                "Value": {
                                    "Ref": "ASGapp"
                                }
                            }
                        ]
                    },
                    "Type": "AWS::CloudWatch::Alarm"
                },
                "ASGapp": {
                    "Properties": {
                        "AvailabilityZones": {
                            "Fn::GetAZs": ""
                        },
                        "DesiredCapacity": 6,
                        "HealthCheckType": "EC2",
                        "HealthCheckGracePeriod": 600,
                        "LaunchConfigurationName": {
                            "Ref": "LCapp"
                        },
                        "MaxSize": 6,
                        "MinSize": 6,
                        "Tags": [
                            {
                                "Key": "Name",
                                "PropagateAtLaunch": True,
                                "Value": "test::app::test"
                            },
                            {
                                "Key": "App",
                                "PropagateAtLaunch": True,
                                "Value": "app"
                            }
                        ],
                    },
                    "Type": "AWS::AutoScaling::AutoScalingGroup"
                },
                "LCapp": {
                    "Properties": {
                        "BlockDeviceMappings": [
                            {
                                "DeviceName": "/dev/xvdb",
                                "VirtualName": "ephemeral0"
                            },
                            {
                                "DeviceName": "/dev/xvdc",
                                "VirtualName": "ephemeral1"
                            }
                        ],
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
                'public': False,
                'sg': [],
                'scaling_policy': {
                    'metric': "Piksel/sequoiaidentity/nodejs_concurrents",
                    'unit': 'Count',
                    'up': {
                        'stat': 'Average',
                        'condition': "> 50",
                        'change': '1',
                    },
                    'down': {
                        'stat': 'Average',
                        'condition': "> 35",
                        'change': "-1",
                    },
                },
                'size': 'm1.large',
                'sshKey': 'bootstrap'
            }]
        }
        tmpl = out.add_resources(res, cfg)
        assert_equals(json.loads(tmpl), ret)

    @mock.patch('pmcf.provisioners.AWSFWProvisioner.userdata', _mock_ud)
    def test_instance_valid_scaling_policy_monitoring(self):
        out = JSONOutput()
        ret = {
            "AWSTemplateFormatVersion": "2010-09-09",
            "Description": "test test stack",
            "Resources": {
                "ASGScaleUpapp": {
                    "Properties": {
                        "AutoScalingGroupName": {
                            "Ref": "ASGapp"
                        },
                        "AdjustmentType": "ChangeInCapacity",
                        "ScalingAdjustment": "1",
                        "Cooldown": 300
                    },
                    "Type": "AWS::AutoScaling::ScalingPolicy"
                },
                "ASGScaleDownapp": {
                    "Properties": {
                        "AutoScalingGroupName": {
                            "Ref": "ASGapp"
                        },
                        "AdjustmentType": "ChangeInCapacity",
                        "ScalingAdjustment": "-1",
                        "Cooldown": 300
                    },
                    "Type": "AWS::AutoScaling::ScalingPolicy"
                },
                "CloudwatchDownapp": {
                    "Properties": {
                        "Statistic": "Average",
                        "EvaluationPeriods": 5,
                        "OKActions": [
                            {
                                "Ref": "ASGScaleDownapp"
                            }
                        ],
                        "MetricName": "nodejs_concurrents",
                        "ActionsEnabled": "true",
                        "Threshold": "35",
                        "Period": 60,
                        "ComparisonOperator": "GreaterThanThreshold",
                        "Unit": "Count",
                        "Namespace": "Piksel/sequoiaidentity",
                        "Dimensions": [
                            {
                                "Name": "AutoScalingGroupName",
                                "Value": {
                                    "Ref": "ASGapp"
                                }
                            }
                        ]
                    },
                    "Type": "AWS::CloudWatch::Alarm"
                },
                "CloudwatchUpapp": {
                    "Properties": {
                        "Statistic": "Average",
                        "EvaluationPeriods": 5,
                        "MetricName": "nodejs_concurrents",
                        "AlarmActions": [
                            {
                                "Ref": "ASGScaleUpapp"
                            }
                        ],
                        "ActionsEnabled": "true",
                        "Threshold": "50",
                        "Period": 60,
                        "ComparisonOperator": "GreaterThanThreshold",
                        "Unit": "Count",
                        "Namespace": "Piksel/sequoiaidentity",
                        "Dimensions": [
                            {
                                "Name": "AutoScalingGroupName",
                                "Value": {
                                    "Ref": "ASGapp"
                                }
                            }
                        ]
                    },
                    "Type": "AWS::CloudWatch::Alarm"
                },
                "ASGapp": {
                    "Properties": {
                        "AvailabilityZones": {
                            "Fn::GetAZs": ""
                        },
                        "DesiredCapacity": 6,
                        "HealthCheckType": "EC2",
                        "HealthCheckGracePeriod": 600,
                        "LaunchConfigurationName": {
                            "Ref": "LCapp"
                        },
                        "MaxSize": 6,
                        "MinSize": 6,
                        "Tags": [
                            {
                                "Key": "Name",
                                "PropagateAtLaunch": True,
                                "Value": "test::app::test"
                            },
                            {
                                "Key": "App",
                                "PropagateAtLaunch": True,
                                "Value": "app"
                            }
                        ],
                    },
                    "Type": "AWS::AutoScaling::AutoScalingGroup"
                },
                "LCapp": {
                    "Properties": {
                        "BlockDeviceMappings": [
                            {
                                "DeviceName": "/dev/xvdb",
                                "VirtualName": "ephemeral0"
                            },
                            {
                                "DeviceName": "/dev/xvdc",
                                "VirtualName": "ephemeral1"
                            }
                        ],
                        "ImageId": "ami-e97f849e",
                        "InstanceMonitoring": "true",
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
                'monitoring': True,
                'name': 'app',
                'provisioner': {
                    'args': {
                        'apps': ['ais-jetty/v2.54-02'],
                        'appBucket': 'test',
                        'roleBucket': 'test',
                        'roles': ['jetty']
                    },
                    'provider': 'AWSFWProvisioner'},
                'public': False,
                'sg': [],
                'scaling_policy': {
                    'metric': "Piksel/sequoiaidentity/nodejs_concurrents",
                    'unit': 'Count',
                    'up': {
                        'stat': 'Average',
                        'condition': "> 50",
                        'change': '1',
                    },
                    'down': {
                        'stat': 'Average',
                        'condition': "> 35",
                        'change': "-1",
                    },
                },
                'size': 'm1.large',
                'sshKey': 'bootstrap'
            }]
        }
        tmpl = out.add_resources(res, cfg)
        assert_equals(json.loads(tmpl), ret)

    def test_instance_valid_timed_scaling_policy(self):
        out = JSONOutput()
        ret = {
            "AWSTemplateFormatVersion": "2010-09-09", 
            "Description": "test test stack", 
            "Resources": {
                "ASGTimedScaleDownapp": {
                    "Properties": {
                        "AutoScalingGroupName": {
                            "Ref": "ASGapp"
                        }, 
                        "DesiredCapacity": 0, 
                        "Recurrence": "0 8 * * *"
                    }, 
                    "Type": "AWS::AutoScaling::ScheduledAction"
                }, 
                "ASGTimedScaleUpapp": {
                    "Properties": {
                        "AutoScalingGroupName": {
                            "Ref": "ASGapp"
                        }, 
                        "DesiredCapacity": 1, 
                        "Recurrence": "0 7 * * *"
                    }, 
                    "Type": "AWS::AutoScaling::ScheduledAction"
                }, 
                "ASGapp": {
                    "Properties": {
                        "AvailabilityZones": {
                            "Fn::GetAZs": ""
                        }, 
                        "DesiredCapacity": 0, 
                        "HealthCheckGracePeriod": 600, 
                        "HealthCheckType": "EC2", 
                        "LaunchConfigurationName": {
                            "Ref": "LCapp"
                        }, 
                        "MaxSize": 0, 
                        "MinSize": 0, 
                        "Tags": [
                            {
                                "Key": "Name", 
                                "PropagateAtLaunch": True, 
                                "Value": "test::app::test"
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
                        "BlockDeviceMappings": [
                            {
                                "DeviceName": "/dev/xvdb", 
                                "VirtualName": "ephemeral0"
                            }, 
                            {
                                "DeviceName": "/dev/xvdc", 
                                "VirtualName": "ephemeral1"
                            }
                        ], 
                        "ImageId": "ami-e97f849e", 
                        "InstanceMonitoring": "false", 
                        "InstanceType": "m1.large", 
                        "KeyName": "bootstrap", 
                        "SecurityGroups": []
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
                'count': 0,
                'image': 'ami-e97f849e',
                'monitoring': False,
                'name': 'app',
                'provisioner': {
                    'args': {},
                    'provider': 'NoopProvisioner'
                },
                'public': False,
                'sg': [],
                'timed_scaling_policy': {
                    'up': {
                        'count': 1,
                        'recurrence': "0 7 * * *",
                    },
                    'down': {
                        'count': 0,
                        'recurrence': "0 8 * * *",
                    },
                },
                'size': 'm1.large',
                'sshKey': 'bootstrap'
            }]
        }
        tmpl = out.add_resources(res, cfg)
        assert_equals(json.loads(tmpl), ret)

    def test_instance_valid_timed_scaling_policy_min(self):
        out = JSONOutput()
        ret = {
            "AWSTemplateFormatVersion": "2010-09-09", 
            "Description": "test test stack", 
            "Resources": {
                "ASGTimedScaleDownapp": {
                    "Properties": {
                        "AutoScalingGroupName": {
                            "Ref": "ASGapp"
                        }, 
                        "MinSize": 1, 
                        "Recurrence": "0 8 * * *"
                    }, 
                    "Type": "AWS::AutoScaling::ScheduledAction"
                }, 
                "ASGTimedScaleUpapp": {
                    "Properties": {
                        "AutoScalingGroupName": {
                            "Ref": "ASGapp"
                        }, 
                        "MinSize": 2, 
                        "Recurrence": "0 7 * * *"
                    }, 
                    "Type": "AWS::AutoScaling::ScheduledAction"
                }, 
                "ASGapp": {
                    "Properties": {
                        "AvailabilityZones": {
                            "Fn::GetAZs": ""
                        }, 
                        "DesiredCapacity": 1, 
                        "HealthCheckGracePeriod": 600, 
                        "HealthCheckType": "EC2", 
                        "LaunchConfigurationName": {
                            "Ref": "LCapp"
                        }, 
                        "MaxSize": 4, 
                        "MinSize": 1, 
                        "Tags": [
                            {
                                "Key": "Name", 
                                "PropagateAtLaunch": True, 
                                "Value": "test::app::test"
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
                        "BlockDeviceMappings": [
                            {
                                "DeviceName": "/dev/xvdb", 
                                "VirtualName": "ephemeral0"
                            }, 
                            {
                                "DeviceName": "/dev/xvdc", 
                                "VirtualName": "ephemeral1"
                            }
                        ], 
                        "ImageId": "ami-e97f849e", 
                        "InstanceMonitoring": "false", 
                        "InstanceType": "m1.large", 
                        "KeyName": "bootstrap", 
                        "SecurityGroups": []
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
                'count': 1,
                'min': 1,
                'max': 4,
                'image': 'ami-e97f849e',
                'monitoring': False,
                'name': 'app',
                'provisioner': {
                    'args': {},
                    'provider': 'NoopProvisioner'
                },
                'public': False,
                'sg': [],
                'timed_scaling_policy': {
                    'up': {
                        'min': 2,
                        'recurrence': "0 7 * * *",
                    },
                    'down': {
                        'min': 1,
                        'recurrence': "0 8 * * *",
                    },
                },
                'size': 'm1.large',
                'sshKey': 'bootstrap'
            }]
        }
        tmpl = out.add_resources(res, cfg)
        assert_equals(json.loads(tmpl), ret)

    def test_instance_valid_timed_scaling_policy_max(self):
        out = JSONOutput()
        ret = {
            "AWSTemplateFormatVersion": "2010-09-09", 
            "Description": "test test stack", 
            "Resources": {
                "ASGTimedScaleDownapp": {
                    "Properties": {
                        "AutoScalingGroupName": {
                            "Ref": "ASGapp"
                        }, 
                        "MaxSize": 4, 
                        "Recurrence": "0 8 * * *"
                    }, 
                    "Type": "AWS::AutoScaling::ScheduledAction"
                }, 
                "ASGTimedScaleUpapp": {
                    "Properties": {
                        "AutoScalingGroupName": {
                            "Ref": "ASGapp"
                        }, 
                        "MaxSize": 6, 
                        "Recurrence": "0 7 * * *"
                    }, 
                    "Type": "AWS::AutoScaling::ScheduledAction"
                }, 
                "ASGapp": {
                    "Properties": {
                        "AvailabilityZones": {
                            "Fn::GetAZs": ""
                        }, 
                        "DesiredCapacity": 1, 
                        "HealthCheckGracePeriod": 600, 
                        "HealthCheckType": "EC2", 
                        "LaunchConfigurationName": {
                            "Ref": "LCapp"
                        }, 
                        "MaxSize": 4, 
                        "MinSize": 1, 
                        "Tags": [
                            {
                                "Key": "Name", 
                                "PropagateAtLaunch": True, 
                                "Value": "test::app::test"
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
                        "BlockDeviceMappings": [
                            {
                                "DeviceName": "/dev/xvdb", 
                                "VirtualName": "ephemeral0"
                            }, 
                            {
                                "DeviceName": "/dev/xvdc", 
                                "VirtualName": "ephemeral1"
                            }
                        ], 
                        "ImageId": "ami-e97f849e", 
                        "InstanceMonitoring": "false", 
                        "InstanceType": "m1.large", 
                        "KeyName": "bootstrap", 
                        "SecurityGroups": []
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
                'count': 1,
                'min': 1,
                'max': 4,
                'image': 'ami-e97f849e',
                'monitoring': False,
                'name': 'app',
                'provisioner': {
                    'args': {},
                    'provider': 'NoopProvisioner'
                },
                'public': False,
                'sg': [],
                'timed_scaling_policy': {
                    'up': {
                        'max': 6,
                        'recurrence': "0 7 * * *",
                    },
                    'down': {
                        'max': 4,
                        'recurrence': "0 8 * * *",
                    },
                },
                'size': 'm1.large',
                'sshKey': 'bootstrap'
            }]
        }
        tmpl = out.add_resources(res, cfg)
        assert_equals(json.loads(tmpl), ret)

    def test_instance_valid_scaling_policy_percent(self):
        out = JSONOutput()
        ret = {
            "AWSTemplateFormatVersion": "2010-09-09", 
            "Description": "test test stack", 
            "Resources": {
                "ASGScaleDownapp": {
                    "Properties": {
                        "AdjustmentType": "PercentChangeInCapacity", 
                        "AutoScalingGroupName": {
                            "Ref": "ASGapp"
                        }, 
                        "Cooldown": 300, 
                        "ScalingAdjustment": "-50"
                    }, 
                    "Type": "AWS::AutoScaling::ScalingPolicy"
                }, 
                "ASGScaleUpapp": {
                    "Properties": {
                        "AdjustmentType": "PercentChangeInCapacity", 
                        "AutoScalingGroupName": {
                            "Ref": "ASGapp"
                        }, 
                        "Cooldown": 300, 
                        "ScalingAdjustment": "50"
                    }, 
                    "Type": "AWS::AutoScaling::ScalingPolicy"
                }, 
                "ASGapp": {
                    "Properties": {
                        "AvailabilityZones": {
                            "Fn::GetAZs": ""
                        }, 
                        "DesiredCapacity": 6, 
                        "HealthCheckGracePeriod": 600, 
                        "HealthCheckType": "EC2", 
                        "LaunchConfigurationName": {
                            "Ref": "LCapp"
                        }, 
                        "MaxSize": 6, 
                        "MinSize": 6, 
                        "Tags": [
                            {
                                "Key": "Name", 
                                "PropagateAtLaunch": True, 
                                "Value": "test::app::test"
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
                "CloudwatchDownapp": {
                    "Properties": {
                        "ActionsEnabled": "true", 
                        "ComparisonOperator": "GreaterThanThreshold", 
                        "Dimensions": [
                            {
                                "Name": "AutoScalingGroupName", 
                                "Value": {
                                    "Ref": "ASGapp"
                                }
                            }
                        ], 
                        "EvaluationPeriods": 5, 
                        "MetricName": "nodejs_concurrents", 
                        "Namespace": "Piksel/sequoiaidentity", 
                        "OKActions": [
                            {
                                "Ref": "ASGScaleDownapp"
                            }
                        ], 
                        "Period": 300, 
                        "Statistic": "Average", 
                        "Threshold": "35", 
                        "Unit": "Count"
                    }, 
                    "Type": "AWS::CloudWatch::Alarm"
                }, 
                "CloudwatchUpapp": {
                    "Properties": {
                        "ActionsEnabled": "true", 
                        "AlarmActions": [
                            {
                                "Ref": "ASGScaleUpapp"
                            }
                        ], 
                        "ComparisonOperator": "GreaterThanThreshold", 
                        "Dimensions": [
                            {
                                "Name": "AutoScalingGroupName", 
                                "Value": {
                                    "Ref": "ASGapp"
                                }
                            }
                        ], 
                        "EvaluationPeriods": 5, 
                        "MetricName": "nodejs_concurrents", 
                        "Namespace": "Piksel/sequoiaidentity", 
                        "Period": 300, 
                        "Statistic": "Average", 
                        "Threshold": "50", 
                        "Unit": "Count"
                    }, 
                    "Type": "AWS::CloudWatch::Alarm"
                }, 
                "LCapp": {
                    "Properties": {
                        "BlockDeviceMappings": [
                            {
                                "DeviceName": "/dev/xvdb", 
                                "VirtualName": "ephemeral0"
                            }, 
                            {
                                "DeviceName": "/dev/xvdc", 
                                "VirtualName": "ephemeral1"
                            }
                        ], 
                        "ImageId": "ami-e97f849e", 
                        "InstanceMonitoring": "false", 
                        "InstanceType": "m1.large", 
                        "KeyName": "bootstrap", 
                        "SecurityGroups": []
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
                    'args': {},
                    'provider': 'NoopProvisioner'
                },
                'public': False,
                'sg': [],
                'scaling_policy': {
                    'metric': "Piksel/sequoiaidentity/nodejs_concurrents",
                    'unit': 'Count',
                    'up': {
                        'stat': 'Average',
                        'condition': "> 50",
                        'change': '50%',
                    },
                    'down': {
                        'stat': 'Average',
                        'condition': "> 35",
                        'change': "-50%",
                    },
                },
                'size': 'm1.large',
                'sshKey': 'bootstrap'
            }]
        }
        tmpl = out.add_resources(res, cfg)
        assert_equals(json.loads(tmpl), ret)

    @mock.patch('pmcf.provisioners.AWSFWProvisioner.userdata', _mock_ud)
    def test_instance_valid_nat(self):
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
                        "HealthCheckGracePeriod": 600, 
                        "HealthCheckType": "EC2", 
                        "LaunchConfigurationName": {
                            "Ref": "LCapp"
                        }, 
                        "MaxSize": 6, 
                        "MinSize": 6, 
                        "Tags": [
                            {
                                "Key": "Name", 
                                "PropagateAtLaunch": True, 
                                "Value": "test::app::test"
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
                "EIPDNSapp": {
                    "Properties": {
                        "Comment": "EIP for app in test", 
                        "HostedZoneName": "test.test.example.com", 
                        "Name": "app.test.test.example.com", 
                        "ResourceRecords": [
                            {
                                "Ref": "EIPapp0"
                            }, 
                            {
                                "Ref": "EIPapp1"
                            }, 
                            {
                                "Ref": "EIPapp2"
                            }, 
                            {
                                "Ref": "EIPapp3"
                            }, 
                            {
                                "Ref": "EIPapp4"
                            }, 
                            {
                                "Ref": "EIPapp5"
                            }
                        ], 
                        "TTL": "300", 
                        "Type": "A"
                    }, 
                    "Type": "AWS::Route53::RecordSet"
                }, 
                "EIPDNSapp01": {
                    "Properties": {
                        "Comment": "EIP for app in test", 
                        "HostedZoneName": "test.test.example.com", 
                        "Name": "app01.test.test.example.com", 
                        "ResourceRecords": [
                            {
                                "Ref": "EIPapp0"
                            }
                        ], 
                        "TTL": "300", 
                        "Type": "A"
                    }, 
                    "Type": "AWS::Route53::RecordSet"
                }, 
                "EIPDNSapp02": {
                    "Properties": {
                        "Comment": "EIP for app in test", 
                        "HostedZoneName": "test.test.example.com", 
                        "Name": "app02.test.test.example.com", 
                        "ResourceRecords": [
                            {
                                "Ref": "EIPapp1"
                            }
                        ], 
                        "TTL": "300", 
                        "Type": "A"
                    }, 
                    "Type": "AWS::Route53::RecordSet"
                }, 
                "EIPDNSapp03": {
                    "Properties": {
                        "Comment": "EIP for app in test", 
                        "HostedZoneName": "test.test.example.com", 
                        "Name": "app03.test.test.example.com", 
                        "ResourceRecords": [
                            {
                                "Ref": "EIPapp2"
                            }
                        ], 
                        "TTL": "300", 
                        "Type": "A"
                    }, 
                    "Type": "AWS::Route53::RecordSet"
                }, 
                "EIPDNSapp04": {
                    "Properties": {
                        "Comment": "EIP for app in test", 
                        "HostedZoneName": "test.test.example.com", 
                        "Name": "app04.test.test.example.com", 
                        "ResourceRecords": [
                            {
                                "Ref": "EIPapp3"
                            }
                        ], 
                        "TTL": "300", 
                        "Type": "A"
                    }, 
                    "Type": "AWS::Route53::RecordSet"
                }, 
                "EIPDNSapp05": {
                    "Properties": {
                        "Comment": "EIP for app in test", 
                        "HostedZoneName": "test.test.example.com", 
                        "Name": "app05.test.test.example.com", 
                        "ResourceRecords": [
                            {
                                "Ref": "EIPapp4"
                            }
                        ], 
                        "TTL": "300", 
                        "Type": "A"
                    }, 
                    "Type": "AWS::Route53::RecordSet"
                }, 
                "EIPDNSapp06": {
                    "Properties": {
                        "Comment": "EIP for app in test", 
                        "HostedZoneName": "test.test.example.com", 
                        "Name": "app06.test.test.example.com", 
                        "ResourceRecords": [
                            {
                                "Ref": "EIPapp5"
                            }
                        ], 
                        "TTL": "300", 
                        "Type": "A"
                    }, 
                    "Type": "AWS::Route53::RecordSet"
                }, 
                "EIPapp0": {
                    "Properties": {
                        "Domain": "vpc"
                    }, 
                    "Type": "AWS::EC2::EIP"
                }, 
                "EIPapp1": {
                    "Properties": {
                        "Domain": "vpc"
                    }, 
                    "Type": "AWS::EC2::EIP"
                }, 
                "EIPapp2": {
                    "Properties": {
                        "Domain": "vpc"
                    }, 
                    "Type": "AWS::EC2::EIP"
                }, 
                "EIPapp3": {
                    "Properties": {
                        "Domain": "vpc"
                    }, 
                    "Type": "AWS::EC2::EIP"
                }, 
                "EIPapp4": {
                    "Properties": {
                        "Domain": "vpc"
                    }, 
                    "Type": "AWS::EC2::EIP"
                }, 
                "EIPapp5": {
                    "Properties": {
                        "Domain": "vpc"
                    }, 
                    "Type": "AWS::EC2::EIP"
                }, 
                "LCapp": {
                    "Properties": {
                        "BlockDeviceMappings": [
                            {
                                "DeviceName": "/dev/xvdb", 
                                "VirtualName": "ephemeral0"
                            }, 
                            {
                                "DeviceName": "/dev/xvdc", 
                                "VirtualName": "ephemeral1"
                            }
                        ], 
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
                'nat': True,
                'dnszone': 'test.example.com',
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
                'public': False,
                'sg': [],
                'size': 'm1.large',
                'sshKey': 'bootstrap'
            }]
        }
        tmpl = out.add_resources(res, cfg)
        assert_equals(json.loads(tmpl), ret)

    def test_instance_valid_wait_no_count(self):
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
                        "DesiredCapacity": 0, 
                        "HealthCheckGracePeriod": 600, 
                        "HealthCheckType": "EC2", 
                        "LaunchConfigurationName": {
                            "Ref": "LCapp"
                        }, 
                        "MaxSize": 0, 
                        "MinSize": 0, 
                        "Tags": [
                            {
                                "Key": "Name", 
                                "PropagateAtLaunch": True, 
                                "Value": "test::app::test"
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
                "Handleapp": {
                    "Type": "AWS::CloudFormation::WaitConditionHandle"
                }, 
                "LCapp": {
                    "Properties": {
                        "BlockDeviceMappings": [
                            {
                                "DeviceName": "/dev/xvdb", 
                                "VirtualName": "ephemeral0"
                            }, 
                            {
                                "DeviceName": "/dev/xvdc", 
                                "VirtualName": "ephemeral1"
                            }
                        ], 
                        "ImageId": "ami-e97f849e", 
                        "InstanceMonitoring": "false", 
                        "InstanceType": "m1.large", 
                        "KeyName": "bootstrap", 
                        "SecurityGroups": [], 
                        "UserData": {
                            "Fn::Base64": {
                                "Fn::Join": [
                                    "", 
                                    [
                                        "#!/bin/bash\n", 
                                        "apt-get -y install python-setuptools\n", 
                                        "easy_install https://s3.amazonaws.com/cloudformation-examples/", 
                                        "aws-cfn-bootstrap-latest.tar.gz\n", 
                                        "cfn-signal -e 0 -r Success '", 
                                        {
                                            "Ref": "Handleapp"
                                        }, 
                                        "'\n"
                                    ]
                                ]
                            }
                        }
                    }, 
                    "Type": "AWS::AutoScaling::LaunchConfiguration"
                }, 
                "Waitapp": {
                    "DependsOn": "ASGapp", 
                    "Properties": {
                        "Count": 0, 
                        "Handle": {
                            "Ref": "Handleapp"
                        }, 
                        "Timeout": 3600
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
                'count': 0,
                'image': 'ami-e97f849e',
                'monitoring': False,
                'name': 'app',
                'provisioner': {
                    'args': {},
                    'provider': 'BlockingProvisioner'
                },
                'public': False,
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
                        "HealthCheckType": "EC2",
                        "HealthCheckGracePeriod": 600,
                        "LaunchConfigurationName": {
                            "Ref": "LCapp"
                        },
                        "MaxSize": 6,
                        "MinSize": 6,
                        "Tags": [
                            {
                                "Key": "Name",
                                "PropagateAtLaunch": True,
                                "Value": "test::app::test"
                            },
                            {
                                "Key": "App",
                                "PropagateAtLaunch": True,
                                "Value": "app"
                            }
                        ],
                    },
                    "Type": "AWS::AutoScaling::AutoScalingGroup"
                },
                "LCapp": {
                    "Properties": {
                        "BlockDeviceMappings": [
                            {
                                "DeviceName": "/dev/xvdb",
                                "VirtualName": "ephemeral0"
                            },
                            {
                                "DeviceName": "/dev/xvdc",
                                "VirtualName": "ephemeral1"
                            }
                        ],
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
                'public': False,
                'sg': [],
                'size': 'm1.large',
                'sshKey': 'bootstrap'
            }]
        }
        tmpl = out.add_resources(res, cfg)
        assert_equals(json.loads(tmpl), ret)

    def test_stream_valid(self):
        out = JSONOutput()
        ret = {
            "AWSTemplateFormatVersion": "2010-09-09",
            "Description": "test test stack",
            "Resources": {
                "Streamtest": {
                    "Properties": {
                        "ShardCount": 2,
                    },
                    "Type": "AWS::Kinesis::Stream"
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
            'instance': [],
            'stream': [{
                'name': 'test',
                'shards': 2,
            }]
        }
        tmpl = out.add_resources(res, cfg)
        assert_equals(json.loads(tmpl), ret)

    def test_run(self):
        sys.stdout = open('/dev/null', 'w')
        assert_equals(True, JSONOutput().run('{}', {}))
