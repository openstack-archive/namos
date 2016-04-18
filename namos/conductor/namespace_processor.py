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

from oslo_config import cfg
from oslo_log import log

from namos.common import exception
from namos.common import utils
from namos.db import api as db_api
from namos.db import openstack_drivers

LOG = log.getLogger(__name__)

CONF = cfg.CONF


class NamespaceProcessor(object):
    # TODO(mrkanag) check Fuel driver at
    # http://docs.openstack.org/mitaka/config-reference/content/
    # hpe-3par-driver.html
    def __init__(self, context, manager, service_worker_id, region_id):
        self.context = context
        self.manager = manager
        self.service_worker_id = service_worker_id
        self.region_id = region_id
        self.config_dict = self._get_config_dict()

    def _get_config_dict(self):
        conf_dict = {}
        for c in db_api.config_get_by_name_for_service_worker(
            self.context,
            self.service_worker_id
        ):
            conf_dict[c.name] = c.to_dict()

        return conf_dict

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
            return (self.config_dict[name].get('value'))
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

    def process_drivers(self):
        for driver_key in self._identify_drivers():
            try:
                drivers = self._get_value(driver_key)
                drivers = utils._to_list(drivers)
                for driver_name in drivers:
                    self.process_driver(driver_key, driver_name)
            except KeyError:  # noqa
                # TODO(mrkanag) run namos-manager and restart nova-scheduler
                # KeyError: 'libvirt.virt_type' is thrown, fix it
                LOG.error('Failed to process driver %s in service worker %s' %
                          (driver_key, self.service_worker_id))
                continue

    def process_driver(self, driver_key, driver_name):
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
                # TODO(mrkanag) Set the right status
                device = db_api.device_create(
                    self.context,
                    dict(name=device_name,
                         status='active',
                         region_id=self.region_id))

                LOG.info('Device %s is created' % device)
            except exception.AlreadyExist:
                device = db_api.device_get_by_name(
                    self.context,
                    device_name)
                LOG.info('Device %s is existing' % device)

            # TODO(mrkanag) Poperly Handle child devices
            if child_device_cfg is not None:
                for d_name in self._get_value(child_device_cfg['key']):
                    base_name = self._get_value(child_device_cfg['base_name'])
                    d_name = '%s-%s' % (base_name, d_name)
                    try:
                        device = db_api.device_get_by_name(
                            self.context,
                            d_name)
                        LOG.info('Device %s is existing' % device)
                    except exception.DeviceNotFound:
                        # TODO(mrkanag) region_id is hard-coded, fix it !
                        # Set the right status as well
                        r_id = 'f7dcd175-27ef-46b5-997f-e6e572f320b0'
                        device = db_api.device_create(
                            self.context,
                            dict(name=d_name,
                                 status='active',
                                 parent_id=device.id,
                                 region_id=r_id))

                LOG.info('Device %s is created' % device)

            # Device Endpoint
            try:
                for k, v in connection_cfg.iteritems():
                    connection[k] = self._get_value(k)

                device_endpoint = db_api.device_endpoint_create(
                    self.context,
                    dict(name=device_endpoint_name,
                         connection=connection,
                         type=endpoint_type,
                         device_id=device.id))
                LOG.info('Device Endpoint %s is created' % device_endpoint)
            except exception.AlreadyExist:
                device_endpoints = db_api.device_endpoint_get_by_device_type(
                    self.context,
                    device_id=device.id,
                    type=endpoint_type,
                    name=device_endpoint_name)
                if len(device_endpoints) >= 1:
                    device_endpoint = device_endpoints[0]
                    LOG.info('Device Endpoint %s is existing' %
                             device_endpoints[0])

            # Device Driver Class
            try:
                device_driver_class = db_api.device_driver_class_create(
                    self.context,
                    dict(name=driver_name,
                         python_class=driver_name,
                         type=driver_def['type'],
                         device_id=device.id,
                         endpoint_id=device_endpoint.id,
                         service_worker_id=self.service_worker_id,
                         extra=driver_def.get('extra')))
                LOG.info('Device Driver Class %s is created' %
                         device_driver_class)
            except exception.AlreadyExist:
                device_driver_class = db_api.device_driver_class_get_by_name(
                    self.context,
                    driver_name)
                LOG.info('Device Driver Class %s is existing' %
                         device_driver_class)

            # Device Driver
            try:
                device_driver = db_api.device_driver_create(
                    self.context,
                    dict(device_id=device.id,
                         name=driver_name,
                         endpoint_id=device_endpoint.id,
                         device_driver_class_id=device_driver_class.id,
                         service_worker_id=self.service_worker_id)
                )
                LOG.info('Device Driver %s is created' %
                         device_driver)
            except exception.AlreadyExist:
                device_drivers = \
                    db_api.device_driver_get_by_device_endpoint_service_worker(
                        self.context,
                        device_id=device.id,
                        endpoint_id=device_endpoint.id,
                        device_driver_class_id=device_driver_class.id,
                        service_worker_id=self.service_worker_id
                    )
                if len(device_drivers) >= 1:
                    device_driver = device_drivers[0]
                    LOG.info('Device Driver %s is existing' %
                             device_driver)
