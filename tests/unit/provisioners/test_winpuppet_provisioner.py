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
import mock
from nose.tools import assert_equals
from troposphere import awsencode

from pmcf.provisioners.winpuppet import WindowsPuppetProvisioner


def _mock_time():
    return 1000


class TestWindowsPuppetProvisioner(object):
    def test_userdata_contains_expected_data(self):
        args = {
            'name': 'test',
            'stackname': 'test',
            'resource': 'LCtest',
            'WaitHandle': 'blah',
            'infrastructure': 'foo.zip',
        }
        script = {
            'Fn::Join': ['', [
                '<script>\n',
                'cfn-init.exe -v -s ',
                {
                    'Ref': u'AWS::StackId'
                },
                ' -r LCtest -c startup',
                ' --region ',
                {
                    'Ref': 'AWS::Region'
                },
                '\n',
                'cfn-signal.exe -e %ERRORLEVEL% ', 
                {
                    'Fn::Base64': {
                        'Ref': 'blah'
                    }
                }, 
                '\n', 
                '</script>'
            ]]
        }
        data = WindowsPuppetProvisioner().userdata(args)
        data = json.loads(json.dumps(data, cls=awsencode))
        assert_equals(data, script)

    @mock.patch('time.time', _mock_time)
    def test_ci_contains_expected_data_custom_facts_ref(self):
        args = {
            'infrastructure': 'zip.tgz',
            'bucket': 'testbucket',
            'role': 'instance-blah',
            'name': 'test',
            'stackname': 'test',
            'appname': 'test',
            'resource': 'LCtest',
            'environment': 'dev',
            'custom_facts': {
                'a': 'b',
                'c': '=d',
            }
        }

        ci_data = {
            "AWS::CloudFormation::Authentication": {
                "rolebased": {
                    "type": "s3", 
                    "buckets": [
                        "testbucket"
                    ], 
                    "roleName": "instance-blah"
                }
            }, 
            "AWS::CloudFormation::Init": {
                "configSets": {
                    "infra": [
                        "infraLoad", 
                        "infraPuppetRun"
                    ], 
                    "infraUpdate": [
                        "infraLoad", 
                        "infraPuppetRun", 
                        "infraPuppetFinal"
                    ], 
                    "puppetFinal": [
                        "infraPuppetFinal"
                    ], 
                    "startup": [
                        "bootstrap", 
                        {
                            "ConfigSet": "infra"
                        }, 
                        {
                            "ConfigSet": "puppetFinal"
                        }
                    ]
                }, 
                "trigger": {
                    "commands": {
                        "01-echo": {
                            "waitAfterCompletion": 0, 
                            "command": "echo 1000", 
                            "ignoreErrors": "true"
                        }
                    }
                }, 
                "infraPuppetRun": {
                    "commands": {
                        "01-run_puppet": {
                            "command": "\"c:\\Program Files\\Puppet Labs\\Puppet\\bin\\puppet.bat\" apply --modulepath c:\\Windows\\Temp\\puppet\\modules --environment first_run c:\\Windows\\Temp\\puppet\\manifests\\site.pp", 
                            "waitAfterCompletion": 0, 
                            "ignoreErrors": "true"
                        }
                    }
                }, 
                "infraPuppetFinal": {
                    "commands": {
                        "02-clean_puppet": {
                            "waitAfterCompletion": 0, 
                            "command": "rmdir /S /Q c:\\Windows\\Temp\\puppet"
                        }, 
                        "01-run_puppet": {
                            "waitAfterCompletion": 0, 
                            "command": "\"c:\\Program Files\\Puppet Labs\\Puppet\\bin\\puppet.bat\" apply --modulepath c:\\Windows\\Temp\\puppet\\modules --detailed-exitcodes c:\\Windows\\Temp\\puppet\\manifests\\site.pp"
                        }
                    }
                }, 
                "infraLoad": {
                    "sources": {
                        "c:\\ProgramData\\PuppetLabs\\puppet\\etc": "https://testbucket.s3.amazonaws.com/artifacts/infrastructure/winhiera.tar.gz", 
                        "c:\\Windows\\Temp\\puppet": "https://testbucket.s3.amazonaws.com/artifacts/infrastructure/test/dev/zip.tgz"
                    }
                }, 
                "bootstrap": {
                    "files": {
                        "c:\\cfn\\hooks.d\\cfn-auto-reloader.conf": {
                            "content": {
                                "Fn::Join": [
                                    "", 
                                    [
                                        "[cfn-auto-reloader-hook]\n", 
                                        "triggers=post.update\n", 
                                        "path=Resources.LCtest.Metadata.AWS::CloudFormation::Init\n", 
                                        "action=cfn-init.exe -v -s ", 
                                        {
                                            "Ref": "AWS::StackId"
                                        }, 
                                        " -r LCtest -c infraUpdate", 
                                        " --region ", 
                                        {
                                            "Ref": "AWS::Region"
                                        }, 
                                        "\n"
                                    ]
                                ]
                            }
                        }, 
                        "c:\\ProgramData\\PuppetLabs\\facter\\facts.d\\localfacts.yaml": {
                            "content": {
                                "Fn::Join": [
                                    "", 
                                    [
                                        "ec2_stack: ", 
                                        {
                                            "Ref": "AWS::StackId"
                                        }, 
                                        "\n", 
                                        "ec2_region: ", 
                                        {
                                            "Ref": "AWS::Region"
                                        }, 
                                        "\n", 
                                        "ec2_resource: LCtest\n", 
                                        "app: test\n", 
                                        "stack: test\n", 
                                        "stage: dev\n", 
                                        "ec2_a: b\n", 
                                        "ec2_c: ", 
                                        {
                                            "Ref": "d"
                                        }, 
                                        "\n"
                                    ]
                                ]
                            }
                        }, 
                        "c:\\cfn\\cfn-hup.conf": {
                            "content": {
                                "Fn::Join": [
                                    "", 
                                    [
                                        "[main]\n", 
                                        "stack=", 
                                        {
                                            "Ref": "AWS::StackId"
                                        }, 
                                        "\n", 
                                        "region=", 
                                        {
                                            "Ref": "AWS::Region"
                                        }, 
                                        "\n",
                                        "interval=5\n"
                                    ]
                                ]
                            }
                        }
                    }, 
                    "packages": {
                        "msi": {
                            "puppet": "https://downloads.puppetlabs.com/windows/puppet-3.7.5-x64.msi"
                        }
                    }, 
                    "commands": {
                        "1-stop-puppet-service": {
                            "waitAfterCompletion": 0, 
                            "command": "sc stop puppet"
                        }, 
                        "2-disable-puppet-service": {
                            "waitAfterCompletion": 0, 
                            "command": "sc config puppet start= disabled"
                        }
                    }, 
                    "services": {
                        "windows": {
                            "cfn-hup": {
                                "enabled": "true", 
                                "ensureRunning": "true", 
                                "files": [
                                    "c:\\cfn\\cfn-hup.conf", 
                                    "c:\\cfn\\hooks.d\\cfn-auto-reloader.conf"
                                ]
                            }
                        }
                    }
                }
            }
        }

        data = WindowsPuppetProvisioner().cfn_init(args)
        data = json.loads(json.dumps(data, cls=awsencode))
        assert_equals(data, ci_data)

    @mock.patch('time.time', _mock_time)
    def test_ci_contains_expected_data_custom_facts(self):
        args = {
            'infrastructure': 'zip.tgz',
            'bucket': 'testbucket',
            'role': 'instance-blah',
            'name': 'test',
            'stackname': 'test',
            'appname': 'test',
            'resource': 'LCtest',
            'environment': 'dev',
            'custom_facts': {
                'a': 'b',
                'c': 'd',
            }
        }

        ci_data = {
            "AWS::CloudFormation::Authentication": {
                "rolebased": {
                    "buckets": [
                        "testbucket"
                    ], 
                    "roleName": "instance-blah", 
                    "type": "s3"
                }
            }, 
            "AWS::CloudFormation::Init": {
                "configSets": {
                    "infraUpdate": [
                        "infraLoad", 
                        "infraPuppetRun", 
                        "infraPuppetFinal"
                    ], 
                    "infra": [
                        "infraLoad", 
                        "infraPuppetRun"
                    ], 
                    "startup": [
                        "bootstrap", 
                        {
                            "ConfigSet": "infra"
                        }, 
                        {
                            "ConfigSet": "puppetFinal"
                        }
                    ], 
                    "puppetFinal": [
                        "infraPuppetFinal"
                    ]
                }, 
                "infraPuppetFinal": {
                    "commands": {
                        "01-run_puppet": {
                            "waitAfterCompletion": 0, 
                            "command": "\"c:\\Program Files\\Puppet Labs\\Puppet\\bin\\puppet.bat\" apply --modulepath c:\\Windows\\Temp\\puppet\\modules --detailed-exitcodes c:\\Windows\\Temp\\puppet\\manifests\\site.pp"
                        }, 
                        "02-clean_puppet": {
                            "waitAfterCompletion": 0, 
                            "command": "rmdir /S /Q c:\\Windows\\Temp\\puppet"
                        }
                    }
                }, 
                "infraPuppetRun": {
                    "commands": {
                        "01-run_puppet": {
                            "ignoreErrors": "true", 
                            "waitAfterCompletion": 0, 
                            "command": "\"c:\\Program Files\\Puppet Labs\\Puppet\\bin\\puppet.bat\" apply --modulepath c:\\Windows\\Temp\\puppet\\modules --environment first_run c:\\Windows\\Temp\\puppet\\manifests\\site.pp"
                        }
                    }
                }, 
                "bootstrap": {
                    "commands": {
                        "1-stop-puppet-service": {
                            "waitAfterCompletion": 0, 
                            "command": "sc stop puppet"
                        }, 
                        "2-disable-puppet-service": {
                            "waitAfterCompletion": 0, 
                            "command": "sc config puppet start= disabled"
                        }
                    }, 
                    "packages": {
                        "msi": {
                            "puppet": "https://downloads.puppetlabs.com/windows/puppet-3.7.5-x64.msi"
                        }
                    }, 
                    "files": {
                        "c:\\cfn\\cfn-hup.conf": {
                            "content": {
                                "Fn::Join": [
                                    "", 
                                    [
                                        "[main]\n", 
                                        "stack=", 
                                        {
                                            "Ref": "AWS::StackId"
                                        }, 
                                        "\n", 
                                        "region=", 
                                        {
                                            "Ref": "AWS::Region"
                                        }, 
                                        "\n",
                                        "interval=5\n"
                                    ]
                                ]
                            }
                        }, 
                        "c:\\cfn\\hooks.d\\cfn-auto-reloader.conf": {
                            "content": {
                                "Fn::Join": [
                                    "", 
                                    [
                                        "[cfn-auto-reloader-hook]\n", 
                                        "triggers=post.update\n", 
                                        "path=Resources.LCtest.Metadata.AWS::CloudFormation::Init\n", 
                                        "action=cfn-init.exe -v -s ", 
                                        {
                                            "Ref": "AWS::StackId"
                                        }, 
                                        " -r LCtest -c infraUpdate", 
                                        " --region ", 
                                        {
                                            "Ref": "AWS::Region"
                                        }, 
                                        "\n"
                                    ]
                                ]
                            }
                        }, 
                        "c:\\ProgramData\\PuppetLabs\\facter\\facts.d\\localfacts.yaml": {
                            "content": {
                                "Fn::Join": [
                                    "", 
                                    [
                                        "ec2_stack: ", 
                                        {
                                            "Ref": "AWS::StackId"
                                        }, 
                                        "\n", 
                                        "ec2_region: ", 
                                        {
                                            "Ref": "AWS::Region"
                                        }, 
                                        "\n", 
                                        "ec2_resource: LCtest\n", 
                                        "app: test\n", 
                                        "stack: test\n", 
                                        "stage: dev\n", 
                                        "ec2_a: b\n", 
                                        "ec2_c: d\n"
                                    ]
                                ]
                            }
                        }
                    }, 
                    "services": {
                        "windows": {
                            "cfn-hup": {
                                "ensureRunning": "true", 
                                "files": [
                                    "c:\\cfn\\cfn-hup.conf", 
                                    "c:\\cfn\\hooks.d\\cfn-auto-reloader.conf"
                                ], 
                                "enabled": "true"
                            }
                        }
                    }
                }, 
                "infraLoad": {
                    "sources": {
                        "c:\\Windows\\Temp\\puppet": "https://testbucket.s3.amazonaws.com/artifacts/infrastructure/test/dev/zip.tgz", 
                        "c:\\ProgramData\\PuppetLabs\\puppet\\etc": "https://testbucket.s3.amazonaws.com/artifacts/infrastructure/winhiera.tar.gz"
                    }
                }, 
                "trigger": {
                    "commands": {
                        "01-echo": {
                            "ignoreErrors": "true", 
                            "waitAfterCompletion": 0, 
                            "command": "echo 1000"
                        }
                    }
                }
            }
        }

        data = WindowsPuppetProvisioner().cfn_init(args)
        data = json.loads(json.dumps(data, cls=awsencode))
        assert_equals(data, ci_data)

    @mock.patch('time.time', _mock_time)
    def test_ci_contains_expected_data_eip(self):
        args = {
            'infrastructure': 'zip.tgz',
            'bucket': 'testbucket',
            'role': 'instance-blah',
            'name': 'test',
            'stackname': 'test',
            'appname': 'test',
            'resource': 'LCtest',
            'environment': 'dev',
            'eip': ['eip-1234', 'eip-2345']
        }

        ci_data = {
            "AWS::CloudFormation::Authentication": {
                "rolebased": {
                    "type": "s3", 
                    "buckets": [
                        "testbucket"
                    ], 
                    "roleName": "instance-blah"
                }
            }, 
            "AWS::CloudFormation::Init": {
                "infraLoad": {
                    "sources": {
                        "c:\\Windows\\Temp\\puppet": "https://testbucket.s3.amazonaws.com/artifacts/infrastructure/test/dev/zip.tgz", 
                        "c:\\ProgramData\\PuppetLabs\\puppet\\etc": "https://testbucket.s3.amazonaws.com/artifacts/infrastructure/winhiera.tar.gz"
                    }
                }, 
                "configSets": {
                    "startup": [
                        "bootstrap", 
                        {
                            "ConfigSet": "infra"
                        }, 
                        {
                            "ConfigSet": "puppetFinal"
                        }
                    ], 
                    "infra": [
                        "infraLoad", 
                        "infraPuppetRun"
                    ], 
                    "puppetFinal": [
                        "infraPuppetFinal"
                    ], 
                    "infraUpdate": [
                        "infraLoad", 
                        "infraPuppetRun", 
                        "infraPuppetFinal"
                    ]
                }, 
                "bootstrap": {
                    "commands": {
                        "2-disable-puppet-service": {
                            "command": "sc config puppet start= disabled", 
                            "waitAfterCompletion": 0
                        }, 
                        "1-stop-puppet-service": {
                            "command": "sc stop puppet", 
                            "waitAfterCompletion": 0
                        }
                    }, 
                    "packages": {
                        "msi": {
                            "puppet": "https://downloads.puppetlabs.com/windows/puppet-3.7.5-x64.msi"
                        }
                    }, 
                    "files": {
                        "c:\\cfn\\hooks.d\\cfn-auto-reloader.conf": {
                            "content": {
                                "Fn::Join": [
                                    "", 
                                    [
                                        "[cfn-auto-reloader-hook]\n", 
                                        "triggers=post.update\n", 
                                        "path=Resources.LCtest.Metadata.AWS::CloudFormation::Init\n", 
                                        "action=cfn-init.exe -v -s ", 
                                        {
                                            "Ref": "AWS::StackId"
                                        }, 
                                        " -r LCtest -c infraUpdate", 
                                        " --region ", 
                                        {
                                            "Ref": "AWS::Region"
                                        }, 
                                        "\n"
                                    ]
                                ]
                            }
                        }, 
                        "c:\\ProgramData\\PuppetLabs\\facter\\facts.d\\localfacts.yaml": {
                            "content": {
                                "Fn::Join": [
                                    "", 
                                    [
                                        "ec2_stack: ", 
                                        {
                                            "Ref": "AWS::StackId"
                                        }, 
                                        "\n", 
                                        "ec2_region: ", 
                                        {
                                            "Ref": "AWS::Region"
                                        }, 
                                        "\n", 
                                        "ec2_resource: LCtest\n", 
                                        "app: test\n", 
                                        "stack: test\n", 
                                        "stage: dev\n", 
                                        "ec2_elastic_ips: ", 
                                        {
                                            "Ref": "eip-1234"
                                        }, 
                                        ",", 
                                        {
                                            "Ref": "eip-2345"
                                        }, 
                                        "\n"
                                    ]
                                ]
                            }
                        }, 
                        "c:\\cfn\\cfn-hup.conf": {
                            "content": {
                                "Fn::Join": [
                                    "", 
                                    [
                                        "[main]\n", 
                                        "stack=", 
                                        {
                                            "Ref": "AWS::StackId"
                                        }, 
                                        "\n", 
                                        "region=", 
                                        {
                                            "Ref": "AWS::Region"
                                        }, 
                                        "\n",
                                        "interval=5\n"
                                    ]
                                ]
                            }
                        }
                    }, 
                    "services": {
                        "windows": {
                            "cfn-hup": {
                                "enabled": "true", 
                                "files": [
                                    "c:\\cfn\\cfn-hup.conf", 
                                    "c:\\cfn\\hooks.d\\cfn-auto-reloader.conf"
                                ], 
                                "ensureRunning": "true"
                            }
                        }
                    }
                }, 
                "infraPuppetFinal": {
                    "commands": {
                        "02-clean_puppet": {
                            "command": "rmdir /S /Q c:\\Windows\\Temp\\puppet", 
                            "waitAfterCompletion": 0
                        }, 
                        "01-run_puppet": {
                            "waitAfterCompletion": 0, 
                            "command": "\"c:\\Program Files\\Puppet Labs\\Puppet\\bin\\puppet.bat\" apply --modulepath c:\\Windows\\Temp\\puppet\\modules --detailed-exitcodes c:\\Windows\\Temp\\puppet\\manifests\\site.pp"
                        }
                    }
                }, 
                "trigger": {
                    "commands": {
                        "01-echo": {
                            "command": "echo 1000", 
                            "waitAfterCompletion": 0, 
                            "ignoreErrors": "true"
                        }
                    }
                }, 
                "infraPuppetRun": {
                    "commands": {
                        "01-run_puppet": {
                            "command": "\"c:\\Program Files\\Puppet Labs\\Puppet\\bin\\puppet.bat\" apply --modulepath c:\\Windows\\Temp\\puppet\\modules --environment first_run c:\\Windows\\Temp\\puppet\\manifests\\site.pp", 
                            "waitAfterCompletion": 0, 
                            "ignoreErrors": "true"
                        }
                    }
                }
            }
        }

        data = WindowsPuppetProvisioner().cfn_init(args)
        data = json.loads(json.dumps(data, cls=awsencode))
        assert_equals(data, ci_data)

    @mock.patch('time.time', _mock_time)
    def test_ci_contains_expected_data_find_nodes(self):
        args = {
            'infrastructure': 'zip.tgz',
            'bucket': 'testbucket',
            'role': 'instance-blah',
            'name': 'test',
            'stackname': 'test',
            'appname': 'test',
            'resource': 'LCtest',
            'environment': 'dev',
            'find_nodes': 'true',
        }

        ci_data = {
            "AWS::CloudFormation::Authentication": {
                "rolebased": {
                    "type": "s3", 
                    "roleName": "instance-blah", 
                    "buckets": [
                        "testbucket"
                    ]
                }
            }, 
            "AWS::CloudFormation::Init": {
                "infraPuppetRun": {
                    "commands": {
                        "01-run_puppet": {
                            "command": "\"c:\\Program Files\\Puppet Labs\\Puppet\\bin\\puppet.bat\" apply --modulepath c:\\Windows\\Temp\\puppet\\modules --environment first_run c:\\Windows\\Temp\\puppet\\manifests\\site.pp", 
                            "waitAfterCompletion": 0, 
                            "ignoreErrors": "true"
                        }
                    }
                }, 
                "bootstrap": {
                    "commands": {
                        "1-stop-puppet-service": {
                            "command": "sc stop puppet", 
                            "waitAfterCompletion": 0
                        }, 
                        "2-disable-puppet-service": {
                            "command": "sc config puppet start= disabled", 
                            "waitAfterCompletion": 0
                        }
                    }, 
                    "services": {
                        "windows": {
                            "cfn-hup": {
                                "enabled": "true", 
                                "files": [
                                    "c:\\cfn\\cfn-hup.conf", 
                                    "c:\\cfn\\hooks.d\\cfn-auto-reloader.conf"
                                ], 
                                "ensureRunning": "true"
                            }
                        }
                    }, 
                    "packages": {
                        "msi": {
                            "puppet": "https://downloads.puppetlabs.com/windows/puppet-3.7.5-x64.msi"
                        }
                    }, 
                    "files": {
                        "c:\\ProgramData\\PuppetLabs\\facter\\facts.d\\localfacts.yaml": {
                            "content": {
                                "Fn::Join": [
                                    "", 
                                    [
                                        "ec2_stack: ", 
                                        {
                                            "Ref": "AWS::StackId"
                                        }, 
                                        "\n", 
                                        "ec2_region: ", 
                                        {
                                            "Ref": "AWS::Region"
                                        }, 
                                        "\n", 
                                        "ec2_resource: LCtest\n", 
                                        "app: test\n", 
                                        "stack: test\n", 
                                        "stage: dev\n"
                                    ]
                                ]
                            }
                        }, 
                        "c:\\cfn\\hooks.d\\cfn-auto-reloader.conf": {
                            "content": {
                                "Fn::Join": [
                                    "", 
                                    [
                                        "[cfn-auto-reloader-hook]\n", 
                                        "triggers=post.update\n", 
                                        "path=Resources.LCtest.Metadata.AWS::CloudFormation::Init\n", 
                                        "action=cfn-init.exe -v -s ", 
                                        {
                                            "Ref": "AWS::StackId"
                                        }, 
                                        " -r LCtest -c infraUpdate", 
                                        " --region ", 
                                        {
                                            "Ref": "AWS::Region"
                                        }, 
                                        "\n"
                                    ]
                                ]
                            }
                        }, 
                        "c:\\cfn\\cfn-hup.conf": {
                            "content": {
                                "Fn::Join": [
                                    "", 
                                    [
                                        "[main]\n", 
                                        "stack=", 
                                        {
                                            "Ref": "AWS::StackId"
                                        }, 
                                        "\n", 
                                        "region=", 
                                        {
                                            "Ref": "AWS::Region"
                                        }, 
                                        "\n",
                                        "interval=5\n"
                                    ]
                                ]
                            }
                        }
                    }
                }, 
                "infraLoad": {
                    "sources": {
                        "c:\\ProgramData\\PuppetLabs\\puppet\\etc": "https://testbucket.s3.amazonaws.com/artifacts/infrastructure/winhiera.tar.gz", 
                        "c:\\Windows\\Temp\\puppet": "https://testbucket.s3.amazonaws.com/artifacts/infrastructure/test/dev/zip.tgz"
                    }
                }, 
                "infraPuppetFinal": {
                    "commands": {
                        "02-clean_puppet": {
                            "command": "rmdir /S /Q c:\\Windows\\Temp\\puppet", 
                            "waitAfterCompletion": 0
                        }, 
                        "01-run_puppet": {
                            "waitAfterCompletion": 0, 
                            "command": "\"c:\\Program Files\\Puppet Labs\\Puppet\\bin\\puppet.bat\" apply --modulepath c:\\Windows\\Temp\\puppet\\modules --detailed-exitcodes c:\\Windows\\Temp\\puppet\\manifests\\site.pp"
                        }
                    }
                }, 
                "configSets": {
                    "puppetFinal": [
                        "infraPuppetFinal"
                    ], 
                    "startup": [
                        "bootstrap", 
                        {
                            "ConfigSet": "infra"
                        }, 
                        {
                            "ConfigSet": "puppetFinal"
                        }
                    ], 
                    "infra": [
                        "infraLoad", 
                        "infraPuppetRun"
                    ], 
                    "infraUpdate": [
                        "infraLoad", 
                        "infraPuppetRun", 
                        "infraPuppetFinal"
                    ]
                }, 
                "trigger": {
                    "commands": {
                        "01-echo": {
                            "command": "echo 1000", 
                            "waitAfterCompletion": 0, 
                            "ignoreErrors": "true"
                        }
                    }
                }
            }
        }

        data = WindowsPuppetProvisioner().cfn_init(args)
        data = json.loads(json.dumps(data, cls=awsencode))
        assert_equals(data, ci_data)

    @mock.patch('time.time', _mock_time)
    def test_ci_contains_expected_data(self):
        args = {
            'infrastructure': 'zip.tgz',
            'application': 'bar.zip',
            'bucket': 'testbucket',
            'role': 'instance-blah',
            'name': 'test',
            'stackname': 'test',
            'appname': 'test',
            'resource': 'LCtest',
            'environment': 'dev',
        }

        ci_data = {
            "AWS::CloudFormation::Authentication": {
                "rolebased": {
                    "type": "s3", 
                    "buckets": [
                        "testbucket"
                    ], 
                    "roleName": "instance-blah"
                }
            }, 
            "AWS::CloudFormation::Init": {
                "configSets": {
                    "infraUpdate": [
                        "infraLoad", 
                        "infraPuppetRun", 
                        "infraPuppetFinal"
                    ], 
                    "infra": [
                        "infraLoad", 
                        "infraPuppetRun"
                    ], 
                    "startup": [
                        "bootstrap", 
                        {
                            "ConfigSet": "infra"
                        }, 
                        {
                            "ConfigSet": "app"
                        }, 
                        {
                            "ConfigSet": "puppetFinal"
                        }
                    ], 
                    "puppetFinal": [
                        "infraPuppetFinal"
                    ], 
                    "app": [
                        "deployRun"
                    ]
                }, 
                "infraPuppetRun": {
                    "commands": {
                        "01-run_puppet": {
                            "command": "\"c:\\Program Files\\Puppet Labs\\Puppet\\bin\\puppet.bat\" apply --modulepath c:\\Windows\\Temp\\puppet\\modules --environment first_run c:\\Windows\\Temp\\puppet\\manifests\\site.pp", 
                            "waitAfterCompletion": 0, 
                            "ignoreErrors": "true"
                        }
                    }
                }, 
                "deployRun": {
                    "commands": {
                        "01-run_deploy": {
                            "waitAfterCompletion": 0, 
                            "command": "powershell -NoProfile -NonInteractive -NoLogo -ExecutionPolicy Bypass -Command c:\Piksel\msdeploy.ps1 -service test -stage dev -artifact bar.zip"
                        }
                    }
                }, 
                "infraLoad": {
                    "sources": {
                        "c:\\ProgramData\\PuppetLabs\\puppet\\etc": "https://testbucket.s3.amazonaws.com/artifacts/infrastructure/winhiera.tar.gz", 
                        "c:\\Windows\\Temp\\puppet": "https://testbucket.s3.amazonaws.com/artifacts/infrastructure/test/dev/zip.tgz"
                    }
                }, 
                "trigger": {
                    "commands": {
                        "01-echo": {
                            "waitAfterCompletion": 0, 
                            "command": "echo 1000", 
                            "ignoreErrors": "true"
                        }
                    }
                }, 
                "infraPuppetFinal": {
                    "commands": {
                        "02-clean_puppet": {
                            "waitAfterCompletion": 0, 
                            "command": "rmdir /S /Q c:\\Windows\\Temp\\puppet"
                        }, 
                        "01-run_puppet": {
                            "waitAfterCompletion": 0, 
                            "command": "\"c:\\Program Files\\Puppet Labs\\Puppet\\bin\\puppet.bat\" apply --modulepath c:\\Windows\\Temp\\puppet\\modules --detailed-exitcodes c:\\Windows\\Temp\\puppet\\manifests\\site.pp"
                        }
                    }
                }, 
                "bootstrap": {
                    "files": {
                        "c:\\cfn\\hooks.d\\cfn-auto-reloader.conf": {
                            "content": {
                                "Fn::Join": [
                                    "", 
                                    [
                                        "[cfn-auto-reloader-hook]\n", 
                                        "triggers=post.update\n", 
                                        "path=Resources.LCtest.Metadata.AWS::CloudFormation::Init\n", 
                                        "action=cfn-init.exe -v -s ", 
                                        {
                                            "Ref": "AWS::StackId"
                                        }, 
                                        " -r LCtest -c infraUpdate", 
                                        " --region ", 
                                        {
                                            "Ref": "AWS::Region"
                                        }, 
                                        "\n"
                                    ]
                                ]
                            }
                        }, 
                        "c:\\ProgramData\\PuppetLabs\\facter\\facts.d\\localfacts.yaml": {
                            "content": {
                                "Fn::Join": [
                                    "", 
                                    [
                                        "ec2_stack: ", 
                                        {
                                            "Ref": "AWS::StackId"
                                        }, 
                                        "\n", 
                                        "ec2_region: ", 
                                        {
                                            "Ref": "AWS::Region"
                                        }, 
                                        "\n", 
                                        "ec2_resource: LCtest\n", 
                                        "app: test\n", 
                                        "stack: test\n", 
                                        "stage: dev\n"
                                    ]
                                ]
                            }
                        }, 
                        "c:\\cfn\\cfn-hup.conf": {
                            "content": {
                                "Fn::Join": [
                                    "", 
                                    [
                                        "[main]\n", 
                                        "stack=", 
                                        {
                                            "Ref": "AWS::StackId"
                                        }, 
                                        "\n", 
                                        "region=", 
                                        {
                                            "Ref": "AWS::Region"
                                        }, 
                                        "\n",
                                        "interval=5\n"
                                    ]
                                ]
                            }
                        }
                    }, 
                    "commands": {
                        "1-stop-puppet-service": {
                            "waitAfterCompletion": 0, 
                            "command": "sc stop puppet"
                        }, 
                        "2-disable-puppet-service": {
                            "waitAfterCompletion": 0, 
                            "command": "sc config puppet start= disabled"
                        }
                    }, 
                    "packages": {
                        "msi": {
                            "puppet": "https://downloads.puppetlabs.com/windows/puppet-3.7.5-x64.msi"
                        }
                    }, 
                    "services": {
                        "windows": {
                            "cfn-hup": {
                                "enabled": "true", 
                                "ensureRunning": "true", 
                                "files": [
                                    "c:\\cfn\\cfn-hup.conf", 
                                    "c:\\cfn\\hooks.d\\cfn-auto-reloader.conf"
                                ]
                            }
                        }
                    }
                }
            }
        }

        data = WindowsPuppetProvisioner().cfn_init(args)
        data = json.loads(json.dumps(data, cls=awsencode))
        assert_equals(data, ci_data)

    def test_provisioner_policy_contains_expected_data(self):
        args = {
            'infrastructure': 'zip.tgz',
            'application': 'bar.zip',
            'bucket': 'testbucket',
            'role': 'instance-blah',
            'name': 'test',
            'stackname': 'test',
            'appname': 'test',
            'resource': 'LCtest',
            'environment': 'dev',
        }
        base = "arn:aws:s3:::%s/artifacts" % args['bucket']
        pp_data = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "s3:GetObject"
                    ],
                    "Resource": [
                        "%s/infrastructure/test/dev/zip.tgz" % base,
                        "%s/infrastructure/winhiera.tar.gz" % base,
                        "%s/application/test/dev/bar.zip" % base
                    ]
                }
            ]
        }
        data = WindowsPuppetProvisioner().provisioner_policy(args)
        assert_equals(data, pp_data)

    def test_provisioner_policy_contains_expected_data_metrics(self):
        args = {
            'bucket': 'testbucket',
            'role': 'instance-blah',
            'name': 'test',
            'stackname': 'test',
            'appname': 'test',
            'resource': 'LCtest',
            'environment': 'dev',
            'metrics': 'true'
        }
        pp_data = {
            'Version': '2012-10-17',
            'Statement': [
                {
                    'Action': ['cloudwatch:PutMetricData'],
                    'Effect': 'Allow',
                    'Resource': '*'
                }
            ]
        }
        data = WindowsPuppetProvisioner().provisioner_policy(args)
        assert_equals(data, pp_data)

    def test_provisioner_policy_contains_expected_data_find_nodes(self):
        args = {
            'bucket': 'testbucket',
            'role': 'instance-blah',
            'name': 'test',
            'stackname': 'test',
            'appname': 'test',
            'resource': 'LCtest',
            'environment': 'dev',
            'find_nodes': 'true'
        }
        pp_data = {
            'Version': '2012-10-17',
            'Statement': [
                {
                    'Action': ['ec2:DescribeInstances'],
                    'Effect': 'Allow',
                    'Resource': '*'
                }
            ]
        }
        data = WindowsPuppetProvisioner().provisioner_policy(args)
        assert_equals(data, pp_data)

    def test_provisioner_policy_contains_expected_data_no_artifacts(self):
        args = {
            'bucket': 'testbucket',
            'role': 'instance-blah',
            'name': 'test',
            'stackname': 'test',
            'resource': 'LCtest',
            'environment': 'dev',
        }
        data = WindowsPuppetProvisioner().provisioner_policy(args)
        assert_equals(data, None)

    def test_provisioner_policy_contains_expected_data_eip(self):
        pp_data = {
            'Version': '2012-10-17',
            'Statement': [
                {
                    'Resource': '*',
                    'Action': [
                        'ec2:AssociateAddress',
                        'ec2:DescribeAddresses'
                    ],
                    'Effect': 'Allow'
                }
            ]
        }
        args = {
            'bucket': 'testbucket',
            'role': 'instance-blah',
            'name': 'test',
            'appname': 'test',
            'stackname': 'test',
            'resource': 'LCtest',
            'environment': 'dev',
            'eip': ['a', 'b'],
        }
        data = WindowsPuppetProvisioner().provisioner_policy(args)
        assert_equals(data, pp_data)
