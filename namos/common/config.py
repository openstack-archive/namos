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
from oslo_log import log as logging

import namos

PROJECT_NAME = 'namos'
VERSION = namos.__version__
MESSAGE_QUEUE_CONDUCTOR_TOPIC = '%s.conductor' % PROJECT_NAME
CONF = cfg.CONF


conductor_opts = [
    cfg.IntOpt('workers',
               default=1,
               help='Number of workers for conductor service. A single '
                    'conductor is enabled by default.'),
    cfg.StrOpt('enabled_services',
               default='namos,cinder,nova,keystone,horizon,heat,'
                       'neutron,glance,swift,trove',
               help='List of service exchanges to listen for'),
    cfg.StrOpt('host',
               default='namos-dev',
               help='conductor host name'),
]


def register_conductor_opts():
    CONF.register_opts(conductor_opts, 'conductor')


def init_conf(prog):
    CONF(project=PROJECT_NAME,
         version=VERSION,
         prog=prog)


def init_log(project=PROJECT_NAME):
    logging.register_options(cfg.CONF)
    logging.setup(cfg.CONF,
                  project,
                  version=VERSION)
