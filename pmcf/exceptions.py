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
..  module:: pmcf.exceptions
    :platform: Unix
    :synopsis: module containing exception classes for PMCF

..  moduleauthor:: Stephen Gran <stephen.gran@piksel.com>
"""


class PMCFException(Exception):
    """
    Base Exception class in PMCF
    """
    pass


class ParserFailure(PMCFException):
    """
    Exception raised for failures parsing stack definitions
    """
    def __init__(self, message):
        full_message = ("Error parsing input: %s" % message)
        super(ParserFailure, self).__init__(full_message)
        self.message = full_message


class PolicyException(PMCFException):
    """
    Exception raised for policy violations
    """
    def __init__(self, message):
        full_message = ("Policy violation: %s" % message)
        super(PolicyException, self).__init__(full_message)
        self.message = full_message


class PropertyException(PMCFException):
    """
    Exception raised for resource validation errors
    """
    def __init__(self, message):
        full_message = ("Error in resource properties: %s" % message)
        super(PropertyException, self).__init__(full_message)
        self.message = full_message


class ProvisionerException(PMCFException):
    """
    Exception raised for failures running provisioner classes
    """
    def __init__(self, message):
        full_message = ("Error during provisioning: %s" % message)
        super(ProvisionerException, self).__init__(full_message)
        self.message = full_message


class AuditException(PMCFException):
    """
    Exception raised for failures during audit logging
    """
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
