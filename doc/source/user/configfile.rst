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

Configuration file
==================

The PMCF configuration file (by default /etc/pmcf/pmcf.conf) is a standard
Windows INI-style file.  Valid section headers are::

    [default]
    [profile profilename]

Profile names are arbitrary strings - choose what makes sense for your
environment.  These can be used by passing::

    -p profilename

on the command line.  Values missing from a profile block will be supplemented
by values from the default block, and then overridden by values passed as
:ref:`cli`

Valid keys for a section in the config file are and their defaults are::

    audit = NoopAudit
    audit_output = None
    action = create
    output = BaseOutput
    parser = BaseParser
    policy = BasePolicy
    provisioner = BaseProvisioner
    verbose = None
    debug = None
    quiet = None
    policyfile = None
    stackfile = None
    accesskey = None
    secretkey = None
    use_iam_profile = False
    instance_accesskey = None
    instance_secretkey = None
    region = None
    environment = None
    poll = False

This will not give you a working config file.  You must select at least a
valid parser, policy, provisioner and output class.  Some outputs, such as
the :class:`pmcf.outputs.cloudformation.AWSCFNOutput` derived classes also
need AWS credentials.  The AWSFW provisioner needs instance_accesskey and
instance_secretkey as well to provide the instances with credentials to
download their apps and roles.

Config file values:

:audit:
    This is the Audit class to use for audit logging.  Must implement the
    interface of :class:`pmcf.audit.base_audit.BaseAudit`, typically by
    subclassing it.

:audit_output:
    Destination for audit logs.  Individual subclasses are free to use
    this field as they see fit.  For instance, the
    :class:`pmcf.audit.s3_audit.S3Audit` needs the name of the S3 bucket in
    this field.

:output:
    This is the Output class to use for output of your parsed stack definition.
    Must implement the interface of
    :class:`pmcf.outputs.base_output.BaseOutput`, typically by subclassing it.

:parser:
    This is the Parser class to use for parsing your stack definition
    Must implement the interface of
    :class:`pmcf.parsers.base_parser.BaseParser`, typically by subclassing it.
    The two available parsers are
    :class:`pmcf.parsers.awsfw_parser.AWSFWParser` and
    :class:`pmcf.parsers.yaml_parser.YamlParser`.  The
    :class:`pmcf.parsers.awsfw_parser.AWSFWParser` is considered legacy and
    provided for backwards compatibility with existing configurations only.

:policy:
    This is the Policy class to use for providing defaults and constraints for
    your stack definition.  Must implement the interface of
    :class:`pmcf.policy.base_policy.BasePolicy`, typically by subclassing it.
    The only current implementation is JSONPolicy, which uses a default config
    file /etc/pmcf/policy.json

:provisioner:
    This is the provisioner class to use to provide userdata scripts suitable
    for consumption by `cloud-init
    <http://cloudinit.readthedocs.org/en/latest/>`_.  Must implement the
    interface of :class:`pmcf.provisioners.base_provisioner.BaseProvisioner`,
    typically by subclassing it.

:verbose:
    Enables logging at loglevel LOG.info

:debug:
    Enables logging at loglevel LOG.debug

:quiet:
    Disables logging above loglevel LOG.warning

:policyfile:
    Policy file to use for policy class.  Defaults to /etc/pmcf/policy.json

:stackfile:
    Stack definition.  Typically would be passed on the command line, but is
    valid in the configuration file

:accesskey:
    AWS access key.  Not needed for all Outputs or Audits.  Typically would be
    different in different profiles, and only stored at the profile level.

:secretkey:
    AWS secret key.  Not needed for all Outputs or Audits.  Typically would be
    different in different profiles, and only stored at the profile level.

:use_iam_profile:
    Use instance profiles instead of an accesskey/secretkey pair.  Not needed
    for all Outputs or Audits.  Typically would be different in different
    profiles, and only stored at the profile level.

:region:
    AWS region.  Not needed for all Outputs or Audits.  Typically would be
    different in different profiles, and only stored at the profile level.

:instance_accesskey:
    AWS access key for use by instances.  Not needed for all Provisioners - at
    present, only the AWSFWProvisioner uses this value.  Typically would be
    different in different profiles, and only stored at the profile level.

:instance_secretkey:
    AWS access key for use by instances.  Not needed for all Provisioners - at
    present, only the AWSFWProvisioner uses this value.  Typically would be
    different in different profiles, and only stored at the profile level.

:environment:
    Environment (dev, test, prod, etc).  Typically would be passed on the
    command line, but is valid in the configuration file.

:poll:
    Whether to poll until stack creation/update completes.  Typically would be
    passed on the command line, but is valid in the configuration file.
    Defaults to False

:action:
    What action to take on the resulting stack definition.  Typically would be
    passed on the command line, but is valid in the configuration file.
    Defaults to 'create'


A full sample config file::

    [default]
    output = SequoiaAWSCFNOutput
    parser = YamlParser
    policy = JSONPolicy
    provisioner = PuppetProvisioner
    audit = S3Audit
    audit_output = piksel-provisioning

    [profile sequoia-dev]
    region = eu-west-1
    accesskey = XXXXX
    secretkey = XXXXX

    [profile sequoia-prod]
    region = eu-west-1
    accesskey = YYYYY
    secretkey = YYYYY
    environment = prod
