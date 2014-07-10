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

from nose.tools import assert_equals, assert_raises

from pmcf.exceptions import PropertyException
from pmcf.resources.aws import elasticloadbalancing as elb

from tests.unit.resources import TestResource


class TestELBResource(TestResource):

    def test_access_logging_policy_invalid_no_enabled(self):
        alp = elb.AccessLoggingPolicy(
            "test",
        )
        assert_raises(PropertyException, alp.JSONrepr)

    def test_access_logging_policy_invalid_no_emit_interval(self):
        alp = elb.AccessLoggingPolicy(
            "test",
            Enabled=True,
            S3BucketName='testme-123',
            S3BucketPrefix='logs/dev',
        )
        assert_raises(PropertyException, alp.JSONrepr)

    def test_access_logging_policy_invalid_no_bucket_name(self):
        alp = elb.AccessLoggingPolicy(
            "test",
            Enabled=True,
            EmitInterval=5,
            S3BucketPrefix='logs/dev',
        )
        assert_raises(PropertyException, alp.JSONrepr)

    def test_access_logging_policy_invalid_bad_emit_interval(self):
        alp = elb.AccessLoggingPolicy(
            "test",
            Enabled=True,
            EmitInterval=7,
            S3BucketName='testme-123',
            S3BucketPrefix='logs/dev',
        )
        assert_raises(PropertyException, alp.JSONrepr)

    def test_access_logging_policy_valid_enabled(self):
        data = {
            'EmitInterval': 5,
            'Enabled': 'true',
            'S3BucketName': 'testme-123',
            'S3BucketPrefix': 'logs/dev'
        }
        alp = elb.AccessLoggingPolicy(
            "test",
            Enabled=True,
            EmitInterval=5,
            S3BucketName='testme-123',
            S3BucketPrefix='logs/dev',
        )
        assert_equals(self._data_for_resource(alp), data)

    def test_access_logging_policy_valid_disabled(self):
        data = {
            'Enabled': 'false',
        }
        alp = elb.AccessLoggingPolicy(
            "test",
            Enabled=False,
        )
        assert_equals(self._data_for_resource(alp), data)

    def test_app_cookie_stickiness_policy_invalid_no_policy(self):
        acsp = elb.AppCookieStickinessPolicy(
            "test",
            CookieName='testcookie-123',
        )
        assert_raises(PropertyException, acsp.JSONrepr)

    def test_app_cookie_stickiness_policy_invalid_no_cookie(self):
        acsp = elb.AppCookieStickinessPolicy(
            "test",
            PolicyName='testpolicy-123',
        )
        assert_raises(PropertyException, acsp.JSONrepr)

    def test_app_cookie_stickiness_policy_valid(self):
        data = {
            'CookieName': 'testcookie-123',
            'PolicyName': 'testpolicy-123'
        }
        acsp = elb.AppCookieStickinessPolicy(
            "test",
            CookieName='testcookie-123',
            PolicyName='testpolicy-123',
        )
        assert_equals(self._data_for_resource(acsp), data)

    def test_healthcheck_invalid_no_healthy_threshold(self):
        hc = elb.HealthCheck(
            "test",
            Interval=5,
            Target='HTTP:80/management/healthcheck',
            Timeout=2,
            UnhealthyThreshold=3,
        )
        assert_raises(PropertyException, hc.JSONrepr)

    def test_healthcheck_invalid_no_interval(self):
        hc = elb.HealthCheck(
            "test",
            HealthyThreshold=3,
            Target='HTTP:80/management/healthcheck',
            Timeout=2,
            UnhealthyThreshold=3,
        )
        assert_raises(PropertyException, hc.JSONrepr)

    def test_healthcheck_invalid_no_target(self):
        hc = elb.HealthCheck(
            "test",
            HealthyThreshold=3,
            Interval=5,
            Timeout=2,
            UnhealthyThreshold=3,
        )
        assert_raises(PropertyException, hc.JSONrepr)

    def test_healthcheck_invalid_no_timeout(self):
        hc = elb.HealthCheck(
            "test",
            HealthyThreshold=3,
            Interval=5,
            Target='HTTP:80/management/healthcheck',
            UnhealthyThreshold=3,
        )
        assert_raises(PropertyException, hc.JSONrepr)

    def test_healthcheck_invalid_no_unhealthy_threshold(self):
        hc = elb.HealthCheck(
            "test",
            HealthyThreshold=3,
            Interval=5,
            Target='HTTP:80/management/healthcheck',
            Timeout=2,
        )
        assert_raises(PropertyException, hc.JSONrepr)

    def test_healthcheck_valid(self):
        data = {
            'HealthyThreshold': 3,
            'Interval': 5,
            'Target': 'HTTP:80/management/healthcheck',
            'Timeout': 2,
            'UnhealthyThreshold': 3
        }
        hc = elb.HealthCheck(
            "test",
            HealthyThreshold=3,
            Interval=5,
            Target='HTTP:80/management/healthcheck',
            Timeout=2,
            UnhealthyThreshold=3,
        )
        assert_equals(self._data_for_resource(hc), data)

    def test_lb_cookie_stickiness_policy_invalid(self):
        lbcsp = elb.LBCookieStickinessPolicy(
            "test",
            CookieExpirationPeriod='10'
        )
        assert_raises(PropertyException, lbcsp.JSONrepr)

    def test_lb_cookie_stickiness_policy_valid(self):
        data = {
            'CookieExpirationPeriod': '10',
            'PolicyName': 'testpolicy'
        }
        lbcsp = elb.LBCookieStickinessPolicy(
            "test",
            CookieExpirationPeriod='10',
            PolicyName='testpolicy'
        )
        assert_equals(self._data_for_resource(lbcsp), data)

    def test_listener_invalid_no_instance_port(self):
        l = elb.Listener(
            "test",
            InstanceProtocol='HTTP',
            LoadBalancerPort=80,
            PolicyNames=['testpolicy-123'],
            Protocol='HTTP',
        )
        assert_raises(PropertyException, l.JSONrepr)

    def test_listener_invalid_no_lb_port(self):
        l = elb.Listener(
            "test",
            InstancePort=80,
            InstanceProtocol='HTTP',
            PolicyNames=['testpolicy-123'],
            Protocol='HTTP',
        )
        assert_raises(PropertyException, l.JSONrepr)

    def test_listener_invalid_no_protocol(self):
        l = elb.Listener(
            "test",
            InstancePort=80,
            InstanceProtocol='HTTP',
            LoadBalancerPort=80,
            PolicyNames=['testpolicy-123'],
        )
        assert_raises(PropertyException, l.JSONrepr)

    def test_listener_valid(self):
        data = {
            'InstancePort': 80,
            'InstanceProtocol': 'HTTP',
            'LoadBalancerPort': 80,
            'PolicyNames': ['testpolicy-123'],
            'Protocol': 'HTTP'
        }
        l = elb.Listener(
            "test",
            InstancePort=80,
            InstanceProtocol='HTTP',
            LoadBalancerPort=80,
            PolicyNames=['testpolicy-123'],
            Protocol='HTTP',
        )
        assert_equals(self._data_for_resource(l), data)

    def test_policy_invalid_no_name(self):
        p = elb.Policy(
            "test",
            PolicyType='SSLNegotiationPolicyType',
        )
        assert_raises(PropertyException, p.JSONrepr)

    def test_policy_invalid_no_type(self):
        p = elb.Policy(
            "test",
            PolicyName='testme-123',
        )
        assert_raises(PropertyException, p.JSONrepr)

    def test_policy_invalid_bad_type(self):
        p = elb.Policy(
            "test",
            PolicyName='testme-123',
            PolicyType='testme-123',
        )
        assert_raises(PropertyException, p.JSONrepr)

    def test_policy_valid(self):
        data = {
            'PolicyName': 'testme-123',
            'PolicyType': 'SSLNegotiationPolicyType'
        }
        p = elb.Policy(
            "test",
            PolicyName='testme-123',
            PolicyType='SSLNegotiationPolicyType',
        )
        assert_equals(self._data_for_resource(p), data)

    def test_connection_draining_policy_invalid_no_enabled(self):
        cdp = elb.ConnectionDrainingPolicy(
            "test",
            Timeout=5
        )
        assert_raises(PropertyException, cdp.JSONrepr)

    def test_connection_draining_policy_valid(self):
        data = {
            'Enabled': True,
            'Timeout': 5,
        }
        cdp = elb.ConnectionDrainingPolicy(
            "test",
            Enabled=True,
            Timeout=5
        )
        assert_equals(self._data_for_resource(cdp), data)

    def test_loadbalancer_invalid_no_listener(self):
        lb = elb.LoadBalancer(
            "test",
        )
        assert_raises(PropertyException, lb.JSONrepr)

    def test_loadbalancer_invalid_subnet_and_az(self):
        l = elb.Listener(
            "test",
            InstancePort=80,
            InstanceProtocol='HTTP',
            LoadBalancerPort=80,
            PolicyNames=['testpolicy-123'],
            Protocol='HTTP',
        )
        lb = elb.LoadBalancer(
            "test",
            Subnets=['testsn-123'],
            AvailabilityZones=['eu-west1c'],
            Listeners=[l],
        )
        assert_raises(PropertyException, lb.JSONrepr)

    def test_loadbalancer_valid(self):
        data = {
            'Properties': {
                'Listeners': [{
                    'InstancePort': 80,
                    'InstanceProtocol': 'HTTP',
                    'LoadBalancerPort': 80,
                    'PolicyNames': ['testpolicy-123'],
                    'Protocol': 'HTTP'}
                ]
            },
            'Type': u'AWS::ElasticLoadBalancing::LoadBalancer'
        }

        l = elb.Listener(
            "test",
            InstancePort=80,
            InstanceProtocol='HTTP',
            LoadBalancerPort=80,
            PolicyNames=['testpolicy-123'],
            Protocol='HTTP',
        )
        lb = elb.LoadBalancer(
            "test",
            Listeners=[l],
        )
        assert_equals(self._data_for_resource(lb), data)

    def test_access_logging_policy_bad_name(self):
        assert_raises(PropertyException, elb.AccessLoggingPolicy, 'bad-name')

    def test_app_cookie_stickiness_policy_bad_name(self):
        assert_raises(
            PropertyException,
            elb.AppCookieStickinessPolicy, 'bad-name')

    def test_health_check_bad_name(self):
        assert_raises(PropertyException, elb.HealthCheck, 'bad-name')

    def test_lb_cookie_stickiness_policy_bad_name(self):
        assert_raises(
            PropertyException,
            elb.LBCookieStickinessPolicy, 'bad-name')

    def test_listener_bad_name(self):
        assert_raises(PropertyException, elb.Listener, 'bad-name')

    def test_policy_bad_name(self):
        assert_raises(PropertyException, elb.Policy, 'bad-name')

    def test_connection_draining_policy_bad_name(self):
        assert_raises(
            PropertyException,
            elb.ConnectionDrainingPolicy, 'bad-name')

    def test_load_balancer_bad_name(self):
        assert_raises(PropertyException, elb.LoadBalancer, 'bad-name')
