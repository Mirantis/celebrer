from oslo_config import cfg
from oslo_db import options

from celebrer.common import config
from celebrer.db import api

CONF = cfg.CONF
options.set_defaults(CONF)


class DBCommand(object):

    def setup_db(self):
        api.setup_db()

    def drop_db(self):
        api.drop_db()


def add_command_parsers(subparsers):
    command_object = DBCommand()

    parser = subparsers.add_parser('setup')
    parser.set_defaults(func=command_object.setup_db())

    parser = subparsers.add_parser('drop')
    parser.set_defaults(func=command_object.drop_db())


command_opt = cfg.SubCommandOpt('command',
                                title='Command',
                                help='Available commands',
                                handler=add_command_parsers)

CONF.register_cli_opt(command_opt)


def main():
    config.parse_args()
    CONF(project='celebrer')
