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

"""
The Namos Infra Management Service
"""

import eventlet
eventlet.monkey_patch()

from oslo_config import cfg
from oslo_log import log
import oslo_messaging
from oslo_service import service as os_service

from namos.common import config
from namos.common import service
from namos.conductor import manager


CONF = cfg.CONF
CMD_NAME = 'namos-manager'
LOG = log.getLogger(__name__)


def main():
    config.init_log()
    config.init_conf(CMD_NAME)

    from namos import conductor  # noqa
    mgr = service.RPCService(CONF.conductor.host,
                             config.PROJECT_NAME,
                             manager.ConductorManager())
    enabled_services = CONF.conductor.enabled_services

    launcher = os_service.ProcessLauncher(CONF)
    for srv in enabled_services.split(','):
        LOG.info('Starting conductor for %s', srv)
        oslo_messaging.set_transport_defaults(srv)
        launcher.launch_service(mgr, CONF.conductor.workers)

    # namos.register_myself()
    # TODO(mrkanag) Namos is not registering the RPC backend, fix it !
    launcher.wait()


if __name__ == '__main__':
    main()
