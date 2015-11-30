import oslo_messaging as messaging
from oslo_messaging import target
import uuid

from oslo_config import cfg
from oslo_log import log as logging

CONF = cfg.CONF

RPC_SERVICE = None

LOG = logging.getLogger(__name__)


def _prepare_rpc_service(server_id, rkey, endpoints):
    transport = messaging.get_transport(CONF)
    s_target = target.Target('celeber', rkey, server=server_id)
    return messaging.get_rpc_server(transport, s_target, endpoints, 'eventlet')


def get_rpc_service():
    global RPC_SERVICE
    if RPC_SERVICE is None:
        RPC_SERVICE = []
        INSTANCE_ID = str(uuid.uuid4())

        RPC_SERVICE.append(_prepare_rpc_service(INSTANCE_ID, 'discovery', []))
        RPC_SERVICE.append(_prepare_rpc_service(INSTANCE_ID, 'reports', []))
        RPC_SERVICE.append(_prepare_rpc_service(INSTANCE_ID, 'tasks', []))
    return RPC_SERVICE