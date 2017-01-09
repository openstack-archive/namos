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

import eventlet
eventlet.monkey_patch()

from oslo_log import log
from oslo_service import service

from namos.common import messaging as rpc

LOG = log.getLogger(__name__)


class RPCService(service.Service):

    def __init__(self,
                 host,
                 exchange,
                 srv):
        super(RPCService, self).__init__()
        self.manager = srv

        self.host = host
        self.exchange = exchange
        self.version = self.manager.RPC_API_VERSION
        self.topic = self.manager.TOPIC
        self.rpcserver = None

    def start(self):
        super(RPCService, self).start()

        self.rpcserver = rpc.get_rpc_server(host=self.host,
                                            topic=self.topic,
                                            version=self.version,
                                            endpoint=self.manager,
                                            exchange=self.exchange)
        self.rpcserver.start()
        LOG.info(('Created RPC server for service %(service)s on host '
                  '%(host)s.', {'service': self.topic, 'host': self.host}))

    def stop(self):
        super(RPCService, self).stop()
        try:
            self.rpcserver.stop()
            self.rpcserver.wait()
        except Exception as e:
            LOG.exception(('Service error occurred when stopping the '
                           'RPC server. Error: %s', e))

        LOG.info(('Stopped RPC server for service %(service)s on host '
                  '%(host)s.', {'service': self.topic, 'host': self.host}))
