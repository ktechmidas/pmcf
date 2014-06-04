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

import boto
import mock
from nose.tools import assert_equals, assert_raises
import sys

from pmcf.exceptions import AuditException, ProvisionerException
from pmcf.outputs import AWSCFNOutput


def _mock_search_regions(svc):
    class FakeRegion(object):
        def __init__(self):
            self.name = 'eu-west-1'
            self.endpoint = 'http://localhost/'
    return [FakeRegion()]


def _mock_create_stack(obj, name, data, tags):
    pass


def _mock_create_stack_fails(obj, name, data, tags):
    raise boto.exception.BotoServerError('I fail', 'nope')


def _mock_describe_stack(obj, name):
    return {}


def _mock_describe_stack_fails(obj, name):
    raise boto.exception.BotoServerError('nope', 'nope')


def _mock_get_template(obj, name):
    return {
        'GetTemplateResponse': {
            'GetTemplateResult': {
                'TemplateBody': '{"a": "b"}'
            }
        }
    }


def _mock_make_diff(old, new):
    return ''


def _mock_make_diff_differs(old, new):
    return 'aargg'


def _mock_return_no(self, prompt):
    return 'No'


def _mock_return_yes(self, prompt):
    return 'Yes'


def _mock_return_true(self, cfn, name, data):
    return True


def _mock_return_false(self, cfn, name, data):
    return False


def _mock_audit_fails(self, stack, dest, credentials):
    raise AuditException('I fail')


