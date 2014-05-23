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
            'type': 'object',
            'properties': {
                'config': {
                    'type': 'object'
                },
                'tags': {
                    'type': 'object',
                },
                'resources': {
                    'type': 'object',
                    'properties': {
                        'load_balancer': {
                            'type': 'array'
                        },
                        'instance': {
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
                }
            },
            'required': [
                'config',
                'resources',
            ],
            'additionalProperties': False,
        }
        data = yaml.load(schema)
        assert_equals(data, schema_data)
