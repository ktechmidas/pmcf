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

Network Schema
====================

The schema for networks is, like the other parts of the schema,
composed from smaller building blocks to make a larger whole.

A network has the following mandatory properties:

:name:
        The name of the network
:netrange:
        CIDR format

A network has the following optional properties:

:public:
        Boolean.  Controls addition of VPC IGW.
:private:
        Boolean.  Controls addition of VPC NAT instance.
:zones:
        A list of availability zones for this network
:subnets:
        A list of subnet definitions.  Only optional with YAML parser.
:routes:
        A list of route definitions
:peers:
        A list of vpc peer definitions
:vpn:
        A list of vpn definitions

A subnet has the following mandatory properties:

:cidr:
        CIDR format.  If the YAML config format is used, the YAMLParser
        will attempt to auto-fill this if it is ommitted.
:name:
        The name of the subnet
:zone:
        Availability Zone for the subnet

A subnet has the following optional properties:

:public:
        Boolean.  Whether this subnet will have a route to the internet
        via an IGW or a NAT instance.

A route has the following mandatory properties:

:cidr:
        CIDR format for the route.
:gateway:
        Gateway or the route.

A VPC peer has the following mandatory properties:

:peerid:
        The remote VPC to peer with.

A VPN has the following mandatory properties:

:asn:
        The BGP ASN to announce over the VPN.
:ip:
        The IP of the remote endpoint.


**Example**

::

  ---
  config: {}
  resources:
    network:
      - name: infra
        netrange: 10.203.8.0/24
        zones:
          - eu-west-1a
          - eu-west-1b
          - eu-west-1c
        peers:
          - peerid: =integration
        vpn:
          - asn: 65000
            ip: 83.98.1.51
      - name: integration
        netrange: 10.203.10.0/24
        zones:
          - eu-west-1a
          - eu-west-1b
          - eu-west-1c
