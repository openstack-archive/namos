# -*- coding: utf-8 -*-

# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""
Client side of the conductor RPC API.
"""
import functools
import json

# import oslo_messaging
from oslo_messaging import RemoteError

from namos.common import config
from namos.common import exception as namos_exception
from namos.common import messaging as rpc


def wrapper_function(func):
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except RemoteError as e:
            exception = getattr(namos_exception, e.exc_type)
            kwargs = json.loads(e.value)
            raise exception(**kwargs)

    return wrapped


class ConductorAPI(object):
    """Client side of the conductor RPC API.

    API version history:

    1.0 - Initial version.


    """

    RPC_API_VERSION = '1.0'

    def __init__(self):
        super(ConductorAPI, self).__init__()
        self.topic = config.MESSAGE_QUEUE_CONDUCTOR_TOPIC

        self.client = rpc.get_rpc_client(version=self.RPC_API_VERSION,
                                         topic=self.topic,
                                         exchange=config.PROJECT_NAME)

    @wrapper_function
    def add_region(self, context, region):
        self.client.call(context, 'add_region', region=region)

    @wrapper_function
    def region_get_all(self, context):
        return self.client.call(context, 'region_get_all')

    @wrapper_function
    def service_perspective_get(self, context, service_id,
                                include_details=False):
        return self.client.call(context,
                                'service_perspective_get',
                                service_id=service_id,
                                include_details=include_details)

    @wrapper_function
    def device_perspective_get(self, context, device_id,
                               include_details=False):
        return self.client.call(context,
                                'device_perspective_get',
                                device_id=device_id,
                                include_details=include_details)

    @wrapper_function
    def region_perspective_get(self, context, region_id,
                               include_details=False):
        return self.client.call(context,
                                'region_perspective_get',
                                region_id=region_id,
                                include_details=include_details)

    @wrapper_function
    def infra_perspective_get(self, context):
        return self.client.call(context,
                                'infra_perspective_get')

    @wrapper_function
    def config_get_by_name_for_service_worker(self,
                                              context,
                                              service_worker_id,
                                              name=None,
                                              only_configured=True):
        return self.client.call(context,
                                'config_get_by_name_for_service_worker',
                                service_worker_id=service_worker_id,
                                name=name,
                                only_configured=only_configured)

if __name__ == '__main__':
    # from namos.common import config

    config.init_log()
    config.init_conf('test-run')

    from oslo_context import context

    c = ConductorAPI()

    def add_sample_region():
        c.add_region(context.RequestContext(),
                     {'name': 'RegionOne11',
                      'keystone_region_id': 'region_one',
                      'extra': {'location': 'bangalore'},
                      'id': 'd7dcd175-27ef-46b5-997f-e6e572f320af'})

    def print_infra():
        print (json.dumps(c.infra_perspective_get(context.RequestContext())))

    def print_sample_conf():
        for cf in c.config_get_by_name_for_service_worker(
            context.RequestContext(),
            service_worker_id='fc88fd41-7e9c-42c9-891d-3823efd4824e'):
            print ('%s %s' % (cf['name'], cf['value']))

    print_sample_conf()
