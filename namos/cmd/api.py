# -*- encoding: utf-8 -*-
#
# Copyright 2013 Hewlett-Packard Development Company, L.P.
# All Rights Reserved.
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

from bottle import route
from bottle import run

from namos.conductor import rpcapi
from oslo_context import context


@route('/v1/regions')
def regions():
    regions = rpcapi.ConductorAPI().region_get_all(
        context.get_admin_context())

    return {'regions': regions}


@route('/v1/view_360')
def infra():
    _infra = rpcapi.ConductorAPI().view_360(
        context.get_admin_context(), True, True, True)
    return {'view_360': _infra}


@route('/v1/config_schema/<service>')
def config_schema(service):
    schema = dict()
    c = rpcapi.ConductorAPI()
    schema = c.config_schema(context.RequestContext(),
                             project=service,
                             with_file_link=True)

    return dict(config_schema=schema)


# Openstack view
@route('/v1/regions/<region_id>/services')
def perspective_region_service_list(region_id):
    _region = rpcapi.ConductorAPI().region_perspective_get(
        context.get_admin_context(), region_id)
    return {'services': _region['services']}


# Data center view
@route('/v1/regions/<region_id>/devices')
def perspective_region_device_list(region_id):
    _region = rpcapi.ConductorAPI().region_perspective_get(
        context.get_admin_context(), region_id)
    return {'devices': _region['devices']}


# Openstack service view
@route('/v1/services/<service_id>')
def perspective_region_service(service_id):
    _srv = rpcapi.ConductorAPI().service_perspective_get(
        context.get_admin_context(), service_id)
    return {'service': _srv}


# Data center device view
@route('/v1/devices/<device_id>')
def perspective_region_device(device_id):
    _dvc = rpcapi.ConductorAPI().device_perspective_get(
        context.get_admin_context(), device_id)
    return {'device': _dvc}


run(host='localhost', port=9999)
