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

import yaml
from pmcf import exceptions
from pmcf.parsers.base_parser import BaseParser


class YamlParser(BaseParser):
    def parse(self, config):
        try:
            return yaml.load(config)
        except Exception, e:
            raise exceptions.ParserFailure(e)


__all__ = [
    YamlParser
]
