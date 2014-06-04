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

from pmcf.audit import S3Audit
from pmcf.exceptions import AuditException


def _mock_s3_connect_raises_denied(aws_access_key_id, aws_secret_access_key):
    raise boto.exception.S3ResponseError('nope', 'nope')


def _mock_s3_connect_raises(aws_access_key_id, aws_secret_access_key):
    raise boto.exception.BotoServerError('nope', 'nope')


def _mock_key_set_contents(self, bucket):
    return True


def _mock_s3_get_bucket(self, bucket):
    return bucket


class TestS3Audit(object):

    @mock.patch('boto.connect_s3', _mock_s3_connect_raises)
    def test_record_stack_fails_raises(self):
        sa = S3Audit()
        creds = {
            'access': '1234',
            'secret': '1234',
            'audit_output': 'test',
        }
        assert_raises(AuditException, sa.record_stack, '{}', 'test', creds)

    @mock.patch('boto.connect_s3', _mock_s3_connect_raises_denied)
    def test_record_stack_fails_denied_raises(self):
        sa = S3Audit()
        creds = {
            'access': '1234',
            'secret': '1234',
            'audit_output': 'test',
        }
        assert_raises(AuditException, sa.record_stack, '{}', 'test', creds)

    @mock.patch('boto.s3.connection.S3Connection.get_bucket',
                _mock_s3_get_bucket)
    @mock.patch('boto.s3.key.Key.set_contents_from_string',
                _mock_key_set_contents)
    def test_record_stack_fails_raises(self):
        sa = S3Audit()
        creds = {
            'access': '1234',
            'secret': '1234',
            'audit_output': 'test',
        }
        assert_equals(True, sa.record_stack('{}', 'test', creds))
