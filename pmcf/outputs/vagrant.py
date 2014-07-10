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
        vagrantfile = """
# -*- mode: ruby -*-
# vi: set ft=ruby :

VAGRANTFILE_API_VERSION = "2"

base_ip = "10.0.5."
iter = 0

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box = "trusty"
  config.vm.box_url = "https://cloud-images.ubuntu.com/vagrant/%s/%s"

""" % ("trusty/20140428", "trusty-server-cloudimg-amd64-vagrant-disk1.box")

        instance_template = """
  tags = {
    "app"   => "%s",
    "stack" => "%s",
    "stage" => "dev",
  }
  config.vm.define "%s" do |app|
    iter += 2
    app.vm.hostname = "%s"
    app.vm.network :private_network, ip: base_ip + "#{iter}"
    app.vm.provision :puppet do |puppet|
      puppet.manifests_path = 'puppet/manifests'
      puppet.manifest_file = 'site.pp'
      puppet.module_path = 'puppet/modules'
      puppet.facter = tags
    end
  end

"""
        for inst in resources['instance']:
            try:
                vagrantfile += instance_template % (
                    inst['name'],
                    config['name'],
                    inst['name'],
                    inst['name']
                )
            except KeyError, e:
                raise ProvisionerException("Missing field %s" % str(e))

        vagrantfile += "end"
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
