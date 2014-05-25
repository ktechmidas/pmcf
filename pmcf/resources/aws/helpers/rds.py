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


class DBParameterGroup(AWSObject):
    type = "AWS::RDS::DBParameterGroup"

    props = {
        'Description': (basestring, False),
        'Family': (basestring, True),
        'Parameters': (dict, False),
        'Tags': (list, False),
    }


class DBSecurityGroupIngress(AWSObject):
    type = "AWS::RDS::DBSecurityGroupIngress"

    props = {
        'CIDRIP': (basestring, False),
        'DBSecurityGroupName': (basestring, True),
        'EC2SecurityGroupId': (basestring, False),
        'EC2SecurityGroupName': (basestring, False),
        'EC2SecurityGroupOwnerId': (basestring, False),
    }


__all__ = [
    DBParameterGroup,
    DBSecurityGroupIngress,
]
