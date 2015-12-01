from oslo_config import cfg
from oslo_config import types
from oslo_log import log as logging

from celebrer import version

portType = types.Integer(1, 65535)

bind_opts = [
    cfg.StrOpt('bind-host', default='0.0.0.0',
               help='Address to bind the celebrer API server to.'),
    cfg.Opt('bind-port',
            type=portType,
            default=8899,
            help='Port the bind the celebrer API server to.'),
]

CONF = cfg.CONF
CONF.register_cli_opts(bind_opts)


def parse_args(args=None, usage=None, default_config_files=None):
    logging.register_options(CONF)
    logging.setup(CONF, 'celebrer')
    CONF(args=args,
         project='celebrer',
         version=version.version_string,
         usage=usage,
         default_config_files=default_config_files)