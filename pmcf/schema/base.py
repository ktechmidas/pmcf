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

# pylint: disable=invalid-name

schema = """
$schema: http://json-schema.org/draft-04/schema#
definitions:
    scaletime:
        type: object
        properties:
            min:
                type: integer
            max:
                type: integer
            count:
                type: integer
            recurrence:
                type: string
        required:
            - count
            - recurrence
    scaledir:
        type: object
        properties:
            stat:
                type: string
            condition:
                type: string
            change:
                type: string
            interval:
                type: integer
            wait:
                type: integer
        required:
            - stat
            - condition
            - change
        additionalProperties: false
    timedscalingpolicy:
        type: object
        properties:
            up:
                $ref: "#/definitions/scaletime"
            down:
                $ref: "#/definitions/scaletime"
        required:
            - up
    scalingpolicy:
        type: object
        properties:
            metric:
                type: string
            unit:
                type: string
            up:
                $ref: "#/definitions/scaledir"
            down:
                $ref: "#/definitions/scaledir"
        required:
            - down
            - metric
            - unit
            - up
        additionalProperties: false
    noopprovisioner:
        type: object
        properties:
            provider:
                enum:
                    - NoopProvisioner
            args:
                type:
                    object
        required:
            - provider
        additionalProperties: false
    blockprovisioner:
        type: object
        properties:
            provider:
                enum:
                    - BlockingProvisioner
            args:
                type:
                    object
        required:
            - provider
        additionalProperties: false
    winpuppetprovisioner:
        type: object
        properties:
            provider:
                enum:
                    - WindowsPuppetProvisioner
            args:
                type:
                    object
                properties:
                    infrastructure:
                        type: string
                    application:
                        type: string
                    appname:
                        type: string
                    bucket:
                        type: string
                    find_nodes:
                        type: boolean
                    metrics:
                        type: boolean
                    custom_profile:
                        type: array
                    custom_facts:
                        type: object
                    custom_tags:
                        type: object
                required:
                    - bucket
                additionalProperties: false
        required:
            - provider
            - args
        additionalProperties: false
    ansibleprovisioner:
        type: object
        properties:
            provider:
                enum:
                    - AnsibleProvisioner
            args:
                type:
                    object
                properties:
                    playbook:
                        type: string
                    bucket:
                        type: string
                    metrics:
                        type: boolean
                    cfn_hup:
                        type:
                            object
                        properties:
                            interval:
                                type: integer
                            enabled:
                                type: boolean
                        required:
                            - enabled
                        additionalProperties: false
                    custom_facts:
                        type: object
                    custom_tags:
                        type: object
                required:
                    - bucket
                additionalProperties: false
        required:
            - provider
            - args
        additionalProperties: false
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
                    appname:
                        type: string
                    bucket:
                        type: string
                    find_nodes:
                        type: boolean
                    metrics:
                        type: boolean
                    custom_profile:
                        type: array
                    custom_facts:
                        type: object
                    custom_tags:
                        type: object
                required:
                    - bucket
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
                    appbucket:
                        type: string
                    rolebucket:
                        type: string
                    platform_environment:
                        type: string
                    AWS_ACCESS_KEY_ID:
                        type: string
                    AWS_SECRET_ACCESS_KEY:
                        type: string
                required:
                    - apps
                    - roles
                    - appbucket
                    - rolebucket
                    - platform_environment
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
            depends:
                type: string
            dns:
                type: object
                properties:
                    record:
                        type: string
                    type:
                        enum:
                            - per-instance-private
                            - per-instance-public
                            - per-group-private
                            - per-group-public
                            - cname-public
                            - cname-private
                    zone:
                        type: string
                required:
                    - type
                    - zone
                additionalProperties: false
            dnszone:
                type: string
            nat:
                type: boolean
            healthcheck:
                type: string
            image:
                type: string
            monitoring:
                type: boolean
            lb:
                type: array
            min:
                type: integer
            max:
                type: integer
                minimum: 1
            name:
                type: string
            notify:
                type: string
            provisioner:
                type: object
                oneOf:
                    - $ref: "#/definitions/winpuppetprovisioner"
                    - $ref: "#/definitions/puppetprovisioner"
                    - $ref: "#/definitions/ansibleprovisioner"
                    - $ref: "#/definitions/awsfwprovisioner"
                    - $ref: "#/definitions/noopprovisioner"
                    - $ref: "#/definitions/blockprovisioner"
            public:
                type: boolean
            timed_scaling_policy:
                $ref: "#/definitions/timedscalingpolicy"
            scaling_policy:
                $ref: "#/definitions/scalingpolicy"
            sg:
                type: array
            subnets:
                type: array
                minItems: 1
            sshKey:
                type: string
            size:
                type: string
            zones:
                type: array
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
           type:
                enum:
                    - io1
                    - gp2
                    - standard
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
            dns:
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
    vpc_peer:
        properties:
            peerid:
                type: string
        required:
            - peerid
        additionalProperties: false
    vpc_route:
        properties:
            cidr:
                type: string
            gateway:
                type: string
        required:
            - cidr
            - gateway
        additionalProperties: false
    vpc_subnet:
        properties:
            cidr:
                type: string
            name:
                type: string
            public:
                type: boolean
            zone:
                type: string
        required:
            - cidr
            - name
            - zone
        additionalProperties: false
    vpc_vpn:
        properties:
            asn:
                type: integer
            ip:
                type: string
        required:
            - asn
            - ip
        additionalProperties: false
    network:
        properties:
            name:
                type: string
            netrange:
                type: string
            public:
                type: boolean
            routes:
                type: array
                minItems: 1
                items:
                    $ref: "#/definitions/vpc_route"
            subnets:
                type: array
                minItems: 1
                items:
                    $ref: "#/definitions/vpc_subnet"
            peers:
                type: array
                minItems: 1
                items:
                    $ref: "#/definitions/vpc_peer"
            vpn:
                type: array
                minItems: 1
                items:
                    $ref: "#/definitions/vpc_vpn"
            zones:
                type: array
        required:
            - name
            - netrange
            - subnets
        additionalProperties: false
    cache_params:
        properties:
            name:
                type: string
            params:
                type: object
        required:
            - name
        additionalProperties: false
    cache:
        properties:
            name:
                type: string
            size:
                type: string
            type:
                type: string
            count:
                type: integer
            sg:
                type: array
                minItems: 1
            params:
                $ref: "#/definitions/cache_params"
        required:
            - count
            - name
            - params
            - size
            - type
        additionalProperties: false
    queue:
        properties:
            name:
                type: string
            retention:
                type: integer
        required:
            - name
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
            vpcid:
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
    stream:
        properties:
            name:
                type: string
            shards:
                type: integer
        required:
            - name
            - shards
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
            network:
                type: array
                items:
                    $ref: "#/definitions/network"
            queue:
                type: array
                items:
                    $ref: "#/definitions/queue"
            cache:
                type: array
                items:
                    $ref: "#/definitions/cache"
            stream:
                type: array
                items:
                    $ref: "#/definitions/stream"
            secgroup:
                type: array
                items:
                    $ref: "#/definitions/secgroup"
        required:
            - cdn
            - db
            - instance
            - load_balancer
            - secgroup
        additionalProperties: false
    tags:
        type: object
required:
    - config
    - resources
additionalProperties: false
"""


__all__ = [
    'schema',
]
