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
from oslo_db import api

CONF = cfg.CONF

_BACKEND_MAPPING = {'sqlalchemy': 'namos.db.sqlalchemy.api'}

IMPL = api.DBAPI.from_config(CONF, backend_mapping=_BACKEND_MAPPING)


def get_engine():
    return IMPL.get_engine()


def get_session():
    return IMPL.get_session()


# TODO(kanagaraj-manickam): Add db wrapper function to capture the db
# exception in each of the below methods and log it

# Region

def region_create(context, values):
    return IMPL.region_create(context, values)


def region_update(context, _id, values):
    return IMPL.region_update(context, _id, values)


def region_get(context, _id):
    return IMPL.region_get(context, _id)


def region_get_by_name(context, name):
    return IMPL.region_get_by_name(context, name)


def region_get_all(context):
    return IMPL.region_get_all(context)


def region_delete(context, _id):
    return IMPL.region_delete(context, _id)


# Device

def device_create(context, values):
    return IMPL.device_create(context, values)


def device_update(context, _id, values):
    return IMPL.device_update(context, _id, values)


def device_get(context, _id):
    return IMPL.device_get(context, _id)


def device_get_by_name(context, name):
    return IMPL.device_get_by_name(context, name)


def device_get_all(context):
    return IMPL.device_get_all(context)


def device_delete(context, _id):
    return IMPL.device_delete(context, _id)


# Device Endpoint

def device_endpoint_create(context, values):
    return IMPL.device_endpoint_create(context, values)


def device_endpoint_update(context, _id, values):
    return IMPL.device_endpoint_update(context, _id, values)


def device_endpoint_get(context, _id):
    return IMPL.device_endpoint_get(context, _id)


def device_endpoint_get_by_name(context, name):
    return IMPL.device_endpoint_get_by_name(context, name)


def device_endpoint_get_by_device_type(context,
                                       device_id,
                                       type=None,
                                       name=None):
    return IMPL.device_endpoint_get_by_device_type(context, device_id,
                                                   type, name)


def device_endpoint_get_all(context):
    return IMPL.device_endpoint_get_all(context)


def device_endpoint_delete(context, _id):
    return IMPL.device_endpoint_delete(context, _id)


# Device Driver

def device_driver_create(context, values):
    return IMPL.device_driver_create(context, values)


def device_driver_update(context, _id, values):
    return IMPL.device_driver_update(context, _id, values)


def device_driver_get(context, _id):
    return IMPL.device_driver_get(context, _id)


def device_driver_get_by_name(context, name):
    return IMPL.device_driver_get_by_name(context, name)


def device_driver_get_by_device_endpoint_service_worker(
        context,
        device_id=None,
        endpoint_id=None,
        device_driver_class_id=None,
        service_worker_id=None):
    return IMPL.device_driver_get_by_device_endpoint_service_worker(
        context,
        device_id,
        endpoint_id,
        device_driver_class_id,
        service_worker_id)


def device_driver_get_all(context):
    return IMPL.device_driver_get_all(context)


def device_driver_delete(context, _id):
    return IMPL.device_driver_delete(context, _id)


# Device Driver Class

def device_driver_class_create(context, values):
    return IMPL.device_driver_class_create(context, values)


def device_driver_class_update(context, _id, values):
    return IMPL.device_driver_class_update(context, _id, values)


def device_driver_class_get(context, _id):
    return IMPL.device_driver_class_get(context, _id)


def device_driver_class_get_by_name(context, name):
    return IMPL.device_driver_class_get_by_name(context, name)


def device_driver_class_get_all(context):
    return IMPL.device_driver_class_get_all(context)


def device_driver_class_delete(context, _id):
    return IMPL.device_driver_class_delete(context, _id)


# Service

def service_create(context, values):
    return IMPL.service_create(context, values)


def service_update(context, _id, values):
    return IMPL.service_update(context, _id, values)


def service_get(context, _id):
    return IMPL.service_get(context, _id)


def service_get_by_name(context, name):
    return IMPL.service_get_by_name(context, name)


def service_get_all(context):
    return IMPL.service_get_all(context)


def service_delete(context, _id):
    return IMPL.service_delete(context, _id)


# Service Node

def service_node_create(context, values):
    return IMPL.service_node_create(context, values)


def service_node_update(context, _id, values):
    return IMPL.service_node_update(context, _id, values)


def service_node_get(context, _id):
    return IMPL.service_node_get(context, _id)


def service_node_get_by_name(context, name):
    return IMPL.service_node_get_by_name(context, name)


def service_node_get_all(context):
    return IMPL.service_node_get_all(context)


def service_node_delete(context, _id):
    return IMPL.service_node_delete(context, _id)


# Service Component

def service_component_create(context, values):
    return IMPL.service_component_create(context, values)


def service_component_update(context, _id, values):
    return IMPL.service_component_update(context, _id, values)


def service_component_get(context, _id):
    return IMPL.service_component_get(context, _id)


def service_component_get_by_name(context, name):
    return IMPL.service_component_get_by_name(context, name)


def service_component_get_all_by_node_for_service(context,
                                                  node_id,
                                                  service_id=None,
                                                  name=None):
    return IMPL.service_component_get_all_by_node_for_service(context,
                                                              node_id,
                                                              service_id,
                                                              name)


