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
..  module:: pmcf.strategy
    :platform: Unix
    :synopsis: module containing strategy classes for PMCF

..  moduleauthor:: Stephen Gran <stephen.gran@piksel.com>
"""

from pmcf.strategy.base_strategy import BaseStrategy
from pmcf.strategy.bluegreen import BlueGreen
from pmcf.strategy.inplace import InPlace
from pmcf.strategy.prompt_inplace import PromptInPlace

__all__ = [
    BaseStrategy,
    BlueGreen,
    InPlace,
    PromptInPlace,
]
