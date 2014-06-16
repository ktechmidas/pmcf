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

import email
import gzip
from nose.tools import assert_equals
import StringIO

from pmcf.provisioners.awsfw import AWSFWProvisioner


class TestAWSFWProvisioner(object):
    def __init__(self):
        self.message = ''
        self.config = {
            'foo': 'baz',
            'bar': 'womble',
            'farm': 'test'
        }

    def setup(self):
        args = {
            'roles': ['test'],
            'roleBucket': 'somewhere',
            'apps': ['test'],
            'appBucket': 'somewhere',
        }
        awsfwp = AWSFWProvisioner()
        data = awsfwp.userdata(self.config, args)
        self.message = email.message_from_string(data)

    def _decode(self, data):
        stringio = StringIO.StringIO(data)
        decompressedFile = gzip.GzipFile(fileobj=stringio)
        return decompressedFile.read()

    def test_userdata_contains_expected_files(self):
        expected_files = ['part-handler', 's3curl.pl', 'vars', 'bootstrap.sh']

        fnames = []
        for part in self.message.walk():
            if part.get_content_maintype() == 'multipart':
                continue
            fnames.append(part.get_filename())

        assert_equals(fnames, expected_files)

    def test_userdata_vars_contains_expected_data(self):
        vars_data = {}
        for part in self.message.walk():
            if part.get_content_maintype() == 'multipart':
                continue
            if part.get_filename() == 'vars':
                # Compare by turning
                # export foo=bar
                # into
                # { 'foo': 'bar' }
                data = self._decode(part.get_payload(decode=True))
                for line in data.split('\n'):
                    if line == '':
                        continue
                    key, val = line.split('=')
                    key = key[7:]  # strip off  leading 'export'
                    vars_data[key] = val

        assert_equals(vars_data, self.config)
