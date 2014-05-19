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

import argparse
import ConfigParser

from pmcf.cli.cmd import PMCFCLI


def main():
    cfg = ConfigParser.ConfigParser()
    parser = argparse.ArgumentParser()
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument("-v", "--verbose",
                              help="set loglevel to verbose",
                              default=False,
                              action="store_true")
    output_group.add_argument("-d", "--debug",
                              help="set loglevel to debug",
                              default=False,
                              action="store_true")
    output_group.add_argument("-q", "--quiet",
                              help="set loglevel to quiet",
                              default=False,
                              action="store_true")
    parser.add_argument("-p", "--profile",
                        default='default',
                        help="use config profile")
    parser.add_argument("-P", "--policyfile",
                        default='/etc/pmcf/policy.json',
                        help="alternate policy file")
    parser.add_argument("-c", "--configfile",
                        default='/etc/pmcf/pmcf.conf',
                        help="alternate config file")
    parser.add_argument("-a", "--action",
                        default='create',
                        help="action (one of create, update, or delete)")
    parser.add_argument("stackfile",
                        help="path to stack (farm) definition file")
    args = parser.parse_args()
    cfg.read(args.configfile)

    profile_name = args.profile
    if profile_name != 'default':
        profile_name = "profile " + args.profile
    if profile_name not in cfg.sections():
        raise ValueError('bad profile %s' % args.profile)

    options = {
        'output': 'AWSCFNOutput',
        'parser': 'AWSFWParser',
        'policy': 'BasePolicy',
        'provisioner': 'AWSFWProvisioner',
        'verbose': args.verbose,
        'debug': args.debug,
        'quiet': args.quiet,
        'policyfile': args.policyfile,
        'stackfile': args.stackfile,
    }

    def get_from_section(cfg, section, option):
        val = None
        try:
            val = cfg.get(section, option)
            if val == -1:
                val = None
        except ConfigParser.NoOptionError:
            pass
        return val

    for opt in options.keys():
        options[opt] = get_from_section(cfg, profile_name, opt) or \
            get_from_section(cfg, 'default', opt) or \
            options[opt]

    for opt in ['region', 'aws_access_key_id', 'aws_secret_access_key']:
        options[opt] = get_from_section(cfg, profile_name, opt) or \
            get_from_section(cfg, 'default', opt)

    foo = PMCFCLI(options)
    foo._run()

if __name__ == '__main__':
    main()
