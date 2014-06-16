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
..  module:: pmcf.outputs.cloudformation
    :platform: Unix
    :synopsis: module containing AWS Cloudformation output class for PMCF

..  moduleauthor:: Stephen Gran <stephen.gran@piksel.com>
"""

import boto
import json
import logging
import time

from pmcf.exceptions import AuditException, ProvisionerException
from pmcf.outputs.json_output import JSONOutput
from pmcf.utils import import_from_string, make_diff

LOG = logging.getLogger(__name__)


class AWSCFNOutput(JSONOutput):
    """
    AWS Cloudformation output class.

    Subclass of the JSONOutput class, this reuses the JSON data and interfaces
    with the AWS Cloudformation API to create or update stacks.
    """

    def _get_input(self, prompt):
        return raw_input(prompt)

    def _show_prompt(self, cfn, stack, data):
        resp = cfn.get_template(stack)['GetTemplateResponse']
        old_body = resp['GetTemplateResult']['TemplateBody']
        diff = make_diff(old_body, data)
        if len(diff):
            print "Diff from previous:"
            print diff
            answer = self._get_input("Continue? [Yn]: ")
            if answer.lower().startswith('n'):
                return False
        else:
            LOG.warning('No difference, not updating')
            return False
        return True

    def _stack_exists(self, cfn, stack):
        """
        Checks to see if a given stack already exists

        :param cfn: boto cloudformation connection object
        :type cfn: object.
        :param stack: Stack name to check
        :type stack: str.
        :returns: boolean
        """

        try:
            cfn.describe_stacks(stack)
        except boto.exception.BotoServerError:
            return False
        return True

    def run(self, data, metadata={}):
        """
        Interfaces with public and private cloud providers.

        :param data: Stack definition
        :type data: str.
        :param metadata: Additional information for stack launch (tags, etc).
        :type metadata: dict.
        :raises: :class:`pmcf.exceptions.ProvisionerException`
        :returns: boolean
        """

        LOG.debug('metadata is %s' % metadata)

        if metadata.get('region', None) is None:
            raise ProvisionerException('Need to supply region in metadata')

        cfn = None
        for region in boto.regioninfo.get_regions('cloudformation'):
            if region.name == metadata['region']:
                cfn = boto.connect_cloudformation(
                    aws_access_key_id=metadata['access'],
                    aws_secret_access_key=metadata['secret'],
                    region=region
                )
        if cfn is None:
            raise ProvisionerException("Can't find a valid region")

        tags = metadata.get('tags', {})

        try:
            if metadata.get('strategy', 'BLUEGREEN') != 'BLUEGREEN' and \
                    self._stack_exists(cfn, metadata['name']):
                LOG.debug('stack %s exists, updating', metadata['name'])
                if metadata['strategy'] == 'prompt_inplace':
                    if not self._show_prompt(cfn, metadata['name'], data):
                        return True

                data = json.dumps(json.loads(data))
                cfn.validate_template(data)
                cfn.update_stack(metadata['name'], data, tags=tags)
            else:
                LOG.debug("stack %s doesn't exist, creating", metadata['name'])
                data = json.dumps(json.loads(data))
                cfn.validate_template(data)
                cfn.create_stack(metadata['name'], data, tags=tags)
        except boto.exception.BotoServerError, e:
            raise ProvisionerException(str(e))

        self.do_audit(data, metadata)
        return True

    def do_audit(self, data, metadata):
        """
        Records audit logs for current transaction

        :param data: Stack definition
        :type data: str.
        :param metadata: Additional information for stack launch (tags, etc).
        :type metadata: dict.
        """

        try:
            audit = import_from_string('pmcf.audit', metadata['audit'])()
            creds = {
                'access': metadata['access'],
                'secret': metadata['secret'],
                'audit_output': metadata.get('audit_output', None)
            }
            dest = 'audit/%s/%s/%s-%s' % (
                metadata['name'],
                metadata['environment'],
                metadata['name'],
                time.strftime('%Y%m%dT%H%M%S'))
            audit.record_stack(data, dest, creds)
        except AuditException, e:
            LOG.error(e)


__all__ = [
    AWSCFNOutput,
]
