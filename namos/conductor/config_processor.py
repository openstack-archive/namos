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

LOG = log.getLogger(__name__)

CONF = cfg.CONF


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
