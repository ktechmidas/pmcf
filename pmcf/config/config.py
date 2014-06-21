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

"""
..  module:: pmcf.config.config
    :platform: Unix
    :synopsis: module containing config class

..  moduleauthor:: Stephen Gran <stephen.gran@piksel.com>
"""

import ConfigParser
import logging

LOG = logging.getLogger(__name__)


class PMCFConfig(object):
    """
    Config class responsible to assemble config from files, defaults and
    command line arguments.
    """

    def __init__(self, configfile, profile_name, args):
        """
        Constructor

        :param configfile: Path to configuration file
        :type configfile: str.
        :param profile_name: Profile in configuration file
        :type profile_name: str.
        :param args: command line arguments
        :type args: dict.
        """

        self.cfg = ConfigParser.ConfigParser()
        self.configfile = configfile
        self.profile_name = profile_name
        self.args = args

        if self.profile_name != 'default':
            self.profile_name = "profile " + profile_name

        self.options = {
            'action': 'create',
            'audit': 'NoopAudit',
            'audit_output': None,
            'output': 'BaseOutput',
            'parser': 'BaseParser',
            'policy': 'BasePolicy',
            'provisioner': 'BaseProvisioner',
            'verbose': None,
            'debug': None,
            'poll': False,
            'quiet': None,
            'policyfile': None,
            'stackfile': None,
            'accesskey': None,
            'secretkey': None,
            'instance_accesskey': None,
            'instance_secretkey': None,
            'region': None,
            'environment': None,
        }

    def get_config(self):
        """
        Returns configuration in dictionary form.

        :returns:  dictionary
        """

        self.cfg.read(self.configfile)

        if self.profile_name not in self.cfg.sections():
            raise ValueError('bad profile %s' % self.profile_name)

        default_options = {}
        profile_options = {}
        cli_options = {}
        options = {}

        for opt in self.options.keys():
            default_options[opt] = self._get_from_section(
                'default', opt) or self.options[opt]
            profile_options[opt] = self._get_from_section(self.profile_name,
                                                          opt) or None
            cli_options[opt] = getattr(self.args, opt, None) or None

            if profile_options[opt] is None:
                profile_options.pop(opt, None)
            if cli_options[opt] is None:
                cli_options.pop(opt, None)

        options.update(default_options)
        options.update(profile_options)
        options.update(cli_options)

        return options

    def _get_from_section(self, section, option):
        """
        Reads option out of section of ini file

        :param section: Section of ini file to look for option.
        :type section: str.
        :param option: Option name to search for.
        :type option: str.
        :returns: string or None
        """
        val = None
        try:
            val = self.cfg.get(section, option)
        except ConfigParser.NoOptionError:
            pass
        return val


__all__ = [
    PMCFConfig,
]
