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


import sys

from oslo_config import cfg
from oslo_db import exception as db_exception
from oslo_db.sqlalchemy import session as db_session

from namos.common import exception
from namos.common import utils
from namos.db.sqlalchemy import models


CONF = cfg.CONF

_facade = None


def get_facade():
    global _facade

    if not _facade:
        _facade = db_session.EngineFacade.from_config(CONF)
    return _facade


get_engine = lambda: get_facade().get_engine()
get_session = lambda: get_facade().get_session()


def get_backend():
    """The backend is this module itself."""
    return sys.modules[__name__]


def _model_query(context, *args):
    session = _session(context)
    query = session.query(*args)

    return query


def _session(context):
    return (context and hasattr(context, 'session') and context.session) \
        or get_session()


def _create(context, resource_ref, values):
    resource_ref.update(values)
    try:
        resource_ref.save(_session(context))
    except db_exception.DBDuplicateEntry:
        raise exception.AlreadyExist(model=resource_ref.__class__.__name__,
                                     name=resource_ref.name)
    return resource_ref


def _update(context, cls, _id, values):
    resource_ref = _get(context, cls, _id)
    resource_ref.update_and_save(values, _session(context))
    return resource_ref


def _get(context, cls, _id):
    result = _model_query(context, cls).get(_id)
    return result


def _get_by_name(context, cls, name):
    result = _model_query(context, cls). \
        filter_by(name=name).first()
    return result


# TODO(kanagaraj-manickam): Add pagination
def _get_all(context, cls):
    results = _model_query(context, cls).all()

    if results is None:
        results = []

    return results


def _get_all_by(context, cls, **kwargs):
    results = _model_query(context, cls).filter_by(**kwargs).all()
    return results


def _delete(context, cls, _id, soft=True):
    result = _get(context, cls, _id)
    if result is not None:
        if soft and hasattr(result, 'soft_delete'):
            result.soft_delete(_session(context))
            return
        # TODO(mrkanag) is it ok to hard delete when soft =True and soft_delete
        # is missing
        result.delete(_session(context))


# Region

def region_create(context, values):
    return _create(context, models.Region(), values)


def region_update(context, _id, values):
    return _update(context, models.Region, _id, values)


def region_get(context, _id):
    region = _get(context, models.Region, _id)
    if region is None:
        raise exception.RegionNotFound(region_id=_id)

    return region


def region_get_by_name(context, name):
    region = _get_by_name(context, models.Region, name)
    if region is None:
        raise exception.RegionNotFound(region_id=name)

    return region


def region_get_all(context):
    return _get_all(context, models.Region)


def region_delete(context, _id):
    return _delete(context, models.Region, _id)


# Device

def device_create(context, values):
    return _create(context, models.Device(), values)


def device_update(context, _id, values):
    return _update(context, models.Device, _id, values)


def device_get(context, _id):
    region = _get(context, models.Device, _id)
    if region is None:
        raise exception.DeviceNotFound(device_id=_id)

    return region


def device_get_by_name(context, name):
    region = _get_by_name(context, models.Device, name)
    if region is None:
        raise exception.DeviceNotFound(device_id=name)

    return region


def device_get_all(context):
    return _get_all(context, models.Device)


def device_get_all_by(context, **kwargs):
    return _get_all_by(context, models.Device, **kwargs)


def device_delete(context, _id):
    return _delete(context, models.Device, _id)


# Device Endpoint

def device_endpoint_create(context, values):
    return _create(context, models.DeviceEndpoint(), values)


def device_endpoint_update(context, _id, values):
    return _update(context, models.DeviceEndpoint, _id, values)


def device_endpoint_get(context, _id):
    region = _get(context, models.DeviceEndpoint, _id)
    if region is None:
        raise exception.DeviceEndpointNotFound(device_endpoint_id=_id)

    return region


def device_endpoint_get_by_name(context, name):
    region = _get_by_name(context, models.DeviceEndpoint, name)
    if region is None:
        raise exception.DeviceEndpointNotFound(device_endpoint_id=name)

    return region


