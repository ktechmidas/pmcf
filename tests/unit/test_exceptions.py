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
from pmcf import exceptions


class TestException(object):

    def test_raise_parser_failure(self):
        def raiser(message):
            raise exceptions.ParserFailure(message)

        msg = 'test message'
        try:
            raiser(msg)
        except exceptions.ParserFailure, e:
            assert_equals(e.message, "Error parsing input: " + msg)
