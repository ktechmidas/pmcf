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

from pmcf.strategy import InPlace


class TestInPlaceStrategy(object):

    def test_should_update_true(self):
        strategy = InPlace()
        assert_equals(strategy.should_update('update'), True)

    def test_should_prompt_update_false(self):
        strategy = InPlace()
        assert_equals(strategy.should_prompt('update'), False)

    def test_should_prompt_delete_false(self):
        strategy = InPlace()
        assert_equals(strategy.should_prompt('delete'), False)

    def test_allowed_update_should_not_match_invalid(self):
        strategy = InPlace()
        match = strategy.allowed_update()
        matcher = 'anything, really, nothing will match'
        assert_equals(match.match(matcher), None)

    def test_termination_policy_returns_default(self):
        strategy = InPlace()
        assert_equals(strategy.termination_policy(), ['Default'])
