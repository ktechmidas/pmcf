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

import mock
from nose.tools import assert_equals, assert_raises

from pmcf import exceptions
from pmcf import utils


def mock_colourise(start, string, end=None):
    return string


def mock_valchange(old, new):
    return ['a']


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

    @mock.patch('pmcf.utils.colourise_output', mock_colourise)
    def test_make_diff_same_data(self):
        a = b = '[1, 2, 3]'
        assert_equals(utils.make_diff(a, b), '')

    @mock.patch('pmcf.utils.colourise_output', mock_colourise)
    def test_make_diff_different_data(self):
        a = '{"a": [1, 2, 3]}'
        b = '{"a": [1, 2, 4]}'
        output = utils.make_diff(a, b)
        assert_equals(True, len(output) > 0)

    @mock.patch('pmcf.utils.valchange', mock_valchange)
    def test_get_changed_keys_from_templates_same_data(self):
        a = '{"a": [1, 2, 3]}'
        b = '{"a": [1, 2, 3]}'
        output = utils.get_changed_keys_from_templates(a, b)
        assert_equals(True, len(output) == 0)

    @mock.patch('pmcf.utils.valchange', mock_valchange)
    def test_get_changed_keys_from_templates_different_data(self):
        a = '{"a": [1, 2, 3]}'
        b = '{"a": [1, 2, 4]}'
        output = utils.get_changed_keys_from_templates(a, b)
        assert_equals(True, len(output) == 1)

    def test_valchange_same_data(self):
        a = {"a": [1, 2, 3]}
        b = {"a": [1, 2, 3]}
        output = utils.valchange(a, b)
        assert_equals(True, len(output) == 0)

    def test_valchange_same_data_nested_dict(self):
        a = {"a": {"b": [1, 2, 3]}}
        b = {"a": {"b": [1, 2, 3]}}
        output = utils.valchange(a, b)
        assert_equals(True, len(output) == 0)

    def test_valchange_missing_key(self):
        a = {"a": {"b": [1, 2, 3]}}
        b = {"a": {"c": [1, 2, 3]}}
        output = utils.valchange(a, b)
        assert_equals(True, len(output) == 1)

    def test_valchange_different_data(self):
        a = {"a": {"b": [1, 2, 3]}}
        b = {"a": {"b": [1, 2, 4]}}
        output = utils.valchange(a, b)
        assert_equals(True, len(output) == 1)