def device_endpoint_get_by_device_type(context,
                                       device_id,
                                       type=None,
                                       name=None):
    query = _model_query(context, models.DeviceEndpoint)
    if device_id is not None:
        query = query.filter_by(device_id=device_id)
    if type is not None:
        query = query.filter_by(type=type)
    if name is not None:
        query = query.filter_by(name=name)
    return query.all()


def device_endpoint_get_all(context):
    return _get_all(context, models.DeviceEndpoint)


def device_endpoint_get_all_by(context, **kwargs):
    return _get_all_by(context, models.DeviceEndpoint, **kwargs)


def device_endpoint_delete(context, _id):
    return _delete(context, models.DeviceEndpoint, _id)


# Device Driver
def device_driver_create(context, values):
    return _create(context, models.DeviceDriver(), values)


def device_driver_update(context, _id, values):
    return _update(context, models.DeviceDriver, _id, values)


def device_driver_get(context, _id):
    region = _get(context, models.DeviceDriver, _id)
    if region is None:
        raise exception.DeviceDriverNotFound(device_driver_id=_id)

    return region


def device_driver_get_by_name(context, name):
    region = _get_by_name(context, models.DeviceDriver, name)
    if region is None:
        raise exception.DeviceDriverNotFound(device_driver_id=name)

    return region


def device_driver_get_by_device_endpoint_service_worker(
        context,
        device_id=None,
        endpoint_id=None,
        device_driver_class_id=None,
        service_worker_id=None):
    query = _model_query(context, models.DeviceDriver)
    if device_id is not None:
        query = query.filter_by(device_id=device_id)
    if endpoint_id is not None:
        query = query.filter_by(endpoint_id=endpoint_id)
    if device_driver_class_id is not None:
        query = query.filter_by(device_driver_class_id=device_driver_class_id)
    if service_worker_id is not None:
        query = query.filter_by(service_worker_id=service_worker_id)
    return query.all()


def device_driver_get_all(context):
    return _get_all(context, models.DeviceDriver)


def device_driver_get_all_by(context, **kwargs):
    return _get_all_by(context, models.DeviceDriver, **kwargs)


def device_driver_delete(context, _id):
    return _delete(context, models.DeviceDriver, _id)


# Device Driver Class

def device_driver_class_create(context, values):
    return _create(context, models.DeviceDriverClass(), values)


def device_driver_class_update(context, _id, values):
    return _update(context, models.DeviceDriverClass, _id, values)


def device_driver_class_get(context, _id):
    region = _get(context, models.DeviceDriverClass, _id)
    if region is None:
        raise exception.DeviceDriverClassNotFound(device_driver_id=_id)

    return region


def device_driver_class_get_by_name(context, name):
    region = _get_by_name(context, models.DeviceDriverClass, name)
    if region is None:
        raise exception.DeviceDriverClassNotFound(device_driver_class_id=name)

    return region


def device_driver_class_get_all(context):
    return _get_all(context, models.DeviceDriverClass)


def device_driver_class_get_all_by(context, **kwargs):
    return _get_all_by(context, models.DeviceDriverClass, **kwargs)


def device_driver_class_delete(context, _id):
    return _delete(context, models.DeviceDriverClass, _id)


# Service

def service_create(context, values):
    return _create(context, models.Service(), values)


def service_update(context, _id, values):
    return _update(context, models.Service, _id, values)


def service_get(context, _id):
    region = _get(context, models.Service, _id)
    if region is None:
        raise exception.ServiceNotFound(service_id=_id)

    return region


def service_get_by_name(context, name):
    region = _get_by_name(context, models.Service, name)
    if region is None:
        raise exception.ServiceNotFound(service_id=name)

    return region


def service_get_all(context):
    return _get_all(context, models.Service)


def service_get_all_by(context, **kwargs):
    return _get_all_by(context, models.Service, **kwargs)


def service_delete(context, _id):
    return _delete(context, models.Service, _id)


# ServiceNode

def service_node_create(context, values):
    return _create(context, models.ServiceNode(), values)


def service_node_update(context, _id, values):
    return _update(context, models.ServiceNode, _id, values)


def service_node_get(context, _id):
    region = _get(context, models.ServiceNode, _id)
    if region is None:
        raise exception.ServiceNodeNotFound(service_node_id=_id)

    return region


