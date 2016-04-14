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
from namos.common import exception
from namos.common import messaging
from namos.common import utils
from namos.db import api as db_api
from namos.db import openstack_drivers

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
        dp = DriverProcessor(context,
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


class RegionProcessor(object):
    def __init__(self,
                 context,
                 manager,
                 registration_info):
        self.registration_info = registration_info
        self.manager = manager
        self.context = context

    def process_region(self):
        # region
        # If region is not provided, make it as belongs to namos's region
        if not self.registration_info.get('region_name'):
            self.registration_info[
                'region_name'] = cfg.CONF.os_namos.region_name

        try:
            region = db_api.region_create(
                self.context,
                dict(name=self.registration_info.get('region_name'))
            )
            LOG.info('Region %s is created' % region)
        except exception.AlreadyExist:
            region = db_api.region_get_by_name(
                self.context,
                name=self.registration_info.get('region_name')
            )
            LOG.info('Region %s is existing' % region)

        return region.id


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


class ConfigProcessor(object):
    def __init__(self, context, manager, registration_info, service_worker_id):
        self.context = context
        self.manager = manager
        self.registration_info = registration_info
        self.service_worker_id = service_worker_id
        self.service_component_id = db_api.service_worker_get(
            self.context,
            self.service_worker_id).service_component_id
        sc = db_api.service_component_get(
            self.context,
            self.service_component_id
        )
        self.service_node_id = sc.node_id
        self.project = db_api.service_get(self.context, sc.service_id).name

    def file_to_configs(self, file_content):
        import uuid
        tmp_file_path = '/tmp/%s.conf' % str(uuid.uuid4())
        with open(tmp_file_path, 'w') as file:
            file.write(file_content)

        conf_dict = utils.file_to_configs(tmp_file_path)

        import os
        os.remove(tmp_file_path)

        return conf_dict

    def _form_config_name(self, group, key):
        return '%s.%s' % (group, key)

    def process_config_files(self):
        # config file
        conf_name_to_file_id = dict()
        for cfg_f in self.registration_info['config_file_dict'].keys():
            try:
                config_file = db_api.config_file_create(
                    self.context,
                    dict(name=cfg_f,
                         file=self.registration_info[
                             'config_file_dict'][cfg_f],
                         service_node_id=self.service_node_id))
                LOG.info('Oslo config file %s is created' % config_file)
            except exception.AlreadyExist:
                config_files = \
                    db_api.config_file_get_by_name_for_service_node(
                        self.context,
                        service_node_id=self.service_node_id,
                        name=cfg_f
                    )
                if len(config_files) == 1:
                    config_file = \
                        db_api.config_file_update(
                            self.context,
                            config_files[0].id,
                            dict(file=self.registration_info[
                                'config_file_dict'][cfg_f]))
                    LOG.info('Oslo config file %s is existing and is updated'
                             % config_file)

            config_dict = self.file_to_configs(
                config_file.file
            )

            # config file entry
            for grp, keys in config_dict.items():
                for key, value in keys.items():
                    # find config schema
                    cfg_schs = db_api.config_schema_get_by(
                        context=self.context,
                        group=grp,
                        name=key,
                        project=self.project
                    )

                    cfg_sche = None
                    if len(cfg_schs) == 0:
                        LOG.debug("[%s] No Config Schema is existing, so "
                                  "no schema is associated for Config Entry "
                                  "%s::%s" %
                                  (self.service_component_id,
                                   grp,
                                   key))
                    elif len(cfg_schs) > 1:
                        LOG.debug("[%s] More than one Config Schema is "
                                  "existing, so no schema is associated for "
                                  "Config Entry %s::%s" %
                                  (self.service_component_id,
                                   grp,
                                   key))
                    else:
                        cfg_sche = cfg_schs[0]
                        LOG.debug("[%s] Config Schema %s is existing and is "
                                  "used to associated for Config Entry"
                                  " %s::%s" %
                                  (self.service_component_id,
                                   cfg_sche.id,
                                   grp,
                                   key))

                    # config file entry
                    cfg_name = self._form_config_name(grp, key)

                    cfg_obj_ = dict(
                        service_component_id=self.service_component_id,
                        name=cfg_name,
                        value=value,
                        oslo_config_schema_id=cfg_sche.id if
                        cfg_sche else None,
                        oslo_config_file_id=config_file.id
                    )

                    try:
                        config = db_api.config_file_entry_create(
                            self.context,
                            cfg_obj_)
                        LOG.debug("Config Entry %s is created" % config)
                    except exception.AlreadyExist:
                        configs = db_api.config_file_entry_get_all_by(
                            self.context,
                            service_component_id=cfg_obj_[
                                'service_component_id'],
                            oslo_config_file_id=config_file.id,
                            name=cfg_obj_['name'])
                        if len(configs) == 1:
                            config = db_api.config_file_entry_update(
                                self.context,
                                configs[0].id,
                                cfg_obj_)
                            LOG.debug("Config Entry %s is existing and is "
                                      "updated" % config)

                    conf_name_to_file_id[cfg_name] = config.id

        return conf_name_to_file_id

    def process_configs(self):
        conf_name_to_file_id = self.process_config_files()
        # Config
        for cfg_obj in self.registration_info['config_list']:
            # This format is used by DriverProcessor
            cfg_name = self._form_config_name(cfg_obj['group'],
                                              cfg_obj['name'])

            if not conf_name_to_file_id.get(cfg_name):
                cfg_schm_id = None
                cfg_f_entry = None

                # find config schema
                # ignore the config file_name right now !!, assumed conf unique
                # across the service wth given group and name
                cfg_schs = db_api.config_schema_get_by(
                    context=self.context,
                    group=cfg_obj['group'],
                    name=cfg_obj['name'],
                    project=self.project
                )

                if len(cfg_schs) == 0:
                    LOG.debug("[%s] No Config Schema is existing, so "
                              "no schema is associated for Config %s::%s" %
                              (self.service_worker_id,
                               cfg_obj['group'],
                               cfg_obj['name']))
                elif len(cfg_schs) > 1:
                    LOG.debug("[%s] More than one Config Schema is existing, "
                              "so no schema is associated for Config %s::%s" %
                              (self.service_worker_id,
                               cfg_obj['group'],
                               cfg_obj['name']))
                else:
                    # try:
                    #     cfg_sche = db_api.config_schema_create(
                    #         self.context,
                    #         dict(
                    #             namespace='UNKNOWN-tagged-by-NAMOS',
                    #             default_value=cfg_obj['default_value'],
                    #             type=cfg_obj['type'],
                    #             help=cfg_obj['help'],
                    #             required=cfg_obj['required'],
                    #             secret=cfg_obj['secret'],
                    #             mutable=False,
                    #             group_name=cfg_obj['group'],
                    #             name=cfg_obj['name']
                    #         )
                    #     )
                    #     LOG.info("Config Schema %s is created" % cfg_sche)
                    # except exception.AlreadyExist:
                    #     cfg_schs = db_api.config_schema_get_by(
                    #         context=self.context,
                    #         group=cfg_obj['group'],
                    #         name=cfg_obj['name'],
                    #         namespace='UNKNOWN-tagged-by-NAMOS'
                    #     )

                    cfg_sche = cfg_schs[0]
                    LOG.debug("[%s] Config Schema %s is existing and is used "
                              "for Config %s::%s" %
                              (self.service_worker_id,
                               cfg_sche.id,
                               cfg_obj['group'],
                               cfg_obj['name']))
                    cfg_schm_id = cfg_sche.id
            else:
                cfg_schm_id = None
                cfg_f_entry = conf_name_to_file_id[cfg_name]

            # config_file_entry_id = None
            # for f_id, conf_groups in conf_name_to_file_id.items():
            #     if cfg_obj['group'] in list(conf_groups):
            #         if cfg_obj['name'] in list(conf_groups[cfg_obj[
            #            'group']]):
            #             config_entrys=db_api.config_file_entry_get_all_by(
            #                 self.context,
            #                 service_component_id=self.service_component_id,
            #                 oslo_config_file_id=f_id,
            #                 name=cfg_name)
            #             if len(config_entrys) == 1:
            #                 config_file_entry_id = config_entrys[0].id
            #
            #             break

            cfg_obj_ = dict(
                service_worker_id=self.service_worker_id,
                name=cfg_name,
                value=cfg_obj['value'] if cfg_obj['value'] else cfg_obj[
                    'default_value'],
                oslo_config_schema_id=cfg_schm_id,
                oslo_config_file_entry_id=cfg_f_entry
            )

            try:
                config = db_api.config_create(self.context, cfg_obj_)
                LOG.debug("Config %s is created" % config)
            except exception.AlreadyExist:
                configs = db_api.config_get_by_name_for_service_worker(
                    self.context,
                    service_worker_id=cfg_obj_['service_worker_id'],
                    name=cfg_obj_['name'])
                if len(configs) == 1:
                    config = db_api.config_update(self.context,
                                                  configs[0].id,
                                                  cfg_obj_)
                    LOG.debug("Config %s is existing and is updated" % config)


class DriverProcessor(object):
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


if __name__ == '__main__':
    print (DriverProcessor(None, None)._to_list("[\"file\', \'http\']"))
