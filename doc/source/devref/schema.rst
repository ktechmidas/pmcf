..
      Copyright 2014 Piksel Ltd.

      Licensed under the Apache License, Version 2.0 (the "License"); you may
      not use this file except in compliance with the License. You may obtain
      a copy of the License at

          http://www.apache.org/licenses/LICENSE-2.0

      Unless required by applicable law or agreed to in writing, software
      distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
      WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
      License for the specific language governing permissions and limitations
      under the License.

Schema
******

The schema in pmcf implements the `Draft 4 JSON Schema
<http://json-schema.org/>`_, and is responsible for validating the internal
data structure for correctness and completeness.

Most of the structure should be fairly straight  forward, if slightly verbose.
References to other definitions are allowed, which can both make the schema
more compact and slightly more difficult to read.

This is the schema definition for a load balancer, which references the schema
definition for a listener (a load balancer can have one or more listeners)::

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
