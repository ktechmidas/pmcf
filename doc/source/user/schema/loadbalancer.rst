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

Load Balancer Schema
====================

The schema for security groups is, like the other parts of the schema,
composed from smaller building blocks to make a larger whole.

The basic format of a security group is:

:name:
        The name of the load balancer

:listener:
        A list of listener definitions

:healthcheck:
        A healthcheck definition

A listener has the following mandatory properties:

:instance_port:
        The TCP port on the instance to connect to for traffic.

:protocol:
        One of HTTP, HTTPS, or TCP

:instance_protocol:
        One of HTTP, HTTPS, or TCP

:lb_port:
        The TCP port to listen for traffic on

Additionally, a listener has the following optional properties:

:sslCert:
        The name of an SSL cert that has already been upload to IAM.

A healthcheck has the following properties:

:path:
        The path to be checked for HTTP/HTTPS healthchecks.

:protocol:
        One of HTTP, HTTPS, or TCP

:port:
        The TCP port to connect to for the healthcheck.

A load balancer must have at least one listener, and must have a healthcheck.
Additional properties that are allowed on a load balancer definition are:

:dns:
        Top level domain for route53 Alias record.  For a load balancer named
        'mylb' in the 'test' environment, if this is set to 'example.com.',
        the resulting route53 Alias record will be 'mylb.test.example.com.'

:internal:
        A boolean determining whether this load balancer is scheme internal or
        not.  Defaults to False.

:subnets:
        A list of subnets for internal loadbalancers.  Must be present if
        internal is set to true.

:policy:
        A list of policy objects.  Details of policy objects are still evolving

:sg:
        A list of names of security groups to attach.  If ommitted, the default
        security group for ELBs will be used.

**Example**

::

  ---
  config: {}
  resources:
    load_balancer:
      - name: puppetforge
        dns: aws.sequoia.piksel.com.
        listener:
          - instance_port: 80
            instance_protocol: HTTP
            protocol: HTTP
            lb_port: 80
        healthcheck:
          protocol: HTTP
          port: 80
          path: /
        policy:
          - type: log_policy
            policy:
              emit_interval: 5
              enabled: true
              s3bucket: piksel-logging
              s3prefix: puppetforge