def service_component_get_all(context):
    return IMPL.service_component_get_all(context)


def service_component_get_all_by_config_file(context, config_file_id):
    return IMPL.service_component_get_all_by_config_file(context,
                                                         config_file_id)


def service_component_delete(context, _id):
    return IMPL.service_component_delete(context, _id)


#  Service Worker
def service_worker_create(context, values):
    return IMPL.service_worker_create(context, values)


def service_worker_update(context, _id, values):
    return IMPL.service_worker_update(context, _id, values)


def service_worker_get(context, _id):
    return IMPL.service_worker_get(context, _id)


def service_worker_get_by_name(context, name):
    return IMPL.service_worker_get_by_name(context, name)


def service_worker_get_by_host_for_service_component(context,
                                                     service_component_id,
                                                     host=None):
    return IMPL.service_worker_get_by_host_for_service_component(
        context,
        service_component_id,
        host)


def service_worker_get_all(context):
    return IMPL.service_worker_get_all(context)


def service_worker_get_all_by(context, **kwargs):
    return IMPL.service_worker_get_all_by(context, **kwargs)


def service_worker_delete(context, _id):
    return IMPL.service_worker_delete(context, _id)


def config_file_entry_create(context, values):
    return IMPL.config_file_entry_create(context, values)


def config_file_entry_update(context, _id, values):
    return IMPL.config_file_entry_update(context, _id, values)


def config_file_entry_get(context, _id):
    return IMPL.config_file_entry_get(context, _id)


def config_file_entry_get_by_name(context, name):
    return IMPL.config_file_entry_get_by_name(context, name)


def config_file_entry_get_all(context):
    return IMPL.config_file_entry_get_all(context)


def config_file_entry_get_all_by(context, **kwargs):
    return IMPL.config_file_entry_get_all_by(context, **kwargs)


def config_file_entry_delete(context, _id):
    return IMPL.config_file_entry_delete(context, _id)


#  config schema
def config_schema_create(context, values):
    return IMPL.config_schema_create(context, values)


def config_schema_update(context, _id, values):
    return IMPL.config_schema_update(context, _id, values)


def config_schema_get(context, _id):
    return IMPL.config_schema_get(context, _id)


def config_schema_get_by_name(context, name):
    return IMPL.config_schema_get_by_name(context, name)


def config_schema_get_by(context,
                         namespace=None,
                         group=None,
                         name=None,
                         project=None):
    return IMPL.config_schema_get_by(context, namespace, group, name, project)


def config_schema_get_all(context):
    return IMPL.config_schema_get_all(context)


def config_schema_get_all_by(context, **kwargs):
    return IMPL.config_schema_get_all_by(context, **kwargs)


def config_schema_delete(context, _id):
    return IMPL.config_schema_delete(context, _id)


#  Config
def config_create(context, values):
    return IMPL.config_create(context, values)


def config_update(context, _id, values):
    return IMPL.config_update(context, _id, values)


def config_get(context, _id):
    return IMPL.config_get(context, _id)


def config_get_by_name(context, name):
    return IMPL.config_get_by_name(context, name)


def config_get_by_name_for_service_worker(context,
                                          service_worker_id,
                                          name=None,
                                          only_configured=True):
    return IMPL.config_get_by_name_for_service_worker(context,
                                                      service_worker_id,
                                                      name,
                                                      only_configured)


def config_get_all(context):
    return IMPL.config_get_all(context)


def config_delete(context, _id):
    return IMPL.config_delete(context, _id)


# config file

def config_file_create(context, values):
    return IMPL.config_file_create(context, values)


def config_file_update(context, _id, values):
    return IMPL.config_file_update(context, _id, values)


def config_file_get(context, _id):
    return IMPL.config_file_get(context, _id)


def config_file_get_by_name(context, name):
    return IMPL.config_file_get_by_name(context, name)


def config_file_get_by_name_for_service_node(
        context,
        service_node_id,
        name=None):
    return IMPL.config_file_get_by_name_for_service_node(
        context,
        service_node_id,
        name)


def config_file_get_all(context):
    return IMPL.config_file_get_all(context)


def config_file_delete(context, _id):
    return IMPL.config_file_delete(context, _id)


def service_perspective_get(context, service_id,
                            include_details=False):
    return IMPL.service_perspective_get(context,
                                        service_id,
                                        include_details)


def device_perspective_get(context, device_id,
                           include_details=False):
    return IMPL.device_perspective_get(context,
                                       device_id,
                                       include_details)


def region_perspective_get(context, region_id,
                           include_details=False):
    return IMPL.region_perspective_get(context,
                                       region_id,
                                       include_details)


def infra_perspective_get(context):
    return IMPL.infra_perspective_get(context)


def view_360(context, include_conf_file=False, include_status=False):
    return IMPL.view_360(context,
                         include_conf_file=include_conf_file,
                         include_status=include_status)


def get_status(context, node=None, service=None, type=None, component=None):
    return IMPL.get_status(context, node, service, type, component)


def cleanup(context, service_component_id=None, dead_since=300):
    return IMPL.cleanup(context, service_component_id, dead_since)
