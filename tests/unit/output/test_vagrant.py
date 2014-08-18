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
from pmcf.outputs import VagrantOutput


class TestVagrantOutput(object):

    def test_add_resources_no_stack_name_raises(self):
        md = {}
        data = {
            'instance': [{
                'name': 'test'
            }]
        }
        vgtout = VagrantOutput()
        assert_raises(ProvisionerException, vgtout.add_resources, data, md)

    def test_add_resources_no_instance_name_raises(self):
        md = {
            'name': 'dev',
        }
        data = {
            'instance': [{}]
        }
        vgtout = VagrantOutput()
        assert_raises(ProvisionerException, vgtout.add_resources, data, md)

    def test_dev_add_resources_succeeds(self):
        md = {
            'name': 'test',
        }
        data = {
            'instance': [{
                'name': 'test'
            }]
        }
        should = """
# -*- mode: ruby -*-
# vi: set ft=ruby :

VAGRANTFILE_API_VERSION = "2"

base_ip = "10.0.5."
iter = 0

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box = "trusty"
  config.vm.box_url = "https://cloud-images.ubuntu.com/vagrant/%s/%s"


  tags = {
    "app"   => "test",
    "stack" => "test",
    "stage" => "dev",
  }
  config.vm.define "test" do |app|
    iter += 2
    app.vm.hostname = "test"
    app.vm.network :private_network, ip: base_ip + "#{iter}"
    app.vm.provision :puppet do |puppet|
      puppet.manifests_path = 'puppet/manifests'
      puppet.manifest_file = 'site.pp'
      puppet.module_path = 'puppet/modules'
      puppet.facter = tags
    end
  end

end""" % (
            "trusty/current",
            "trusty-server-cloudimg-amd64-vagrant-disk1.box"
        )
        ret = VagrantOutput().add_resources(data, md)
        print ret
        assert_equals(ret, should)

    def test_run_succeeds(self):
        assert_equals(VagrantOutput().run(''), True)

    def test_do_audit_does_nothing(self):
        assert_equals(VagrantOutput().do_audit(''), None)
