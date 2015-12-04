from oslo_config import cfg
import oslo_messaging as messaging
from oslo_messaging import rpc
from oslo_messaging import target

CONF = cfg.CONF

TRANSPORT = None


def call(rkey, method, **kwargs):
    global TRANSPORT
    if TRANSPORT is None:
        TRANSPORT = messaging.get_transport(CONF)

    client_target = target.Target('celebrer', rkey, fanout=False)
    client = rpc.RPCClient(TRANSPORT, client_target, timeout=120)

    return client.call({}, method, **kwargs)


def cast(rkey, method, **kwargs):
    global TRANSPORT
    if TRANSPORT is None:
        TRANSPORT = messaging.get_transport(CONF)

    client_target = target.Target('celebrer', rkey, fanout=True)
    client = rpc.RPCClient(TRANSPORT, client_target, timeout=120)

    return client.cast({}, method, **kwargs)