def service_node_get_by_name(context, name):
    region = _get_by_name(context, models.ServiceNode, name)
    if region is None:
        raise exception.ServiceNodeNotFound(service_node_id=name)

    return region


def service_node_get_all(context):
    return _get_all(context, models.ServiceNode)


def service_node_get_all_by(context, **kwargs):
    return _get_all_by(context, models.ServiceNode, **kwargs)


def service_node_delete(context, _id):
    return _delete(context, models.ServiceNode, _id)


# ServiceComponent

def service_component_create(context, values):
    return _create(context, models.ServiceComponent(), values)


def service_component_update(context, _id, values):
    return _update(context, models.ServiceComponent, _id, values)


def service_component_get(context, _id):
    region = _get(context, models.ServiceComponent, _id)
    if region is None:
        raise exception.ServiceComponentNotFound(service_component_id=_id)

    return region


def service_component_get_by_name(context, name):
    region = _get_by_name(context, models.ServiceComponent, name)
    if region is None:
        raise exception.ServiceComponentNotFound(service_component_id=name)

    return region


def service_component_get_all_by_node_for_service(context,
                                                  node_id,
                                                  service_id=None,
                                                  name=None):
    query = _model_query(context, models.ServiceComponent). \
        filter_by(node_id=node_id)
    if service_id is not None:
        query = query.filter_by(service_id=service_id)
    if name is not None:
        query = query.filter_by(name=name)

    query = query.order_by(models.ServiceComponent.type)
    return query.all()


def service_component_get_all_by_config_file(context, config_file_id):
    query = _model_query(context,
                         models.OsloConfigFileEntry.service_component_id). \
        filter_by(oslo_config_file_id=config_file_id).distinct()
    query_sc = _model_query(context, models.ServiceComponent).filter(
        models.ServiceComponent.id.in_(query)
    )

    return query_sc.all()


def service_component_get_all(context):
    return _get_all(context, models.ServiceComponent)


def service_component_get_all_by(context, **kwargs):
    return _get_all_by(context, models.ServiceComponent, **kwargs)


def service_component_delete(context, _id):
    return _delete(context, models.ServiceComponent, _id)


# ServiceWorker

def service_worker_create(context, values):
    return _create(context, models.ServiceWorker(), values)


def service_worker_update(context, _id, values):
    return _update(context, models.ServiceWorker, _id, values)


def service_worker_get(context, _id):
    service_worker = _get(context, models.ServiceWorker, _id)
    if service_worker is None:
        raise exception.ServiceWorkerNotFound(service_worker_id=_id)

    return service_worker


def service_worker_get_by_name(context, name):
    service_worker = _get_by_name(context, models.ServiceWorker, name)
    if service_worker is None:
        raise exception.ServiceWorkerNotFound(service_worker_id=name)

    return service_worker


def service_worker_get_by_host_for_service_component(context,
                                                     service_component_id,
                                                     host=None):
    query = _model_query(context, models.ServiceWorker). \
        filter_by(service_component_id=service_component_id)
    if host is not None:
        query = query.filter_by(host=host)

    return query.all()


def service_worker_get_all(context):
    return _get_all(context, models.ServiceWorker)


def service_worker_get_all_by(context, **kwargs):
    return _get_all_by(context, models.ServiceWorker, **kwargs)


def service_worker_delete(context, _id):
    return _delete(context, models.ServiceWorker, _id)


# Config Schema

def config_schema_create(context, values):
    return _create(context, models.OsloConfigSchema(), values)


def config_schema_update(context, _id, values):
    return _update(context, models.OsloConfigSchema, _id, values)


def config_schema_get(context, _id):
    config = _get(context, models.OsloConfigSchema, _id)
    if config is None:
        raise exception.ConfigNotFound(config_schema_id=_id)

    return config


def config_schema_get_by_name(context, name):
    config = _get_by_name(context, models.OsloConfigSchema, name)
    if config is None:
        raise exception.ConfigSchemaNotFound(config_schema_id=name)

    return config


