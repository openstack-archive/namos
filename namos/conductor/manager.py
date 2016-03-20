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

import functools

from oslo_config import cfg
from oslo_context import context
from oslo_log import log

from namos.common import config
from namos.common import exception
from namos.db import api as db_api
from namos.db import openstack_drivers

LOG = log.getLogger(__name__)

config.register_conductor_opts()

CONF = cfg.CONF


def request_context(func):
    @functools.wraps(func)
    def wrapped(self, ctx, *args, **kwargs):
        if ctx is not None and not isinstance(ctx, context.RequestContext):
            ctx = context.RequestContext.from_dict(ctx.to_dict())

        return func(self, ctx, *args, **kwargs)

    return wrapped


class ConductorManager(object):
    RPC_API_VERSION = '1.0'
    TOPIC = config.MESSAGE_QUEUE_CONDUCTOR_TOPIC

    @request_context
    def add_region(self, context, region):
        # Move this try except to wrpper fn of the db layer
        try:
            db_api.region_create(context, region)
        except Exception as e:
            raise exception.NamosException(e)

    @request_context
    def region_get_all(self, context):
        return db_api.region_get_all(context)

    @request_context
    def register_myself(self, context, registration_info):
        LOG.info("REGISTERING %s.%s" % (registration_info['project_name'],
                                        registration_info['prog_name']))

        # Service processing
        sp = ServiceProcessor(registration_info)
        service_worker_id = sp.process_service(context)

        #  Device Driver processing
        dp = DriverProcessor(service_worker_id,
                             registration_info['config_dict'])
        dp.process_drivers(context)

        return service_worker_id

    @request_context
    def service_perspective_get(self,
                                context,
                                service_id,
                                include_details=False):
        return db_api.service_perspective_get(context,
                                              service_id,
                                              include_details)

    @request_context
    def device_perspective_get(self,
                               context,
                               device_id,
                               include_details=False):
        return db_api.device_perspective_get(context,
                                             device_id,
                                             include_details)

    @request_context
    def region_perspective_get(self,
                               context,
                               region_id,
                               include_details=False):
        return db_api.region_perspective_get(context,
                                             region_id,
                                             include_details)

    @request_context
    def infra_perspective_get(self, context):
        return db_api.infra_perspective_get(context)


class ServiceProcessor(object):
    def __init__(self, registration_info):
        self.registration_info = registration_info

    def process_service(self, context):
        # Service Node
        try:
            # TODO(mrkanag) is this to be region specifc search
            node = db_api.service_node_get_by_name(
                context,
                self.registration_info.get('fqdn'))
            LOG.info('Service node %s is existing' % node)
        except exception.ServiceNodeNotFound:
            # TODO(mrkanag) region_id is hard-coded, fix it !
            # user proper node name instead of fqdn
            node = db_api.service_node_create(
                context,
                dict(name=self.registration_info.get('fqdn'),
                     fqdn=self.registration_info.get('fqdn'),
                     region_id='f7dcd175-27ef-46b5-997f-e6e572f320b0'))

            LOG.info('Service node %s is created' % node)

        # Service
        try:
            service = db_api.service_get_by_name(
                context,
                self.registration_info.get('project_name'))
            LOG.info('Service %s is existing' % service)
        except exception.ServiceNotFound:
            s_id = 'b9c2549f-f685-4bc2-92e9-ba8af9c18591'
            service = db_api.service_create(
                context,
                # TODO(mrkanag) use keystone python client and
                # use real service id here
                dict(name=self.registration_info.get('project_name'),
                     keystone_service_id=s_id))

            LOG.info('Service %s is created' % service)

        # Service Component
        service_components = \
            db_api.service_component_get_all_by_node_for_service(
                context,
                node_id=node.id,
                service_id=service.id,
                name=self.registration_info['prog_name']
            )
        if len(service_components) == 1:
            service_component = service_components[0]
            LOG.info('Service Component %s is existing' % service_component)
        # TODO(mrkanag) what to do when service_components size is > 1
        else:
            service_component = db_api.service_component_create(
                context,
                dict(name=self.registration_info['prog_name'],
                     node_id=node.id,
                     service_id=service.id))
            LOG.info('Service Component %s is created' % service_component)

        # Service Worker
        # TODO(mrkanag) Find a way to purge the dead service worker
        # Once each service  is enabled with heart beating namos
        # purging can be done once heart beat stopped. this can be
        # done from openstack.common.service.py
        service_workers = \
            db_api.service_worker_get_by_host_for_service_component(
                context,
                service_component_id=service_component.id,
                host=self.registration_info['host']
            )
        if len(service_workers) == 1:
            service_worker = \
                db_api.service_worker_update(
                    context,
                    service_workers[0].id,
                    dict(
                        pid=self.registration_info['pid']))
            LOG.info('Service Worker %s is existing and is updated'
                     % service_worker)

        # TODO(mrkanag) what to do when service_workers size is > 1
        else:
            service_worker = db_api.service_worker_create(
                context,
                # TODO(mrkanag) Fix the name, device driver proper !
                dict(name='%s@%s' % (self.registration_info['pid'],
                                     service_component.name),
                     pid=self.registration_info['pid'],
                     host=self.registration_info['host'],
                     service_component_id=service_component.id))
            LOG.info('Service Worker %s is created' % service_worker)

        # Config
        # TODO(mrkanag) Optimize the config like per service_component
        # or per service_worker,
        for cfg_name, cfg_obj in self.registration_info[
            'config_dict'].iteritems():
            cfg_obj['service_worker_id'] = service_worker.id
            configs = db_api.config_get_by_name_for_service_worker(
                context,
                service_worker_id=cfg_obj['service_worker_id'],
                name=cfg_obj['name'])
            if len(configs) == 1:
                config = db_api.config_update(context,
                                              configs[0].id,
                                              cfg_obj)
                LOG.info("Config %s is existing and is updated" % config)
            else:
                config = db_api.config_create(context, cfg_obj)
                LOG.info("Config %s is created" % config)

        return service_worker.id


