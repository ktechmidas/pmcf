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

from pmcf.exceptions import PolicyException
from pmcf.policy import BasePolicy


class TestBasePolicy(object):

    def test_policy_file_load(self):
        policy = BasePolicy()
        assert_equals(policy.json_policy, {})

    def test_return_on_no_policy(self):
        policy = BasePolicy()
        assert_equals(True, policy.validate_resource('wombat', {}))