def config_schema_get_by(context,
                         namespace=None,
                         group=None,
                         name=None,
                         project=None):
    query = _model_query(context, models.OsloConfigSchema)
    if name is not None:
        query = query.filter_by(name=name)
    if group is not None:
        query = query.filter_by(group_name=group)
    if namespace is not None:
        query = query.filter_by(namespace=namespace)
    if project is not None:
        query = query.filter_by(project=project)

    return query.all()


def config_schema_get_all(context):
    return _get_all(context, models.OsloConfigSchema)


def config_schema_get_all_by(context, **kwargs):
    return _get_all_by(context, models.OsloConfigSchema, **kwargs)


def config_schema_delete(context, _id):
    return _delete(context, models.OsloConfigSchema, _id)


# Config

def config_create(context, values):
    return _create(context, models.OsloConfig(), values)


def config_update(context, _id, values):
    return _update(context, models.OsloConfig, _id, values)


def config_get(context, _id):
    config = _get(context, models.OsloConfig, _id)
    if config is None:
        raise exception.ConfigNotFound(config_id=_id)

    return config


def config_get_by_name(context, name):
    config = _get_by_name(context, models.OsloConfig, name)
    if config is None:
        raise exception.ConfigNotFound(config_id=name)

    return config


def config_get_by_name_for_service_worker(context,
                                          service_worker_id,
                                          name=None,
                                          only_configured=True):
    query = _model_query(context, models.OsloConfig). \
        filter_by(service_worker_id=service_worker_id)
    if name is not None:
        query = query.filter_by(name=name)
    elif only_configured:
        query = query.filter(
            models.OsloConfig.oslo_config_file_entry_id is not None)
    return query.all()


def config_get_all(context):
    return _get_all(context, models.OsloConfig)


def config_get_all_by(context, **kwargs):
    return _get_all_by(context, models.OsloConfig, **kwargs)


def config_delete(context, _id):
    return _delete(context, models.OsloConfig, _id)


# Config File Entry

def config_file_entry_create(context, values):
    return _create(context, models.OsloConfigFileEntry(), values)


def config_file_entry_update(context, _id, values):
    return _update(context, models.OsloConfigFileEntry, _id, values)


def config_file_entry_get(context, _id):
    config_file_entry = _get(context, models.OsloConfigFileEntry, _id)
    if config_file_entry is None:
        raise exception.ConfigNotFound(config_file_entry_id=_id)

    return config_file_entry


def config_file_entry_get_by_name(context, name):
    config_file_entry = _get_by_name(context, models.OsloConfigFileEntry, name)
    if config_file_entry is None:
        raise exception.ConfigNotFound(config_file_entry_id=name)

    return config_file_entry


def config_file_entry_get_all(context):
    return _get_all(context, models.OsloConfigFileEntry)


def config_file_entry_get_all_by(context, **kwargs):
    return _get_all_by(context, models.OsloConfigFileEntry, **kwargs)


def config_file_entry_delete(context, _id):
    return _delete(context, models.OsloConfigFileEntry, _id)


# Config file
def config_file_create(context, values):
    return _create(context, models.OsloConfigFile(), values)


def config_file_update(context, _id, values):
    return _update(context, models.OsloConfigFile, _id, values)


def config_file_get(context, _id):
    config = _get(context, models.OsloConfigFile, _id)
    if config is None:
        raise exception.ConfigFileNotFound(config_file_id=_id)

    return config


def config_file_get_by_name(context, name):
    config = _get_by_name(context, models.OsloConfigFile, name)
    if config is None:
        raise exception.ConfigFileNotFound(config_file_id=name)

    return config


def config_file_get_by_name_for_service_node(
        context,
        service_node_id,
        name=None):
    query = _model_query(context, models.OsloConfigFile). \
        filter_by(service_node_id=service_node_id)
    if name is not None:
        query = query.filter_by(name=name)

    return query.all()


def _config_file_id_get_for_service_component(context, service_component_id):
    entries = config_file_entry_get_all_by(
        context,
        service_component_id=service_component_id)
    files = []
    for e in entries:
        if e.oslo_config_file_id not in files:
            files.append(e.oslo_config_file_id)

    return files


def config_file_get_all(context):
    return _get_all(context, models.OsloConfigFile)