class DriverProcessor(object):
    def __init__(self, service_worker_id, config_dict):
        self.config_dict = config_dict
        self.service_worker_id = service_worker_id

    def _identify_drivers(self):
        return (set(openstack_drivers.get_drivers_config().keys()) &
                set(self.config_dict.keys()))

    def _get_value(self, name):
        if name is None:
            return name

        if isinstance(name, str):
            # Constant naming
            if name[0] == '#':
                return name[1:]
            return (self.config_dict[name].get('value') or
                    self.config_dict[name].get('default_value'))
        elif isinstance(name, tuple):
            fn = name[0]
            args = list()
            for var in name[1:]:
                args.append(self._get_value(var))
            return fn(*args)
        elif isinstance(name, list):
            fmt_str = name[0]
            params = [self._get_value(param) for param in name[1:]]
            return fmt_str % tuple(params)

    @staticmethod
    def _to_list(list_in_str):
        def strip_out(s):
            start_idx = 0
            end_idx = len(s)
            if s[start_idx] == '[' \
                    or s[start_idx] == '\'' \
                    or s[start_idx] == '"':
                start_idx += 1
            if s[end_idx - 1] == ']' \
                    or s[end_idx - 1] == '\'' \
                    or s[end_idx - 1] == '"':
                end_idx -= 1
            return s[start_idx:end_idx]

        l = []
        for s in strip_out(list_in_str.strip()).split(','):
            s = str(strip_out(s.strip()))
            l.append(s)

        return l

    def process_drivers(self, context):
        for driver_key in self._identify_drivers():
            drivers = self._get_value(driver_key)
            drivers = DriverProcessor._to_list(drivers)
            for driver_name in drivers:
                self.process_driver(context, driver_key, driver_name)

    def process_driver(self, context, driver_key, driver_name):
            driver_config = \
                openstack_drivers.get_drivers_config()[driver_key][driver_name]

            if driver_config.get('alias') is not None:
                alias = driver_config.get('alias')
                driver_config = \
                    openstack_drivers.get_drivers_config()
                for key in alias.split(':'):
                    driver_config = driver_config[key]
                driver_name = key

            driver_def = \
                openstack_drivers.get_drivers_def()[driver_name]

            connection = dict()

            endpoint_type = None
            connection_cfg = None
            device_endpoint_name = None
            device_cfg = None
            child_device_cfg = None

            if driver_config.get('device') is not None:
                device_cfg = driver_config['device']

            if driver_config['endpoint'].get('type') is not None:
                endpoint_type = driver_config['endpoint']['type']
                if endpoint_type[0] != '#':
                    endpoint_type = self._get_value(endpoint_type)

                connection_cfg = driver_config['endpoint'][endpoint_type][
                    'connection']
                device_endpoint_name = self._get_value(
                    driver_config['endpoint'][endpoint_type]['name'])
                # override the device name
                if driver_config['endpoint'][endpoint_type].get(
                        'device') is not None:
                    device_cfg = driver_config['endpoint'][endpoint_type][
                        'device']
                if driver_config['endpoint'][endpoint_type].get(
                        'child_device') is not None:
                    child_device_cfg = driver_config['endpoint'][
                        endpoint_type]['child_device']
            else:
                endpoint_type = None
                connection_cfg = driver_config['endpoint']['connection']
                device_endpoint_name = self._get_value(
                    driver_config['endpoint']['name']
                )
                # override the device name
                if driver_config['endpoint'].get('device') is not None:
                    device_cfg = driver_config['endpoint']['device']

                if driver_config['endpoint'].get('child_device') is not None:
                    child_device_cfg = driver_config['endpoint'][
                        'child_device']

            # Device
            device_name = self._get_value(device_cfg['name'])
            try:
                device = db_api.device_get_by_name(
                    context,
                    device_name)
                LOG.info('Device %s is existing' % device)
            except exception.DeviceNotFound:
                # TODO(mrkanag) region_id is hard-coded, fix it !
                # Set the right status as well
                device = db_api.device_create(
                    context,
                    dict(name=device_name,
                         status='active',
                         region_id='f7dcd175-27ef-46b5-997f-e6e572f320b0'))

                LOG.info('Device %s is created' % device)

            # Handle child devices
            if child_device_cfg is not None:
                for d_name in self._get_value(child_device_cfg['key']):
                    base_name = self._get_value(child_device_cfg['base_name'])
                    d_name = '%s-%s' % (base_name, d_name)
                    try:
                        device = db_api.device_get_by_name(
                            context,
                            d_name)
                        LOG.info('Device %s is existing' % device)
                    except exception.DeviceNotFound:
                        # TODO(mrkanag) region_id is hard-coded, fix it !
                        # Set the right status as well
                        r_id = 'f7dcd175-27ef-46b5-997f-e6e572f320b0'
                        device = db_api.device_create(
                            context,
                            dict(name=d_name,
                                 status='active',
                                 parent_id=device.id,
                                 region_id=r_id))

                LOG.info('Device %s is created' % device)

            # Device Endpoint
            device_endpoints = db_api.device_endpoint_get_by_device_type(
                context,
                device_id=device.id,
                type=endpoint_type,
                name=device_endpoint_name)
            if len(device_endpoints) >= 1:
                device_endpoint = device_endpoints[0]
                LOG.info('Device Endpoint %s is existing' %
                         device_endpoints[0])
            else:
                for k, v in connection_cfg.iteritems():
                    connection[k] = self._get_value(k)

                device_endpoint = db_api.device_endpoint_create(
                    context,
                    dict(name=device_endpoint_name,
                         connection=connection,
                         type=endpoint_type,
                         device_id=device.id))
                LOG.info('Device Endpoint %s is created' % device_endpoint)

            # Device Driver Class
            try:
                device_driver_class = db_api.device_driver_class_get_by_name(
                    context,
                    driver_name)
                LOG.info('Device Driver Class %s is existing' %
                         device_driver_class)
            except exception.DeviceDriverClassNotFound:
                device_driver_class = db_api.device_driver_class_create(
                    context,
                    dict(name=driver_name,
                         python_class=driver_name,
                         type=driver_def['type'],
                         device_id=device.id,
                         endpoint_id=device_endpoint.id,
                         service_worker_id=self.service_worker_id,
                         extra=driver_def.get('extra')))
                LOG.info('Device Driver Class %s is created' %
                         device_driver_class)

            # Device Driver
            device_drivers = \
                db_api.device_driver_get_by_device_endpoint_service_worker(
                    context,
                    device_id=device.id,
                    endpoint_id=device_endpoint.id,
                    device_driver_class_id=device_driver_class.id,
                    service_worker_id=self.service_worker_id
                )
            if len(device_drivers) >= 1:
                device_driver = device_drivers[0]
                LOG.info('Device Driver %s is existing' %
                         device_driver)
            else:
                device_driver = db_api.device_driver_create(
                    context,
                    dict(device_id=device.id,
                         name=driver_name,
                         endpoint_id=device_endpoint.id,
                         device_driver_class_id=device_driver_class.id,
                         service_worker_id=self.service_worker_id)
                )
                LOG.info('Device Driver %s is created' %
                         device_driver)


if __name__ == '__main__':
    print (DriverProcessor(None, None)._to_list("[\"file\', \'http\']"))
