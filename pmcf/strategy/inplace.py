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
..  module:: pmcf.strategy.inplace
    :platform: Unix
    :synopsis: module containing abstract base strategy class

..  moduleauthor:: Stephen Gran <stephen.gran@piksel.com>
"""

import logging

from pmcf.strategy.base_strategy import BaseStrategy

LOG = logging.getLogger(__name__)


class InPlace(BaseStrategy):
    """
    Abstract base class for strategy classes.

    The PMCF Strategy classes are responsible for instrumenting the output
    layers.  They respond to methods about whether to prompt, proceed
    automatically, or fail altogether, given the current constraints.

    This class provides the InPlace strategy, which allows updates.
    """

    def should_update(self, action):
        """
        Method signature for whether to proceed with an update.

        :param action: String representation of current action
        :type action: str.
        :returns: bool.
        """

        return True

    def should_prompt(self, action):
        """
        Method signature for whether to prompt on update.

        :param action: String representation of current action
        :type action: str.
        :returns: bool.
        """

        return False


__all__ = [
    InPlace,
]
