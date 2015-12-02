from oslo_config import cfg
import oslo_messaging as messaging
from oslo_messaging import rpc
from oslo_messaging import target

CONF = cfg.CONF

TRANSPORT = None


class RpcClient(object):
    def __init__(self, transport, rkey):
        client_target = target.Target('celebrer', rkey)
        self._client = rpc.RPCClient(transport, client_target, timeout=15)

    def __call__(self, method, **kwargs):
        return self._client.call({}, method, **kwargs)

    def __cast__(self, method, **kwargs):
        return self._client.cast({}, method, **kwargs)


def get_client(rkey):
    global TRANSPORT
    if TRANSPORT is None:
        TRANSPORT = messaging.get_transport(CONF)

    return RpcClient(TRANSPORT, rkey)
