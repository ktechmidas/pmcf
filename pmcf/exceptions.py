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


class PMCFException(Exception):
    pass


class ParserFailure(PMCFException):
    def __init__(self, message):
        full_message = ("Error parsing input: %s" % message)
        super(ParserFailure, self).__init__(full_message)
        self.message = full_message


class PolicyException(PMCFException):
    def __init__(self, message):
        full_message = ("Policy violation: %s" % message)
        super(PolicyException, self).__init__(full_message)
        self.message = full_message


class PropertyException(PMCFException):
    def __init__(self, message):
        full_message = ("Error in resource properties: %s" % message)
        super(PropertyException, self).__init__(full_message)
        self.message = full_message


class ProvisionerException(PMCFException):
    def __init__(self, message):
        full_message = ("Error during provisioning: %s" % message)
        super(ProvisionerException, self).__init__(full_message)
        self.message = full_message


class AuditException(PMCFException):
    def __init__(self, message):
        full_message = ("Error during audit logging: %s" % message)
        super(AuditException, self).__init__(full_message)
        self.message = full_message


__all__ = [
    AuditException,
    ParserFailure,
    PMCFException,
    PolicyException,
    PropertyException,
    ProvisionerException
]