class TestAWSCFNOutput(object):

    def test_run_no_region_raises(self):
        cfno = AWSCFNOutput()
        assert_raises(ProvisionerException, cfno.run, '{"a": "b"}', {})

    def test_run_bad_region_raises(self):
        cfno = AWSCFNOutput()
        assert_raises(ProvisionerException, cfno.run,
                      '{"a": "b"}', {'region': 'nah'})

    @mock.patch('boto.regioninfo.get_regions', _mock_search_regions)
    @mock.patch('boto.cloudformation.CloudFormationConnection.create_stack',
                _mock_create_stack)
    def test_run_connects(self):
        cfno = AWSCFNOutput()
        metadata = {
            'region': 'eu-west-1',
            'access': '1234',
            'secret': '2345',
            'name': 'test',
            'stage': 'test',
            'audit': 'NoopAudit',
        }
        assert_equals(cfno.run('{"a": "b"}', metadata), True)

    @mock.patch('boto.regioninfo.get_regions', _mock_search_regions)
    @mock.patch('boto.cloudformation.CloudFormationConnection.create_stack',
                _mock_create_stack)
    @mock.patch('pmcf.audit.S3Audit.record_stack', _mock_audit_fails)
    def test_run_audit_failure_connects(self):
        cfno = AWSCFNOutput()
        metadata = {
            'region': 'eu-west-1',
            'access': '1234',
            'secret': '2345',
            'name': 'test',
            'stage': 'test',
            'audit': 'S3Audit',
        }
        assert_equals(cfno.run('{"a": "b"}', metadata), True)

    @mock.patch('boto.regioninfo.get_regions', _mock_search_regions)
    @mock.patch('boto.cloudformation.CloudFormationConnection.create_stack',
                _mock_create_stack)
    def test_run_with_tags_connects(self):
        cfno = AWSCFNOutput()
        metadata = {
            'region': 'eu-west-1',
            'access': '1234',
            'secret': '2345',
            'name': 'test',
            'stage': 'test',
            'audit': 'NoopAudit',
            'tags': {
                'Name': 'test'
            }
        }
        assert_equals(cfno.run('{"a": "b"}', metadata), True)

    @mock.patch('boto.regioninfo.get_regions', _mock_search_regions)
    @mock.patch('boto.cloudformation.CloudFormationConnection.create_stack',
                _mock_create_stack)
    @mock.patch('boto.cloudformation.CloudFormationConnection.update_stack',
                _mock_create_stack)
    @mock.patch('boto.cloudformation.CloudFormationConnection.describe_stacks',
                _mock_describe_stack)
    @mock.patch('pmcf.outputs.cloudformation.AWSCFNOutput._show_prompt',
                _mock_return_true)
    def test_run_with_prompt_true_succeeds(self):
        cfno = AWSCFNOutput()
        metadata = {
            'region': 'eu-west-1',
            'access': '1234',
            'secret': '2345',
            'name': 'test',
            'stage': 'test',
            'strategy': 'prompt_inplace',
            'audit': 'NoopAudit',
            'tags': {
                'Name': 'test'
            }
        }
        assert_equals(cfno.run('{"a": "b"}', metadata), True)

    @mock.patch('boto.regioninfo.get_regions', _mock_search_regions)
    @mock.patch('boto.cloudformation.CloudFormationConnection.create_stack',
                _mock_create_stack)
    @mock.patch('boto.cloudformation.CloudFormationConnection.update_stack',
                _mock_create_stack)
    @mock.patch('boto.cloudformation.CloudFormationConnection.describe_stacks',
                _mock_describe_stack)
    @mock.patch('pmcf.outputs.cloudformation.AWSCFNOutput._show_prompt',
                _mock_return_false)
    def test_run_with_prompt_false_succeeds(self):
        cfno = AWSCFNOutput()
        metadata = {
            'region': 'eu-west-1',
            'access': '1234',
            'secret': '2345',
            'name': 'test',
            'stage': 'test',
            'strategy': 'prompt_inplace',
            'audit': 'NoopAudit',
            'tags': {
                'Name': 'test'
            }
        }
        assert_equals(cfno.run('{"a": "b"}', metadata), True)

    @mock.patch('boto.regioninfo.get_regions', _mock_search_regions)
    @mock.patch('boto.cloudformation.CloudFormationConnection.create_stack',
                _mock_create_stack_fails)
    def test_run_stack_fails(self):
        cfno = AWSCFNOutput()
        metadata = {
            'region': 'eu-west-1',
            'access': '1234',
            'secret': '2345',
            'audit': 'NoopAudit',
            'stage': 'test',
            'name': 'test'
        }
        assert_raises(ProvisionerException, cfno.run, '{"a": "b"}', metadata)

    @mock.patch('boto.cloudformation.CloudFormationConnection.describe_stacks',
                _mock_describe_stack)
    def test__stack_exists_exists(self):
        cfno = AWSCFNOutput()
        cfn = boto.connect_cloudformation(
            aws_access_key_id='access',
            aws_secret_access_key='secret'
        )
        assert_equals(True, cfno._stack_exists(cfn, 'test'))

    @mock.patch('boto.cloudformation.CloudFormationConnection.describe_stacks',
                _mock_describe_stack_fails)
    def test__stack_exists_nonexistant(self):
        cfno = AWSCFNOutput()
        cfn = boto.connect_cloudformation(
            aws_access_key_id='access',
            aws_secret_access_key='secret'
        )
        assert_equals(False, cfno._stack_exists(cfn, 'test'))

    @mock.patch('boto.cloudformation.CloudFormationConnection.get_template',
                _mock_get_template)
    @mock.patch('pmcf.utils.make_diff', _mock_make_diff)
    def test__show_prompt_no_difference(self):
        cfno = AWSCFNOutput()
        cfn = boto.connect_cloudformation(
            aws_access_key_id='access',
            aws_secret_access_key='secret'
        )
        assert_equals(False, cfno._show_prompt(cfn, 'test', '{"a": "b"}'))

    @mock.patch('boto.cloudformation.CloudFormationConnection.get_template',
                _mock_get_template)
    @mock.patch('pmcf.utils.make_diff', _mock_make_diff_differs)
    @mock.patch('pmcf.outputs.cloudformation.AWSCFNOutput._get_input',
                _mock_return_no)
    def test__show_prompt_difference_no(self):
        cfno = AWSCFNOutput()
        cfn = boto.connect_cloudformation(
            aws_access_key_id='access',
            aws_secret_access_key='secret'
        )
        sys.stdout = open('/dev/null', 'w')
        assert_equals(False, cfno._show_prompt(cfn, 'test', '{"a": "c"}'))

    @mock.patch('boto.cloudformation.CloudFormationConnection.get_template',
                _mock_get_template)
    @mock.patch('pmcf.utils.make_diff', _mock_make_diff_differs)
    @mock.patch('pmcf.outputs.cloudformation.AWSCFNOutput._get_input',
                _mock_return_yes)
    def test__show_prompt_difference_yes(self):
        cfno = AWSCFNOutput()
        cfn = boto.connect_cloudformation(
            aws_access_key_id='access',
            aws_secret_access_key='secret'
        )
        sys.stdout = open('/dev/null', 'w')
        assert_equals(True, cfno._show_prompt(cfn, 'test', '{"a": "c"}'))
