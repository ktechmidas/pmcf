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

from pmcf import exceptions
from pmcf import utils


class TestUtils(object):

    def test_error(self):
        msg = 'test message'
        try:
            utils.error(object(), msg)
        except exceptions.PropertyException, e:
            assert_equals(e.message, "Error in resource properties: " + msg +
                                     " in type <unknown type>")

    def test_import_from_string_no_module(self):
        assert_raises(ImportError, utils.import_from_string, 'foo', 'bar')

    def test_import_from_string_success(self):
        kls = utils.import_from_string('pmcf.parsers', 'BaseParser')
        from pmcf.parsers import BaseParser
        assert_equals(BaseParser, kls)
