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

Instance Schema
===============

The schema for instances is, like the other parts of the schema,
composed from smaller building blocks to make a larger whole.

The required fields for an instance are:

:count:
        Number of instances to be created (will be created in an autoscaling
        group)

:image:
        AMI image id to use for the instances

:monitoring:
        Specifies whether monitoring is enabled for the instance

:name:
        Name of the instance (name of the autoscaling group).

:provisioner:
        One of PuppetProvisioner or AWSFWProvisioner.  Configuration
        management system to use

:sg:
        Security groups to use for the instance

:sshKey:
        SSH key to use

:size:
        One of the AWS sizes, eg, t2.micro, m3.medium, etc

Optional fields that can also be used:

:block_device:
        A list of block devices that should be created and attached to the
        instances

:lb:
        A list of names of loadbalancers

:min:
        For dynamically scaling groups, specifying min and max will allow
        finer grained control of autoscaling behavior.  These fields default
        to the value of count if ommitted.

:max:
        For dynamically scaling groups, specifying min and max will allow
        finer grained control of autoscaling behavior.  These fields default
        to the value of count if ommitted.

:notify:
        Topic name for notification of scaling events.

:zones:
        A list of availability zones to launch instances in.  Defaults to all
        availability zones in the region.

A block device entry is composed of the following fields:

:size:
        The size in GB of the disk device
:device:
        The device name in the instance

Provisioners are one of PuppetProvisioner, AWSFWProvisioner, or NoopProvisioner
and they each take different arguments.

PuppetProvisioner takes:

:provider:
        Must be set to PuppetProvisioner

:args:
        A dictionary of arguments to be passed to the provisioner.  The

PuppetProvisioner has the following mandatory fields:

:bucket:
        S3 bucket to download artifacts from.

Optional parameters are:

:infrastructure:
        Name of the infrastructure artifact to download from S3

:application:
        Name of the application artifact to download from S3

AWSFWProvisioner takes:

:provider:
        Must be set to AWSFWProvisioner

:args:
        A dictionary of arguments to be passed to the provisioner.  The

AWSFWProvisioner has the following mandatory fields:

:apps:
        A list of applications to install

:roles:
        A list of roles to install

:appbucket:
        The S3 bucket to download applications from

:rolebucket:
        The S3 bucket to download applications from

:platform_environment:
        The environment (eg, dev, stage, prod) for the platform

Optional parameters are:

:AWS_ACCESS_KEY_ID:
        If the instances need credentials, eg, to download from S3, this
        is the access key

:AWS_SECRET_ACCESS_KEY:
        If the instances need credentials, eg, to download from S3, this
        is the secret key

NoopProvisioner takes:

:provider:
        Must be set to NoopProvisioner

:args:
        An empty dictionary of arguments that will have no effect

**Example**

::

  ---
  config: {}
  resources:
    instance:
      - name: testbox
        count: 1
        image: ami-896c96fe
        sshKey: bootstrap
        monitoring: False
        provisioner:
          provider: PuppetProvisioner
          args:
            infrastructure: buildhelper-git.tar.gz
            application: buildhelper-git.jar
            bucket: piksel-provisioning
        sg:
          - buildhelper
        size: t1.micro
