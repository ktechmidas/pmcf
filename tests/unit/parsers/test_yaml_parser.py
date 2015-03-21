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

from pmcf.parsers import yaml_parser
from pmcf.exceptions import ParserFailure


def _mock_validate_raises(data, schema):
    raise jsonschema.exceptions.ValidationError('error')


class TestParser(object):

    def test__get_value_for_env_int_returns_int(self):
        parser = yaml_parser.YamlParser()
        data = 10
        ret = parser._get_value_for_env(data, 'test', 'thingy')
        assert_equals(data, ret)

    def test__get_value_for_env_str_returns_str(self):
        parser = yaml_parser.YamlParser()
        data = 'hello'
        ret = parser._get_value_for_env(data, 'test', 'thingy')
        assert_equals(data, ret)

    def test__get_value_for_env_list_returns_list(self):
        parser = yaml_parser.YamlParser()
        data = [1, 'a', '2']
        ret = parser._get_value_for_env(data, 'test', 'thingy')
        assert_equals(data, ret)

    def test__get_value_for_env_returns_env_value(self):
        parser = yaml_parser.YamlParser()
        data = {'test': 'foo', 'default': 'bar'}
        ret = parser._get_value_for_env(data, 'test', 'thingy')
        assert_equals('foo', ret)

    def test__get_value_for_env_returns_default_value(self):
        parser = yaml_parser.YamlParser()
        data = {'test2': 'foo', 'default': 'bar'}
        ret = parser._get_value_for_env(data, 'test', 'thingy')
        assert_equals('bar', ret)

    def test__get_value_for_env_raises_no_match(self):
        parser = yaml_parser.YamlParser()
        data = {'test2': 'foo', 'test3': 'bar'}
        assert_raises(ParserFailure,
                      parser._get_value_for_env, data, 'test', 'thingy')

    def test_parse_invalid_args_raises(self):
        parser = yaml_parser.YamlParser()
        fname = 'tests/data/yaml/ais-test-farm.yaml'
        assert_raises(ParserFailure, parser.parse_file, fname, {})

    def test_parser_raises_invalid_environment(self):
        args = {
            'environment': 'nosuchstage',
            'accesskey': '1234',
            'secretkey': '2345',
            'instance_accesskey': '12345',
            'instance_secretkey': '23456',
            'action': 'create',
        }
        parser = yaml_parser.YamlParser()
        fname = 'tests/data/yaml/ais-test-farm.yaml'
        assert_raises(ParserFailure, parser.parse_file, fname, args)

    def test_parse_invalid_yaml_raises(self):
        config = """
            foo:
            - one
                bar:
                  - 1
                  - three
        """
        parser = yaml_parser.YamlParser()
        assert_raises(ParserFailure, parser.parse, config)

    @mock.patch('jsonschema.validate', _mock_validate_raises)
    def test_schema_validation_failure_raises(self):
        parser = yaml_parser.YamlParser()
        # Append empty instance
        parser._stack['resources']['instance'].append({})
        assert_raises(ParserFailure, parser.validate)

    def test_sg_other_env(self):
        ds = """
config:
  name: ais
  environments:
      - dev
resources:
  secgroup:
    - name: test
      stages: [test]
      rules:
        - port: 8000
          protocol: tcp
          source_cidr:
            - 54.76.250.234/32
            - 83.98.0.0/17
            - 93.57.15.30/32
            - 80.113.0.0/17
            - 83.97.8.0/20
"""
        args = {
            'environment': 'dev',
            'accesskey': '1234',
            'secretkey': '2345',
            'instance_accesskey': '12345',
            'instance_secretkey': '23456'
        }
        parser = yaml_parser.YamlParser()
        data = parser.parse(ds, args)
        assert_equals(len(data['resources']['secgroup']), 0)

    def test_sg_list(self):
        ds = """
config:
  name: ais
  environments:
      - dev
resources:
  secgroup:
    - name: test
      rules:
        - port: 8000
          protocol: tcp
          source_cidr:
            - 54.76.250.234/32
            - 83.98.0.0/17
            - 93.57.15.30/32
            - 80.113.0.0/17
            - 83.97.8.0/20
"""
        args = {
            'environment': 'dev',
            'accesskey': '1234',
            'secretkey': '2345',
            'instance_accesskey': '12345',
            'instance_secretkey': '23456'
        }
        parser = yaml_parser.YamlParser()
        data = parser.parse(ds, args)
        assert_equals(len(data['resources']['secgroup'][0]['rules']), 5)

    def test_elb_prefix_multiple_lbs(self):
        ds = """
config:
  name: ais
  environments:
      - dev
resources:
  load_balancer:
    - &PUBLICTEST
      name: testelb
      listener:
        - instance_port: 80
          instance_protocol: HTTP
          protocol: HTTP
          lb_port: 80
      policy:
        default:
          - type: log_policy
            policy:
              emit_interval: 5
              enabled: true
              s3bucket: piksel-logging
              s3prefix: ais/testelb
      healthcheck:
        protocol: HTTP
        path: /
        port: 80
    - <<: *PUBLICTEST
      name: internal.testelb
      internal: true
      listener:
        - instance_port: 2003
          instance_protocol: TCP
          protocol: TCP
          lb_port: 2003
      healthcheck:
        protocol: HTTP
        port: 8080
        path: /ping
"""
        args = {
            'environment': 'dev',
            'accesskey': '1234',
            'secretkey': '2345',
        }
        parser = yaml_parser.YamlParser()
        data = parser.parse(ds, args)
        lba = data['resources']['load_balancer'][0]
        lbb = data['resources']['load_balancer'][1]
        prfxa = lba['policy'][0]['policy']['s3prefix']
        prfxb = lbb['policy'][0]['policy']['s3prefix']
        assert_equals(prfxa, 'dev/ais/testelb/external')
        assert_equals(prfxb, 'dev/ais/testelb/internal')

    def test_instance_defaultsg(self):
        args = {
            'environment': 'stage',
            'accesskey': '1234',
            'secretkey': '2345',
            'instance_accesskey': '12345',
            'instance_secretkey': '23456'
        }
        parser = yaml_parser.YamlParser()
        fname = 'tests/data/yaml/ais-test-farm-defaultsg.yaml'
        data = parser.parse_file(fname, args)
        sgs = ['app', 'sg-123']
        assert_equals(data['resources']['instance'][0]['sg'], sgs)

    def test_instance_present_dev(self):
        args = {
            'environment': 'dev',
            'accesskey': '1234',
            'secretkey': '2345',
            'instance_accesskey': '12345',
            'instance_secretkey': '23456'
        }
        parser = yaml_parser.YamlParser()
        fname = 'tests/data/yaml/ais-test-farm-stage.yaml'
        data = parser.parse_file(fname, args)
        assert_equals(len(data['resources']['instance']), 2)

    def test_instance_missing_prod(self):
        args = {
            'environment': 'prod',
            'accesskey': '1234',
            'secretkey': '2345',
            'instance_accesskey': '12345',
            'instance_secretkey': '23456'
        }
        parser = yaml_parser.YamlParser()
        fname = 'tests/data/yaml/ais-test-farm-stage.yaml'
        data = parser.parse_file(fname, args)
        assert_equals(len(data['resources']['instance']), 1)

    def test_parser_instance_scaling_policy_invalid_raises(self):
        data = """
config:
  name: ais
  environments:
      - dev
resources:
  instance:
    - name: app
      count: 3
      image: ami-0bceb93b
      sshKey: bootstrap
      nat: True
      provisioner:
        provider: NoopProvisioner
        args: {}
      monitoring: False
      sg: []
      scaling_policy:
        default:
          metric: "Piksel/sequoiaidentity/nodejs_concurrents"
          unit: Count
          up:
            stat: Average
            condition: "> 50"
            change: 50%
          down:
            stat: Average
            condition: "> 35"
            change: "-1"
      size: m1.large
"""
        args = {
            'environment': 'dev',
            'accesskey': '1234',
            'secretkey': '2345',
            'instance_accesskey': '12345',
            'instance_secretkey': '23456'
        }
        parser = yaml_parser.YamlParser()
        assert_raises(ParserFailure, parser.parse, data, args)

    def test_parser_instance_scaling_policy_valid_other_env(self):
        data = """
config:
  name: ais
  environments:
      - dev
resources:
  instance:
    - name: app
      count: 3
      image: ami-0bceb93b
      sshKey: bootstrap
      provisioner:
        provider: NoopProvisioner
        args: {}
      monitoring: False
      scaling_policy:
        dev: []
        default:
          metric: "Piksel/sequoiaidentity/nodejs_concurrents"
          unit: Count
          up:
            stat: Average
            condition: "> 50"
            change: 50%
          down:
            stat: Average
            condition: "> 35"
            change: "-1"
      sg: []
      size: m1.large
"""
        args = {
            'environment': 'dev',
            'accesskey': '1234',
            'secretkey': '2345',
            'instance_accesskey': '12345',
            'instance_secretkey': '23456'
        }
        parser = yaml_parser.YamlParser()
        p_data = parser.parse(data, args)
        assert_equals(p_data['resources']['instance'][0].get(
                      'scaling_policy', None), None)

    def test_parser_instance_scaling_policy_valid(self):
        data = """
config:
  name: ais
  environments:
      - dev
resources:
  instance:
    - name: app
      count: 3
      image: ami-0bceb93b
      sshKey: bootstrap
      provisioner:
        provider: NoopProvisioner
        args: {}
      monitoring: False
      scaling_policy:
        default:
          metric: "Piksel/sequoiaidentity/nodejs_concurrents"
          unit: Count
          up:
            stat: Average
            condition: "> 50"
            change: 50%
          down:
            stat: Average
            condition: "> 35"
            change: "-1"
      sg: []
      size: m1.large
"""
        args = {
            'environment': 'dev',
            'accesskey': '1234',
            'secretkey': '2345',
            'instance_accesskey': '12345',
            'instance_secretkey': '23456'
        }
        parser = yaml_parser.YamlParser()
        p_data = parser.parse(data, args)
        assert_equals(type(p_data['resources']['instance'][0].get(
                      'scaling_policy', None)), dict)

    def test_parser_instance_dns_invalid_raises(self):
        data = """
config:
  name: ais
  environments:
      - dev
resources:
  instance:
    - name: app
      count: 3
      dns:
        type: per-instance-public
        zone: aws.sequoia.piksel.com
      image: ami-0bceb93b
      sshKey: bootstrap
      provisioner:
        provider: NoopProvisioner
        args: {}
      monitoring: False
      size: m1.large
"""
        args = {
            'environment': 'dev',
            'accesskey': '1234',
            'secretkey': '2345',
            'instance_accesskey': '12345',
            'instance_secretkey': '23456'
        }
        parser = yaml_parser.YamlParser()
        assert_raises(ParserFailure, parser.parse, data, args)

    def test_parser_instance_dns_valid(self):
        data = """
config:
  name: ais
  environments:
      - dev
resources:
  instance:
    - name: app
      count: 3
      dns:
        type: per-instance-public
        zone: aws.sequoia.piksel.com.
      image: ami-0bceb93b
      sshKey: bootstrap
      provisioner:
        provider: NoopProvisioner
        args: {}
      monitoring: False
      size: m1.large
"""
        args = {
            'environment': 'dev',
            'accesskey': '1234',
            'secretkey': '2345',
            'instance_accesskey': '12345',
            'instance_secretkey': '23456'
        }
        parser = yaml_parser.YamlParser()
        data = parser.parse(data, args)
        assert_equals(len(data['resources']['instance']), 1)

    def test_parser_public_net_valid(self):
        data = """
config:
  name: ais
  environments:
      - dev
resources:
  network:
    - name: test
      zones: [eu-west-1a, eu-west-1b, eu-west-1c]
      netrange: 10.0.0.0/8
"""
        args = {
            'environment': 'dev',
            'accesskey': '1234',
            'secretkey': '2345',
            'instance_accesskey': '12345',
            'instance_secretkey': '23456'
        }
        parser = yaml_parser.YamlParser()
        data = parser.parse(data, args)

        assert_equals(len(data['resources']['network'][0]['subnets']), 3)
        assert_equals(
            data['resources']['network'][0]['subnets'][0]['public'], True)
        assert_equals(
            data['resources']['network'][0]['subnets'][1]['public'], True)
        assert_equals(
            data['resources']['network'][0]['subnets'][2]['public'], True)

    def test_parser_private_net_valid(self):
        data = """
config:
  name: ais
  environments:
      - dev
resources:
  network:
    - name: test
      zones: [eu-west-1a, eu-west-1b, eu-west-1c]
      netrange: 10.0.0.0/8
      public: False
"""
        args = {
            'environment': 'dev',
            'accesskey': '1234',
            'secretkey': '2345',
            'instance_accesskey': '12345',
            'instance_secretkey': '23456'
        }
        parser = yaml_parser.YamlParser()
        data = parser.parse(data, args)

        assert_equals(len(data['resources']['network'][0]['subnets']), 3)
        assert_equals(
            data['resources']['network'][0]['subnets'][0]['public'], False)
        assert_equals(
            data['resources']['network'][0]['subnets'][1]['public'], False)
        assert_equals(
            data['resources']['network'][0]['subnets'][2]['public'], False)

    def test_parser_instance_auto_provisioner_valid(self):
        data = """
config:
  name: ais
  environments:
    - dev
  subnets:
    - 1243
  vpcid: 1123
  provisioner: PuppetProvisioner
  bucket: test-bucket
  audit_output: test-bucket
resources:
  instance:
    - name: app
      count: 3
      image: ami-0bceb93b
      sshKey: bootstrap
      monitoring: False
      size: m1.large
"""
        args = {
            'environment': 'dev',
            'accesskey': '1234',
            'secretkey': '2345',
            'instance_accesskey': '12345',
            'instance_secretkey': '23456'
        }
        parser = yaml_parser.YamlParser()
        data = parser.parse(data, args)
        assert_equals(
            data['resources']['instance'][0]['provisioner']['provider'],
            'PuppetProvisioner')

    def test_parser_instance_subnets_valid(self):
        data = """
config:
  name: ais
  environments:
    - dev
  subnets:
    - 1243
  vpcid: 1123
resources:
  instance:
    - name: app
      count: 3
      image: ami-0bceb93b
      sshKey: bootstrap
      provisioner:
        provider: NoopProvisioner
        args: {}
      monitoring: False
      size: m1.large
"""
        args = {
            'environment': 'dev',
            'accesskey': '1234',
            'secretkey': '2345',
            'instance_accesskey': '12345',
            'instance_secretkey': '23456'
        }
        parser = yaml_parser.YamlParser()
        data = parser.parse(data, args)
        assert_equals(len(data['resources']['instance']), 1)

    def test_parser_instance_subnets_invalid_no_vpcid(self):
        data = """
config:
  name: ais
  environments:
    - dev
  subnets:
    - 1243
resources:
  instance:
    - name: app
      count: 3
      image: ami-0bceb93b
      sshKey: bootstrap
      provisioner:
        provider: NoopProvisioner
        args: {}
      monitoring: False
      size: m1.large
"""
        args = {
            'environment': 'dev',
            'accesskey': '1234',
            'secretkey': '2345',
            'instance_accesskey': '12345',
            'instance_secretkey': '23456'
        }
        parser = yaml_parser.YamlParser()
        assert_raises(ParserFailure, parser.parse, data, args)


