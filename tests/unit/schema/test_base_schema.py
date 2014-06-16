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
from jsonschema.exceptions import ValidationError
from nose.tools import assert_equals, assert_raises
import yaml

from pmcf.schema.base import schema as base_schema


class TestBaseSchema(object):

    def __init__(self):
        self.data = {
            'config': {},
            'resources': {
                'secgroup': [],
                'load_balancer': [],
                'db': [],
                'cdn': [],
                'instance': [
                    {
                        'count': 3,
                        'image': 'ami-0bceb93b',
                        'lb': 'app',
                        'monitoring': False,
                        'name': 'app',
                        'provisioner': {'provider': 'PuppetProvisioner'},
                        'sg': ['app'],
                        'size': 'm1.large',
                        'sshKey': 'bootstrap'
                    }
                ]
            }
        }

    def _add_sg_data(self):
        self.data['resources']['secgroup'].append({
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
        })

    def _add_lb_data(self):
        self.data['resources']['load_balancer'].append({
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
        })

    def test_schema_loads(self):
        yaml.load(base_schema)
        # We're only testing for valid YAML
        assert_equals(True, True)

    def test_schema_invalid_no_config(self):
        schema = yaml.load(base_schema)
        self.data.pop('config')
        assert_raises(ValidationError, jsonschema.validate, self.data, schema)

    def test_schema_invalid_extra_property(self):
        schema = yaml.load(base_schema)
        self.data['wobble'] = True
        assert_raises(ValidationError, jsonschema.validate, self.data, schema)

    def test_schema_invalid_no_resources(self):
        schema = yaml.load(base_schema)
        self.data.pop('resources')
        assert_raises(ValidationError, jsonschema.validate, self.data, schema)

    def test_schema_one_instance_valid(self):
        schema = yaml.load(base_schema)
        assert_equals(None, jsonschema.validate(self.data, schema))

    def test_schema_invalid_instance_extra_property(self):
        schema = yaml.load(base_schema)
        self.data['resources']['instance'][0]['wobble'] = True
        assert_raises(ValidationError, jsonschema.validate, self.data, schema)

    def test_schema_no_instance_invalid(self):
        schema = yaml.load(base_schema)
        self.data['resources']['instance'].pop(0)
        assert_raises(ValidationError, jsonschema.validate, self.data, schema)

    def test_schema_one_instance_invalid_no_count(self):
        schema = yaml.load(base_schema)
        self.data['resources']['instance'][0].pop('count')
        assert_raises(ValidationError, jsonschema.validate, self.data, schema)

    def test_schema_one_instance_invalid_no_image(self):
        schema = yaml.load(base_schema)
        self.data['resources']['instance'][0].pop('image')
        assert_raises(ValidationError, jsonschema.validate, self.data, schema)

    def test_schema_one_instance_invalid_no_monitoring(self):
        schema = yaml.load(base_schema)
        self.data['resources']['instance'][0].pop('monitoring')
        assert_raises(ValidationError, jsonschema.validate, self.data, schema)

    def test_schema_one_instance_invalid_no_name(self):
        schema = yaml.load(base_schema)
        self.data['resources']['instance'][0].pop('name')
        assert_raises(ValidationError, jsonschema.validate, self.data, schema)

    def test_schema_one_instance_invalid_no_provisioner(self):
        schema = yaml.load(base_schema)
        self.data['resources']['instance'][0].pop('provisioner')
        assert_raises(ValidationError, jsonschema.validate, self.data, schema)

    def test_schema_one_instance_invalid_no_sg(self):
        schema = yaml.load(base_schema)
        self.data['resources']['instance'][0].pop('sg')
        assert_raises(ValidationError, jsonschema.validate, self.data, schema)

    def test_schema_one_instance_invalid_no_size(self):
        schema = yaml.load(base_schema)
        self.data['resources']['instance'][0].pop('size')
        assert_raises(ValidationError, jsonschema.validate, self.data, schema)

    def test_schema_one_instance_invalid_no_sshKey(self):
        schema = yaml.load(base_schema)
        self.data['resources']['instance'][0].pop('sshKey')
        assert_raises(ValidationError, jsonschema.validate, self.data, schema)

    def test_schema_loadbalancer_valid(self):
        schema = yaml.load(base_schema)
        self._add_lb_data()
        assert_equals(None, jsonschema.validate(self.data, schema))

    def test_schema_invalid_loadbalancer_extra_property(self):
        schema = yaml.load(base_schema)
        self._add_lb_data()
        self.data['resources']['load_balancer'][0]['wobble'] = True
        assert_raises(ValidationError, jsonschema.validate, self.data, schema)

    def test_schema_invalid_listener_extra_property(self):
        schema = yaml.load(base_schema)
        self._add_lb_data()
        self.data['resources']['load_balancer'][0]['listener'][0]['wobble'] =\
            True
        assert_raises(ValidationError, jsonschema.validate, self.data, schema)

    def test_schema_invalid_healthcheck_extra_property(self):
        schema = yaml.load(base_schema)
        self._add_lb_data()
        self.data['resources']['load_balancer'][0]['healthcheck']['wobble'] =\
            True
        assert_raises(ValidationError, jsonschema.validate, self.data, schema)

    def test_schema_loadbalancer_invalid_listener_no_instance_port(self):
        schema = yaml.load(base_schema)
        self._add_lb_data()
        self.data['resources']['load_balancer'][0]['listener'][0].pop(
            'instance_port')
        assert_raises(ValidationError, jsonschema.validate, self.data, schema)

    def test_schema_loadbalancer_invalid_listener_no_protocol(self):
        schema = yaml.load(base_schema)
        self._add_lb_data()
        self.data['resources']['load_balancer'][0]['listener'][0].pop(
            'protocol')
        assert_raises(ValidationError, jsonschema.validate, self.data, schema)

    def test_schema_loadbalancer_invalid_listener_no_instance_protocol(self):
        schema = yaml.load(base_schema)
        self._add_lb_data()
        self.data['resources']['load_balancer'][0]['listener'][0].pop(
            'instance_protocol')
        assert_raises(ValidationError, jsonschema.validate, self.data, schema)

    def test_schema_loadbalancer_invalid_listener_no_lb_port(self):
        schema = yaml.load(base_schema)
        self._add_lb_data()
        self.data['resources']['load_balancer'][0]['listener'][0].pop(
            'lb_port')
        assert_raises(ValidationError, jsonschema.validate, self.data, schema)

    def test_schema_loadbalancer_invalid_healthcheck_no_protocol(self):
        schema = yaml.load(base_schema)
        self._add_lb_data()
        self.data['resources']['load_balancer'][0]['healthcheck'].pop(
            'protocol')
        assert_raises(ValidationError, jsonschema.validate, self.data, schema)

    def test_schema_loadbalancer_invalid_healthcheck_no_port(self):
        schema = yaml.load(base_schema)
        self._add_lb_data()
        self.data['resources']['load_balancer'][0]['healthcheck'].pop('port')
        assert_raises(ValidationError, jsonschema.validate, self.data, schema)

    def test_schema_loadbalancer_invalid_no_name(self):
        schema = yaml.load(base_schema)
        self._add_lb_data()
        self.data['resources']['load_balancer'][0].pop('name')
        assert_raises(ValidationError, jsonschema.validate, self.data, schema)

    def test_schema_loadbalancer_invalid_no_healthcheck(self):
        schema = yaml.load(base_schema)
        self._add_lb_data()
        self.data['resources']['load_balancer'][0].pop('healthcheck')
        assert_raises(ValidationError, jsonschema.validate, self.data, schema)

    def test_schema_loadbalancer_invalid_no_listener(self):
        schema = yaml.load(base_schema)
        self._add_lb_data()
        self.data['resources']['load_balancer'][0].pop('listener')
        assert_raises(ValidationError, jsonschema.validate, self.data, schema)

    def test_schema_secgroup_valid(self):
        schema = yaml.load(base_schema)
        self._add_sg_data()
        assert_equals(None, jsonschema.validate(self.data, schema))

    def test_schema_secgroup_valid_empty_rules(self):
        schema = yaml.load(base_schema)
        self._add_sg_data()
        self.data['resources']['secgroup'][0]['rules'].pop(0)
        self.data['resources']['secgroup'][0]['rules'].pop(0)
        assert_equals(None, jsonschema.validate(self.data, schema))

    def test_schema_secgroup_invalid_no_name(self):
        schema = yaml.load(base_schema)
        self._add_sg_data()
        self.data['resources']['secgroup'][0].pop('name')
        assert_raises(ValidationError, jsonschema.validate, self.data, schema)

    def test_schema_secgroup_invalid_no_rules(self):
        schema = yaml.load(base_schema)
        self._add_sg_data()
        self.data['resources']['secgroup'][0].pop('rules')
        assert_raises(ValidationError, jsonschema.validate, self.data, schema)

    def test_schema_secgroup_invalid_rule_no_from_port(self):
        schema = yaml.load(base_schema)
        self._add_sg_data()
        self.data['resources']['secgroup'][0]['rules'][0].pop('from_port')
        assert_raises(ValidationError, jsonschema.validate, self.data, schema)

    def test_schema_secgroup_invalid_rule_no_to_port(self):
        schema = yaml.load(base_schema)
        self._add_sg_data()
        self.data['resources']['secgroup'][0]['rules'][0].pop('to_port')
        assert_raises(ValidationError, jsonschema.validate, self.data, schema)

    def test_schema_secgroup_invalid_rule_no_protocol(self):
        schema = yaml.load(base_schema)
        self._add_sg_data()
        self.data['resources']['secgroup'][0]['rules'][0].pop('protocol')
        assert_raises(ValidationError, jsonschema.validate, self.data, schema)

    def test_schema_invalid_secgroup_extra_property(self):
        schema = yaml.load(base_schema)
        self._add_sg_data()
        self.data['resources']['secgroup'][0]['wobble'] = True
        assert_raises(ValidationError, jsonschema.validate, self.data, schema)

    def test_schema_invalid_secgroup_cidr_rule_extra_property(self):
        schema = yaml.load(base_schema)
        self._add_sg_data()
        self.data['resources']['secgroup'][0]['rules'][0]['wobble'] = True
        assert_raises(ValidationError, jsonschema.validate, self.data, schema)

    def test_schema_invalid_secgroup_group_rule_extra_property(self):
        schema = yaml.load(base_schema)
        self._add_sg_data()
        self.data['resources']['secgroup'][0]['rules'][1]['wobble'] = True
        assert_raises(ValidationError, jsonschema.validate, self.data, schema)