def config_file_get_all_by(context, **kwargs):
    return _get_all_by(context, models.OsloConfigFile, **kwargs)


def config_file_delete(context, _id):
    return _delete(context, models.OsloConfigFile, _id)


# REST-API
def service_perspective_get(context, service_id, include_details=False):
    # 1. itr over Service Components and find name vs set of components
    #      (for example, nova-compute vs set of nova-compute deployment)
    #      Mention the service_node
    # 2. For each components, itr over Service Workers
    # 3. For each workers, itr over device_drivers
    # 4. For each device_driver, Mention
    #               device_driver_class
    #               device_endpoint<->device

    # on include_details, for each of the entity, include complete details
    service_perspective = dict()
    service_perspective['service'] = service_get(context, service_id).to_dict()
    service_components = service_component_get_all_by(context,
                                                      service_id=service_id)
    service_perspective['service_components'] = dict()
    # service_perspective['service_components']['size'] =
    # len(service_components)

    for sc in service_components:
        service_perspective['service_components'][sc.id] = dict()
        service_perspective['service_components'][sc.id]['service_component']\
            = sc.to_dict()
        service_perspective['service_components'][sc.id]['service_node']\
            = service_node_get(context, sc.node_id).to_dict()
        service_workers = service_worker_get_all_by(
            context,
            service_component_id=sc.id)
        service_perspective['service_components'][sc.id]['service_workers'] \
            = dict()
        # service_perspective['service_components'][sc.id]\
        # ['service_workers']['size'] = len(service_workers)

        for sw in service_workers:
            service_perspective['service_components'][
                sc.id]['service_workers'][sw.id] = dict()
            service_perspective['service_components'][
                sc.id]['service_workers'][sw.id][
                'service_worker'] = sw.to_dict()

            device_drivers = device_driver_get_all_by(
                context,
                service_worker_id=sw.id)
            service_perspective['service_components'][
                sc.id]['service_workers'][sw.id]['device_drivers'] = dict()

            # service_perspective['service_components'][sc.id]\
            # ['service_workers'][sw.id]['device_drivers']['size'] \
            #     = len(device_drivers)
            for driver in device_drivers:
                service_perspective['service_components'][
                    sc.id]['service_workers'][sw.id]['device_drivers'][
                    driver.id] = dict()
                service_perspective['service_components'][
                    sc.id]['service_workers'][sw.id]['device_drivers'][
                    driver.id]['driver'] = driver.to_dict()
                service_perspective['service_components'][
                    sc.id]['service_workers'][sw.id]['device_drivers'][
                    driver.id]['device_endpoint'] = device_endpoint_get(
                    context,
                    driver.endpoint_id).to_dict()
                service_perspective['service_components'][
                    sc.id]['service_workers'][sw.id]['device_drivers'][
                    driver.id]['device'] = device_get(
                    context,
                    driver.device_id).to_dict()
                service_perspective['service_components'][
                    sc.id]['service_workers'][sw.id]['device_drivers'][
                    driver.id][
                    'device_driver_class'] = device_driver_class_get(
                    context,
                    driver.device_driver_class_id
                ).to_dict()

    return service_perspective