class TestParserData(object):

    def __init__(self):
        self.data = {}

    def setup(self):
        args = {
            'environment': 'stage',
            'accesskey': '1234',
            'secretkey': '2345',
            'instance_accesskey': '12345',
            'instance_secretkey': '23456',
            'audit_output': 'testbucket'
        }
        parser = yaml_parser.YamlParser()
        fname = 'tests/data/yaml/ais-test-farm.yaml'
        self.data = parser.parse_file(fname, args)

    def test_parser_has_valid_keys(self):
        assert_equals(set(['config', 'resources']), set(self.data.keys()))

    def test_parser_config_has_valid_keys(self):
        keys = [
            'audit_output',
            'name',
            'access',
            'secret',
            'environment',
            'instance_access',
            'instance_secret',
            'notify',
            'subnets',
            'provisioner',
            'profile',
            'vpcid',
        ]
        assert_equals(set(keys), set(self.data['config'].keys()))

    def test_parser_resource_has_valid_keys(self):
        keys = [
            'instance',
            'load_balancer',
            'secgroup',
            'network',
            'cdn',
            'db',
        ]
        assert_equals(set(keys), set(self.data['resources'].keys()))

    def test_parser_resource_first_instance_has_notify(self):
        assert_equals(
            True,
            'notify' in self.data['resources']['instance'][0].keys())

    def test_parser_resource_first_instance_has_custom_profile(self):
        inst = self.data['resources']['instance'][0]
        assert_equals(
            True,
            'custom_profile' in inst['provisioner']['args'].keys())

    def test_parser_resource_second_instance_has_notify(self):
        assert_equals(
            True,
            'notify' in self.data['resources']['instance'][1].keys())

    def test_parser_resource_has_valid_instance_count(self):
        assert_equals(2, len(self.data['resources']['instance']))

    def test_parser_resource_has_valid_lb_count(self):
        assert_equals(2, len(self.data['resources']['load_balancer']))

    def test_parser_resource_has_valid_secgroup_count(self):
        assert_equals(2, len(self.data['resources']['secgroup']))

    def test_parser_lb_has_valid_listener_count(self):
        assert_equals(2, len(
            self.data['resources']['load_balancer'][0]['listener']))

    def test_parser_lb_has_valid_policy_count(self):
        assert_equals(1, len(
            self.data['resources']['load_balancer'][0]['policy']))

    def test_parser_lb_has_valid_policy_prefix(self):
        elb = self.data['resources']['load_balancer'][0]
        p = elb['policy'][0]['policy']['s3prefix']
        assert_equals('stage/test/external', p)

    def test_parser_sg_has_valid_rule_count_app(self):
        assert_equals(12, len(self.data['resources']['secgroup'][1]['rules']))

    def test_parser_sg_has_valid_rule_count_app2(self):
        assert_equals(0, len(self.data['resources']['secgroup'][0]['rules']))

    def test_parser_network_has_correct_count(self):
        assert_equals(2, len(self.data['resources']['network']))

    def test_parser_network_has_correct_subnet_count(self):
        assert_equals(3, len(self.data['resources']['network'][0]['subnets']))
