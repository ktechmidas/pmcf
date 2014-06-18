..
      Copyright 2014 Piksel Ltd.

      Licensed under the Apache License, Version 2.0 (the "License"); you may
      not use this file except in compliance with the License. You may obtain
      a copy of the License at

          http://www.apache.org/licenses/LICENSE-2.0

      Unless required by applicable law or agreed to in writing, software
      distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
      WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
      License for the specific language governing permissions and limitations
      under the License.

.. _extending:

Modifying behaviour with subclasses
===================================

PMCF has been written with modification in mind.  Modifications that cannot be
made at the configuration level can be made by creation of new subclasses.

The process flow for stack creation is:

* Parser.parse_file()

* Policy.validate_resource()

* Parser.validate()

* Output.add_resources()

* Output.run()

* Audit.do_audit()


during Output.add_resources(), calls are additionally made to
Provisioner.userdata() and Provisioner.cfn_init().

Each of the modules audit, output, parser, policy and provisioner have been
written with an abstract base class that defines the interface, and one or
more implementation classes that are subclasses of that abstract base class.

If you need to modify behavior slightly, for instance, applying a local
tagging policy, it should be enough to subclass one of the implementation
classes.   If you need a more fundamental change in behavior, subclassing the
abstract base class and starting fresh will let you do what you want.

A good example of slight modifications in behaviour are the classes
:class:`pmcf.outputs.c4cloudformation.C4AWSCFNOutput` and
:class:`pmcf.outputs.sequoiacloudformation.SequoiaAWSCFNOutput`.  A good
example of radical changes in behavior are the classes
:class:`pmcf.provisioners.puppet.PuppetProvisioner` and
:class:`pmcf.provisioners.awsfw.AWSFWProvisioner`.