# REST-API
def device_perspective_get(context, device_id, include_details=False):
    # 1. list endpoints
    # 2. For each endpoint, itr over device_drivers and
    # find device_driver_class vs set of device_driver (for example,
    # nova-compute-vc-driver vs set of nova-compute's device-driver deployment)
    # 3. For each drivers, mention service_worker,
    #    service_component<->service_node<->service

    # on include_details, for each of the entity, include complete details
    device_perspective = dict()
    device_perspective['device'] = device_get(context, device_id).to_dict()
    endpoints = device_endpoint_get_all_by(context,
                                           device_id=device_id)
    device_perspective['device_endpoints'] = dict()
    # device_perspective['device_endpoints']['size'] = len(endpoints)

    for ep in endpoints:
        device_perspective['device_endpoints'][ep.id] = dict()
        device_perspective['device_endpoints'][
            ep.id]['device_endpoint'] = ep.to_dict()

        device_drivers = device_driver_get_all_by(context,
                                                  endpoint_id=ep.id)
        device_perspective['device_endpoints'][
            ep.id]['device_drivers'] = dict()
        # device_perspective['device_endpoints'][ep.id] \
        # ['device_drivers']['size'] = len(device_drivers)

        for driver in device_drivers:
            device_perspective['device_endpoints'][
                ep.id]['device_drivers'][driver.id] = dict()
            device_perspective['device_endpoints'][
                ep.id]['device_drivers'][driver.id][
                'device_driver'] = driver.to_dict()

            service_worker = service_worker_get(
                context,
                driver.service_worker_id)
            service_component = service_component_get(
                context,
                service_worker.service_component_id)
            device_perspective['device_endpoints'][
                ep.id]['device_drivers'][
                driver.id]['service_worker'] = service_worker.to_dict()
            service = service_get(context, service_component.service_id)

            device_perspective['device_endpoints'][
                ep.id]['device_drivers'][
                driver.id]['service_component'] = service_component.to_dict()

            device_perspective['device_endpoints'][
                ep.id]['device_drivers'][
                driver.id]['service'] = service.to_dict()
            device_perspective['device_endpoints'][
                ep.id]['device_drivers'][driver.id][
                'device_driver_class'] = device_driver_class_get(
                    context,
                    driver.device_driver_class_id
                ).to_dict()

    return device_perspective


# REST-API
def region_perspective_get(context, region_id, include_details=False):
    # itr over service_nodes
    #   For each service_nodes, itr over service_id
    # itr over devices.

    # on include_details, for each of the entity, include complete details

    region_perspective = dict()
    region_perspective['region'] = region_get(context, region_id).to_dict()
    s_nodes = service_node_get_all_by(context,
                                      region_id=region_id)
    # region_perspective['service_nodes'] = dict()
    # region_perspective['service_nodes']['size'] = len(s_nodes)
    # for s_node in s_nodes:
    #     region_perspective['service_nodes'][s_node.id] = dict()
    #     region_perspective['service_nodes'][s_node.id]['service_node']\
    #         = s_node
    #     s_components = _service_component_get_all_by(context,
    #                             node_id=s_node.id)
    #     srvs = list()
    #     for s_component in s_components:
    #         srvs.append(s_component.service_id)
    #     srvs = set(srvs)
    #
    #     region_perspective['service_nodes'][s_node.id]['services'] = dict()
    #     region_perspective['service_nodes'][s_node.id]['services']['size']\
    #         = len(srvs)
    #     for s_id in srvs:
    #         s = service_get(context, s_id)
    #         region_perspective['service_nodes'][s_node.id]['services'][s_id]\
    #             = s

    region_perspective['services'] = dict()
    for s_node in s_nodes:
        s_components = service_component_get_all_by(
            context,
            node_id=s_node.id)
        srvs = list()
        for s_component in s_components:
            srvs.append(s_component.service_id)
        srvs = set(srvs)

        # region_perspective['services']['size']\
        #     = len(srvs)
        for s_id in srvs:
            s = service_get(context, s_id)
            region_perspective['services'][s_id] = s.to_dict()

    devices = device_get_all_by(context, region_id=region_id)
    region_perspective['devices'] = dict()
    # region_perspective['devices']['size'] = len(devices)
    for d in devices:
        region_perspective['devices'][d.id] = d.to_dict()

    return region_perspective


def infra_perspective_get(context):
    infra_perspective = dict()

    regions = region_get_all(context)
    infra_perspective['regions'] = dict()
    # infra_perspective['regions']['size'] = len(regions)

    for region in regions:
        infra_perspective['regions'][region.id] = dict()
        infra_perspective['regions'][region.id]['region'] = region.to_dict()
        region_perspective = region_perspective_get(context,
                                                    region.id)

        infra_perspective['regions'][region.id]['services'] = dict()
        for s_id in region_perspective['services']:
            infra_perspective['regions'][
                region.id]['services'][s_id] = service_perspective_get(
                context,
                s_id)

        infra_perspective['regions'][region.id]['devices'] = dict()
        for d_id in region_perspective['devices']:
            infra_perspective['regions'][region.id]['devices'][
                d_id] = device_perspective_get(
                context,
                d_id)

    return infra_perspective


