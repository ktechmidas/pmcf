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

import ConfigParser

import logging

LOG = logging.getLogger(__name__)


class PMCFConfig(object):
    def __init__(self, configfile, profile_name, args):
        self.cfg = ConfigParser.ConfigParser()
        self.configfile = configfile
        self.profile_name = profile_name
        self.args = args

        if self.profile_name != 'default':
            self.profile_name = "profile " + profile_name

        self.options = {
            'output': 'BaseOutput',
            'parser': 'BaseParser',
            'policy': 'BasePolicy',
            'provisioner': 'BaseProvisioner',
            'verbose': None,
            'debug': None,
            'quiet': None,
            'policyfile': None,
            'stackfile': None,
            'accesskey': None,
            'secretkey': None,
            'region': None,
        }

    def get_config(self):
        self.cfg.read(self.configfile)

        if self.profile_name not in self.cfg.sections():
            raise ValueError('bad profile %s' % self.profile_name)

        default_options = {}
        profile_options = {}
        cli_options = {}
        options = {}

        for opt in self.options.keys():
            default_options[opt] = self.get_from_section(
                'default', opt) or self.options[opt]
            profile_options[opt] = self.get_from_section(self.profile_name,
                                                         opt) or None
            cli_options[opt] = getattr(self.args, opt, None) or None

            if profile_options[opt] is None:
                profile_options.pop(opt, None)
            if cli_options[opt] is None:
                cli_options.pop(opt, None)

        options.update(default_options)
        options.update(profile_options)
        options.update(cli_options)
        for opt in self.options.keys():
            if options.get(opt, 'missing') == 'missing':
                options[opt] = None

        return options

    def get_from_section(self, section, option):
        val = None
        try:
            val = self.cfg.get(section, option)
            if val == -1:
                val = None
        except ConfigParser.NoOptionError:
            pass
        return val

__all__ = [
    PMCFConfig,
]
