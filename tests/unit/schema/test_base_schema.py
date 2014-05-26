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
            'additionalProperties': False,
            'definitions': {
                'instance': {
                    'additionalProperties': False,
                    'required': [
                        'count',
                        'image',
                        'monitoring',
                        'name',
                        'provisioner',
                        'sg',
                        'sshKey',
                        'size'
                    ],
                    'properties': {
                        'count': {
                            'minimum': 1,
                            'type': 'integer'
                        },
                        'monitoring': {
                            'type': 'boolean'
                        },
                        'name': {
                            'type': 'string'
                        },
                        'min': {
                            'minimum': 1,
                            'type': 'integer'
                        },
                        'block_device': {
                            'type': 'array'
                        },
                        'max': {
                            'minimum': 1,
                            'type': 'integer'
                        },
                        'image': {
                            'type': 'string'
                        },
                        'sshKey': {
                            'type': 'string'
                        },
                        'provisioner': {
                            'type': 'object',
                            'properties': {
                                'args': {
                                    'type': 'object'
                                },
                                'provider': {
                                    'type': 'string'
                                }
                            }
                        },
                        'lb': {
                            'type': 'string'
                        },
                        'sg': {
                            'type': 'array'
                        },
                        'size': {
                            'type': 'string'
                        }
                    }
                }
            },
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'required': [
                'config',
                'resources'
            ],
            'type': 'object',
            'properties': {
                'config': {
                    'type': 'object'
                },
                'resources': {
                    'type': 'object',
                    'properties': {
                        'load_balancer': {
                            'type': 'array'
                        },
                        'instance': {
                            'minItems': 1,
                            'items': {
                                '$ref': '#/definitions/instance'
                            },
                            'type': 'array'
                        },
                        'cdn': {
                            'type': 'array'
                        },
                        'db': {
                            'type': 'array'
                        },
                        'sec_group': {
                            'type': 'array'
                        }
                    }
                },
                'tags': {
                    'type': 'object'
                }
            }
        }
        data = yaml.load(schema)
        assert_equals(data, schema_data)
