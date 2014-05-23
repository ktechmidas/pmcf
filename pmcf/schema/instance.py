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


schema = """
type: object
properties:
    block_device:
        type: array
    count:
        type: integer
    image:
        type: string
    monitoring:
        type: boolean
    name:
        type: string
    provisioner:
        type: object
        properties:
            args:
                type: object
            provider:
                type: string
    sg:
        type: array
    sshKey:
        type: string
    size:
        type: string
"""


__all__ = [
    schema
]