def view_360(context, include_conf_file=False, include_status=False):
    view = dict()

    view['region'] = dict()
    view['service_node'] = dict()
    view['service_component'] = dict()
    view['service'] = dict()
    view['service_worker'] = dict()
    view['device_driver'] = dict()
    view['device_driver_class'] = dict()
    view['device_endpoint'] = dict()
    view['device'] = dict()
    view['config_file'] = dict()
    view['status'] = dict()

    region_list = region_get_all(context)
    for rg in region_list:
        # region
        view['region'][rg.id] = region_get(context, rg.id).to_dict()

        view['region'][rg.id]['service_node'] = dict()
        srv_nd_lst = service_node_get_all_by(context,
                                             region_id=rg.id)
        for srv_nd in srv_nd_lst:
            # service node
            view['service_node'][srv_nd.id] = service_node_get(
                context,
                srv_nd.id
            ).to_dict()

            view['region'][rg.id]['service_node'][srv_nd.id] = dict()
            view['region'][rg.id]['service_node'][srv_nd.id][
                'service_component'] = dict()
            srv_cmp_lst = service_component_get_all_by_node_for_service(
                context,
                srv_nd.id
            )
            for srv_cmp in srv_cmp_lst:
                # service component
                view['service_component'][
                    srv_cmp.id] = service_component_get(context,
                                                        srv_cmp.id).to_dict()

                # service
                srv_id = view['service_component'][srv_cmp.id]['service_id']
                if srv_id not in view['service']:
                    view['service'][srv_id] = service_get(context,
                                                          srv_id).to_dict()

                view['region'][rg.id]['service_node'][srv_nd.id][
                    'service_component'][srv_cmp.id] = dict()
                view['region'][rg.id]['service_node'][srv_nd.id][
                    'service_component'][srv_cmp.id]['config_file'] = dict()
                cfg_fl_lst = _config_file_id_get_for_service_component(
                    context,
                    service_component_id=srv_cmp.id
                )
                for cfg_fl_id in cfg_fl_lst:
                    # config file
                    if include_conf_file:
                        view['config_file'][cfg_fl_id] = config_file_get(
                            context,
                            cfg_fl_id
                        )
                    else:
                        view['config_file'][cfg_fl_id] = dict()

                    view['region'][rg.id]['service_node'][srv_nd.id][
                        'service_component'][srv_cmp.id][
                        'config_file'][cfg_fl_id] = dict()

                view['region'][rg.id]['service_node'][srv_nd.id][
                    'service_component'][srv_cmp.id]['service'] = srv_id
                view['region'][rg.id]['service_node'][srv_nd.id][
                    'service_component'][srv_cmp.id][
                    'service_worker'] = dict()
                srv_wkr_lst = service_worker_get_by_host_for_service_component(
                    context,
                    srv_cmp.id
                )
                for srv_wkr in srv_wkr_lst:
                    # service worker
                    view['service_worker'][
                        srv_wkr.id] = service_worker_get(context,
                                                         srv_wkr.id).to_dict()

                    view['region'][rg.id]['service_node'][srv_nd.id][
                        'service_component'][srv_cmp.id][
                        'service_worker'][srv_wkr.id] = dict()
                    view['region'][rg.id]['service_node'][srv_nd.id][
                        'service_component'][srv_cmp.id][
                        'service_worker'][srv_wkr.id]['device_driver'] = dict()
                    dvc_drv_list = device_driver_get_all_by(
                        context,
                        service_worker_id=srv_wkr.id
                    )
                    for dvc_drv in dvc_drv_list:
                        # device driver
                        view['device_driver'][
                            dvc_drv.id] = device_driver_get(
                            context,
                            dvc_drv.id).to_dict()

                        view['region'][rg.id]['service_node'][srv_nd.id][
                            'service_component'][srv_cmp.id][
                            'service_worker'][srv_wkr.id]['device_driver'][
                            dvc_drv.id] = dict()

                        # device driver class
                        dvc_drv_cls_id = view['device_driver'][
                            dvc_drv.id]['device_driver_class_id']
                        if dvc_drv_cls_id not in view['device_driver_class']:
                            view['device_driver_class'][
                                dvc_drv_cls_id] = device_driver_class_get(
                                context,
                                dvc_drv_cls_id).to_dict()
                        view['region'][rg.id]['service_node'][srv_nd.id][
                            'service_component'][srv_cmp.id][
                            'service_worker'][srv_wkr.id]['device_driver'][
                            dvc_drv.id]['device_driver_class'] = dvc_drv_cls_id

                        # device endpoint
                        dvc_endp_id = view['device_driver'][
                            dvc_drv.id]['endpoint_id']
                        view['device_endpoint'][
                            dvc_endp_id] = device_endpoint_get(
                            context,
                            dvc_endp_id).to_dict()
                        view['region'][rg.id]['service_node'][srv_nd.id][
                            'service_component'][srv_cmp.id][
                            'service_worker'][srv_wkr.id]['device_driver'][
                            dvc_drv.id]['device_endpoint'] = dvc_endp_id

                        # device
                        dvc_id = view['device_driver'][
                            dvc_drv.id]['device_id']
                        if dvc_id not in view['device']:
                            view['device'][
                                dvc_id] = device_get(
                                context,
                                dvc_id).to_dict()
                            view['region'][rg.id]['service_node'][srv_nd.id][
                                'service_component'][srv_cmp.id][
                                'service_worker'][srv_wkr.id]['device_driver'][
                                dvc_drv.id]['device'] = dvc_id

    if include_status:
        view['status'] = get_status(context)

    return view


