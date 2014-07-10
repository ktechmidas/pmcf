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

Security Group Schema
=====================

The schema for security groups is, like the other parts of the schema,
composed from smaller building blocks to make a larger whole.


The basic format of a security group is:

:name:
        The name of the security group
:rules:
        An array of rules associated with the security group

Each member of the rules array can be composed in one of several ways.

The common properties are:

:protocol:
        The network protocol (TCP/UDP/etc) that this rule applies to

Additionally, rules must have one (and only one) of the properties:

:source_group:
        This is the AWS security group that originates the traffic.  To
        reference a security group being created in this stack, prefix the
        name with '='.  To reference a security group in another account,
        use the 'account_number'/'group_name' form.  Note that this will not
        work in VPC deployments.
:source_cidr:
        Standard CIDR notation for the source of traffic

Finally, rules must use one of the following notation formats:

:port:
        Port to allow for ingress traffic.  This shorthand may be used on
        single port rules

or

:from_port:
        Beginning of port range to allow for ingress traffic
:to_port:
        End of port range to allow for ingress traffic

A stack describes a list of security groups.  It is permissable for a stack
to omit the security group block.

**Example**

::

  ---
  config: {}
  resources:
    secgroup:
      - name: appservers
        rules: []
      - name: test
        rules:
          - port: 22
            protocol: tcp
            source_cidr: 0.0.0.0/0
          - port: 80
            protocol: tcp
            source_group: default_elb_be7533e2-c63d-3951-a0af-363d10c4b103
          - from_port: 1024
            to_port: 1224
            protocol: tcp
            source_cidr: 0.0.0.0/0
          - from_port: 80
            to_port: 80
            protocol: tcp
            source_group: =appservers
