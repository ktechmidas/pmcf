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
..  module:: pmcf.provisioners
    :platform: Unix
    :synopsis: module containing provisioner classes

..  moduleauthor:: Stephen Gran <stephen.gran@piksel.com>
"""

from pmcf.provisioners.awsfw import AWSFWProvisioner
from pmcf.provisioners.base_provisioner import BaseProvisioner
from pmcf.provisioners.block import BlockingProvisioner
from pmcf.provisioners.ansible import AnsibleProvisioner
from pmcf.provisioners.chef import ChefProvisioner
from pmcf.provisioners.noop import NoopProvisioner
from pmcf.provisioners.puppet import PuppetProvisioner
from pmcf.provisioners.winpuppet import WindowsPuppetProvisioner

__all__ = [
    'AWSFWProvisioner',
    'BaseProvisioner',
    'BlockingProvisioner',
    'AnsibleProvisioner',
    'ChefProvisioner',
    'NoopProvisioner',
    'PuppetProvisioner',
    'WindowsPuppetProvisioner',
]
