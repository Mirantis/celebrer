from oslo_config import cfg
import oslo_messaging as messaging
from oslo_messaging import rpc
from oslo_messaging import target

CONF = cfg.CONF

TRANSPORT = None


class ApiClient(object):
    def __init__(self, transport, rkey):
        client_target = target.Target('celebrer', rkey)
        self._client = rpc.RPCClient(transport, client_target, timeout=15)

    def __call__(self, method, **kwargs):
        return self._client.call({}, method, **kwargs)


class EngineClient(object):
    def __init__(self, transport, rkey):
        client_target = target.Target('celebrer', rkey)
        self._client = rpc.RPCClient(transport, client_target, timeout=15)

    def __call__(self, method, **kwargs):
        return self._client.call({}, method, **kwargs)


class AgentClient(object):
    def __init__(self, transport, rkey):
        client_target = target.Target('celebrer', rkey)
        self._client = rpc.RPCClient(transport, client_target, timeout=15)

    def __call__(self, method, **kwargs):
        return self._client.call({}, method, **kwargs)


def api(rkey):
    global TRANSPORT
    if TRANSPORT is None:
        TRANSPORT = messaging.get_transport(CONF)

    return ApiClient(TRANSPORT, rkey)


def engine(rkey):
    global TRANSPORT
    if TRANSPORT is None:
        TRANSPORT = messaging.get_transport(CONF)

    return EngineClient(TRANSPORT, rkey)


def agent(rkey):
    global TRANSPORT
    if TRANSPORT is None:
        TRANSPORT = messaging.get_transport(CONF)

    return AgentClient(TRANSPORT, rkey)
