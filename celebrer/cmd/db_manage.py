import os
import sys

from oslo_config import cfg

from celebrer.common import config
from celebrer.db import api as db_api

# If ../imagination/__init__.py exists, add ../ to Python search path, so that
# it will override what happens to be installed in /usr/(local/)lib/python...
root = os.path.join(os.path.abspath(__file__), os.pardir, os.pardir, os.pardir)
if os.path.exists(os.path.join(root, 'celebrer', '__init__.py')):
    sys.path.insert(0, root)

CONF = cfg.CONF


def main():
    config.parse_args()
    # TODO(agalkin): Implement DB drop support
    # try:
    #     db_api.drop_db()
    # except:
    #     pass
    db_api.setup_db()

if __name__ == '__main__':
    main()
