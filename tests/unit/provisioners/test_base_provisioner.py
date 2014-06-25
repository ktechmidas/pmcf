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

    def test_cfn_init_returns_none(self):
        assert_equals(None, self.provisioner.cfn_init({}))

    def test_parse_raises(self):
        assert_raises(NotImplementedError, self.provisioner.userdata, {})

    def test_userdata_too_long(self):
        data = self.provisioner.make_skeleton()
        with open('tests/data/userdata/test_data') as fd:
            self.provisioner.add_data(data, fd.read(), 'test_data')
        assert_raises(ProvisionerException, self.provisioner.resize, data)

    def test_skeleton_output(self):
        expected = """Content-Type: multipart/mixed; boundary="%s"
MIME-Version: 1.0

--%s

--%s--""" % (self.provisioner.boundary,
             self.provisioner.boundary,
             self.provisioner.boundary)
        data = self.provisioner.make_skeleton().as_string().rstrip("\n")
        assert_equals(data, expected)
