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
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import gzip
import logging
import os
import StringIO
import sys

from pmcf.exceptions import ProvisionerException

LOG = logging.getLogger(__name__)


class BaseProvisioner(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        self.boundary = '===============4206204907479218652=='

    @abc.abstractmethod
    def userdata(self, config):
        raise NotImplementedError

    def add_file(self, ud, filename, ftype='plain', compress=True):
        fname = os.path.basename(filename)
        with open(filename) as fd:
            return self.add_data(ud, fd.read(), fname, ftype, compress)

    def add_data(self, message, part, filename, ftype='plain', compress=True):
        if compress:
            stringio = StringIO.StringIO()
            gz_file = gzip.GzipFile(filename=filename, fileobj=stringio,
                                    compresslevel=9, mode='w')
            gz_file.write(part)
            gz_file.close()
            data = stringio.getvalue()
            sub_message = MIMEApplication(data, 'x-gzip')
        else:
            sub_message = MIMEText(part, ftype, sys.getdefaultencoding())

        sub_message.add_header('Content-Disposition',
                               'attachment; filename="%s"' % (filename))
        message.attach(sub_message)
        return message

    def make_skeleton(self):
        return MIMEMultipart(boundary=self.boundary)

    def resize(self, ud):
        data = ud.as_string()
        if len(data) > 16384:
            raise ProvisionerException('userdata is too long')
        return data


__all__ = [
    BaseProvisioner,
]
