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

import json
from nose.tools import assert_equals
from troposphere import awsencode

from pmcf.provisioners.block import BlockingProvisioner


class TestBlockingProvisioner(object):
    def test_userdata_contains_expected_data(self):
        args = {
            'WaitHandle': 'test'
        }
        uri = "https://s3.amazonaws.com/cloudformation-examples/"
        ret = {
            "Fn::Join": ["", [
                "#!/bin/bash\n",
                "apt-get -y install python-setuptools\n",
                "easy_install %s" % uri,
                "aws-cfn-bootstrap-latest.tar.gz\n",
                "cfn-signal -e 0 -r Success '",
                {
                    "Ref": "test"
                },
                "'\n"
            ]]
        }

        data = BlockingProvisioner().userdata(args)
        data = json.loads(json.dumps(data, cls=awsencode))
        assert_equals(data, ret)

    def test_cfn_init_contains_expected_data(self):
        args = {}
        data = BlockingProvisioner().cfn_init(args)
        assert_equals(data, None)

    def test_wants_wait_returns_false(self):
        data = BlockingProvisioner().wants_wait()
        assert_equals(data, True)

    def test_wants_profile_returns_false(self):
        data = BlockingProvisioner().wants_profile()
        assert_equals(data, False)