def get_status(context, node=None, service=None, type=None, component=None):
    sr = {}
    for sn in service_node_get_all(context):
        if node and not node == sn.name:
            continue

        for sc in service_component_get_all_by_node_for_service(
            context,
            node_id=sn.id
        ):
            if sc.deleted_at is not None:
                continue

            s = service_get(context, sc.service_id)
            if service and not s.name == service:
                continue

            if type and not sc.type == type:
                    continue

            if component and not sc.name == component:
                continue

            for sw in service_worker_get_by_host_for_service_component(
                context,
                service_component_id=sc.id
            ):
                # TODO(mrkanag) Move this to db layer and query non deleted
                if sw.deleted_at is not None:
                    continue

                sr[sw.pid] = (
                    dict(node=sn.name,
                         type=sc.type,
                         service=s.name,
                         component=sc.name,
                         worker=sw.name,
                         status=utils.find_status(sw),
                         is_launcher=sw.is_launcher))

    return sr


def cleanup(context, service_component_id=None, dead_since=300):
    # clean up the dead service workers
    service_workers = \
        service_worker_get_all_by(
            context,
            service_component_id=service_component_id
        )

    for srv_wkr in service_workers:
        if srv_wkr.deleted_at is not None:
            continue

        if utils.find_status(srv_wkr, report_interval=dead_since):
            continue
        else:
            confs = config_get_by_name_for_service_worker(
                context,
                service_worker_id=srv_wkr.id
            )

            for conf in confs:
                config_delete(context, conf.id)

            service_worker_delete(context, srv_wkr.id)


if __name__ == '__main__':
    from namos.common import config

    config.init_conf(prog='test-run')
    # print config_get_by_name_for_service_worker(
    #     None,
    #     'f46983a4-6b42-48b0-8b66-66175fa07bc8',
    #     'database.use_db_reconnect'
    # )

    # print region_perspective_get(None,
    #                     region_id='f7dcd175-27ef-46b5-997f-e6e572f320b0')
    #
    # print service_perspective_get(None,
    #                     service_id='11367a37-976f-468a-b8dd-77b28ee63cf4')
    #
    # print device_perspective_get(
    #     None,
    #     device_id='05b935b3-942c-439c-a6a4-9c3c73285430')

    # persp = infra_perspective_get(None)
    # import json
    # perp_json = json.dumps(persp, indent=4)
    # print perp_json

    # import json
    # print (json.dumps(view_360(None, True, True)))

    sc = service_component_get_all_by_config_file(
        None,
        '03cccfb4-5433-47fc-af3c-63869f270d78')
    print (service_worker_get_all_by(None,
                                     service_component_id=sc[0].id,
                                     is_launcher=True))
