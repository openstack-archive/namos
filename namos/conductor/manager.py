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
from oslo_utils import timeutils

from namos.common import config as namos_config
from namos.common import messaging
from namos.common import utils
from namos.conductor.config_processor import ConfigProcessor
from namos.conductor.namespace_processor import NamespaceProcessor
from namos.conductor.region_processor import RegionProcessor
from namos.conductor.service_processor import ServiceProcessor
from namos.db import api as db_api

LOG = log.getLogger(__name__)

namos_config.register_conductor_opts()

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
    TOPIC = namos_config.MESSAGE_QUEUE_CONDUCTOR_TOPIC

    def _regisgration_ackw(self, context, identification):
        client = messaging.get_rpc_client(
            topic=self._os_namos_listener_topic(identification),
            version=self.RPC_API_VERSION,
            exchange=namos_config.PROJECT_NAME)
        client.cast(context,
                    'regisgration_ackw',
                    identification=identification)
        LOG.info("REGISTER [%s] ACK" % identification)

    def _os_namos_listener_topic(self, identification):
        return 'namos.CONF.%s' % identification

    def _ping(self, context, identification):
        client = messaging.get_rpc_client(
            topic=self._os_namos_listener_topic(identification),
            version=self.RPC_API_VERSION,
            exchange=namos_config.PROJECT_NAME,
            timeout=1)
        try:
            client.call(context,
                        'ping_me',
                        identification=identification)

            LOG.info("PING [%s] SUCCESSFUL" % identification)
            return True
        except:  # noqa
            LOG.info("PING [%s] FAILED" % identification)
            return False

    def _update_config_file(self, context, identification, name, content):
        client = messaging.get_rpc_client(
            topic=self._os_namos_listener_topic(identification),
            version=self.RPC_API_VERSION,
            exchange=namos_config.PROJECT_NAME,
            timeout=2)
        client.call(context,
                    'update_config_file',
                    identification=identification,
                    name=name,
                    content=content)
        LOG.info("CONF FILE [%s] UPDATE [%s] DONE" % (name, identification))

    @request_context
    def add_region(self, context, region):
        return db_api.region_create(context, region)

    @request_context
    def region_get(self, context, region_id):
        return db_api.region_get(context. region_id)

    @request_context
    def region_update(self, context, region_id, region):
        return db_api.region_update(context. region_id, region)

    @request_context
    def region_get_all(self, context):
        return db_api.region_get_all(context)

    @request_context
    def region_delete(self, context, region_id):
        return db_api.region_delete(context. region_id)

    @request_context
    def service_node_create(self, context, service_node):
        return db_api.service_node_create(context, service_node)

    @request_context
    def service_node_get(self, context, service_node_id):
        return db_api.service_node_get(context. service_node_id)

    @request_context
    def service_node_update(self, context, service_node_id, service_node):
        return db_api.service_node_update(context.
                                          service_node_id,
                                          service_node)

    @request_context
    def service_node_get_all(self, context):
        return db_api.service_node_get_all(context)

    @request_context
    def service_node_delete(self, context, service_node_id):
        return db_api.service_node_delete(context. service_node_id)

    @request_context
    def register_myself(self, context, registration_info):
        LOG.info("REGISTER [%s.%s.%s] START\n%s" % (
            registration_info['project_name'],
            registration_info['prog_name'],
            registration_info['identification'],
            registration_info
        ))

        # Region processing
        rp = RegionProcessor(context,
                             self,
                             registration_info)
        region_id = rp.process_region()

        # Service processing
        sp = ServiceProcessor(context,
                              self,
                              region_id,
                              registration_info)
        service_component_id, service_worker_id = sp.process_service()

        # COnfig processing
        cp = ConfigProcessor(context,
                             self,
                             registration_info,
                             service_worker_id)
        cp.process_configs()
        #  Device Driver processing
        # TODO(mrkanag) if this to be per service component??
        dp = NamespaceProcessor(context,
                                self,
                                service_worker_id,
                                region_id)
        dp.process_drivers()

        self._regisgration_ackw(context,
                                registration_info['identification'])

        LOG.info("REGISTER [%s.%s.%s] DONE" % (
            registration_info['project_name'],
            registration_info['prog_name'],
            registration_info['identification']
        ))

        # TODO(mrkanag) Move this to periofic task, before deleting each
        # sw, make usre its created atleast 5 mins before
        sp.cleanup(service_component_id)
        return service_worker_id

    @request_context
    def heart_beat(self, context, identification, dieing=False):
        try:
            sw = db_api.service_worker_get_all_by(context,
                                                  pid=identification)
            if len(sw) == 1:
                if not dieing:
                    db_api.service_worker_update(
                        context,
                        sw[0].id,
                        dict(updated_at=timeutils.utcnow()))
                    LOG.info("HEART-BEAT LIVE %s " % identification)
                else:
                    db_api.service_worker_delete(context,
                                                 sw[0].id)
                    LOG.info("HEART-BEAT STOPPED %s " % identification)
            else:
                LOG.error("HEART-BEAT FAILED, No service worker registered "
                          "with identification %s " % identification)
        except Exception as e:  # noqa
            LOG.error("HEART-BEAT FAILED %s " % e)

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

    @request_context
    def view_360(self, context,
                 include_conf_file=False,
                 include_status=False,
                 include_file_entry=False):
        view = db_api.view_360(context, include_conf_file, include_status)
        if include_file_entry:
            view['config_file_entry'] = dict()
            for f in list(view['config_file']):
                view['config_file_entry'][f] = self.config_file_get(
                    context,
                    config_file_id=f
                )['entry']

        return view

    @request_context
    def config_get_by_name_for_service_worker(self,
                                              context,
                                              service_worker_id,
                                              name=None,
                                              only_configured=True):
        return db_api.config_get_by_name_for_service_worker(context,
                                                            service_worker_id,
                                                            name,
                                                            only_configured)

    @request_context
    def get_status(self, context):
        return db_api.get_status(context)

    @request_context
    def config_file_get(self, context, config_file_id):
        file = db_api.config_file_get(context, config_file_id)

        cfg_es = db_api.config_file_entry_get_all_by(
            context,
            oslo_config_file_id=config_file_id
        )
        return dict(file=file, entry=cfg_es)

    @request_context
    def config_file_update(self, context, config_file_id, content):
        # update the db
        db_api.config_file_update(context, config_file_id, {'file': content})
        cf = self.config_file_get(context, config_file_id)['file']

        # update the corresponding file in the respetive node
        sc_list = db_api.service_component_get_all_by_config_file(
            context,
            config_file_id
        )

        # TODO(mrkanag) update the config file entries

        # Find the first active service workr launcher to update the conf file
        if sc_list:
            for sc in sc_list:
                sw_list = db_api.service_worker_get_all_by(
                    context,
                    service_component_id=sc_list[0].id,
                    is_launcher=True
                )
                if sw_list:
                    for sw in sw_list:
                        # TODO(mrkanag) is ping() better option instead?
                        if utils.find_status(sw):
                            try:
                                self._update_config_file(context,
                                                         sw.pid,
                                                         cf.name,
                                                         cf.file)
                                cf['status'] = 'completed'
                                return cf
                            except:  # noqa
                                # try on next available sw
                                pass

        cf['status'] = 'failed'
        return cf

    @request_context
    def config_schema(self, context, project, with_file_link=False):
        # provide the manage oslo_config_schema --gen
        file_schema = dict()
        for cfg_s in db_api.config_schema_get_all_by(context, project=project):
            if cfg_s.file_name not in file_schema:
                file_schema[cfg_s.file_name] = dict()

            if cfg_s.group_name not in file_schema[cfg_s.file_name]:
                file_schema[cfg_s.file_name][cfg_s.group_name] = dict()

            file_schema[cfg_s.file_name][cfg_s.group_name][cfg_s.name] = cfg_s

            if with_file_link:
                cfg_es = db_api.config_file_entry_get_all_by(
                    context,
                    oslo_config_schema_id=cfg_s.id
                )
                file_schema[cfg_s.file_name][cfg_s.group_name][
                    cfg_s.name]['entries'] = cfg_es

        return file_schema
