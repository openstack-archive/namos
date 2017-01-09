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
        return self.client.call(
            context,
            'region_create',
            region=region)

    @wrapper_function
    def region_get(self, context, region_id):
        return self.client.call(
            context,
            'region_get',
            region_id=region_id)

    @wrapper_function
    def region_update(self, context, region_id, region):
        return self.client.call(
            context,
            'region_update',
            region_id=region_id,
            region=region)

    @wrapper_function
    def region_get_all(self, context):
        return self.client.call(
            context,
            'region_get_all')

    @wrapper_function
    def region_delete(self, context, region_id):
        return self.client.call(
            context,
            'region_delete',
            region_id=region_id)

    @wrapper_function
    def service_node_create(self, context, service_node):
        return self.client.call(
            context,
            'service_node_create',
            service_node=service_node)

    @wrapper_function
    def service_node_get(self, context, service_node_id):
        return self.client.call(
            context,
            'service_node_get',
            service_node_id=service_node_id)

    @wrapper_function
    def service_node_update(self, context, service_node_id, service_node):
        return self.client.call(
            context,
            'service_node_update',
            service_node_id=service_node_id,
            service_node=service_node)

    @wrapper_function
    def service_node_get_all(self, context):
        return self.client.call(
            context,
            'service_node_get_all')

    @wrapper_function
    def service_node_delete(self, context, service_node_id):
        return self.client.call(
            context,
            'service_node_delete',
            service_node_id=service_node_id)

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
    def view_360(self, context,
                 include_conf_file=False,
                 include_status=False,
                 include_file_entry=False):
        return self.client.call(context,
                                'view_360',
                                include_conf_file=include_conf_file,
                                include_status=include_status,
                                include_file_entry=include_file_entry)

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

    @wrapper_function
    def get_status(self, context):
        return self.client.call(context,
                                'get_status')

    @wrapper_function
    def ping(self, context, identification):
        return self.client.call(context,
                                'ping',
                                identification=identification)

    @wrapper_function
    def config_file_get(self, context, config_file_id):
        return self.client.call(context,
                                'config_file_get',
                                config_file_id=config_file_id)

    @wrapper_function
    def config_file_update(self, context, config_file_id, content):
        return self.client.call(context,
                                'config_file_update',
                                config_file_id=config_file_id,
                                content=content)

    @wrapper_function
    def config_schema(self, context, project, with_file_link=False):
        return self.client.call(context,
                                'config_schema',
                                project=project,
                                with_file_link=with_file_link)


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

    def print_view_360():
        with open('/tmp/view_360.json', 'w') as file:
            view = c.view_360(context.RequestContext(), True, True, True)
            file.write(json.dumps(view))

    def print_config_schema():
        for s in ['nova', 'cinder', 'glance', 'neutron', 'heat', 'namos',
                  'keystone', 'ceilometer', 'tacker']:
            with open('/tmp/config_schema_%s.json' % s, 'w') as file:
                file.write(json.dumps(c.config_schema(
                    context.RequestContext(),
                    project=s,
                    with_file_link=True
                )))

    def sample_config_update():
        with open('/tmp/sample.conf', 'r') as content_file:
            content = content_file.read()

            print (c.config_file_update(context.RequestContext(),
                                        'dcf0f17b-99f6-49e9-8d5f-23b3ad1167dc',
                                        content))

    print_config_schema()
    print_view_360()
    # sample_config_update()
