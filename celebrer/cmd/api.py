#!/usr/bin/env python

import os
import sys

import eventlet

from oslo_config import cfg
from oslo_log import log as logging
from oslo_service import service

from celebrer.common import app_loader
from celebrer.common import config
from celebrer.common import wsgi

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

        app = app_loader.load_paste_app('celebrer')
        port, host = (CONF.bind_port, CONF.bind_host)

        launcher.launch_service(wsgi.Service(app, port, host))

        launcher.wait()
    except RuntimeError as e:
        sys.stderr.write("ERROR: %s\n" % e)
        sys.exit(1)


if __name__ == '__main__':
    main()