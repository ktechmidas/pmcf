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
..  module:: pmcf.policy.json_policy
    :platform: Unix
    :synopsis: module containing JSON policy class

..  moduleauthor:: Stephen Gran <stephen.gran@piksel.com>
"""

import json
import logging

from pmcf.exceptions import PolicyException
from pmcf.policy.base_policy import BasePolicy

LOG = logging.getLogger(__name__)


class JSONPolicy(BasePolicy):
    """
    Baseline Policy class.

    This is the supported policy class.
    """

    def __init__(self, json_file='/etc/pmcf/policy.json'):
        try:
            with open(json_file) as fd:
                self.json_policy = json.loads(fd.read())
        except (IOError, ValueError), e:
            raise PolicyException("Can't load policy file %s: %s" %
                                  (json_file, e))

    def validate_resource(self, resource_type, resource_data):
        """
        Validates resource against local policy.

        :param resource_type: Type of resource to validate
        :type resource_type: str.
        :param resource_data: Resource to validate
        :type resource_data: dict.
        :raises: :class:`NotImplementedError`
        :returns: dict
        """

        if not self.json_policy.get(resource_type):
            return True
        policy = self.json_policy.get(resource_type)
        for key in policy.keys():
            if resource_data.get(key, None) is None:
                resource_data[key] = policy[key]['default']
            if policy[key].get('constraints'):
                if resource_data[key] not in policy[key]['constraints']:
                    raise PolicyException("Data field `%s' with value `%s' "
                                          "not allowed for `%s'" %
                                          (key, resource_data[key],
                                           resource_type))
        return True


__all__ = [
    JSONPolicy,
]
