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
..  module:: pmcf.provisioners.base_provisioner
    :platform: Unix
    :synopsis: module containing abstract base provisioner class

..  moduleauthor:: Stephen Gran <stephen.gran@piksel.com>
"""

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


# pylint: disable=no-self-use


class BaseProvisioner(object):
    """
    Abstract base class for provisioner classes.

    The PMCF Provisioner classes are responsible for providing userdata and/or
    cfn-init metadata suitable for use with cfn-init and/or cloud-init.

    Only provides an interface, and can not be used directly
    """

    __metaclass__ = abc.ABCMeta

    def __init__(self):
        self.boundary = '===============4206204907479218652=='

    @abc.abstractmethod
    def userdata(self, args):
        """
        Validates resource against local policy.

        :param args: provisioner arguments
        :type args: dict.
        :raises: :class:`NotImplementedError`
        :returns: str.
        """

        raise NotImplementedError

# pylint: disable=unused-argument

    def provisioner_policy(self, args):
        """
        Policy that a provisioner needs for an instance.  Not called unless
        wants_profile() returns True.

        :param args: provisioner arguments
        :type args: dict.
        :returns: boolean.
        """

        return None

# pylint: enable=unused-argument

    def wants_profile(self):
        """
        Whether a provisioner implementation wants a profile to be created

        :returns: boolean.
        """

        return False

    def wants_wait(self):
        """
        Whether a provisioner implementation wants a wait condition created

        :returns: boolean.
        """

        return False

# pylint: disable=unused-argument

    def cfn_init(self, args):
        """
        Return metadata suitable for consumption by cfn_init

        :param config: Config items for userdata
        :type config: dict.
        :param args: instance definition
        :type args: dict.
        :raises: :class:`NotImplementedError`
        :returns: dict.
        """

        return None

# pylint: enable=unused-argument

    def add_file(self, userdata, filename,
                 ftype='plain', compress=True):
        """
        Add data from file to userdata

        :param userdata: userdata object built so far
        :type userdata: :class:`email.mime.multipart.MIMEMultipart`
        :param filename: filename of data to add to userdata
        :type filename: str.
        :param ftype: file Mimetype
        :type ftype: str.
        :param compress: whether to gzip file before adding
        :type compress: bool.
        :returns: str.
        """

        fname = os.path.basename(filename)
        with open(filename) as fld:
            return self.add_data(userdata, fld.read(), fname, ftype, compress)

    def add_data(self, userdata, part, filename,
                 ftype='plain', compress=True):
        """
        Add data from string to userdata

        :param userdata: userdata object built so far
        :type userdata: :class:`email.mime.multipart.MIMEMultipart`
        :param part: string data to add to userdata
        :type part: str.
        :param filename: filename of data to add to userdata
        :type filename: str.
        :param ftype: file Mimetype
        :type ftype: str.
        :param compress: whether to gzip file before adding
        :type compress: bool.
        :returns: str.
        """

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
        userdata.attach(sub_message)
        return userdata

    def make_skeleton(self):
        """
        Create empty skeleton to add userdata parts to

        :returns: :class:`email.mime.multipart.MIMEMultipart`
        """

        return MIMEMultipart(boundary=self.boundary)

    def resize(self, userdata):
        """
        Checks size of userdata and aborts if it is too large

        :param userdata: userdata object built so far
        :type userdata: :class:`email.mime.multipart.MIMEMultipart`
        :raises: :class:`pmcf.exceptions.ProvisionerException`
        """

        data = userdata.as_string()
        if len(data) > 16384:
            raise ProvisionerException('userdata is too long')
        return data


__all__ = [
    'BaseProvisioner',
]
