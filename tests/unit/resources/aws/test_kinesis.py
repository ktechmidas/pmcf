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

from pmcf.exceptions import PropertyException
from pmcf.resources.aws import kinesis

from tests.unit.resources import TestResource


class TestKinesisResource(TestResource):
    def test_stream_invalid_no_shard_count(self):
        assert_raises(PropertyException, kinesis.Stream, 'bad-name')

    def test_stream_valid(self):
        data = {
            'Properties': {
                'ShardCount': 1,
            },
            'Type': 'AWS::Kinesis::Stream'
        }
        ks = kinesis.Stream(
            'test',
            ShardCount=1
        )
        assert_equals(self._data_for_resource(ks), data)
