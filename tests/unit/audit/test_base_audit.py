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

from nose.tools import assert_raises

from pmcf.audit import BaseAudit


class TestBaseAudit(object):

    def __init__(self):
        self.audit = None

    def setup(self):
        #  HACK alert: have to empty this so we can instantiate the class
        BaseAudit.__abstractmethods__ = set()
        self.audit = BaseAudit()

    def test_record_stack_raises(self):
        assert_raises(NotImplementedError, self.audit.record_stack,
                      None, None, None)
