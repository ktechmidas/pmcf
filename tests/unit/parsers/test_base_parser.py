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

from pmcf.exceptions import ParserFailure
from pmcf.parsers import BaseParser


class TestBaseParser(object):

    def __init__(self):
        self.parser = None

    def setup(self):
        #  HACK alert: have to empty this so we can instantiate the class
        BaseParser.__abstractmethods__ = set()
        self.parser = BaseParser()

    def test_parse_raises(self):
        config = """
            foo:
                bar:
                  - 1
                  - three
                baz: true
        """
        assert_raises(NotImplementedError, self.parser.parse, config)

    def test_parse_file_missing_file_raises(self):
        assert_raises(ParserFailure, self.parser.parse_file, 'missing')

    def test_parse_file_raises(self):
        assert_raises(NotImplementedError, self.parser.parse_file, 'README.md')

    def test_validate_succeeds(self):
        assert_equals(None, self.parser.validate())

    def test_validate_fails_on_bad_schema(self):
        self.parser._stack['monkey'] = 'business'
        assert_raises(ParserFailure, self.parser.validate)
