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

from pmcf.parsers import BaseParser


class TestBaseParser(object):

    def test_parse_raises(self):
        struct = {
            'foo': {
                'bar': [1, 'three'],
                'baz': True
            }
        }

        config = """
            foo:
                bar:
                  - 1
                  - three
                baz: true
        """
        #  HACK alert: have to empty this so we can instantiate the class
        BaseParser.__abstractmethods__ = set()
        parser = BaseParser()
        assert_raises(NotImplementedError, parser.parse, config)
