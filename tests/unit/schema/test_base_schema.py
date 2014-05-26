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

from nose.tools import assert_equals
import yaml

from pmcf.schema.base import schema


class TestBaseSchema(object):

    def test_schema_loads(self):
        schema_data = {
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'additionalProperties': False,
            'definitions': {
                'block_storage': {
                    'additionalProperties': False,
                    'properties': {
                        'device': {
                            'type': 'string'
                        },
                        'size': {
                            'type': 'string'
                        }
                    },
                    'required': ['size', 'device']
                },
                'instance': {
                    'additionalProperties': False,
                    'properties': {
                        'block_device': {
                            'items': {
                                '$ref': '#/definitions/block_storage'
                            },
                            'type': 'array'
                        },
                        'count': {
                            'minimum': 1,
                            'type': 'integer'
                        },
                        'image': {
                            'type': 'string'
                        },
                        'lb': {
                            'type': 'string'
                        },
                        'max': {
                            'minimum': 1,
                            'type': 'integer'
                        },
                        'min': {
                            'minimum': 1,
                            'type': 'integer'
                        },
                        'monitoring': {
                            'type': 'boolean'
                        },
                        'name': {
                            'type': 'string'
                        },
                        'provisioner': {
                            'properties': {
                                'args': {
                                    'type': 'object'
                                },
                                'provider': {
                                    'enum': [
                                        'puppet',
                                        'chef',
                                        'awsfw_standalone'
                                    ]
                                }
                            },
                            'type': 'object'
                        },
                        'sg': {
                            'type': 'array'
                        },
                        'size': {
                            'type': 'string'
                        },
                        'sshKey': {
                            'type': 'string'
                        }
                    },
                    'required': [
                        'count',
                        'image',
                        'monitoring',
                        'name',
                        'provisioner',
                        'sg',
                        'sshKey',
                        'size'
                    ]
                },
                'listener': {
                    'additionalProperties': False,
                    'properties': {
                        'instance_port': {
                            'type': 'integer'
                        },
                        'instance_protocol': {
                            'enum': [
                                'HTTP',
                                'HTTPS',
                                'TCP'
                            ]
                        },
                        'lb_port': {
                            'type': 'integer'
                        },
                        'protocol': {
                            'enum': [
                                'HTTP',
                                'HTTPS',
                                'TCP'
                            ]
                        },
                        'sslCert': {
                            'type': 'string'
                        }
                    },
                    'required': [
                        'instance_port',
                        'protocol',
                        'instance_protocol',
                        'lb_port'
                    ]
                },
                'load_balancer': {
                    'additionalProperties': False,
                    'properties': {
                        'healthcheck': {
                            'properties': {
                                'port': {
                                    'type': 'integer'
                                },
                                'protocol': {
                                    'enum': [
                                        'HTTP',
                                        'HTTPS',
                                        'TCP'
                                    ]
                                }
                            },
                            'type': 'object'
                        },
                        'listener': {
                            'items': {
                                '$ref': '#/definitions/listener'
                            },
                            'minItems': 1,
                            'type': 'array'
                        },
                        'logging': {
                            'type': 'object'
                        },
                        'name': {
                            'type': 'string'
                        },
                        'policy': {
                            'type': 'array'
                        }
                    },
                    'required': [
                        'name',
                        'listener',
                        'healthcheck'
                    ]
                },
                'secgroup': {
                    'additionalProperties': False,
                    'properties': {
                        'name': {
                            'type': 'string'
                        },
                        'rules': {
                            'items': {
                                '$ref': '#/definitions/secgrouprule'
                            },
                            'minItems': 1,
                            'type': 'array'
                        }
                    },
                    'required': ['name', 'rules']
                },
                'secgrouprule': {
                    'additionalProperties': False,
                    'properties': {
                        'from_port': {
                            'type': 'integer'
                        },
                        'protocol': {
                            'type': 'string'
                        },
                        'oneOf': {
                            'source_cidr': {
                                'type': 'string'
                            },
                            'source_group': {
                                'type': 'string'
                            }
                        },
                        'to_port': {
                            'type': 'integer'
                        }
                    },
                    'required': [
                        'from_port',
                        'to_port',
                        'protocol'
                    ]
                }
            },
            'properties': {
                'config': {
                    'type': 'object'
                },
                'resources': {
                    'properties': {
                        'cdn': {
                            'type': 'array'
                        },
                        'db': {
                            'type': 'array'
                        },
                        'instance': {
                            'items': {
                                '$ref': '#/definitions/instance'
                            },
                            'minItems': 1,
                            'type': 'array'
                        },
                        'load_balancer': {
                            'items': {
                                '$ref': '#/definitions/load_balancer'
                            },
                            'type': 'array'
                        },
                        'sec_group': {
                            'items': {
                                '$ref': '#/definitions/secgroup'
                            },
                            'type': 'array'
                        }
                    },
                    'type': 'object'
                },
                'tags': {
                    'type': 'object'
                }
            },
            'required': ['config', 'resources'],
            'type': 'object'
        }
        data = yaml.load(schema)
        print data
        assert_equals(data, schema_data)
