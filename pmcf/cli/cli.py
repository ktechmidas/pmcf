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
import logging

from pmcf.exceptions import PMCFException
from pmcf.utils import import_from_string


def main():
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
    parser.add_argument("-C", "--configreader",
                        default='PMCFConfig',
                        help="use alternate config reader")
    parser.add_argument("-r", "--runner",
                        default='PMCFCLI',
                        help="use alternate CLI implementation")
    parser.add_argument("-s", "--stage",
                        default='dev',
                        help="run config for this stage")
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

    # Log everything, and send it to stderr.
    FORMAT = "[%(asctime)-15s] [%(levelname)s] %(message)s"

    # Simple coloured output
    logging.addLevelName(logging.DEBUG,
                         "\033[1;32m %s \033[1;m"
                         % logging.getLevelName(logging.DEBUG))
    logging.addLevelName(logging.INFO,
                         "\033[1;36m %s  \033[1;m"
                         % logging.getLevelName(logging.INFO))
    logging.addLevelName(logging.WARNING,
                         "\033[1;33m%s\033[1;m"
                         % logging.getLevelName(logging.WARNING))
    logging.addLevelName(logging.ERROR,
                         "\033[1;31m %s \033[1;m"
                         % logging.getLevelName(logging.ERROR))

    if args.debug:
        lvl = logging.DEBUG
    elif args.verbose:
        lvl = logging.INFO
    elif args.quiet:
        lvl = logging.ERROR
    else:
        lvl = logging.WARNING

    logging.basicConfig(format=FORMAT, level=lvl)

    LOG = logging.getLogger(__name__)

    try:
        cfgkls = import_from_string('pmcf.config', args.configreader)
        cfg = cfgkls(args.configfile, args.profile, args)
        options = cfg.get_config()

        clikls = import_from_string('pmcf.cli', args.runner)
        cli = clikls(options)
        return cli.run()
    except PMCFException, e:
        LOG.error(e.message)
        return True

if __name__ == '__main__':
    main()
