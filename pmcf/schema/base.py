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
..  module:: pmcf.schema.base
    :platform: Unix
    :synopsis: module containing base schema data

..  moduleauthor:: Stephen Gran <stephen.gran@piksel.com>
"""

schema = """
$schema: http://json-schema.org/draft-04/schema#
definitions:
    puppetprovisioner:
        type: object
        properties:
            provider:
                enum:
                    - PuppetProvisioner
            args:
                type:
                    object
                properties:
                    infrastructure:
                        type: string
                    application:
                        type: string
                    bucket:
                        type: string
                    name:
                        type: string
                    profile:
                        type: string
                required:
                    - name
                    - bucket
                    - profile
                additionalProperties: false
        required:
            - provider
            - args
        additionalProperties: false
    awsfwprovisioner:
        type: object
        properties:
            provider:
                enum:
                    - AWSFWProvisioner
            args:
                type:
                    object
                properties:
                    apps:
                        type: array
                    roles:
                        type: array
                required:
                    - apps
                    - roles
                additionalProperties: false
        required:
            - provider
            - args
        additionalProperties: false
    instance:
        properties:
            block_device:
                type: array
                items:
                    $ref: "#/definitions/block_storage"
            count:
                type: integer
                minimum: 1
            image:
                type: string
            monitoring:
                type: boolean
            lb:
                type: string
            min:
                type: integer
                minimum: 1
            max:
                type: integer
                minimum: 1
            name:
                type: string
            profile:
                type: string
            provisioner:
                type: object
                oneOf:
                    - $ref: "#/definitions/puppetprovisioner"
                    - $ref: "#/definitions/awsfwprovisioner"
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
    block_storage:
        properties:
           size:
               type: string
           device:
               type: string
        required:
            - size
            - device
        additionalProperties: false
    listener:
        properties:
            instance_port:
                type: integer
            protocol:
                enum:
                    - HTTP
                    - HTTPS
                    - TCP
            instance_protocol:
                enum:
                    - HTTP
                    - HTTPS
                    - TCP
            lb_port:
                type: integer
            sslCert:
                type: string
        required:
            - instance_port
            - protocol
            - instance_protocol
            - lb_port
        additionalProperties: false
    load_balancer:
        properties:
            name:
                type: string
            internal:
                type: boolean
            subnets:
                type: array
                minItems: 1
            listener:
                type: array
                minItems: 1
                items:
                    $ref: "#/definitions/listener"
            policy:
                type: array
            sg:
                type: array
            healthcheck:
                type: object
                properties:
                    path:
                        type: string
                    protocol:
                        enum:
                            - HTTP
                            - HTTPS
                            - TCP
                    port:
                        type: integer
                required:
                    - protocol
                    - port
                additionalProperties: false
        required:
            - name
            - listener
            - healthcheck
        additionalProperties: false
    secgrouprule_cidr_port:
        properties:
            port:
                type: integer
            protocol:
                type: string
            source_cidr:
                type: string
        required:
            - port
            - protocol
            - source_cidr
        additionalProperties: false
    secgrouprule_group_port:
        properties:
            port:
                type: integer
            protocol:
                type: string
            source_group:
                type: string
        required:
            - port
            - protocol
            - source_group
        additionalProperties: false
    secgrouprule_cidr:
        properties:
            to_port:
                type: integer
            from_port:
                type: integer
            protocol:
                type: string
            source_cidr:
                type: string
        required:
            - from_port
            - to_port
            - protocol
            - source_cidr
        additionalProperties: false
    secgrouprule_group:
        properties:
            to_port:
                type: integer
            from_port:
                type: integer
            protocol:
                type: string
            source_group:
                type: string
        required:
            - from_port
            - to_port
            - protocol
            - source_group
        additionalProperties: false
    secgroup:
        properties:
            name:
                type: string
            rules:
                type: array
                items:
                    anyOf:
                        - $ref: "#/definitions/secgrouprule_group"
                        - $ref: "#/definitions/secgrouprule_cidr"
                        - $ref: "#/definitions/secgrouprule_group_port"
                        - $ref: "#/definitions/secgrouprule_cidr_port"
        required:
            - name
            - rules
        additionalProperties: false
    role:
        properties:
            name:
                type: string
            access:
                type: object
                properties:
                    application:
                        type: string
                    infrastructure:
                        type: string
                additionalProperties: false
        required:
            - name
            - access
        additionalProperties: false
type: object
properties:
    config:
        type: object
    resources:
        type: object
        properties:
            cdn:
                type: array
            db:
                type: array
            instance:
                type: array
                items:
                    $ref: "#/definitions/instance"
            load_balancer:
                type: array
                items:
                    $ref: "#/definitions/load_balancer"
            secgroup:
                type: array
                items:
                    $ref: "#/definitions/secgroup"
            role:
                type: array
                items:
                    $ref: "#/definitions/role"
        required:
            - cdn
            - db
            - instance
            - load_balancer
            - secgroup
            - role
        additionalProperties: false
    tags:
        type: object
required:
    - config
    - resources
additionalProperties: false
"""

__all__ = [
    schema
]
