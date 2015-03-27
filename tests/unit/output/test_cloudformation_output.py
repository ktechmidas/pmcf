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
import random
import re
import sys
import datetime

from pmcf.exceptions import AuditException, ProvisionerException
from pmcf.outputs import AWSCFNOutput


class Output(object):
    def __init__(self):
        self.description = 'a'
        self.value = 'a'


class Event(object):
    def __init__(self, same=False, in_past=False):
        if in_past:
            self.timestamp = datetime.datetime.utcnow() -\
                datetime.timedelta(random.random())
        else:
            self.timestamp = datetime.datetime.utcnow() +\
                datetime.timedelta(random.random())
        self.logical_resource_id = 'a'
        self.resource_type = 'a'
        self.resource_status = 'a'
        self.resource_status_reason = 'a'
        if same:
            self.event_id = 1
        else:
            self.event_id = random.randint(1, 100)


class Stack(object):
    def __init__(self, ret='CREATE_COMPLETE',
                 same_event=False, in_past=False):
        self.stack_status = ret
        self.same_event = same_event
        self.in_past = in_past
        self.outputs = [Output(), Output()]

    def describe_events(self):
        return [Event(self.same_event, self.in_past),
                Event(self.same_event, self.in_past)]


def _mock_search_regions(svc):
    class FakeRegion(object):
        def __init__(self):
            self.name = 'eu-west-1'
            self.endpoint = 'http://localhost/'
    return [FakeRegion()]


def _mock_validate_template_url(obj, template_url):
    pass


def _mock_create_stack_url(obj, name, template_url, capabilities, tags):
    pass


def _mock_validate_template(obj, data):
    pass


def _mock_create_stack(obj, name, data, capabilities, tags):
    pass


def _mock_delete_stack(obj, name):
    pass


def _mock_delete_stack_fails(obj, name):
    raise boto.exception.BotoServerError('I fail', 'nope')


def _mock_create_stack_fails(obj, name, data, capabilities, tags):
    raise boto.exception.BotoServerError('I fail', 'nope')


def _mock_describe_stack_raises_does_not_exist(obj, name):
    status = 404
    reason = 'nope'
    body = {'message': 'that does not exist'}
    raise boto.exception.BotoServerError(status, reason, body=body)


def _mock_describe_stack_raises_limit_exceeded(obj, name):
    status = 404
    reason = 'nope'
    body = {'message': 'Rate exceeded'}
    raise boto.exception.BotoServerError(status, reason, body=body)


def _mock_describe_stack(obj, name):
    return [Stack()]


def _mock_describe_stack_fails(obj, name):
    raise boto.exception.BotoServerError('nope', 'nope')


def _mock_get_changed_keys_from_templates(new, old):
    return []


def _mock_get_difference_no_diff(self, cfn, new, old):
    return []


def _mock_get_difference_diff(self, cfn, new, old):
    return ['test.test']


def _mock_allowed_update(self):
    return re.compile('test')


def _mock_get_template(obj, name):
    return {
        'GetTemplateResponse': {
            'GetTemplateResult': {
                'TemplateBody': '{"a": "b"}'
            }
        }
    }


def _mock_stack_exists_true(self, cfn, name):
    return True


def _mock_stack_exists_false(self, cfn, name):
    return False


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


def _mock_upload(self, stack, dest, credentials):
    pass


def _mock_audit_fails(self, stack, dest, credentials):
    raise AuditException('I fail')


def _mock_describe_stack_returns_mock_stack(self, stack):
    return [Stack()]


def _mock_describe_stack_returns_failed_mock_stack(self, stack):
    return [Stack(ret='CREATE_FAILED')]


def _mock_describe_stack_returns_rollback_mock_stack(self, stack):
    return [Stack(ret='ROLLBACK_COMPLETE')]


def _mock_describe_stack_returns_mock_stack_same_event(self, stack):
    return [Stack(same_event=True)]


def _mock_describe_stack_returns_mock_stack_old_events(self, stack):
    return [Stack(in_past=True)]


def _mock_describe_stack_returns_mock_stack_different_status(self, stack):
    _mock_describe_stack_returns_mock_stack_different_status.counter += 1
    if _mock_describe_stack_returns_mock_stack_different_status.counter < 2:
        return [Stack(ret='CREATE_IN_PROGRESS')]
    return [Stack()]

_mock_describe_stack_returns_mock_stack_different_status.counter = 0


def _mock_describe_stack_raises_different_exceptions(self, stack):
    _mock_describe_stack_raises_different_exceptions.counter += 1
    if _mock_describe_stack_raises_different_exceptions.counter % 2 == 0:
        _mock_describe_stack_raises_does_not_exist(self, stack)
    _mock_describe_stack_raises_limit_exceeded(self, stack)

