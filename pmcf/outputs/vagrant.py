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
..  module:: pmcf.outputs.vagrant
    :platform: Unix
    :synopsis: module containing Vagrant class for output

..  moduleauthor:: Stephen Gran <stephen.gran@piksel.com>
"""
import json
import logging

from pmcf.exceptions import ProvisionerException
from pmcf.outputs.base_output import BaseOutput

LOG = logging.getLogger(__name__)


class VagrantOutput(BaseOutput):
    def add_resources(self, resources, config):
        """
        Creates a Vagrantfile from stripped-down stack definition.

        :param resources: Internal data structure of resources
        :type resources: dict.
        :param config: Config key/value pairs
        :type config: dict.
        :returns: string
        :raises: :class:`pmcf.exceptions.ProvisionerException`
        """

        LOG.info('Start building Vagrantfile')
        net = config.get('vagrant_net', '10.0.5')
        last_octet = 2

        vagrantfile = """
# -*- mode: ruby -*-
# vi: set ft=ruby :

VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box = "trusty"
  config.vm.box_url = "https://cloud-images.ubuntu.com/vagrant/%s/%s"

""" % ("trusty/current", "trusty-server-cloudimg-amd64-vagrant-disk1.box")

        inst_block = []
        for inst in resources['instance']:
            last_octet += 1
            try:
                inst_block.append({
                    'name': '%s' % inst['name'],
                    'ip': '%s.%s' % (net, last_octet),
                    'tags': {
                        'app': inst['name'],
                        'stack': config['name'],
                        'stage': 'dev',
                        'vagrant_net': net
                    }
                })
            except KeyError, e:
                raise ProvisionerException("Missing field %s" % str(e))
        vagrantfile += "  instances = '%s'" % json.dumps(inst_block,
                                                         sort_keys=True)
        vagrantfile += """

  JSON.load(instances).each do |instance|
    config.vm.define instance['name'] do |app|
      app.vm.hostname = instance['name']
      app.vm.network :private_network, ip: instance['ip']
      app.vm.provision :puppet do |puppet|
        puppet.manifests_path = 'puppet/manifests'
        puppet.manifest_file = 'site.pp'
        puppet.module_path = 'puppet/modules'
        puppet.facter = instance['tags']
        puppet.hiera_config_path = 'puppet/hiera.yaml'
        puppet.working_directory = '/vagrant/puppet'
      end
    end
  end
end
"""

        LOG.info('Finished building Vagrantfile')
        return vagrantfile

    def run(self, data, metadata={}, poll=False,
            action='create', upload=False):
        """
        Outputs a vagrantfile of the stack definition

        :param data: Stack definition
        :type data: str.
        :param metadata: Additional information for stack launch (tags, etc).
        :type metadata: dict.
        :param poll: Whether to poll until completion
        :type poll: boolean.
        :param action: Action to take on the stack
        :type action: str.
        :param upload: Whether to upload stack definition to s3 before launch
        :type upload: bool.
        :returns: boolean
        """

        LOG.info('Start running data')
        print data
        LOG.info('Finished running data')
        self.do_audit(data, metadata)
        return True

    def do_audit(self, data, metadata={}):
        """
        Records audit logs for current transaction

        :param data: Stack definition
        :type data: str.
        :param metadata: Additional information for stack launch (tags, etc).
        :type metadata: dict.
        """

        pass


__all__ = [
    VagrantOutput,
]
