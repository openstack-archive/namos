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

from namos.common import config as namos_config
from namos.common import exception
from namos.db import api as db_api

LOG = log.getLogger(__name__)

CONF = cfg.CONF


class ServiceProcessor(object):
    def __init__(self,
                 context,
                 manager,
                 region_id,
                 registration_info):
        self.registration_info = registration_info
        self.manager = manager
        self.context = context
        self.region_id = region_id

    def process_service(self):
        # Service Node
        try:
            # TODO(mrkanag) user proper node name instead of fqdn
            node = db_api.service_node_create(
                self.context,
                dict(name=self.registration_info.get('fqdn'),
                     fqdn=self.registration_info.get('fqdn'),
                     region_id=self.region_id,
                     extra={'ips': self.registration_info.get('ips')}))
            LOG.info('Service node %s is created' % node)
        except exception.AlreadyExist:
            # TODO(mrkanag) is this to be region specifc search
            node = db_api.service_node_get_by_name(
                self.context,
                self.registration_info.get('fqdn'))
            LOG.info('Service node %s is existing' % node)

        # Service
        try:
            s_id = 'b9c2549f-f685-4bc2-92e9-ba8af9c18591'
            service = db_api.service_create(
                self.context,
                # TODO(mrkanag) use keystone python client and
                # use real service id here
                dict(name=self.registration_info.get('project_name'),
                     keystone_service_id=s_id))

            LOG.info('Service %s is created' % service)
        except exception.AlreadyExist:
            service = db_api.service_get_by_name(
                self.context,
                self.registration_info.get('project_name'))
            LOG.info('Service %s is existing' % service)

        # Service Component
        try:
            service_component = db_api.service_component_create(
                self.context,
                dict(name=self.registration_info['prog_name'],
                     node_id=node.id,
                     service_id=service.id,
                     type=namos_config.find_type(self.registration_info[
                         'prog_name'])))
            LOG.info('Service Component %s is created' % service_component)
        except exception.AlreadyExist:
            service_components = \
                db_api.service_component_get_all_by_node_for_service(
                    self.context,
                    node_id=node.id,
                    service_id=service.id,
                    name=self.registration_info['prog_name']
                )
            if len(service_components) == 1:
                service_component = service_components[0]
                LOG.info('Service Component %s is existing' %
                         service_component)
            # TODO(mrkanag) what to do when service_components size is > 1

        # Service Worker
        try:
            service_worker = db_api.service_worker_create(
                self.context,
                # TODO(mrkanag) Fix the name, device driver proper !
                dict(name='%s@%s' % (service_component.name,
                                     self.registration_info['pid']),
                     pid=self.registration_info['identification'],
                     host=self.registration_info['host'],
                     service_component_id=service_component.id,
                     deleted_at=None,
                     is_launcher=self.registration_info['i_am_launcher']
                     ))
            LOG.info('Service Worker %s is created' % service_worker)
        except exception.AlreadyExist:
            service_worker = db_api.service_worker_get_all_by(
                self.context,
                pid=self.registration_info['identification'],
                service_component_id=service_component.id
            )[0]
            LOG.info('Service Worker %s is existing' %
                     service_worker)

        return service_component.id, service_worker.id

    def cleanup(self, service_component_id):
        # clean up the dead service workers
        db_api.cleanup(self.context, service_component_id)
