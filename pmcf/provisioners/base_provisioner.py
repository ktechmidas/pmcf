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

import abc
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import sys
import zlib

from pmcf.exceptions import ProvisionerException


class BaseProvisioner(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        self.boundary = '===============4206204907479218652=='

    @abc.abstractmethod
    def userdata(self, config):
        raise NotImplementedError

    def add_data(self, message, part, part_type, filename):
        sub_message = MIMEText(part, part_type, sys.getdefaultencoding())
        sub_message.add_header('Content-Disposition',
                               'attachment; filename="%s"' % (filename))
        message.attach(sub_message)
        return message

    def make_skeleton(self):
        return MIMEMultipart(boundary=self.boundary)

    def resize(self, ud):
        data = zlib.compress(ud.as_string(), 9).encode('base64', 'strict')
        if len(data) > 16384:
            raise ProvisionerException('userdata is too long')
        return data


__all__ = [
    BaseProvisioner,
]
