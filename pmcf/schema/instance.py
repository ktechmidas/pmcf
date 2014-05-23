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
$schema: http://json-schema.org/draft-04/schema#
type: object
properties:
    block_device:
        type: array
    count:
        type: integer
        minimum: 1
    image:
        type: string
    monitoring:
        type: boolean
    lb:
        type: string
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
required:
    - count
    - image
    - monitoring
    - name
    - provisioner
    - sg
    - sshKey
    - size
additionalProperties: false
"""

__all__ = [
    schema
]
