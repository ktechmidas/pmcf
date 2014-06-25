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

from pmcf.provisioners.noop import NoopProvisioner


class TestNoopProvisioner(object):
    def test_userdata_contains_expected_data(self):
        args = {}
        data = NoopProvisioner().userdata(args)
        assert_equals(data, None)

    def test_cfn_init_contains_expected_data(self):
        args = {}
        data = NoopProvisioner().cfn_init(args)
        assert_equals(data, None)

    def test_wants_wait_returns_false(self):
        data = NoopProvisioner().wants_wait()
        assert_equals(data, False)

    def test_wants_profile_returns_false(self):
        data = NoopProvisioner().wants_profile()
        assert_equals(data, False)
