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
from oslo_context import context
import oslo_messaging
from oslo_serialization import jsonutils


DEFAULT_URL = "__default__"
TRANSPORTS = {}

_ALIASES = {
    'namos.openstack.common.rpc.impl_kombu': 'rabbit',
    'namos.openstack.common.rpc.impl_qpid': 'qpid',
    'namos.openstack.common.rpc.impl_zmq': 'zmq',
}


class RequestContextSerializer(oslo_messaging.Serializer):
    def __init__(self, base):
        self._base = base

    def serialize_entity(self, ctxt, entity):
        if not self._base:
            return entity
        return self._base.serialize_entity(ctxt, entity)

    def deserialize_entity(self, ctxt, entity):
        if not self._base:
            return entity
        return self._base.deserialize_entity(ctxt, entity)

    @staticmethod
    def serialize_context(ctxt):
        return ctxt.to_dict()

    @staticmethod
    def deserialize_context(ctxt):
        return context.RequestContext(ctxt)


class JsonPayloadSerializer(oslo_messaging.NoOpSerializer):
    @classmethod
    def serialize_entity(cls, context, entity):
        return jsonutils.to_primitive(entity, convert_instances=True)


def get_transport(url=None, optional=False, cache=True):
    """Initialise the olso.messaging layer."""
    global TRANSPORTS, DEFAULT_URL
    cache_key = url or DEFAULT_URL
    transport = TRANSPORTS.get(cache_key)
    if not transport or not cache:
        try:
            transport = oslo_messaging.get_transport(cfg.CONF, url,
                                                     aliases=_ALIASES)
        except oslo_messaging.InvalidTransportURL as e:
            if not optional or e.url:
                # NOTE(sileht): olso.messaging is configured but unloadable
                # so reraise the exception
                raise
            return None
        else:
            if cache:
                TRANSPORTS[cache_key] = transport
    return transport


def get_rpc_server(host, exchange, topic, version, endpoint):
    """Return a configured olso.messaging rpc server."""
    # oslo_messaging.set_transport_defaults(exchange)
    target = oslo_messaging.Target(server=host,
                                   topic=topic,
                                   version=version)
    serializer = RequestContextSerializer(JsonPayloadSerializer())
    transport = get_transport(optional=True)
    return oslo_messaging.get_rpc_server(transport, target,
                                         [endpoint], executor='eventlet',
                                         serializer=serializer)


def get_rpc_client(topic, exchange, version, retry=None, timeout=60, **kwargs):
    """Return a configured olso.messaging RPCClient."""
    oslo_messaging.set_transport_defaults(exchange)
    target = oslo_messaging.Target(version=version,
                                   topic=topic, **kwargs)
    serializer = RequestContextSerializer(JsonPayloadSerializer())
    transport = get_transport(optional=True)
    return oslo_messaging.RPCClient(transport, target,
                                    serializer=serializer,
                                    retry=retry,
                                    version_cap=version,
                                    timeout=timeout)


def cleanup():
    """Cleanup the olso.messaging layer."""
    global TRANSPORTS

    for url in TRANSPORTS:
        TRANSPORTS[url].cleanup()
        del TRANSPORTS[url]
