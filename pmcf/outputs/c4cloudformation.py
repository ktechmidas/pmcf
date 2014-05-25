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

import datetime
import logging

from pmcf.outputs.cloudformation import AWSCFNOutput

LOG = logging.getLogger(__name__)


class C4AWSCFNOutput(AWSCFNOutput):

    def run(self, data, metadata={}):
        if config['stage'].lower() == 'prod':
            review_date = (datetime.date.today() +
                           datetime.timedelta(6*365/12)).isoformat()
        else:
            review_date = (datetime.date.today() +
                           datetime.timedelta(2*365/12)).isoformat()

        metadata['tags'] = {
            'Project': config['name'],
            'Environment': config['stage'],
            'CodeVersion': config['version'],
            'Farm': '-'.join(
                    [config['name'], config['stage'], config['version']]),
            'ReviewDate': review_date,
            'Owner': config['owner']
        }

        super(self.__class__, self).run(data, metadata)
