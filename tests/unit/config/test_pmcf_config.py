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

from pmcf.config.config import PMCFConfig


class TestPMCFConfig(object):
    def test_create_succeeds(self):
        cfg = PMCFConfig('/etc/testfile', 'testprofile', {})
        opts = {
            'debug': None,
            'instance_accesskey': None,
            'instance_secretkey': None,
            'audit': 'NoopAudit',
            'audit_output': None,
            'output': 'BaseOutput',
            'parser': 'BaseParser',
            'policy': 'BasePolicy',
            'policyfile': None,
            'provisioner': 'BaseProvisioner',
            'quiet': None,
            'region': None,
            'secretkey': None,
            'stackfile': None,
            'stage': None,
            'verbose': None,
            'accesskey': None,
        }
        assert_equals(cfg.options, opts)

    def test_get_config_missing_profile_fails(self):
        cfg = PMCFConfig('tests/data/etc/pmcf.conf', 'missing', {})
        assert_raises(ValueError, cfg.get_config)

    def test_get_config_succeeds(self):
        cfg = PMCFConfig('tests/data/etc/pmcf.conf', 'default', {})

        opts = {
            'debug': None,
            'instance_accesskey': None,
            'instance_secretkey': None,
            'output': 'AWSCFNOutput',
            'parser': 'AWSFWParser',
            'policy': 'JSONPolicy',
            'audit': 'NoopAudit',
            'audit_output': None,
            'policyfile': None,
            'provisioner': 'AWSFWProvisioner',
            'quiet': None,
            'region': None,
            'secretkey': None,
            'stackfile': None,
            'stage': None,
            'verbose': None,
            'accesskey': None,
        }
        assert_equals(cfg.get_config(), opts)

    def test_get_from_section_succeeds(self):
        cfg = PMCFConfig('tests/data/etc/pmcf.conf', 'default', {})
        cfg.get_config()
        item = cfg._get_from_section('default', 'output')
        assert_equals(item, 'AWSCFNOutput')

    def test_get_missing_from_section_returns_none(self):
        cfg = PMCFConfig('tests/data/etc/pmcf.conf', 'default', {})
        cfg.get_config()
        item = cfg._get_from_section('default', 'wibble')
        assert_equals(item, None)
