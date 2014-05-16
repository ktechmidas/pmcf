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

from pmcf.exceptions import ProvisionerException
from pmcf.provisioners import BaseProvisioner


class TestBaseProvisioner(object):
    def __init__(self):
        self.provisioner = None

    def setup(self):
        #  HACK alert: have to empty this so we can instantiate the class
        BaseProvisioner.__abstractmethods__ = set()
        self.provisioner = BaseProvisioner()

    def test_parse_raises(self):
        config = {}
        assert_raises(NotImplementedError, self.provisioner.userdata, config)

    def test_userdata_too_long(self):
        data = self.provisioner.make_skeleton()
        with open('scripts/base/test_data') as fd:
            ud = self.provisioner.add_data(data, fd.read(),
                                           'x-binary', 'test_data')
        assert_raises(ProvisionerException, self.provisioner.resize, data)

    def test_skeleton_output(self):
        expected = """Content-Type: multipart/mixed; boundary="%s"
MIME-Version: 1.0

--%s

--%s--""" % (self.provisioner.boundary,
             self.provisioner.boundary,
             self.provisioner.boundary)
        data = self.provisioner.make_skeleton()
        assert_equals(data.as_string(), expected)

    def test_add_data_output(self):
        expected = """Content-Type: multipart/mixed; boundary="%s"
MIME-Version: 1.0

--%s
MIME-Version: 1.0
Content-Type: text/plain; charset="us-ascii"
Content-Transfer-Encoding: 7bit
Content-Disposition: attachment; filename="test"

foo=bar
--%s--""" % (self.provisioner.boundary,
             self.provisioner.boundary,
             self.provisioner.boundary)
        test_data = 'foo=bar'
        data = self.provisioner.make_skeleton()
        data = self.provisioner.add_data(data, test_data, 'plain', 'test')
        assert_equals(data.as_string(), expected)

    def test_resize(self):
        expected = """
eNqNjrEOgkAQRPv7isv1p0hQFHKVWljYGfsFFt0E9sjdksDfayw0JhZOOTMvM3vPgiz2Mg9Y6H7s
hAYIsuxpwqbUlR+5gTA7476VpckmTbJdkmf5Ll1tN+vUOaPOp/PRXjFE8lzo1SJRytp/0B/k/uua
4CTLoQPiUtd3CBHFmTFaiDWR+ZQDcGwx2CPXviG+FTqvSN75geLgI8lrBUSgvvdPv9QtdcjQozOC
UYxSrfeugvDnf2sfCJJi/A==
"""
        test_data = 'foo=bar'
        data = self.provisioner.make_skeleton()
        data = self.provisioner.add_data(data, test_data, 'plain', 'test')
        data = self.provisioner.resize(data)
