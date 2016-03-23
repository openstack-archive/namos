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

import json
import logging
import six


LOG = logging.getLogger(__name__)


class NamosException(Exception):
    msg_fmt = ("An unknown exception occurred.")
    message = None
    error_code = None
    http_status_code = None
    data = {}

    def __init__(self, **kwargs):
        self.kwargs = kwargs

        try:
            if kwargs.get('message') is not None:
                self.message = kwargs['message']
            else:
                self.message = json.dumps(
                    {'error_code': self.error_code,
                     'message': self.msg_fmt % kwargs,
                     'http_code': self.http_status_code,
                     'data': kwargs})
            if kwargs.get('data') is not None:
                self.data = kwargs['data']
        except KeyError:
            self.message = self.msg_fmt
            LOG.exception(('Exception in string format operation'))
            for name, value in six.iteritems(kwargs):
                LOG.error("%s: %s" % (name, value))  # noqa

    def __str__(self):
        return unicode(self.message).encode('UTF-8')

    def __unicode__(self):
        return unicode(self.message)

    def __deepcopy__(self, memo):
        return self.__class__(**self.kwargs)


class NotFound(NamosException):
    msg_fmt = ("Not Found")
    error_code = -1
    http_status_code = 404


class AlreadyExist(NamosException):
    msg_fmt = ("%(model)s  %(name)s already exists")
    error_code = 0x01002
    http_status_code = 403


class RegionNotFound(NotFound):
    msg_fmt = ("Region %(region_id)s does not found")
    error_code = 0x01001


class RegionAlreadyExist(NamosException):
    msg_fmt = ("Region %(region_id)s already exists")
    error_code = 0x01002
    http_status_code = 403


class DeviceNotFound(NotFound):
    msg_fmt = ("Device %(device_id)s does not found")
    error_code = 0x02001


class DeviceEndpointNotFound(NotFound):
    msg_fmt = ("Device Endpoint %(device_endpoint_id)s does not found")
    error_code = 0x03001


class DeviceDriverNotFound(NotFound):
    msg_fmt = ("Device Driver %(device_driver_id)s does not found")
    error_code = 0x04001


class DeviceDriverClassNotFound(NotFound):
    msg_fmt = ("Device Driver Class %(device_driver_class_id)s "
               "does not found")
    error_code = 0x05001


class ServiceNotFound(NotFound):
    msg_fmt = ("Service %(service_id)s does not found")
    error_code = 0x06001


class ServiceNodeNotFound(NotFound):
    msg_fmt = ("Service Node %(service_node_id)s does not found")
    error_code = 0x07001


class ServiceComponentNotFound(NotFound):
    msg_fmt = ("Service Component %(service_component_id)s does not found")
    error_code = 0x08001


class ServiceWorkerNotFound(NotFound):
    msg_fmt = ("Service Worker %(service_worker_id)s "
               "does not found")
    error_code = 0x09001


class ConfigNotFound(NotFound):
    msg_fmt = ("Config %(config_id)s does not found")
    error_code = 0x0a001
