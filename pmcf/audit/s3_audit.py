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

import boto
import logging

from pmcf.audit.base_audit import BaseAudit
from pmcf.exceptions import AuditException

LOG = logging.getLogger(__name__)


class S3Audit(BaseAudit):
    def record_stack(self, stack, destination, credentials):
        LOG.debug('recording stack definition to s3://%s/%s' %
                  (credentials['audit_output'], destination))
        try:
            s3 = boto.connect_s3(
                aws_access_key_id=credentials['access'],
                aws_secret_access_key=credentials['secret']
            )
            bucket = s3.get_bucket(credentials['audit_output'])
            k = boto.s3.key.Key(bucket)
            k.key = destination
            k.set_contents_from_string(stack)
        except (boto.exception.S3ResponseError,
                boto.exception.BotoServerError), e:
            raise AuditException(e)

        LOG.debug('Audit logging successful')
        return True


__all__ = [
    S3Audit,
]
