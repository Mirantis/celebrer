import os
import sys

import eventlet

from oslo_config import cfg
from oslo_log import log as logging
from oslo_service import service

from celebrer.common import engine
from celebrer.common import config

CONF = cfg.CONF

if os.name == 'nt':
    # eventlet monkey patching causes subprocess.Popen to fail on Windows
    # when using pipes due to missing non blocking I/O support
    eventlet.monkey_patch(os=False)
else:
    eventlet.monkey_patch()

# If ../celebrer/__init__.py exists, add ../ to Python search path, so that
# it will override what happens to be installed in /usr/(local/)lib/python...
root = os.path.join(os.path.abspath(__file__), os.pardir, os.pardir, os.pardir)
if os.path.exists(os.path.join(root, 'celebrer', '__init__.py')):
    sys.path.insert(0, root)


def main():
    try:
        config.parse_args()
        logging.setup(CONF, 'celebrer')
        launcher = service.ServiceLauncher(CONF)
        for rpc_service in engine.get_rpc_service():
            launcher.launch_service(rpc_service)
        launcher.wait()
    except RuntimeError as e:
        sys.stderr.write("ERROR: %s\n" % e)
        sys.exit(1)


if __name__ == '__main__':
    main()