_mock_describe_stack_raises_different_exceptions.counter = 0


def _mock_sleep(sleep_time):
    pass


def _mock_key_set_contents(self, bucket):
    return True


def _mock_s3_get_bucket(self, bucket):
    return bucket


def _mock_s3_connect():
    return boto.s3.connection.S3Connection('a', 'b')


def _mock_s3_connect_raises(aws_access_key_id, aws_secret_access_key):
    raise boto.exception.BotoServerError('nope', 'nope')


def _mock_is_term_false():
    return False


class TestAWSCFNOutput(object):

    @mock.patch('pmcf.utils.is_term', _mock_is_term_false)
    def test__get_input_not_term(self):
        cfno = AWSCFNOutput()
        assert_equals(cfno._get_input('test'), 'y')

    def test_run_no_region_raises(self):
        cfno = AWSCFNOutput()
        assert_raises(ProvisionerException, cfno.run, '{"a": "b"}', {})

    def test_run_bad_region_raises(self):
        cfno = AWSCFNOutput()
        assert_raises(ProvisionerException, cfno.run,
                      '{"a": "b"}', {'region': 'nah'})

    @mock.patch('boto.connect_s3', _mock_s3_connect)
    @mock.patch('boto.regioninfo.get_regions', _mock_search_regions)
    @mock.patch(
        'boto.cloudformation.CloudFormationConnection.validate_template',
        _mock_validate_template)
    @mock.patch('boto.cloudformation.CloudFormationConnection.create_stack',
                _mock_create_stack)
    @mock.patch('pmcf.outputs.cloudformation.AWSCFNOutput._stack_exists',
                _mock_stack_exists_false)
    def test_run_create_instance_profile_returns_true(self):
        cfno = AWSCFNOutput()
        metadata = {
            'region': 'eu-west-1',
            'use_iam_profile': True,
            'name': 'test',
            'environment': 'test',
            'audit': 'NoopAudit',
        }
        assert_equals(cfno.run('{"a": "b"}', metadata), True)

    @mock.patch('boto.regioninfo.get_regions', _mock_search_regions)
    @mock.patch(
        'boto.cloudformation.CloudFormationConnection.validate_template',
        _mock_validate_template)
    @mock.patch('boto.cloudformation.CloudFormationConnection.create_stack',
                _mock_create_stack)
    @mock.patch('pmcf.outputs.cloudformation.AWSCFNOutput._stack_exists',
                _mock_stack_exists_false)
    def test_run_create_returns_true(self):
        cfno = AWSCFNOutput()
        metadata = {
            'region': 'eu-west-1',
            'access': '1234',
            'secret': '2345',
            'name': 'test',
            'environment': 'test',
            'audit': 'NoopAudit',
        }
        assert_equals(cfno.run('{"a": "b"}', metadata), True)

    @mock.patch('boto.regioninfo.get_regions', _mock_search_regions)
    @mock.patch(
        'boto.cloudformation.CloudFormationConnection.validate_template',
        _mock_validate_template_url)
    @mock.patch('boto.cloudformation.CloudFormationConnection.create_stack',
                _mock_create_stack_url)
    @mock.patch('pmcf.outputs.cloudformation.AWSCFNOutput._upload_stack',
                _mock_upload)
    @mock.patch('pmcf.outputs.cloudformation.AWSCFNOutput._stack_exists',
                _mock_stack_exists_false)
    def test_run_create_upload_returns_true(self):
        cfno = AWSCFNOutput()
        metadata = {
            'region': 'eu-west-1',
            'access': '1234',
            'secret': '2345',
            'name': 'test',
            'environment': 'test',
            'audit': 'NoopAudit',
            'audit_output': 'thingy',
        }
        assert_equals(cfno.run('{"a": "b"}', metadata, upload=True), True)

    @mock.patch('boto.regioninfo.get_regions', _mock_search_regions)
    @mock.patch(
        'boto.cloudformation.CloudFormationConnection.validate_template',
        _mock_validate_template_url)
    @mock.patch('boto.cloudformation.CloudFormationConnection.create_stack',
                _mock_create_stack_url)
    @mock.patch('pmcf.outputs.cloudformation.AWSCFNOutput._upload_stack',
                _mock_upload)
    @mock.patch('pmcf.outputs.cloudformation.AWSCFNOutput._stack_exists',
                _mock_stack_exists_false)
    def test_run_connects_upload_succeeds(self):
        cfno = AWSCFNOutput()
        metadata = {
            'region': 'eu-west-1',
            'access': '1234',
            'secret': '2345',
            'name': 'test',
            'environment': 'test',
            'audit': 'NoopAudit',
            'audit_output': 'thingy',
            'strategy': 'InPlace',
        }
        assert_equals(cfno.run('{"a": "b"}', metadata, poll=False,
                               action='create', upload=True), True)

    @mock.patch('boto.regioninfo.get_regions', _mock_search_regions)
    @mock.patch(
        'boto.cloudformation.CloudFormationConnection.validate_template',
        _mock_validate_template)
    @mock.patch('boto.cloudformation.CloudFormationConnection.create_stack',
                _mock_create_stack)
    @mock.patch('pmcf.audit.S3Audit.record_stack', _mock_audit_fails)
    @mock.patch('pmcf.outputs.cloudformation.AWSCFNOutput._stack_exists',
                _mock_stack_exists_false)
    def test_run_audit_failure_connects(self):
        cfno = AWSCFNOutput()
        metadata = {
            'region': 'eu-west-1',
            'access': '1234',
            'secret': '2345',
            'name': 'test',
            'environment': 'test',
            'audit': 'S3Audit',
        }
        assert_equals(cfno.run('{"a": "b"}', metadata), True)

    @mock.patch('boto.regioninfo.get_regions', _mock_search_regions)
    @mock.patch(
        'boto.cloudformation.CloudFormationConnection.validate_template',
        _mock_validate_template)
    @mock.patch('boto.cloudformation.CloudFormationConnection.create_stack',
                _mock_create_stack)
    @mock.patch('pmcf.outputs.cloudformation.AWSCFNOutput._stack_exists',
                _mock_stack_exists_false)
    def test_run_with_tags_connects(self):
        cfno = AWSCFNOutput()
        metadata = {
            'region': 'eu-west-1',
            'access': '1234',
            'secret': '2345',
            'name': 'test',
            'environment': 'test',
            'audit': 'NoopAudit',
            'tags': {
                'Name': 'test'
            }
        }
        assert_equals(cfno.run('{"a": "b"}', metadata), True)

    @mock.patch('boto.regioninfo.get_regions', _mock_search_regions)
    @mock.patch(
        'boto.cloudformation.CloudFormationConnection.validate_template',
        _mock_validate_template)
    @mock.patch('boto.cloudformation.CloudFormationConnection.update_stack',
                _mock_create_stack)
    @mock.patch('boto.cloudformation.CloudFormationConnection.describe_stacks',
                _mock_describe_stack)
    @mock.patch('pmcf.outputs.cloudformation.AWSCFNOutput._show_prompt',
                _mock_return_true)
    @mock.patch('pmcf.strategy.inplace.InPlace.allowed_update',
                _mock_allowed_update)
    @mock.patch('pmcf.outputs.cloudformation.AWSCFNOutput._get_difference',
                _mock_get_difference_diff)
    def test_run_with_prompt_true_succeeds(self):
        cfno = AWSCFNOutput()
        metadata = {
            'region': 'eu-west-1',
            'access': '1234',
            'secret': '2345',
            'name': 'test',
            'environment': 'test',
            'strategy': 'PromptInPlace',
            'audit': 'NoopAudit',
            'tags': {
                'Name': 'test'
            }
        }
        assert_equals(cfno.run('{"a": "b"}', metadata, action='update'), True)

    @mock.patch('boto.regioninfo.get_regions', _mock_search_regions)
    @mock.patch(
        'boto.cloudformation.CloudFormationConnection.validate_template',
        _mock_validate_template)
    @mock.patch('boto.cloudformation.CloudFormationConnection.create_stack',
                _mock_create_stack)
    @mock.patch('boto.cloudformation.CloudFormationConnection.describe_stacks',
                _mock_describe_stack)
    def test_run_with_iam_caps_succeeds(self):
        cfno = AWSCFNOutput()
        metadata = {
            'region': 'eu-west-1',
            'access': '1234',
            'secret': '2345',
            'name': 'test',
            'environment': 'test',
            'strategy': 'InPlace',
            'audit': 'NoopAudit',
            'tags': {
                'Name': 'test'
            }
        }
        data = '{"Resources": {"foo": {"Type": "AWS::IAM::Thing"}}}'
        assert_equals(cfno.run(data, metadata), True)

    @mock.patch('boto.regioninfo.get_regions', _mock_search_regions)
    @mock.patch(
        'boto.cloudformation.CloudFormationConnection.validate_template',
        _mock_validate_template)
    @mock.patch('boto.cloudformation.CloudFormationConnection.create_stack',
                _mock_create_stack)
    @mock.patch('boto.cloudformation.CloudFormationConnection.describe_stacks',
                _mock_describe_stack)
    def test_run_with_no_iam_caps_succeeds(self):
        cfno = AWSCFNOutput()
        metadata = {
            'region': 'eu-west-1',
            'access': '1234',
            'secret': '2345',
            'name': 'test',
            'environment': 'test',
            'strategy': 'InPlace',
            'audit': 'NoopAudit',
            'tags': {
                'Name': 'test'
            }
        }
        data = '{"Resources": {"foo": {"Type": "AWS::AMI::Thing"}}}'
        assert_equals(cfno.run(data, metadata), True)

    @mock.patch('boto.regioninfo.get_regions', _mock_search_regions)
    @mock.patch(
        'boto.cloudformation.CloudFormationConnection.validate_template',
        _mock_validate_template)
    @mock.patch('boto.cloudformation.CloudFormationConnection.update_stack',
                _mock_create_stack)
    @mock.patch('boto.cloudformation.CloudFormationConnection.describe_stacks',
                _mock_describe_stack)
    @mock.patch('pmcf.outputs.cloudformation.AWSCFNOutput._show_prompt',
                _mock_return_false)
    @mock.patch('pmcf.strategy.inplace.InPlace.allowed_update',
                _mock_allowed_update)
    @mock.patch('pmcf.outputs.cloudformation.AWSCFNOutput._get_difference',
                _mock_get_difference_diff)
    def test_run_with_prompt_false_succeeds(self):
        cfno = AWSCFNOutput()
        metadata = {
            'region': 'eu-west-1',
            'access': '1234',
            'secret': '2345',
            'name': 'test',
            'environment': 'test',
            'strategy': 'PromptInPlace',
            'audit': 'NoopAudit',
            'tags': {
                'Name': 'test'
            }
        }
        assert_equals(cfno.run('{"a": "b"}', metadata, action='update'), True)

    @mock.patch('boto.regioninfo.get_regions', _mock_search_regions)
    @mock.patch(
        'boto.cloudformation.CloudFormationConnection.validate_template',
        _mock_validate_template)
    @mock.patch('boto.cloudformation.CloudFormationConnection.create_stack',
                _mock_create_stack_fails)
    @mock.patch('pmcf.outputs.cloudformation.AWSCFNOutput._stack_exists',
                _mock_stack_exists_false)
    def test_run_stack_fails(self):
        cfno = AWSCFNOutput()
        metadata = {
            'region': 'eu-west-1',
            'access': '1234',
            'secret': '2345',
            'audit': 'NoopAudit',
            'environment': 'test',
            'name': 'test'
        }
        assert_raises(ProvisionerException, cfno.run, '{"a": "b"}', metadata)

    @mock.patch('boto.regioninfo.get_regions', _mock_search_regions)
    @mock.patch('pmcf.outputs.cloudformation.AWSCFNOutput._stack_exists',
                _mock_stack_exists_false)
    def test_run_delete_nonexistant_stack_succeeds(self):
        cfno = AWSCFNOutput()
        metadata = {
            'region': 'eu-west-1',
            'access': '1234',
            'secret': '2345',
            'name': 'test',
            'environment': 'test',
            'audit': 'NoopAudit',
            'audit_output': 'thingy',
            'strategy': 'InPlace',
        }
        assert_equals(cfno.run('{"a": "b"}', metadata,
                      action='delete', upload=True), True)

    @mock.patch('boto.regioninfo.get_regions', _mock_search_regions)
    @mock.patch('pmcf.outputs.cloudformation.AWSCFNOutput._stack_exists',
                _mock_stack_exists_true)
    @mock.patch('boto.cloudformation.CloudFormationConnection.delete_stack',
                _mock_delete_stack)
    def test_run_delete_existing_stack_succeeds(self):
        cfno = AWSCFNOutput()
        metadata = {
            'region': 'eu-west-1',
            'access': '1234',
            'secret': '2345',
            'name': 'test',
            'environment': 'test',
            'audit': 'NoopAudit',
            'audit_output': 'thingy',
            'strategy': 'InPlace',
        }
        assert_equals(cfno.run('{"a": "b"}', metadata,
                      action='delete', upload=True), True)

    @mock.patch('boto.regioninfo.get_regions', _mock_search_regions)
    @mock.patch('pmcf.outputs.cloudformation.AWSCFNOutput._stack_exists',
                _mock_stack_exists_true)
    @mock.patch('boto.cloudformation.CloudFormationConnection.delete_stack',
                _mock_delete_stack)
    @mock.patch('pmcf.outputs.cloudformation.AWSCFNOutput._get_input',
                _mock_return_no)
    def test_run_delete_existing_stack_prompt_no_returns_false(self):
        cfno = AWSCFNOutput()
        metadata = {
            'region': 'eu-west-1',
            'access': '1234',
            'secret': '2345',
            'name': 'test',
            'environment': 'test',
            'audit': 'NoopAudit',
            'audit_output': 'thingy',
            'strategy': 'PromptInPlace',
        }
        assert_equals(cfno.run('{"a": "b"}', metadata,
                      action='delete', upload=True), False)

    @mock.patch('boto.regioninfo.get_regions', _mock_search_regions)
    @mock.patch('pmcf.outputs.cloudformation.AWSCFNOutput._stack_exists',
                _mock_stack_exists_true)
    @mock.patch('boto.cloudformation.CloudFormationConnection.delete_stack',
                _mock_delete_stack_fails)
    def test_run_delete_existing_stack_exception_raises(self):
        cfno = AWSCFNOutput()
        metadata = {
            'region': 'eu-west-1',
            'access': '1234',
            'secret': '2345',
            'name': 'test',
            'environment': 'test',
            'audit': 'NoopAudit',
            'audit_output': 'thingy',
            'strategy': 'InPlace',
        }
        assert_raises(ProvisionerException, cfno.run, '{"a": "b"}',
                      metadata, action='delete', upload=True)

    @mock.patch('boto.regioninfo.get_regions', _mock_search_regions)
    @mock.patch('pmcf.outputs.cloudformation.AWSCFNOutput._stack_updatable',
                _mock_stack_exists_false)
    def test_run_trigger_stack_does_not_exist_returns_true(self):
        cfno = AWSCFNOutput()
        metadata = {
            'region': 'eu-west-1',
            'access': '1234',
            'secret': '2345',
            'name': 'test',
            'environment': 'test',
            'audit': 'NoopAudit',
            'audit_output': 'thingy',
            'strategy': 'InPlace',
        }
        assert_equals(True, cfno.run('{"a": "b"}', metadata, action='trigger'))

    @mock.patch('boto.regioninfo.get_regions', _mock_search_regions)
    @mock.patch('pmcf.outputs.cloudformation.AWSCFNOutput._stack_updatable',
                _mock_stack_exists_true)
    @mock.patch('pmcf.outputs.cloudformation.AWSCFNOutput._get_difference',
                _mock_get_difference_no_diff)
    def test_run_trigger_stack_exists_no_update_returns_true(self):
        cfno = AWSCFNOutput()
        metadata = {
            'region': 'eu-west-1',
            'access': '1234',
            'secret': '2345',
            'name': 'test',
            'environment': 'test',
            'audit': 'NoopAudit',
            'audit_output': 'thingy',
            'strategy': 'InPlace',
        }
        assert_equals(True, cfno.run('{"a": "b"}', metadata, action='trigger'))

    @mock.patch('boto.regioninfo.get_regions', _mock_search_regions)
    @mock.patch('pmcf.outputs.cloudformation.AWSCFNOutput._stack_updatable',
                _mock_stack_exists_true)
    @mock.patch('pmcf.outputs.cloudformation.AWSCFNOutput._get_difference',
                _mock_get_difference_diff)
    def test_run_trigger_stack_exists_no_update_allowed_raises(self):
        cfno = AWSCFNOutput()
        metadata = {
            'region': 'eu-west-1',
            'access': '1234',
            'secret': '2345',
            'name': 'test',
            'environment': 'test',
            'audit': 'NoopAudit',
            'audit_output': 'thingy',
            'strategy': 'InPlace',
        }
        assert_raises(ProvisionerException, cfno.run,
                      '{"a": "b"}', metadata, action='trigger')

    @mock.patch('boto.regioninfo.get_regions', _mock_search_regions)
    @mock.patch('pmcf.outputs.cloudformation.AWSCFNOutput._stack_updatable',
                _mock_stack_exists_true)
    @mock.patch('pmcf.outputs.cloudformation.AWSCFNOutput._get_difference',
                _mock_get_difference_diff)
    @mock.patch('pmcf.strategy.inplace.InPlace.allowed_update',
                _mock_allowed_update)
    @mock.patch('pmcf.outputs.cloudformation.AWSCFNOutput._upload_stack',
                _mock_upload)
    @mock.patch(
        'boto.cloudformation.CloudFormationConnection.validate_template',
        _mock_validate_template_url)
    @mock.patch('boto.cloudformation.CloudFormationConnection.update_stack',
                _mock_create_stack_url)
    def test_run_trigger_stack_exists_update_allowed_upload_returns_true(self):
        cfno = AWSCFNOutput()
        metadata = {
            'region': 'eu-west-1',
            'access': '1234',
            'secret': '2345',
            'name': 'test',
            'environment': 'test',
            'audit': 'NoopAudit',
            'audit_output': 'thingy',
            'strategy': 'InPlace',
        }
        assert_equals(cfno.run('{"a": "b"}', metadata, poll=False,
                               action='trigger', upload=True), True)

    @mock.patch('boto.regioninfo.get_regions', _mock_search_regions)
    @mock.patch('pmcf.outputs.cloudformation.AWSCFNOutput._stack_updatable',
                _mock_stack_exists_true)
    @mock.patch('pmcf.outputs.cloudformation.AWSCFNOutput._get_difference',
                _mock_get_difference_diff)
    @mock.patch('pmcf.strategy.inplace.InPlace.allowed_update',
                _mock_allowed_update)
    @mock.patch(
        'boto.cloudformation.CloudFormationConnection.validate_template',
        _mock_validate_template_url)
    @mock.patch('boto.cloudformation.CloudFormationConnection.update_stack',
                _mock_create_stack_url)
    def test_run_trigger_stack_exists_update_allowed_returns_true(self):
        cfno = AWSCFNOutput()
        metadata = {
            'region': 'eu-west-1',
            'access': '1234',
            'secret': '2345',
            'name': 'test',
            'environment': 'test',
            'audit': 'NoopAudit',
            'audit_output': 'thingy',
            'strategy': 'InPlace',
        }
        assert_equals(cfno.run('{"a": "b"}', metadata, poll=False,
                               action='trigger', upload=False), True)

    @mock.patch('boto.regioninfo.get_regions', _mock_search_regions)
    @mock.patch('pmcf.outputs.cloudformation.AWSCFNOutput._stack_exists',
                _mock_stack_exists_true)
    @mock.patch('pmcf.outputs.cloudformation.AWSCFNOutput._stack_updatable',
                _mock_stack_exists_true)
    def test_run_update_stack_existing_stack_no_update_allowed_raises(self):
        cfno = AWSCFNOutput()
        metadata = {
            'region': 'eu-west-1',
            'access': '1234',
            'secret': '2345',
            'name': 'test',
            'environment': 'test',
            'audit': 'NoopAudit',
            'tags': {
                'Name': 'test'
            }
        }
        assert_raises(ProvisionerException, cfno.run, '{"a": "b"}',
                      metadata, action='update')

    @mock.patch('boto.regioninfo.get_regions', _mock_search_regions)
    @mock.patch('pmcf.outputs.cloudformation.AWSCFNOutput._stack_exists',
                _mock_stack_exists_true)
    @mock.patch('pmcf.outputs.cloudformation.AWSCFNOutput._stack_updatable',
                _mock_stack_exists_true)
    @mock.patch(
        'boto.cloudformation.CloudFormationConnection.validate_template',
        _mock_validate_template_url)
    @mock.patch('boto.cloudformation.CloudFormationConnection.update_stack',
                _mock_create_stack_url)
    @mock.patch('pmcf.outputs.cloudformation.AWSCFNOutput._upload_stack',
                _mock_upload)
    @mock.patch('pmcf.strategy.inplace.InPlace.allowed_update',
                _mock_allowed_update)
    @mock.patch('pmcf.outputs.cloudformation.AWSCFNOutput._get_difference',
                _mock_get_difference_diff)
    def test_run_update_existing_stack_upload_returns_true(self):
        cfno = AWSCFNOutput()
        metadata = {
            'region': 'eu-west-1',
            'access': '1234',
            'secret': '2345',
            'name': 'test',
            'environment': 'test',
            'audit': 'NoopAudit',
            'audit_output': 'thingy',
            'strategy': 'InPlace',
        }
        assert_equals(cfno.run('{"a": "b"}', metadata, poll=False,
                               action='update', upload=True), True)

    @mock.patch('boto.regioninfo.get_regions', _mock_search_regions)
    @mock.patch('pmcf.outputs.cloudformation.AWSCFNOutput._stack_exists',
                _mock_stack_exists_true)
    @mock.patch('pmcf.outputs.cloudformation.AWSCFNOutput._stack_updatable',
                _mock_stack_exists_true)
    @mock.patch(
        'boto.cloudformation.CloudFormationConnection.validate_template',
        _mock_validate_template)
    @mock.patch('boto.cloudformation.CloudFormationConnection.update_stack',
                _mock_create_stack)
    @mock.patch('pmcf.strategy.inplace.InPlace.allowed_update',
                _mock_allowed_update)
    @mock.patch('pmcf.outputs.cloudformation.AWSCFNOutput._get_difference',
                _mock_get_difference_diff)
    def test_run_update_existing_stack_returns_true(self):
        cfno = AWSCFNOutput()
        metadata = {
            'region': 'eu-west-1',
            'access': '1234',
            'secret': '2345',
            'name': 'test',
            'environment': 'test',
            'audit': 'NoopAudit',
            'audit_output': 'thingy',
            'strategy': 'InPlace',
        }
        assert_equals(cfno.run('{"a": "b"}', metadata, poll=False,
                               action='update', upload=False), True)

    @mock.patch('boto.regioninfo.get_regions', _mock_search_regions)
    @mock.patch('pmcf.outputs.cloudformation.AWSCFNOutput._stack_exists',
                _mock_stack_exists_false)
    @mock.patch('pmcf.outputs.cloudformation.AWSCFNOutput._stack_updatable',
                _mock_stack_exists_false)
    def test_run_update_stack_nonexisting_stack_returns_true(self):
        cfno = AWSCFNOutput()
        metadata = {
            'region': 'eu-west-1',
            'access': '1234',
            'secret': '2345',
            'name': 'test',
            'environment': 'test',
            'audit': 'NoopAudit',
            'audit_output': 'thingy',
            'strategy': 'InPlace',
        }
        assert_equals(cfno.run('{"a": "b"}', metadata, poll=False,
                               action='update', upload=True), True)

    @mock.patch('boto.cloudformation.CloudFormationConnection.describe_stacks',
                _mock_describe_stack)
    def test__stack_updatable_exists(self):
        cfno = AWSCFNOutput()
        cfn = boto.connect_cloudformation(
            aws_access_key_id='access',
            aws_secret_access_key='secret'
        )
        assert_equals(True, cfno._stack_updatable(cfn, 'test'))

    @mock.patch('boto.cloudformation.CloudFormationConnection.describe_stacks',
                _mock_describe_stack_fails)
    def test__stack_updatable_nonexistant(self):
        cfno = AWSCFNOutput()
        cfn = boto.connect_cloudformation(
            aws_access_key_id='access',
            aws_secret_access_key='secret'
        )
        assert_equals(False, cfno._stack_updatable(cfn, 'test'))

    @mock.patch('time.sleep', _mock_sleep)
    @mock.patch('boto.cloudformation.CloudFormationConnection.describe_stacks',
                _mock_describe_stack_raises_different_exceptions)
    def test__stack_updatable_limit_exceeded_does_not_exist(self):
        cfno = AWSCFNOutput()
        cfn = boto.connect_cloudformation(
            aws_access_key_id='access',
            aws_secret_access_key='secret'
        )
        assert_equals(False, cfno._stack_updatable(cfn, 'test'))

    @mock.patch('time.sleep', _mock_sleep)
    @mock.patch('boto.cloudformation.CloudFormationConnection.describe_stacks',
                _mock_describe_stack_raises_different_exceptions)
    def test__stack_exists_limit_exceeded_does_not_exist(self):
        cfno = AWSCFNOutput()
        cfn = boto.connect_cloudformation(
            aws_access_key_id='access',
            aws_secret_access_key='secret'
        )
        assert_equals(False, cfno._stack_exists(cfn, 'test'))

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
    @mock.patch('pmcf.utils.get_changed_keys_from_templates',
                _mock_get_changed_keys_from_templates)
    def test__get_difference_no_difference(self):
        cfno = AWSCFNOutput()
        cfn = boto.connect_cloudformation(
            aws_access_key_id='access',
            aws_secret_access_key='secret'
        )
        assert_equals([], cfno._get_difference(cfn, 'test', '{"a": "b"}'))

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
    @mock.patch('pmcf.outputs.cloudformation.make_diff',
                _mock_make_diff_differs)
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
    @mock.patch('pmcf.outputs.cloudformation.make_diff',
                _mock_make_diff_differs)
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

    @mock.patch('time.sleep', _mock_sleep)
    def test_do_poll_false_returns_true(self):
        cfno = AWSCFNOutput()
        assert_equals(True, cfno.do_poll(None, 'test', False, 'create'))

    @mock.patch('time.sleep', _mock_sleep)
    @mock.patch('boto.cloudformation.CloudFormationConnection.describe_stacks',
                _mock_describe_stack_returns_mock_stack)
    def test_do_poll_true_returns_true(self):
        cfno = AWSCFNOutput()
        cfn = boto.connect_cloudformation(
            aws_access_key_id='access',
            aws_secret_access_key='secret'
        )
        assert_equals(True, cfno.do_poll(cfn, 'test', True, 'create'))

    @mock.patch('time.sleep', _mock_sleep)
    @mock.patch('boto.cloudformation.CloudFormationConnection.describe_stacks',
                _mock_describe_stack_returns_failed_mock_stack)
    def test_do_poll_true_returns_false_on_failure(self):
        cfno = AWSCFNOutput()
        cfn = boto.connect_cloudformation(
            aws_access_key_id='access',
            aws_secret_access_key='secret'
        )
        assert_equals(False, cfno.do_poll(cfn, 'test', True, 'create'))

    @mock.patch('time.sleep', _mock_sleep)
    @mock.patch('boto.cloudformation.CloudFormationConnection.describe_stacks',
                _mock_describe_stack_returns_rollback_mock_stack)
    def test_do_poll_true_returns_false_on_rollback(self):
        cfno = AWSCFNOutput()
        cfn = boto.connect_cloudformation(
            aws_access_key_id='access',
            aws_secret_access_key='secret'
        )
        assert_equals(False, cfno.do_poll(cfn, 'test', True, 'create'))

    @mock.patch('time.sleep', _mock_sleep)
    @mock.patch('boto.cloudformation.CloudFormationConnection.describe_stacks',
                _mock_describe_stack_returns_mock_stack_same_event)
    def test_do_poll_true_returns_true_multiple_same_events(self):
        cfno = AWSCFNOutput()
        cfn = boto.connect_cloudformation(
            aws_access_key_id='access',
            aws_secret_access_key='secret'
        )
        assert_equals(True, cfno.do_poll(cfn, 'test', True, 'create'))

    @mock.patch('time.sleep', _mock_sleep)
    @mock.patch('boto.cloudformation.CloudFormationConnection.describe_stacks',
                _mock_describe_stack_returns_mock_stack_old_events)
    def test_do_poll_true_returns_true_multiple_old_events(self):
        cfno = AWSCFNOutput()
        cfn = boto.connect_cloudformation(
            aws_access_key_id='access',
            aws_secret_access_key='secret'
        )
        assert_equals(True, cfno.do_poll(cfn, 'test', True, 'create'))

    @mock.patch('time.sleep', _mock_sleep)
    @mock.patch('boto.cloudformation.CloudFormationConnection.describe_stacks',
                _mock_describe_stack_returns_mock_stack_different_status)
    @mock.patch('time.sleep', _mock_sleep)
    def test_do_poll_true_returns_true_multiple_loops(self):
        cfno = AWSCFNOutput()
        cfn = boto.connect_cloudformation(
            aws_access_key_id='access',
            aws_secret_access_key='secret'
        )
        assert_equals(True, cfno.do_poll(cfn, 'test', True, 'create'))

    @mock.patch('boto.connect_s3', _mock_s3_connect)
    @mock.patch('boto.s3.connection.S3Connection.get_bucket',
                _mock_s3_get_bucket)
    @mock.patch('boto.s3.key.Key.set_contents_from_string',
                _mock_key_set_contents)
    def test__upload_stack_succeeds_iam_profile(self):
        cfno = AWSCFNOutput()
        creds = {
            'audit_output': 'test',
            'use_iam_profile': True,
        }
        assert_equals(None, cfno._upload_stack('{}', 'test', creds))

    @mock.patch('boto.s3.connection.S3Connection.get_bucket',
                _mock_s3_get_bucket)
    @mock.patch('boto.s3.key.Key.set_contents_from_string',
                _mock_key_set_contents)
    def test__upload_stack_succeeds(self):
        cfno = AWSCFNOutput()
        creds = {
            'access': '1234',
            'secret': '1234',
            'audit_output': 'test',
        }
        assert_equals(None, cfno._upload_stack('{}', 'test', creds))

    @mock.patch('boto.connect_s3', _mock_s3_connect_raises)
    def test_record_stack_fails_raises(self):
        cfno = AWSCFNOutput()
        creds = {
            'access': '1234',
            'secret': '1234',
            'audit_output': 'test',
        }
        assert_raises(ProvisionerException, cfno._upload_stack,
                      '{}', 'test', creds)

    @mock.patch('time.sleep', _mock_sleep)
    @mock.patch('boto.cloudformation.CloudFormationConnection.describe_stacks',
                _mock_describe_stack_raises_does_not_exist)
    def test_do_poll_true_delete_returns_true_on_non_existing_stack(self):
        cfno = AWSCFNOutput()
        cfn = boto.connect_cloudformation(
            aws_access_key_id='access',
            aws_secret_access_key='secret'
        )
        assert_equals(True, cfno.do_poll(cfn, 'test', True, 'delete'))

    @mock.patch('time.sleep', _mock_sleep)
    @mock.patch('boto.cloudformation.CloudFormationConnection.describe_stacks',
                _mock_describe_stack_raises_different_exceptions)
    def test_do_poll_true_delete_catches_rate_limit(self):
        cfno = AWSCFNOutput()
        cfn = boto.connect_cloudformation(
            aws_access_key_id='access',
            aws_secret_access_key='secret'
        )
        assert_equals(True, cfno.do_poll(cfn, 'test', True, 'delete'))

    @mock.patch('time.sleep', _mock_sleep)
    @mock.patch('boto.cloudformation.CloudFormationConnection.describe_stacks',
                _mock_describe_stack_raises_does_not_exist)
    def test_do_poll_true_create_returns_false_on_non_existing_stack(self):
        cfno = AWSCFNOutput()
        cfn = boto.connect_cloudformation(
            aws_access_key_id='access',
            aws_secret_access_key='secret'
        )
        assert_equals(False, cfno.do_poll(cfn, 'test', True, 'create'))
