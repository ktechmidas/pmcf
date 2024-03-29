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
    :synopsis: module containing AWS Cloudformation output class

..  moduleauthor:: Stephen Gran <stephen.gran@piksel.com>
"""

import boto
import json
import logging
import time

from pmcf.exceptions import AuditException, ProvisionerException
from pmcf.outputs.json_output import JSONOutput
from pmcf.utils import import_from_string, make_diff
from pmcf.utils import get_changed_keys_from_templates, is_term

LOG = logging.getLogger(__name__)


class AWSCFNOutput(JSONOutput):
    """
    AWS Cloudformation output class.

    Subclass of the JSONOutput class, this reuses the JSON data and interfaces
    with the AWS Cloudformation API to create or update stacks.
    """

    def _get_input(self, prompt):
        """
        Helper method to take input if input is a tty
        """
        if is_term():
            return raw_input(prompt)
        return 'y'

    def _get_difference(self, cfn, stack, data):
        """
        Helper method to find differences between two JSON documents
        """
        resp = cfn.get_template(stack)['GetTemplateResponse']
        old_body = resp['GetTemplateResult']['TemplateBody']
        return get_changed_keys_from_templates(old_body, data)

    def _show_prompt(self, cfn, stack, data, allowed):
        """
        Helper method to create colourised diff outut and prompt for update
        """
        resp = cfn.get_template(stack)['GetTemplateResponse']
        old_body = resp['GetTemplateResult']['TemplateBody']
        diff = make_diff(old_body, data)
        if len(diff):
            print "Diff from previous:"
            print diff
            chkeys = get_changed_keys_from_templates(old_body, data)
            chkeys = [k for k in chkeys if not allowed.match(k)]
            print "Changed data:"
            for k in sorted(chkeys):
                print k
            answer = self._get_input("Continue? [Yn]: ")
            if answer.lower().startswith('n'):
                return False
        else:
            LOG.warning('No difference, not updating')
            return False
        return True

    def _stack_updatable(self, cfn, stack):
        """
        Checks to see if a given stack exists and is ready to be updated

        :param cfn: boto cloudformation connection object
        :type cfn: object.
        :param stack: Stack name to check
        :type stack: str.
        :returns: boolean
        """

        LOG.info('Checking whether stack %s is able to be updated', stack)
        try:
            ret = cfn.describe_stacks(stack)
            if len(ret) == 1:
                stack = ret[0]
                if stack.stack_status.endswith('COMPLETE'):
                    return True
        except boto.exception.BotoServerError, exc:
            if exc.message.endswith('Rate exceeded'):
                time.sleep(1)
                return self._stack_updatable(cfn, stack)
        return False

    def _stack_exists(self, cfn, stack):
        """
        Checks to see if a given stack already exists

        :param cfn: boto cloudformation connection object
        :type cfn: object.
        :param stack: Stack name to check
        :type stack: str.
        :returns: boolean
        """

        LOG.info('Checking for existance of stack %s', stack)
        try:
            cfn.describe_stacks(stack)
            return True
        except boto.exception.BotoServerError, exc:
            if exc.message.endswith('Rate exceeded'):
                time.sleep(1)
                return self._stack_exists(cfn, stack)
        return False

    def _need_iam_caps(self, data):
        """
        Checks for IAM resources in a stack definition and adds the necessary
        IAM capabilities to the stack definition if present.

        :param data: Stack definition
        :type data: str.
        :returns: boolean
        """

        json_data = json.loads(data)
        if not json_data.get('Resources'):
            return False
        for k in json_data['Resources'].keys():
            if json_data['Resources'][k].get('Type', '').find('IAM') > 0:
                LOG.debug('Found IAM resources, adding IAM capability')
                return True
        return False

    def _upload_stack(self, stack, destination, credentials):
        """
        Uploads stack to S3.  Allows for much larger stack definitions.

        :param stack: stack definition
        :type stack: str.
        :param destination: destination to copy stack to
        :type destination: str.
        :param credentials: credentials for copy command
        :type credentials: dict.
        :returns:  boolean
        :raises: :class:`pmcf.exceptions.ProvisionerException`
        """

        LOG.info('uploading stack definition to s3://%s/%s',
                 credentials['audit_output'], destination)
        try:
            s3conn = None
            if credentials.get('use_iam_profile'):
                s3conn = boto.connect_s3()
            else:
                s3conn = boto.connect_s3(
                    aws_access_key_id=credentials['access'],
                    aws_secret_access_key=credentials['secret']
                )
            bucket = s3conn.get_bucket(credentials['audit_output'])
            k = boto.s3.key.Key(bucket)
            k.key = destination
            k.set_contents_from_string(stack)
        except (boto.exception.S3ResponseError,
                boto.exception.BotoServerError), exc:
            raise ProvisionerException(exc)

    def run(self, data, metadata=None, poll=False,
            action='create', upload=False):
        """
        Interfaces with public and private cloud providers - responsible for
        actual stack creation and update in AWS.

        :param data: Stack definition
        :type data: str.
        :param metadata: Additional information for stack launch (tags, etc).
        :type metadata: dict.
        :param poll: Whether to poll until completion
        :type poll: boolean.
        :param action: Action to take on the stack
        :type action: str.
        :param upload: Whether to upload stack definition to s3 before launch
        :type upload: bool.
        :raises: :class:`pmcf.exceptions.ProvisionerException`
        :returns: boolean
        """

        metadata = metadata or {}
        LOG.debug('metadata is %s', metadata)

        if metadata.get('region', None) is None:
            raise ProvisionerException('Need to supply region in metadata')

        cfn = None
        for region in boto.regioninfo.get_regions('cloudformation'):
            if region.name == metadata['region']:
                if metadata.get('use_iam_profile'):
                    cfn = boto.connect_cloudformation(region=region)
                else:
                    cfn = boto.connect_cloudformation(
                        aws_access_key_id=metadata['access'],
                        aws_secret_access_key=metadata['secret'],
                        region=region
                    )
        if cfn is None:
            raise ProvisionerException("Can't find a valid region")

        strategy = import_from_string(
            'pmcf.strategy',
            metadata.get('strategy', 'BlueGreen')
        )()

        tags = metadata.get('tags', {})

        capabilities = None
        if self._need_iam_caps(data):
            capabilities = ['CAPABILITY_IAM']

        try:
            if action == 'delete':
                if self._stack_exists(cfn, metadata['name']):
                    LOG.info('stack %s exists, deleting', metadata['name'])
                    if strategy.should_prompt('delete'):
                        answer = self._get_input(
                            "Proceed with deletion of %s? [Yn]: " %
                            metadata['name']
                        )
                        if answer.lower().startswith('n'):
                            return False
                    cfn.delete_stack(metadata['name'])
                    return self.do_poll(cfn, metadata['name'], poll, action)
                else:
                    LOG.info("stack %s doesn't exist", metadata['name'])
                    return True

            if upload:
                creds = {
                    'access': metadata['access'],
                    'secret': metadata['secret'],
                    'audit_output': metadata.get('audit_output', None)
                }
                dest = 'launch/%s/%s/%s-%s' % (
                    metadata['name'],
                    metadata['environment'],
                    metadata['name'],
                    time.strftime('%Y%m%dT%H%M%S'))
                url = 'https://%s.%s/%s' % (
                    metadata['audit_output'],
                    's3.amazonaws.com',
                    dest
                )

            else:
                creds = {}
                dest = ''
                url = ''

            data = json.dumps(json.loads(data))
            if action == 'trigger':
                if self._stack_updatable(cfn, metadata['name']):
                    LOG.info('stack %s exists, triggering', metadata['name'])
                    allowed_update = strategy.allowed_update()

                    diff = self._get_difference(cfn, metadata['name'], data)
                    if len(diff) == 0:
                        LOG.warning('No difference, not updating')
                        return True

                    for change in diff:
                        if not allowed_update.match(change):
                            raise ProvisionerException(
                                'Not updating: %s not allowed field' % change)
                    if upload:
                        self._upload_stack(data, dest, creds)
                        cfn.validate_template(template_url=url)
                        cfn.update_stack(metadata['name'], template_url=url,
                                         capabilities=capabilities, tags=tags)
                    else:
                        cfn.validate_template(data)
                        cfn.update_stack(metadata['name'], data,
                                         capabilities=capabilities, tags=tags)

                else:
                    LOG.info("stack %s not updatable", metadata['name'])
                    return True

            elif action == 'create':
                if self._stack_exists(cfn, metadata['name']):
                    LOG.info("stack %s already exists", metadata['name'])
                    return True

                LOG.info("stack %s doesn't exist, creating", metadata['name'])
                if upload:
                    self._upload_stack(data, dest, creds)
                    cfn.validate_template(template_url=url)
                    cfn.create_stack(metadata['name'], template_url=url,
                                     capabilities=capabilities, tags=tags)
                else:
                    cfn.validate_template(data)
                    cfn.create_stack(metadata['name'], data,
                                     capabilities=capabilities, tags=tags)

            elif action == 'update':
                if not self._stack_exists(cfn, metadata['name']):
                    LOG.info("stack %s doesn't exist", metadata['name'])
                    return True

                if self._stack_updatable(cfn, metadata['name']):
                    if not strategy.should_update(action):
                        raise ProvisionerException(
                            'Stack exists but strategy does not allow update')

                    allowed_update = strategy.allowed_update()

                    diff = self._get_difference(cfn, metadata['name'], data)
                    if len(diff) == 0:
                        LOG.warning('No difference, not updating')
                        return True

                    changes = 0
                    for change in diff:
                        if allowed_update.match(change):
                            continue
                        changes += 1
                    if changes == 0:
                        LOG.warning('No difference, not updating')
                        return True

                    if strategy.should_prompt('update'):
                        if not self._show_prompt(
                                cfn,
                                metadata['name'],
                                data,
                                allowed_update):
                            return True

                    LOG.info("stack %s exists, updating",
                             metadata['name'])
                    if upload:
                        self._upload_stack(data, dest, creds)
                        cfn.validate_template(template_url=url)
                        cfn.update_stack(metadata['name'], template_url=url,
                                         capabilities=capabilities, tags=tags)
                    else:
                        cfn.validate_template(data)
                        cfn.update_stack(metadata['name'], data,
                                         capabilities=capabilities, tags=tags)
                else:
                    LOG.info("stack %s not updateable", metadata['name'])
                    return True

            self.do_audit(data, metadata)
            return self.do_poll(cfn, metadata['name'], poll, action)

        except boto.exception.BotoServerError, exc:
            raise ProvisionerException(str(exc))

    def do_poll(self, cfn, name, poll, action):
        """
        Polls remote API until stack is complete

        :param cfn: Cloudformation connection object
        :type cfn: object.
        :param name: Stack name
        :type name: str.
        :param poll: Whether to actually poll
        :type poll: boolean.
        """

        if poll:
            LOG.info('Polling until %s is complete', name)
            LOG.info('%20s | %35s | %20s | %s',
                     'resource id',
                     'resource type',
                     'resource status',
                     'resource status reason')
            seen_events = set()
            stack = None
            while True:
                time.sleep(3)
                try:
                    stack = cfn.describe_stacks(name)[0]
                    all_events = stack.describe_events()
                except boto.exception.BotoServerError, exc:
                    LOG.info(exc.message)
                    if action == 'delete' and \
                            exc.message.endswith('does not exist'):
                        return True
                    if exc.message.endswith('Rate exceeded'):
                        continue
                    return False
                for event in sorted(all_events, key=lambda x: x.timestamp):
                    if event.event_id in seen_events:
                        continue
                    if event.timestamp < self.start_time:
                        seen_events.add(event.event_id)
                        continue
                    LOG.info('%20s | %35s | %20s | %s',
                             event.logical_resource_id,
                             event.resource_type,
                             event.resource_status,
                             event.resource_status_reason)
                    seen_events.add(event.event_id)
                if stack.stack_status.endswith('COMPLETE') or\
                        stack.stack_status.endswith('FAILED'):
                    break
            if stack.stack_status.endswith('FAILED') or\
                    stack.stack_status.startswith('ROLLBACK') or\
                    stack.stack_status.startswith('UPDATE_ROLLBACK') or\
                    stack.stack_status.startswith('DELETE'):
                return False
            if len(stack.outputs) > 0:
                LOG.info('Stack outputs')
                for output in stack.outputs:
                    LOG.info('%s: %s', output.description, output.value)
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
            creds = {}
            if metadata.get('use_iam_profile'):
                creds['use_iam_profile'] = metadata['use_iam_profile']
            else:
                creds['access'] = metadata['access']
                creds['secret'] = metadata['secret']
            creds['audit_output'] = metadata.get('audit_output', None)
            dest = 'audit/%s/%s/%s-%s' % (
                metadata['name'],
                metadata['environment'],
                metadata['name'],
                time.strftime('%Y%m%dT%H%M%S'))
            audit.record_stack(data, dest, creds)
        except AuditException, exc:
            LOG.error(exc)


__all__ = [
    'AWSCFNOutput',
]
