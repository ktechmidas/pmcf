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

from troposphere import AWSObject


class Route(AWSObject):
    type = "AWS::EC2::Route"

    props = {
        'DestinationCidrBlock': (basestring, True),
        'GatewayId': (basestring, False),
        'InstanceId': (basestring, False),
        'NetworkInterfaceId': (basestring, False),
        'RouteTableId': (basestring, True),
        'VpcPeeringConnectionId': (basestring, False),
    }


class VPCPeeringConnection(AWSObject):
    type = "AWS::EC2::VPCPeeringConnection"

    props = {
        'PeerVpcId': (basestring, True),
        'VpcId': (basestring, True),
        'Tags': (list, False),
    }


class VPNGatewayRoutePropagation(AWSObject):
    type = "AWS::EC2::VPNGatewayRoutePropagation"

    props = {
        'RouteTableIds': (list, False),
        'VpnGatewayId': (basestring, True),
    }


__all__ = [
    Route,
    VPCPeeringConnection,
    VPNGatewayRoutePropagation,
]
