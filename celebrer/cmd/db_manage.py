from oslo_config import cfg
from oslo_db import options

CONF = cfg.CONF
options.set_defaults(CONF)


class DBCommand(object):

    def upgrade(self, config):
        migration.upgrade(CONF.command.revision, config=config)

    def downgrade(self, config):
        migration.downgrade(CONF.command.revision, config=config)

    def revision(self, config):
        migration.revision(CONF.command.message,
                           CONF.command.autogenerate,
                           config=config)

    def stamp(self, config):
        migration.stamp(CONF.command.revision, config=config)

    def version(self, config):
        print(migration.version())


def add_command_parsers(subparsers):
    command_object = DBCommand()

    parser = subparsers.add_parser('upgrade')
    parser.set_defaults(func=command_object.upgrade)
    parser.add_argument('--revision', nargs='?')

    parser = subparsers.add_parser('downgrade')
    parser.set_defaults(func=command_object.downgrade)
    parser.add_argument('--revision', nargs='?')

    parser = subparsers.add_parser('stamp')
    parser.add_argument('--revision', nargs='?')
    parser.set_defaults(func=command_object.stamp)

    parser = subparsers.add_parser('revision')
    parser.add_argument('-m', '--message')
    parser.add_argument('--autogenerate', action='store_true')
    parser.set_defaults(func=command_object.revision)

    parser = subparsers.add_parser('version')
    parser.set_defaults(func=command_object.version)


command_opt = cfg.SubCommandOpt('command',
                                title='Command',
                                help='Available commands',
                                handler=add_command_parsers)

CONF.register_cli_opt(command_opt)


def main():
    CONF(project='celebrer')
